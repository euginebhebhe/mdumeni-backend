"""
MDUMENI — Unified FastAPI Integration Layer
=============================================
Single API that exposes all four intelligence engines + market intelligence:

  Engine 1 — Crop Recommendation
  Engine 2 — Farming Calendar
  Engine 3 — Planning
  Engine 4 — Pest & Disease
  Engine 5 — Market Intelligence (prices, profit, alerts)

<<<<<<< HEAD
Base URL:   https://mdumeni-api.onrender.com
Docs:       https://mdumeni-api.onrender.com/docs
=======
All endpoints follow the same pattern:
  - POST body with JSON payload
  - Validated input with clear error messages
  - Structured JSON response
  - Health check at /health

Base URL:   http://mdumeni-api.onrender.com
Docs:       http://mdumeni-api.onrender.com/docs  (Swagger UI — auto-generated)

Run:
    pip install fastapi uvicorn
    uvicorn api_main:app --reload --port 8000

Or production:
    gunicorn api_main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

Offline fallback:
    The Flask api.py in /crop_engine/ works without FastAPI if uvicorn
    is unavailable. This file is the production integration layer.
>>>>>>> 2b0ebb970cfb988e613c58929dfc8d132d385e0e
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date, timedelta

from db   import get_db
from auth import hash_pin, verify_pin, create_token, verify_token, normalize_phone

# ── Import all four engines ───────────────────────────────────────────────────
from crop_engine.recommender  import recommend_crops,    CropInput
from calendar_engine.engine   import get_daily_guidance, CalendarInput
from planning_engine.engine   import generate_plan,      PlanningInput
from pest_engine.engine       import crop_threats, diagnose, get_treatment_plan
from crop_engine.crop_dataset import CROPS, CROP_BY_ID

# ── Import market intelligence routers ───────────────────────────────────────
from market_api    import router as market_router
from price_scraper import scraper_router

# ══ App setup ══════════════════════════════════════════════════════════════════

app = FastAPI(
    title       = "MDUMENI Intelligence Engine API",
    description = "AI agronomist + market intelligence for Zimbabwe — crop recommendation, "
                  "farming calendar, planning, pest/disease diagnosis, live market prices.",
    version     = "2.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_methods     = ["*"],
    allow_headers     = ["*"],
    allow_credentials = True,
)

# ── Register market intelligence routers ──────────────────────────────────────
app.include_router(market_router)
app.include_router(scraper_router)

# ══ Global error handlers ══════════════════════════════════════════════════════

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"error": "Validation error", "detail": str(exc)})

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal engine error", "detail": str(exc)})

# ══ Startup event ══════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_price_update():
    """Run price scraper on startup if prices are not current today."""
    import asyncio
    try:
        db = get_db()
        result = db.table("market_prices").select("price_date").order("price_date", desc=True).limit(1).execute()
        last_date = result.data[0]["price_date"] if result.data else None
        if last_date != str(date.today()):
            from price_scraper import run_daily_update
            asyncio.create_task(run_daily_update(use_ai=False))
            print(f"[MDUMENI] Price scraper triggered — last update was {last_date}")
        else:
            print(f"[MDUMENI] Prices are current for {date.today()}")
    except Exception as e:
        print(f"[MDUMENI] Startup price check error: {e}")

# ══ In-memory sensor store ═════════════════════════════════════════════════════

_latest_reading: dict = {
    "device_id":   "WEB-INPUT",
    "soil_ph":      6.1,
    "moisture_pct": 62,
    "temp_c":       24.0,
    "battery_pct":  100,
    "recorded_at":  datetime.utcnow().isoformat() + "Z",
    "source":       "demo",
}

# ══ Web input form HTML ════════════════════════════════════════════════════════

_INPUT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>MDUMENI — Soil Input</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#F4F7F5;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:16px}
  .card{background:white;border-radius:20px;padding:28px 24px;width:100%;max-width:420px;box-shadow:0 8px 32px rgba(0,0,0,0.10)}
  .logo{display:flex;align-items:center;gap:10px;margin-bottom:24px}
  .logo-icon{width:40px;height:40px;background:#1A5C2A;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px}
  .logo-text{font-size:22px;font-weight:800;color:#1A5C2A;letter-spacing:-0.5px}
  .logo-text span{color:#EF9F27}
  h1{font-size:18px;font-weight:700;color:#0F1A12;margin-bottom:4px}
  .sub{font-size:13px;color:#607868;margin-bottom:24px;line-height:1.4}
  .field{margin-bottom:18px}
  label{display:block;font-size:12px;font-weight:700;color:#607868;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:7px}
  .input-row{display:flex;align-items:center;gap:8px}
  .adj{width:40px;height:44px;background:#F4F7F5;border:1.5px solid #E0E9E2;border-radius:9px;font-size:22px;color:#3B5040;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;-webkit-tap-highlight-color:transparent}
  .adj:active{background:#E0E9E2}
  input[type=number]{flex:1;height:44px;border:1.5px solid #E0E9E2;border-radius:9px;font-size:22px;font-weight:700;color:#0F1A12;text-align:center;background:#F4F7F5;outline:none;-moz-appearance:textfield}
  input[type=number]:focus{border-color:#1A5C2A;background:white}
  input::-webkit-outer-spin-button,input::-webkit-inner-spin-button{-webkit-appearance:none}
  .status{display:flex;align-items:center;gap:6px;margin-top:7px;min-height:18px}
  .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
  .status-text{font-size:12px;font-weight:500}
  .scale{height:4px;background:#E0E9E2;border-radius:2px;margin-top:6px;overflow:hidden}
  .scale-fill{height:100%;border-radius:2px;transition:width .3s,background .3s}
  .btn{width:100%;height:52px;background:#1A5C2A;color:white;border:none;border-radius:12px;font-size:16px;font-weight:700;cursor:pointer;margin-top:8px;-webkit-tap-highlight-color:transparent}
  .btn:active{background:#237533}
  .btn:disabled{background:#B8C9BC;cursor:not-allowed}
  .toast{display:none;margin-top:14px;padding:12px 16px;border-radius:10px;font-size:14px;font-weight:500;text-align:center}
  .toast.success{background:#E8F5EC;color:#1A5C2A;display:block}
  .toast.error{background:#FDEAEA;color:#DC3545;display:block}
  .divider{height:1px;background:#E0E9E2;margin:20px 0}
  .footer{font-size:12px;color:#8A9F90;text-align:center}
</style>
</head>
<body>
<div class="card">
  <div class="logo"><div class="logo-icon">🌱</div><div class="logo-text">MDU<span>MENI</span></div></div>
  <h1>Soil readings input</h1>
  <p class="sub">Enter your soil readings below. The mobile app picks them up automatically.</p>
  <div class="field">
    <label>Soil pH</label>
    <div class="input-row">
      <button class="adj" onclick="adj('ph',-0.1)">−</button>
      <input type="number" id="ph" value="6.1" min="0" max="14" step="0.1" oninput="update()">
      <button class="adj" onclick="adj('ph',0.1)">+</button>
    </div>
    <div class="scale"><div class="scale-fill" id="ph-scale"></div></div>
    <div class="status"><div class="dot" id="ph-dot"></div><span class="status-text" id="ph-status"></span></div>
  </div>
  <div class="field">
    <label>Soil moisture %</label>
    <div class="input-row">
      <button class="adj" onclick="adj('mo',-1)">−</button>
      <input type="number" id="mo" value="62" min="0" max="100" step="1" oninput="update()">
      <button class="adj" onclick="adj('mo',1)">+</button>
    </div>
    <div class="scale"><div class="scale-fill" id="mo-scale"></div></div>
    <div class="status"><div class="dot" id="mo-dot"></div><span class="status-text" id="mo-status"></span></div>
  </div>
  <div class="field">
    <label>Soil temperature °C</label>
    <div class="input-row">
      <button class="adj" onclick="adj('tm',-0.5)">−</button>
      <input type="number" id="tm" value="24" min="0" max="60" step="0.5" oninput="update()">
      <button class="adj" onclick="adj('tm',0.5)">+</button>
    </div>
    <div class="scale"><div class="scale-fill" id="tm-scale"></div></div>
    <div class="status"><div class="dot" id="tm-dot"></div><span class="status-text" id="tm-status"></span></div>
  </div>
  <button class="btn" id="submit-btn" onclick="submit()">Update readings →</button>
  <div class="toast" id="toast"></div>
  <div class="divider"></div>
  <div class="footer">MDUMENI · Intelli-Farming · University of Zimbabwe</div>
</div>
<script>
const PH_RANGES=[{max:5.0,label:'Very acidic — lime urgently needed',color:'#DC3545'},{max:5.5,label:'Acidic — lime recommended',color:'#EF9F27'},{max:6.5,label:'Ideal for most crops',color:'#1A5C2A'},{max:7.5,label:'Neutral — good',color:'#237533'},{max:14,label:'Alkaline — sulphur may help',color:'#EF9F27'}];
const MO_RANGES=[{max:30,label:'Too dry — irrigate now',color:'#DC3545'},{max:40,label:'Low — monitor closely',color:'#EF9F27'},{max:80,label:'Good moisture',color:'#1A5C2A'},{max:100,label:'Waterlogged — improve drainage',color:'#EF9F27'}];
const TM_RANGES=[{max:15,label:'Cold — limits germination',color:'#2563EB'},{max:18,label:'Cool — some crops only',color:'#0ea5e9'},{max:30,label:'Ideal for most crops',color:'#1A5C2A'},{max:35,label:'Warm — watch for drought stress',color:'#EF9F27'},{max:60,label:'Very hot — crop stress',color:'#DC3545'}];
function getRange(val,ranges){return ranges.find(r=>val<r.max)||ranges[ranges.length-1]}
function setStatus(id,val,ranges,min,max){const r=getRange(val,ranges);document.getElementById(id+'-dot').style.background=r.color;document.getElementById(id+'-status').textContent=r.label;document.getElementById(id+'-status').style.color=r.color;const pct=((val-min)/(max-min)*100).toFixed(1);document.getElementById(id+'-scale').style.width=pct+'%';document.getElementById(id+'-scale').style.background=r.color;}
function update(){const ph=parseFloat(document.getElementById('ph').value);const mo=parseFloat(document.getElementById('mo').value);const tm=parseFloat(document.getElementById('tm').value);if(!isNaN(ph)&&ph>=0&&ph<=14)setStatus('ph',ph,PH_RANGES,0,14);if(!isNaN(mo)&&mo>=0&&mo<=100)setStatus('mo',mo,MO_RANGES,0,100);if(!isNaN(tm)&&tm>=0&&tm<=60)setStatus('tm',tm,TM_RANGES,0,60);}
function adj(id,delta){const el=document.getElementById(id);const val=parseFloat(el.value)||0;const step=Math.abs(delta);el.value=(Math.round((val+delta)/step)*step).toFixed(delta%1===0?0:1);update();}
async function submit(){const ph=parseFloat(document.getElementById('ph').value);const mo=parseInt(document.getElementById('mo').value);const tm=parseFloat(document.getElementById('tm').value);if(isNaN(ph)||isNaN(mo)||isNaN(tm)){showToast('Enter all three readings','error');return;}const btn=document.getElementById('submit-btn');btn.disabled=true;btn.textContent='Sending...';try{const res=await fetch('/sensor/reading',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({soil_ph:ph,moisture_pct:mo,temp_c:tm})});if(res.ok){showToast('Readings saved — app will update on next refresh','success');}else{showToast('Server error — try again','error');}}catch(e){showToast('Could not reach server','error');}btn.disabled=false;btn.textContent='Update readings →';}
function showToast(msg,type){const t=document.getElementById('toast');t.textContent=msg;t.className='toast '+type;setTimeout(()=>{t.className='toast'},4000);}
update();
</script>
</body>
</html>"""

