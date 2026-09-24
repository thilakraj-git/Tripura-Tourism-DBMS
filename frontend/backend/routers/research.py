"""
Research and Scientific Evaluation Router
Provides empirical benchmarking harnesses for DBMS indexing efficiency and
algorithmic recommendation performance (Precision@K, NDCG, Intra-List Diversity).
"""

import math
import time
from fastapi import APIRouter
from typing import Dict, Any, List

from database.db_manager import execute_query, profile_query, execute_update
from backend.services.recommendation_engine import RecommendationEngine

router = APIRouter(prefix="/api/v1/research", tags=["Research & DBMS Benchmarking"])

@router.post("/benchmark-db")
def run_dbms_indexing_benchmark():
    """
    Executes a controlled benchmark comparing optimized indexed queries
    vs simulated unindexed scans across 4 complex analytical queries.
    """
    test_queries = [
        {
            "id": "Q1",
            "name": "District Full Profile Join",
            "description": "5-Table join across destinations, districts, eco_sites, cultural_sites, and sustainability_metrics with filter.",
            "sql_optimized": """
                SELECT d.name, dist.name, es.ecosystem_type, cs.historical_epoch, sm.biodiversity_index
                FROM destinations d
                JOIN districts dist ON d.district_id = dist.district_id
                LEFT JOIN eco_sites es ON d.destination_id = es.destination_id
                LEFT JOIN cultural_sites cs ON d.destination_id = cs.destination_id
                LEFT JOIN sustainability_metrics sm ON d.destination_id = sm.destination_id
                WHERE d.eco_responsibility_index >= 85.0
                ORDER BY d.eco_responsibility_index DESC;
            """,
            "sql_unindexed": """
                SELECT d.name, dist.name, es.ecosystem_type, cs.historical_epoch, sm.biodiversity_index
                FROM destinations d
                JOIN districts dist ON d.district_id = dist.district_id
                LEFT JOIN eco_sites es ON d.destination_id = es.destination_id
                LEFT JOIN cultural_sites cs ON d.destination_id = cs.destination_id
                LEFT JOIN sustainability_metrics sm ON d.destination_id = sm.destination_id
                WHERE (d.eco_responsibility_index + 0) >= 85.0
                ORDER BY (d.eco_responsibility_index + 0) DESC;
            """
        },
        {
            "id": "Q2",
            "name": "Spatial Range & Bounding Box Query",
            "description": "Geographic coordinate filtering bounding central and northern Tripura.",
            "sql_optimized": """
                SELECT name, latitude, longitude, eco_responsibility_index
                FROM destinations
                WHERE latitude BETWEEN 23.5 AND 24.5 AND longitude BETWEEN 91.2 AND 92.2;
            """,
            "sql_unindexed": """
                SELECT name, latitude, longitude, eco_responsibility_index
                FROM destinations
                WHERE (latitude + 0) BETWEEN 23.5 AND 24.5 AND (longitude + 0) BETWEEN 91.2 AND 92.2;
            """
        },
        {
            "id": "Q3",
            "name": "Aggregated Multi-Criterion Review Rollup",
            "description": "Aggregate average ratings grouped by destination and district.",
            "sql_optimized": """
                SELECT d.name, dist.name as district, COUNT(r.review_id) as total_rev, AVG(r.overall_rating) as avg_rating
                FROM destinations d
                JOIN districts dist ON d.district_id = dist.district_id
                LEFT JOIN reviews r ON d.destination_id = r.destination_id
                GROUP BY d.destination_id, d.name, dist.name;
            """,
            "sql_unindexed": """
                SELECT d.name, dist.name as district, COUNT(r.review_id) as total_rev, AVG(r.overall_rating) as avg_rating
                FROM destinations d
                JOIN districts dist ON (d.district_id + 0) = (dist.district_id + 0)
                LEFT JOIN reviews r ON (d.destination_id + 0) = (r.destination_id + 0)
                GROUP BY d.destination_id, d.name, dist.name;
            """
        },
        {
            "id": "Q4",
            "name": "Faceted Multi-Attribute Discovery Search",
            "description": "Composite filtering by destination type, crowd level, and minimum ERI.",
            "sql_optimized": """
                SELECT destination_id, name, destination_type, crowd_density_level, eco_responsibility_index
                FROM destinations
                WHERE destination_type IN ('eco_sanctuary', 'rock_carving', 'lake_wetland')
                  AND crowd_density_level IN ('Very Low', 'Low')
                  AND eco_responsibility_index >= 80.0;
            """,
            "sql_unindexed": """
                SELECT destination_id, name, destination_type, crowd_density_level, eco_responsibility_index
                FROM destinations
                WHERE destination_type IN ('eco_sanctuary', 'rock_carving', 'lake_wetland')
                  AND crowd_density_level IN ('Very Low', 'Low')
                  AND (eco_responsibility_index + 0) >= 80.0;
            """
        }
    ]

    benchmark_results = []
    
    for q in test_queries:
        opt_prof = profile_query(q["sql_optimized"])
        unopt_prof = profile_query(q["sql_unindexed"])
        
        speedup = round(unopt_prof["execution_time_ms"] / max(opt_prof["execution_time_ms"], 0.001), 2)
        
        # Log to query_audit_logs table
        execute_update("""
            INSERT INTO query_audit_logs (query_label, query_type, has_indexes, execution_time_ms, rows_returned, plan_summary)
            VALUES (?, 'Optimized_Indexed', 1, ?, ?, ?);
        """, (q["name"], opt_prof["execution_time_ms"], opt_prof["rows_returned"], str(opt_prof["query_plan"])))

        execute_update("""
            INSERT INTO query_audit_logs (query_label, query_type, has_indexes, execution_time_ms, rows_returned, plan_summary)
            VALUES (?, 'Unindexed_Scan', 0, ?, ?, ?);
        """, (q["name"], unopt_prof["execution_time_ms"], unopt_prof["rows_returned"], str(unopt_prof["query_plan"])))

        benchmark_results.append({
            "id": q["id"],
            "name": q["name"],
            "description": q["description"],
            "optimized_time_ms": opt_prof["execution_time_ms"],
            "unindexed_time_ms": unopt_prof["execution_time_ms"],
            "speedup_factor": f"{speedup}x",
            "rows_returned": opt_prof["rows_returned"],
            "query_plan_summary": opt_prof["query_plan"]
        })

    return {
        "status": "success",
        "benchmark_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "database_engine": "SQLite 3.x (WAL mode, Foreign Keys Enforced)",
        "results": benchmark_results
    }

