"""
Culture & Eco Specialized Router
Provides deep access to indigenous heritage, craft knowledge, culinary culture,
wildlife sanctuaries, eco-trails, and seasonal festivals.
"""

from fastapi import APIRouter
from typing import Optional
from database.db_manager import execute_query

router = APIRouter(prefix="/api/v1", tags=["Culture & Eco-Trails"])

@router.get("/culture/communities")
def list_indigenous_communities():
    """Returns profiles of Tripura's indigenous communities with etiquette guidelines."""
    data = execute_query("SELECT * FROM indigenous_communities ORDER BY name ASC")
    return {"status": "success", "count": len(data), "data": data}

@router.get("/culture/sites")
def list_cultural_heritage_sites():
    """Returns all cultural, architectural, and rock-cut sites with historical context."""
    query = """
        SELECT 
            d.destination_id, d.name, d.slug, d.tagline, d.image_url,
            d.latitude, d.longitude, dist.name as district_name,
            cs.historical_epoch, cs.architectural_style, cs.indigenous_community_link,
            cs.cultural_significance, cs.rituals_and_folklore, cs.dress_code_guidelines,
            cs.photography_allowed, cs.preservation_agency
        FROM destinations d
        JOIN cultural_sites cs ON d.destination_id = cs.destination_id
        JOIN districts dist ON d.district_id = dist.district_id
        ORDER BY d.average_rating DESC;
    """
    data = execute_query(query)
    return {"status": "success", "count": len(data), "data": data}

@router.get("/eco/trails-sanctuaries")
def list_eco_sanctuaries_and_trails():
    """Returns ecological destinations, wildlife sanctuaries, and montane hiking trails."""
    query = """
        SELECT 
            d.destination_id, d.name, d.slug, d.tagline, d.image_url,
            d.latitude, d.longitude, d.eco_responsibility_index,
            d.difficulty_level, d.best_season, dist.name as district_name,
            es.ecosystem_type, es.biodiversity_significance, es.key_flora, es.key_fauna,
            es.conservation_status, es.carrying_capacity_per_day, es.trail_length_km,
            es.best_birdwatching_time, es.plastic_free_zone
        FROM destinations d
        JOIN eco_sites es ON d.destination_id = es.destination_id
        JOIN districts dist ON d.district_id = dist.district_id
        ORDER BY d.eco_responsibility_index DESC;
    """
    data = execute_query(query)
    return {"status": "success", "count": len(data), "data": data}

@router.get("/events")
def list_events(upcoming_only: bool = False):
    """Returns cultural festivals, tribal ceremonies, and seasonal events."""
    query = """
        SELECT 
            e.*, dist.name as district_name, d.name as destination_name
        FROM events e
        JOIN districts dist ON e.district_id = dist.district_id
        LEFT JOIN destinations d ON e.destination_id = d.destination_id
        ORDER BY e.start_date ASC;
    """
    data = execute_query(query)
    return {"status": "success", "count": len(data), "data": data}

@router.get("/experiences")
def list_all_experiences(category: Optional[str] = None):
    """Returns local community-led sustainable tourism experiences."""
    query = """
        SELECT 
            exp.*, d.name as destination_name, d.slug as destination_slug,
            dist.name as district_name
        FROM experiences exp
        JOIN destinations d ON exp.destination_id = d.destination_id
        JOIN districts dist ON d.district_id = dist.district_id
        WHERE exp.is_active = 1
    """
    params = []
    if category:
        query += " AND exp.category = ?"
        params.append(category)
        
    query += " ORDER BY exp.cost_inr ASC;"
    data = execute_query(query, tuple(params))
    return {"status": "success", "count": len(data), "data": data}
