# MDUMENI Deployment Guide

This guide covers deploying MDUMENI to production: backend on Railway, database on Supabase, and mobile app on Google Play.

---

## Backend Deployment (Railway)

### Initial setup

1. Create an account at [railway.com](https://railway.com)
2. Connect your GitHub repository
3. Create a new project from the `mdumeni` repository
4. Configure:
   - **Root directory:** `backend/mdumeni-backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`

### Environment variables on Railway

Set these in the Railway dashboard under Variables:

```
SUPABASE_URL        = https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY= eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET          = (generate: python3 -c "import secrets; print(secrets.token_hex(32))")
GROQ_API_KEY        = gsk_...
```

### Province data files

The province JSON files must be in the repository at:
```
backend/mdumeni-backend/data/provinces/province_harare.json
backend/mdumeni-backend/data/provinces/province_bulawayo.json
... (all 10 provinces)
```

Ensure this directory is **not** in `.gitignore`. Railway deploys the repository contents, so the files must be committed.

### Verifying deployment

After deploy, check:
- `https://mdumeni-api-production.up.railway.app/health` -> `{"status": "healthy"}`
- `https://mdumeni-api-production.up.railway.app/services/provinces` -> list of 10 provinces
- `https://mdumeni-api-production.up.railway.app/docs` -> Swagger UI

### Price scraper cron job

Set up automated daily price updates:
1. Railway dashboard -> your service -> **Cron**
2. Add a scheduled job:
   - **Command:** `python price_scraper.py`
   - **Schedule:** `0 4 * * *` (4am UTC = 6am Zimbabwe time)

### Hosting plan limits

Review Railway usage and plan limits before any public launch or pilot.

---

## Supabase Setup

### Creating the database

1. Create a project at [supabase.com](https://supabase.com)
2. Note your project URL and service role key (Settings → API)
3. Open the SQL Editor and run the following in order:

### Core tables

```sql
-- Farmers
CREATE TABLE IF NOT EXISTS farmers (
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

-- Active crops
CREATE TABLE IF NOT EXISTS active_crops (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id       UUID REFERENCES farmers(id) ON DELETE CASCADE,
  crop_id         TEXT NOT NULL,
  crop_name       TEXT NOT NULL,
  planting_date   DATE NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Sensor readings
CREATE TABLE IF NOT EXISTS sensor_readings (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_id       UUID REFERENCES farmers(id) ON DELETE CASCADE,
  soil_ph         NUMERIC(4,2),
  moisture_pct    NUMERIC(5,2),
  temp_c          NUMERIC(5,2),
  device_id       TEXT,
  source          TEXT DEFAULT 'manual',
  recorded_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Season history
CREATE TABLE IF NOT EXISTS season_history (
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

-- Grants for service role
GRANT ALL ON farmers        TO service_role;
GRANT ALL ON active_crops   TO service_role;
GRANT ALL ON sensor_readings TO service_role;
GRANT ALL ON season_history TO service_role;
```

### Marketplace tables

Run `marketplace_tables.sql` (in the repository) to create the marketplace schema.

### Marketplace storage bucket

1. Supabase dashboard → Storage → New bucket
2. Name: `marketplace-photos`
3. Public: **ON**
4. File size limit: 5 MB
5. Allowed MIME types: `image/jpeg, image/png, image/webp`

### Row Level Security

For the pilot phase, RLS is handled at the application layer via the JWT. The service role key (used by the backend) bypasses RLS. This is appropriate for the current scale.

For public launch, add proper RLS policies:
```sql
ALTER TABLE farmers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "farmers_own_data" ON farmers
  FOR ALL USING (id = auth.uid());
```

---

## Marketplace Backend Wiring

Add these two lines to `main.py`:

```python
# In the imports section (around line 60):
from marketplace import router as marketplace_router

# In the router registration section (around line 86):
app.include_router(marketplace_router)
```

Then copy `marketplace.py` to the backend folder and push. The marketplace endpoints will appear under `/marketplace/` in the API docs.

---

## Google Play Store Submission

### One-time account setup

1. Go to [play.google.com/console](https://play.google.com/console)
2. Pay the $25 one-time registration fee
3. Complete identity verification (takes 1–3 days)

### Release signing setup

Generate a keystore for signing the release APK:

```bash
keytool -genkeypair -v \
  -keystore mdumeni-release.keystore \
  -alias mdumeni \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

**Store this keystore file safely.** If you lose it, you cannot update your app on the Play Store.

Add to `android/app/build.gradle`:

```gradle
android {
  signingConfigs {
    release {
      storeFile file('mdumeni-release.keystore')
      storePassword 'your_store_password'
      keyAlias 'mdumeni'
      keyPassword 'your_key_password'
    }
  }
  buildTypes {
    release {
      signingConfig signingConfigs.release
      minifyEnabled false
      proguardFiles getDefaultProguardFile('proguard-android-optimize.txt')
    }
  }
}
```

Build the signed APK:
```bash
cd src/android
./gradlew bundleRelease
```

This produces an `.aab` (Android App Bundle) at `android/app/build/outputs/bundle/release/`.

### Play Store listing

**App name:** MDUMENI — AI Farm Advisor

**Short description (80 chars):**
AI crop advice for Zimbabwean farmers. Works offline. Free.

**Full description:**
```
MDUMENI is your personal AI agronomist — built specifically for Zimbabwean farmers.

Get personalised recommendations for which crops to grow based on your soil, rainfall zone, farm size, and budget. Know exactly what to do on your farm every day of the growing season. Identify pests and diseases before they destroy your crop.

WORKS FULLY OFFLINE — all AI runs on your phone. No internet needed for crop recommendations, calendar, or pest diagnosis.

FEATURES:
• AI crop recommendations — 60 crops, 5 agro-ecological regions
• Day-by-day farming calendar for your active crop
• Pest and disease diagnosis with treatment plans
• Live market prices for major crops
• ZimAgroMarket — buy and sell produce directly with other farmers
• Find agro dealers, GMB depots, and AGRITEX offices near you
• PDF season report for bank and NGO loan applications
• AI chat powered by Groq (online) + 486-question offline guide

Built by INTELLI-Farming, University of Zimbabwe.
Free and open source.
```

**Category:** Agriculture

**Content rating:** Everyone

**App icon:** Use the 🌱 MDUMENI green brand icon (512×512 PNG)

**Screenshots:** Capture at minimum:
1. Home screen showing soil readings and today's task
2. Crop recommendation results
3. Farming calendar phase view
4. AI chat interaction
5. ZimAgroMarket listing

### Required policy links for Play Store

During submission you must provide:
- **Privacy Policy URL** — host `PRIVACY_POLICY.md` at a public URL (e.g. GitHub Pages or a simple web page)
- **Data safety section** — declare what data you collect (see Privacy Policy for the complete list)

**Data safety declarations for Play Store:**

| Data type | Collected | Shared | Optional |
|---|---|---|---|
| Phone number | Yes | No | No |
| Personal info (location/farm data) | Yes | No | No |
| App activity (crop/chat history) | Yes | No | No |

All data is encrypted in transit. Users can request deletion.

---

## Monitoring and Alerts

### Railway monitoring

- Railway provides service logs and usage metrics in the dashboard
- Set up email alerts for service restarts

### Supabase monitoring

- Supabase dashboard shows database size, API usage, and active connections
- Free tier limit: 500MB database, 2GB bandwidth

### Error tracking (future)

Consider adding Sentry for crash reporting:
```bash
npm install @sentry/react-native
```

---

## Upgrading the Railway Service

When ready for the pilot (recommended at 50+ active users):

1. Railway dashboard -> your project -> service settings
2. Review usage, resource limits, and plan options
3. Upgrade before pilot traffic exceeds the current plan

At 500+ active users, consider:
- A higher Railway plan for more backend capacity
- **Supabase Pro** ($25/month) for higher database limits and daily backups
- PostgreSQL read replica if database traffic requires it

Total cost for a production-grade setup depends on Railway and Supabase usage.

---

## Checklist Before Pilot Launch

- [ ] All 10 province JSON files in `backend/mdumeni-backend/data/provinces/`
- [ ] All output files from development session dropped into `src/`
- [ ] `cropDataset.json` updated to 60 crops
- [ ] `pestDataset.json` updated with lookup maps
- [ ] `marketplace.py` wired into `main.py`
- [ ] Marketplace SQL tables created in Supabase
- [ ] `marketplace-photos` storage bucket created
- [ ] Price scraper cron job configured in Railway
- [ ] Backend health check passing
- [ ] `/services/provinces` returning all 10 provinces
- [ ] Privacy Policy hosted at a public URL
- [ ] APK tested on at least 3 different Android devices
- [ ] Play Store account created (if going to Play Store)
- [ ] Farmer onboarding guide prepared for pilot participants