@router.post("/evaluate-recommendations")
def evaluate_recommendation_algorithm():
    """
    Computes scientific information retrieval evaluation metrics:
    Precision@K, Recall@K, Normalized Discounted Cumulative Gain (NDCG@K),
    and Intra-List Diversity across 4 synthetic tourist persona cohorts.
    """
    cohorts = [
        {"persona": "Eco-Sanctuary Explorer", "nature": 0.95, "culture": 0.20, "budget": "medium", "style": "nature_retreat"},
        {"persona": "Indigenous Culture Historian", "nature": 0.30, "culture": 0.95, "budget": "medium", "style": "cultural_immersion"},
        {"persona": "Slow Travel Backpacker", "nature": 0.70, "culture": 0.70, "budget": "budget", "style": "slow_travel"},
        {"persona": "Family Leisure Eco-Tourist", "nature": 0.50, "culture": 0.60, "budget": "premium", "style": "family_eco"}
    ]

    all_destinations = execute_query("SELECT * FROM vw_destination_full_profile")
    K = 5
    eval_results = []

    for cohort in cohorts:
        user_prefs = {
            "nature_weight": cohort["nature"],
            "culture_weight": cohort["culture"],
            "requires_accessibility": 0
        }
        
        ranked = RecommendationEngine.rank_destinations(all_destinations, user_prefs, limit=K)
        
        # Ground Truth Relevance: Destination considered relevant if affinity score >= 75.0
        relevance_vector = [1 if item["recommendation_score"] >= 75.0 else 0 for item in ranked]
        
        # 1. Precision@K
        precision_at_k = sum(relevance_vector) / K
        
        # 2. Recall@K (relative to all eligible destinations in db matching persona)
        total_eligible = sum(1 for d in all_destinations if RecommendationEngine.calculate_destination_score(d, user_prefs)["score"] >= 75.0)
        recall_at_k = sum(relevance_vector) / max(total_eligible, 1)

        # 3. DCG and IDCG for NDCG@K
        dcg = sum([rel / math.log2(idx + 2) for idx, rel in enumerate(relevance_vector)])
        ideal_relevance = sorted(relevance_vector, reverse=True)
        idcg = sum([rel / math.log2(idx + 2) for idx, rel in enumerate(ideal_relevance)])
        ndcg = round(dcg / max(idcg, 1e-5), 3)

        # 4. Intra-List Diversity (distinct destination types in Top-K)
        distinct_types = len(set(d["destination_type"] for d in ranked))
        diversity_score = round(distinct_types / K, 3)

        # 5. Average ERI of Top-K
        avg_top_k_eri = round(sum(d["eco_responsibility_index"] for d in ranked) / K, 1)

        eval_results.append({
            "persona": cohort["persona"],
            "profile_vector": f"Nature: {cohort['nature']}, Culture: {cohort['culture']}",
            "precision_at_5": round(precision_at_k, 3),
            "recall_at_5": round(recall_at_k, 3),
            "ndcg_at_5": ndcg,
            "intra_list_diversity": diversity_score,
            "average_eri_top_k": avg_top_k_eri,
            "recommended_top_items": [d["name"] for d in ranked[:3]]
        })

    # Global averages across cohorts
    mean_precision = round(sum(r["precision_at_5"] for r in eval_results) / len(eval_results), 3)
    mean_recall = round(sum(r["recall_at_5"] for r in eval_results) / len(eval_results), 3)
    mean_ndcg = round(sum(r["ndcg_at_5"] for r in eval_results) / len(eval_results), 3)
    mean_diversity = round(sum(r["intra_list_diversity"] for r in eval_results) / len(eval_results), 3)

    return {
        "status": "success",
        "evaluation_metrics": {
            "mean_precision_at_5": mean_precision,
            "mean_recall_at_5": mean_recall,
            "mean_ndcg_at_5": mean_ndcg,
            "mean_intra_list_diversity": mean_diversity
        },
        "cohort_breakdown": eval_results
    }
