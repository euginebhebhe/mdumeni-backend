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

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
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
