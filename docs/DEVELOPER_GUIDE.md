# MDUMENI Developer Guide

This guide covers local development setup, architecture decisions, database schema, and how to contribute.

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Node.js | 18+ | Mobile app build |
| Expo CLI | Latest | React Native toolchain |
| Python | 3.11+ | Backend |
| Android Studio | Latest | APK builds |
| Git | Any | Version control |

Optional but recommended:
- VS Code with ESLint and TypeScript extensions
- Supabase CLI for local database development
- Postman or Bruno for API testing

---

## Repository Structure

```
mdumeni/
├── src/                    # React Native mobile app (Expo)
├── backend/
│   └── mdumeni-backend/    # FastAPI Python backend
└── docs/                   # Documentation
```

---

## Mobile App Setup

```bash
git clone https://github.com/intellifarming/mdumeni
cd mdumeni/src
npm install
```

### Running in development

```bash
npx expo start
```

Then press `a` for Android emulator, or scan the QR code with Expo Go on your phone.

### Building an APK (local)

```bash
cd android
./gradlew assembleRelease
```

The APK will be at `android/app/build/outputs/apk/release/app-release.apk`.

### Path aliases

The project uses `@/` as an alias for `src/`. Configured in `babel.config.js` and `tsconfig.json`. All imports use `@/` instead of relative paths.

---

## Backend Setup

```bash
cd mdumeni/backend/mdumeni-backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file (never commit this):

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...
JWT_SECRET=choose-a-strong-random-secret
GROQ_API_KEY=gsk_...
```

### Running locally

```bash
uvicorn main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`.

### Adding province data for local development

Copy the province JSON files to the backend data directory:
```bash
mkdir -p data/provinces
cp ../../src/data/provinces/*.json data/provinces/
```

---

## Architecture

### Mobile app architecture

```
User interaction
      ↓
  Screen (*.tsx)
      ↓
  Zustand store (global state)
      ↓                    ↓
 SQLite (local)        API calls (when online)
      ↓                    ↓
 useSession hook     FastAPI backend
      ↓                    ↓
 On-device engines    AI engines (Python)
 (cropEngine.js,      Groq (AI chat)
  pestEngine.js)      Supabase (data)
```

**Key principle: offline first.** The app is fully functional without internet. All AI engines, crop data, pest data, and province service data are bundled in the app. The backend provides enhanced capabilities (live prices, AI chat, persistent history) when online.

### State management

Zustand is used for all global state. The store (`src/store/index.ts`) contains:

| Slice | Contents |
|---|---|
| Auth | `farmerId`, `token`, `isAuthenticated` |
| Profile | `profile` (FarmerProfile), `isDemoMode` |
| Sensor | `sensorReading`, `sensorConnected`, `sensorDeviceId` |
| Session | `session`, `sessionLoading`, `sessionError` |
| Crops | `activeCrop`, `cropRecommendations` |
| Chat | `chatMessages`, `addChatMessage`, `clearChat` |
| Network | `isOnline` |

### Database (SQLite — on device)

Tables managed by `src/db/database.ts`:

```sql
farmer_profile          -- farm setup data
active_crops            -- current planted crop
sensor_readings         -- historical soil readings (local)
season_history          -- past yield records
```

### On-device AI engines

All AI logic is duplicated in both Python (backend) and JavaScript (on-device). The Python versions are the source of truth — the JS versions are ports of the same algorithm, keeping the same weights, scoring functions, and output structure.

If you change the Python scoring algorithm, you must update the JS engine to match.

---

## Supabase Schema

