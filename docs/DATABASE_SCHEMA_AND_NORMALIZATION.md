# Relational Database Schema & Normalization Proof — Tripura Terra

## 1. Formal Relational Schema Specification

In standard relational notation (Primary Keys are **bold underlined**, Foreign Keys are marked with $(FK)$):

1. **DISTRICTS** (**<u>district_id</u>**, name, headquarters, area_sq_km, forest_cover_percent, center_latitude, center_longitude, description)
2. **USERS** (**<u>user_id</u>**, full_name, email, password_hash, role, country, is_active, created_at, last_login)
3. **USER_PREFERENCES** (**<u>preference_id</u>**, user_id$(FK)$, preferred_travel_style, budget_tier, preferred_pace, nature_weight, culture_weight, requires_accessibility, max_travel_hours_per_day, updated_at)
4. **DESTINATIONS** (**<u>destination_id</u>**, district_id$(FK)$, name, slug, tagline, destination_type, short_description, full_description, latitude, longitude, altitude_meters, best_season, recommended_duration_hours, difficulty_level, accessibility_level, crowd_density_level, entry_fee_inr, is_lesser_known, is_verified, image_url, thumbnail_url, average_rating, total_reviews, eco_responsibility_index, created_at, updated_at)
5. **ECO_SITES** (**<u>eco_id</u>**, destination_id$(FK)$, ecosystem_type, biodiversity_significance, key_flora, key_fauna, conservation_status, carrying_capacity_per_day, guide_mandatory, plastic_free_zone, trail_length_km, best_birdwatching_time)
6. **CULTURAL_SITES** (**<u>culture_id</u>**, destination_id$(FK)$, historical_epoch, architectural_style, indigenous_community_link, cultural_significance, rituals_and_folklore, dress_code_guidelines, photography_allowed, preservation_agency)
7. **SUSTAINABILITY_METRICS** (**<u>metric_id</u>**, destination_id$(FK)$, biodiversity_index, environmental_sensitivity, waste_management_score, community_employment_score, visitor_pressure_score, sustainable_transit_score, water_conservation_score, data_source_type, audit_year, last_assessed_at)
8. **EXPERIENCES** (**<u>experience_id</u>**, destination_id$(FK)$, title, category, description, duration_minutes, cost_inr, max_participants, community_beneficiary, eco_footprint_rating, is_active)
9. **INDIGENOUS_COMMUNITIES** (**<u>community_id</u>**, name, primary_language, traditional_occupations, cultural_hallmark, crafts_heritage, dance_forms, respectful_engagement_code, associated_districts)
10. **REVIEWS** (**<u>review_id</u>**, user_id$(FK)$, destination_id$(FK)$, overall_rating, cleanliness_rating, eco_practice_rating, community_respect_rating, review_title, review_text, visit_month_year, is_verified_visit, created_at)
11. **ITINERARIES** (**<u>itinerary_id</u>**, user_id$(FK)$, title, total_days, budget_inr, travel_style, estimated_distance_km, composite_eco_score, explanation_notes, created_at)
12. **ITINERARY_ITEMS** (**<u>item_id</u>**, itinerary_id$(FK)$, destination_id$(FK)$, day_number, time_slot, sequence_order, activity_note, transit_km_from_prev)
13. **SAVED_PLACES** (**<u>save_id</u>**, user_id$(FK)$, destination_id$(FK)$, notes, saved_at)
14. **EVENTS** (**<u>event_id</u>**, district_id$(FK)$, destination_id$(FK)$, name, category, start_date, end_date, significance, guidelines_for_tourists, location_details, image_url)
15. **QUERY_AUDIT_LOGS** (**<u>log_id</u>**, query_label, query_type, has_indexes, execution_time_ms, rows_returned, plan_summary, executed_at)

---

## 2. Formal Proof of Normalization up to 3NF

### 2.1 First Normal Form (1NF)
**Requirement**: Each relation must have atomic (indivisible) attribute domains, unique row identifiers (candidate keys), and no repeating groups.
- All attribute domains are atomic scalar types (`INTEGER`, `REAL`, `VARCHAR`, `TIMESTAMP`).
- Multi-valued attributes were avoided:
  - Rather than storing multiple community experiences inside a destination text column, experiences are normalized into the separate relation `EXPERIENCES`.
  - Rather than storing multi-day schedule items as JSON arrays or comma-delimited strings inside `ITINERARIES`, each day/slot visit is stored as an individual row in `ITINERARY_ITEMS`.
- Every relation defines a primary key (`PRIMARY KEY AUTOINCREMENT`).

$$\therefore \text{The schema satisfies First Normal Form (1NF).}$$

---

