"""
MDUMENI — Unified FastAPI Integration Layer
=============================================
Single API that exposes all four intelligence engines:

  Engine 1 — Crop Recommendation
  Engine 2 — Farming Calendar
  Engine 3 — Planning
  Engine 4 — Pest & Disease

All endpoints follow the same pattern:
  - POST body with JSON payload
  - Validated input with clear error messages
  - Structured JSON response
  - Health check at /health

Base URL:   http://localhost:8000
Docs:       http://localhost:8000/docs  (Swagger UI — auto-generated)

Run:
    pip install fastapi uvicorn
    uvicorn api_main:app --reload --port 8000

Or production:
    gunicorn api_main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

Offline fallback:
    The Flask api.py in /crop_engine/ works without FastAPI if uvicorn
    is unavailable. This file is the production integration layer.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Request, Header
from typing import Optional
from db import get_db
from auth import hash_pin, verify_pin, create_token, verify_token, normalize_phone
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# ── Import all four engines ───────────────────────────────────────────────────
from crop_engine.recommender    import recommend_crops, CropInput
from calendar_engine.engine     import get_daily_guidance, CalendarInput
from planning_engine.engine     import generate_plan, PlanningInput
from pest_engine.engine         import crop_threats, diagnose, get_treatment_plan
from crop_engine.crop_dataset   import CROPS, CROP_BY_ID


# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "MDUMENI Intelligence Engine API",
    description = "AI agronomist for Zimbabwe — crop recommendation, farming calendar, planning, and pest/disease diagnosis.",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],  # tighten in production
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)


# ── Global error handler ──────────────────────────────────────────────────────
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"error": "Validation error", "detail": str(exc)})

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal engine error", "detail": str(exc)})


# ══════════════════════════════════════════════════════════════════════════════
# HEALTH & INFO
# ══════════════════════════════════════════════════════════════════════════════


# ── Web input form HTML ──────────────────────────────────────────────────────
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
  .btn{width:100%;height:52px;background:#1A5C2A;color:white;border:none;border-radius:12px;font-size:16px;font-weight:700;cursor:pointer;margin-top:8px;transition:background .2s;-webkit-tap-highlight-color:transparent}
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
  <div class="logo">
    <div class="logo-icon">🌱</div>
    <div class="logo-text">MDU<span>MENI</span></div>
  </div>
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

function setStatus(id,val,ranges,min,max){
  const r=getRange(val,ranges);
  document.getElementById(id+'-dot').style.background=r.color;
  document.getElementById(id+'-status').textContent=r.label;
  document.getElementById(id+'-status').style.color=r.color;
  const pct=((val-min)/(max-min)*100).toFixed(1);
  document.getElementById(id+'-scale').style.width=pct+'%';
  document.getElementById(id+'-scale').style.background=r.color;
}

function update(){
  const ph=parseFloat(document.getElementById('ph').value);
  const mo=parseFloat(document.getElementById('mo').value);
  const tm=parseFloat(document.getElementById('tm').value);
  if(!isNaN(ph)&&ph>=0&&ph<=14) setStatus('ph',ph,PH_RANGES,0,14);
  if(!isNaN(mo)&&mo>=0&&mo<=100) setStatus('mo',mo,MO_RANGES,0,100);
  if(!isNaN(tm)&&tm>=0&&tm<=60) setStatus('tm',tm,TM_RANGES,0,60);
}

function adj(id,delta){
  const el=document.getElementById(id);
  const val=parseFloat(el.value)||0;
  const step=Math.abs(delta);
  el.value=(Math.round((val+delta)/step)*step).toFixed(delta%1===0?0:1);
  update();
}

async function submit(){
  const ph=parseFloat(document.getElementById('ph').value);
  const mo=parseInt(document.getElementById('mo').value);
  const tm=parseFloat(document.getElementById('tm').value);
  if(isNaN(ph)||isNaN(mo)||isNaN(tm)){showToast('Enter all three readings','error');return;}
  const btn=document.getElementById('submit-btn');
  btn.disabled=true;btn.textContent='Sending...';
  try{
    const res=await fetch('/sensor/reading',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({soil_ph:ph,moisture_pct:mo,temp_c:tm})});
    if(res.ok){
      showToast('✅ Readings saved — app will update on next refresh','success');
    } else {
      showToast('Server error — try again','error');
    }
  }catch(e){
    showToast('Could not reach server','error');
  }
  btn.disabled=false;btn.textContent='Update readings →';
}

function showToast(msg,type){
  const t=document.getElementById('toast');
  t.textContent=msg;t.className='toast '+type;
  setTimeout(()=>{t.className='toast'},4000);
}

update();
</script>
</body>
</html>"""

