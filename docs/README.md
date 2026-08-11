# 🌱 MDUMENI — AI Agronomist for Zimbabwean Farmers

> *Mudhumeni* (Shona) — *farm advisor*

MDUMENI is an open-source AI-powered agronomist mobile application designed specifically for Zimbabwean smallholder farmers. It provides real-time crop recommendations, farming calendars, pest and disease diagnosis, market intelligence, and agricultural services — all working fully offline when no internet connection is available.

Built by **INTELLI-Farming**, University of Zimbabwe.

---

## The Problem

Zimbabwe has approximately 1.8 million smallholder farming households. Fewer than 1 in 10 have consistent access to an agricultural extension officer. Input costs are rising, rainfall is increasingly erratic, and soil degradation is widespread. Most farmers make critical planting decisions — what to grow, when to plant, what to apply — based on tradition and guesswork rather than their actual soil conditions.

MDUMENI changes this by putting a knowledgeable agronomist in every farmer's pocket.

---

## What It Does

| Feature | Description |
|---|---|
| **AI Crop Recommendation** | Analyses soil pH, moisture, temperature, agro-ecological region, farm size, budget, and irrigation access to recommend the best crops from a dataset of 60 varieties |
| **Farming Calendar** | Personalised day-by-day task schedule from planting to harvest, adapted to the farmer's active crop and current season progress |
| **Pest & Disease Diagnosis** | Identifies 36 pests and 38 diseases from symptom descriptions; provides treatment plans graded by budget (chemical vs organic) |
| **AI Chat** | Natural language farming advice powered by Groq (Llama 3.3 70B) when online; 486-question offline guide when not |
| **Market Intelligence** | Live crop prices, input costs, profit calculator, and market opportunity analysis |
| **ZimAgroMarket** | In-app marketplace for farmers to list produce for sale and find buyers |
| **Agricultural Services** | GPS-based finder for agro dealers, GMB depots, AGRITEX offices, financial services, and specialty buyers across all 10 Zimbabwe provinces |
| **ESP32 Sensor Integration** | Wireless soil sensor (in development) for automatic pH, moisture, and temperature readings |
| **Fully Offline** | All AI engines, crop data, pest database, and province service data run on-device with no internet required |

---

## Tech Stack

### Mobile App
| Component | Technology |
|---|---|
| Framework | React Native (Expo SDK 54) |
| Language | TypeScript |
| Navigation | React Navigation v7 |
| State | Zustand v5 |
| Local database | expo-sqlite (SQLite) |
| Secure storage | expo-secure-store |
| Notifications | expo-notifications |
| PDF generation | expo-print + expo-sharing |

### Backend
| Component | Technology |
|---|---|
| API framework | FastAPI |
| Runtime | Python 3.11 |
| Database | Supabase (PostgreSQL) |
| AI inference | Groq (Llama 3.3 70B) |
| Hosting | Cloudflare Workers |
| Auth | JWT (python-jose) |
| HTTP client | httpx |

### AI Engines (on-device)
- Crop recommendation — 6-factor weighted scoring across 60 crops
- Farming calendar — phase-based state machine per crop
- Planning engine — yield/cost/profit calculator
- Pest & disease — symptom-matching diagnosis with treatment plans

---

## Project Structure

```
mdumeni/
├── src/                          # React Native mobile app
│   ├── screens/                  # All app screens
│   ├── engines/                  # On-device AI engines (JS)
│   │   ├── cropEngine.js
│   │   ├── pestEngine.js
│   │   ├── cropDataset.json      # 60 crops
│   │   └── pestDataset.json      # 36 pests, 38 diseases
│   ├── data/                     # Province location data
│   │   ├── locationTypes.ts
│   │   ├── provinceIndex.ts      # Master index (all provinces)
│   │   └── provinces/            # 10 province JSON files
│   ├── services/                 # API calls, caching, storage
│   ├── hooks/                    # useSession, useTranslation
│   ├── store/                    # Zustand global state
│   ├── db/                       # SQLite schema and queries
│   └── components/               # Reusable UI components
│
├── backend/
│   └── mdumeni-backend/
│       ├── main.py               # FastAPI app, all routers
│       ├── auth.py               # JWT authentication
│       ├── market_api.py         # Market prices and inputs
│       ├── services_api.py       # Agricultural services endpoints
│       ├── marketplace.py        # ZimAgroMarket API
│       ├── price_scraper.py      # Price data collection
│       ├── crop_engine/          # Python AI crop recommendation engine
│       ├── calendar_engine/      # Farming calendar engine
│       ├── planning_engine/      # Yield/profit planning engine
│       ├── pest_engine/          # Pest and disease diagnosis engine
│       └── data/
│           └── provinces/        # Province JSON files (server-side)
│
└── docs/                         # Project documentation
```

---

## Agro-Ecological Regions

MDUMENI's recommendation engine is calibrated for Zimbabwe's five agro-ecological regions:

