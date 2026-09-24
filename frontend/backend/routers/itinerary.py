"""
Itinerary and Smart Trip Planner Router
Powers the 'Build My Journey' feature with constraint-based itinerary synthesis,
atomic database saving, and trip management.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from database.db_manager import execute_query, execute_query_one, execute_update, execute_transaction
from backend.auth import get_current_user, get_optional_user
from backend.services.recommendation_engine import RecommendationEngine

router = APIRouter(prefix="/api/v1", tags=["Trip Planner & Itineraries"])

class PlanRequestModel(BaseModel):
    days: int = Field(3, ge=1, le=14)
    budget: float = Field(12000.0, ge=1000.0)
    travel_style: str = "slow_travel"
    preferred_district: Optional[str] = "all"
    nature_weight: float = Field(0.6, ge=0.0, le=1.0)
    culture_weight: float = Field(0.6, ge=0.0, le=1.0)

class SaveItineraryModel(BaseModel):
    title: str
    total_days: int
    budget_inr: float
    travel_style: str
    estimated_distance_km: float
    composite_eco_score: float
    explanation_notes: str
    items: List[Dict[str, Any]]

@router.post("/planner/generate")
def generate_itinerary(plan_req: PlanRequestModel):
    """Synthesizes a structured multi-day itinerary with geographic clustering and explainability."""
    # Pull destinations with district names
    destinations = execute_query("SELECT * FROM vw_destination_full_profile WHERE 1=1")
    
    itinerary = RecommendationEngine.generate_smart_itinerary(
        destinations=destinations,
        days=plan_req.days,
        budget=plan_req.budget,
        travel_style=plan_req.travel_style,
        preferred_district=plan_req.preferred_district,
        nature_pref=plan_req.nature_weight,
        culture_pref=plan_req.culture_weight
    )

    return {
        "status": "success",
        "data": itinerary
    }

@router.post("/itineraries/save")
def save_itinerary(
    itin_data: SaveItineraryModel,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Atomically persists a generated or custom itinerary with all scheduled items."""
    user_id = current_user["user_id"]
    try:
        itin_id = execute_update("""
            INSERT INTO itineraries (
                user_id, title, total_days, budget_inr, travel_style,
                estimated_distance_km, composite_eco_score, explanation_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            user_id, itin_data.title, itin_data.total_days, itin_data.budget_inr,
            itin_data.travel_style, itin_data.estimated_distance_km,
            itin_data.composite_eco_score, itin_data.explanation_notes
        ))

        # Insert schedule items
        for seq, item in enumerate(itin_data.items, start=1):
            execute_update("""
                INSERT INTO itinerary_items (
                    itinerary_id, destination_id, day_number, time_slot,
                    sequence_order, activity_note, transit_km_from_prev
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                itin_id,
                item["destination_id"],
                item.get("day_number", 1),
                "Morning" if "Morning" in item.get("time_slot", "") else "Afternoon",
                seq,
                item.get("activity_note", ""),
                item.get("transit_km", 0.0)
            ))

        return {
            "status": "success",
            "itinerary_id": itin_id,
            "message": "Itinerary successfully saved to your profile."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save itinerary: {str(e)}")

@router.get("/itineraries/my-trips")
def list_user_trips(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieves all itineraries saved by the authenticated user."""
    user_id = current_user["user_id"]
    trips = execute_query("""
        SELECT * FROM itineraries WHERE user_id = ? ORDER BY created_at DESC;
    """, (user_id,))

    for trip in trips:
        items = execute_query("""
            SELECT ii.*, d.name as destination_name, d.image_url, d.destination_type,
                   dist.name as district_name
            FROM itinerary_items ii
            JOIN destinations d ON ii.destination_id = d.destination_id
            JOIN districts dist ON d.district_id = dist.district_id
            WHERE ii.itinerary_id = ?
            ORDER BY ii.day_number ASC, ii.sequence_order ASC;
        """, (trip["itinerary_id"],))
        trip["items"] = items

    return {"status": "success", "count": len(trips), "data": trips}

@router.delete("/itineraries/{itinerary_id}")
def delete_trip(itinerary_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Deletes a saved itinerary owned by the authenticated user."""
    user_id = current_user["user_id"]
    existing = execute_query_one(
        "SELECT itinerary_id FROM itineraries WHERE itinerary_id = ? AND user_id = ?",
        (itinerary_id, user_id)
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Itinerary not found or access denied")

    execute_update("DELETE FROM itineraries WHERE itinerary_id = ?", (itinerary_id,))
    return {"status": "success", "message": "Itinerary deleted successfully"}
