# MDUMENI API Reference

**Base URL:** `https://mdumeni-api-production.up.railway.app`  
**Interactive docs:** `https://mdumeni-api-production.up.railway.app/docs`  
**Authentication:** Bearer JWT token (obtained from `/auth/login`)  
**Content-Type:** `application/json`

> **Note:** The backend is hosted on Railway. Review Railway plan limits before public launch or pilot use.

---

## Authentication

### POST /auth/register
Register a new farmer account.

**Request body:**
```json
{
  "phone_number": "0771234567",
  "pin": "1234",
  "province": "Mashonaland East",
  "district": "Marondera",
  "farm_size_ha": 2.5,
  "agro_region": 2,
  "has_irrigation": false,
  "budget_level": "low"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "farmer_id": "uuid",
  "message": "Registration successful"
}
```

---

### POST /auth/login
Log in to an existing account.

**Request body:**
```json
{
  "phone_number": "0771234567",
  "pin": "1234"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "farmer_id": "uuid"
}
```

---

### GET /auth/me
Get the current farmer's profile.  
**Auth required:** Yes

**Response:**
```json
{
  "farmer_id": "uuid",
  "phone_number": "+2630771234567",
  "province": "Mashonaland East",
  "district": "Marondera",
  "farm_size_ha": 2.5,
  "agro_region": 2,
  "has_irrigation": false,
  "budget_level": "low",
  "language": "english",
  "created_at": "2026-01-15T08:00:00Z"
}
```

---

### PUT /auth/profile
Update the farmer's profile.  
**Auth required:** Yes

**Request body:** (all fields optional)
```json
{
  "province": "Midlands",
  "district": "Gweru",
  "farm_size_ha": 3.0,
  "budget_level": "medium"
}
```

---

## AI Engines

### POST /recommend
Get AI crop recommendations for a farm profile.  
**Auth required:** No

**Request body:**
```json
{
  "soil_ph": 6.2,
  "soil_moisture_pct": 55.0,
  "soil_temp_c": 24.0,
  "agro_region": 2,
  "has_irrigation": false,
  "budget_level": "low",
  "planting_month": 11,
  "farm_size_ha": 2.5
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "rank": 1,
      "crop_id": "CROP_001",
      "crop_name": "Maize",
      "score_pct": 94,
      "selected_variety": {
        "name": "SC403",
        "type": "hybrid",
        "maturity_days": 90,
        "yield_t_ha": 7.0,
        "input_level": "low"
      },
      "notes": ["Good pH match", "Short season suits November planting"],
      "disqualifiers": [],
      "score_breakdown": {
        "soil_ph": 0.95,
        "moisture": 0.88,
        "region": 1.0,
        "temperature": 0.92,
        "irrigation": 1.0,
        "budget": 1.0
      }
    }
  ],
  "excluded": [],
  "input_summary": { "ph": 6.2, "region": 2, "month": 11 }
}
```

---

### POST /calendar
Get the farming calendar for an active crop.  
**Auth required:** No

**Request body:**
```json
{
  "crop_id": "CROP_001",
  "days_since_planting": 25,
  "soil_moisture_pct": 62.0,
  "soil_ph": 6.1,
  "soil_temp_c": 26.0,
  "budget_level": "low",
  "farm_size_ha": 2.5,
  "has_irrigation": false,
  "planting_month": 11
}
```

**Response:**
```json
{
  "crop_id": "CROP_001",
  "crop_name": "Maize",
  "days_since_planting": 25,
  "days_to_harvest": 65,
  "season_progress_pct": 28,
  "current_phase": {
    "phase_name": "Vegetative growth",
    "phase_number": 2,
    "start_day": 10,
    "end_day": 45,
    "description": "Rapid leaf and stem development..."
  },
  "tasks_today": [
    {
      "task": "top_dress",
      "priority": "high",
      "message": "Apply 50kg/ha Ammonium Nitrate (LAN 28%)...",
      "products": [{ "name": "LAN 28%", "rate": "50 kg/ha" }]
    }
  ],
  "alerts": [],
  "harvest_note": "Harvest SC403 when husks are dry..."
}
```

---

### POST /plan
Get yield and profitability plan for a crop.  
**Auth required:** No

**Request body:**
```json
{
  "crop_id": "CROP_001",
  "farm_size_ha": 2.5,
  "budget_level": "low",
  "agro_region": 2,
  "has_irrigation": false,
  "planting_month": 11
}
```

