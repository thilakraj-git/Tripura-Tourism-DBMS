# Entity-Relationship (ER) Diagram — Tripura Terra

## Overview
This document specifies the conceptual and logical data model for the **Tripura Terra** intelligent tourism platform. The database architecture is designed in Third Normal Form (3NF) to support transactional integrity, multi-dimensional sustainability indicators, explainable recommendations, and GIS location attributes.

---

## Complete Mermaid ER Diagram

```mermaid
erDiagram
    DISTRICTS ||--o{ DESTINATIONS : "contains"
    DISTRICTS ||--o{ EVENTS : "hosts"
    
    DESTINATIONS ||--o| ECO_SITES : "extends"
    DESTINATIONS ||--o| CULTURAL_SITES : "extends"
    DESTINATIONS ||--o| SUSTAINABILITY_METRICS : "assessed_by"
    DESTINATIONS ||--o{ EXPERIENCES : "offers"
    DESTINATIONS ||--o{ REVIEWS : "evaluated_in"
    DESTINATIONS ||--o{ SAVED_PLACES : "bookmarked_in"
    DESTINATIONS ||--o{ ITINERARY_ITEMS : "scheduled_in"
    DESTINATIONS ||--o{ EVENTS : "associated_with"

    USERS ||--o| USER_PREFERENCES : "defines"
    USERS ||--o{ REVIEWS : "authors"
    USERS ||--o{ SAVED_PLACES : "bookmarks"
    USERS ||--o{ ITINERARIES : "creates"

    ITINERARIES ||--|{ ITINERARY_ITEMS : "contains"

    DISTRICTS {
        int district_id PK
        string name UK
        string headquarters
        real area_sq_km
        real forest_cover_percent
        real center_latitude
        real center_longitude
        text description
    }

    DESTINATIONS {
        int destination_id PK
        int district_id FK
        string name
        string slug UK
        string destination_type
        text short_description
        text full_description
        real latitude
        real longitude
        int altitude_meters
        string best_season
        real recommended_duration_hours
        string difficulty_level
        string accessibility_level
        string crowd_density_level
        real entry_fee_inr
        int is_lesser_known
        real average_rating
        int total_reviews
        real eco_responsibility_index
    }

    ECO_SITES {
        int eco_id PK
        int destination_id FK,UK
        string ecosystem_type
        text biodiversity_significance
        text key_flora
        text key_fauna
        string conservation_status
        int carrying_capacity_per_day
        int guide_mandatory
        int plastic_free_zone
        real trail_length_km
        string best_birdwatching_time
    }

    CULTURAL_SITES {
        int culture_id PK
        int destination_id FK,UK
        string historical_epoch
        string architectural_style
        string indigenous_community_link
        text cultural_significance
        text rituals_and_folklore
        text dress_code_guidelines
        string photography_allowed
        string preservation_agency
    }

    SUSTAINABILITY_METRICS {
        int metric_id PK
        int destination_id FK,UK
        real biodiversity_index
        real environmental_sensitivity
        real waste_management_score
        real community_employment_score
        real visitor_pressure_score
        real sustainable_transit_score
        real water_conservation_score
        string data_source_type
        int audit_year
    }

    EXPERIENCES {
        int experience_id PK
        int destination_id FK
        string title
        string category
        text description
        int duration_minutes
        real cost_inr
        int max_participants
        string community_beneficiary
        string eco_footprint_rating
    }

    INDIGENOUS_COMMUNITIES {
        int community_id PK
        string name UK
        string primary_language
        text traditional_occupations
        text cultural_hallmark
        text crafts_heritage
        text dance_forms
        text respectful_engagement_code
        string associated_districts
    }

    USERS {
        int user_id PK
        string full_name
        string email UK
        string password_hash
        string role
        string country
        int is_active
        timestamp created_at
        timestamp last_login
    }

    USER_PREFERENCES {
        int preference_id PK
        int user_id FK,UK
        string preferred_travel_style
        string budget_tier
        string preferred_pace
        real nature_weight
        real culture_weight
        int requires_accessibility
        int max_travel_hours_per_day
    }

    REVIEWS {
        int review_id PK
        int user_id FK
        int destination_id FK
        real overall_rating
        real cleanliness_rating
        real eco_practice_rating
        real community_respect_rating
        string review_title
        text review_text
        string visit_month_year
        int is_verified_visit
    }

    ITINERARIES {
        int itinerary_id PK
        int user_id FK
        string title
        int total_days
        real budget_inr
        string travel_style
        real estimated_distance_km
        real composite_eco_score
        text explanation_notes
    }

    ITINERARY_ITEMS {
        int item_id PK
        int itinerary_id FK
        int destination_id FK
        int day_number
        string time_slot
        int sequence_order
        text activity_note
        real transit_km_from_prev
    }

    SAVED_PLACES {
        int save_id PK
        int user_id FK
        int destination_id FK
        text notes
        timestamp saved_at
    }

    EVENTS {
        int event_id PK
        int district_id FK
        int destination_id FK
        string name
        string category
        date start_date
        date end_date
        text significance
        text guidelines_for_tourists
        string location_details
    }

    QUERY_AUDIT_LOGS {
        int log_id PK
        string query_label
        string query_type
        int has_indexes
        real execution_time_ms
        int rows_returned
        text plan_summary
        timestamp executed_at
    }
```

---

## Cardinality and Referential Integrity Rules

| Relationship | Cardinality | Enforcement | Cascade Action |
|:---|:---:|:---|:---|
| `districts` $\rightarrow$ `destinations` | $1 : N$ | Foreign Key (`district_id`) | `ON DELETE RESTRICT` |
| `destinations` $\rightarrow$ `eco_sites` | $1 : 0..1$ | Foreign Key (`destination_id`) Unique | `ON DELETE CASCADE` |
| `destinations` $\rightarrow$ `cultural_sites` | $1 : 0..1$ | Foreign Key (`destination_id`) Unique | `ON DELETE CASCADE` |
| `destinations` $\rightarrow$ `sustainability_metrics` | $1 : 1$ | Foreign Key (`destination_id`) Unique | `ON DELETE CASCADE` |
| `destinations` $\rightarrow$ `experiences` | $1 : N$ | Foreign Key (`destination_id`) | `ON DELETE CASCADE` |
| `users` $\rightarrow$ `user_preferences` | $1 : 1$ | Foreign Key (`user_id`) Unique | `ON DELETE CASCADE` |
| `users` $\times$ `destinations` $\rightarrow$ `reviews` | $M : N$ | Composite Unique (`user_id`, `destination_id`) | `ON DELETE CASCADE` |
| `users` $\times$ `destinations` $\rightarrow$ `saved_places`| $M : N$ | Composite Unique (`user_id`, `destination_id`) | `ON DELETE CASCADE` |
| `users` $\rightarrow$ `itineraries` | $1 : N$ | Foreign Key (`user_id`) | `ON DELETE CASCADE` |
| `itineraries` $\rightarrow$ `itinerary_items` | $1 : N$ | Foreign Key (`itinerary_id`) | `ON DELETE CASCADE` |
| `destinations` $\rightarrow$ `itinerary_items` | $1 : N$ | Foreign Key (`destination_id`) | `ON DELETE CASCADE` |
| `districts` $\rightarrow$ `events` | $1 : N$ | Foreign Key (`district_id`) | `ON DELETE RESTRICT` |
