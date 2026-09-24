# REST API Specification — Tripura Terra

## Base URL
- Local Server: `http://127.0.0.1:8000`
- Interactive OpenAPI Swagger UI: `http://127.0.0.1:8000/api/docs`
- Interactive ReDoc: `http://127.0.0.1:8000/api/redoc`

---

## 1. Authentication & Users

### `POST /api/v1/auth/login`
Authenticates a user and issues a signed JWT token.
- **Request Body**:
  ```json
  {
    "email": "marcus.eco@traveler.org",
    "password": "Traveler@2026"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "token": "eyJhbGciOi...",
    "user": {
      "user_id": 3,
      "full_name": "Marcus Lindqvist",
      "email": "marcus.eco@traveler.org",
      "role": "tourist",
      "country": "Sweden"
    }
  }
  ```

### `GET /api/v1/auth/me`
Retrieves authenticated user profile, preferences, and activity counters.
- **Headers**: `Authorization: Bearer <token>`
- **Response (200 OK)**: Returns user object with saved places count, trip count, and reviews count.

### `PUT /api/v1/users/preferences`
Updates traveler interest weights and pacing settings.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "preferred_travel_style": "slow_travel",
    "budget_tier": "medium",
    "preferred_pace": "moderate",
    "nature_weight": 0.8,
    "culture_weight": 0.7,
    "requires_accessibility": 0,
    "max_travel_hours_per_day": 6
  }
  ```

---

## 2. Destinations

### `GET /api/v1/destinations`
Faceted search across destinations with filtering and composite index sorting.
- **Query Parameters**:
  - `district` (string, optional): e.g. `West Tripura`, `Unakoti`, `Gomati`
  - `destination_type` (string, optional): e.g. `eco_sanctuary`, `rock_carving`, `hill_station`
  - `min_eco_score` (float, optional): minimum ERI score (0.0 to 100.0)
  - `crowd_level` (string, optional): `Very Low`, `Low`, `Moderate`, `High`
  - `search` (string, optional): free-text keyword search
  - `sort_by` (string, default `eco_score_desc`): `eco_score_desc`, `rating_desc`, `name_asc`
- **Response (200 OK)**: Array of destinations with district names and calculated ERI tier badges.

### `GET /api/v1/destinations/{id_or_slug}`
Returns the comprehensive 14-section information architecture profile.
- **Parameters**: `id_or_slug` (integer ID or string slug, e.g. `unakoti-rock-cut-reliefs`)
- **Response (200 OK)**:
  - `profile`: base destination and geographic coordinates
  - `eco_details`: habitat type, flora, fauna, daily carrying capacity, trail length
  - `cultural_details`: historical epoch, architectural style, rituals, etiquette
  - `sustainability`: composite ERI score and weighted sub-indicator progress values
  - `experiences`: community-led guided tours and workshops
  - `reviews`: verified traveler feedback and multi-criteria ratings
  - `nearby_destinations`: proximity-filtered suggestions
  - `is_saved`: boolean status for authenticated user

### `POST /api/v1/destinations/{id}/reviews`
Submits a tourist review; automatically recalculates destination average rating and count via database triggers.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "overall_rating": 4.9,
    "cleanliness_rating": 5.0,
    "eco_practice_rating": 5.0,
    "community_respect_rating": 5.0,
    "review_title": "Pristine morning hike",
    "review_text": "Remarkable conservation standards.",
    "visit_month_year": "September 2026"
  }
  ```

---

## 3. Smart Trip Planner

### `POST /api/v1/planner/generate`
Synthesizes a structured multi-day itinerary with district geographic clustering and explainability.
- **Request Body**:
  ```json
  {
    "days": 3,
    "budget": 12000.0,
    "travel_style": "slow_travel",
    "preferred_district": "all",
    "nature_weight": 0.7,
    "culture_weight": 0.6
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "data": {
      "title": "Tripura 3-Day Sustainable Slow Travel Journey",
      "total_days": 3,
      "estimated_budget_inr": 9250.0,
      "estimated_distance_km": 215.0,
      "composite_eco_score": 90.8,
      "eco_tier": "Elite Sustainable Itinerary",
      "explanation": "Crafted for 3 days of slow travel...",
      "daily_schedule": [ ... ]
    }
  }
  ```

### `POST /api/v1/itineraries/save`
Atomically persists the generated itinerary and schedule items.
- **Headers**: `Authorization: Bearer <token>`

---

## 4. Analytics & Research Endpoints

### `GET /api/v1/analytics/overview`
Returns high-level state KPIs (destinations count, ERI average, ratings).

### `GET /api/v1/analytics/district-rollup`
Returns grouped data from view `vw_district_analytics`.

### `POST /api/v1/research/benchmark-db`
Executes live query performance tests comparing indexed vs unindexed executions across 4 complex SQL joins and logs execution metrics into `query_audit_logs`.

### `POST /api/v1/research/evaluate-recommendations`
Evaluates Precision@5, Recall@5, NDCG@5, and Intra-List Diversity across 4 synthetic persona cohorts.