# ── Web sensor input form ─────────────────────────────────────────────────────

class SensorInput(BaseModel):
    soil_ph:      float = Field(..., ge=0.0, le=14.0)
    moisture_pct: int   = Field(..., ge=0,   le=100)
    temp_c:       float = Field(..., ge=0.0, le=60.0)

@app.post("/sensor/reading", tags=["Sensor"])
def submit_sensor_reading(data: SensorInput, farmer_id: str = None):
    """Accept a manual sensor reading from the web input form."""
    global _latest_reading
    _latest_reading = {
        "device_id":    "WEB-INPUT",
        "soil_ph":       data.soil_ph,
        "moisture_pct":  data.moisture_pct,
        "temp_c":        data.temp_c,
        "battery_pct":   100,
        "recorded_at":   datetime.utcnow().isoformat() + "Z",
        "source":        "web-form",
    }
    # Also persist to Supabase if farmer_id provided
    if farmer_id:
        try:
            db = get_db()
            db.table("sensor_readings").insert({
                "farmer_id": farmer_id, "device_id": "WEB-INPUT",
                "soil_ph": data.soil_ph, "moisture_pct": data.moisture_pct,
                "temp_c": data.temp_c, "source": "web-form",
            }).execute()
        except Exception:
            pass  # Don't fail if DB unavailable
    return {"status": "ok", "reading": _latest_reading}


@app.get("/sensor/latest", tags=["Sensor"])
def get_latest_reading():
    """Return the most recent sensor reading — polled by the mobile app."""
    return _latest_reading


@app.get("/input", response_class=HTMLResponse, tags=["Sensor"])
def sensor_input_form():
    """Web form for manually entering soil readings during testing."""
    return HTMLResponse(content=_INPUT_HTML, status_code=200)


# ── AI Chat endpoint ─────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    context:  dict = Field(default_factory=dict)

class RegisterRequest(BaseModel):
    phone_number: str = Field(..., description="Zimbabwe phone e.g. 0771234567")
    pin:          str = Field(..., min_length=4, max_length=4)
    agro_region:  int = Field(..., ge=1, le=5)
    farm_size_ha: float = Field(..., gt=0)
    has_irrigation: bool = False
    budget_level: str = Field("low")
    province:     str = ""
    district:     str = ""
    language:     str = "english"

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
    planting_date:      str          # ISO date string
    harvest_date:       str          # ISO date string
    farm_size_ha:       float
    budget_level:       str = "low"
    predicted_yield_kg: float = 0
    actual_yield_kg:    float
    total_cost_usd:     float = 0
    gross_revenue_usd:  float = 0
    net_profit_usd:     float = 0
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
    farmer_id = get_farmer_id(authorization)
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
    farmer_id = get_farmer_id(authorization)
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
    farmer_id = get_farmer_id(authorization)
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
def save_farmer_reading(req: SyncRequest):
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
    farmer_id = get_farmer_id(authorization)
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

@app.post("/auth/register", tags=["Auth"])
def register(req: RegisterRequest):
    db    = get_db()
    phone = normalize_phone(req.phone_number)
    existing = db.table("farmers").select("id").eq("phone_number", phone).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Phone number already registered")
    pin_hash = hash_pin(req.pin, phone)
    result = db.table("farmers").insert({
        "phone_number": phone, "pin_hash": pin_hash,
        "agro_region": req.agro_region, "farm_size_ha": req.farm_size_ha,
        "has_irrigation": req.has_irrigation, "budget_level": req.budget_level,
        "province": req.province, "district": req.district,
        "language": req.language, "is_demo": False,
    }).execute()
    farmer = result.data[0]
    return {"status": "registered", "farmer_id": farmer["id"],
            "token": create_token(farmer["id"], phone), "farmer": farmer}