### farmers table
```sql
CREATE TABLE farmers (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone_number    TEXT UNIQUE NOT NULL,
  pin_hash        TEXT NOT NULL,
  province        TEXT,
  district        TEXT,
  farm_size_ha    NUMERIC(6,2),
  agro_region     INTEGER CHECK (agro_region BETWEEN 1 AND 5),
  has_irrigation  BOOLEAN DEFAULT FALSE,
  budget_level    TEXT CHECK (budget_level IN ('low','medium','high')),
  language        TEXT DEFAULT 'english',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### active_crops table
```sql
CREATE TABLE active_crops (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id       UUID REFERENCES farmers(id) ON DELETE CASCADE,
  crop_id         TEXT NOT NULL,
  crop_name       TEXT NOT NULL,
  planting_date   DATE NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### sensor_readings table
```sql
CREATE TABLE sensor_readings (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id       UUID REFERENCES farmers(id) ON DELETE CASCADE,
  soil_ph         NUMERIC(4,2),
  moisture_pct    NUMERIC(5,2),
  temp_c          NUMERIC(5,2),
  device_id       TEXT,
  source          TEXT DEFAULT 'manual',
  recorded_at     TIMESTAMPTZ DEFAULT NOW()
);
```

### season_history table
```sql
CREATE TABLE season_history (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id         UUID REFERENCES farmers(id) ON DELETE CASCADE,
  crop_id           TEXT NOT NULL,
  crop_name         TEXT NOT NULL,
  season            TEXT NOT NULL,
  actual_yield_kg   NUMERIC(10,2),
  farm_size_ha      NUMERIC(6,2),
  input_cost_usd    NUMERIC(10,2),
  sell_price_usd_kg NUMERIC(8,4),
  notes             TEXT,
  recorded_at       TIMESTAMPTZ DEFAULT NOW()
);
```

### marketplace tables
See `marketplace_tables.sql` for the full marketplace schema.

---

## Adding a New Crop

1. Add the crop record to `crop_engine/crop_dataset_extended.py` (CROP_061 onwards)
2. Add a calendar entry to `calendar_engine/crop_calendars.py` using `_generic_calendar()`
3. Add any new pests/diseases to `pest_engine/pest_disease_db.py`
4. Regenerate the JS JSON files:
   ```bash
   cd backend/mdumeni-backend
   python3 -c "import json; from crop_engine.crop_dataset import CROPS; json.dump(CROPS, open('../../src/engines/cropDataset.json','w'), indent=2)"
   python3 -c "import json; from pest_engine.pest_disease_db import PESTS, DISEASES, PESTS_BY_CROP, DISEASES_BY_CROP; json.dump({'pests':PESTS,'diseases':DISEASES,'pestsByCrop':PESTS_BY_CROP,'diseasesByCrop':DISEASES_BY_CROP}, open('../../src/engines/pestDataset.json','w'), indent=2)"
   ```

---

## Adding a New Province Service Record

1. Open the relevant `src/data/provinces/province_*.json` file
2. Add a new object to the `services` array following the `ServiceLocation` schema in `src/data/locationTypes.ts`
3. Assign the next available ID in the sequence (e.g. `AGR_HA_028` for Harare agro dealers)
4. Copy the updated JSON to `backend/mdumeni-backend/data/provinces/` as well
5. Mark `verified: false` if you cannot confirm the details from an official source

---

## Testing

### Backend tests

```bash
cd backend/mdumeni-backend
python3 -m pytest tests/ -v
```

### Manual API testing

The backend auto-generates interactive docs at `/docs` (Swagger UI). Use these to test any endpoint directly in the browser.

### Mobile testing

For device testing without a physical device:
```bash
npx expo start --android  # opens Android emulator
```

---

## Deployment

### Backend (Cloudflare Workers)

1. Push to the `main` branch on GitHub
2. Deploy using the configured Cloudflare Workers workflow
3. Check deployment logs in the Cloudflare dashboard

**Cloudflare Workers environment variables required:**

| Variable | Value source |
|---|---|
| `SUPABASE_URL` | Supabase project settings |
| `SUPABASE_SERVICE_KEY` | Supabase project settings → Service role key |
| `JWT_SECRET` | Generate: `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `GROQ_API_KEY` | https://console.groq.com |

**Important:** The province JSON data files must be included in the repository and deployed to Cloudflare Workers. They live at `backend/mdumeni-backend/data/provinces/`. Do not add this directory to `.gitignore`.

### Mobile app (APK sideload)

```bash
cd src/android
./gradlew assembleRelease
# APK at android/app/build/outputs/apk/release/app-release.apk
```

### Mobile app (Play Store)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full Play Store submission instructions.

---

## Code Style

- TypeScript strict mode is enabled
- ESLint is configured — run `npm run lint` before committing
- No default exports in service files — named exports only
- All screen components are named exports in their own file
- API calls are centralised in `src/services/api.ts`
- Never import from `./provinces/province_*.json` directly — always use `provinceIndex.ts`

---

## Key Design Decisions

**Why offline-first?** Rural Zimbabwe has poor and expensive mobile data. A farmer in Binga should get the same quality advice as a farmer in Harare. All intelligence runs on-device.

**Why duplicate the AI engines in JS and Python?** The Python engines are authoritative (easier to test, debug, and update). The JS engines are ports for offline mobile use. The output schema is identical so the app behaves consistently online and offline.

**Why FastAPI over Django/Express?** Automatic OpenAPI docs, Python typing support, async performance, and minimal boilerplate. The entire backend is ~900 lines of Python.

**Why Supabase?** Postgres with Row Level Security, authentication, file storage, and generous free tier — everything needed without managing infrastructure.

**Why Zustand over Redux?** Less boilerplate, no action creators, works well with React's concurrent features. For a farming app, we don't need the full Redux pattern.

**Why 10 separate province JSON files instead of one big file?** The master index uses lazy loading — only the active farmer's province is loaded into memory. A single 500KB file would be loaded into memory on every app start regardless of which province the farmer is in.

---

## Contributing

### Reporting bugs

Open a GitHub issue with:
- MDUMENI version
- Android version and device model
- Steps to reproduce
- What you expected vs what happened
- Screenshots if relevant

### Submitting changes

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test thoroughly on device
5. Submit a pull request with a clear description of what changed and why

### Priority contribution areas

- Agronomist review of crop dataset against AGRITEX field data
- Shona and Ndebele translation of UI strings and offline guide
- Additional indigenous and traditional crop records
- ESP32 sensor firmware
- Additional province service records (especially verification of unverified entries)

---

## Licence

MIT. See [LICENSE](../LICENSE) for details.

The agronomic dataset is separately licenced for non-commercial agricultural use with attribution to INTELLI-Farming, University of Zimbabwe.
