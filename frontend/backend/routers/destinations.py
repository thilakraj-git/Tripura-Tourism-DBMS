"""
Destinations API Router
Provides high-performance faceted discovery, rich composite profile retrieval,
review submission, and administrative management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from database.db_manager import execute_query, execute_query_one, execute_update
from backend.auth import get_current_user, get_optional_user, require_role
from backend.services.sustainability_engine import SustainabilityEngine

router = APIRouter(prefix="/api/v1/destinations", tags=["Destinations"])

class DestinationCreateModel(BaseModel):
    district_id: int
    name: str
    slug: str
    tagline: Optional[str] = None
    destination_type: str
    short_description: str
    full_description: str
    latitude: float
    longitude: float
    altitude_meters: Optional[int] = 50
    best_season: str
    recommended_duration_hours: float
    difficulty_level: str = "Easy"
    accessibility_level: str = "Full"
    crowd_density_level: str = "Low"
    entry_fee_inr: float = 0.0
    is_lesser_known: int = 0
    image_url: str

class ReviewCreateModel(BaseModel):
    overall_rating: float = Field(..., ge=1.0, le=5.0)
    cleanliness_rating: Optional[float] = Field(5.0, ge=1.0, le=5.0)
    eco_practice_rating: Optional[float] = Field(5.0, ge=1.0, le=5.0)
    community_respect_rating: Optional[float] = Field(5.0, ge=1.0, le=5.0)
    review_title: Optional[str] = None
    review_text: str
    visit_month_year: Optional[str] = "Recent Visit"

@router.get("")
def list_destinations(
    district: Optional[str] = None,
    destination_type: Optional[str] = None,
    min_eco_score: Optional[float] = None,
    difficulty: Optional[str] = None,
    accessibility: Optional[str] = None,
    crowd_level: Optional[str] = None,
    is_lesser_known: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "eco_score_desc",
    limit: int = 50,
    offset: int = 0
):
    """Faceted destination search utilizing normalized views and composite indexes."""
    query = """
        SELECT 
            destination_id, name, slug, tagline, destination_type,
            short_description, latitude, longitude, altitude_meters,
            best_season, recommended_duration_hours, difficulty_level,
            accessibility_level, crowd_density_level, entry_fee_inr,
            is_lesser_known, image_url, average_rating, total_reviews,
            eco_responsibility_index, district_id, district_name, forest_cover_percent
        FROM vw_destination_full_profile
        WHERE 1=1
    """
    params = []

    if district and district.lower() != "all":
        query += " AND LOWER(district_name) = LOWER(?)"
        params.append(district)

    if destination_type and destination_type.lower() != "all":
        query += " AND destination_type = ?"
        params.append(destination_type)

    if min_eco_score is not None:
        query += " AND eco_responsibility_index >= ?"
        params.append(min_eco_score)

    if difficulty and difficulty.lower() != "all":
        query += " AND difficulty_level = ?"
        params.append(difficulty)

    if accessibility and accessibility.lower() != "all":
        query += " AND accessibility_level = ?"
        params.append(accessibility)

    if crowd_level and crowd_level.lower() != "all":
        query += " AND crowd_density_level = ?"
        params.append(crowd_level)

    if is_lesser_known is not None:
        query += " AND is_lesser_known = ?"
        params.append(is_lesser_known)

    if search:
        query += " AND (name LIKE ? OR short_description LIKE ? OR district_name LIKE ?)"
        s_term = f"%{search}%"
        params.extend([s_term, s_term, s_term])

    # Sorting
    if sort_by == "rating_desc":
        query += " ORDER BY average_rating DESC, total_reviews DESC"
    elif sort_by == "eco_score_desc":
        query += " ORDER BY eco_responsibility_index DESC"
    elif sort_by == "name_asc":
        query += " ORDER BY name ASC"
    elif sort_by == "duration_asc":
        query += " ORDER BY recommended_duration_hours ASC"
    else:
        query += " ORDER BY eco_responsibility_index DESC"

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    results = execute_query(query, tuple(params))
    
    # Enrich with ERI tier badge information
    for item in results:
        eri = item.get("eco_responsibility_index", 75.0)
        item["eri_tier"] = SustainabilityEngine.get_tier_label(eri)

    total_count = len(results)
    return {
        "status": "success",
        "count": total_count,
        "data": results
    }

@router.get("/{id_or_slug}")
def get_destination_detail(id_or_slug: str, user: Optional[Dict[str, Any]] = Depends(get_optional_user)):
    """Retrieves complete 14-section information architecture profile for a destination."""
    if id_or_slug.isdigit():
        base_query = "SELECT * FROM vw_destination_full_profile WHERE destination_id = ?"
        param = (int(id_or_slug),)
    else:
        base_query = "SELECT * FROM vw_destination_full_profile WHERE slug = ?"
        param = (id_or_slug,)

    destination = execute_query_one(base_query, param)
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")

    dest_id = destination["destination_id"]

    # 1. Eco Extension
    eco_details = execute_query_one("SELECT * FROM eco_sites WHERE destination_id = ?", (dest_id,))

    # 2. Cultural Extension
    cultural_details = execute_query_one("SELECT * FROM cultural_sites WHERE destination_id = ?", (dest_id,))

    # 3. Sustainability Metrics Breakdown
    metrics_row = execute_query_one("SELECT * FROM sustainability_metrics WHERE destination_id = ?", (dest_id,))
    sustainability_breakdown = SustainabilityEngine.generate_indicators_breakdown(metrics_row or {})

    # 4. Experiences
    experiences = execute_query("SELECT * FROM experiences WHERE destination_id = ? AND is_active = 1", (dest_id,))

    # 5. Reviews
    reviews = execute_query("""
        SELECT r.*, u.full_name as author_name, u.country as author_country
        FROM reviews r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.destination_id = ?
        ORDER BY r.created_at DESC
        LIMIT 10
    """, (dest_id,))

    # 6. Nearby Destinations within same or adjacent district
    nearby = execute_query("""
        SELECT destination_id, name, slug, image_url, destination_type, eco_responsibility_index, district_name
        FROM vw_destination_full_profile
        WHERE district_id = ? AND destination_id != ?
        LIMIT 3
    """, (destination["district_id"], dest_id))

    # 7. Check if user bookmarked
    is_saved = False
    if user:
        save_check = execute_query_one(
            "SELECT 1 FROM saved_places WHERE user_id = ? AND destination_id = ?",
            (user["user_id"], dest_id)
        )
        is_saved = bool(save_check)

    return {
        "status": "success",
        "data": {
            "profile": destination,
            "eco_details": eco_details,
            "cultural_details": cultural_details,
            "sustainability": sustainability_breakdown,
            "experiences": experiences,
            "reviews": reviews,
            "nearby_destinations": nearby,
            "is_saved": is_saved
        }
    }

@router.post("/{destination_id}/reviews")
def submit_review(
    destination_id: int,
    review_data: ReviewCreateModel,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Submits a verified review; automated database trigger updates destination ratings."""
    dest = execute_query_one("SELECT destination_id FROM destinations WHERE destination_id = ?", (destination_id,))
    if not dest:
        raise HTTPException(status_code=404, detail="Destination does not exist")

    user_id = current_user["user_id"]
    try:
        review_id = execute_update("""
            INSERT INTO reviews (
                user_id, destination_id, overall_rating, cleanliness_rating,
                eco_practice_rating, community_respect_rating, review_title,
                review_text, visit_month_year, is_verified_visit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(user_id, destination_id) DO UPDATE SET
                overall_rating = excluded.overall_rating,
                cleanliness_rating = excluded.cleanliness_rating,
                eco_practice_rating = excluded.eco_practice_rating,
                community_respect_rating = excluded.community_respect_rating,
                review_title = excluded.review_title,
                review_text = excluded.review_text,
                created_at = CURRENT_TIMESTAMP;
        """, (
            user_id, destination_id, review_data.overall_rating,
            review_data.cleanliness_rating, review_data.eco_practice_rating,
            review_data.community_respect_rating, review_data.review_title,
            review_data.review_text, review_data.visit_month_year
        ))

        # Fetch updated destination rating
        updated_dest = execute_query_one(
            "SELECT average_rating, total_reviews FROM destinations WHERE destination_id = ?",
            (destination_id,)
        )

        return {
            "status": "success",
            "message": "Review recorded successfully and ratings recalculated.",
            "data": updated_dest
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to submit review: {str(e)}")

@router.post("/{destination_id}/toggle-save")
def toggle_save_place(destination_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Toggles bookmark for a destination in the user's personal travel dashboard."""
    user_id = current_user["user_id"]
    existing = execute_query_one(
        "SELECT save_id FROM saved_places WHERE user_id = ? AND destination_id = ?",
        (user_id, destination_id)
    )
    if existing:
        execute_update("DELETE FROM saved_places WHERE user_id = ? AND destination_id = ?", (user_id, destination_id))
        return {"status": "success", "is_saved": False, "message": "Removed from Saved Places"}
    else:
        execute_update("INSERT INTO saved_places (user_id, destination_id) VALUES (?, ?)", (user_id, destination_id))
        return {"status": "success", "is_saved": True, "message": "Saved to your Personal Journey Bookmarks"}

@router.post("", dependencies=[Depends(require_role(["admin", "content_manager"]))])
def create_destination(dest: DestinationCreateModel):
    """Administrative creation of a new destination record."""
    try:
        new_id = execute_update("""
            INSERT INTO destinations (
                district_id, name, slug, tagline, destination_type, short_description,
                full_description, latitude, longitude, altitude_meters, best_season,
                recommended_duration_hours, difficulty_level, accessibility_level,
                crowd_density_level, entry_fee_inr, is_lesser_known, image_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            dest.district_id, dest.name, dest.slug, dest.tagline, dest.destination_type,
            dest.short_description, dest.full_description, dest.latitude, dest.longitude,
            dest.altitude_meters, dest.best_season, dest.recommended_duration_hours,
            dest.difficulty_level, dest.accessibility_level, dest.crowd_density_level,
            dest.entry_fee_inr, dest.is_lesser_known, dest.image_url
        ))
        
        # Initialize default baseline sustainability metrics for the new destination
        execute_update("""
            INSERT INTO sustainability_metrics (
                destination_id, biodiversity_index, environmental_sensitivity,
                waste_management_score, community_employment_score,
                visitor_pressure_score, sustainable_transit_score,
                water_conservation_score, data_source_type
            ) VALUES (?, 75.0, 50.0, 70.0, 75.0, 40.0, 70.0, 75.0, 'Prototype Model');
        """, (new_id,))

        return {"status": "success", "destination_id": new_id, "message": "Destination registered."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create destination: {str(e)}")

@router.delete("/{destination_id}", dependencies=[Depends(require_role(["admin"]))])
def delete_destination(destination_id: int):
    """Admin-only deletion of a destination record."""
    dest = execute_query_one("SELECT destination_id FROM destinations WHERE destination_id = ?", (destination_id,))
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
        
    execute_update("DELETE FROM destinations WHERE destination_id = ?", (destination_id,))
    return {"status": "success", "message": f"Destination {destination_id} deleted."}