@app.post("/auth/login", tags=["Auth"])
def login(req: LoginRequest):
    db    = get_db()
    phone = normalize_phone(req.phone_number)
    result = db.table("farmers").select("*").eq("phone_number", phone).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Phone number not found. Register first.")
    farmer = result.data[0]
    if not verify_pin(req.pin, phone, farmer["pin_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect PIN")
    token = create_token(farmer["id"], phone)
    crop_r   = db.table("active_crops").select("*").eq("farmer_id", farmer["id"]).eq("is_active", True).order("created_at", desc=True).limit(1).execute()
    sensor_r = db.table("sensor_readings").select("*").eq("farmer_id", farmer["id"]).order("recorded_at", desc=True).limit(1).execute()
    return {"status": "ok", "farmer_id": farmer["id"], "token": token,
            "farmer": farmer,
            "active_crop":    crop_r.data[0]    if crop_r.data    else None,
            "latest_reading": sensor_r.data[0]  if sensor_r.data  else None}

@app.get("/auth/me", tags=["Auth"])
def get_me(authorization: str = Header(None)):
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    db = get_db()
    result = db.table("farmers").select("*").eq("id", farmer_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return result.data[0]

@app.put("/auth/profile", tags=["Auth"])
def update_profile(req: RegisterRequest, authorization: str = Header(None)):
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    db = get_db()
    db.table("farmers").update({
        "agro_region": req.agro_region, "farm_size_ha": req.farm_size_ha,
        "has_irrigation": req.has_irrigation, "budget_level": req.budget_level,
        "province": req.province, "district": req.district, "language": req.language,
    }).eq("id", farmer_id).execute()
    return {"status": "updated"}

@app.post("/farmer/crop", tags=["Farmer Data"])
def set_farmer_crop(crop_id: str, crop_name: str, planting_date: str,
                    authorization: str = Header(None)):
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
    db = get_db()
    result = db.table("sensor_readings").insert({
        "farmer_id": req.farmer_id, "device_id": req.device_id,
        "soil_ph": req.soil_ph, "moisture_pct": req.moisture_pct,
        "temp_c": req.temp_c, "source": req.source,
    }).execute()
    return {"status": "saved", "id": result.data[0]["id"]}

@app.get("/farmer/readings", tags=["Farmer Data"])
def get_farmer_readings(authorization: str = Header(None), limit: int = 30):
    farmer_id = extract_farmer_id(authorization)
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    db = get_db()
    result = db.table("sensor_readings").select("*").eq("farmer_id", farmer_id).order("recorded_at", desc=True).limit(limit).execute()
    return result.data

@app.get("/admin/stats", tags=["Admin"])
def admin_stats():
    db = get_db()
    try:
        farmers  = db.table("farmers").select("id", count="exact").eq("is_demo", False).execute()
        readings = db.table("sensor_readings").select("id", count="exact").execute()
        crops    = db.table("active_crops").select("crop_name").eq("is_active", True).execute()
        crop_counts: dict = {}
        for c in (crops.data or []):
            n = c["crop_name"]
            crop_counts[n] = crop_counts.get(n, 0) + 1
        return {"total_farmers": farmers.count, "total_readings": readings.count,
                "active_crops": crop_counts}
    except Exception as e:
        return {"error": str(e)}


# ── Yield recording & Season history ──────────────────────────────────────────

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

class RecommendRequest(BaseModel):
    soil_ph:           float = Field(..., ge=3.0, le=9.0,   description="Soil pH reading from sensor")
    soil_moisture_pct: float = Field(..., ge=0,   le=100,   description="Soil moisture % from sensor")
    soil_temp_c:       float = Field(..., ge=0,   le=50,    description="Soil temperature °C from sensor")
    agro_region:       int   = Field(..., ge=1,   le=5,     description="Zimbabwe agro-ecological region (1–5)")
    has_irrigation:    bool  = Field(...,                   description="True if irrigation is available")
    budget_level:      str   = Field(...,                   description="low | medium | high")
    planting_month:    int   = Field(..., ge=1,   le=12,    description="Current or planned planting month")
    farm_size_ha:      Optional[float] = Field(None, gt=0,  description="Farm size in hectares (optional)")
    top_n:             int   = Field(5, ge=1, le=10,        description="Number of recommendations to return")

    @field_validator("budget_level")
    @classmethod
    def validate_budget(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("budget_level must be 'low', 'medium', or 'high'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "soil_ph": 6.1, "soil_moisture_pct": 62, "soil_temp_c": 24,
                "agro_region": 2, "has_irrigation": False,
                "budget_level": "low", "planting_month": 11,
                "farm_size_ha": 2.4, "top_n": 5
            }
        }


@app.post("/recommend", tags=["Crop Recommendation"],
          summary="Get ranked crop recommendations based on soil and farmer profile")
def recommend(req: RecommendRequest):
    """
    Scores all 30 Zimbabwean crops against live sensor readings and
    farmer profile. Returns a ranked list of viable crops with score
    breakdowns, selected seed varieties, and agronomic notes.

    **Weights:** Region fit 25% · Soil pH 20% · Moisture 20% · Temperature 15% · Irrigation 10% · Budget 10%

    Hard disqualifiers remove crops that physically can't survive conditions
    (wrong region, pH out of range, full-irrigation crop without water).
    """
    inp = CropInput(
        soil_ph           = req.soil_ph,
        soil_moisture_pct = req.soil_moisture_pct,
        soil_temp_c       = req.soil_temp_c,
        agro_region       = req.agro_region,
        has_irrigation    = req.has_irrigation,
        budget_level      = req.budget_level,
        planting_month    = req.planting_month,
        farm_size_ha      = req.farm_size_ha,
    )
    result = recommend_crops(inp, top_n=req.top_n)
    return result.to_dict()


# ══════════════════════════════════════════════════════════════════════════════
# ENGINE 2 — FARMING CALENDAR
# ══════════════════════════════════════════════════════════════════════════════

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
        if not v:
            raise ValueError("crop_id cannot be empty")
        return v.upper()

    class Config:
        json_schema_extra = {
            "example": {
                "crop_id": "CROP_001", "days_since_planting": 35,
                "soil_ph": 5.1, "soil_moisture_pct": 43, "soil_temp_c": 29,
                "has_irrigation": False, "budget_level": "low",
                "planting_month": 11
            }
        }


@app.post("/calendar", tags=["Farming Calendar"],
          summary="Get daily farming guidance and sensor-triggered alerts")
def calendar(req: CalendarRequest):
    """
    Returns today's farming tasks, upcoming tasks for the next 7 days,
    and real-time sensor-triggered alerts for the active crop phase.

    Tasks are filtered by budget level — low-input farmers get organic
    alternatives, high-input farmers get commercial fertiliser schedules.

    Sensor alerts fire when readings cross phase-specific thresholds
    (e.g. critical moisture warning during pollination, pH alert during
    vegetative growth).
    """
    inp = CalendarInput(
        crop_id            = req.crop_id,
        days_since_planting= req.days_since_planting,
        soil_ph            = req.soil_ph,
        soil_moisture_pct  = req.soil_moisture_pct,
        soil_temp_c        = req.soil_temp_c,
        has_irrigation     = req.has_irrigation,
        budget_level       = req.budget_level,
        planting_month     = req.planting_month,
        farm_size_ha       = req.farm_size_ha,
    )
    result = get_daily_guidance(inp)
    return result.to_dict()


# ══════════════════════════════════════════════════════════════════════════════
# ENGINE 3 — PLANNING
# ══════════════════════════════════════════════════════════════════════════════

class PlanRequest(BaseModel):
    crop_id:              str   = Field(..., description="Crop ID, e.g. CROP_001")
    farm_size_ha:         float = Field(..., gt=0, description="Farm size in hectares")
    budget_level:         str   = Field(...)
    has_irrigation:       bool
    planting_month:       int   = Field(..., ge=1, le=12)
    market_price_override: Optional[float] = Field(None, ge=0,
        description="Override market price USD/kg (uses dataset default if omitted)")

    @field_validator("budget_level")
    @classmethod
    def validate_budget(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("budget_level must be 'low', 'medium', or 'high'")
        return v

    @field_validator("crop_id")
    @classmethod
    def validate_crop(cls, v):
        if not v:
            raise ValueError("crop_id cannot be empty")
        return v.upper()

    class Config:
        json_schema_extra = {
            "example": {
                "crop_id": "CROP_001", "farm_size_ha": 2.4,
                "budget_level": "low", "has_irrigation": False,
                "planting_month": 11
            }
        }


@app.post("/plan", tags=["Planning"],
          summary="Generate a full financial plan: yield, costs, profit, break-even")
def plan(req: PlanRequest):
    """
    Generates a complete pre-season financial plan including:
    - Expected yield (conservative 85% factor applied)
    - Full cost breakdown: seed, fertiliser, labour, irrigation, chemicals, contingency
    - Gross revenue, net profit, ROI %, profit per hectare
    - Break-even yield and margin of safety
    - Harvest plan: timing, storage, market guidance, rotation suggestion
    - Scenario comparison: low / medium / high input side-by-side

    All values in USD. Labour uses Zimbabwe smallholder rates ($5/day).
    Costs scale linearly with farm_size_ha.
    """
    inp = PlanningInput(
        crop_id               = req.crop_id,
        farm_size_ha          = req.farm_size_ha,
        budget_level          = req.budget_level,
        has_irrigation        = req.has_irrigation,
        planting_month        = req.planting_month,
        market_price_override = req.market_price_override,
    )
    result = generate_plan(inp)
    return result.to_dict()


# ══════════════════════════════════════════════════════════════════════════════
# ENGINE 4 — PEST & DISEASE
# ══════════════════════════════════════════════════════════════════════════════

class ThreatsRequest(BaseModel):
    crop_id: str = Field(..., description="Crop ID, e.g. CROP_001")
    month:   int = Field(..., ge=1, le=12, description="Current month (1–12)")

    @field_validator("crop_id")
    @classmethod
    def validate_crop(cls, v):
        if not v:
            raise ValueError("crop_id cannot be empty")
        return v.upper()

    class Config:
        json_schema_extra = {"example": {"crop_id": "CROP_001", "month": 11}}


@app.post("/threats", tags=["Pest & Disease"],
          summary="Get all active pest and disease threats for a crop in the current month")
def threats(req: ThreatsRequest):
    """
    Returns all pests and diseases that affect this crop, ranked by:
    1. In-season threats first (active risk now)
    2. Severity descending (critical → high → medium → low)

    Each threat includes symptom previews, treatment count, and whether
    organic options are available — for the app's proactive alert system.
    """
    return crop_threats(req.crop_id, req.month)


class DiagnoseRequest(BaseModel):
    crop_id:      str        = Field(..., description="Crop ID, e.g. CROP_001")
    symptoms:     list[str]  = Field(..., min_length=1, description="List of observed symptom descriptions")
    month:        int        = Field(..., ge=1, le=12)
    budget_level: str        = Field("medium")
    top_n:        int        = Field(3, ge=1, le=5)

    @field_validator("budget_level")
    @classmethod
    def validate_budget(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("budget_level must be 'low', 'medium', or 'high'")
        return v

    @field_validator("crop_id")
    @classmethod
    def validate_crop(cls, v):
        if not v:
            raise ValueError("crop_id cannot be empty")
        return v.upper()

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, v):
        if not v:
            raise ValueError("symptoms list cannot be empty")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "crop_id": "CROP_001", "month": 11, "budget_level": "medium",
                "symptoms": ["holes in leaves", "frass in whorl", "caterpillar in plant"],
                "top_n": 3
            }
        }


@app.post("/diagnose", tags=["Pest & Disease"],
          summary="Match reported symptoms to pest/disease diagnoses with confidence scores")
def diagnose_endpoint(req: DiagnoseRequest):
    """
    Matches farmer-reported symptoms against the pest and disease database
    using keyword overlap scoring, weighted by severity and seasonal risk.

    Returns ranked diagnoses with:
    - Confidence score (0–99%)
    - Matched symptom list (shows which symptoms triggered the match)
    - Treatment options filtered by budget level
    - Scouting method to confirm diagnosis
    - Prevention measures
    - Urgency level: immediate | monitor | low
    """
    return diagnose(
        crop_id      = req.crop_id,
        symptoms     = req.symptoms,
        month        = req.month,
        budget_level = req.budget_level,
        top_n        = req.top_n,
    )


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
        json_schema_extra = {
            "example": {
                "pest_disease_id": "PEST_001",
                "budget_level": "medium",
                "farm_size_ha": 2.4
            }
        }


@app.post("/treatment", tags=["Pest & Disease"],
          summary="Get a complete, costed treatment plan for a confirmed pest or disease")
def treatment(req: TreatmentRequest):
    """
    Returns a complete treatment plan for a confirmed pest or disease,
    including:
    - Recommended products filtered by budget level (organic for low budget)
    - Product rates, timing, and application notes
    - Estimated cost per product and total treatment cost
    - PPE and safety reminders
    - Economic threshold for retreat decisions

    Costs scale linearly with farm_size_ha.
    """
    plan = get_treatment_plan(
        pest_disease_id = req.pest_disease_id.upper(),
        budget_level    = req.budget_level,
        farm_size_ha    = req.farm_size_ha,
    )
    return plan.to_dict()


# ══════════════════════════════════════════════════════════════════════════════
# COMPOSITE ENDPOINT — run all engines in one call
# ══════════════════════════════════════════════════════════════════════════════

class FullSessionRequest(BaseModel):
    """
    Full farmer session — runs all four engines and returns a complete
    daily briefing in a single API call. Designed for the mobile app's
    main screen refresh.
    """
    # Sensor readings
    soil_ph:             float = Field(..., ge=3.0, le=9.0)
    soil_moisture_pct:   float = Field(..., ge=0, le=100)
    soil_temp_c:         float = Field(..., ge=0, le=50)

    # Farmer profile
    agro_region:         int   = Field(..., ge=1, le=5)
    has_irrigation:      bool
    budget_level:        str
    planting_month:      int   = Field(..., ge=1, le=12)
    farm_size_ha:        float = Field(..., gt=0)

    # Active crop (null if not yet selected)
    active_crop_id:      Optional[str] = None
    days_since_planting: Optional[int] = Field(None, ge=0)

    @field_validator("budget_level")
    @classmethod
    def validate_budget(cls, v):
        if v not in ("low", "medium", "high"):
            raise ValueError("budget_level must be 'low', 'medium', or 'high'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "soil_ph": 6.1, "soil_moisture_pct": 62, "soil_temp_c": 24,
                "agro_region": 2, "has_irrigation": False,
                "budget_level": "low", "planting_month": 11,
                "farm_size_ha": 2.4,
                "active_crop_id": "CROP_001",
                "days_since_planting": 35,
            }
        }