# ══ Pydantic Models ════════════════════════════════════════════════════════════

class SensorInput(BaseModel):
    soil_ph:      float = Field(..., ge=0.0, le=14.0)
    moisture_pct: int   = Field(..., ge=0,   le=100)
    temp_c:       float = Field(..., ge=0.0, le=60.0)

class ChatRequest(BaseModel):
    question: str  = Field(..., min_length=1, max_length=2000)
    context:  dict = Field(default_factory=dict)

class RegisterRequest(BaseModel):
    phone_number:   str   = Field(..., description="Zimbabwe phone e.g. 0771234567")
    pin:            str   = Field(..., min_length=4, max_length=4)
    agro_region:    int   = Field(..., ge=1, le=5)
    farm_size_ha:   float = Field(..., gt=0)
    has_irrigation: bool  = False
    budget_level:   str   = Field("low")
    province:       str   = ""
    district:       str   = ""
    language:       str   = "english"

class LoginRequest(BaseModel):
    phone_number: str
    pin:          str = Field(..., min_length=4, max_length=4)

class FarmerSyncRequest(BaseModel):
    farmer_id:    str
    soil_ph:      float
    moisture_pct: int
    temp_c:       float
    device_id:    str = "MANUAL"
    source:       str = "manual"

class YieldRecordRequest(BaseModel):
    farmer_id:          str
    crop_id:            str
    crop_name:          str
    planting_date:      str
    harvest_date:       str
    farm_size_ha:       float
    budget_level:       str   = "low"
    predicted_yield_kg: float = 0
    actual_yield_kg:    float
    total_cost_usd:     float = 0
    gross_revenue_usd:  float = 0
    net_profit_usd:     float = 0
