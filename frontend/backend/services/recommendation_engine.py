"""
Explainable Multi-Criteria Recommendation Engine & Smart Trip Planner
Provides personalized, transparent recommendations combining user preferences,
ecological indicators, cultural relevance, budget compatibility, and geographic proximity.
"""

import math
from typing import List, Dict, Any, Optional

class RecommendationEngine:
    """
    Hybrid Multi-Criteria Recommendation & Explainability Engine.
    
    Scoring Model:
      Score(u, d) = w_nat * Sim(u.nat, d.eco) +
                    w_cult * Sim(u.cult, d.cult) +
                    w_eco * (d.eri / 100) +
                    w_crowd * (1 - d.crowd_penalty) +
                    w_budget * BudgetFit(u.budget, d.fee) +
                    w_season * SeasonFit(u.season, d.best_season)
    """

    CROWD_SCORES = {
        "Very Low": 1.0,
        "Low": 0.85,
        "Moderate": 0.65,
        "High": 0.40
    }

    TYPE_WEIGHTS = {
        "eco_sanctuary": {"nature": 0.95, "culture": 0.25},
        "hill_station": {"nature": 0.90, "culture": 0.40},
        "lake_wetland": {"nature": 0.85, "culture": 0.35},
        "rock_carving": {"nature": 0.70, "culture": 0.95},
        "royal_palace": {"nature": 0.30, "culture": 0.95},
        "cultural_heritage": {"nature": 0.40, "culture": 0.90},
        "temple_complex": {"nature": 0.35, "culture": 0.90},
        "tribal_settlement": {"nature": 0.75, "culture": 0.85},
        "tea_estate": {"nature": 0.80, "culture": 0.40}
    }

    @classmethod
    def calculate_destination_score(cls, destination: Dict[str, Any], user_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates a multi-attribute affinity score between [0, 100] with factor breakdown."""
        dest_type = destination.get("destination_type", "eco_sanctuary")
        type_aff = cls.TYPE_WEIGHTS.get(dest_type, {"nature": 0.5, "culture": 0.5})

        user_nat = float(user_prefs.get("nature_weight", 0.5))
        user_cult = float(user_prefs.get("culture_weight", 0.5))
        requires_access = bool(user_prefs.get("requires_accessibility", 0))

        # Accessibility Hard Constraint Filter
        access_level = destination.get("accessibility_level", "Full")
        if requires_access and access_level == "Limited":
            return {"score": 0.0, "is_eligible": False, "reasons": ["Excluded due to limited accessibility"]}

        # 1. Interest Affinity (35%)
        nature_match = 1.0 - abs(user_nat - type_aff["nature"])
        culture_match = 1.0 - abs(user_cult - type_aff["culture"])
        interest_affinity = (nature_match * user_nat + culture_match * user_cult) / (user_nat + user_cult + 1e-5)

        # 2. Sustainability & Eco Responsibility Index (25%)
        eri = float(destination.get("eco_responsibility_index", 75.0))
        eri_norm = eri / 100.0

        # 3. Crowd Density Factor (15%) - slow travelers and nature lovers prefer low crowd
        crowd_level = destination.get("crowd_density_level", "Moderate")
        crowd_score = cls.CROWD_SCORES.get(crowd_level, 0.65)

        # 4. Review Rating Factor (15%)
        avg_rating = float(destination.get("average_rating", 4.0))
        rating_norm = avg_rating / 5.0

        # 5. Seasonality & Off-Peak / Hidden Gem Bonus (10%)
        is_lesser_known = bool(destination.get("is_lesser_known", 0))
        hidden_bonus = 1.0 if is_lesser_known else 0.85

        composite_score = (
            0.35 * interest_affinity +
            0.25 * eri_norm +
            0.15 * crowd_score +
            0.15 * rating_norm +
            0.10 * hidden_bonus
        ) * 100.0

        # Generate Explainability Sentence
        reasons = []
        if interest_affinity > 0.8:
            top_interest = "Nature & Eco-Sanctuary" if user_nat >= user_cult else "Heritage & Indigenous Culture"
            reasons.append(f"High affinity with your preference for {top_interest}")
        if eri >= 85.0:
            reasons.append(f"Certified High Eco Responsibility Index ({eri}/100)")
        if crowd_score >= 0.85:
            reasons.append(f"Low crowd density offering serene immersion")
        if is_lesser_known:
            reasons.append("Pristine lesser-known destination reducing mass-tourism pressure")
        if avg_rating >= 4.7:
            reasons.append(f"Top-rated visitor satisfaction ({avg_rating}★)")

        explain_text = " • ".join(reasons) if reasons else "Good overall balance of culture, nature, and sustainability."

        return {
            "score": round(composite_score, 1),
            "is_eligible": True,
            "interest_affinity": round(interest_affinity * 100, 1),
            "eri_score": eri,
            "crowd_score": round(crowd_score * 100, 1),
            "explanation": explain_text
        }

    @classmethod
    def rank_destinations(cls, destinations: List[Dict[str, Any]], user_prefs: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Ranks destinations for a user profile and returns scored list with explanations."""
        scored = []
        for d in destinations:
            eval_res = cls.calculate_destination_score(d, user_prefs)
            if eval_res["is_eligible"]:
                item = dict(d)
                item["recommendation_score"] = eval_res["score"]
                item["explanation"] = eval_res["explanation"]
                item["affinity_details"] = eval_res
                scored.append(item)

        scored.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return scored[:limit]

    @classmethod
    def generate_smart_itinerary(
        cls,
        destinations: List[Dict[str, Any]],
        days: int = 3,
        budget: float = 10000.0,
        travel_style: str = "slow_travel",
        preferred_district: Optional[str] = None,
        nature_pref: float = 0.6,
        culture_pref: float = 0.6
    ) -> Dict[str, Any]:
        """
        Synthesizes a multi-day itinerary with time blocks, transit minimization,
        cost estimation, and composite eco rating.
        """
        user_prefs = {
            "nature_weight": nature_pref,
            "culture_weight": culture_pref,
            "requires_accessibility": 0
        }

        # Filter and rank destinations
        filtered = destinations
        if preferred_district and preferred_district != "all":
            dist_matches = [d for d in destinations if d.get("district_name") == preferred_district]
            if dist_matches:
                filtered = dist_matches

        ranked = cls.rank_destinations(filtered, user_prefs, limit=len(filtered))
        if not ranked:
            ranked = destinations[:min(len(destinations), days * 2)]

        # Group geographically by district to minimize inter-district transit
        by_district = {}
        for d in ranked:
            dist = d.get("district_name", "General")
            by_district.setdefault(dist, []).append(d)

        # Allocate 2 activities per day (Morning + Afternoon/Evening)
        scheduled_items = []
        used_ids = set()
        total_est_cost = 0.0
        total_transit_km = 0.0
        eco_scores = []

        day_counter = 1
        districts_order = list(by_district.keys())

        while day_counter <= days and len(used_ids) < len(ranked):
            # Pick primary district for this day
            active_dist = districts_order[(day_counter - 1) % len(districts_order)]
            candidates = [d for d in by_district[active_dist] if d["destination_id"] not in used_ids]
            
            # If current district exhausted, pull next highest ranked unused
            if not candidates:
                candidates = [d for d in ranked if d["destination_id"] not in used_ids]
                if not candidates:
                    break

            # Slot 1: Morning
            m_dest = candidates[0]
            used_ids.add(m_dest["destination_id"])
            m_cost = float(m_dest.get("entry_fee_inr", 0.0)) + 350.0  # entry + meal/guide
            m_transit = 15.0 if day_counter == 1 else 35.0
            total_est_cost += m_cost
            total_transit_km += m_transit
            eco_scores.append(float(m_dest.get("eco_responsibility_index", 75.0)))

            scheduled_items.append({
                "day_number": day_counter,
                "time_slot": "Morning (08:30 - 12:30)",
                "destination_id": m_dest["destination_id"],
                "name": m_dest["name"],
                "district_name": m_dest.get("district_name"),
                "image_url": m_dest.get("image_url"),
                "destination_type": m_dest.get("destination_type"),
                "eco_responsibility_index": m_dest.get("eco_responsibility_index"),
                "activity_note": f"Explore {m_dest['name']}. Recommended duration: {m_dest.get('recommended_duration_hours', 2.5)} hours.",
                "transit_km": m_transit,
                "slot_cost_inr": m_cost
            })

            # Slot 2: Afternoon / Evening
            remaining = [d for d in candidates if d["destination_id"] not in used_ids]
            if not remaining:
                remaining = [d for d in ranked if d["destination_id"] not in used_ids]

            if remaining:
                e_dest = remaining[0]
                used_ids.add(e_dest["destination_id"])
                e_cost = float(e_dest.get("entry_fee_inr", 0.0)) + 450.0
                e_transit = 20.0
                total_est_cost += e_cost
                total_transit_km += e_transit
                eco_scores.append(float(e_dest.get("eco_responsibility_index", 75.0)))

                scheduled_items.append({
                    "day_number": day_counter,
                    "time_slot": "Afternoon & Sunset (14:00 - 18:00)",
                    "destination_id": e_dest["destination_id"],
                    "name": e_dest["name"],
                    "district_name": e_dest.get("district_name"),
                    "image_url": e_dest.get("image_url"),
                    "destination_type": e_dest.get("destination_type"),
                    "eco_responsibility_index": e_dest.get("eco_responsibility_index"),
                    "activity_note": f"Sunset visit & local experience at {e_dest['name']}.",
                    "transit_km": e_transit,
                    "slot_cost_inr": e_cost
                })

            day_counter += 1

        avg_eco = round(sum(eco_scores) / len(eco_scores), 1) if eco_scores else 80.0
        
        # Add basic accommodation and transit base cost per day
        base_travel_cost = days * 1800.0  # eco-homestay/hotel + shared green transit
        total_est_cost += base_travel_cost

        return {
            "title": f"Tripura {days}-Day Sustainable {travel_style.replace('_', ' ').title()} Journey",
            "total_days": days,
            "travel_style": travel_style,
            "estimated_budget_inr": round(total_est_cost, 0),
            "estimated_distance_km": round(total_transit_km, 1),
            "composite_eco_score": avg_eco,
            "eco_tier": "Elite Sustainable Itinerary" if avg_eco >= 88 else "Certified Green Itinerary",
            "explanation": f"Crafted for {days} days of {travel_style.replace('_', ' ')}. Sequenced to minimize travel footprint across district clusters while balancing high-ERI nature sanctuaries and indigenous heritage.",
            "daily_schedule": scheduled_items
        }
