"""
Analytics and Administrative Statistics Router
Presents aggregated database views, metrics distributions, district indicators,
and sustainability pressure matrixes.
"""

from fastapi import APIRouter
from database.db_manager import execute_query, execute_query_one

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & Reporting"])

@router.get("/overview")
def get_analytics_overview():
    """Provides high-level system metrics and key performance indicators."""
    total_dest = execute_query_one("SELECT COUNT(*) as count FROM destinations")["count"]
    total_users = execute_query_one("SELECT COUNT(*) as count FROM users")["count"]
    total_reviews = execute_query_one("SELECT COUNT(*) as count FROM reviews")["count"]
    total_itineraries = execute_query_one("SELECT COUNT(*) as count FROM itineraries")["count"]
    
    avg_eco = execute_query_one("SELECT ROUND(AVG(eco_responsibility_index), 2) as val FROM destinations")["val"] or 0.0
    avg_rating = execute_query_one("SELECT ROUND(AVG(average_rating), 2) as val FROM destinations")["val"] or 0.0

    eco_dest_count = execute_query_one("""
        SELECT COUNT(*) as count FROM destinations 
        WHERE destination_type IN ('eco_sanctuary', 'lake_wetland', 'hill_station')
    """)["count"]

    cult_dest_count = execute_query_one("""
        SELECT COUNT(*) as count FROM destinations 
        WHERE destination_type IN ('cultural_heritage', 'rock_carving', 'royal_palace', 'temple_complex')
    """)["count"]

    lesser_known_count = execute_query_one("""
        SELECT COUNT(*) as count FROM destinations WHERE is_lesser_known = 1
    """)["count"]

    return {
        "status": "success",
        "data": {
            "total_destinations": total_dest,
            "eco_destinations": eco_dest_count,
            "cultural_destinations": cult_dest_count,
            "lesser_known_destinations": lesser_known_count,
            "total_registered_users": total_users,
            "total_reviews": total_reviews,
            "total_generated_itineraries": total_itineraries,
            "state_average_eco_index": avg_eco,
            "overall_average_rating": avg_rating
        }
    }

@router.get("/district-rollup")
def get_district_rollup():
    """Returns analytics from the 3NF view vw_district_analytics."""
    data = execute_query("SELECT * FROM vw_district_analytics ORDER BY total_destinations DESC")
    return {"status": "success", "data": data}

@router.get("/category-distribution")
def get_category_distribution():
    """Counts destinations across all defined tourism types."""
    data = execute_query("""
        SELECT destination_type, COUNT(*) as count, ROUND(AVG(eco_responsibility_index), 1) as avg_eco
        FROM destinations
        GROUP BY destination_type
        ORDER BY count DESC
    """)
    return {"status": "success", "data": data}

@router.get("/sustainability-pressure-matrix")
def get_sustainability_matrix():
    """Returns bivariate points: ERI vs Visitor Pressure for carrying capacity analysis."""
    data = execute_query("""
        SELECT 
            d.destination_id, d.name, dist.name as district_name,
            d.eco_responsibility_index, d.crowd_density_level,
            sm.visitor_pressure_score, sm.biodiversity_index, sm.waste_management_score
        FROM destinations d
        JOIN districts dist ON d.district_id = dist.district_id
        JOIN sustainability_metrics sm ON d.destination_id = sm.destination_id
        ORDER BY d.eco_responsibility_index DESC;
    """)
    return {"status": "success", "data": data}