### 2.2 Second Normal Form (2NF)
**Requirement**: The relation must be in 1NF, and every non-prime attribute must be fully functionally dependent on the entire primary key (i.e., no partial dependency on a proper subset of any candidate key).
- In relations with single-column surrogate primary keys (`destination_id`, `district_id`, `user_id`, etc.), partial dependency is impossible because proper subsets of a single-column key do not exist.
- In composite candidate key relations:
  - `REVIEWS` has candidate key $(user\_id, destination\_id)$:
    - $FD_1: (user\_id, destination\_id) \rightarrow overall\_rating, cleanliness\_rating, review\_text$
    - No non-prime attribute depends on only $user\_id$ or only $destination\_id$. (e.g., user name is stored in `USERS`, destination name is in `DESTINATIONS`).
  - `ITINERARY_ITEMS` has alternate unique constraint $(itinerary\_id, day\_number, sequence\_order)$:
    - $FD_2: (itinerary\_id, day\_number, sequence\_order) \rightarrow destination\_id, activity\_note, transit\_km$
    - All non-prime attributes require the full tuple key to be determined.

$$\therefore \text{The schema satisfies Second Normal Form (2NF).}$$

---

### 2.3 Third Normal Form (3NF)
**Requirement**: The relation must be in 2NF, and no non-prime attribute is transitively dependent on the primary key (i.e., for every non-trivial functional dependency $X \rightarrow Y$, either $X$ is a superkey, or $Y$ is a prime attribute).
- Analysis of potential transitive dependencies:
  - In `DESTINATIONS`:
    - District details ($forest\_cover\_percent$, $headquarters$) depend on $district\_id$, which in turn depends on $destination\_id$.
    - **Normalization applied**: District details were decomposed into the separate `DISTRICTS` relation. `DESTINATIONS` retains only the foreign key `district_id`.
  - In `ECO_SITES` and `CULTURAL_SITES`:
    - Ecological parameters ($carrying\_capacity$, $biodiversity\_significance$) only apply to eco sites, not all destinations.
    - Storing them in `DESTINATIONS` would produce excessive NULLs and partial transitive relationships.
    - **Normalization applied**: Vertical decomposition into subtype extension tables (`ECO_SITES`, `CULTURAL_SITES`) using $1:0..1$ foreign key relationships.
  - In `SUSTAINABILITY_METRICS`:
    - Raw environmental indicator readings ($biodiversity\_index$, $waste\_management\_score$, $visitor\_pressure\_score$) are decoupled from transient destination metadata, allowing temporal re-auditing ($audit\_year$) without mutating the parent destination entity.

$$\therefore \text{The schema satisfies Third Normal Form (3NF).}$$

---

## 3. Database Triggers Specification

### 3.1 `trg_review_after_insert` / `trg_review_after_delete`
Automatically recalculates the aggregate rating and review count on the destination table whenever reviews change:
```sql
CREATE TRIGGER trg_review_after_insert
AFTER INSERT ON reviews
BEGIN
    UPDATE destinations 
    SET 
        average_rating = ROUND((SELECT AVG(overall_rating) FROM reviews WHERE destination_id = NEW.destination_id), 2),
        total_reviews = (SELECT COUNT(*) FROM reviews WHERE destination_id = NEW.destination_id)
    WHERE destination_id = NEW.destination_id;
END;
```

### 3.2 `trg_sustainability_metric_update`
Maintains synchronization between raw sustainability metrics and the pre-computed composite Eco Responsibility Index:
```sql
CREATE TRIGGER trg_sustainability_metric_update
AFTER UPDATE ON sustainability_metrics
BEGIN
    UPDATE destinations
    SET 
        eco_responsibility_index = ROUND((
            0.25 * NEW.biodiversity_index +
            0.20 * (100.0 - (NEW.environmental_sensitivity * 0.3)) + 
            0.15 * NEW.waste_management_score +
            0.15 * NEW.community_employment_score +
            0.15 * (100.0 - NEW.visitor_pressure_score) +
            0.10 * NEW.sustainable_transit_score
        ), 1),
        updated_at = CURRENT_TIMESTAMP
    WHERE destination_id = NEW.destination_id;
END;
```

---

## 4. Analytical Views

1. **`vw_destination_full_profile`**: Integrates `destinations`, `districts`, `eco_sites`, `cultural_sites`, and `sustainability_metrics` for atomic retrieval.
2. **`vw_eco_rankings`**: Computes state-wide percentile and ordinal rank based on the ERI index using SQL window functions (`RANK() OVER (ORDER BY eco_responsibility_index DESC)`).
3. **`vw_district_analytics`**: Aggregates total sites, mean eco scores, forest cover percentages, and cultural site ratios across all 8 districts.
