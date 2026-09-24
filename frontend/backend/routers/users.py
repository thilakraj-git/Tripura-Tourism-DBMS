"""
User Profile, Authentication & District Router
Handles login, registration, user preferences, bookmarks, and district metadata.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr

from database.db_manager import execute_query, execute_query_one, execute_update
from backend.auth import hash_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/v1", tags=["Users & Auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class UserPreferencesUpdate(BaseModel):
    preferred_travel_style: str = "slow_travel"
    budget_tier: str = "medium"
    preferred_pace: str = "moderate"
    nature_weight: float = 0.5
    culture_weight: float = 0.5
    requires_accessibility: int = 0
    max_travel_hours_per_day: int = 6

@router.post("/auth/login")
def login(creds: LoginRequest):
    """Authenticates credentials and issues a signed JWT token."""
    pwd_hash = hash_password(creds.password)
    user = execute_query_one("""
        SELECT user_id, full_name, email, role, country, is_active
        FROM users
        WHERE LOWER(email) = LOWER(?) AND password_hash = ?;
    """, (creds.email.strip(), pwd_hash))

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if user["is_active"] != 1:
        raise HTTPException(status_code=403, detail="Account is deactivated.")

    # Update last login
    execute_update("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", (user["user_id"],))

    token = create_access_token(user["user_id"], user["role"], user["email"], user["full_name"])

    # Fetch user preferences
    prefs = execute_query_one("SELECT * FROM user_preferences WHERE user_id = ?", (user["user_id"],))

    return {
        "status": "success",
        "token": token,
        "user": {
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"],
            "country": user["country"],
            "preferences": prefs
        }
    }

@router.get("/auth/me")
def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieves full profile with preferences and activity counts."""
    user_id = current_user["user_id"]
    prefs = execute_query_one("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
    
    saved_count = execute_query_one(
        "SELECT COUNT(*) as count FROM saved_places WHERE user_id = ?", (user_id,)
    )["count"]
    
    trips_count = execute_query_one(
        "SELECT COUNT(*) as count FROM itineraries WHERE user_id = ?", (user_id,)
    )["count"]

    reviews_count = execute_query_one(
        "SELECT COUNT(*) as count FROM reviews WHERE user_id = ?", (user_id,)
    )["count"]

    return {
        "status": "success",
        "user": current_user,
        "preferences": prefs,
        "stats": {
            "saved_places_count": saved_count,
            "itineraries_count": trips_count,
            "reviews_submitted_count": reviews_count
        }
    }

@router.put("/users/preferences")
def update_preferences(prefs: UserPreferencesUpdate, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Updates personalized travel preferences."""
    user_id = current_user["user_id"]
    execute_update("""
        INSERT INTO user_preferences (
            user_id, preferred_travel_style, budget_tier, preferred_pace,
            nature_weight, culture_weight, requires_accessibility,
            max_travel_hours_per_day, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            preferred_travel_style = excluded.preferred_travel_style,
            budget_tier = excluded.budget_tier,
            preferred_pace = excluded.preferred_pace,
            nature_weight = excluded.nature_weight,
            culture_weight = excluded.culture_weight,
            requires_accessibility = excluded.requires_accessibility,
            max_travel_hours_per_day = excluded.max_travel_hours_per_day,
            updated_at = CURRENT_TIMESTAMP;
    """, (
        user_id, prefs.preferred_travel_style, prefs.budget_tier, prefs.preferred_pace,
        prefs.nature_weight, prefs.culture_weight, prefs.requires_accessibility,
        prefs.max_travel_hours_per_day
    ))
    return {"status": "success", "message": "Preferences updated successfully."}

@router.get("/users/saved-places")
def get_saved_places(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieves all bookmarked destinations for current user."""
    user_id = current_user["user_id"]
    query = """
        SELECT 
            sp.save_id, sp.saved_at, sp.notes,
            d.destination_id, d.name, d.slug, d.tagline, d.image_url,
            d.destination_type, d.eco_responsibility_index, d.average_rating,
            dist.name as district_name
        FROM saved_places sp
        JOIN destinations d ON sp.destination_id = d.destination_id
        JOIN districts dist ON d.district_id = dist.district_id
        WHERE sp.user_id = ?
        ORDER BY sp.saved_at DESC;
    """
    places = execute_query(query, (user_id,))
    return {"status": "success", "count": len(places), "data": places}

@router.get("/districts")
def list_districts():
    """Lists all 8 administrative districts with geographic centres and forest covers."""
    districts = execute_query("SELECT * FROM districts ORDER BY name ASC")
    return {"status": "success", "count": len(districts), "data": districts}
