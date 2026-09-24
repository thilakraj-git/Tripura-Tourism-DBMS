"""
Sustainability Engine: Eco Responsibility Index (ERI)
Calculates and validates the multi-criteria sustainability index for tourist destinations.
Incorporates biodiversity conservation, environmental vulnerability, community benefit,
waste management infrastructure, carrying capacity pressure, and sustainable transit.
"""

from typing import Dict, Any

class SustainabilityEngine:
    """
    Mathematical Framework for the Eco Responsibility Index (ERI).
    
    Formula:
      ERI = (0.25 * Biodiversity_Index) +
            (0.20 * (100 - 0.3 * Environmental_Sensitivity)) +
            (0.15 * Waste_Management_Score) +
            (0.15 * Community_Employment_Score) +
            (0.15 * (100 - Visitor_Pressure_Score)) +
            (0.10 * Sustainable_Transit_Score)
            
    Domain: [0.0, 100.0]
    """
    
    WEIGHTS = {
        "biodiversity": 0.25,
        "sensitivity": 0.20,
        "waste_management": 0.15,
        "community_employment": 0.15,
        "visitor_pressure": 0.15,
        "sustainable_transit": 0.10
    }

    @classmethod
    def calculate_eri(cls, metrics: Dict[str, float]) -> float:
        """Computes the composite ERI score based on normalized 0-100 sub-indicators."""
        bio = float(metrics.get("biodiversity_index", 70.0))
        sens = float(metrics.get("environmental_sensitivity", 50.0))
        waste = float(metrics.get("waste_management_score", 70.0))
        comm = float(metrics.get("community_employment_score", 70.0))
        pressure = float(metrics.get("visitor_pressure_score", 50.0))
        transit = float(metrics.get("sustainable_transit_score", 70.0))

        # Sensitivity term reflects protection status: higher sensitivity requires stricter mitigation
        sens_mitigation_score = max(0.0, min(100.0, 100.0 - (sens * 0.3)))
        pressure_cushion_score = max(0.0, min(100.0, 100.0 - pressure))

        raw_eri = (
            cls.WEIGHTS["biodiversity"] * bio +
            cls.WEIGHTS["sensitivity"] * sens_mitigation_score +
            cls.WEIGHTS["waste_management"] * waste +
            cls.WEIGHTS["community_employment"] * comm +
            cls.WEIGHTS["visitor_pressure"] * pressure_cushion_score +
            cls.WEIGHTS["sustainable_transit"] * transit
        )

        return round(max(0.0, min(100.0, raw_eri)), 1)

    @classmethod
    def get_tier_label(cls, eri_score: float) -> Dict[str, str]:
        """Categorizes the destination based on its ERI score."""
        if eri_score >= 90.0:
            return {
                "tier": "Tier I: Pristine Eco Sanctuary",
                "badge_class": "badge-pristine",
                "color": "#1B4332",
                "description": "Exceptional ecological integrity, strict zero-plastic compliance, and direct indigenous community co-management."
            }
        elif eri_score >= 80.0:
            return {
                "tier": "Tier II: High Sustainability Certified",
                "badge_class": "badge-sustainable",
                "color": "#2D6A4F",
                "description": "Strong conservation safeguards, active waste management, and sustainable visitor volume controls."
            }
        elif eri_score >= 70.0:
            return {
                "tier": "Tier III: Balanced Cultural-Eco Site",
                "badge_class": "badge-balanced",
                "color": "#C25E2E",
                "description": "Moderate visitor traffic with established basic conservation amenities and ongoing green transit transitions."
            }
        else:
            return {
                "tier": "Tier IV: Developing Green Destination",
                "badge_class": "badge-developing",
                "color": "#9E2A2B",
                "description": "High visitor pressure requiring enhanced waste infrastructure and carrying-capacity regulation."
            }

    @classmethod
    def generate_indicators_breakdown(cls, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Provides a detailed diagnostic breakdown for UI presentation and research."""
        eri = cls.calculate_eri(metrics)
        tier_info = cls.get_tier_label(eri)
        
        return {
            "eri_score": eri,
            "tier_info": tier_info,
            "weights": cls.WEIGHTS,
            "indicators": {
                "biodiversity_value": {
                    "score": metrics.get("biodiversity_index", 75.0),
                    "weight_percent": 25,
                    "label": "Flora & Avifaunal Biodiversity Index"
                },
                "ecological_stability": {
                    "score": round(100.0 - (metrics.get("environmental_sensitivity", 50.0) * 0.3), 1),
                    "weight_percent": 20,
                    "label": "Habitat Sensitivity & Protection Index"
                },
                "waste_management": {
                    "score": metrics.get("waste_management_score", 70.0),
                    "weight_percent": 15,
                    "label": "Zero-Waste & Composting Infrastructure"
                },
                "community_benefit": {
                    "score": metrics.get("community_employment_score", 80.0),
                    "weight_percent": 15,
                    "label": "Indigenous Livelihoods & Revenue Sharing"
                },
                "carrying_capacity_cushion": {
                    "score": round(100.0 - metrics.get("visitor_pressure_score", 40.0), 1),
                    "weight_percent": 15,
                    "label": "Low Crowding & Carrying Capacity Buffer"
                },
                "green_transit": {
                    "score": metrics.get("sustainable_transit_score", 70.0),
                    "weight_percent": 10,
                    "label": "Electric / Walking / Shared Transit Access"
                }
            },
            "data_source_type": metrics.get("data_source_type", "Verified Baseline"),
            "audit_year": metrics.get("audit_year", 2026)
        }
