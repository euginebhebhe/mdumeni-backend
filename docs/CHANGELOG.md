# MDUMENI Changelog

All notable changes to MDUMENI are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — June 2026

### First production release

#### Mobile app
- Five-tab navigation: Home, Market, Plan, My Farm, More
- Complete farmer onboarding flow (6 steps: location, region, farm size, irrigation, budget, account)
- PIN-based authentication with expo-secure-store token persistence
- Demo mode and real project mode
- Province and district selection backed by live province index (10 provinces, 61 districts)

#### AI engines (on-device, fully offline)
- Crop recommendation engine: 60 crops, 6-factor weighted scoring across all 5 agro-ecological regions
- Farming calendar engine: 60 crops, phase-based daily task generation
- Planning engine: yield/cost/profit calculator with input-level variants
- Pest and disease engine: 36 pests, 38 diseases, symptom-based diagnosis

#### Dataset
- 60 crop records with full agronomic profiles, Zimbabwe-specific varieties, fertiliser schedules, and market data
- Indigenous/traditional crops added: Finger millet (Zviyo), Bambara groundnut (Nyimo), Okra (Derere), Covo, Amaranth (Mowa), Pigeon peas, Lablab, Moringa
- High-value export crops added: Coffee (Arabica), Tea, Macadamia, Green beans, Passion fruit
- 36 pests and 38 diseases with symptom descriptions, severity ratings, economic thresholds, and graded treatment plans
- 74 farming calendars with Zimbabwe-specific harvest notes and market advice

#### Agricultural services data
- 247 service records across all 10 Zimbabwe provinces
- 61 AGRITEX district offices
- GMB depots (all major silos)
- Agro dealers (Windmill, Farm & City, ZFC, and regional dealers)
- Specialty buyers (Chipinge Coffee Growers, Tanganda Tea, Cottco, TIMB, Interfresh, Hippo Valley, Triangle)
- Financial services (Agribank, AFC Holdings, CBZ)
- Research stations (Matopos, Henderson, Kutsaga/TRB, Katiyo, Lowveld)
- Community seed banks (Matabeleland North and South)

#### Backend
- FastAPI on Cloudflare Workers with 28 endpoints across 8 functional areas
- JWT authentication with bcrypt PIN hashing
- Groq-powered AI chat (Llama 3.3 70B) with full conversation history continuity
- 486-question offline chat guide interpolated with real farm context
- Market intelligence: crop prices, input costs, profit calculator
- ZimAgroMarket: listings, deals, price alerts, photo upload, SMS broadcast (pending carrier API)
- Agricultural services API: GPS-sorted nearby services from province JSON files
- Price scraper with Cloudflare Workers scheduled-job support

#### Home screen
- Real-time soil readings display (pH, moisture, temperature)
- Today's most important farming task
- Active crop season progress (phases, days to harvest)
- Market opportunity card (best crop at current prices)
- Online/offline status indicator

#### Market screen
- Live crop prices with demand indicators
- ZimAgroMarket sell/buy/deals tabs
- Price alerts with target price setting
- Offline draft queue (persisted via SecureStore, flushed on reconnect)

#### Chat screen
- Full conversation history maintained across the session
- Farm context (soil, crop, region) injected into every Groq conversation
- Session continuity — Groq remembers earlier messages in the conversation
- Offline guide with 486 pre-answered farming questions

#### Settings screen
- Notification preference persistence (expo-secure-store)
- Nearby services section (AGRITEX office, agro dealers, GMB depot, market)
- Online/offline path for services (backend when online, bundled JSON when offline)
- Language: English (Shona/Ndebele pending translation review)

#### Analytics screen
- Real season history from Supabase
- Soil reading trends over time
- Season-over-season comparison
- Pull-to-refresh

#### More screen
- PDF season report using real session data (yield, costs, profit, market advice)
- Season history view
- Yield recording

#### Technical
- All API calls have 20-second AbortController timeouts
- Offline-first: all critical features work without internet
- No hardcoded test data in production screens
- No debug endpoints in production
- Marketplace offline drafts persisted via SecureStore
- Push notifications for critical soil alerts (expo-notifications)

---

## [0.9.0] — April 2026 (Internal beta)

- Initial dataset: 30 crops, 30 pests, 33 diseases
- Core screens functional
- Demo mode only
- Basic Groq chat (no history continuity)
- Province data: hardcoded flat list

---

## [0.5.0] — February 2026 (Prototype)

- Proof of concept with maize and soya only
- Manual soil entry only
- Single-screen design
- No marketplace
- No authentication

---

## Planned

### [1.1.0] — Pending
- ESP32 Bluetooth soil sensor integration (blocked on hardware procurement)
- Shona and Ndebele language support (pending agronomic translation review)
- SMS broadcast for marketplace alerts (pending Econet/Netone API agreement)
- Play Store public release
- 500-farmer pilot — 2026/2027 growing season

### [1.2.0] — Future
- Weather forecast integration (Zimbabwe Meteorological Services API)
- Satellite NDVI imagery for field health monitoring
- Offline map of agro dealer locations
- WhatsApp integration for marketplace notifications
- Zambia / Malawi regional adaptation
