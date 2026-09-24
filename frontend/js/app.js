/**
 * Tripura Terra: Core Frontend Application Engine
 * Handles client-side routing, API state synchronization, authentication,
 * interactive Leaflet GIS maps, Chart.js analytics, and modal controllers.
 */

// Global State
const AppState = {
  currentUser: null,
  token: localStorage.getItem('tripura_terra_token') || null,
  districts: [],
  allDestinations: [],
  savedPlacesCount: 0,
  activeRoute: 'home',
  routeParams: null,
  leafletMapInstance: null
};

// API Client Helper
const API = {
  baseUrl: '',

  async request(endpoint, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (AppState.token) {
      headers['Authorization'] = `Bearer ${AppState.token}`;
    }
    try {
      const response = await fetch(this.baseUrl + endpoint, { ...options, headers });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Request failed');
      }
      return data;
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  },

  get(endpoint) { return this.request(endpoint, { method: 'GET' }); },
  post(endpoint, body) { return this.request(endpoint, { method: 'POST', body: JSON.stringify(body) }); },
  put(endpoint, body) { return this.request(endpoint, { method: 'PUT', body: JSON.stringify(body) }); },
  delete(endpoint) { return this.request(endpoint, { method: 'DELETE' }); }
};

// Toast Notification Manager
const Toast = {
  show(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    const icon = type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ');
    toast.innerHTML = `<span style="font-weight: bold; color: ${type === 'success' ? '#a7f3d0' : '#fecaca'}">${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }
};

// Authentication Controller
const AppAuth = {
  async init() {
    if (AppState.token) {
      try {
        const res = await API.get('/api/v1/auth/me');
        AppState.currentUser = res.user;
        AppState.savedPlacesCount = res.stats.saved_places_count;
        this.updateNav();
      } catch (e) {
        this.logout(false);
      }
    } else {
      this.updateNav();
    }
  },

  updateNav() {
    const container = document.getElementById('auth-actions-container');
    const badge = document.getElementById('saved-badge-count');
    if (badge) badge.innerText = AppState.savedPlacesCount || '0';

    if (!container) return;
    if (AppState.currentUser) {
      container.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 0.85rem; font-weight: 600; color: var(--pine-800); cursor: pointer;" onclick="AppRouter.navigate('dashboard')">
            👤 ${AppState.currentUser.full_name.split(' ')[0]}
          </span>
          <button class="btn btn-secondary btn-sm" onclick="AppAuth.logout()">Logout</button>
        </div>
      `;
    } else {
      container.innerHTML = `
        <button class="btn btn-primary btn-sm" onclick="AppAuth.openLoginModal()">Login</button>
      `;
    }
  },

  openLoginModal() {
    const modal = document.getElementById('modal-container');
    modal.style.display = 'flex';
    modal.innerHTML = `
      <div class="modal-backdrop" onclick="if(event.target === this) AppAuth.closeModal()">
        <div class="modal-content">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
            <h3 class="font-serif">Tripura Terra Access</h3>
            <button onclick="AppAuth.closeModal()" style="background:none; border:none; font-size: 1.5rem; cursor:pointer;">&times;</button>
          </div>
          <p class="text-muted" style="font-size: 0.88rem; margin-bottom: 20px;">
            Sign in to explore personalized eco-cultural recommendations, build itineraries, and save travel plans.
          </p>

          <div style="background: var(--sand-bg); padding: 12px; border-radius: var(--radius-md); font-size: 0.82rem; margin-bottom: 20px; border: 1px solid var(--border-subtle);">
            <strong>Demo Accounts:</strong><br>
            • Admin: <code>admin@tripuraterra.in</code> / <code>Admin@Tripura2026</code><br>
            • Tourist: <code>marcus.eco@traveler.org</code> / <code>Traveler@2026</code>
          </div>

          <form id="login-form" onsubmit="AppAuth.handleLogin(event)">
            <div style="margin-bottom: 16px;">
              <label style="display:block; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;">Email Address</label>
              <input type="email" id="login-email" required class="filter-input" style="width: 100%;" value="marcus.eco@traveler.org">
            </div>
            <div style="margin-bottom: 24px;">
              <label style="display:block; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; margin-bottom: 6px;">Password</label>
              <input type="password" id="login-password" required class="filter-input" style="width: 100%;" value="Traveler@2026">
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%;">Sign In</button>
          </form>
        </div>
      </div>
    `;
  },

  closeModal() {
    const modal = document.getElementById('modal-container');
    modal.style.display = 'none';
    modal.innerHTML = '';
  },

  async handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    try {
      const res = await API.post('/api/v1/auth/login', { email, password });
      AppState.token = res.token;
      AppState.currentUser = res.user;
      localStorage.setItem('tripura_terra_token', res.token);
      this.closeModal();
      Toast.show(`Welcome back, ${res.user.full_name}!`);
      this.init();
      AppRouter.refresh();
    } catch (err) {
      Toast.show(err.message, 'error');
    }
  },

  logout(showToast = true) {
    AppState.token = null;
    AppState.currentUser = null;
    AppState.savedPlacesCount = 0;
    localStorage.removeItem('tripura_terra_token');
    this.updateNav();
    if (showToast) Toast.show('You have logged out successfully.');
    AppRouter.navigate('home');
  }
};

// Router
const AppRouter = {
  navigate(route, params = null) {
    AppState.activeRoute = route;
    AppState.routeParams = params;
    window.location.hash = params ? `${route}/${params}` : route;
    this.render();
  },

  refresh() {
    this.render();
  },

  handleHashChange() {
    const hash = window.location.hash.replace('#', '') || 'home';
    const parts = hash.split('/');
    AppState.activeRoute = parts[0];
    AppState.routeParams = parts[1] || null;
    this.render();
  },

  async render() {
    // Update active nav class
    document.querySelectorAll('.nav-link').forEach(el => {
      el.classList.toggle('active', el.getAttribute('data-route') === AppState.activeRoute);
    });

    const viewport = document.getElementById('app-viewport');
    window.scrollTo({ top: 0, behavior: 'smooth' });

    try {
      switch (AppState.activeRoute) {
        case 'home':
          await Views.renderHome(viewport);
          break;
        case 'destinations':
          await Views.renderDestinations(viewport, AppState.routeParams);
          break;
        case 'accommodations':
          await Views.renderAccommodations(viewport);
          break;
        case 'packages':
          await Views.renderPackages(viewport);
          break;
        case 'destination-detail':
          await Views.renderDestinationDetail(viewport, AppState.routeParams);
          break;
        case 'eco-trails':
          await Views.renderEcoTrails(viewport);
          break;
        case 'culture':
          await Views.renderCulture(viewport);
          break;
        case 'planner':
          await Views.renderPlanner(viewport);
          break;
        case 'map':
          await Views.renderGISMap(viewport);
          break;
        case 'analytics':
          await Views.renderAnalytics(viewport);
          break;
        case 'research':
          await Views.renderResearchBenchmarking(viewport);
          break;
        case 'dashboard':
          await Views.renderDashboard(viewport);
          break;
        case 'admin':
          await Views.renderAdminCMS(viewport);
          break;
        default:
          await Views.renderHome(viewport);
      }
    } catch (err) {
      viewport.innerHTML = `
        <div style="text-align: center; padding: 60px var(--space-4);">
          <h2 class="font-serif" style="color: #991b1b;">Connection Error</h2>
          <p class="text-muted" style="margin: 12px 0 24px;">${err.message}</p>
          <button class="btn btn-primary" onclick="AppRouter.refresh()">Retry</button>
        </div>
      `;
    }
  }
};

