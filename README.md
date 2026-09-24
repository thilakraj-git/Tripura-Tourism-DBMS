# Tripura Terra (ত্রিপুরা ভূখণ্ড)

### An Intelligent Digital Platform for Sustainable Eco & Cultural Tourism in Tripura

> *“Discover Tripura. Respect the Land. Experience the Culture.”*

[![DBMS: 3NF Relational](https://img.shields.io/badge/DBMS-3NF%20Relational-1b4332.svg)](#database-architecture)
[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-059669.svg)](#backend-api)
[![GIS: Leaflet OSM](https://img.shields.io/badge/GIS-Leaflet%20OSM-c25e2e.svg)](#gis-interactive-map)
[![Python: 3.14+](https://img.shields.io/badge/Python-3.14+-blue.svg)](#quick-start)
[![Tests: 100% Passed](https://img.shields.io/badge/Tests-10%2F10%20Passed-brightgreen.svg)](#automated-verification)

---

## 1. Executive Summary & Vision

**Tripura Terra** is a professional, research-oriented, database-driven smart tourism platform for **Tripura, India**. Developed with a strong academic Database Management System (DBMS) foundation and an explainable decision-support engine, it addresses the core challenge of sustainable travel in ecologically sensitive and culturally rich regions:

> **“Where should I go, what should I experience, how can I plan it, and how can I travel responsibly without causing environmental degradation or cultural commodification?”**

The platform connects **Tourists + Destinations + Local Culture + Nature + Local Communities + Tourism Data** into a cohesive digital ecosystem.

---

## 2. Key Architecture & Research Pillars

### 🏛️ 1. DBMS Foundation (3NF Normalized)
- Fully normalized relational schema across **15 core entities**:
  - `districts`, `destinations`, `eco_sites`, `cultural_sites`, `experiences`, `indigenous_communities`, `sustainability_metrics`, `reviews`, `itineraries`, `itinerary_items`, `saved_places`, `events`, `users`, `user_preferences`, `query_audit_logs`.
- **Integrity Constraints**: Primary keys, composite unique constraints (`user_id, destination_id`), check constraints (`CHECK(forest_cover_percent BETWEEN 0 AND 100)`), and foreign key cascade rules (`ON DELETE RESTRICT` / `ON DELETE CASCADE`).
- **Database Triggers**:
  - `trg_review_after_insert` / `trg_review_after_delete`: Automatically updates average ratings and review counts on destinations.
  - `trg_sustainability_metric_update`: Recalculates the composite Eco Responsibility Index on metric updates.
- **Analytical Views**:
  - `vw_destination_full_profile`: Denormalized 5-table join for high-speed single-query lookups.
  - `vw_eco_rankings`: State-wide ranking using SQL window function `RANK() OVER (ORDER BY eco_responsibility_index DESC)`.
  - `vw_district_analytics`: Rollup aggregations of total sites, eco sites, and average ratings across all 8 districts.

### 🌿 2. Eco Responsibility Index (ERI)
Transparent mathematical model synthesizing 6 measurable parameters:
$$ERI = 0.25 \cdot \text{Bio} + 0.20 \cdot \max(0, 100 - 0.3 \cdot \text{Sens}) + 0.15 \cdot \text{Waste} + 0.15 \cdot \text{Comm} + 0.15 \cdot (100 - \text{Pressure}) + 0.10 \cdot \text{Transit}$$
- Clearly categorizes data into **Verified Baseline** vs **Prototype Demonstration Models**.
- Assigns destinations into 4 certified sustainability tiers.

### 🎯 3. Explainable Multi-Criteria Recommender Engine
- Ranks destinations using interest similarity vectors, ERI scores, crowd density factors, and budget constraints.
- **Explainability**: Every recommendation includes a transparent explanation (e.g., *"High affinity with Nature & Eco-Sanctuary • Certified High Eco Responsibility Index (94/100) • Low crowd density"*).
- **Smart Trip Planner ("Build My Journey")**: Generates day-by-day morning/afternoon schedules, clusters visits by district proximity to minimize transit time, and estimates total carbon and monetary budgets.

### 🔬 4. Live Research & DBMS Benchmark Harness
- **DBMS Indexing Benchmark**: Runs live queries comparing indexed B-tree lookups vs unindexed scans via `EXPLAIN QUERY PLAN`, logging results and demonstrating speedup factors.
- **RecSys Evaluation**: Computes empirical information retrieval metrics (**Precision@5**, **Recall@5**, **NDCG@5**, and **Intra-List Diversity**) across 4 synthetic tourist personas.

### 🗺️ 5. Interactive GIS Map & Editorial Design System
- Built with **Leaflet.js** and OpenStreetMap.
- Layer toggles for Eco Sanctuaries, Rock Art, Royal Palaces, Hill Stations, and Wetlands.
- Editorial travel-tech design system: Deep pine (`#183B2B`), warm terracotta (`#C25E2E`), soft sand (`#F8F6F0`), and DM Serif Display + Plus Jakarta Sans typography.

---

## 3. Directory Structure

```text
/dbms tourism project
├── backend/
│   ├── app.py                      # FastAPI application entry point
│   ├── auth.py                     # JWT token signing, verification & RBAC
│   ├── routers/
│   │   ├── destinations.py         # Faceted search, 14-section detail, reviews
│   │   ├── culture_eco.py          # Indigenous communities, trails, festivals
│   │   ├── itinerary.py            # Trip planner engine & itinerary persistence
│   │   ├── analytics.py            # Aggregated statistics and district views
│   │   ├── research.py             # Live DB benchmarks & RecSys evaluation
│   │   └── users.py                # Authentication, profile & bookmarks
│   └── services/
│       ├── recommendation_engine.py# Explainable multi-attribute scoring & planner
│       └── sustainability_engine.py# ERI formula calculator & indicators breakdown
├── database/
│   ├── schema.sql                  # 3NF DDL schema with triggers, views & indexes
│   ├── db_manager.py               # SQLite connection manager with WAL & query profiling
│   ├── seeds.py                    # Authentic Tripura geographic & cultural seed data
│   └── tripura_terra.db            # Initialized SQLite database
├── frontend/
│   ├── index.html                  # Semantic HTML5 shell with Leaflet & Chart.js
│   ├── styles/
│   │   └── main.css                # Editorial travel-tech design system tokens & styles
│   └── js/
│       └── app.js                  # Modular SPA router, map controller, and view renderers
├── docs/
│   ├── ER_DIAGRAM.md               # Mermaid ER diagram & cardinality rules
│   ├── DATABASE_SCHEMA_AND_NORMALIZATION.md # Formal 1NF/2NF/3NF proofs
│   ├── SYSTEM_ARCHITECTURE_AND_DFD.md       # Tiered architecture, Level 0/1/2 DFDs
│   ├── RECOMMENDATION_AND_SUSTAINABILITY_ALGORITHM.md # Mathematical formulations
│   └── API_DOCUMENTATION.md        # Comprehensive REST API reference
├── run_server.py                   # One-click platform launcher
├── test_system.py                  # Automated test suite (10/10 tests)
└── README.md                       # Master project documentation
```

---

## 4. Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Pre-installed packages: `fastapi`, `uvicorn`, `pydantic`

### Launch the Application
Run the single launcher command:
```bash
python run_server.py
```

Open your web browser and navigate to:
- **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)
- **OpenAPI ReDoc**: [http://127.0.0.1:8000/api/redoc](http://127.0.0.1:8000/api/redoc)

---

## 5. Demo Credentials

| Role | Email | Password | Permissions |
|:---|:---|:---|:---|
| **Administrator** | `admin@tripuraterra.in` | `Admin@Tripura2026` | Full CRUD, database audit, analytics |
| **Content Curator**| `curator@tripuraterra.in` | `Curator@Tripura2026` | Destination & cultural management |
| **Tourist** | `marcus.eco@traveler.org` | `Traveler@2026` | Bookmarks, review submission, custom trips |

---

## 6. Automated Verification

Execute the complete end-to-end test suite:
```bash
python test_system.py
```

### Verified Test Cases:
1. `test_01`: All 8 Tripura districts and initial destination records exist.
2. `test_02`: Foreign key enforcement blocks orphaned destination with invalid district.
3. `test_03`: Triggers `trg_review_after_insert` & `trg_review_after_delete` automatically recalculate ratings.
4. `test_04`: Analytical views (`vw_destination_full_profile`, `vw_district_analytics`) execute correctly.
5. `test_05`: ERI formula calculations, bounds, and sustainability tiers.
6. `test_06`: Recommendation multi-criteria scoring and transparent explanation generation.
7. `test_07`: Smart trip planner multi-day itinerary synthesis with transit optimization.
8. `test_08`: Destinations faceted search router across districts.
9. `test_09`: JWT login authentication and protected profile retrieval.
10. `test_10`: Research endpoints for live DBMS indexing benchmark and RecSys persona evaluation.

---

## 7. Authentic Tripura Data Coverage

The seed dataset incorporates verified geographic and cultural records across all 8 districts:
- **Rock Art & Temples**: Unakoti 7th-9th century bas-reliefs, Chabimura Gomati canyon reliefs, Pilak Buddhist-Hindu ruins, Tripura Sundari Shakti Peetha (Matabari), Kasba Kalibari.
- **Palaces & Heritage**: Neermahal Water Palace (Rudrasagar Ramsar Lake), Ujjayanta Palace & State Museum, Heritage Park.
- **Wildlife & Sanctuaries**: Sepahijala Wildlife Sanctuary (Clouded Leopard National Park & Phayre's Langur), Trishna Wildlife Sanctuary (Indian Gaur / Bison), Rowa Wildlife Sanctuary.
- **Lakes & Ridges**: Dumbur Lake archipelago (Narikel Kunja), Jampui Hills (Vanghmun model eco-village), Betlingchhip Peak (930m summit), Hathai Kotor (Baramura).
- **Indigenous Communities**: Tripuri (Debbarma), Reang (Bru), Jamatia, Chakma, Mizo (Lushai).
- **Crafts, Cuisine & Festivals**: Risa handloom weaving, bamboo crafts, Mui Borok / Chakhwi culinary heritage, Kharchi Puja, Garia Puja, Neermahal Water Festival.

---

## 8. Academic Attribution & License
Developed as an academic research and Database Management System (DBMS) showcase project for sustainable intelligent tourism.  
Released under the MIT License.
