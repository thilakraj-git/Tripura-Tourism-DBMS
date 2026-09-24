-- ============================================================================
-- TRIPURA TERRA: RELATIONAL DATABASE MANAGEMENT SYSTEM SCHEMA
-- Specification: 3NF Normalized Architecture with Referential Integrity,
-- Constraints, Triggers, Views, and Spatial/B-tree Indexing.
-- Compatible with SQLite 3.37+ and PostgreSQL 14+
-- ============================================================================

-- Enforce foreign keys (SQLite specific runtime pragma)
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. DISTRICTS TABLE
-- Captures Tripura's 8 administrative geographic divisions.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS districts (
    district_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    headquarters VARCHAR(50) NOT NULL,
    area_sq_km REAL NOT NULL CHECK(area_sq_km > 0),
    forest_cover_percent REAL NOT NULL CHECK(forest_cover_percent >= 0 AND forest_cover_percent <= 100),
    center_latitude REAL NOT NULL CHECK(center_latitude BETWEEN 23.0 AND 24.6),
    center_longitude REAL NOT NULL CHECK(center_longitude BETWEEN 91.0 AND 92.6),
    description TEXT
);

-- ----------------------------------------------------------------------------
-- 2. USERS TABLE
-- Role-based authentication and user profiles.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE CHECK(email LIKE '%@%.%'),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'tourist' CHECK(role IN ('tourist', 'content_manager', 'admin')),
    country VARCHAR(60) DEFAULT 'India',
    is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 3. USER PREFERENCES TABLE (1:1 with USERS, normalized)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_preferences (
    preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    preferred_travel_style VARCHAR(30) DEFAULT 'slow_travel' CHECK(preferred_travel_style IN ('slow_travel', 'adventure', 'cultural_immersion', 'nature_retreat', 'family_eco')),
    budget_tier VARCHAR(20) DEFAULT 'medium' CHECK(budget_tier IN ('budget', 'medium', 'premium')),
    preferred_pace VARCHAR(20) DEFAULT 'moderate' CHECK(preferred_pace IN ('relaxed', 'moderate', 'intensive')),
    nature_weight REAL DEFAULT 0.5 CHECK(nature_weight BETWEEN 0 AND 1),
    culture_weight REAL DEFAULT 0.5 CHECK(culture_weight BETWEEN 0 AND 1),
    requires_accessibility INTEGER DEFAULT 0 CHECK(requires_accessibility IN (0, 1)),
    max_travel_hours_per_day INTEGER DEFAULT 6 CHECK(max_travel_hours_per_day BETWEEN 1 AND 14),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 4. DESTINATIONS TABLE
-- Central entity for all discoverable sites across Tripura.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS destinations (
    destination_id INTEGER PRIMARY KEY AUTOINCREMENT,
    district_id INTEGER NOT NULL,
    name VARCHAR(120) NOT NULL,
    slug VARCHAR(130) NOT NULL UNIQUE,
    tagline VARCHAR(200),
    destination_type VARCHAR(40) NOT NULL CHECK(destination_type IN (
        'eco_sanctuary', 'cultural_heritage', 'rock_carving', 'royal_palace', 
        'lake_wetland', 'tribal_settlement', 'tea_estate', 'hill_station', 'temple_complex'
    )),
    short_description TEXT NOT NULL,
    full_description TEXT NOT NULL,
    latitude REAL NOT NULL CHECK(latitude BETWEEN 23.0 AND 24.6),
    longitude REAL NOT NULL CHECK(longitude BETWEEN 91.0 AND 92.6),
    altitude_meters INTEGER DEFAULT 50,
    best_season VARCHAR(80) NOT NULL,
    recommended_duration_hours REAL NOT NULL CHECK(recommended_duration_hours > 0),
    difficulty_level VARCHAR(20) NOT NULL DEFAULT 'Easy' CHECK(difficulty_level IN ('Easy', 'Moderate', 'Challenging')),
    accessibility_level VARCHAR(20) NOT NULL DEFAULT 'Full' CHECK(accessibility_level IN ('Full', 'Partial', 'Limited')),
    crowd_density_level VARCHAR(20) NOT NULL DEFAULT 'Low' CHECK(crowd_density_level IN ('Very Low', 'Low', 'Moderate', 'High')),
    entry_fee_inr REAL DEFAULT 0.0 CHECK(entry_fee_inr >= 0),
    is_lesser_known INTEGER DEFAULT 0 CHECK(is_lesser_known IN (0, 1)),
    is_verified INTEGER DEFAULT 1 CHECK(is_verified IN (0, 1)),
    image_url VARCHAR(255) NOT NULL,
    thumbnail_url VARCHAR(255),
    average_rating REAL DEFAULT 0.0 CHECK(average_rating BETWEEN 0.0 AND 5.0),
    total_reviews INTEGER DEFAULT 0 CHECK(total_reviews >= 0),
    eco_responsibility_index REAL DEFAULT 70.0 CHECK(eco_responsibility_index BETWEEN 0.0 AND 100.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES districts(district_id) ON DELETE RESTRICT
);

-- ----------------------------------------------------------------------------
-- 5. ECO SITES TABLE (Extension entity for ecological destinations)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS eco_sites (
    eco_id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL UNIQUE,
    ecosystem_type VARCHAR(60) NOT NULL,
    biodiversity_significance TEXT NOT NULL,
    key_flora TEXT,
    key_fauna TEXT,
    conservation_status VARCHAR(50) NOT NULL,
    carrying_capacity_per_day INTEGER NOT NULL CHECK(carrying_capacity_per_day > 0),
    guide_mandatory INTEGER DEFAULT 0 CHECK(guide_mandatory IN (0, 1)),
    plastic_free_zone INTEGER DEFAULT 1 CHECK(plastic_free_zone IN (0, 1)),
    trail_length_km REAL DEFAULT 0.0 CHECK(trail_length_km >= 0.0),
    best_birdwatching_time VARCHAR(80),
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 6. CULTURAL SITES TABLE (Extension entity for cultural & heritage sites)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cultural_sites (
    culture_id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL UNIQUE,
    historical_epoch VARCHAR(80) NOT NULL,
    architectural_style VARCHAR(80),
    indigenous_community_link VARCHAR(100),
    cultural_significance TEXT NOT NULL,
    rituals_and_folklore TEXT,
    dress_code_guidelines TEXT,
    photography_allowed VARCHAR(20) DEFAULT 'Yes' CHECK(photography_allowed IN ('Yes', 'No', 'Restricted', 'Fee Required')),
    preservation_agency VARCHAR(100) DEFAULT 'Archaeological Survey of India / State Dept of Cultural Affairs',
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 7. EXPERIENCES TABLE
-- Local community-led and sustainable tourism activities.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS experiences (
    experience_id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL,
    title VARCHAR(120) NOT NULL,
    category VARCHAR(50) NOT NULL CHECK(category IN ('tribal_craft', 'local_culinary', 'guided_trek', 'birding', 'boat_safari', 'cultural_dance', 'pottery_workshop')),
    description TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK(duration_minutes BETWEEN 15 AND 720),
    cost_inr REAL NOT NULL CHECK(cost_inr >= 0),
    max_participants INTEGER DEFAULT 12 CHECK(max_participants > 0),
    community_beneficiary VARCHAR(100) NOT NULL,
    eco_footprint_rating VARCHAR(10) DEFAULT 'Low' CHECK(eco_footprint_rating IN ('Very Low', 'Low', 'Moderate')),
    is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 8. INDIGENOUS COMMUNITIES & CRAFTS (Cultural Knowledge Base)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS indigenous_communities (
    community_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(80) NOT NULL UNIQUE,
    primary_language VARCHAR(60) NOT NULL,
    traditional_occupations TEXT NOT NULL,
    cultural_hallmark TEXT NOT NULL,
    crafts_heritage TEXT NOT NULL,
    dance_forms TEXT NOT NULL,
    respectful_engagement_code TEXT NOT NULL,
    associated_districts VARCHAR(120) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 9. SUSTAINABILITY METRICS TABLE
-- Normalized measurable parameters backing the Eco Responsibility Index (ERI).
-- Documented: Prototype / Demonstration vs Verified Baseline.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sustainability_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL UNIQUE,
    biodiversity_index REAL NOT NULL CHECK(biodiversity_index BETWEEN 0 AND 100),
    environmental_sensitivity REAL NOT NULL CHECK(environmental_sensitivity BETWEEN 0 AND 100),
    waste_management_score REAL NOT NULL CHECK(waste_management_score BETWEEN 0 AND 100),
    community_employment_score REAL NOT NULL CHECK(community_employment_score BETWEEN 0 AND 100),
    visitor_pressure_score REAL NOT NULL CHECK(visitor_pressure_score BETWEEN 0 AND 100),
    sustainable_transit_score REAL NOT NULL CHECK(sustainable_transit_score BETWEEN 0 AND 100),
    water_conservation_score REAL NOT NULL CHECK(water_conservation_score BETWEEN 0 AND 100),
    data_source_type VARCHAR(40) DEFAULT 'Verified Baseline' CHECK(data_source_type IN ('Verified Baseline', 'Prototype Model', 'Field Survey Pending')),
    audit_year INTEGER NOT NULL DEFAULT 2026,
    last_assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 10. REVIEWS TABLE
-- User feedback with multi-attribute rating criteria.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    overall_rating REAL NOT NULL CHECK(overall_rating BETWEEN 1.0 AND 5.0),
    cleanliness_rating REAL CHECK(cleanliness_rating BETWEEN 1.0 AND 5.0),
    eco_practice_rating REAL CHECK(eco_practice_rating BETWEEN 1.0 AND 5.0),
    community_respect_rating REAL CHECK(community_respect_rating BETWEEN 1.0 AND 5.0),
    review_title VARCHAR(120),
    review_text TEXT NOT NULL,
    visit_month_year VARCHAR(30),
    is_verified_visit INTEGER DEFAULT 1 CHECK(is_verified_visit IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id) ON DELETE CASCADE,
    CONSTRAINT uq_user_dest_review UNIQUE (user_id, destination_id)
);

-- ----------------------------------------------------------------------------
-- 11. ITINERARIES TABLE
-- User-saved or planner-generated trip schedules.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS itineraries (
    itinerary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(120) NOT NULL,
    total_days INTEGER NOT NULL CHECK(total_days BETWEEN 1 AND 14),
    budget_inr REAL CHECK(budget_inr >= 0),
    travel_style VARCHAR(40) NOT NULL,
    estimated_distance_km REAL DEFAULT 0.0 CHECK(estimated_distance_km >= 0),
    composite_eco_score REAL CHECK(composite_eco_score BETWEEN 0 AND 100),
    explanation_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 12. ITINERARY ITEMS TABLE (1:M with ITINERARY)
-- Day-by-day scheduled visits with sequence.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS itinerary_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    itinerary_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    day_number INTEGER NOT NULL CHECK(day_number BETWEEN 1 AND 14),
    time_slot VARCHAR(20) NOT NULL CHECK(time_slot IN ('Morning', 'Afternoon', 'Evening', 'Full Day')),
    sequence_order INTEGER NOT NULL CHECK(sequence_order >= 1),
    activity_note TEXT,
    transit_km_from_prev REAL DEFAULT 0.0 CHECK(transit_km_from_prev >= 0),
    FOREIGN KEY (itinerary_id) REFERENCES itineraries(itinerary_id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id) ON DELETE CASCADE,
    CONSTRAINT uq_itinerary_slot UNIQUE (itinerary_id, day_number, sequence_order)
);

-- ----------------------------------------------------------------------------
-- 13. SAVED PLACES TABLE (Bookmarks)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS saved_places (
    save_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    notes TEXT,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id) ON DELETE CASCADE,
    CONSTRAINT uq_user_saved_place UNIQUE (user_id, destination_id)
);

-- ----------------------------------------------------------------------------
-- 14. EVENTS AND FESTIVALS TABLE
-- Cultural celebrations, conservation drives, seasonal fairs.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    district_id INTEGER NOT NULL,
    destination_id INTEGER,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(40) NOT NULL CHECK(category IN ('Religious Festival', 'Indigenous Celebration', 'Eco Workshop', 'Craft Fair', 'Water Carnival')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    significance TEXT NOT NULL,
    guidelines_for_tourists TEXT NOT NULL,
    location_details VARCHAR(150) NOT NULL,
    image_url VARCHAR(255),
    FOREIGN KEY (district_id) REFERENCES districts(district_id) ON DELETE RESTRICT,
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id) ON DELETE SET NULL
);

-- ----------------------------------------------------------------------------
-- 15. QUERY PERFORMANCE AUDIT LOG TABLE
-- Used for research benchmarking (indexed vs non-indexed execution timing).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS query_audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_label VARCHAR(80) NOT NULL,
    query_type VARCHAR(40) NOT NULL,
    has_indexes INTEGER NOT NULL CHECK(has_indexes IN (0, 1)),
    execution_time_ms REAL NOT NULL,
    rows_returned INTEGER NOT NULL,
    plan_summary TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE AND SPATIAL/SEARCH RETRIEVAL
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_destinations_district ON destinations(district_id);
CREATE INDEX IF NOT EXISTS idx_destinations_type ON destinations(destination_type);
CREATE INDEX IF NOT EXISTS idx_destinations_eco_score ON destinations(eco_responsibility_index DESC);
CREATE INDEX IF NOT EXISTS idx_destinations_rating ON destinations(average_rating DESC);
CREATE INDEX IF NOT EXISTS idx_destinations_coords ON destinations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_reviews_destination ON reviews(destination_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user ON reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_itinerary_items_itin ON itinerary_items(itinerary_id, day_number);
CREATE INDEX IF NOT EXISTS idx_experiences_destination ON experiences(destination_id);
CREATE INDEX IF NOT EXISTS idx_saved_places_user ON saved_places(user_id);
CREATE INDEX IF NOT EXISTS idx_events_dates ON events(start_date, end_date);

-- ============================================================================
-- VIEWS FOR COMPLEX QUERY ENCAPSULATION & ANALYTICS
-- ============================================================================

-- 1. Full Destination Composite View (Joins 5 tables)
CREATE VIEW IF NOT EXISTS vw_destination_full_profile AS
SELECT 
    d.destination_id,
    d.name,
    d.slug,
    d.tagline,
    d.destination_type,
    d.short_description,
    d.full_description,
    d.latitude,
    d.longitude,
    d.altitude_meters,
    d.best_season,
    d.recommended_duration_hours,
    d.difficulty_level,
    d.accessibility_level,
    d.crowd_density_level,
    d.entry_fee_inr,
    d.is_lesser_known,
    d.is_verified,
    d.image_url,
    d.average_rating,
    d.total_reviews,
    d.eco_responsibility_index,
    dist.district_id,
    dist.name AS district_name,
    dist.forest_cover_percent,
    es.ecosystem_type,
    es.carrying_capacity_per_day,
    es.key_fauna,
    es.key_flora,
    cs.historical_epoch,
    cs.architectural_style,
    cs.indigenous_community_link,
    sm.biodiversity_index,
    sm.environmental_sensitivity,
    sm.waste_management_score,
    sm.community_employment_score,
    sm.visitor_pressure_score,
    sm.sustainable_transit_score,
    sm.data_source_type
FROM destinations d
JOIN districts dist ON d.district_id = dist.district_id
LEFT JOIN eco_sites es ON d.destination_id = es.destination_id
LEFT JOIN cultural_sites cs ON d.destination_id = cs.destination_id
LEFT JOIN sustainability_metrics sm ON d.destination_id = sm.destination_id;

-- 2. Ranked Eco Destinations View
CREATE VIEW IF NOT EXISTS vw_eco_rankings AS
SELECT 
    d.destination_id,
    d.name,
    dist.name AS district_name,
    d.destination_type,
    d.eco_responsibility_index,
    sm.biodiversity_index,
    sm.waste_management_score,
    sm.community_employment_score,
    sm.visitor_pressure_score,
    d.average_rating,
    RANK() OVER (ORDER BY d.eco_responsibility_index DESC) as eco_rank
FROM destinations d
JOIN districts dist ON d.district_id = dist.district_id
JOIN sustainability_metrics sm ON d.destination_id = sm.destination_id;

-- 3. District Analytics Rollup View
CREATE VIEW IF NOT EXISTS vw_district_analytics AS
SELECT 
    dist.district_id,
    dist.name AS district_name,
    dist.area_sq_km,
    dist.forest_cover_percent,
    COUNT(d.destination_id) AS total_destinations,
    ROUND(AVG(d.eco_responsibility_index), 2) AS avg_eco_responsibility,
    ROUND(AVG(d.average_rating), 2) AS avg_user_rating,
    SUM(CASE WHEN d.destination_type IN ('eco_sanctuary', 'lake_wetland', 'hill_station') THEN 1 ELSE 0 END) AS eco_destination_count,
    SUM(CASE WHEN d.destination_type IN ('cultural_heritage', 'rock_carving', 'royal_palace', 'temple_complex') THEN 1 ELSE 0 END) AS cultural_destination_count,
    SUM(CASE WHEN d.is_lesser_known = 1 THEN 1 ELSE 0 END) AS lesser_known_count
FROM districts dist
LEFT JOIN destinations d ON dist.district_id = d.district_id
GROUP BY dist.district_id, dist.name, dist.area_sq_km, dist.forest_cover_percent;

-- ============================================================================
-- TRIGGERS FOR DATA INTEGRITY & AUTOMATED RECALCULATION
-- ============================================================================

-- Trigger 1: Recalculate average rating & total reviews on review insert
CREATE TRIGGER IF NOT EXISTS trg_review_after_insert
AFTER INSERT ON reviews
BEGIN
    UPDATE destinations 
    SET 
        average_rating = ROUND((
            SELECT AVG(overall_rating) FROM reviews WHERE destination_id = NEW.destination_id
        ), 2),
        total_reviews = (
            SELECT COUNT(*) FROM reviews WHERE destination_id = NEW.destination_id
        )
    WHERE destination_id = NEW.destination_id;
END;

-- Trigger 2: Recalculate average rating & total reviews on review delete
CREATE TRIGGER IF NOT EXISTS trg_review_after_delete
AFTER DELETE ON reviews
BEGIN
    UPDATE destinations 
    SET 
        average_rating = COALESCE(ROUND((
            SELECT AVG(overall_rating) FROM reviews WHERE destination_id = OLD.destination_id
        ), 2), 0.0),
        total_reviews = (
            SELECT COUNT(*) FROM reviews WHERE destination_id = OLD.destination_id
        )
    WHERE destination_id = OLD.destination_id;
END;

-- Trigger 3: Recalculate Eco Responsibility Index on sustainability metrics update
-- Formula: ERI = 0.25*Bio + 0.20*(100-Sens_Vulnerability_Factor) + 0.15*Waste + 0.15*Comm + 0.15*(100-VisitorPressure) + 0.10*Transit
CREATE TRIGGER IF NOT EXISTS trg_sustainability_metric_update
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