<<<<<<< HEAD
    notes:              str   = ""
=======
    notes:              str = ""

SYSTEM_PROMPT = """You are MDUMENI, a knowledgeable and friendly AI agronomist specialising in Zimbabwean agriculture.

You work with smallholder farmers across Zimbabwe's 5 agro-ecological regions. You know:
- All 30 major Zimbabwean crops: maize, sugar beans, groundnuts, sorghum, pearl millet, cotton, tobacco, soya, sunflower, sesame, cassava, sweet potato, cowpeas, and more
- Zimbabwe's AGRITEX crop management recommendations
- Local product names: AN 34.5%, Compound D, Compound S, Lafarge lime, Bt DiPel, Proclaim, Karate
- Local market prices, GMB procedures, Cottco contracts, Seed Co varieties (ZM521, SC403, SC627)
- Regional rainfall patterns: Region I (>1000mm), II (750-1000mm), III (650-800mm), IV (450-650mm), V (<450mm)
- Soil challenges: acidic granitic soils in Mashonaland, alkaline soils in parts of Matabeleland
- Climate challenges: El Niño droughts, mid-season dry spells, late onset of rains

Always:
- Use the farmer's actual farm data (pH, moisture, crop, region, farm size, budget) in your answer
- Give specific numbers: kg/ha rates, costs in USD, timing in days
- Recommend products available in Zimbabwe
- Keep answers practical and actionable — farmers implement advice the same day
- Be encouraging and respectful
- For critical issues (very low pH, severe pest outbreak), be direct about urgency

Never:
- Give generic answers that ignore the farmer's actual data
- Recommend products not available in Zimbabwe
- Use overly technical language without explanation
- Give advice that contradicts AGRITEX standards without good reason
"""

@app.post("/chat", tags=["AI Chat"])
async def ai_chat(req: ChatRequest):
    """
    Farmer question → Groq Llama 3.3 70B with full farm context.
    Requires GROQ_API_KEY in Render environment variables.
    Free tier: 500,000 tokens/day — more than enough for pilot.
    """
    import os, httpx

    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="AI chat not configured — GROQ_API_KEY missing")

    ctx = req.context
    system_prompt = """You are MDUMENI, an expert AI agronomist for Zimbabwean smallholder farmers.
You give precise, practical advice based on the farmer's actual soil data.
Always mention specific quantities, costs in USD, and Zimbabwean product names.
Keep responses under 120 words. If asked in Shona, reply in Shona."""

    user_message = f"""FARMER DATA:
- Soil pH: {ctx.get('soil_ph', 'unknown')} | Moisture: {ctx.get('moisture_pct', 'unknown')}% | Temp: {ctx.get('temp_c', 'unknown')}°C
- Crop: {ctx.get('active_crop', 'not set')} | Region: {ctx.get('agro_region', 'unknown')} | Farm: {ctx.get('farm_size_ha', 'unknown')} ha
- Budget: {ctx.get('budget_level', 'unknown')} input | Month: {ctx.get('current_month', 'unknown')}

QUESTION: {req.question}"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_message},
                    ],
                    "max_tokens":  300,
                    "temperature": 0.4,
                }
            )
            data = response.json()
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Groq API error {response.status_code}: {data.get('error', {}).get('message', 'Unknown')}"
                )
            answer = data["choices"][0]["message"]["content"]
            return {"response": answer, "answer": answer, "source": "groq-llama3"}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI response timed out — try again")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI chat error: {type(e).__name__}: {str(e)}")


@app.post("/auth/register", tags=["Auth"])
def register(req: RegisterRequest):
    """Register a new farmer with phone number and 4-digit PIN."""
    db  = get_db()
    phone = normalize_phone(req.phone_number)

    # Check if already registered
    existing = db.table("farmers").select("id").eq("phone_number", phone).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Phone number already registered")

    pin_hash = hash_pin(req.pin, phone)

    result = db.table("farmers").insert({
        "phone_number":   phone,
        "pin_hash":       pin_hash,
        "agro_region":    req.agro_region,
        "farm_size_ha":   req.farm_size_ha,
        "has_irrigation": req.has_irrigation,
        "budget_level":   req.budget_level,
        "province":       req.province,
        "district":       req.district,
        "language":       req.language,
        "is_demo":        False,
    }).execute()

    farmer = result.data[0]
    token  = create_token(farmer["id"], phone)

    return {
        "status":    "registered",
        "farmer_id": farmer["id"],
        "token":     token,
        "farmer":    farmer,
    }


@app.post("/auth/login", tags=["Auth"])
def login(req: LoginRequest):
    """Login with phone number and PIN. Returns JWT token."""
    db    = get_db()
    phone = normalize_phone(req.phone_number)

    result = db.table("farmers").select("*").eq("phone_number", phone).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Phone number not found. Register first.")

    farmer = result.data[0]

    if not verify_pin(req.pin, phone, farmer["pin_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect PIN")

    token = create_token(farmer["id"], phone)

    # Load active crop
    crop_result = db.table("active_crops") \
        .select("*").eq("farmer_id", farmer["id"]).eq("is_active", True) \
        .order("created_at", desc=True).limit(1).execute()

    # Load latest sensor reading
    sensor_result = db.table("sensor_readings") \
        .select("*").eq("farmer_id", farmer["id"]) \
        .order("recorded_at", desc=True).limit(1).execute()

    return {
        "status":    "ok",
        "farmer_id": farmer["id"],
        "token":     token,
        "farmer":    farmer,
        "active_crop":    crop_result.data[0] if crop_result.data else None,
        "latest_reading": sensor_result.data[0] if sensor_result.data else None,
    }


@app.get("/auth/me", tags=["Auth"])
def get_me(authorization: str = Header(None)):
    """Get current farmer profile from token."""
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    db     = get_db()
    result = db.table("farmers").select("*").eq("id", farmer_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Farmer not found")

    return result.data[0]


@app.put("/auth/profile", tags=["Auth"])
def update_profile(req: RegisterRequest, authorization: str = Header(None)):
    """Update farmer profile."""
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    db = get_db()
    db.table("farmers").update({
        "agro_region":    req.agro_region,
        "farm_size_ha":   req.farm_size_ha,
        "has_irrigation": req.has_irrigation,
        "budget_level":   req.budget_level,
        "province":       req.province,
        "district":       req.district,
        "language":       req.language,
        "updated_at":     datetime.utcnow().isoformat(),
    }).eq("id", farmer_id).execute()

    return {"status": "updated"}


@app.post("/farmer/crop", tags=["Farmer Data"])
def set_farmer_crop(
    crop_id: str, crop_name: str, planting_date: str,
    authorization: str = Header(None)
):
    """Set the farmer's active crop and planting date."""
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    db = get_db()
    # Deactivate previous crops
    db.table("active_crops").update({"is_active": False}).eq("farmer_id", farmer_id).execute()
    # Insert new
    db.table("active_crops").insert({
        "farmer_id":    farmer_id,
        "crop_id":      crop_id,
        "crop_name":    crop_name,
        "planting_date": planting_date,
        "is_active":    True,
    }).execute()
    return {"status": "ok"}