| Region | Rainfall | Description | Key Crops |
|---|---|---|---|
| I | >1,000mm | Eastern Highlands | Tea, Coffee, Wheat, Barley, Potatoes |
| II | 750–1,000mm | Intensive cropping zone | Maize, Tobacco, Soybeans, Horticulture |
| III | 650–800mm | Semi-intensive | Maize, Cotton, Groundnuts, Sunflower |
| IV | 450–650mm | Semi-arid | Sorghum, Millet, Cotton, Livestock |
| V | <450mm | Arid | Pearl millet, Cowpeas, Cattle, Goats |

---

## The Dataset

### Crops (60 total)
Traditional cereals · legumes · oilseeds · vegetables · fruit · cash crops · indigenous crops

Includes: Maize, Tobacco, Cotton, Soybeans, Sorghum, Pearl millet, Finger millet (Zviyo), Groundnuts, Sunflower, Sesame, Sugar cane, Cowpeas, Bambara groundnut (Nyimo), Pigeon peas, Lablab, Green peas, Lima bean, Okra (Derere), Covo (Swiss chard), Spinach, Carrots, Beetroot, Cucumber, Eggplant, Green beans, Lettuce, Sweet corn, Orange (Citrus), Guava, Passion fruit, Lemon, Coffee (Arabica), Macadamia, Tea, Moringa, Castor bean, Safflower, Ginger, Jatropha, Amaranth (Mowa), Coriander, and more.

### Pests & Diseases (74 total)
36 pests + 38 diseases, including: Fall Armyworm, Stalk Borer, Aphids, Leaf Miner, Coffee Berry Borer, Fruit Fly, Grey Leaf Spot, Rust, Fusarium, Late Blight, and 64 others.

### Agricultural Services (247 records)
All 10 provinces · 61 districts · Agro dealers · GMB depots · AGRITEX offices · Markets · Specialty buyers · Financial services · Research stations · Community seed banks

---

## Getting Started

### Prerequisites
- Node.js 18+
- Expo CLI (`npm install -g expo`)
- Android Studio (for APK builds) or Expo Go app
- Python 3.11+ (for backend)
- Supabase account
- Groq API key (free tier available)

### Mobile App Setup

```bash
git clone https://github.com/intellifarming/mdumeni
cd mdumeni/src
npm install
npx expo start
```

For an APK build:
```bash
cd android
./gradlew assembleRelease
```

### Backend Setup

```bash
cd mdumeni/backend/mdumeni-backend
pip install -r requirements.txt

# Set environment variables
export SUPABASE_URL=your_supabase_url
export SUPABASE_SERVICE_KEY=your_service_key
export JWT_SECRET=your_secret
export GROQ_API_KEY=your_groq_key

uvicorn main:app --reload
```

### Environment Variables (Cloudflare Workers)

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `JWT_SECRET` | Secret for JWT signing |
| `GROQ_API_KEY` | Groq API key for AI chat |
| `ANTHROPIC_API_KEY` | Optional — Anthropic fallback |

---

## API

Base URL: `https://mdumeni-backend.eugineeuman.workers.dev`

Interactive docs: `https://mdumeni-backend.eugineeuman.workers.dev/docs`

See [API Reference](docs/API_REFERENCE.md) for full documentation.

---

## Research & Academic Context

MDUMENI is a research project affiliated with the **University of Zimbabwe Department of Computer Science** and the **INTELLI-Farming research group**.

**Research questions:**
1. Can AI-driven crop recommendations reduce input waste and improve yields for smallholder farmers in semi-arid agro-ecological zones?
2. Does an offline-first AI agronomist meaningfully increase access to agricultural extension services in connectivity-constrained rural environments?
3. What is the effectiveness of ESP32-based low-cost soil sensing for smallholder precision agriculture?

**Target outcomes by August 2026:**
- 500-farmer pilot across 3 districts (Regions II, III, and IV)
- Baseline and end-of-season yield comparison data
- Full paper submission to AARSE 2026 (African Association of Remote Sensing of Environment) — August 31 deadline

---

## Contributing

MDUMENI is open-source and welcomes contributions. Priority areas:

1. **Agronomist review** — crop dataset validation against AGRITEX field data
2. **Shona/Ndebele translations** — agronomically accurate translation of the UI and offline guide
3. **Additional crop records** — more indigenous and traditional crops
4. **ESP32 firmware** — pending hardware procurement
5. **Market price integrations** — live GMB price feed, AMIS-Zimbabwe

Please read [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) before contributing.

---

## Licence

MIT — free to use, modify, and distribute with attribution.

---

## Contact

**Eugine Bhebhe** — Lead Developer  
INTELLI-Farming · University of Zimbabwe  
📱 +263 78 461 7009  
📧 bhebheeugine@gmail.com

---

*MDUMENI is built for Zimbabwean farmers, by Zimbabweans.*