**Response:**
```json
{
  "crop_id": "CROP_001",
  "crop_name": "Maize",
  "expected_yield_kg": 6250,
  "total_cost_usd": 312.50,
  "gross_revenue_usd": 1250.00,
  "net_profit_usd": 937.50,
  "roi_pct": 300,
  "market_price_usd_kg": 0.20,
  "sell_month": "April",
  "harvest_plan": {
    "market_advice": "Sell at Mbare Musika or GMB depot",
    "storage_advice": "Store in hermetic bags at <13% moisture"
  },
  "input_costs": [
    { "item": "Seed (SC403)", "qty": "22.5kg", "cost_usd": 67.50 },
    { "item": "Compound D (basal)", "qty": "500kg", "cost_usd": 125.00 }
  ]
}
```

---

### POST /threats
Get pest and disease threats for a crop and month.  
**Auth required:** No

**Request body:**
```json
{
  "crop_id": "CROP_001",
  "month": 2,
  "budget_level": "low"
}
```

**Response:**
```json
{
  "crop_id": "CROP_001",
  "month": 2,
  "total_threats": 3,
  "threats": [
    {
      "id": "PEST_001",
      "common_name": "Fall Armyworm",
      "severity": "critical",
      "risk_level": "high",
      "symptoms": ["Ragged holes in leaves...", "Frass in whorl..."],
      "economic_threshold": "Treat when >20% of plants show damage",
      "recommended_treatments": [
        { "type": "organic", "product": "Neem extract", "rate": "5 mL/L" }
      ]
    }
  ]
}
```

---

### POST /diagnose
Diagnose a pest or disease from symptoms.  
**Auth required:** No

**Request body:**
```json
{
  "symptoms": ["yellow leaves", "white powder", "stunted growth"],
  "crop_id": "CROP_001",
  "budget_level": "low"
}
```

**Response:**
```json
{
  "matches": [
    {
      "id": "DIS_005",
      "common_name": "Grey Leaf Spot",
      "confidence": 0.87,
      "pathogen_type": "fungal",
      "symptoms": [...],
      "treatments": [...],
      "prevention": [...]
    }
  ],
  "query_tokens": ["yellow", "white", "powder", "stunted"]
}
```

---

### POST /treatment
Get a treatment plan for a specific pest or disease.  
**Auth required:** No

**Request body:**
```json
{
  "pest_or_disease_id": "PEST_001",
  "farm_size_ha": 2.5,
  "budget_level": "low"
}
```

---

## Composite Session

### POST /session
The mobile app's primary endpoint — runs all AI engines in parallel and returns a complete dashboard payload in one call.  
**Auth required:** Yes

**Request body:**
```json
{
  "farmer_id": "uuid",
  "soil_ph": 6.2,
  "soil_moisture_pct": 55.0,
  "soil_temp_c": 24.0,
  "days_since_planting": 25
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "generated_at": "2026-06-01T08:00:00Z",
  "farmer_profile": { "...": "..." },
  "active_crop": { "crop_id": "CROP_001", "crop_name": "Maize", "...": "..." },
  "sensor_reading": { "soil_ph": 6.2, "moisture_pct": 55.0, "temp_c": 24.0 },
  "crop_recommendations": { "recommendations": [...], "...": "..." },
  "daily_calendar": { "current_phase": {...}, "tasks_today": [...], "...": "..." },
  "crop_plan": { "expected_yield_kg": 6250, "net_profit_usd": 937.50, "...": "..." },
  "pest_threats": { "total_threats": 3, "threats": [...] },
  "market_summary": { "top_crops": [...], "input_prices": {...} }
}
```

---

## Farmer Data

### POST /farmer/crop
Set or update the active crop.  
**Auth required:** Yes

**Request body:**
```json
{
  "crop_id": "CROP_001",
  "crop_name": "Maize",
  "planting_date": "2026-11-15"
}
```

---

### POST /farmer/reading
Submit a sensor reading.  
**Auth required:** Yes

**Request body:**
```json
{
  "soil_ph": 6.2,
  "soil_moisture_pct": 55.0,
  "soil_temp_c": 24.0,
  "device_id": "MDUMENI-001",
  "source": "esp32"
}
```

---

### GET /farmer/readings
Get recent sensor readings.  
**Auth required:** Yes

**Query params:** `limit` (default 10), `days` (default 7)

---

### POST /farmer/yield
Record a season yield.  
**Auth required:** Yes

**Request body:**
```json
{
  "crop_id": "CROP_001",
  "crop_name": "Maize",
  "season": "2025/2026",
  "actual_yield_kg": 5800,
  "farm_size_ha": 2.5,
  "input_cost_usd": 312.50,
  "sell_price_usd_kg": 0.20,
  "notes": "Good rains in January helped"
}
```

---

### GET /farmer/history
Get season history records.  
**Auth required:** Yes