@app.post("/farmer/reading", tags=["Farmer Data"])
def save_farmer_reading(req: FarmerSyncRequest):
    """Save a sensor reading linked to a specific farmer."""
    db = get_db()
    result = db.table("sensor_readings").insert({
        "farmer_id":   req.farmer_id,
        "device_id":   req.device_id,
        "soil_ph":     req.soil_ph,
        "moisture_pct": req.moisture_pct,
        "temp_c":      req.temp_c,
        "source":      req.source,
    }).execute()
    return {"status": "saved", "id": result.data[0]["id"]}


@app.get("/farmer/readings", tags=["Farmer Data"])
def get_farmer_readings(authorization: str = Header(None), limit: int = 30):
    """Get the farmer's sensor reading history."""
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    db = get_db()
    result = db.table("sensor_readings") \
        .select("*").eq("farmer_id", farmer_id) \
        .order("recorded_at", desc=True).limit(limit).execute()
    return result.data


@app.get("/admin/stats", tags=["Admin"])
def admin_stats():
    """Aggregate pilot statistics — for research dashboard."""
    db = get_db()
    try:
        farmers    = db.table("farmers").select("id", count="exact").eq("is_demo", False).execute()
        readings   = db.table("sensor_readings").select("id", count="exact").execute()
        crops      = db.table("active_crops").select("crop_name").eq("is_active", True).execute()

        crop_counts: dict = {}
        for c in (crops.data or []):
            name = c["crop_name"]
            crop_counts[name] = crop_counts.get(name, 0) + 1

        return {
            "total_farmers":  farmers.count,
            "total_readings": readings.count,
            "active_crops":   crop_counts,
        }
    except Exception as e:
        return {"error": str(e)}


# ── Farmer Auth endpoints ──────────────────────────────────────────────────────


def extract_farmer_id(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    payload = verify_token(token)
    return payload.get("farmer_id") if payload else None

@app.post("/farmer/yield", tags=["Season History"])
def record_yield(req: YieldRecordRequest):
    """Record actual harvest yield — saved to season_history for research analysis."""
    db = get_db()
    result = db.table("season_history").insert({
        "farmer_id":          req.farmer_id,
        "crop_id":            req.crop_id,
        "crop_name":          req.crop_name,
        "planting_date":      req.planting_date,
        "harvest_date":       req.harvest_date,
        "farm_size_ha":       req.farm_size_ha,
        "budget_level":       req.budget_level,
        "predicted_yield_kg": req.predicted_yield_kg,
        "actual_yield_kg":    req.actual_yield_kg,
        "total_cost_usd":     req.total_cost_usd,
        "gross_revenue_usd":  req.gross_revenue_usd,
        "net_profit_usd":     req.net_profit_usd,
        "notes":              req.notes,
    }).execute()
    return {"status": "recorded", "id": result.data[0]["id"]}

@app.get("/farmer/history", tags=["Season History"])
def get_season_history(authorization: str = Header(None)):
    """Get all completed seasons for this farmer."""
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    db = get_db()
    result = db.table("season_history") \
        .select("*").eq("farmer_id", farmer_id) \
        .order("planting_date", desc=True).execute()
    return result.data


@app.get("/debug/auth", tags=["System"])
def debug_auth(authorization: str = Header(None)):
    """Debug endpoint — tests JWT verification. Remove after fix confirmed."""
    import os
    secret = os.environ.get("JWT_SECRET", "NOT_SET")
    if not authorization:
        return {"error": "No Authorization header", "secret_prefix": secret[:8]}
    if not authorization.startswith("Bearer "):
        return {"error": "No Bearer prefix", "received": authorization[:20]}
    token = authorization.split(" ", 1)[1]
    result = verify_token(token)
    return {
        "token_prefix":   token[:20],
        "secret_prefix":  secret[:8],
        "secret_length":  len(secret),
        "verify_result":  result,
        "is_valid":       result is not None,
    }

@app.get("/health", tags=["System"])
def health():
    """Check API health and engine status."""
    return {
        "status":         "ok",
        "service":        "MDUMENI Intelligence Engine",
        "version":        "1.0.0",
        "timestamp":      datetime.utcnow().isoformat() + "Z",
        "engines": {
            "crop_recommendation": "ready",
            "farming_calendar":    "ready",
            "planning":            "ready",
            "pest_disease":        "ready",
        },
        "dataset": {
            "crops":    len(CROPS),
            "regions":  5,
        }
    }


@app.get("/crops", tags=["Dataset"])
def list_crops(type: Optional[str] = None, region: Optional[int] = None):
    """
    List all crops in the dataset.
    Optional filters: type (cereal, legume, vegetable, etc.), region (1–5).
    """
    results = []
    for c in CROPS:
        if type and c["type"] != type:
            continue
        if region and region not in c["agro_regions"]:
            continue
        results.append({
            "id":          c["id"],
            "name":        c["name"],
            "shona":       c["local_names"].get("shona", ""),
            "ndebele":     c["local_names"].get("ndebele", ""),
            "type":        c["type"],
            "regions":     c["agro_regions"],
            "irrigation":  c["irrigation"]["required"],
            "market_usd":  c["market"]["price_usd_per_kg"],
            "demand":      c["market"]["demand"],
        })
    return {"count": len(results), "crops": results}


@app.get("/crops/{crop_id}", tags=["Dataset"])
def get_crop(crop_id: str):
    """Get full agronomic profile for a single crop."""
    crop = CROP_BY_ID.get(crop_id.upper())
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_id}' not found.")
    return crop


# ══════════════════════════════════════════════════════════════════════════════
# ENGINE 1 — CROP RECOMMENDATION
# ══════════════════════════════════════════════════════════════════════════════
>>>>>>> 2b0ebb970cfb988e613c58929dfc8d132d385e0e