@app.post("/session", tags=["Composite"],
          summary="Full farmer session — runs all four engines in one call")
def full_session(req: FullSessionRequest):
    """
    Single endpoint for the mobile app's daily refresh.

    Always returns:
      - crop_recommendations: top 5 crops for current conditions
      - planning_scenarios: quick scenario for top recommendation

    If active_crop_id + days_since_planting are provided, also returns:
      - daily_calendar: today's tasks + alerts for active crop
      - crop_threats: active pest/disease risks for current month
      - crop_plan: full financial plan for active crop
    """
    response = {"generated_at": datetime.utcnow().isoformat() + "Z"}

    # ── Always: crop recommendations
    crop_inp = CropInput(
        soil_ph           = req.soil_ph,
        soil_moisture_pct = req.soil_moisture_pct,
        soil_temp_c       = req.soil_temp_c,
        agro_region       = req.agro_region,
        has_irrigation    = req.has_irrigation,
        budget_level      = req.budget_level,
        planting_month    = req.planting_month,
        farm_size_ha      = req.farm_size_ha,
    )
    recs = recommend_crops(crop_inp, top_n=5)
    response["crop_recommendations"] = recs.to_dict()

    # ── Active crop section
    crop_id = req.active_crop_id.upper() if req.active_crop_id else None
    dsp     = req.days_since_planting

    if crop_id and crop_id in CROP_BY_ID:
        # Calendar
        if dsp is not None:
            cal_inp = CalendarInput(
                crop_id            = crop_id,
                days_since_planting= dsp,
                soil_ph            = req.soil_ph,
                soil_moisture_pct  = req.soil_moisture_pct,
                soil_temp_c        = req.soil_temp_c,
                has_irrigation     = req.has_irrigation,
                budget_level       = req.budget_level,
                planting_month     = req.planting_month,
                farm_size_ha       = req.farm_size_ha,
            )
            cal = get_daily_guidance(cal_inp)
            response["daily_calendar"] = cal.to_dict()

        # Threats
        response["crop_threats"] = crop_threats(crop_id, req.planting_month)

        # Plan
        plan_inp = PlanningInput(
            crop_id       = crop_id,
            farm_size_ha  = req.farm_size_ha,
            budget_level  = req.budget_level,
            has_irrigation= req.has_irrigation,
            planting_month= req.planting_month,
        )
        plan = generate_plan(plan_inp)
        response["crop_plan"] = plan.to_dict()

    return response


# ── Entry point for direct execution ─────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("\nMDUMENI Intelligence Engine API")
    print(f"Crops loaded: {len(CROPS)}")
    print("Starting on http://localhost:8000")
    print("Swagger docs: http://localhost:8000/docs\n")
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)