---

## AI Chat

### POST /chat
Send a question to the AI agronomist.  
**Auth required:** Yes (optional — unauthenticated requests use generic context)

**Request body:**
```json
{
  "question": "My maize leaves are turning yellow at the tips. What is wrong?",
  "context": {
    "soil_ph": 6.2,
    "moisture_pct": 55.0,
    "temp_c": 24.0,
    "active_crop": "Maize",
    "agro_region": 2,
    "farm_size_ha": 2.5,
    "budget_level": "low",
    "current_month": "February"
  },
  "history": [
    { "role": "user", "content": "When did I plant my maize?" },
    { "role": "assistant", "content": "Your maize was planted on 15 November..." }
  ]
}
```

**Response:**
```json
{
  "answer": "Yellow tips on maize leaves in February typically indicate nitrogen deficiency...",
  "model": "llama-3.3-70b-versatile",
  "tokens_used": 287
}
```

---

## Market Intelligence

### GET /market/summary
Get a summary of current crop prices.

**Response:**
```json
{
  "crops": [
    {
      "crop_id": "CROP_001",
      "crop_name": "Maize",
      "price_usd_kg": 0.20,
      "price_usd_tonne": 200,
      "demand": "high",
      "updated": "2026-06-01"
    }
  ]
}
```

---

### GET /market/prices/crops/best
Get the top market opportunities ranked by expected return.

---

### GET /market/prices/inputs
Get current input prices by category.  
**Query params:** `category` — one of `fertiliser`, `seed`, `chemical`, `machinery`

---

### POST /market/profit/calculate
Calculate yield and profit for given inputs.

**Request body:**
```json
{
  "crop_id": "CROP_001",
  "farm_size_ha": 2.5,
  "budget_level": "low",
  "agro_region": 2,
  "has_irrigation": false
}
```

---

## Agricultural Services

### POST /services/nearby
Get agricultural services near a GPS location, sorted by distance.

**Request body:**
```json
{
  "lat": -17.858,
  "lng": 31.044,
  "province": "Harare",
  "types": ["agro_dealer", "gmb_depot"],
  "crop_id": "CROP_001",
  "radius_km": 50,
  "limit": 10
}
```

**Response:**
```json
[
  {
    "id": "AGR_HA_001",
    "name": "Farm & City Centre — Avondale",
    "type": "agro_dealer",
    "province": "Harare",
    "district": "Harare",
    "town": "Avondale",
    "address": "Avondale Shopping Centre, King George Road",
    "phone": "+263 242 336 666",
    "lat": -17.7985,
    "lng": 31.0330,
    "products": ["fertilisers", "seeds", "chemicals"],
    "open_hours": "Mon–Fri 08:00–17:30, Sat 08:00–13:00",
    "notes": "Largest retail agro dealer in Harare.",
    "verified": true,
    "distance_km": 6.7
  }
]
```

---

### GET /services/district/{province}/{district}
Get the AGRITEX office and key services for a specific district.

**Example:** `GET /services/district/Manicaland/Chipinge`

**Response:**
```json
{
  "province": "Manicaland",
  "district": "Chipinge",
  "district_info": {
    "name": "Chipinge",
    "agro_region": 1,
    "rainfall_mm": 1200,
    "main_crops": ["Tea", "Coffee", "Macadamia", "Cotton", "Maize"]
  },
  "agritex_office": { "name": "AGRITEX District Office — Chipinge", "..." },
  "services": [...]
}
```

---

### GET /services/province/{province_name}
Get all services in a province.  
**Query params:** `type` — filter by service type (optional)

---

### GET /services/provinces
List all provinces with service counts.

---

## Dataset

### GET /crops
Get all 60 crops in the dataset.  
**Query params:** `region` (filter by agro-ecological region), `type` (filter by crop type)

---

### GET /crops/{crop_id}
Get full details for a specific crop.  
**Example:** `GET /crops/CROP_001`

---

## System

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-06-01T08:00:00Z"
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Human-readable error message"
}
```

| Status code | Meaning |
|---|---|
| 400 | Bad request — invalid parameters |
| 401 | Unauthorized — missing or invalid token |
| 404 | Resource not found |
| 422 | Validation error — request body schema mismatch |
| 500 | Internal server error |
| 503 | Server waking from sleep (retry after 60 seconds) |

---

## Rate Limits

The API currently has no rate limits. Be respectful — this runs on a free-tier server.

---

## Authentication Details

Tokens are JWTs signed with HS256. They do not expire automatically in the current implementation — a future release will add 30-day expiry with refresh tokens.

Include the token in all authenticated requests:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