class RecommendRequest(BaseModel):
    soil_ph:           float = Field(..., ge=3.0, le=9.0,  description="Soil pH reading from sensor")
    soil_moisture_pct: float = Field(..., ge=0,   le=100,  description="Soil moisture % from sensor")
    soil_temp_c:       float = Field(..., ge=0,   le=50,   description="Soil temperature C from sensor")
    agro_region:       int   = Field(..., ge=1,   le=5,    description="Zimbabwe agro-ecological region (1-5)")
    has_irrigation:    bool  = Field(...,                  description="True if irrigation is available")
    budget_level:      str   = Field(...,                  description="low | medium | high")
    planting_month:    int   = Field(..., ge=1,   le=12,   description="Current or planned planting month")
    farm_size_ha:      Optional[float] = Field(None, gt=0, description="Farm size in hectares (optional)")
    top_n:             int   = Field(5, ge=1, le=10,       description="Number of recommendations to return")

    @field_validator("budget_level")
    @classmethod
    def validate_budget(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("budget_level must be 'low', 'medium', or 'high'")
        return v

    class Config:
        json_schema_extra = {"example": {"soil_ph": 6.1, "soil_moisture_pct": 62, "soil_temp_c": 24, "agro_region": 2, "has_irrigation": False, "budget_level": "low", "planting_month": 11, "farm_size_ha": 2.4, "top_n": 5}}

class CalendarRequest(BaseModel):
    crop_id:             str   = Field(..., description="Crop ID, e.g. CROP_001")
    days_since_planting: int   = Field(..., ge=0, description="Days since planting date (0 = planting day)")
    soil_ph:             float = Field(..., ge=3.0, le=9.0)
    soil_moisture_pct:   float = Field(..., ge=0, le=100)
    soil_temp_c:         float = Field(..., ge=0, le=50)
    has_irrigation:      bool
    budget_level:        str   = Field(...)
    planting_month:      int   = Field(..., ge=1, le=12)
    farm_size_ha:        Optional[float] = Field(None, gt=0)

    @field_validator("budget_level")
    @classmethod
    def validate_budget(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("budget_level must be 'low', 'medium', or 'high'")
        return v

    @field_validator("crop_id")
    @classmethod
    def validate_crop(cls, v):
        if not v: raise ValueError("crop_id cannot be empty")
        return v.upper()

    class Config:
        json_schema_extra = {"example": {"crop_id": "CROP_001", "days_since_planting": 35, "soil_ph": 5.1, "soil_moisture_pct": 43, "soil_temp_c": 29, "has_irrigation": False, "budget_level": "low", "planting_month": 11}}

class PlanRequest(BaseModel):
    crop_id:               str   = Field(..., description="Crop ID, e.g. CROP_001")
    farm_size_ha:          float = Field(..., gt=0, description="Farm size in hectares")
    budget_level:          str   = Field(...)
    has_irrigation:        bool
    planting_month:        int   = Field(..., ge=1, le=12)
    market_price_override: Optional[float] = Field(None, ge=0, description="Override market price USD/kg")

    @field_validator("budget_level")
    @classmethod
    def validate_budget(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("budget_level must be 'low', 'medium', or 'high'")
        return v

    @field_validator("crop_id")
    @classmethod
    def validate_crop(cls, v):
        if not v: raise ValueError("crop_id cannot be empty")
        return v.upper()

    class Config:
        json_schema_extra = {"example": {"crop_id": "CROP_001", "farm_size_ha": 2.4, "budget_level": "low", "has_irrigation": False, "planting_month": 11}}

class ThreatsRequest(BaseModel):
    crop_id: str = Field(..., description="Crop ID, e.g. CROP_001")
    month:   int = Field(..., ge=1, le=12, description="Current month (1-12)")

    @field_validator("crop_id")
    @classmethod
    def validate_crop(cls, v):
        if not v: raise ValueError("crop_id cannot be empty")
        return v.upper()

    class Config:
        json_schema_extra = {"example": {"crop_id": "CROP_001", "month": 11}}

class DiagnoseRequest(BaseModel):
    crop_id:      str       = Field(..., description="Crop ID, e.g. CROP_001")
    symptoms:     list[str] = Field(..., min_length=1, description="List of observed symptom descriptions")
    month:        int       = Field(..., ge=1, le=12)
    budget_level: str       = Field("medium")
    top_n:        int       = Field(3, ge=1, le=5)

    @field_validator("budget_level")
    @classmethod
    def validate_budget(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("budget_level must be 'low', 'medium', or 'high'")
        return v

    @field_validator("crop_id")
    @classmethod
    def validate_crop(cls, v):
        if not v: raise ValueError("crop_id cannot be empty")
        return v.upper()

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, v):
        if not v: raise ValueError("symptoms list cannot be empty")
        return v

    class Config:
        json_schema_extra = {"example": {"crop_id": "CROP_001", "month": 11, "budget_level": "medium", "symptoms": ["holes in leaves", "frass in whorl", "caterpillar in plant"], "top_n": 3}}

class TreatmentRequest(BaseModel):
    pest_disease_id: str   = Field(..., description="e.g. PEST_001 or DIS_014")
    budget_level:    str   = Field(...)
    farm_size_ha:    float = Field(..., gt=0)

    @field_validator("budget_level")
    @classmethod
    def validate_budget(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("budget_level must be 'low', 'medium', or 'high'")
        return v

    class Config:
        json_schema_extra = {"example": {"pest_disease_id": "PEST_001", "budget_level": "medium", "farm_size_ha": 2.4}}

class FullSessionRequest(BaseModel):
    """Full farmer session - runs all four engines in one call."""
    soil_ph:             float = Field(..., ge=3.0, le=9.0)
    soil_moisture_pct:   float = Field(..., ge=0, le=100)
    soil_temp_c:         float = Field(..., ge=0, le=50)
    agro_region:         int   = Field(..., ge=1, le=5)
    has_irrigation:      bool
    budget_level:        str
    planting_month:      int   = Field(..., ge=1, le=12)
    farm_size_ha:        float = Field(..., gt=0)
    active_crop_id:      Optional[str] = None
    days_since_planting: Optional[int] = Field(None, ge=0)
    farmer_id:           Optional[str] = None

    @field_validator("budget_level")
    @classmethod
    def validate_budget(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("budget_level must be 'low', 'medium', or 'high'")
        return v

    class Config:
        json_schema_extra = {"example": {"soil_ph": 6.1, "soil_moisture_pct": 62, "soil_temp_c": 24, "agro_region": 2, "has_irrigation": False, "budget_level": "low", "planting_month": 11, "farm_size_ha": 2.4, "active_crop_id": "CROP_001", "days_since_planting": 35}}

# ══ Auth helper ════════════════════════════════════════════════════════════════

def extract_farmer_id(authorization: str = Header(None)) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    payload = verify_token(token)
    return payload.get("farmer_id") if payload else None

# ══ AI system prompt ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are MDUMENI, an AI farming business advisor for Zimbabwean smallholder farmers.
You combine agronomic knowledge with live market intelligence.

Your knowledge:
- Soil and crop science: pH, moisture, fertiliser rates, planting calendars, pest management
- All 30 major Zimbabwean crops and AGRITEX recommendations
- Zimbabwe market prices: crop sell prices at Mbare Musika, GMB depots, and export buyers
- Input prices: Compound D, AN 34.5%, certified seeds at Windmill, Agrifoods, Seed Co
- Business planning: ROI calculations, break-even analysis, when to sell vs hold
- Zimbabwe context: 5 agro-ecological regions, local product names (ZM521, SC403, SC627, DiPel, Proclaim, Karate)
- Regional rainfall: Region I (>1000mm), II (750-1000mm), III (650-800mm), IV (450-650mm), V (<450mm)
- Market timing: post-harvest (Mar-May) = lowest prices, pre-planting (Sep-Nov) = highest prices

Rules:
- Give specific numbers: prices, quantities, costs in USD
- Reference actual Zimbabwe suppliers and markets by name
- When asked about selling: compare GMB price vs open market vs export buyer
- When asked about inputs: mention cheapest supplier today
- Keep answers under 130 words
- If asked in Shona, reply in Shona
- Be encouraging and respectful"""

# ══ Sensor endpoints ═══════════════════════════════════════════════════════════

@app.get("/input", response_class=HTMLResponse, tags=["Sensor"])
def sensor_input_form():
    """Web form for manually entering soil readings during testing."""
    return HTMLResponse(content=_INPUT_HTML, status_code=200)

@app.post("/sensor/reading", tags=["Sensor"])
def submit_sensor_reading(data: SensorInput, farmer_id: str = None):
    """Accept a manual sensor reading from the web input form."""
    global _latest_reading
    _latest_reading = {
        "device_id":   "WEB-INPUT",
        "soil_ph":      data.soil_ph,
        "moisture_pct": data.moisture_pct,
        "temp_c":       data.temp_c,
        "battery_pct":  100,
        "recorded_at":  datetime.utcnow().isoformat() + "Z",
        "source":       "web-form",
    }
    if farmer_id:
        try:
            db = get_db()
            db.table("sensor_readings").insert({
                "farmer_id": farmer_id, "device_id": "WEB-INPUT",
                "soil_ph": data.soil_ph, "moisture_pct": data.moisture_pct,
                "temp_c": data.temp_c, "source": "web-form",
            }).execute()
        except Exception:
            pass
    return {"status": "ok", "reading": _latest_reading}

@app.get("/sensor/latest", tags=["Sensor"])
def get_latest_reading():
    """Return the most recent sensor reading - polled by the mobile app."""
    return _latest_reading

# ══ Auth endpoints ═════════════════════════════════════════════════════════════

@app.post("/auth/register", tags=["Auth"])
def register(req: RegisterRequest):
    """Register a new farmer with phone number and 4-digit PIN."""
    db    = get_db()
    phone = normalize_phone(req.phone_number)
    existing = db.table("farmers").select("id").eq("phone_number", phone).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Phone number already registered")
    result = db.table("farmers").insert({
        "phone_number": phone, "pin_hash": hash_pin(req.pin, phone),
        "agro_region": req.agro_region, "farm_size_ha": req.farm_size_ha,
        "has_irrigation": req.has_irrigation, "budget_level": req.budget_level,
        "province": req.province, "district": req.district,
        "language": req.language, "is_demo": False,
    }).execute()
    farmer = result.data[0]
    token  = create_token(farmer["id"], phone)
    return {"status": "registered", "farmer_id": farmer["id"], "token": token, "farmer": farmer}

@app.post("/auth/login", tags=["Auth"])
def login(req: LoginRequest):
    """Login with phone number and PIN. Returns JWT token."""
    db    = get_db()
    phone = normalize_phone(req.phone_number)
    result = db.table("farmers").select("*").eq("phone_number", phone).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Phone number not found. Register first.")
    farmer = result.data[0]
    if not verify_pin(req.pin, phone, farmer["pin_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect PIN")
    token    = create_token(farmer["id"], phone)
    crop_r   = db.table("active_crops").select("*").eq("farmer_id", farmer["id"]).eq("is_active", True).order("created_at", desc=True).limit(1).execute()
    sensor_r = db.table("sensor_readings").select("*").eq("farmer_id", farmer["id"]).order("recorded_at", desc=True).limit(1).execute()
    return {
        "status": "ok", "farmer_id": farmer["id"], "token": token, "farmer": farmer,
        "active_crop":    crop_r.data[0]   if crop_r.data   else None,
        "latest_reading": sensor_r.data[0] if sensor_r.data else None,
    }

@app.get("/auth/me", tags=["Auth"])
def get_me(authorization: str = Header(None)):
    """Get current farmer profile from token."""
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    result = get_db().table("farmers").select("*").eq("id", farmer_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return result.data[0]

@app.put("/auth/profile", tags=["Auth"])
def update_profile(req: RegisterRequest, authorization: str = Header(None)):
    """Update farmer profile."""
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    get_db().table("farmers").update({
        "agro_region": req.agro_region, "farm_size_ha": req.farm_size_ha,
        "has_irrigation": req.has_irrigation, "budget_level": req.budget_level,
        "province": req.province, "district": req.district, "language": req.language,
    }).eq("id", farmer_id).execute()
    return {"status": "updated"}

# ══ Farmer data endpoints ══════════════════════════════════════════════════════

@app.post("/farmer/crop", tags=["Farmer Data"])
def set_farmer_crop(
    crop_id: str, crop_name: str, planting_date: str,
    authorization: str = Header(None)
):
    """Set the farmer's active crop and planting date."""
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    db = get_db()
    db.table("active_crops").update({"is_active": False}).eq("farmer_id", farmer_id).execute()
    db.table("active_crops").insert({
        "farmer_id": farmer_id, "crop_id": crop_id,
        "crop_name": crop_name, "planting_date": planting_date, "is_active": True,
    }).execute()
    return {"status": "ok"}

@app.post("/farmer/reading", tags=["Farmer Data"])
def save_farmer_reading(req: FarmerSyncRequest):
    """Save a sensor reading linked to a specific farmer."""
    db = get_db()
    result = db.table("sensor_readings").insert({
        "farmer_id": req.farmer_id, "device_id": req.device_id,
        "soil_ph": req.soil_ph, "moisture_pct": req.moisture_pct,
        "temp_c": req.temp_c, "source": req.source,
    }).execute()
    return {"status": "saved", "id": result.data[0]["id"]}

@app.get("/farmer/readings", tags=["Farmer Data"])
def get_farmer_readings(authorization: str = Header(None), limit: int = 30):
    """Get the farmer's sensor reading history."""
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    result = get_db().table("sensor_readings").select("*").eq("farmer_id", farmer_id).order("recorded_at", desc=True).limit(limit).execute()
    return result.data

@app.post("/farmer/yield", tags=["Season History"])
def record_yield(req: YieldRecordRequest):
    """Record actual harvest yield - saved to season_history for research analysis."""
    db = get_db()
    result = db.table("season_history").insert({
        "farmer_id": req.farmer_id, "crop_id": req.crop_id, "crop_name": req.crop_name,
        "planting_date": req.planting_date, "harvest_date": req.harvest_date,
        "farm_size_ha": req.farm_size_ha, "budget_level": req.budget_level,
        "predicted_yield_kg": req.predicted_yield_kg, "actual_yield_kg": req.actual_yield_kg,
        "total_cost_usd": req.total_cost_usd, "gross_revenue_usd": req.gross_revenue_usd,
        "net_profit_usd": req.net_profit_usd, "notes": req.notes,
    }).execute()
    return {"status": "recorded", "id": result.data[0]["id"]}

@app.get("/farmer/history", tags=["Season History"])
def get_season_history(authorization: str = Header(None)):
    """Get all completed seasons for this farmer."""
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    result = get_db().table("season_history").select("*").eq("farmer_id", farmer_id).order("planting_date", desc=True).execute()
    return result.data

# ══ Admin ══════════════════════════════════════════════════════════════════════

@app.get("/admin/stats", tags=["Admin"])
def admin_stats():
    """Aggregate pilot statistics - for research dashboard."""
    db = get_db()
    try:
        farmers  = db.table("farmers").select("id", count="exact").eq("is_demo", False).execute()
        readings = db.table("sensor_readings").select("id", count="exact").execute()
        crops    = db.table("active_crops").select("crop_name").eq("is_active", True).execute()
        crop_counts: dict = {}
        for c in (crops.data or []):
            n = c["crop_name"]
            crop_counts[n] = crop_counts.get(n, 0) + 1
        return {"total_farmers": farmers.count, "total_readings": readings.count, "active_crops": crop_counts}
    except Exception as e:
        return {"error": str(e)}

# ══ AI Chat ════════════════════════════════════════════════════════════════════

@app.post("/chat", tags=["AI Chat"])
async def ai_chat(req: ChatRequest):
    """
    Farmer question to Groq Llama 3.3 70B with full farm context + live market prices.
    Requires GROQ_API_KEY in Render environment variables.
    Free tier: 500,000 tokens/day.
    """
    import httpx
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="AI chat not configured - GROQ_API_KEY missing")

    market_context = ""
    try:
        db_client = get_db()
        price_r = db_client.table("market_prices") \
            .select("crop_name, price_usd_kg, markets(name)") \
            .gte("price_date", str(date.today() - timedelta(days=3))) \
            .order("price_usd_kg", desc=True).limit(8).execute()
        if price_r.data:
            prices = [
                f"{p['crop_name']}: ${p['price_usd_kg']:.3f}/kg at {p.get('markets', {}).get('name', 'market')}"
                for p in price_r.data[:6]
            ]
            market_context = "\nTODAY'S MARKET PRICES:\n" + "\n".join(prices)
    except Exception:
        pass

    ctx = req.context
    user_message = f"""FARMER DATA:
- Soil pH: {ctx.get('soil_ph','unknown')} | Moisture: {ctx.get('moisture_pct','unknown')}% | Temp: {ctx.get('temp_c','unknown')}C
- Crop: {ctx.get('active_crop','not set')} | Region: {ctx.get('agro_region','unknown')} | Farm: {ctx.get('farm_size_ha','unknown')} ha
- Budget: {ctx.get('budget_level','unknown')} input | Month: {ctx.get('current_month','unknown')}{market_context}

QUESTION: {req.question}"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": user_message},
                    ],
                    "max_tokens": 300, "temperature": 0.4,
                }
            )
            data = response.json()
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail=f"Groq error {response.status_code}: {data.get('error',{}).get('message','Unknown')}")
            answer = data["choices"][0]["message"]["content"]
            return {"response": answer, "answer": answer, "source": "groq-llama3"}
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI response timed out - try again")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI chat error: {type(e).__name__}: {str(e)}")

# ══ System ══════════════════════════════════════════════════════════════════════

@app.get("/debug/auth", tags=["System"])
def debug_auth(authorization: str = Header(None)):
    """Debug endpoint - tests JWT verification."""
    secret = os.environ.get("JWT_SECRET", "NOT_SET")
    if not authorization:
        return {"error": "No Authorization header", "secret_prefix": secret[:8]}
    if not authorization.startswith("Bearer "):
        return {"error": "No Bearer prefix", "received": authorization[:20]}
    token  = authorization.split(" ", 1)[1]
    result = verify_token(token)
    return {"token_prefix": token[:20], "secret_prefix": secret[:8], "secret_length": len(secret), "verify_result": result, "is_valid": result is not None}

@app.get("/health", tags=["System"])
def health():
    """Check API health and engine status."""
    return {
        "status": "ok", "service": "MDUMENI Intelligence Engine",
        "version": "2.0.0", "timestamp": datetime.utcnow().isoformat() + "Z",
        "market_intelligence": True,
        "engines": {"crop_recommendation": "ready", "farming_calendar": "ready", "planning": "ready", "pest_disease": "ready", "market_prices": "ready"},
        "dataset": {"crops": len(CROPS), "regions": 5},
    }

# ══ Dataset endpoints ══════════════════════════════════════════════════════════

@app.get("/crops", tags=["Dataset"])
def list_crops(type: Optional[str] = None, region: Optional[int] = None):
    """
    List all crops in the dataset.
    Optional filters: type (cereal, legume, vegetable, etc.), region (1-5).
    """
    results = []
    for c in CROPS:
        if type   and c["type"] != type:                continue
        if region and region not in c["agro_regions"]:  continue
        results.append({
            "id": c["id"], "name": c["name"],
            "shona":   c["local_names"].get("shona",   ""),
            "ndebele": c["local_names"].get("ndebele", ""),
            "type": c["type"], "regions": c["agro_regions"],
            "irrigation": c["irrigation"]["required"],
            "market_usd": c["market"]["price_usd_per_kg"],
            "demand":     c["market"]["demand"],
        })
    return {"count": len(results), "crops": results}

@app.get("/crops/{crop_id}", tags=["Dataset"])
def get_crop(crop_id: str):
    """Get full agronomic profile for a single crop."""
    crop = CROP_BY_ID.get(crop_id.upper())
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_id}' not found.")
    return crop

# ══ Engine endpoints ═══════════════════════════════════════════════════════════

@app.post("/recommend", tags=["Crop Recommendation"],
          summary="Get ranked crop recommendations based on soil and farmer profile")
def recommend(req: RecommendRequest):
    """
    Scores all 30 Zimbabwean crops against live sensor readings and farmer profile.
    Returns a ranked list with score breakdowns, seed varieties, and agronomic notes.
    Weights: Region fit 25% | Soil pH 20% | Moisture 20% | Temperature 15% | Irrigation 10% | Budget 10%
    """
    result = recommend_crops(CropInput(
        soil_ph=req.soil_ph, soil_moisture_pct=req.soil_moisture_pct,
        soil_temp_c=req.soil_temp_c, agro_region=req.agro_region,
        has_irrigation=req.has_irrigation, budget_level=req.budget_level,
        planting_month=req.planting_month, farm_size_ha=req.farm_size_ha,
    ), top_n=req.top_n)
    return result.to_dict()

@app.post("/calendar", tags=["Farming Calendar"],
          summary="Get daily farming guidance and sensor-triggered alerts")
def calendar(req: CalendarRequest):
    """
    Returns today's farming tasks, upcoming tasks for the next 7 days,
    and real-time sensor-triggered alerts for the active crop phase.
    Tasks filtered by budget level - low-input gets organic alternatives.
    """
    result = get_daily_guidance(CalendarInput(
        crop_id=req.crop_id, days_since_planting=req.days_since_planting,
        soil_ph=req.soil_ph, soil_moisture_pct=req.soil_moisture_pct,
        soil_temp_c=req.soil_temp_c, has_irrigation=req.has_irrigation,
        budget_level=req.budget_level, planting_month=req.planting_month,
        farm_size_ha=req.farm_size_ha,
    ))
    return result.to_dict()

@app.post("/plan", tags=["Planning"],
          summary="Generate a full financial plan: yield, costs, profit, break-even")
def plan(req: PlanRequest):
    """
    Generates a complete pre-season financial plan including expected yield,
    full cost breakdown, gross revenue, net profit, ROI%, and break-even yield.
    Scenario comparison: low / medium / high input side-by-side.
    """
    result = generate_plan(PlanningInput(
        crop_id=req.crop_id, farm_size_ha=req.farm_size_ha,
        budget_level=req.budget_level, has_irrigation=req.has_irrigation,
        planting_month=req.planting_month,
        market_price_override=req.market_price_override,
    ))
    return result.to_dict()

@app.post("/threats", tags=["Pest & Disease"],
          summary="Get all active pest and disease threats for a crop in the current month")
def threats(req: ThreatsRequest):
    """
    Returns all pests and diseases that affect this crop, ranked by severity.
    Each threat includes symptom previews, treatment count, and organic options flag.
    """
    return crop_threats(req.crop_id, req.month)

@app.post("/diagnose", tags=["Pest & Disease"],
          summary="Match reported symptoms to pest/disease diagnoses with confidence scores")
def diagnose_endpoint(req: DiagnoseRequest):
    """
    Matches farmer-reported symptoms against the pest and disease database.
    Returns ranked diagnoses with confidence scores, matched symptoms, and treatment options.
    Urgency levels: immediate | monitor | low
    """
    return diagnose(
        crop_id=req.crop_id, symptoms=req.symptoms,
        month=req.month, budget_level=req.budget_level, top_n=req.top_n,
    )

@app.post("/treatment", tags=["Pest & Disease"],
          summary="Get a complete, costed treatment plan for a confirmed pest or disease")
def treatment(req: TreatmentRequest):
    """
    Returns a complete treatment plan with recommended products, rates,
    timing, estimated costs, and safety reminders. Costs scale with farm_size_ha.
    """
    p = get_treatment_plan(
        pest_disease_id=req.pest_disease_id.upper(),
        budget_level=req.budget_level,
        farm_size_ha=req.farm_size_ha,
    )
    return p.to_dict()

@app.post("/session", tags=["Composite"],
          summary="Full farmer session - runs all four engines in one call")
def full_session(req: FullSessionRequest):
    """
    Single endpoint for the mobile app's daily refresh.
    Always returns crop recommendations.
    If active_crop_id + days_since_planting provided, also returns
    daily calendar, crop threats, and financial plan.
    """
    response = {"generated_at": datetime.utcnow().isoformat() + "Z", "from_cache": False}

    try:
        recs = recommend_crops(CropInput(
            soil_ph=req.soil_ph, soil_moisture_pct=req.soil_moisture_pct,
            soil_temp_c=req.soil_temp_c, agro_region=req.agro_region,
            has_irrigation=req.has_irrigation, budget_level=req.budget_level,
            planting_month=req.planting_month, farm_size_ha=req.farm_size_ha,
        ), top_n=5)
        response["crop_recommendations"] = recs.to_dict()
    except Exception as e:
        response["crop_recommendations"] = {"error": str(e)}

    crop_id = req.active_crop_id.upper() if req.active_crop_id else None
    dsp     = req.days_since_planting

    if crop_id and crop_id in CROP_BY_ID:
        if dsp is not None:
            try:
                cal = get_daily_guidance(CalendarInput(
                    crop_id=crop_id, days_since_planting=dsp,
                    soil_ph=req.soil_ph, soil_moisture_pct=req.soil_moisture_pct,
                    soil_temp_c=req.soil_temp_c, has_irrigation=req.has_irrigation,
                    budget_level=req.budget_level, planting_month=req.planting_month,
                    farm_size_ha=req.farm_size_ha,
                ))
                response["daily_calendar"] = cal.to_dict()
            except Exception as e:
                response["daily_calendar"] = {"error": str(e)}

        try:
            response["crop_threats"] = crop_threats(crop_id, req.planting_month)
        except Exception as e:
            response["crop_threats"] = {"error": str(e)}

        try:
            p = generate_plan(PlanningInput(
                crop_id=crop_id, farm_size_ha=req.farm_size_ha,
                budget_level=req.budget_level, has_irrigation=req.has_irrigation,
                planting_month=req.planting_month,
            ))
            response["crop_plan"] = p.to_dict()
        except Exception as e:
            response["crop_plan"] = {"error": str(e)}

    if req.farmer_id:
        try:
            get_db().table("sensor_readings").insert({
                "farmer_id": req.farmer_id, "device_id": "SESSION",
                "soil_ph": req.soil_ph, "moisture_pct": req.soil_moisture_pct,
                "temp_c": req.soil_temp_c, "source": "session",
            }).execute()
        except Exception:
            pass

    return response

# ══ Entry point ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print("\nMDUMENI Intelligence Engine API v2.0.0")
    print(f"Crops loaded: {len(CROPS)}")
<<<<<<< HEAD
    print("Market intelligence: enabled")
    print("Starting on http://mdumeni-api.onrender.com")
    print("Swagger docs: http://mdumeni-api.onrender.com/docs\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
=======
    print("Starting on http://mdumeni-api.onrender.com")
    print("Swagger docs: http://mdumeni-api.onrender.com/docs\n")
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)
>>>>>>> 2b0ebb970cfb988e613c58929dfc8d132d385e0e