// View Controllers
const Views = {
  // 1. OFFICIAL TRIPURA TOURISM HOMEPAGE (modeled on tripuratourism.gov.in)
  async renderHome(container) {
    const [destRes, analyticsRes] = await Promise.all([
      API.get('/api/v1/destinations?limit=8&sort_by=rating_desc'),
      API.get('/api/v1/analytics/overview')
    ]);

    const stats = analyticsRes.data;
    const featured = destRes.data;

    container.innerHTML = `
      <!-- Official Hero Carousel Section -->
      <section class="gov-hero-container" id="gov-hero-slider">
        <div class="gov-hero-slide active" style="background-image: url('/static/images/neermahal.jpg');">
          <div class="gov-hero-overlay">
            <span class="badge" style="background: rgba(21, 128, 61, 0.9); color: #fff; margin-bottom: 12px; font-size: 0.82rem; padding: 6px 14px; text-transform: uppercase; letter-spacing: 0.08em;">Tripura's Water Palace • Melaghar</span>
            <h1 class="gov-hero-title">Neermahal Palace</h1>
            <p class="gov-hero-subtitle">The shimmering floating architectural marvel situated in the middle of Rudrasagar Lake, built by Maharaja Bir Bikram.</p>
            <div style="display: flex; gap: 12px;">
              <button class="btn btn-primary" onclick="AppRouter.navigate('destinations', 'dest:neermahal-water-palace')">Explore Neermahal →</button>
              <button class="btn btn-secondary" onclick="Views.openLodgeBookingModal('Sagarika Parjatan Niwas (Rudrasagar)')">Book Nearby Lodge 🏨</button>
            </div>
          </div>
        </div>

        <div class="gov-hero-slide" style="background-image: url('/static/images/unakoti.jpg');">
          <div class="gov-hero-overlay">
            <span class="badge" style="background: rgba(180, 83, 9, 0.9); color: #fff; margin-bottom: 12px; font-size: 0.82rem; padding: 6px 14px; text-transform: uppercase; letter-spacing: 0.08em;">National Heritage • Kailashahar</span>
            <h1 class="gov-hero-title">Unakoti Rock-Cut Reliefs</h1>
            <p class="gov-hero-subtitle">7th-9th century colossal stone carvings of Lord Shiva and Ganesha carved directly into vertical forest gorges.</p>
            <div style="display: flex; gap: 12px;">
              <button class="btn btn-primary" onclick="AppRouter.navigate('destinations', 'dest:unakoti-rock-cut-reliefs')">Explore Unakoti →</button>
              <button class="btn btn-secondary" onclick="AppRouter.navigate('packages')">Conducted Tours 🎒</button>
            </div>
          </div>
        </div>

        <div class="gov-hero-slide" style="background-image: url('/static/images/ujjayanta.jpg');">
          <div class="gov-hero-overlay">
            <span class="badge" style="background: rgba(21, 128, 61, 0.9); color: #fff; margin-bottom: 12px; font-size: 0.82rem; padding: 6px 14px; text-transform: uppercase; letter-spacing: 0.08em;">Capital Heritage • Agartala</span>
            <h1 class="gov-hero-title">Ujjayanta Palace & State Museum</h1>
            <p class="gov-hero-subtitle">The neoclassical white crown of the Manikya Dynasty featuring grand Mughal gardens, fountains, and state ethnography.</p>
            <div style="display: flex; gap: 12px;">
              <button class="btn btn-primary" onclick="AppRouter.navigate('destinations', 'dest:ujjayanta-palace-museum')">View Details →</button>
              <button class="btn btn-secondary" onclick="Views.openLodgeBookingModal('Geetanjali Tourism Guest House (Agartala)')">Stay in Agartala 🏨</button>
            </div>
          </div>
        </div>

        <div class="gov-hero-slide" style="background-image: url('/static/images/tripura_sundari.jpg');">
          <div class="gov-hero-overlay">
            <span class="badge" style="background: rgba(185, 28, 28, 0.9); color: #fff; margin-bottom: 12px; font-size: 0.82rem; padding: 6px 14px; text-transform: uppercase; letter-spacing: 0.08em;">51 Shakti Peethas • Udaipur</span>
            <h1 class="gov-hero-title">Maa Tripura Sundari Temple</h1>
            <p class="gov-hero-subtitle">Ancient 1501 CE sacred shrine of Goddess Kali on tortoise hillock, fronting the holy Kalyan Sagar lake.</p>
            <div style="display: flex; gap: 12px;">
              <button class="btn btn-primary" onclick="AppRouter.navigate('destinations', 'dest:tripura-sundari-temple')">Visit Matabari →</button>
              <button class="btn btn-secondary" onclick="Views.openLodgeBookingModal('Tepania Tourist Log Hut (Udaipur)')">Book Udaipur Stay 🏨</button>
            </div>
          </div>
        </div>

        <div class="gov-hero-slide" style="background-image: url('/static/images/chabimura.jpg');">
          <div class="gov-hero-overlay">
            <span class="badge" style="background: rgba(21, 128, 61, 0.9); color: #fff; margin-bottom: 12px; font-size: 0.82rem; padding: 6px 14px; text-transform: uppercase; letter-spacing: 0.08em;">River Canyon Wonder • Amarpur</span>
            <h1 class="gov-hero-title">Chabimura River Gorge</h1>
            <p class="gov-hero-subtitle">The Amazon of Tripura — dramatic jungle cliffs rising above Gomati river with ancient rock-carved deities.</p>
            <div style="display: flex; gap: 12px;">
              <button class="btn btn-primary" onclick="AppRouter.navigate('destinations', 'dest:chabimura-rock-carvings')">Boat Safari Details →</button>
            </div>
          </div>
        </div>

        <div class="gov-hero-slide" style="background-image: url('/static/images/jampui_hills.jpg');">
          <div class="gov-hero-overlay">
            <span class="badge" style="background: rgba(2, 132, 199, 0.9); color: #fff; margin-bottom: 12px; font-size: 0.82rem; padding: 6px 14px; text-transform: uppercase; letter-spacing: 0.08em;">Hill Station • North Tripura</span>
            <h1 class="gov-hero-title">Jampui Hills & Vanghmun</h1>
            <p class="gov-hero-subtitle">Seat of eternal spring at 3,000 feet, celebrated for cool breezes, orange orchards, and panoramic sunrise vistas.</p>
            <div style="display: flex; gap: 12px;">
              <button class="btn btn-primary" onclick="AppRouter.navigate('destinations', 'dest:jampui-hills-vanghmun')">Explore Jampui →</button>
              <button class="btn btn-secondary" onclick="Views.openLodgeBookingModal('Eden Tourist Lodge (Jampui Hills)')">Book Eden Lodge 🏨</button>
            </div>
          </div>
        </div>
      </section>

      <!-- Live Search & Booking Widget (matching tourism.tripura.gov.in) -->
      <div class="gov-search-bar">
        <div class="gov-search-field">
          <label>📍 Where to Explore</label>
          <select id="quick-search-location">
            <option value="all">All Locations (Tripura)</option>
            <option value="West Tripura">Agartala / West Tripura</option>
            <option value="Sepahijala">Melaghar / Neermahal (Sepahijala)</option>
            <option value="Gomati">Udaipur / Matabari / Chabimura</option>
            <option value="Unakoti">Kailashahar / Unakoti</option>
            <option value="North Tripura">Jampui Hills / Vanghmun</option>
            <option value="South Tripura">Pilak / Trishna Sanctuary</option>
            <option value="Dhalai">Dumbur Lake / Gandacherra</option>
            <option value="Khowai">Baramura / Hathai Kotor</option>
          </select>
        </div>

        <div class="gov-search-field">
          <label>🏨 Service / Category</label>
          <select id="quick-search-type">
            <option value="all">All Attractions & Services</option>
            <option value="lodges">TTDCL Tourist Lodges & Log Huts</option>
            <option value="royal_palace">Royal Palaces & Heritage</option>
            <option value="rock_carving">Ancient Rock Carvings</option>
            <option value="temple_complex">Sacred Temples & Peethas</option>
            <option value="eco_sanctuary">Eco Sanctuaries & Wildlife</option>
            <option value="hill_station">Hill Station Ridges</option>
          </select>
        </div>

        <div class="gov-search-field" style="max-width: 160px;">
          <label>📅 Check-in Date</label>
          <input type="date" id="quick-checkin-date" value="${new Date().toISOString().split('T')[0]}">
        </div>

        <div class="gov-search-field" style="max-width: 160px;">
          <label>📅 Check-out Date</label>
          <input type="date" id="quick-checkout-date" value="${new Date(Date.now() + 86400000 * 2).toISOString().split('T')[0]}">
        </div>

        <button class="gov-search-btn" onclick="Views.executeQuickSearch()">
          <span>🔍</span>
          <span>Search & Book</span>
        </button>
      </div>

      <!-- TTDCL Government Tourist Lodges Showcase (Directly from tourism.tripura.gov.in) -->
      <section style="margin: 48px 0;">
        <div class="section-header">
          <div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="badge" style="background: #15803d; color: white;">Featured Stays</span>
              <span class="badge badge-pristine">Online Booking Active</span>
            </div>
            <h2 class="section-title" style="margin-top: 8px;">Tourist Lodges & Log Huts</h2>
            <p class="section-subtitle">Comfortable eco lodges, guest houses, and nature stays across Tripura.</p>
          </div>
          <button class="btn btn-outline btn-sm" onclick="AppRouter.navigate('accommodations')">View All Lodges (6) →</button>
        </div>

        <div class="ttdcl-lodges-grid">
          <!-- Lodge 1: Eden Tourist Lodge -->
          <div class="ttdcl-lodge-card">
            <div class="lodge-img-wrap">
              <span class="lodge-govt-tag">TTDCL Property</span>
              <img src="/static/images/eden_lodge.jpg" alt="Eden Tourist Lodge" onerror="this.src='/static/images/jampui_hills.jpg'">
            </div>
            <div class="lodge-card-body">
              <div class="lodge-location">📍 Vanghmun, Jampui Hills (North Tripura)</div>
              <h3 class="lodge-name">Eden Tourist Lodge</h3>
              <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
                Perched high on the Jampui ridge amidst orange orchards with cool breeze and breathtaking valley views of Mizoram.
              </p>
              <div class="lodge-amenities-pills">
                <span class="amenity-pill">❄️ AC & Non-AC</span>
                <span class="amenity-pill">📶 Wi-Fi</span>
                <span class="amenity-pill">🍽️ Restaurant</span>
                <span class="amenity-pill">🌄 Valley View</span>
              </div>
              <div class="lodge-footer-action">
                <div>
                  <span class="lodge-price-val">₹1,200</span>
                  <span class="lodge-price-unit">/ night</span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Eden Tourist Lodge (Jampui Hills)')">Book Room</button>
              </div>
            </div>
          </div>

          <!-- Lodge 2: Sagarika Parjatan Niwas -->
          <div class="ttdcl-lodge-card">
            <div class="lodge-img-wrap">
              <span class="lodge-govt-tag">TTDCL Property</span>
              <img src="/static/images/sagarika_lodge.jpg" alt="Sagarika Parjatan Niwas" onerror="this.src='/static/images/neermahal.jpg'">
            </div>
            <div class="lodge-card-body">
              <div class="lodge-location">📍 Melaghar, Rudrasagar Lake (Sepahijala)</div>
              <h3 class="lodge-name">Sagarika Parjatan Niwas</h3>
              <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
                Prime lakeside accommodation at the banks of Rudrasagar Lake with direct jetty access for Neermahal Palace boat tours.
              </p>
              <div class="lodge-amenities-pills">
                <span class="amenity-pill">🚤 Boat Jetty</span>
                <span class="amenity-pill">❄️ Deluxe AC</span>
                <span class="amenity-pill">🍽️ Dining Hall</span>
                <span class="amenity-pill">🌊 Lake View</span>
              </div>
              <div class="lodge-footer-action">
                <div>
                  <span class="lodge-price-val">₹1,500</span>
                  <span class="lodge-price-unit">/ night</span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Sagarika Parjatan Niwas (Rudrasagar)')">Book Room</button>
              </div>
            </div>
          </div>

          <!-- Lodge 3: Geetanjali Tourism Guest House -->
          <div class="ttdcl-lodge-card">
            <div class="lodge-img-wrap">
              <span class="lodge-govt-tag">TTDCL Property</span>
              <img src="/static/images/geetanjali_lodge.jpg" alt="Geetanjali Tourism Guest House" onerror="this.src='/static/images/ujjayanta.jpg'">
            </div>
            <div class="lodge-card-body">
              <div class="lodge-location">📍 Kunjaban, Agartala (West Tripura)</div>
              <h3 class="lodge-name">Geetanjali Tourism Guest House</h3>
              <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
                Premium government guest house in the state capital, close to Ujjayanta Palace, Heritage Park, and Agartala Airport.
              </p>
              <div class="lodge-amenities-pills">
                <span class="amenity-pill">💼 Conference Hall</span>
                <span class="amenity-pill">❄️ Executive AC</span>
                <span class="amenity-pill">🅿️ Free Parking</span>
                <span class="amenity-pill">🍽️ Multi-Cuisine</span>
              </div>
              <div class="lodge-footer-action">
                <div>
                  <span class="lodge-price-val">₹2,000</span>
                  <span class="lodge-price-unit">/ night</span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Geetanjali Tourism Guest House (Agartala)')">Book Room</button>
              </div>
            </div>
          </div>

          <!-- Lodge 4: Tepania Tourist Log Hut -->
          <div class="ttdcl-lodge-card">
            <div class="lodge-img-wrap">
              <span class="lodge-govt-tag">TTDCL Eco Loghut</span>
              <img src="/static/images/tepania_loghut.jpg" alt="Tepania Tourist Log Hut" onerror="this.src='/static/images/tripura_sundari.jpg'">
            </div>
            <div class="lodge-card-body">
              <div class="lodge-location">📍 Udaipur, Gomati District</div>
              <h3 class="lodge-name">Tepania Tourist Log Hut</h3>
              <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
                Rustic wooden log huts set inside the tranquil Tepania Eco-Park forest, 6 km from Maa Tripura Sundari Temple.
              </p>
              <div class="lodge-amenities-pills">
                <span class="amenity-pill">🪵 Wooden Cottages</span>
                <span class="amenity-pill">🌲 Eco Park</span>
                <span class="amenity-pill">❄️ AC Log Huts</span>
                <span class="amenity-pill">🐦 Birding Trail</span>
              </div>
              <div class="lodge-footer-action">
                <div>
                  <span class="lodge-price-val">₹1,800</span>
                  <span class="lodge-price-unit">/ night</span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Tepania Tourist Log Hut (Udaipur)')">Book Room</button>
              </div>
            </div>
          </div>

          <!-- Lodge 5: Kashba View Tourist Lodge -->
          <div class="ttdcl-lodge-card">
            <div class="lodge-img-wrap">
              <span class="lodge-govt-tag">TTDCL Property</span>
              <img src="/static/images/kashba_lodge.jpg" alt="Kashba View Tourist Lodge" onerror="this.src='/static/images/home_banner2.jpeg'">
            </div>
            <div class="lodge-card-body">
              <div class="lodge-location">📍 Kamalasagar, Sepahijala District</div>
              <h3 class="lodge-name">Kashba View Tourist Lodge</h3>
              <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
                Scenic hillside lodge overlooking the historic 15th-century Kamalasagar Lake and Kasba Kalibari on the border.
              </p>
              <div class="lodge-amenities-pills">
                <span class="amenity-pill">🌊 Border Lake View</span>
                <span class="amenity-pill">❄️ AC Rooms</span>
                <span class="amenity-pill">🍽️ Bengali Cuisine</span>
              </div>
              <div class="lodge-footer-action">
                <div>
                  <span class="lodge-price-val">₹1,400</span>
                  <span class="lodge-price-unit">/ night</span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Kashba View Tourist Lodge (Kamalasagar)')">Book Room</button>
              </div>
            </div>
          </div>

          <!-- Lodge 6: Sepahijala Wildlife Loghut -->
          <div class="ttdcl-lodge-card">
            <div class="lodge-img-wrap">
              <span class="lodge-govt-tag">TTDCL Eco Haven</span>
              <img src="/static/images/sepahijala.jpg" alt="Sepahijala Loghut">
            </div>
            <div class="lodge-card-body">
              <div class="lodge-location">📍 Bishramganj, Sepahijala Sanctuary</div>
              <h3 class="lodge-name">Sepahijala Sanctuary Loghut</h3>
              <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
                Immersive forest rest house situated right inside the bio-rich wildlife sanctuary and Clouded Leopard National Park.
              </p>
              <div class="lodge-amenities-pills">
                <span class="amenity-pill">🐆 Wildlife Habitat</span>
                <span class="amenity-pill">🪵 Forest Huts</span>
                <span class="amenity-pill">🌿 Nature Walk</span>
              </div>
              <div class="lodge-footer-action">
                <div>
                  <span class="lodge-price-val">₹1,600</span>
                  <span class="lodge-price-unit">/ night</span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Sepahijala Sanctuary Loghut')">Book Room</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Key Tourist Destinations Showcase -->
      <section style="margin: 64px 0;">
        <div class="section-header">
          <div>
            <h2 class="section-title">Major Destinations of Tripura</h2>
            <p class="section-subtitle">Official verified heritage, archaeological, and ecological landmarks across 8 districts</p>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="AppRouter.navigate('destinations')">View All Destinations (${stats.total_destinations}) →</button>
        </div>

        <div class="destinations-grid">
          ${featured.map(d => Views.renderDestinationCardHTML(d)).join('')}
        </div>
      </section>

      <!-- Official Conducted Tour Packages (modeled on tripuratourism.gov.in) -->
      <section style="margin: 64px 0; background: #ffffff; padding: 40px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 20px rgba(0,0,0,0.04);">
        <div class="section-header">
          <div>
            <span class="badge" style="background: #b45309; color: #fff;">Conducted Package Tours</span>
            <h2 class="section-title" style="margin-top: 8px;">Tripura Tourism Guided Packages</h2>
            <p class="section-subtitle">Comfortable AC coach tours with verified guides, entrance tickets, and TTDCL lodge stays included</p>
          </div>
          <button class="btn btn-primary btn-sm" onclick="AppRouter.navigate('packages')">Explore All Packages →</button>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; margin-top: 24px;">
          <!-- Package 1 -->
          <div class="package-card">
            <div class="package-header" style="background-image: linear-gradient(180deg, rgba(0,0,0,0.2), rgba(0,0,0,0.85)), url('/static/images/neermahal.jpg');">
              <span class="package-duration-badge">⏱️ 1 Day / Same Day Return</span>
              <div>
                <h3 style="color: #fff; font-size: 1.25rem;">Capital & Lake Palace Tour</h3>
                <span style="color: #fde047; font-size: 0.85rem;">Agartala • Neermahal • Sepahijala</span>
              </div>
            </div>
            <div style="padding: 20px; display: flex; flex-direction: column; flex: 1;">
              <ul style="font-size: 0.85rem; color: #475569; line-height: 1.8; margin-bottom: 16px; padding-left: 18px;">
                <li>Pick up from Geetanjali Guest House, Agartala</li>
                <li>Ujjayanta Palace & State Museum exploration</li>
                <li>Speedboat ride to Neermahal Water Palace</li>
                <li>Sepahijala Wildlife Sanctuary and Langur trails</li>
              </ul>
              <div style="margin-top: auto; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 14px;">
                <div>
                  <span style="font-size: 1.35rem; font-weight: 800; color: #15803d;">₹1,450</span>
                  <span style="font-size: 0.75rem; color: #64748b;">/ person</span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="Views.openPackageBookingModal('Capital & Lake Palace Tour (1 Day)')">Book Package</button>
              </div>
            </div>
          </div>

          <!-- Package 2 -->
          <div class="package-card">
            <div class="package-header" style="background-image: linear-gradient(180deg, rgba(0,0,0,0.2), rgba(0,0,0,0.85)), url('/static/images/unakoti.jpg');">
              <span class="package-duration-badge">⏱️ 2 Days / 1 Night</span>
              <div>
                <h3 style="color: #fff; font-size: 1.25rem;">Unakoti & Jampui Ridge Expedition</h3>
                <span style="color: #fde047; font-size: 0.85rem;">Kailashahar • Jampui Hills • Vanghmun</span>
              </div>
            </div>
            <div style="padding: 20px; display: flex; flex-direction: column; flex: 1;">
              <ul style="font-size: 0.85rem; color: #475569; line-height: 1.8; margin-bottom: 16px; padding-left: 18px;">
                <li>Scenic drive through northern foothills</li>
                <li>Guided tour of 30ft rock carvings at Unakoti</li>
                <li>Overnight stay at Eden Tourist Lodge, Vanghmun</li>
                <li>Sunrise ridge walk & orange orchard visits</li>
              </ul>
              <div style="margin-top: auto; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 14px;">
                <div>
                  <span style="font-size: 1.35rem; font-weight: 800; color: #15803d;">₹3,800</span>
                  <span style="font-size: 0.75rem; color: #64748b;">/ person</span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="Views.openPackageBookingModal('Unakoti & Jampui Ridge Expedition (2D/1N)')">Book Package</button>
              </div>
            </div>
          </div>

          <!-- Package 3 -->
          <div class="package-card">
            <div class="package-header" style="background-image: linear-gradient(180deg, rgba(0,0,0,0.2), rgba(0,0,0,0.85)), url('/static/images/chabimura.jpg');">
              <span class="package-duration-badge">⏱️ 3 Days / 2 Nights</span>
              <div>
                <h3 style="color: #fff; font-size: 1.25rem;">Complete Spiritual & Eco Wonder Circuit</h3>
                <span style="color: #fde047; font-size: 0.85rem;">Matabari • Chabimura • Dumbur Lake</span>
              </div>
            </div>
            <div style="padding: 20px; display: flex; flex-direction: column; flex: 1;">
              <ul style="font-size: 0.85rem; color: #475569; line-height: 1.8; margin-bottom: 16px; padding-left: 18px;">
                <li>Darshan at 500-yr Maa Tripura Sundari Temple</li>
                <li>Chabimura Gomati river canyon boat safari</li>
                <li>Dumbur Lake archipelago & Narikel Kunja retreat</li>
                <li>Accommodations at Tepania Log Hut & Dumbur</li>
              </ul>
              <div style="margin-top: auto; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 14px;">
                <div>
                  <span style="font-size: 1.35rem; font-weight: 800; color: #15803d;">₹5,600</span>
                  <span style="font-size: 0.75rem; color: #64748b;">/ person</span>
                </div>
                <button class="btn btn-primary btn-sm" onclick="Views.openPackageBookingModal('Complete Spiritual & Eco Wonder Circuit (3D/2N)')">Book Package</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Fairs, Festivals & Indigenous Culture Section -->
      <section style="margin: 64px 0;">
        <div class="section-header">
          <div>
            <h2 class="section-title">Festivals & Cultural Heritage</h2>
            <p class="section-subtitle">Experience living Tripuri royal customs, sacred indigenous pujas, and bamboo crafts</p>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="AppRouter.navigate('culture')">Discover Heritage →</button>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
          <div style="background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
            <div style="font-size: 2rem; margin-bottom: 12px;">🪔</div>
            <h3 style="font-size: 1.2rem; color: #15803d; margin-bottom: 8px;">Kharchi Puja</h3>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
              The grand 7-day royal festival honoring the Fourteen Gods (Chaturdasha Devata) at Old Agartala, celebrated with vibrant cultural fairs.
            </p>
          </div>

          <div style="background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
            <div style="font-size: 2rem; margin-bottom: 12px;">🌾</div>
            <h3 style="font-size: 1.2rem; color: #15803d; margin-bottom: 8px;">Garia Festival</h3>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
              Sacred indigenous harvest dance festival celebrated by Tripuri, Reang, and Jamatia communities with sacred bamboo deities and community feasts.
            </p>
          </div>

          <div style="background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
            <div style="font-size: 2rem; margin-bottom: 12px;">🚣</div>
            <h3 style="font-size: 1.2rem; color: #15803d; margin-bottom: 8px;">Neermahal Water Festival</h3>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
              Annual aquatic carnival featuring thrilling traditional long-boat races on Rudrasagar Lake and cultural night dances at the illuminated palace.
            </p>
          </div>

          <div style="background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
            <div style="font-size: 2rem; margin-bottom: 12px;">🍊</div>
            <h3 style="font-size: 1.2rem; color: #15803d; margin-bottom: 8px;">Orange & Tourism Festival</h3>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
              Held in winter in the picturesque Jampui Hills celebrating the bountiful sweet orange harvest, Lushai folk dances, and mist walks.
            </p>
          </div>
        </div>
      </section>
    `;

    // Start hero carousel auto-sliding
    Views.initHeroSlider();
  },

  initHeroSlider() {
    if (window._heroSliderInterval) clearInterval(window._heroSliderInterval);
    const slides = document.querySelectorAll('.gov-hero-slide');
    if (!slides || slides.length === 0) return;
    let currentIdx = 0;

    window._heroSliderInterval = setInterval(() => {
      slides[currentIdx].classList.remove('active');
      currentIdx = (currentIdx + 1) % slides.length;
      slides[currentIdx].classList.add('active');
    }, 4500);
  },

  executeQuickSearch() {
    const loc = document.getElementById('quick-search-location').value;
    const type = document.getElementById('quick-search-type').value;

    if (type === 'lodges') {
      AppRouter.navigate('accommodations');
      return;
    }

    if (loc !== 'all' && type !== 'all') {
      AppRouter.navigate('destinations', `type:${type}`);
    } else if (loc !== 'all') {
      AppRouter.navigate('destinations', `district:${loc}`);
    } else if (type !== 'all') {
      AppRouter.navigate('destinations', `type:${type}`);
    } else {
      AppRouter.navigate('destinations');
    }
  },

  // 1B. OFFICIAL ACCOMMODATION / LODGES VIEW
  async renderAccommodations(container) {
    container.innerHTML = `
      <div style="margin-bottom: 32px;">
        <span class="badge" style="background: #15803d; color: white;">Tripura Tourism</span>
        <h1 class="font-serif" style="font-size: 2.4rem; margin: 8px 0;">Tourist Lodges & Stays</h1>
        <p class="text-muted">Direct reservations for curated tourist lodges, guest houses, and eco log huts across Tripura.</p>
      </div>

      <div class="ttdcl-lodges-grid">
        <!-- Lodge 1 -->
        <div class="ttdcl-lodge-card">
          <div class="lodge-img-wrap">
            <span class="lodge-govt-tag">TTDCL Property</span>
            <img src="/static/images/eden_lodge.jpg" alt="Eden Tourist Lodge" onerror="this.src='/static/images/jampui_hills.jpg'">
          </div>
          <div class="lodge-card-body">
            <div class="lodge-location">📍 Vanghmun, Jampui Hills (North Tripura)</div>
            <h3 class="lodge-name">Eden Tourist Lodge</h3>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
              Perched high on the Jampui ridge amidst orange orchards with cool breeze and breathtaking valley views of Mizoram.
            </p>
            <div class="lodge-amenities-pills">
              <span class="amenity-pill">❄️ AC & Non-AC</span>
              <span class="amenity-pill">📶 Wi-Fi</span>
              <span class="amenity-pill">🍽️ Restaurant</span>
              <span class="amenity-pill">🌄 Valley View</span>
            </div>
            <div class="lodge-footer-action">
              <div>
                <span class="lodge-price-val">₹1,200</span>
                <span class="lodge-price-unit">/ night</span>
              </div>
              <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Eden Tourist Lodge (Jampui Hills)')">Book Room</button>
            </div>
          </div>
        </div>

        <!-- Lodge 2 -->
        <div class="ttdcl-lodge-card">
          <div class="lodge-img-wrap">
            <span class="lodge-govt-tag">TTDCL Property</span>
            <img src="/static/images/sagarika_lodge.jpg" alt="Sagarika Parjatan Niwas" onerror="this.src='/static/images/neermahal.jpg'">
          </div>
          <div class="lodge-card-body">
            <div class="lodge-location">📍 Melaghar, Rudrasagar Lake (Sepahijala)</div>
            <h3 class="lodge-name">Sagarika Parjatan Niwas</h3>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
              Prime lakeside accommodation at the banks of Rudrasagar Lake with direct jetty access for Neermahal Palace boat tours.
            </p>
            <div class="lodge-amenities-pills">
              <span class="amenity-pill">🚤 Boat Jetty</span>
              <span class="amenity-pill">❄️ Deluxe AC</span>
              <span class="amenity-pill">🍽️ Dining Hall</span>
              <span class="amenity-pill">🌊 Lake View</span>
            </div>
            <div class="lodge-footer-action">
              <div>
                <span class="lodge-price-val">₹1,500</span>
                <span class="lodge-price-unit">/ night</span>
              </div>
              <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Sagarika Parjatan Niwas (Rudrasagar)')">Book Room</button>
            </div>
          </div>
        </div>

        <!-- Lodge 3 -->
        <div class="ttdcl-lodge-card">
          <div class="lodge-img-wrap">
            <span class="lodge-govt-tag">TTDCL Property</span>
            <img src="/static/images/geetanjali_lodge.jpg" alt="Geetanjali Tourism Guest House" onerror="this.src='/static/images/ujjayanta.jpg'">
          </div>
          <div class="lodge-card-body">
            <div class="lodge-location">📍 Kunjaban, Agartala (West Tripura)</div>
            <h3 class="lodge-name">Geetanjali Tourism Guest House</h3>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
              Premium government guest house in the state capital, close to Ujjayanta Palace, Heritage Park, and Agartala Airport.
            </p>
            <div class="lodge-amenities-pills">
              <span class="amenity-pill">💼 Conference Hall</span>
              <span class="amenity-pill">❄️ Executive AC</span>
              <span class="amenity-pill">🅿️ Free Parking</span>
              <span class="amenity-pill">🍽️ Multi-Cuisine</span>
            </div>
            <div class="lodge-footer-action">
              <div>
                <span class="lodge-price-val">₹2,000</span>
                <span class="lodge-price-unit">/ night</span>
              </div>
              <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Geetanjali Tourism Guest House (Agartala)')">Book Room</button>
            </div>
          </div>
        </div>

        <!-- Lodge 4 -->
        <div class="ttdcl-lodge-card">
          <div class="lodge-img-wrap">
            <span class="lodge-govt-tag">TTDCL Eco Loghut</span>
            <img src="/static/images/tepania_loghut.jpg" alt="Tepania Tourist Log Hut" onerror="this.src='/static/images/tripura_sundari.jpg'">
          </div>
          <div class="lodge-card-body">
            <div class="lodge-location">📍 Udaipur, Gomati District</div>
            <h3 class="lodge-name">Tepania Tourist Log Hut</h3>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
              Rustic wooden log huts set inside the tranquil Tepania Eco-Park forest, 6 km from Maa Tripura Sundari Temple.
            </p>
            <div class="lodge-amenities-pills">
              <span class="amenity-pill">🪵 Wooden Cottages</span>
              <span class="amenity-pill">🌲 Eco Park</span>
              <span class="amenity-pill">❄️ AC Log Huts</span>
              <span class="amenity-pill">🐦 Birding Trail</span>
            </div>
            <div class="lodge-footer-action">
              <div>
                <span class="lodge-price-val">₹1,800</span>
                <span class="lodge-price-unit">/ night</span>
              </div>
              <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Tepania Tourist Log Hut (Udaipur)')">Book Room</button>
            </div>
          </div>
        </div>

        <!-- Lodge 5 -->
        <div class="ttdcl-lodge-card">
          <div class="lodge-img-wrap">
            <span class="lodge-govt-tag">TTDCL Property</span>
            <img src="/static/images/kashba_lodge.jpg" alt="Kashba View Tourist Lodge" onerror="this.src='/static/images/home_banner2.jpeg'">
          </div>
          <div class="lodge-card-body">
            <div class="lodge-location">📍 Kamalasagar, Sepahijala District</div>
            <h3 class="lodge-name">Kashba View Tourist Lodge</h3>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
              Scenic hillside lodge overlooking the historic 15th-century Kamalasagar Lake and Kasba Kalibari on the border.
            </p>
            <div class="lodge-amenities-pills">
              <span class="amenity-pill">🌊 Border Lake View</span>
              <span class="amenity-pill">❄️ AC Rooms</span>
              <span class="amenity-pill">🍽️ Bengali Cuisine</span>
            </div>
            <div class="lodge-footer-action">
              <div>
                <span class="lodge-price-val">₹1,400</span>
                <span class="lodge-price-unit">/ night</span>
              </div>
              <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Kashba View Tourist Lodge (Kamalasagar)')">Book Room</button>
            </div>
          </div>
        </div>

        <!-- Lodge 6 -->
        <div class="ttdcl-lodge-card">
          <div class="lodge-img-wrap">
            <span class="lodge-govt-tag">TTDCL Eco Haven</span>
            <img src="/static/images/sepahijala.jpg" alt="Sepahijala Loghut">
          </div>
          <div class="lodge-card-body">
            <div class="lodge-location">📍 Bishramganj, Sepahijala Sanctuary</div>
            <h3 class="lodge-name">Sepahijala Sanctuary Loghut</h3>
            <p style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
              Immersive forest rest house situated right inside the bio-rich wildlife sanctuary and Clouded Leopard National Park.
            </p>
            <div class="lodge-amenities-pills">
              <span class="amenity-pill">🐆 Wildlife Habitat</span>
              <span class="amenity-pill">🪵 Forest Huts</span>
              <span class="amenity-pill">🌿 Nature Walk</span>
            </div>
            <div class="lodge-footer-action">
              <div>
                <span class="lodge-price-val">₹1,600</span>
                <span class="lodge-price-unit">/ night</span>
              </div>
              <button class="btn btn-primary btn-sm" onclick="Views.openLodgeBookingModal('Sepahijala Sanctuary Loghut')">Book Room</button>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  // 1C. TOUR PACKAGES VIEW
  async renderPackages(container) {
    container.innerHTML = `
      <div style="margin-bottom: 32px;">
        <span class="badge" style="background: #b45309; color: white;">Conducted Tours</span>
        <h1 class="font-serif" style="font-size: 2.4rem; margin: 8px 0;">Official Conducted Tour Packages</h1>
        <p class="text-muted">Curated itineraries by Tripura Tourism with AC transportation, government lodge stays, and local expert guides.</p>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 28px;">
        <!-- Package 1 -->
        <div class="package-card">
          <div class="package-header" style="background-image: linear-gradient(180deg, rgba(0,0,0,0.2), rgba(0,0,0,0.85)), url('/static/images/neermahal.jpg');">
            <span class="package-duration-badge">⏱️ 1 Day / Same Day Return</span>
            <div>
              <h3 style="color: #fff; font-size: 1.3rem;">Capital & Lake Palace Tour</h3>
              <span style="color: #fde047; font-size: 0.85rem;">Agartala • Neermahal • Sepahijala</span>
            </div>
          </div>
          <div style="padding: 24px; display: flex; flex-direction: column; flex: 1;">
            <p style="font-size: 0.88rem; color: #475569; margin-bottom: 16px;">
              Designed for travelers seeking an authentic introduction to royal Manikya architecture and pristine wetland nature.
            </p>
            <ul style="font-size: 0.85rem; color: #334155; line-height: 1.8; margin-bottom: 20px; padding-left: 18px;">
              <li>08:00 AM: Departure from Geetanjali Guest House, Agartala</li>
              <li>09:00 AM: Ujjayanta Palace & State Ethnography Museum</li>
              <li>12:30 PM: Traditional lunch at Sagarika Parjatan Niwas</li>
              <li>01:30 PM: Motorboat cruise to Neermahal Water Palace</li>
              <li>03:30 PM: Sepahijala Sanctuary & Clouded Leopard Park</li>
              <li>06:00 PM: Return arrival in Agartala</li>
            </ul>
            <div style="margin-top: auto; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 16px;">
              <div>
                <span style="font-size: 1.4rem; font-weight: 800; color: #15803d;">₹1,450</span>
                <span style="font-size: 0.75rem; color: #64748b;">/ person</span>
              </div>
              <button class="btn btn-primary" onclick="Views.openPackageBookingModal('Capital & Lake Palace Tour (1 Day)')">Book Tour</button>
            </div>
          </div>
        </div>

        <!-- Package 2 -->
        <div class="package-card">
          <div class="package-header" style="background-image: linear-gradient(180deg, rgba(0,0,0,0.2), rgba(0,0,0,0.85)), url('/static/images/unakoti.jpg');">
            <span class="package-duration-badge">⏱️ 2 Days / 1 Night</span>
            <div>
              <h3 style="color: #fff; font-size: 1.3rem;">Unakoti & Jampui Ridge Expedition</h3>
              <span style="color: #fde047; font-size: 0.85rem;">Kailashahar • Jampui Hills • Vanghmun</span>
            </div>
          </div>
          <div style="padding: 24px; display: flex; flex-direction: column; flex: 1;">
            <p style="font-size: 0.88rem; color: #475569; margin-bottom: 16px;">
              Journey into sub-Himalayan rainforest ravines to witness thousand-year-old rock sculptures and experience the heights of Jampui.
            </p>
            <ul style="font-size: 0.85rem; color: #334155; line-height: 1.8; margin-bottom: 20px; padding-left: 18px;">
              <li>Day 1: Scenic drive to Unakoti rock carvings with ASI guide</li>
              <li>Day 1: Mountain ridge drive to Vanghmun model eco-village</li>
              <li>Day 1: Night stay at Eden Tourist Lodge with bonfire dinner</li>
              <li>Day 2: Sunrise viewpoint at Betlingchhip Peak (930m)</li>
              <li>Day 2: Orange orchard visits & Return to Agartala</li>
            </ul>
            <div style="margin-top: auto; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 16px;">
              <div>
                <span style="font-size: 1.4rem; font-weight: 800; color: #15803d;">₹3,800</span>
                <span style="font-size: 0.75rem; color: #64748b;">/ person</span>
              </div>
              <button class="btn btn-primary" onclick="Views.openPackageBookingModal('Unakoti & Jampui Ridge Expedition (2D/1N)')">Book Tour</button>
            </div>
          </div>
        </div>

        <!-- Package 3 -->
        <div class="package-card">
          <div class="package-header" style="background-image: linear-gradient(180deg, rgba(0,0,0,0.2), rgba(0,0,0,0.85)), url('/static/images/chabimura.jpg');">
            <span class="package-duration-badge">⏱️ 3 Days / 2 Nights</span>
            <div>
              <h3 style="color: #fff; font-size: 1.3rem;">Complete Spiritual & Eco Wonder Circuit</h3>
              <span style="color: #fde047; font-size: 0.85rem;">Matabari • Chabimura • Dumbur Lake</span>
            </div>
          </div>
          <div style="padding: 24px; display: flex; flex-direction: column; flex: 1;">
            <p style="font-size: 0.88rem; color: #475569; margin-bottom: 16px;">
              The ultimate exploration of Tripura's sacred Shakti heritage, Amazonian Gomati river canyons, and island archipelagos.
            </p>
            <ul style="font-size: 0.85rem; color: #334155; line-height: 1.8; margin-bottom: 20px; padding-left: 18px;">
              <li>Day 1: Agartala to Udaipur, darshan at Tripura Sundari Temple</li>
              <li>Day 1: Overnight stay at Tepania Tourist Log Hut</li>
              <li>Day 2: Morning boat safari in Chabimura vertical canyon</li>
              <li>Day 2: Afternoon transfer to Dumbur Lake & Narikel Kunja</li>
              <li>Day 3: Island boat cruise and return to Agartala</li>
            </ul>
            <div style="margin-top: auto; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 16px;">
              <div>
                <span style="font-size: 1.4rem; font-weight: 800; color: #15803d;">₹5,600</span>
                <span style="font-size: 0.75rem; color: #64748b;">/ person</span>
              </div>
              <button class="btn btn-primary" onclick="Views.openPackageBookingModal('Complete Spiritual & Eco Wonder Circuit (3D/2N)')">Book Tour</button>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  openLodgeBookingModal(lodgeName) {
    const modal = document.getElementById('modal-container');
    modal.style.display = 'flex';
    modal.innerHTML = `
      <div class="modal-backdrop" onclick="if(event.target === this) AppAuth.closeModal()">
        <div class="modal-content" style="max-width: 520px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
              <span class="badge" style="background: #15803d; color: #fff;">TTDCL Reservation</span>
              <h3 class="font-serif" style="margin-top: 6px;">Book Your Stay</h3>
            </div>
            <button onclick="AppAuth.closeModal()" style="background:none; border:none; font-size: 1.5rem; cursor:pointer;">&times;</button>
          </div>

          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
            <div style="font-weight: 700; color: #0f172a;">🏨 ${lodgeName}</div>
            <div style="font-size: 0.8rem; color: #64748b;">Tripura Tourism Development Corporation Property</div>
          </div>

          <form onsubmit="Views.submitLodgeBooking(event, '${lodgeName}')">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
              <div>
                <label style="font-size: 0.75rem; font-weight: 700; color: #475569;">CHECK-IN DATE</label>
                <input type="date" id="book-checkin" required class="filter-select" style="width: 100%; margin-top: 4px;" value="${new Date().toISOString().split('T')[0]}">
              </div>
              <div>
                <label style="font-size: 0.75rem; font-weight: 700; color: #475569;">CHECK-OUT DATE</label>
                <input type="date" id="book-checkout" required class="filter-select" style="width: 100%; margin-top: 4px;" value="${new Date(Date.now() + 86400000 * 2).toISOString().split('T')[0]}">
              </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
              <div>
                <label style="font-size: 0.75rem; font-weight: 700; color: #475569;">ROOM TYPE</label>
                <select id="book-room-type" class="filter-select" style="width: 100%; margin-top: 4px;">
                  <option value="Standard AC">Standard AC Room</option>
                  <option value="Deluxe AC">Deluxe AC Room</option>
                  <option value="Executive Log Hut">Executive Log Hut</option>
                  <option value="Standard Non-AC">Standard Non-AC Room</option>
                </select>
              </div>
              <div>
                <label style="font-size: 0.75rem; font-weight: 700; color: #475569;">GUESTS</label>
                <select id="book-guests" class="filter-select" style="width: 100%; margin-top: 4px;">
                  <option value="1">1 Adult</option>
                  <option value="2" selected>2 Adults</option>
                  <option value="3">3 Adults (Extra Bed)</option>
                  <option value="4">Family (2 Adults + 2 Kids)</option>
                </select>
              </div>
            </div>

            <div style="margin-bottom: 14px;">
              <label style="font-size: 0.75rem; font-weight: 700; color: #475569;">FULL NAME</label>
              <input type="text" id="book-name" required placeholder="Enter primary guest name" class="filter-select" style="width: 100%; margin-top: 4px;" value="${AppState.currentUser ? AppState.currentUser.full_name : ''}">
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px;">
              <div>
                <label style="font-size: 0.75rem; font-weight: 700; color: #475569;">MOBILE NUMBER</label>
                <input type="tel" id="book-mobile" required placeholder="+91 9876543210" class="filter-select" style="width: 100%; margin-top: 4px;">
              </div>
              <div>
                <label style="font-size: 0.75rem; font-weight: 700; color: #475569;">EMAIL</label>
                <input type="email" id="book-email" required placeholder="guest@example.com" class="filter-select" style="width: 100%; margin-top: 4px;" value="${AppState.currentUser ? AppState.currentUser.email : ''}">
              </div>
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 12px;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="AppAuth.closeModal()">Cancel</button>
              <button type="submit" class="btn btn-primary btn-sm">Confirm Reservation ✓</button>
            </div>
          </form>
        </div>
      </div>
    `;
  },

  submitLodgeBooking(e, lodgeName) {
    e.preventDefault();
    const guest = document.getElementById('book-name').value;
    const checkin = document.getElementById('book-checkin').value;
    const checkout = document.getElementById('book-checkout').value;
    const room = document.getElementById('book-room-type').value;

    AppAuth.closeModal();
    Toast.show(`🎉 Reservation confirmed for ${guest} at ${lodgeName} (${room}) from ${checkin} to ${checkout}! Booking ID: TTDCL-${Math.floor(100000 + Math.random() * 900000)}`, 'success');
  },

  openPackageBookingModal(packageName) {
    const modal = document.getElementById('modal-container');
    modal.style.display = 'flex';
    modal.innerHTML = `
      <div class="modal-backdrop" onclick="if(event.target === this) AppAuth.closeModal()">
        <div class="modal-content" style="max-width: 500px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div>
              <span class="badge" style="background: #b45309; color: #fff;">Package Tour</span>
              <h3 class="font-serif" style="margin-top: 6px;">Book Guided Tour</h3>
            </div>
            <button onclick="AppAuth.closeModal()" style="background:none; border:none; font-size: 1.5rem; cursor:pointer;">&times;</button>
          </div>

          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
            <div style="font-weight: 700; color: #0f172a;">🎒 ${packageName}</div>
            <div style="font-size: 0.8rem; color: #64748b;">Includes AC Transport, Guide, Entry Fees, and TTDCL Lodge</div>
          </div>

          <form onsubmit="Views.submitPackageBooking(event, '${packageName}')">
            <div style="margin-bottom: 14px;">
              <label style="font-size: 0.75rem; font-weight: 700; color: #475569;">TOUR START DATE</label>
              <input type="date" id="pkg-date" required class="filter-select" style="width: 100%; margin-top: 4px;" value="${new Date(Date.now() + 86400000 * 3).toISOString().split('T')[0]}">
            </div>

            <div style="margin-bottom: 14px;">
              <label style="font-size: 0.75rem; font-weight: 700; color: #475569;">NUMBER OF TRAVELERS</label>
              <select id="pkg-travelers" class="filter-select" style="width: 100%; margin-top: 4px;">
                <option value="1">1 Person</option>
                <option value="2" selected>2 Persons</option>
                <option value="3">3 Persons</option>
                <option value="4">4 Persons</option>
                <option value="5+">Group (5+ Persons)</option>
              </select>
            </div>

            <div style="margin-bottom: 14px;">
              <label style="font-size: 0.75rem; font-weight: 700; color: #475569;">LEAD TRAVELER NAME</label>
              <input type="text" id="pkg-name" required placeholder="Enter full name" class="filter-select" style="width: 100%; margin-top: 4px;" value="${AppState.currentUser ? AppState.currentUser.full_name : ''}">
            </div>

            <div style="margin-bottom: 20px;">
              <label style="font-size: 0.75rem; font-weight: 700; color: #475569;">CONTACT NUMBER</label>
              <input type="tel" id="pkg-phone" required placeholder="+91 9876543210" class="filter-select" style="width: 100%; margin-top: 4px;">
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 12px;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="AppAuth.closeModal()">Cancel</button>
              <button type="submit" class="btn btn-primary btn-sm">Confirm Package Booking ✓</button>
            </div>
          </form>
        </div>
      </div>
    `;
  },

  submitPackageBooking(e, packageName) {
    e.preventDefault();
    const name = document.getElementById('pkg-name').value;
    const date = document.getElementById('pkg-date').value;
    const travelers = document.getElementById('pkg-travelers').value;

    AppAuth.closeModal();
    Toast.show(`🎉 Tour booking confirmed for ${name} (${travelers} travelers) on ${date}! Booking ID: PKG-${Math.floor(100000 + Math.random() * 900000)}`, 'success');
  },

  renderDestinationCardHTML(d) {
    const eriTier = d.eri_tier || { tier: 'High Sustainable', badge_class: 'badge-sustainable' };
    return `
      <div class="destination-card" onclick="AppRouter.navigate('destination-detail', '${d.slug}')">
        <div class="dest-card-image-wrap">
          <img src="${d.image_url}" alt="${d.name}" loading="lazy">
          <div class="dest-floating-badges">
            <span class="badge ${eriTier.badge_class}">${d.eco_responsibility_index} ERI</span>
            ${d.is_lesser_known ? '<span class="badge badge-balanced">Hidden Gem</span>' : ''}
          </div>
        </div>
        <div class="dest-card-body">
          <div class="dest-card-meta">
            <span>📍 ${d.district_name}</span>
            <span>•</span>
            <span>${d.destination_type.replace('_', ' ')}</span>
          </div>
          <h3 class="dest-card-title">${d.name}</h3>
          <p class="dest-card-description">${d.short_description}</p>
          <div class="dest-card-footer">
            <span>⭐ ${d.average_rating ? d.average_rating.toFixed(1) : '5.0'} (${d.total_reviews} reviews)</span>
            <span>⏱️ ${d.recommended_duration_hours} hrs</span>
          </div>
        </div>
      </div>
    `;
  },

  // 2. DESTINATION DISCOVERY (Faceted Filter + Grid)
  async renderDestinations(container, presetParam = null) {
    let presetType = 'all';
    let presetLesser = null;
    if (presetParam) {
      if (presetParam.startsWith('type:')) presetType = presetParam.replace('type:', '');
      if (presetParam.startsWith('lesser:')) presetLesser = 1;
    }

    const [destRes, distRes] = await Promise.all([
      API.get('/api/v1/destinations?limit=50'),
      API.get('/api/v1/districts')
    ]);

    const districts = distRes.data;
    AppState.allDestinations = destRes.data;

    container.innerHTML = `
      <div style="margin-bottom: 32px;">
        <h1 class="font-serif" style="font-size: 2.5rem; margin-bottom: 8px;">Explore Tripura Destinations</h1>
        <p class="text-muted">Faceted multi-criteria discovery across all 8 districts, sorted by ecological responsibility and user satisfaction.</p>
      </div>

      <!-- Filter Controls Toolbar -->
      <div class="filter-toolbar">
        <div class="filter-group">
          <label>District</label>
          <select id="filter-district" class="filter-select" onchange="Views.applyDestinationFilters()">
            <option value="all">All Districts (8)</option>
            ${districts.map(d => `<option value="${d.name}">${d.name}</option>`).join('')}
          </select>
        </div>

        <div class="filter-group">
          <label>Category</label>
          <select id="filter-type" class="filter-select" onchange="Views.applyDestinationFilters()">
            <option value="all">All Categories</option>
            <option value="eco_sanctuary" ${presetType === 'eco_sanctuary' ? 'selected' : ''}>Eco Sanctuary</option>
            <option value="rock_carving" ${presetType === 'rock_carving' ? 'selected' : ''}>Rock Carvings</option>
            <option value="royal_palace">Royal Palace</option>
            <option value="lake_wetland">Lake & Wetlands</option>
            <option value="hill_station" ${presetType === 'hill_station' ? 'selected' : ''}>Hill Station / Ridge</option>
            <option value="cultural_heritage">Cultural Heritage</option>
            <option value="temple_complex">Temple Complex</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Min Eco Index (ERI)</label>
          <select id="filter-eco" class="filter-select" onchange="Views.applyDestinationFilters()">
            <option value="0">Any Score</option>
            <option value="80">80+ (High Certified)</option>
            <option value="90">90+ (Pristine Sanctuary)</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Crowd Density</label>
          <select id="filter-crowd" class="filter-select" onchange="Views.applyDestinationFilters()">
            <option value="all">Any Crowd Level</option>
            <option value="Very Low">Very Low / Solitude</option>
            <option value="Low">Low</option>
            <option value="Moderate">Moderate</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Search Keyword</label>
          <input type="text" id="filter-search" class="filter-input" placeholder="Search name or lore..." oninput="Views.applyDestinationFilters()">
        </div>
      </div>

      <!-- Results Count Bar -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
        <div id="dest-count-label" style="font-size: 0.9rem; font-weight: 600; color: var(--charcoal-700);">
          Showing ${destRes.data.length} verified destinations
        </div>
        <button class="btn btn-secondary btn-sm" onclick="AppRouter.navigate('map')">🗺️ Open Split GIS Map</button>
      </div>

      <!-- Destination Grid -->
      <div class="destinations-grid" id="destinations-results-grid">
        ${destRes.data.map(d => Views.renderDestinationCardHTML(d)).join('')}
      </div>
    `;

    if (presetType !== 'all' || presetLesser !== null) {
      this.applyDestinationFilters();
    }
  },

  async applyDestinationFilters() {
    const district = document.getElementById('filter-district')?.value || 'all';
    const type = document.getElementById('filter-type')?.value || 'all';
    const minEco = document.getElementById('filter-eco')?.value || '0';
    const crowd = document.getElementById('filter-crowd')?.value || 'all';
    const search = document.getElementById('filter-search')?.value.trim() || '';

    let url = `/api/v1/destinations?district=${encodeURIComponent(district)}&destination_type=${encodeURIComponent(type)}&min_eco_score=${minEco}&crowd_level=${encodeURIComponent(crowd)}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    const res = await API.get(url);
    const grid = document.getElementById('destinations-results-grid');
    const label = document.getElementById('dest-count-label');

    if (label) label.innerText = `Showing ${res.data.length} destinations matching criteria`;

    if (res.data.length === 0) {
      grid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 64px 20px; background: #fff; border-radius: var(--radius-lg); border: 1px solid var(--border-subtle);">
          <div style="font-size: 2.5rem; margin-bottom: 12px;">🔍</div>
          <h3 class="font-serif">No destinations match all selected filters</h3>
          <p class="text-muted" style="margin: 8px 0 20px;">Try lowering the minimum Eco Index or expanding your district search radius.</p>
          <button class="btn btn-secondary btn-sm" onclick="Views.resetFilters()">Reset All Filters</button>
        </div>
      `;
    } else {
      grid.innerHTML = res.data.map(d => Views.renderDestinationCardHTML(d)).join('');
    }
  },

  resetFilters() {
    document.getElementById('filter-district').value = 'all';
    document.getElementById('filter-type').value = 'all';
    document.getElementById('filter-eco').value = '0';
    document.getElementById('filter-crowd').value = 'all';
    document.getElementById('filter-search').value = '';
    this.applyDestinationFilters();
  },

  // 3. SMART DESTINATION DETAIL PAGE (14-Section Information Architecture)
  async renderDestinationDetail(container, slugOrId) {
    const res = await API.get(`/api/v1/destinations/${slugOrId}`);
    const data = res.data;
    const p = data.profile;
    const eco = data.eco_details;
    const cult = data.cultural_details;
    const sust = data.sustainability;
    const exp = data.experiences;
    const reviews = data.reviews;
    const nearby = data.nearby_destinations;
    const isSaved = data.is_saved;

    container.innerHTML = `
      <div class="dest-profile-container">
        <!-- Section 1: Hero Banner -->
        <div class="dest-hero-banner">
          <img src="${p.image_url}" alt="${p.name}">
          <div class="dest-hero-gradient">
            <div style="display: flex; gap: 8px; margin-bottom: 8px;">
              <span class="badge badge-pristine">${p.eco_responsibility_index} ERI</span>
              <span class="badge badge-category">${p.destination_type.replace('_', ' ')}</span>
              ${p.is_lesser_known ? '<span class="badge badge-balanced">Hidden Gem</span>' : ''}
            </div>
            <h1 class="dest-hero-title">${p.name}</h1>
            <p class="dest-hero-tagline">${p.tagline || p.short_description}</p>
          </div>
        </div>

        <!-- Section 2: Action Toolbar -->
        <div style="display: flex; justify-content: space-between; align-items: center; background: #fff; padding: 16px 24px; border-radius: var(--radius-lg); border: 1px solid var(--border-subtle);">
          <div style="display: flex; gap: 24px; font-size: 0.88rem;">
            <span><strong>District:</strong> ${p.district_name}</span>
            <span><strong>Season:</strong> ${p.best_season}</span>
            <span><strong>Duration:</strong> ${p.recommended_duration_hours} Hours</span>
            <span><strong>Difficulty:</strong> ${p.difficulty_level}</span>
          </div>
          <div style="display: flex; gap: 12px;">
            <button class="btn ${isSaved ? 'btn-terracotta' : 'btn-secondary'} btn-sm" onclick="Views.toggleSaveDestination(${p.destination_id})">
              ${isSaved ? '★ Saved to Profile' : '☆ Save Destination'}
            </button>
            <button class="btn btn-primary btn-sm" onclick="Views.openReviewModal(${p.destination_id})">✍️ Write Review</button>
          </div>
        </div>

        <!-- Layout Grid: Main Content (Left) & Sidebar Facts (Right) -->
        <div class="profile-layout-grid">
          <div class="profile-main-content">
            <!-- Section 3: Overview -->
            <div class="info-card">
              <h3 class="info-card-title">Destination Overview</h3>
              <p style="font-size: 1.05rem; line-height: 1.8; color: var(--charcoal-800);">${p.full_description}</p>
            </div>

            <!-- Section 4: Ecological Significance -->
            ${eco ? `
              <div class="info-card">
                <h3 class="info-card-title">🌿 Ecological Significance & Habitat</h3>
                <p style="margin-bottom: 16px;">${eco.biodiversity_significance}</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 0.9rem; background: var(--sand-bg); padding: 16px; border-radius: var(--radius-md);">
                  <div><strong>Key Flora:</strong> ${eco.key_flora || 'Subtropical species'}</div>
                  <div><strong>Key Fauna:</strong> ${eco.key_fauna || 'Avifauna & endemic primates'}</div>
                  <div><strong>Daily Carrying Capacity:</strong> ${eco.carrying_capacity_per_day} visitors/day</div>
                  <div><strong>Trail Distance:</strong> ${eco.trail_length_km} km</div>
                </div>
              </div>
            ` : ''}

            <!-- Section 5: Cultural & Historical Significance -->
            ${cult ? `
              <div class="info-card">
                <h3 class="info-card-title">🏛️ Cultural & Historical Heritage</h3>
                <p style="margin-bottom: 16px;">${cult.cultural_significance}</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 0.9rem; background: var(--sand-bg); padding: 16px; border-radius: var(--radius-md);">
                  <div><strong>Historical Epoch:</strong> ${cult.historical_epoch}</div>
                  <div><strong>Architectural Style:</strong> ${cult.architectural_style || 'Indigenous traditional'}</div>
                  <div><strong>Living Folklore:</strong> ${cult.rituals_and_folklore || 'Tribal prayers & seasonal rites'}</div>
                  <div><strong>Preservation Body:</strong> ${cult.preservation_agency}</div>
                </div>
              </div>
            ` : ''}

            <!-- Section 6: Local Community-Led Experiences -->
            ${exp.length > 0 ? `
              <div class="info-card">
                <h3 class="info-card-title">✨ Community-Led Tourism Experiences</h3>
                <div style="display: flex; flex-direction: column; gap: 16px;">
                  ${exp.map(x => `
                    <div style="border: 1px solid var(--border-subtle); padding: 16px; border-radius: var(--radius-md); background: var(--surface-subtle); display: flex; justify-content: space-between; align-items: center;">
                      <div>
                        <h4 style="color: var(--pine-900);">${x.title}</h4>
                        <p style="font-size: 0.88rem; color: var(--charcoal-600); margin: 4px 0 8px;">${x.description}</p>
                        <div style="font-size: 0.8rem; color: var(--terracotta-600); font-weight: 600;">
                          Beneficiary: ${x.community_beneficiary} • Footprint: ${x.eco_footprint_rating}
                        </div>
                      </div>
                      <div style="text-align: right; min-width: 120px;">
                        <div style="font-size: 1.25rem; font-weight: 700; color: var(--pine-800);">₹${x.cost_inr}</div>
                        <div style="font-size: 0.75rem; color: var(--charcoal-400);">${x.duration_minutes} Mins</div>
                      </div>
                    </div>
                  `).join('')}
                </div>
              </div>
            ` : ''}

            <!-- Section 7: Verified Reviews -->
            <div class="info-card">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 class="info-card-title" style="margin-bottom: 0; border-bottom: none;">
                  Tourist Reviews (${reviews.length})
                </h3>
                <span style="font-size: 1.15rem; font-weight: 700; color: var(--pine-800);">
                  ⭐ ${p.average_rating ? p.average_rating.toFixed(1) : '5.0'} / 5.0
                </span>
              </div>

              ${reviews.length === 0 ? '<p class="text-muted">No reviews recorded yet. Be the first visitor to share your eco-cultural experience!</p>' : `
                <div style="display: flex; flex-direction: column; gap: 16px;">
                  ${reviews.map(r => `
                    <div style="border-bottom: 1px solid var(--sand-darker); padding-bottom: 16px;">
                      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <strong>${r.author_name} (${r.author_country})</strong>
                        <span style="color: var(--ochre-600); font-weight: 700;">★ ${r.overall_rating.toFixed(1)}</span>
                      </div>
                      <div style="font-size: 0.78rem; color: var(--charcoal-400); margin-bottom: 8px;">Visited ${r.visit_month_year}</div>
                      <h4 style="font-size: 0.95rem; margin-bottom: 4px;">${r.review_title || ''}</h4>
                      <p style="font-size: 0.88rem; color: var(--charcoal-700);">${r.review_text}</p>
                    </div>
                  `).join('')}
                </div>
              `}
            </div>
          </div>

          <!-- Right Sidebar: Facts & Eco Responsibility Indicators -->
          <div class="profile-sidebar">
            <!-- Quick Facts Card -->
            <div class="info-card">
              <h3 class="info-card-title">Quick Facts</h3>
              <div class="fact-row">
                <span class="fact-label">District</span>
                <span class="fact-value">${p.district_name}</span>
              </div>
              <div class="fact-row">
                <span class="fact-label">Altitude</span>
                <span class="fact-value">${p.altitude_meters}m</span>
              </div>
              <div class="fact-row">
                <span class="fact-label">Coordinates</span>
                <span class="fact-value">${p.latitude.toFixed(3)}° N, ${p.longitude.toFixed(3)}° E</span>
              </div>
              <div class="fact-row">
                <span class="fact-label">Accessibility</span>
                <span class="fact-value">${p.accessibility_level} Access</span>
              </div>
              <div class="fact-row">
                <span class="fact-label">Crowd Density</span>
                <span class="fact-value">${p.crowd_density_level}</span>
              </div>
              <div class="fact-row">
                <span class="fact-label">Entry Fee</span>
                <span class="fact-value">${p.entry_fee_inr > 0 ? `₹${p.entry_fee_inr}` : 'Free'}</span>
              </div>
            </div>

            <!-- Eco Responsibility Index Diagnostic Breakdown -->
            <div class="info-card">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 class="info-card-title" style="margin-bottom: 0; border: none;">Eco Index: ${sust.eri_score}</h3>
                <span class="badge ${sust.tier_info.badge_class}">${sust.tier_info.tier.split(':')[0]}</span>
              </div>
              <p style="font-size: 0.8rem; color: var(--charcoal-500); margin-bottom: 16px;">
                ${sust.tier_info.description}
              </p>

              <!-- Indicators Bars -->
              <div>
                ${Object.entries(sust.indicators).map(([k, v]) => `
                  <div class="indicator-bar-item">
                    <div class="indicator-header">
                      <span>${v.label}</span>
                      <strong>${v.score}</strong>
                    </div>
                    <div class="progress-track">
                      <div class="progress-fill" style="width: ${v.score}%"></div>
                    </div>
                  </div>
                `).join('')}
              </div>

              <div style="margin-top: 16px; font-size: 0.75rem; color: var(--charcoal-400); border-top: 1px solid var(--border-subtle); padding-top: 8px;">
                Data Category: <span class="badge badge-category">${sust.data_source_type}</span>
              </div>
            </div>

            <!-- Responsible Travel Etiquette -->
            <div class="info-card" style="background-color: var(--pine-50); border-color: var(--pine-100);">
              <h3 class="info-card-title" style="color: var(--pine-800);">🌿 Visitor Guidelines</h3>
              <ul style="font-size: 0.85rem; color: var(--charcoal-700); padding-left: 18px; line-height: 1.6;">
                <li>Strict zero-single-use-plastic policy in force.</li>
                <li>Respect indigenous tribal traditions and obtain consent before photography.</li>
                <li>Stay on designated trails to prevent ravine soil erosion.</li>
                <li>Use quiet observation to protect nesting avifauna.</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  async toggleSaveDestination(destId) {
    if (!AppState.currentUser) {
      AppAuth.openLoginModal();
      return;
    }
    try {
      const res = await API.post(`/api/v1/destinations/${destId}/toggle-save`, {});
      Toast.show(res.message);
      AppState.savedPlacesCount += (res.is_saved ? 1 : -1);
      AppAuth.updateNav();
      AppRouter.refresh();
    } catch (e) {
      Toast.show(e.message, 'error');
    }
  },

  openReviewModal(destId) {
    if (!AppState.currentUser) {
      AppAuth.openLoginModal();
      return;
    }
    const modal = document.getElementById('modal-container');
    modal.style.display = 'flex';
    modal.innerHTML = `
      <div class="modal-backdrop" onclick="if(event.target === this) AppAuth.closeModal()">
        <div class="modal-content">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3 class="font-serif">Submit Verified Review</h3>
            <button onclick="AppAuth.closeModal()" style="background:none; border:none; font-size: 1.5rem; cursor:pointer;">&times;</button>
          </div>
          <form onsubmit="Views.submitReview(event, ${destId})">
            <div style="margin-bottom: 16px;">
              <label style="display:block; font-size: 0.8rem; font-weight: 700; margin-bottom: 6px;">Overall Rating (1.0 to 5.0)</label>
              <select id="review-rating" class="filter-select" style="width: 100%;">
                <option value="5.0">5.0 — Exceptional & Pristine</option>
                <option value="4.5">4.5 — Very Good</option>
                <option value="4.0">4.0 — Good</option>
                <option value="3.0">3.0 — Average</option>
              </select>
            </div>
            <div style="margin-bottom: 16px;">
              <label style="display:block; font-size: 0.8rem; font-weight: 700; margin-bottom: 6px;">Review Title</label>
              <input type="text" id="review-title" required class="filter-input" style="width: 100%;" placeholder="e.g. Breathtaking dawn view with zero crowds">
            </div>
            <div style="margin-bottom: 24px;">
              <label style="display:block; font-size: 0.8rem; font-weight: 700; margin-bottom: 6px;">Detailed Feedback</label>
              <textarea id="review-text" rows="4" required class="filter-input" style="width: 100%;" placeholder="Describe the ecological cleanliness, guide respect, and cultural atmosphere..."></textarea>
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%;">Post Review to Database</button>
          </form>
        </div>
      </div>
    `;
  },

  async submitReview(event, destId) {
    event.preventDefault();
    const overall = parseFloat(document.getElementById('review-rating').value);
    const title = document.getElementById('review-title').value;
    const text = document.getElementById('review-text').value;

    try {
      await API.post(`/api/v1/destinations/${destId}/reviews`, {
        overall_rating: overall,
        cleanliness_rating: overall,
        eco_practice_rating: overall,
        community_respect_rating: overall,
        review_title: title,
        review_text: text,
        visit_month_year: 'September 2026'
      });
      AppAuth.closeModal();
      Toast.show('Review submitted! Database trigger recalculated ratings.');
      AppRouter.refresh();
    } catch (e) {
      Toast.show(e.message, 'error');
    }
  },

  // 4. INTERACTIVE GIS MAP (Leaflet Integration)
  async renderGISMap(container) {
    container.innerHTML = `
      <div style="margin-bottom: 24px;">
        <h1 class="font-serif" style="font-size: 2.5rem; margin-bottom: 8px;">Interactive Tripura GIS Map</h1>
        <p class="text-muted">Geographic exploration across Tripura's 8 administrative districts with layered ecological and cultural point-of-interest markers.</p>
      </div>

      <div style="display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap;">
        <button class="btn btn-secondary btn-sm" onclick="Views.filterMapPins('all')">All Sites</button>
        <button class="btn btn-secondary btn-sm" onclick="Views.filterMapPins('eco_sanctuary')">🌿 Eco Sanctuaries</button>
        <button class="btn btn-secondary btn-sm" onclick="Views.filterMapPins('rock_carving')">🏛️ Rock Art</button>
        <button class="btn btn-secondary btn-sm" onclick="Views.filterMapPins('royal_palace')">👑 Palaces</button>
        <button class="btn btn-secondary btn-sm" onclick="Views.filterMapPins('hill_station')">⛰️ Ridge Points</button>
        <button class="btn btn-secondary btn-sm" onclick="Views.filterMapPins('lake_wetland')">🛶 Wetlands</button>
      </div>

      <div id="leaflet-map-view"></div>
    `;

    // Fetch destinations
    const res = await API.get('/api/v1/destinations?limit=50');
    AppState.allDestinations = res.data;

    setTimeout(() => {
      if (AppState.leafletMapInstance) {
        AppState.leafletMapInstance.remove();
      }
      // Centered on Tripura (23.83, 91.5)
      const map = L.map('leaflet-map-view').setView([23.83, 91.6], 9);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '© OpenStreetMap contributors | Tripura Terra GIS'
      }).addTo(map);

      AppState.leafletMapInstance = map;
      AppState.mapMarkers = [];

      Views.plotMapMarkers(res.data);
    }, 100);
  },

  plotMapMarkers(destinations) {
    if (!AppState.leafletMapInstance) return;
    if (AppState.mapMarkers) {
      AppState.mapMarkers.forEach(m => m.remove());
    }
    AppState.mapMarkers = [];

    destinations.forEach(d => {
      const marker = L.marker([d.latitude, d.longitude]).addTo(AppState.leafletMapInstance);
      marker.bindPopup(`
        <div style="font-family: var(--font-sans); min-width: 200px;">
          <h4 style="margin-bottom: 4px; color: #1b4332;">${d.name}</h4>
          <div style="font-size: 0.75rem; text-transform: uppercase; color: #c25e2e; font-weight: bold; margin-bottom: 6px;">${d.district_name} • ${d.destination_type.replace('_', ' ')}</div>
          <div style="font-size: 0.8rem; margin-bottom: 8px;">ERI Score: <strong>${d.eco_responsibility_index}</strong> / 100</div>
          <button class="btn btn-primary btn-sm" style="width: 100%; font-size: 0.75rem;" onclick="AppRouter.navigate('destination-detail', '${d.slug}')">View Profile</button>
        </div>
      `);
      marker.dest_type = d.destination_type;
      AppState.mapMarkers.push(marker);
    });
  },

  filterMapPins(category) {
    if (!AppState.mapMarkers) return;
    AppState.mapMarkers.forEach(m => {
      if (category === 'all' || m.dest_type === category) {
        m.addTo(AppState.leafletMapInstance);
      } else {
        m.remove();
      }
    });
  },

  // 5. SMART TRIP PLANNER ("Build My Journey")
  async renderPlanner(container) {
    const distRes = await API.get('/api/v1/districts');
    const districts = distRes.data;

    container.innerHTML = `
      <div style="margin-bottom: 32px;">
        <h1 class="font-serif" style="font-size: 2.5rem; margin-bottom: 8px;">Build My Sustainable Journey</h1>
        <p class="text-muted">Personalized multi-day itinerary synthesis driven by constraint optimization, carrying-capacity balancing, and explainability.</p>
      </div>

      <div class="planner-card">
        <form onsubmit="Views.executePlanGeneration(event)">
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 24px; margin-bottom: 32px;">
            <div>
              <label style="display:block; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Trip Duration (Days)</label>
              <select id="plan-days" class="filter-select" style="width: 100%;">
                <option value="2">2 Days (Weekend Circuit)</option>
                <option value="3" selected>3 Days (Classic Eco-Cultural Circuit)</option>
                <option value="5">5 Days (Deep Tripura Expedition)</option>
                <option value="7">7 Days (Full State Comprehensive Tour)</option>
              </select>
            </div>

            <div>
              <label style="display:block; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Travel Style</label>
              <select id="plan-style" class="filter-select" style="width: 100%;">
                <option value="slow_travel">Slow & Immersive Travel</option>
                <option value="nature_retreat">Nature & Wildlife Retreat</option>
                <option value="cultural_immersion">Indigenous Cultural Immersion</option>
                <option value="adventure">High-Altitude Trekking</option>
                <option value="family_eco">Family-Friendly Eco Tour</option>
              </select>
            </div>

            <div>
              <label style="display:block; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Preferred District Focus</label>
              <select id="plan-district" class="filter-select" style="width: 100%;">
                <option value="all">Balanced (All Districts)</option>
                ${districts.map(d => `<option value="${d.name}">${d.name}</option>`).join('')}
              </select>
            </div>

            <div>
              <label style="display:block; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">Budget (INR)</label>
              <input type="number" id="plan-budget" class="filter-input" value="12000" min="2000" step="1000" style="width: 100%;">
            </div>
          </div>

          <!-- Affinity Priority Weights Sliders -->
          <div style="background: var(--sand-bg); padding: 20px; border-radius: var(--radius-lg); margin-bottom: 32px; border: 1px solid var(--border-subtle);">
            <h4 style="margin-bottom: 16px; color: var(--pine-900);">Personal Interest Weightings</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
              <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">
                  <span>🌿 Nature & Sanctuaries</span>
                  <span id="nature-val">70%</span>
                </div>
                <input type="range" id="plan-nature-weight" min="0" max="1" step="0.1" value="0.7" style="width: 100%; accent-color: var(--pine-700);" oninput="document.getElementById('nature-val').innerText = Math.round(this.value * 100) + '%'">
              </div>

              <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">
                  <span>🏛️ Heritage & Indigenous Crafts</span>
                  <span id="culture-val">70%</span>
                </div>
                <input type="range" id="plan-culture-weight" min="0" max="1" step="0.1" value="0.7" style="width: 100%; accent-color: var(--terracotta-600);" oninput="document.getElementById('culture-val').innerText = Math.round(this.value * 100) + '%'">
              </div>
            </div>
          </div>

          <button type="submit" class="btn btn-primary" style="width: 100%; padding: 14px; font-size: 1rem;">
            Generate Personalized Itinerary ✨
          </button>
        </form>

        <div id="planner-results-container" style="margin-top: 40px;"></div>
      </div>
    `;
  },

  async executePlanGeneration(event) {
    event.preventDefault();
    const days = parseInt(document.getElementById('plan-days').value);
    const style = document.getElementById('plan-style').value;
    const district = document.getElementById('plan-district').value;
    const budget = parseFloat(document.getElementById('plan-budget').value);
    const nat = parseFloat(document.getElementById('plan-nature-weight').value);
    const cult = parseFloat(document.getElementById('plan-culture-weight').value);

    const container = document.getElementById('planner-results-container');
    container.innerHTML = '<div style="text-align:center; padding: 32px;"><p class="text-muted">Synthesizing itinerary and running multi-criteria optimization...</p></div>';

    try {
      const res = await API.post('/api/v1/planner/generate', {
        days: days,
        budget: budget,
        travel_style: style,
        preferred_district: district,
        nature_weight: nat,
        culture_weight: cult
      });

      const itin = res.data;
      AppState.currentGeneratedItinerary = itin;

      // Render Schedule
      container.innerHTML = `
        <div style="border-top: 2px solid var(--pine-700); padding-top: 32px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
            <div>
              <span class="badge badge-pristine">${itin.eco_tier}</span>
              <h2 class="font-serif" style="margin: 8px 0;">${itin.title}</h2>
              <p class="text-muted" style="max-width: 750px;">${itin.explanation}</p>
            </div>
            <button class="btn btn-terracotta" onclick="Views.saveGeneratedItinerary()">💾 Save to My Trips</button>
          </div>

          <!-- Trip KPI Summary -->
          <div style="display: flex; gap: 20px; background: var(--sand-bg); padding: 16px 24px; border-radius: var(--radius-md); margin-bottom: 32px; border: 1px solid var(--border-subtle); flex-wrap: wrap;">
            <div><strong>Est. Total Cost:</strong> ₹${itin.estimated_budget_inr}</div>
            <div><strong>Total Transit Distance:</strong> ~${itin.estimated_distance_km} km</div>
            <div><strong>Average Eco Responsibility:</strong> ${itin.composite_eco_score} / 100</div>
          </div>

          <!-- Schedule By Day -->
          <div>
            ${itin.daily_schedule.map(slot => `
              <div class="itinerary-slot">
                <div>
                  <strong style="color: var(--terracotta-600);">Day ${slot.day_number}</strong>
                  <div style="font-size: 0.8rem; color: var(--charcoal-500);">${slot.time_slot}</div>
                </div>
                <div>
                  <h4 style="color: var(--pine-900); cursor: pointer;" onclick="AppRouter.navigate('destination-detail', ${slot.destination_id})">
                    ${slot.name}
                  </h4>
                  <p style="font-size: 0.85rem; color: var(--charcoal-700);">${slot.activity_note}</p>
                </div>
                <div style="text-align: right;">
                  <span class="badge badge-pristine">${slot.eco_responsibility_index} ERI</span>
                  <div style="font-size: 0.75rem; color: var(--charcoal-400); margin-top: 4px;">~${slot.transit_km} km transit</div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    } catch (e) {
      Toast.show(e.message, 'error');
    }
  },

  async saveGeneratedItinerary() {
    if (!AppState.currentUser) {
      AppAuth.openLoginModal();
      return;
    }
    const itin = AppState.currentGeneratedItinerary;
    if (!itin) return;

    try {
      await API.post('/api/v1/itineraries/save', {
        title: itin.title,
        total_days: itin.total_days,
        budget_inr: itin.estimated_budget_inr,
        travel_style: itin.travel_style,
        estimated_distance_km: itin.estimated_distance_km,
        composite_eco_score: itin.composite_eco_score,
        explanation_notes: itin.explanation,
        items: itin.daily_schedule
      });
      Toast.show('Itinerary saved to your personal dashboard!');
      AppRouter.navigate('dashboard');
    } catch (e) {
      Toast.show(e.message, 'error');
    }
  },

  // 6. ECO TRAILS & SANCTUARIES
  async renderEcoTrails(container) {
    const res = await API.get('/api/v1/eco/trails-sanctuaries');
    const trails = res.data;

    container.innerHTML = `
      <div style="margin-bottom: 32px;">
        <h1 class="font-serif" style="font-size: 2.5rem; margin-bottom: 8px;">Tripura Eco Trails & Sanctuaries</h1>
        <p class="text-muted">Dedicated ecological conservation biospheres, protected sal corridors, and montane ridge walks.</p>
      </div>

      <div class="destinations-grid">
        ${trails.map(t => `
          <div class="destination-card" onclick="AppRouter.navigate('destination-detail', '${t.slug}')">
            <div class="dest-card-image-wrap">
              <img src="${t.image_url}" alt="${t.name}">
              <div class="dest-floating-badges">
                <span class="badge badge-pristine">${t.eco_responsibility_index} ERI</span>
                <span class="badge badge-category">${t.difficulty_level} Trek</span>
              </div>
            </div>
            <div class="dest-card-body">
              <div class="dest-card-meta">
                <span>📍 ${t.district_name}</span>
                <span>•</span>
                <span>Cap: ${t.carrying_capacity_per_day}/day</span>
              </div>
              <h3 class="dest-card-title">${t.name}</h3>
              <p class="dest-card-description">${t.biodiversity_significance}</p>
              <div class="dest-card-footer">
                <span>🦜 ${t.best_birdwatching_time || 'Morning'}</span>
                <span>🥾 ${t.trail_length_km} km</span>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  },

  // 7. CULTURAL HERITAGE MODULE
  async renderCulture(container) {
    const [commRes, cultRes, eventsRes] = await Promise.all([
      API.get('/api/v1/culture/communities'),
      API.get('/api/v1/culture/sites'),
      API.get('/api/v1/events')
    ]);

    const communities = commRes.data;
    const sites = cultRes.data;
    const events = eventsRes.data;

    container.innerHTML = `
      <div style="margin-bottom: 40px;">
        <h1 class="font-serif" style="font-size: 2.5rem; margin-bottom: 8px;">Indigenous Culture & Heritage</h1>
        <p class="text-muted">Honoring Tripura's 19 indigenous tribes, traditional back-strap loom Risa weaving, and sacred seasonal festivals.</p>
      </div>

      <!-- Indigenous Communities Section -->
      <section style="margin-bottom: 56px;">
        <h2 class="section-title" style="margin-bottom: 24px;">Indigenous Communities of Tripura</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px;">
          ${communities.map(c => `
            <div class="info-card">
              <span class="badge badge-category" style="margin-bottom: 8px;">${c.primary_language} Language</span>
              <h3 style="color: var(--pine-900); font-size: 1.35rem; margin-bottom: 8px;">${c.name}</h3>
              <p style="font-size: 0.88rem; color: var(--charcoal-700); margin-bottom: 12px;">${c.cultural_hallmark}</p>
              <div style="font-size: 0.82rem; background: var(--sand-bg); padding: 12px; border-radius: var(--radius-md); margin-bottom: 12px;">
                <strong>Crafts:</strong> ${c.crafts_heritage}<br>
                <strong>Dances:</strong> ${c.dance_forms}
              </div>
              <div style="font-size: 0.78rem; color: var(--terracotta-700); font-weight: 600;">
                Code of Respect: ${c.respectful_engagement_code}
              </div>
            </div>
          `).join('')}
        </div>
      </section>

      <!-- Sacred Festivals Section -->
      <section style="margin-bottom: 56px;">
        <h2 class="section-title" style="margin-bottom: 24px;">Sacred Festivals & Seasonal Celebrations</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px;">
          ${events.map(e => `
            <div class="destination-card" style="cursor: default;">
              <div class="dest-card-image-wrap" style="aspect-ratio: 16/9;">
                <img src="${e.image_url}" alt="${e.name}">
                <div class="dest-floating-badges">
                  <span class="badge badge-balanced">${e.category}</span>
                </div>
              </div>
              <div class="dest-card-body">
                <div class="dest-card-meta">📍 ${e.district_name} • ${e.start_date}</div>
                <h3 class="dest-card-title">${e.name}</h3>
                <p class="dest-card-description">${e.significance}</p>
                <div style="font-size: 0.8rem; color: var(--pine-800); background: var(--pine-50); padding: 8px; border-radius: var(--radius-sm);">
                  <strong>Etiquette:</strong> ${e.guidelines_for_tourists}
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </section>
    `;
  },

  // 8. DATABASE ANALYTICS DASHBOARD
  async renderAnalytics(container) {
    const [overviewRes, rollupRes, catRes, matrixRes] = await Promise.all([
      API.get('/api/v1/analytics/overview'),
      API.get('/api/v1/analytics/district-rollup'),
      API.get('/api/v1/analytics/category-distribution'),
      API.get('/api/v1/analytics/sustainability-pressure-matrix')
    ]);

    const stats = overviewRes.data;
    const districts = rollupRes.data;
    const categories = catRes.data;

    container.innerHTML = `
      <div style="margin-bottom: 32px;">
        <h1 class="font-serif" style="font-size: 2.5rem; margin-bottom: 8px;">Tourism Analytics & Database Intelligence</h1>
        <p class="text-muted">Real-time analytical metrics aggregated from normalized relational database views.</p>
      </div>

      <!-- KPI Summary Cards -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px;">
        <div class="info-card" style="text-align: center;">
          <div style="font-size: 2.2rem; font-weight: 700; color: var(--pine-800);">${stats.total_destinations}</div>
          <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--charcoal-500); font-weight: 600;">Total Destinations</div>
        </div>
        <div class="info-card" style="text-align: center;">
          <div style="font-size: 2.2rem; font-weight: 700; color: var(--pine-800);">${stats.state_average_eco_index}</div>
          <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--charcoal-500); font-weight: 600;">State Avg ERI Index</div>
        </div>
        <div class="info-card" style="text-align: center;">
          <div style="font-size: 2.2rem; font-weight: 700; color: var(--terracotta-600);">${stats.lesser_known_destinations}</div>
          <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--charcoal-500); font-weight: 600;">Lesser-Known Sites</div>
        </div>
        <div class="info-card" style="text-align: center;">
          <div style="font-size: 2.2rem; font-weight: 700; color: var(--pine-800);">${stats.total_reviews}</div>
          <div style="font-size: 0.8rem; text-transform: uppercase; color: var(--charcoal-500); font-weight: 600;">Verified Reviews</div>
        </div>
      </div>

      <!-- Charts Grid -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-bottom: 40px;">
        <div class="info-card">
          <h3 class="info-card-title">District Tourism Distribution</h3>
          <canvas id="chart-district-dist" height="220"></canvas>
        </div>
        <div class="info-card">
          <h3 class="info-card-title">Tourism Categories Breakdown</h3>
          <canvas id="chart-category-dist" height="220"></canvas>
        </div>
      </div>

      <!-- Database Views Demonstration Table (vw_district_analytics) -->
      <div class="info-card">
        <h3 class="info-card-title">Relational View Data: <code>vw_district_analytics</code></h3>
        <p class="text-muted" style="font-size: 0.85rem; margin-bottom: 16px;">
          Direct execution of SQL view combining district metadata, aggregate destination counts, and mean Eco Responsibility Indexes.
        </p>
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; font-size: 0.88rem; text-align: left;">
            <thead>
              <tr style="border-bottom: 2px solid var(--border-medium); background: var(--sand-bg);">
                <th style="padding: 10px;">District</th>
                <th style="padding: 10px;">Forest Cover</th>
                <th style="padding: 10px;">Total Sites</th>
                <th style="padding: 10px;">Eco Sites</th>
                <th style="padding: 10px;">Cultural Sites</th>
                <th style="padding: 10px;">Mean ERI Score</th>
              </tr>
            </thead>
            <tbody>
              ${districts.map(d => `
                <tr style="border-bottom: 1px solid var(--border-subtle);">
                  <td style="padding: 10px; font-weight: 600;">${d.district_name}</td>
                  <td style="padding: 10px;">${d.forest_cover_percent}%</td>
                  <td style="padding: 10px;">${d.total_destinations}</td>
                  <td style="padding: 10px;">${d.eco_destination_count}</td>
                  <td style="padding: 10px;">${d.cultural_destination_count}</td>
                  <td style="padding: 10px;"><span class="badge badge-pristine">${d.avg_eco_responsibility || 0}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    // Render Chart.js
    setTimeout(() => {
      new Chart(document.getElementById('chart-district-dist'), {
        type: 'bar',
        data: {
          labels: districts.map(d => d.district_name),
          datasets: [{
            label: 'Total Sites',
            data: districts.map(d => d.total_destinations),
            backgroundColor: '#1b4332'
          }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
      });

      new Chart(document.getElementById('chart-category-dist'), {
        type: 'doughnut',
        data: {
          labels: categories.map(c => c.destination_type.replace('_', ' ')),
          datasets: [{
            data: categories.map(c => c.count),
            backgroundColor: ['#1b4332', '#2d6a4f', '#c25e2e', '#df7341', '#d97706', '#52b788', '#b7e4c7']
          }]
        },
        options: { responsive: true }
      });
    }, 100);
  },

  // 9. RESEARCH & DBMS BENCHMARKING HARNESS
  async renderResearchBenchmarking(container) {
    container.innerHTML = `
      <div style="margin-bottom: 32px;">
        <h1 class="font-serif" style="font-size: 2.5rem; margin-bottom: 8px;">Scientific Evaluation & DBMS Benchmarks</h1>
        <p class="text-muted">Empirical experiment harnesses for scientific research publication, verifying database indexing speedup and recommendation relevance metrics.</p>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 40px;">
        <!-- Harness 1: DB Indexing Benchmark -->
        <div class="info-card">
          <h3 class="info-card-title">1. DBMS Query Optimization Harness</h3>
          <p style="font-size: 0.88rem; color: var(--charcoal-600); margin-bottom: 20px;">
            Executes controlled analytical queries comparing optimized indexed access vs unindexed full table scans using <code>EXPLAIN QUERY PLAN</code>.
          </p>
          <button class="btn btn-primary" id="btn-run-db-benchmark" onclick="Views.runDBBenchmark()">
            ⚡ Run Live Database Benchmark
          </button>
          <div id="db-benchmark-results" style="margin-top: 24px;"></div>
        </div>

        <!-- Harness 2: Recommendation Engine Evaluation -->
        <div class="info-card">
          <h3 class="info-card-title">2. Recommendation Algorithm Metrics</h3>
          <p style="font-size: 0.88rem; color: var(--charcoal-600); margin-bottom: 20px;">
            Evaluates Precision@K, Recall@K, Normalized Discounted Cumulative Gain (NDCG@5), and Intra-List Diversity across diverse synthetic tourist persona cohorts.
          </p>
          <button class="btn btn-terracotta" id="btn-run-recsys-benchmark" onclick="Views.runRecSysBenchmark()">
            🎯 Run RecSys Evaluation Harness
          </button>
          <div id="recsys-benchmark-results" style="margin-top: 24px;"></div>
        </div>
      </div>
    `;
  },

  async runDBBenchmark() {
    const btn = document.getElementById('btn-run-db-benchmark');
    const container = document.getElementById('db-benchmark-results');
    btn.innerText = 'Running Benchmark Queries...';
    btn.disabled = true;

    try {
      const res = await API.post('/api/v1/research/benchmark-db', {});
      const data = res.data;

      container.innerHTML = `
        <div style="background: var(--sand-bg); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);">
          <div style="font-size: 0.8rem; font-weight: 700; color: var(--pine-800); margin-bottom: 12px;">
            ✓ Benchmark Execution Logged (${data.benchmark_timestamp})
          </div>
          ${data.results.map(r => `
            <div style="border-bottom: 1px solid var(--border-subtle); padding: 8px 0; font-size: 0.85rem;">
              <div style="display: flex; justify-content: space-between; font-weight: 600;">
                <span>${r.id}: ${r.name}</span>
                <span style="color: var(--pine-700);">${r.speedup_factor} Faster</span>
              </div>
              <div style="font-size: 0.75rem; color: var(--charcoal-500); margin-top: 2px;">
                Indexed: <strong>${r.optimized_time_ms} ms</strong> | Unindexed: <strong>${r.unindexed_time_ms} ms</strong>
              </div>
            </div>
          `).join('')}
        </div>
      `;
      Toast.show('Database benchmark completed!');
    } catch (e) {
      Toast.show(e.message, 'error');
    } finally {
      btn.innerText = '⚡ Run Live Database Benchmark';
      btn.disabled = false;
    }
  },

  async runRecSysBenchmark() {
    const btn = document.getElementById('btn-run-recsys-benchmark');
    const container = document.getElementById('recsys-benchmark-results');
    btn.innerText = 'Computing Persona Metrics...';
    btn.disabled = true;

    try {
      const res = await API.post('/api/v1/research/evaluate-recommendations', {});
      const metrics = res.data.evaluation_metrics;
      const cohorts = res.data.cohort_breakdown;

      container.innerHTML = `
        <div style="background: var(--sand-bg); padding: 16px; border-radius: var(--radius-md); border: 1px solid var(--border-subtle);">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
            <div><strong>Mean Precision@5:</strong> ${(metrics.mean_precision_at_5 * 100).toFixed(1)}%</div>
            <div><strong>Mean NDCG@5:</strong> ${metrics.mean_ndcg_at_5}</div>
            <div><strong>Intra-List Diversity:</strong> ${metrics.mean_intra_list_diversity}</div>
            <div><strong>Mean Recall@5:</strong> ${(metrics.mean_recall_at_5 * 100).toFixed(1)}%</div>
          </div>
          <div style="font-size: 0.78rem; color: var(--charcoal-500); border-top: 1px solid var(--border-subtle); padding-top: 8px;">
            Evaluated 4 cohorts: Eco Explorer, Culture Historian, Backpacker, Family Leisure.
          </div>
        </div>
      `;
      Toast.show('Recommendation evaluation completed!');
    } catch (e) {
      Toast.show(e.message, 'error');
    } finally {
      btn.innerText = '🎯 Run RecSys Evaluation Harness';
      btn.disabled = false;
    }
  },

  // 10. USER DASHBOARD (Saved Places & Saved Trips)
  async renderDashboard(container) {
    if (!AppState.currentUser) {
      container.innerHTML = `
        <div style="text-align: center; padding: 64px 20px; background: #fff; border-radius: var(--radius-xl); border: 1px solid var(--border-subtle);">
          <h2 class="font-serif">Tourist Profile Sign-In</h2>
          <p class="text-muted" style="margin: 12px 0 24px;">Please sign in to view your saved places, created itineraries, and custom travel preferences.</p>
          <button class="btn btn-primary" onclick="AppAuth.openLoginModal()">Login to Tripura Terra</button>
        </div>
      `;
      return;
    }

    const [savedRes, tripsRes] = await Promise.all([
      API.get('/api/v1/users/saved-places'),
      API.get('/api/v1/itineraries/my-trips')
    ]);

    const saved = savedRes.data;
    const trips = tripsRes.data;

    container.innerHTML = `
      <div style="margin-bottom: 32px;">
        <h1 class="font-serif" style="font-size: 2.5rem; margin-bottom: 8px;">Traveler Dashboard</h1>
        <p class="text-muted">Welcome, ${AppState.currentUser.full_name} (${AppState.currentUser.role.toUpperCase()})</p>
      </div>

      <!-- Saved Places Section -->
      <section style="margin-bottom: 48px;">
        <h3 class="font-serif" style="font-size: 1.6rem; margin-bottom: 16px;">Saved Destinations (${saved.length})</h3>
        ${saved.length === 0 ? '<p class="text-muted">No destinations bookmarked yet.</p>' : `
          <div class="destinations-grid">
            ${saved.map(d => Views.renderDestinationCardHTML(d)).join('')}
          </div>
        `}
      </section>

      <!-- Saved Itineraries Section -->
      <section>
        <h3 class="font-serif" style="font-size: 1.6rem; margin-bottom: 16px;">My Generated Trips (${trips.length})</h3>
        ${trips.length === 0 ? '<p class="text-muted">No custom itineraries saved yet.</p>' : `
          <div>
            ${trips.map(t => `
              <div class="itinerary-day-card">
                <div class="day-header">
                  <span>${t.title} (${t.total_days} Days)</span>
                  <button class="btn btn-outline btn-sm" style="color: #991b1b; border-color: #fecaca;" onclick="Views.deleteTrip(${t.itinerary_id})">Delete Trip</button>
                </div>
                <p style="font-size: 0.88rem; color: var(--charcoal-600); margin-bottom: 16px;">${t.explanation_notes}</p>
                <div style="font-size: 0.82rem; color: var(--charcoal-500); margin-bottom: 12px;">
                  Budget: ₹${t.budget_inr} • Distance: ${t.estimated_distance_km} km • Eco Score: ${t.composite_eco_score}/100
                </div>
                <div>
                  ${t.items.map(item => `
                    <div class="itinerary-slot">
                      <div><strong>Day ${item.day_number}</strong> (${item.time_slot})</div>
                      <div><strong>${item.destination_name}</strong>: ${item.activity_note}</div>
                      <div>~${item.transit_km_from_prev} km</div>
                    </div>
                  `).join('')}
                </div>
              </div>
            `).join('')}
          </div>
        `}
      </section>
    `;
  },

  async deleteTrip(itinId) {
    if (!confirm('Are you sure you want to delete this itinerary?')) return;
    try {
      await API.delete(`/api/v1/itineraries/${itinId}`);
      Toast.show('Itinerary deleted.');
      AppRouter.refresh();
    } catch (e) {
      Toast.show(e.message, 'error');
    }
  }
};

// Initialize Application on Window Load
window.addEventListener('DOMContentLoaded', async () => {
  await AppAuth.init();
  window.addEventListener('hashchange', () => AppRouter.handleHashChange());
  AppRouter.handleHashChange();
});
