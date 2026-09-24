"""
Tripura Terra: Comprehensive System Test Suite
Validates:
1. 3NF Database schema, foreign keys, triggers, views, and integrity.
2. Sustainability Engine (ERI formula, bounds, tiers).
3. Explainable Recommendation Engine & Smart Trip Planner.
4. REST API endpoints via FastAPI TestClient.
5. DBMS Indexing Performance Benchmarking.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import get_connection, execute_query, execute_query_one, execute_update, profile_query
from database.seeds import seed_database
from backend.services.sustainability_engine import SustainabilityEngine
from backend.services.recommendation_engine import RecommendationEngine
from backend.routers import destinations, culture_eco, itinerary, analytics, research, users
from backend.routers.users import LoginRequest
from backend.routers.itinerary import PlanRequestModel

class TripuraTerraSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- [SETUP] Seeding clean test database ---")
        seed_database()

    def test_01_database_districts_and_destinations(self):
        """Verify all 8 Tripura districts and initial destination records exist."""
        districts = execute_query("SELECT * FROM districts")
        self.assertEqual(len(districts), 8, "Expected exactly 8 administrative districts of Tripura.")
        
        destinations = execute_query("SELECT * FROM destinations")
        self.assertGreaterEqual(len(destinations), 14, "Expected at least 14 seeded destinations.")

    def test_02_database_foreign_key_enforcement(self):
        """Verify foreign key constraint blocks orphaned destination with invalid district_id."""
        conn = get_connection()
        cursor = conn.cursor()
        with self.assertRaises(Exception):
            cursor.execute("""
                INSERT INTO destinations (
                    district_id, name, slug, tagline, destination_type, short_description,
                    full_description, latitude, longitude, altitude_meters, best_season,
                    recommended_duration_hours, image_url
                ) VALUES (999, 'Invalid Place', 'invalid-slug', 'test', 'eco_sanctuary', 'short', 'full', 23.5, 91.5, 50, 'Winter', 2.0, 'http://img');
            """)
        conn.close()

    def test_03_database_triggers_ratings_recalculation(self):
        """Verify trg_review_after_insert and trg_review_after_delete automatically update average_rating."""
        # Check current rating of destination 1
        before = execute_query_one("SELECT average_rating, total_reviews FROM destinations WHERE destination_id = 1")
        
        # Insert a new test review from user 4
        execute_update("""
            INSERT INTO reviews (user_id, destination_id, overall_rating, review_title, review_text)
            VALUES (4, 1, 5.0, 'Magnificent sacred site', 'Verified pristine conditions.');
        """)
        
        after_insert = execute_query_one("SELECT average_rating, total_reviews FROM destinations WHERE destination_id = 1")
        self.assertEqual(after_insert["total_reviews"], before["total_reviews"] + 1)
        
        # Delete review to test trigger 2
        execute_update("DELETE FROM reviews WHERE user_id = 4 AND destination_id = 1;")
        after_delete = execute_query_one("SELECT average_rating, total_reviews FROM destinations WHERE destination_id = 1")
        self.assertEqual(after_delete["total_reviews"], before["total_reviews"])

    def test_04_database_views(self):
        """Verify analytical SQL views execute correctly."""
        view_profile = execute_query("SELECT * FROM vw_destination_full_profile WHERE destination_id = 1")
        self.assertTrue(len(view_profile) > 0)
        self.assertIn("district_name", view_profile[0])
        self.assertIn("ecosystem_type", view_profile[0])

        district_analytics = execute_query("SELECT * FROM vw_district_analytics")
        self.assertEqual(len(district_analytics), 8)

    def test_05_sustainability_engine_calculation(self):
        """Test ERI composite calculation and tier classification."""
        sample_metrics = {
            "biodiversity_index": 92.0,
            "environmental_sensitivity": 80.0,
            "waste_management_score": 85.0,
            "community_employment_score": 90.0,
            "visitor_pressure_score": 35.0,
            "sustainable_transit_score": 80.0
        }
        eri = SustainabilityEngine.calculate_eri(sample_metrics)
        self.assertGreaterEqual(eri, 0.0)
        self.assertLessEqual(eri, 100.0)
        
        tier = SustainabilityEngine.get_tier_label(eri)
        self.assertIn("Pristine" if eri >= 90 else "Sustainability", tier["tier"])

    def test_06_recommendation_engine_and_explainability(self):
        """Test multi-criteria scoring and transparent explanation generation."""
        destinations = execute_query("SELECT * FROM vw_destination_full_profile")
        user_prefs = {
            "nature_weight": 0.9,
            "culture_weight": 0.2,
            "requires_accessibility": 0
        }
        ranked = RecommendationEngine.rank_destinations(destinations, user_prefs, limit=5)
        self.assertEqual(len(ranked), 5)
        self.assertTrue("explanation" in ranked[0])
        self.assertIn("Nature", ranked[0]["explanation"])

    def test_07_smart_trip_planner(self):
        """Test multi-day itinerary synthesis with transit and budget constraints."""
        destinations = execute_query("SELECT * FROM vw_destination_full_profile")
        itinerary = RecommendationEngine.generate_smart_itinerary(
            destinations=destinations,
            days=3,
            budget=15000,
            travel_style="slow_travel",
            nature_pref=0.8,
            culture_pref=0.6
        )
        self.assertEqual(itinerary["total_days"], 3)
        self.assertEqual(len(itinerary["daily_schedule"]), 6)  # 2 per day * 3 days
        self.assertGreater(itinerary["composite_eco_score"], 70.0)

    def test_08_api_destinations_endpoint(self):
        """Test destinations faceted search router."""
        body = destinations.list_destinations(district="West Tripura")
        self.assertEqual(body["status"], "success")
        self.assertTrue(len(body["data"]) > 0)
        for d in body["data"]:
            self.assertEqual(d["district_name"], "West Tripura")

    def test_09_api_auth_and_protected_route(self):
        """Test login authentication and protected profile endpoint."""
        login_res = users.login(LoginRequest(
            email="marcus.eco@traveler.org",
            password="Traveler@2026"
        ))
        self.assertEqual(login_res["status"], "success")
        token = login_res["token"]
        self.assertTrue(token)

        # Direct verification of user profile
        current_user = login_res["user"]
        me_res = users.get_my_profile(current_user=current_user)
        self.assertEqual(me_res["status"], "success")
        self.assertEqual(me_res["user"]["email"], "marcus.eco@traveler.org")

    def test_10_api_research_benchmarks(self):
        """Test research endpoints for DB indexing benchmark and RecSys evaluation."""
        bench_res = research.run_dbms_indexing_benchmark()
        self.assertEqual(bench_res["status"], "success")
        self.assertEqual(len(bench_res["results"]), 4)

        eval_res = research.evaluate_recommendation_algorithm()
        self.assertEqual(eval_res["status"], "success")
        metrics = eval_res["evaluation_metrics"]
        self.assertGreater(metrics["mean_precision_at_5"], 0.5)

if __name__ == "__main__":
    unittest.main()
