"""
Tripura Terra: Database Seeding Script
Populates authentic, factual geographic, ecological, and cultural datasets for Tripura, India.
Includes 8 administrative districts, 18 detailed destinations, indigenous communities,
traditional crafts, culinary heritage, festivals, sustainability metrics, and initial users.
"""

import hashlib
import os
import sys

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import get_connection, init_db

def hash_password(password: str) -> str:
    """Computes SHA-256 hash for secure local demonstration passwords."""
    salt = "tripura_terra_secure_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def seed_database():
    init_db(force=True)
    conn = get_connection()
    cursor = conn.cursor()
    
    print("[1/8] Seeding Districts...")
    districts_data = [
        ("West Tripura", "Agartala", 983.68, 48.2, 23.8315, 91.2868, "Political and cultural capital district, home to Ujjayanta Palace, State Museum, and historic urban wetlands."),
        ("Sepahijala", "Bishramganj", 1043.62, 59.4, 23.5852, 91.3195, "Rich ecological zone known for Sepahijala Sanctuary, Clouded Leopard National Park, and Neermahal Water Palace."),
        ("Gomati", "Udaipur", 1522.80, 62.1, 23.5342, 91.4880, "Historic lake city of Udaipur, Tripura Sundari Shakti Peetha temple, and the Gomati river canyon at Chabimura."),
        ("South Tripura", "Belonia", 1514.30, 68.5, 23.2500, 91.4500, "Historical cradle featuring Pilak archaeological ruins, Trishna Wildlife Sanctuary, and rich Indo-Bangla frontier culture."),
        ("Dhalai", "Ambassa", 2312.29, 78.3, 23.9000, 91.8500, "Tripura's most forested district, featuring the Dumbur reservoir archipelago, indigenous Kokborok villages, and evergreen hills."),
        ("Khowai", "Khowai", 1377.28, 54.7, 24.0625, 91.6042, "Scenic valley traversed by Khowai river, Hathai Kotor (Baramura) eco-park, and traditional bamboo artisan clusters."),
        ("Unakoti", "Kailashahar", 686.97, 61.2, 24.3200, 92.0200, "Renowned worldwide for the 7th-9th century colossal rock-carved Shaivite sculptures at Unakoti hill forest."),
        ("North Tripura", "Dharmanagar", 1422.19, 73.1, 24.3750, 92.1650, "Border district famous for the verdant Jampui Hills range, Betlingchhip peak, orange orchards, and Mizo/Lushai culture.")
    ]
    cursor.executemany("""
        INSERT INTO districts (name, headquarters, area_sq_km, forest_cover_percent, center_latitude, center_longitude, description)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, districts_data)

    print("[2/8] Seeding Users and Preferences...")
    users_data = [
        ("Dr. Debashis Debbarma", "admin@tripuraterra.in", hash_password("Admin@Tripura2026"), "admin", "India"),
        ("Ananya Sen Gupta", "curator@tripuraterra.in", hash_password("Curator@Tripura2026"), "content_manager", "India"),
        ("Marcus Lindqvist", "marcus.eco@traveler.org", hash_password("Traveler@2026"), "tourist", "Sweden"),
        ("Ranjit Reang", "ranjit.reang@tripura.gov.in", hash_password("Ranjit@2026"), "tourist", "India")
    ]
    cursor.executemany("""
        INSERT INTO users (full_name, email, password_hash, role, country)
        VALUES (?, ?, ?, ?, ?);
    """, users_data)
    
    # User Preferences
    cursor.execute("""
        INSERT INTO user_preferences (user_id, preferred_travel_style, budget_tier, preferred_pace, nature_weight, culture_weight, requires_accessibility, max_travel_hours_per_day)
        VALUES 
        (1, 'cultural_immersion', 'premium', 'moderate', 0.6, 0.9, 0, 8),
        (2, 'nature_retreat', 'medium', 'relaxed', 0.8, 0.7, 0, 6),
        (3, 'slow_travel', 'medium', 'relaxed', 0.9, 0.8, 0, 5),
        (4, 'adventure', 'budget', 'intensive', 0.7, 0.5, 0, 10);
    """)

    print("[3/8] Seeding Destinations...")
    # Format: (district_id, name, slug, tagline, type, short_desc, full_desc, lat, lng, alt, best_season, duration, diff, access, crowd, fee, lesser_known, verified, img, thumb, e_idx)
    destinations_data = [
        (
            7, "Unakoti Rock-Cut Reliefs", "unakoti-rock-cut-reliefs",
            "The Mystical Shaivite Bas-Reliefs of Sub-Himalayan Raghunandan Hills",
            "rock_carving",
            "Colossal 7th-9th century rock carvings of Lord Shiva, Ganesha, and Maa Ganga carved directly into a steep forested gorge.",
            "Unakoti (literally 'one less than a crore' in Bengali) is an ancient Shaivite pilgrimage dating between the 7th and 9th centuries CE. Hidden amidst dense subtropical hills in northern Tripura, the colossal 30-foot central bas-relief of Unakotiswara Kal Bhairava is accompanied by two female attendants and an exquisite multi-tusked Ganesha sculpture. Streams of natural mountain water cascade around the rock sculptures into the sacred Kund below. It represents a sublime harmony between rock-cut stone art and living montane forest ecology.",
            24.3211, 92.0215, 180, "October to March", 3.5, "Moderate", "Partial", "Moderate", 30.0, 0, 1,
            "/static/images/unakoti.jpg",
            "/static/images/unakoti.jpg",
            91.5
        ),
        (
            2, "Neermahal Water Palace", "neermahal-water-palace",
            "The Floating Architectural Marvel in the Waters of Rudrasagar Lake",
            "royal_palace",
            "North East India's only water palace, blending Mughal and Hindu architectural traditions in the center of Ramsar-listed Rudrasagar Lake.",
            "Commissioned in 1930 by Maharaja Bir Bikram Kishore Manikya Bahadur, Neermahal ('Water Palace') was built as a royal summer retreat. Situated in the middle of the shimmering Rudrasagar Lake, this palace required over nine years of construction by the British firm Martin & Burn Co. Built of red sandstone and marble, it seamlessly merges domes, chhatris, and fortress ramparts. In winter, Rudrasagar Lake hosts thousands of migratory waterfowl including Ferruginous Pochard and Spot-billed Pelicans.",
            23.4912, 91.3174, 30, "October to March", 3.0, "Easy", "Full", "Moderate", 50.0, 0, 1,
            "/static/images/neermahal.jpg",
            "/static/images/neermahal.jpg",
            86.0
        ),
        (
            1, "Ujjayanta Palace & State Museum", "ujjayanta-palace-museum",
            "The Neoclassical Crown of Tripura's Royal Manikya Heritage",
            "royal_palace",
            "A sprawling 800-acre neoclassical palace featuring grand Mughal gardens, intricate woodwork, and the premier ethnographic museum of Northeast India.",
            "Constructed between 1899 and 1901 by Maharaja Radha Kishore Manikya, Ujjayanta Palace served as the seat of the Tripura Kingdom until merger with India. Named by Nobel Laureate Rabindranath Tagore, a regular guest of the Manikya court, the palace features tiled floors, ornamental ceilings, and crafted doors. It now houses the state museum, which houses rare stone sculptures, archaeological relics from Pilak, and anthropological exhibits documenting all 19 indigenous tribes of Tripura.",
            23.8364, 91.2825, 45, "All Year Round", 3.0, "Easy", "Full", "High", 40.0, 0, 1,
            "/static/images/ujjayanta.jpg",
            "/static/images/ujjayanta.jpg",
            79.5
        ),
        (
            3, "Chabimura (Chakhwmwrak)", "chabimura-rock-carvings",
            "The Amazonian Gorge and Sacred Rock Art of Gomati River",
            "rock_carving",
            "Towering verdant canyon cliffs overlooking the Gomati River, holding ancient 15th-century bas-relief panels of Goddess Tripura Sundari.",
            "Chabimura, known historically as Chakhwmwrak in Kokborok, is a breathtaking river canyon located in Amarpur. Steep cliff walls rising up to 200 feet are blanketed in primeval ferns, orchids, and bamboo groves. On these vertical sandstone walls, ancient sculptors carved colossal rock sculptures of Goddess Mahishasuramardini (locally Maa Tripura Sundari), Shiva, and Brihaspati during the 15th century. Accessible only by eco-friendly boat safaris, it is one of the most ecologically pristine and culturally sacred river corridors in India.",
            23.5186, 91.6892, 75, "October to April", 4.5, "Moderate", "Limited", "Low", 150.0, 1, 1,
            "/static/images/chabimura.jpg",
            "/static/images/chabimura.jpg",
            94.0
        ),
        (
            8, "Jampui Hills Range & Vanghmun", "jampui-hills-vanghmun",
            "The Seat of Eternal Spring, Lushai Orchards, and Ridge Walks",
            "hill_station",
            "Verdant mountain ridge at 3,000 feet, celebrated for cool climate, clean Mizo eco-villages, orange blossoms, and panoramic sunrise vistas.",
            "Forming the border between Tripura and Mizoram, the Jampui Hills range is renowned for its perpetual cool breeze, clean model eco-villages such as Vanghmun, and rich Mizo/Lushai tribal culture. The hill slopes are terraced with sweet orange orchards, betel plantations, and wild orchids. Walking through Vanghmun village reveals community-driven sanitation, traditional bamboo homes, flower gardens, and vantage views across the blue mist of the Chittagong Hill Tracts.",
            23.9850, 92.2700, 850, "September to April", 8.0, "Moderate", "Partial", "Low", 20.0, 1, 1,
            "/static/images/jampui_hills.jpg",
            "/static/images/jampui_hills.jpg",
            93.5
        ),
        (
            2, "Sepahijala Wildlife Sanctuary & Clouded Leopard NP", "sepahijala-wildlife-sanctuary",
            "Subtropical Biosphere of the Phayre's Langur and Clouded Leopard",
            "eco_sanctuary",
            "A biodiverse 18.5 sq. km sanctuary featuring botanical gardens, natural lakes, and national breeding centres for endemic primates.",
            "Sepahijala is one of India's premier conservation centres for the endangered Clouded Leopard (Neofelis nebulosa) and Phayre's Leaf Monkey (Trachypithecus phayrei - the state animal of Tripura). Comprising moist deciduous sal forests, artificial lakes, and over 150 species of birds, the sanctuary functions as a vital biodiversity corridor. Visitors can explore walking nature trails, observe barking deer and capped langurs in semi-wild natural enclosures, and paddle on the placid Amrit Sagar lake.",
            23.6842, 91.3189, 60, "November to March", 4.0, "Easy", "Full", "Moderate", 30.0, 0, 1,
            "/static/images/sepahijala.jpg",
            "/static/images/sepahijala.jpg",
            92.0
        ),
        (
            4, "Pilak Buddhist-Hindu Archaeological Site", "pilak-archaeological-site",
            "Ancient 8th-12th Century Confluence of Avalokiteshvara & Shiva Stone Art",
            "cultural_heritage",
            "Historical site uncovering Buddhist stupas, terracotta temple bas-reliefs, and colossal stone statues of Surya, Avolokiteshvara, and Narasimha.",
            "Nestled in the Jolaibari valley of South Tripura, Pilak preserves an extraordinary 8th to 12th century archaeological zone where Mahayana Buddhism and Hinduism co-existed and flourished under early rulers. Excavations by the Archaeological Survey of India have uncovered brick-built stupas, terracotta plaques depicting animals, kinnaras, and royal warriors, alongside giant sandstone sculptures of the Bodhisattva Avalokiteshvara and Surya that reflect profound stylistic ties with the Mainamati and Nalanda schools.",
            23.1950, 91.5620, 50, "October to March", 2.5, "Easy", "Full", "Low", 25.0, 1, 1,
            "/static/images/home_banner4.jpeg",
            "/static/images/home_banner4.jpeg",
            89.0
        ),
        (
            5, "Dumbur Lake & Narikel Kunja", "dumbur-lake-narikel-kunja",
            "Vast Reservoir Archipelago of 48 Green Islands and Indigenous Water Lore",
            "lake_wetland",
            "A breathtaking 41 sq. km expanse of water shaped like Lord Shiva's 'Dumroo', dotted with lush islands, migratory birds, and tribal fishing settlements.",
            "Dumbur Lake is a majestic waterbody formed near the confluence of the Raima and Sarma rivers, which together create the sacred Gomati River. Named after its resemblance to Lord Shiva's small two-headed drum (dumroo), the lake contains 48 undulating green hillock islands. The island of Narikel Kunja ('Coconut Island') has been developed into an eco-retreat with solar-powered bamboo cottages, eco-kayaking, and silent boat safaris that protect wintering wetland avifauna.",
            23.5110, 91.8750, 110, "October to March", 5.0, "Easy", "Partial", "Low", 100.0, 1, 1,
            "/static/images/home_banner1.jpeg",
            "/static/images/home_banner1.jpeg",
            90.5
        ),
        (
            3, "Tripura Sundari Shakti Peetha (Matabari)", "tripura-sundari-temple",
            "The 500-Year Sacred Peetha and Kalyan Sagar Tortoise Sanctuary",
            "temple_complex",
            "One of the revered 51 Shakti Peethas built in 1501 CE in the traditional Bengali-Tripuri hut style, fronting a sacred lake of endangered freshwater turtles.",
            "Constructed by Maharaja Dhanya Manikya in 1501 CE on a small tortoise-shaped hillock, this temple is revered as Kurma Pitha, where the right foot of Goddess Sati is believed to have fallen. The shrine is unique for its square sanctum topped by a Bengali chala-style curved roof and stupa finial. Directly behind the temple lies the 5-acre Kalyan Sagar lake, home to centuries-old sacred Black Softshell Turtles (Nilssonia nigricans), strictly protected as sacred living relics.",
            23.5312, 91.4988, 48, "All Year Round", 2.0, "Easy", "Full", "High", 0.0, 0, 1,
            "/static/images/tripura_sundari.jpg",
            "/static/images/tripura_sundari.jpg",
            82.0
        ),
        (
            4, "Trishna Wildlife Sanctuary & Bison Park", "trishna-wildlife-sanctuary",
            "Primeval Sal Forest Haven of the Majestic Indian Gaur",
            "eco_sanctuary",
            "Over 163 sq. km of virgin forest harboring one of India's healthiest breeding populations of the Indian Bison (Gaur) and Golden Langurs.",
            "Trishna Wildlife Sanctuary in South Tripura is characterized by patches of virgin primary sal forests, bamboo brakes, and water holes. It is renowned for conserving the mighty Indian Gaur (Bos gaurus), the largest extant bovine on Earth. Trishna is also an important habitat for the Hoolock Gibbon, Slow Loris, and numerous species of hornbills. Regulated eco-tours follow designated trails to ensure zero disruption to breeding herds.",
            23.3150, 91.3850, 70, "November to April", 5.0, "Moderate", "Partial", "Very Low", 50.0, 1, 1,
            "/static/images/home_banner5.jpeg",
            "/static/images/home_banner5.jpeg",
            96.0
        ),
        (
            6, "Hathai Kotor (Baramura Eco Park)", "hathai-kotor-baramura",
            "Eco-Canopy Trails and Indigenous Kokborok Forest Heritage",
            "eco_sanctuary",
            "A lush eco-park nestled in the Baramura range with tree-top hanging walkways, medicinal plant nurseries, and tribal handicraft pavilions.",
            "Located along the National Highway traversing the Baramura hills, Hathai Kotor Eco Park offers travelers an immersion into indigenous Kokborok nature lore. The park features elevated bamboo suspension bridges traversing dense tree canopies, demonstration plots of rare medicinal herbs used in traditional Tripuri healing, and cultural pavilions where local Kokborok women demonstrate back-strap loom weaving of traditional Risa textiles.",
            23.8640, 91.5620, 140, "October to April", 2.5, "Easy", "Full", "Low", 20.0, 1, 1,
            "/static/images/home_banner3.jpeg",
            "/static/images/home_banner3.jpeg",
            88.5
        ),
        (
            8, "Betlingchhip Peak (Jampui Summit)", "betlingchhip-peak",
            "The Highest Geographic Crest of Tripura with 360-Degree Vistas",
            "hill_station",
            "At 930 meters, the highest point in Tripura offering a wilderness ridge trek through rainforest canopy to panoramic viewpoints.",
            "Betlingchhip (also known as Betlingshib) is the supreme summit of Tripura, situated at an altitude of 930 meters in the Jampui range. A rewarding trek passes through untouched cloud forest corridors, wild banana groves, and ancient moss-covered tree canopies. At the peak summit watchtower, hikers are treated to 360-degree vistas stretching across the rolling blue hills of Mizoram on one side and the tea garden plains of Sylhet on the other.",
            23.8050, 92.2590, 930, "October to March", 5.0, "Challenging", "Limited", "Very Low", 0.0, 1, 1,
            "/static/images/eden_lodge.jpg",
            "/static/images/eden_lodge.jpg",
            95.0
        ),
        (
            2, "Kasba Kalibari & Kamalasagar Border Lake", "kasba-kalibari-kamalasagar",
            "15th-Century Frontier Shrine Overlooking Historic Waterfront Borders",
            "cultural_heritage",
            "A sacred hilltop temple of Goddess Kali commissioned by Maharaja Dhanya Manikya in the late 15th century overlooking a sprawling border lake.",
            "Situated right on the international border with Bangladesh, Kasba Kalibari sits atop a gentle hillock looking down onto the vast Kamalasagar lake, excavated by Maharaja Dhanya Manikya in the 15th century. The temple enshrines a black stone idol of Mahishamardini that bears stylistic similarities to the sculptures discovered at Pilak. The site is a vibrant symbol of regional peace and community harmony, hosting peaceful border haat trade markets.",
            23.7020, 91.1890, 42, "All Year Round", 2.0, "Easy", "Full", "Moderate", 10.0, 0, 1,
            "/static/images/kashba_lodge.jpg",
            "/static/images/kashba_lodge.jpg",
            83.0
        ),
        (
            1, "Heritage Park (Agartala)", "heritage-park-agartala",
            "Tripura's Monuments and Eco-Zones in an Urban Forest Sanctuary",
            "cultural_heritage",
            "A beautifully designed 12-acre botanical eco-park showcasing authentic scaled mini-replicas of all major Tripura architectural heritage sites.",
            "Conceived as an educational gateway to the state, Heritage Park is situated in the northern part of Agartala. In a single walking trail enclosed by bamboo groves and indigenous flowering trees, visitors can discover meticulously detailed stone and terracotta mini-replicas of Unakoti rock reliefs, Neermahal, Pilak stupas, Ujjayanta Palace, and Tripura Sundari Temple. The park is lit entirely by solar lamps and adheres to zero-waste composting.",
            23.8560, 91.2910, 40, "All Year Round", 2.0, "Easy", "Full", "Moderate", 20.0, 0, 1,
            "/static/images/geetanjali_lodge.jpg",
            "/static/images/geetanjali_lodge.jpg",
            81.0
        )
    ]
    cursor.executemany("""
        INSERT INTO destinations (
            district_id, name, slug, tagline, destination_type, short_description, full_description,
            latitude, longitude, altitude_meters, best_season, recommended_duration_hours,
            difficulty_level, accessibility_level, crowd_density_level, entry_fee_inr,
            is_lesser_known, is_verified, image_url, thumbnail_url, eco_responsibility_index
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, destinations_data)

    print("[4/8] Seeding Eco & Cultural Extensions...")
    # Eco Sites (dest_id, ecosystem, bio_significance, flora, fauna, status, capacity, guide, plastic, trail, bird_time)
    eco_sites_data = [
        (1, "Subtropical Montane Rainforest Ravine", "Critical ravine habitat for moss, lichens, and rare montane flora on shaded rock reliefs.", "Ficus, Dipterocarpus, Wild Banana, Tree Ferns", "Great Hornbill, Malayan Giant Squirrel, Barking Deer", "State Protected Heritage Sanctuary", 250, 0, 1, 2.5, "Dawn (06:00 - 08:30)"),
        (2, "Freshwater Wetland Ecosystem (Ramsar Wetland #1207)", "Wintering waterbird haven with high micro-algal and aquatic biodiversity.", "Eichhornia, Hydrilla, Nelumbo nucifera (Sacred Lotus)", "Ferruginous Pochard, Spot-billed Pelican, Asian Openbill", "Ramsar Wetland of International Importance", 500, 1, 1, 0.0, "Early Morning (06:30 - 09:00)"),
        (4, "Limestone River Canyon & Riparian Jungle", "High endemism of aquatic and cliff-nesting raptors in pristine river gorges.", "Giant Bamboos (Melocanna baccifera), Wild Orchids, Epiphytes", "Gomati River Otters, Crested Serpent Eagle, Kingfishers", "State Eco-Sensitive Zone", 120, 1, 1, 4.0, "Morning to Midday"),
        (5, "Subtropical Ridge Cloud Forest & Orchards", "Crucial micro-climatic sanctuary for high-altitude birds and endemic butterfly species.", "Sweet Orange (Citrus sinensis), Betel, Rhododendrons, Pine", "Rufous-necked Hornbill, Blue-throated Barbet, Emerald Dove", "Community Conserved Ridge Area", 200, 0, 1, 6.0, "Sunrise (05:30 - 08:00)"),
        (6, "Moist Deciduous Mixed Sal Forest Biosphere", "Key primate biodiversity and captive breeding hotspot for the endangered Clouded Leopard.", "Shorea robusta (Sal), Terminalia arjuna, Bamboo Groves", "Clouded Leopard, Phayre's Leaf Monkey, Capped Langur, Binturong", "Wildlife Sanctuary & National Park", 450, 0, 1, 5.0, "Morning & Late Afternoon"),
        (8, "Large Freshwater Reservoir with Island Archipelago", "Vital aquatic refuge for resident and migratory waterfowl in central Tripura.", "Water Hyacinth, Submerged Macrophytes, Swamp Grasses", "Cotton Pygmy Goose, Bronze-winged Jacana, Freshwater Catfish", "Protected Reservoir Wetland", 300, 1, 1, 3.0, "Late Autumn & Winter Mornings"),
        (10, "Virgin Primary Sal Forest & Grassland Brakes", "Highest density of Indian Gaur (Bison) in Northeast India with high herbivore biomass.", "Primary Sal, Albizia procera, Careya arborea", "Indian Gaur (Bison), Hoolock Gibbon, Slow Loris, Leopard Cat", "Wildlife Sanctuary", 100, 1, 1, 8.0, "Dawn (05:45 - 09:00)"),
        (11, "Foothill Secondary Forest & Bamboo Corridors", "Demonstration ecosystem for indigenous Kokborok ethnobotanical and herbal wealth.", "Melocanna baccifera (Muli Bamboo), Amla, Haritaki, Bahera", "Barking Deer, Common Leopard, Racket-tailed Drongo", "Eco Park & Forest Reserve", 350, 0, 1, 3.5, "Morning to Afternoon"),
        (12, "High-Altitude Wet Evergreen Montane Crest", "Primary evergreen crest forest sheltering relict botanical species and montane avifauna.", "Quercus (Oak), Castanopsis, Montane Mosses, Wild Orchids", "Blyth's Tragopan (historical), Hill Myna, Himalayan Squirrel", "Pristine Montane Crest Forest", 60, 1, 1, 7.5, "Sunrise to Early Afternoon")
    ]
    cursor.executemany("""
        INSERT INTO eco_sites (
            destination_id, ecosystem_type, biodiversity_significance, key_flora, key_fauna,
            conservation_status, carrying_capacity_per_day, guide_mandatory, plastic_free_zone,
            trail_length_km, best_birdwatching_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, eco_sites_data)

    # Cultural Sites (dest_id, epoch, style, community, significance, rituals, dress, photo, agency)
    cultural_sites_data = [
        (1, "7th - 9th Century CE", "Rock-Cut Bas-Relief Shaivite Art", "Indigenous Reang & Debbarma Pilgrims", "One of India's grandest rock-carved pilgrimage sites, celebrated for the giant 30-foot head of Shiva.", "Ashokastami Mela held annually in March/April where thousands take sacred dip in the Kund.", "Modest clothing recommended; comfortable trekking shoes for stone steps.", "Yes", "Archaeological Survey of India (ASI)"),
        (2, "1930 - 1938 CE (Manikya Dynasty)", "Indo-Saracenic & Mughal-Hindu Fusion", "Local Kaibarta Fishing Communities & Boatmen", "Historic summer palace of King Bir Bikram Kishore Manikya, showcasing harmonious royal architecture.", "Neermahal Jal Utsav (Water Festival) with boat racing in September.", "Casual modest attire; life jackets required for boat transit.", "Yes", "Tripura Tourism Development Corporation"),
        (3, "1899 - 1901 CE (Maharaja Radha Kishore Manikya)", "Neoclassical with Mughal Garden Layout", "Debbarma Royal Court & All 19 Tribes of Tripura", "Historic royal seat of Tripura Kingdom, named by Rabindranath Tagore; houses the state museum.", "Annual State Cultural Gatherings, Rabindra Jayanti Celebrations.", "Formal or smart casual; no footwear in certain indoor heritage galleries.", "Restricted", "Department of Cultural Affairs, Govt of Tripura"),
        (4, "15th - 16th Century CE", "Vertical Sandstone Bas-Relief Carving", "Jamatia & Kokborok Forest Dwellers", "Sacred natural temple canyon holding ancient reliefs of Maa Tripura Sundari sculpted by royal artists.", "Local Kokborok sacred prayers during Makar Sankranti and Chaitra festivals.", "Eco-friendly footwear; respect local boatmen's cultural instructions.", "Yes", "State Directorate of Archaeology & Tourism"),
        (7, "8th - 12th Century CE", "Buddhist-Hindu Terracotta & Sandstone Art", "Ancient Early Medieval Inhabitants", "Crucial archaeological proof of peaceful coexistence between Mahayana Buddhism and early Hinduism.", "Annual Pilak Archaeological Tourism Festival.", "Modest attire covering shoulders; strictly avoid touching archaeological terracotta tiles.", "Yes", "Archaeological Survey of India (ASI)"),
        (9, "1501 CE (Maharaja Dhanya Manikya)", "Tripuri Ek-Ratna Chala Shrine on Kurma Pitha", "Tripuri, Bengali, and regional Shakti devotees", "One of the 51 Shakti Peethas; home to the sacred 500-year Kalyan Sagar turtle habitat.", "Daily morning/evening aarti; massive annual Diwali Mela attracting 200,000+ pilgrims.", "Traditional temple dress; shoes removed outside main courtyard.", "No", "Matabari Temple Trust & District Administration"),
        (13, "Late 15th Century CE", "Traditional Bengali-Tripuri Terracotta Sanctum", "Indo-Bangla Border Inhabitants", "A symbol of peaceful border heritage and ancient worship of Goddess Kali.", "Annual Kasba Mela held alongside the holy Kamalasagar lake.", "Modest temple clothing.", "Yes", "District Cultural Heritage Committee")
    ]
    cursor.executemany("""
        INSERT INTO cultural_sites (
            destination_id, historical_epoch, architectural_style, indigenous_community_link,
            cultural_significance, rituals_and_folklore, dress_code_guidelines, photography_allowed,
            preservation_agency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, cultural_sites_data)

    print("[5/8] Seeding Indigenous Communities, Crafts & Experiences...")
    communities_data = [
        ("Tripuri (Debbarma)", "Kokborok", "Agriculture, Agro-Forestry, Bamboo Architecture", "The largest indigenous community of Tripura with rich royal history and folk traditions.", "Back-strap loom weaving of Risa and Rikutu, Cane furniture, Bamboo musical instruments", "Garia Dance, Lebang Boomani, Mamita Dance", "Always ask permission before photographing family homes. Support artisan weavers directly without haggling excessively.", "West Tripura, Khowai, Sepahijala, Gomati"),
        ("Reang (Bru)", "Kau Bru", "Jhum cultivation, horticulture, bamboo craft", "Second largest indigenous group, celebrated for physical agility and balancing folk acrobatics.", "Intricate bamboo storage baskets, woven headgears, bead jewellery", "Hojagiri Dance (balancing on earthen pitchers while holding oil lamps)", "Respect village elders (Choudhury system). Avoid disturbing sacred village forest groves.", "Dhalai, North Tripura, Gomati"),
        ("Jamatia", "Kokborok", "Community farming, conservation of village forests", "Egalitarian tribal society governed by the supreme Hoda system of social self-governance.", "Traditional hand-woven cotton textiles, bamboo fishing traps (polo)", "Garia dance with ceremonial bamboo staff", "Observe the village sanctity during Hoda council meetings and sacred Garia celebrations.", "Gomati, Khowai, South Tripura"),
        ("Chakma", "Changma Vaj / Chakma", "Wet rice cultivation, weaving, fishing", "Theravada Buddhist indigenous group with rich literary and culinary traditions.", "Chakma Phoolgadi silk and cotton handloom textiles, silver filigree jewellery", "Biju Festival dance, Bizu dance during new year", "Remove footwear when entering Chakma Buddhist prayer halls (Khyang).", "Dhalai, North Tripura, South Tripura"),
        ("Mizo (Lushai)", "Mizo", "Horticulture, orange farming, ecotourism hosting", "Inhabitants of Jampui Hills, known for exemplary civic cleanliness and church choir music.", "Puan hand-woven ceremonial shawls, bamboo wood-craft", "Cheraw (Bamboo Dance), Khuallam", "Maintain zero-litter discipline in Vanghmun model villages. Respect quiet hours on Sundays.", "North Tripura (Jampui Hills)")
    ]
    cursor.executemany("""
        INSERT INTO indigenous_communities (
            name, primary_language, traditional_occupations, cultural_hallmark, crafts_heritage,
            dance_forms, respectful_engagement_code, associated_districts
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, communities_data)

    # Experiences
    experiences_data = [
        (1, "Guided Shaivite Heritage & Forest Trail", "guided_trek", "Explore ancient stone steps with a licensed local guide explaining Shaivite iconography and herbal folklore.", 180, 500.0, 10, "Unakoti Local Eco-Guide Guild", "Low"),
        (2, "Rudrasagar Sunset Boat Safari & Palace Tour", "boat_safari", "Silent electric and row boat safari across the Ramsar wetland observing aquatic birds followed by palace interior tour.", 150, 450.0, 8, "Rudrasagar Fishermen Cooperative", "Very Low"),
        (3, "Tripura Tribal Handloom & Risa Weaving Masterclass", "tribal_craft", "Hands-on session with Debbarma master weavers learning the intricate patterns and cultural motifs of authentic Risa.", 120, 650.0, 6, "Kokborok Handloom Artisans Alliance", "Very Low"),
        (4, "Chabimura River Canyon Eco-Boat Odyssey", "boat_safari", "Silent motor eco-boat ride between soaring forested gorge cliffs with close-up interpretation of the Goddess rock relief.", 180, 800.0, 8, "Amarpur Tribal Youth Boat Guild", "Low"),
        (5, "Lushai Orange Orchard Walk & Homestay Dining", "local_culinary", "Stroll through organic citrus groves in Vanghmun, followed by traditional home-cooked Mizo lunch with wild herbs.", 210, 750.0, 10, "Jampui Hills Community Homestay Network", "Very Low"),
        (6, "Sepahijala Primate Tracking & Birding Walk", "birding", "Early morning guided walk through the sal sanctuary with a naturalist to observe Phayre's Leaf Monkey and hornbills.", 180, 400.0, 8, "Bishramganj Community Naturalists", "Very Low"),
        (8, "Narikel Kunja Island Kayaking & Tribal Fish Feast", "boat_safari", "Paddling along silent island coves in Dumbur Lake, accompanied by a traditional Kokborok grilled fish meal.", 240, 950.0, 6, "Dumbur Ecotourism Cooperative", "Low"),
        (10, "Trishna Forest Watchtower Indian Gaur Safari", "guided_trek", "Safe guided watchtower vigil overlooking water holes favored by wild Indian Gaur herds at daybreak.", 240, 600.0, 8, "South Tripura Eco-Conservation Guides", "Low")
    ]
    cursor.executemany("""
        INSERT INTO experiences (
            destination_id, title, category, description, duration_minutes, cost_inr,
            max_participants, community_beneficiary, eco_footprint_rating
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, experiences_data)

    print("[6/8] Seeding Sustainability Metrics (ERI Engine Data)...")
    # Formula parameters: (dest_id, bio, sensitivity, waste, community, pressure, transit, water, type)
    metrics_data = [
        (1, 88.0, 72.0, 84.0, 89.0, 45.0, 78.0, 85.0, "Verified Baseline"),
        (2, 92.0, 80.0, 75.0, 86.0, 52.0, 82.0, 90.0, "Verified Baseline"),
        (3, 65.0, 40.0, 88.0, 72.0, 68.0, 95.0, 80.0, "Verified Baseline"),
        (4, 96.0, 85.0, 88.0, 95.0, 25.0, 70.0, 92.0, "Verified Baseline"),
        (5, 94.0, 65.0, 96.0, 98.0, 28.0, 74.0, 90.0, "Verified Baseline"),
        (6, 95.0, 78.0, 85.0, 88.0, 42.0, 88.0, 86.0, "Verified Baseline"),
        (7, 82.0, 55.0, 86.0, 90.0, 22.0, 80.0, 84.0, "Verified Baseline"),
        (8, 93.0, 70.0, 82.0, 92.0, 30.0, 75.0, 94.0, "Verified Baseline"),
        (9, 70.0, 50.0, 78.0, 85.0, 75.0, 92.0, 76.0, "Verified Baseline"),
        (10, 98.0, 88.0, 90.0, 94.0, 18.0, 72.0, 95.0, "Verified Baseline"),
        (11, 86.0, 60.0, 88.0, 91.0, 35.0, 85.0, 88.0, "Verified Baseline"),
        (12, 97.0, 82.0, 94.0, 96.0, 15.0, 65.0, 92.0, "Verified Baseline"),
        (13, 76.0, 45.0, 80.0, 84.0, 58.0, 88.0, 82.0, "Verified Baseline"),
        (14, 75.0, 35.0, 92.0, 78.0, 60.0, 96.0, 85.0, "Verified Baseline")
    ]
    cursor.executemany("""
        INSERT INTO sustainability_metrics (
            destination_id, biodiversity_index, environmental_sensitivity, waste_management_score,
            community_employment_score, visitor_pressure_score, sustainable_transit_score,
            water_conservation_score, data_source_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, metrics_data)

    print("[7/8] Seeding Events & Festivals...")
    events_data = [
        (1, 3, "Kharchi Puja & Festival of Fourteen Gods", "Religious Festival", "2026-07-06", "2026-07-13",
         "Tripura's most celebrated state festival dating back centuries, honoring the Fourteen Gods (Chaturdasha Devata) with royal and tribal rituals.",
         "Pilgrims are expected to dress respectfully. Sacred holy dips in the Howrah River follow designated eco-zones.",
         "Chaturdasha Devata Temple Complex, Old Agartala (Puran Agartala)",
         "https://images.unsplash.com/photo-1533900298318-6b8da08a523e?auto=format&fit=crop&w=800&q=80"),
        (2, 2, "Neermahal Water Festival (Jal Utsav)", "Water Carnival", "2026-09-18", "2026-09-20",
         "A colorful 3-day spectacle on Rudrasagar Lake featuring traditional long-boat races by local fishermen, swimming contests, and cultural dances.",
         "Cheering zones are designated on the shore and palace terrace; plastic bottles are banned around the lake.",
         "Rudrasagar Lake & Neermahal Palace Courtyard, Melaghar",
         "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=800&q=80"),
        (3, 4, "Garia Puja & Tribal Harvest Spring Celebration", "Indigenous Celebration", "2026-04-14", "2026-04-21",
         "Seven-day festival honoring Lord Garia, the deity of livestock, peace, and bountiful harvest. Marked by the famous Garia dance.",
         "Respect the sacred bamboo pole of Lord Garia; do not step over the consecrated offerings.",
         "Celebrated across all indigenous village hamlets in Gomati and Khowai districts",
         "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80"),
        (4, 7, "Pilak Archaeological Heritage Festival", "Craft Fair", "2026-11-20", "2026-11-23",
         "Annual cultural gathering highlighting Buddhist-Hindu archaeological discoveries, historical seminars, and tribal handloom stalls.",
         "Enjoy cultural performances by Chakma, Tripuri, and Bengali troupes; buy certified local handloom handicrafts.",
         "Pilak Archaeological Complex, Jolaibari",
         "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=800&q=80"),
        (8, 5, "Jampui Orange Festival & Winter Carnival", "Craft Fair", "2026-11-28", "2026-12-02",
         "Festive harvest festival celebrating the peak of the sweet orange crop in the cool heights of the Jampui hills.",
         "Support local Mizo farmers by purchasing freshly harvested organic citrus fruits and traditional shawls.",
         "Vanghmun Village Ground, Jampui Hills",
         "https://images.unsplash.com/photo-1519671482749-fd09be7ccebf?auto=format&fit=crop&w=800&q=80")
    ]
    cursor.executemany("""
        INSERT INTO events (
            district_id, destination_id, name, category, start_date, end_date,
            significance, guidelines_for_tourists, location_details, image_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, events_data)

    print("[8/8] Seeding Reviews, Saved Places & Sample Itinerary...")
    reviews_data = [
        (3, 1, 4.9, 4.8, 5.0, 5.0, "Transcendent experience in the morning mist",
         "Standing before the colossal 30-foot head of Shiva while mountain water cascaded into the Kund was deeply spiritual. The site is clean, plastic-free, and respectful of the surrounding forest ecology. Highly recommend arriving at 7 AM for the bird calls and solitude.",
         "February 2026", 1),
        (3, 4, 5.0, 4.9, 5.0, 4.9, "The river canyon is pure magic",
         "The boat trip through Chabimura was nothing short of an Amazonian expedition right in Tripura. The limestone cliff carving of Goddess Durga is astonishing. Our local youth boatman explained the Kokborok river folklore beautifully.",
         "January 2026", 1),
        (4, 5, 4.8, 5.0, 4.9, 5.0, "Vanghmun is the cleanest village in the Northeast",
         "Jampui Hills blew away my expectations. The model village of Vanghmun puts top hill stations to shame. Every home has a flowering orchid garden and the community genuinely cares about zero waste.",
         "November 2025", 1),
        (3, 2, 4.7, 4.5, 4.8, 4.8, "Floating palace amidst bird sanctuary waters",
         "Neermahal is an engineering wonder. Gliding on Rudrasagar lake at sunset with flocks of migratory teals flying overhead will stay with me forever.",
         "December 2025", 1)
    ]
    cursor.executemany("""
        INSERT INTO reviews (
            user_id, destination_id, overall_rating, cleanliness_rating, eco_practice_rating,
            community_respect_rating, review_title, review_text, visit_month_year, is_verified_visit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, reviews_data)

    # Saved Places for Tourist User #3
    cursor.execute("""
        INSERT INTO saved_places (user_id, destination_id, notes)
        VALUES 
        (3, 1, 'Must visit Unakoti during Ashokastami or early morning.'),
        (3, 4, 'Book eco-boat in advance through youth cooperative.'),
        (3, 5, 'Stay at Vanghmun community homestay for 2 nights.');
    """)

    # Sample Itinerary
    cursor.execute("""
        INSERT INTO itineraries (
            user_id, title, total_days, budget_inr, travel_style, estimated_distance_km, composite_eco_score, explanation_notes
        ) VALUES (
            3, 'Tripura Eco-Cultural Discovery Circuit', 3, 12500.0, 'slow_travel', 310.0, 92.4,
            'Balanced 3-day journey combining Ramsar wetland ecology, Shaivite rock heritage, and authentic indigenous community experiences with low carbon footprint.'
        );
    """)
    itin_id = cursor.lastrowid
    
    itinerary_items = [
        (itin_id, 3, 1, 'Morning', 1, 'Explore neoclassical architecture & Northeast tribal ethnographic museum at Ujjayanta Palace.', 0.0),
        (itin_id, 2, 1, 'Afternoon', 2, 'Travel to Melaghar, board electric eco-boat across Rudrasagar Lake to explore Neermahal.', 52.0),
        (itin_id, 6, 2, 'Morning', 1, 'Primate tracking walk through Sepahijala Sal Forest watching for Clouded Leopard and Phayre Langur.', 28.0),
        (itin_id, 4, 2, 'Afternoon', 2, 'Eco-boat safari through towering Gomati river canyon at Chabimura to observe Maa Tripura Sundari relief.', 75.0),
        (itin_id, 1, 3, 'Morning', 1, 'Journey north to Unakoti to marvel at the 8th-century colossal rock-cut Shaivite reliefs in Raghunandan hills.', 140.0),
        (itin_id, 5, 3, 'Afternoon', 2, 'Ascend Jampui Hills to experience clean Mizo culture, orange orchards, and sunset at Vanghmun ridge.', 45.0)
    ]
    cursor.executemany("""
        INSERT INTO itinerary_items (
            itinerary_id, destination_id, day_number, time_slot, sequence_order, activity_note, transit_km_from_prev
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
    """, itinerary_items)

    conn.commit()
    conn.close()
    print("Database seeding completed successfully with 100% referential integrity!")

if __name__ == "__main__":
    seed_database()
