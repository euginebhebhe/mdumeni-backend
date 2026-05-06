"""
MDUMENI — Planning Engine
===========================
Calculates expected yield, full input cost breakdown, and profit
margin for any crop before the farmer plants.

Given:
  - Crop (from crop_dataset)
  - Farm size in hectares
  - Budget level (low / medium / high)
  - Market price (live or dataset default)
  - Irrigation availability
  - Labour cost assumptions (region-adjusted)

The engine returns:
  - Expected yield (kg and tonnes)
  - Full cost breakdown (seed, fertiliser, labour, irrigation, chemicals)
  - Gross revenue
  - Net profit / loss
  - Profit per hectare
  - Break-even yield
  - Return on investment (ROI %)
  - Harvest plan (timing, storage, market recommendation)

Design principle:
  All monetary values are in USD.
  Labour costs use Zimbabwe smallholder averages (adjustable).
  Costs scale linearly with farm_size_ha.
  The engine is deliberately conservative — it underestimates yield
  and overestimates costs so farmers are never disappointed.
"""

from dataclasses import dataclass, field
from typing import Optional
from crop_engine.crop_dataset import CROP_BY_ID


# ── REGIONAL LABOUR RATE ASSUMPTIONS (USD/day) ────────────────────────────────
# Adjustable per region. These are conservative Zimbabwe smallholder rates.
LABOUR_RATE_USD_PER_DAY = 5.00

# Labour days required per hectare by operation
LABOUR_DAYS_PER_HA = {
    "land_preparation":   4.0,   # ploughing, harrowing, ridging
    "planting":           2.0,   # planting and covering
    "weeding_1":          3.0,   # first weeding
    "weeding_2":          2.5,   # second weeding
    "top_dress_1":        1.0,   # applying first top dress
    "top_dress_2":        0.8,   # applying second top dress
    "pest_scouting":      1.5,   # 3 scouting visits × 0.5 days each
    "pest_application":   1.0,   # pesticide application
    "harvesting":         5.0,   # harvesting and collection
    "threshing_drying":   3.0,   # post-harvest processing
}

# Seed cost assumptions (USD/kg planted seed) — varies by variety type
SEED_COST_USD_PER_KG = {
    "hybrid":           8.00,
    "improved":         4.00,
    "open_pollinated":  1.50,
    "local":            0.50,
    "flue_cured":      12.00,
}

# Seeding rate (kg seed per hectare) — crop-specific
SEEDING_RATE_KG_PER_HA = {
    "CROP_001": 25,    # Maize
    "CROP_002": 8,     # Sorghum
    "CROP_003": 120,   # Wheat
    "CROP_004": 5,     # Pearl millet
    "CROP_005": 130,   # Barley
    "CROP_006": 80,    # Soybeans
    "CROP_007": 80,    # Groundnuts (in shell)
    "CROP_008": 50,    # Sugar beans
    "CROP_009": 25,    # Cowpeas
    "CROP_010": 12,    # Cotton
    "CROP_011": 0.08,  # Tobacco (transplants from seedbed — very small)
    "CROP_012": 5,     # Sunflower
    "CROP_013": 0.3,   # Tomatoes (transplants)
    "CROP_014": 4,     # Onions
    "CROP_015": 0.4,   # Cabbages (transplants)
    "CROP_016": 2,     # Rape
    "CROP_017": 2,     # Watermelon
    "CROP_018": 2,     # Butternut squash
    "CROP_019": 79,     # Sweet potato — vine cuttings, no seed cost
    "CROP_020": 700,     # Cassava — stem cuttings
    "CROP_021": 2000,  # Irish potato — seed tubers (kg/ha)
    "CROP_022": 0.3,   # Papaya
    "CROP_023": 50,    # Mango (seedlings — price per seedling, not kg)
    "CROP_024": 50,    # Avocado (grafted seedlings)
    "CROP_025": 800,   # Bananas (suckers — price per 800 suckers/ha)
    "CROP_026": 8000,  # Sugar cane (billets — pieces/ha)
    "CROP_027": 3,     # Sesame
    "CROP_028": 3,     # Pumpkin
    "CROP_029": 600,   # Garlic (cloves — kg/ha)
    "CROP_030": 0.3,   # Chillies (transplants)
}

# Irrigation cost (USD per mm of water applied per hectare)
IRRIGATION_COST_USD_PER_MM_HA = 0.012

# Chemical cost assumptions by budget level (USD/ha/season)
CHEMICAL_COSTS_USD_PER_HA = {
    "low":    15.0,   # minimal — mostly organic treatments
    "medium": 45.0,   # standard pest and disease programme
    "high":   90.0,   # full programme including preventative sprays
}

# Contingency buffer — adds % to total costs to cover unexpected expenses
CONTINGENCY_PCT = 0.08  # 8%


# ── FERTILISER PRICE LOOKUP (USD/kg product) ─────────────────────────────────
FERTILISER_PRICES_USD_PER_KG = {
    "Compound D":               0.55,
    "Compound C":               0.58,
    "Compound L":               0.60,
    "Compound S":               0.62,
    "Ammonium Nitrate (34.5%N)":0.48,
    "Ammonium Nitrate":         0.48,
    "AN (34.5%N)":              0.48,
    "LAN (28%N)":               0.42,
    "LAN":                      0.42,
    "Single Super Phosphate":   0.32,
    "Potassium Chloride":       0.55,
    "Potassium Nitrate":        0.88,
    "Calcium Nitrate":          0.72,
    "Potassium Sulphate":       0.70,
    "Agricultural lime":        0.08,
    "Rhizobium inoculant":      18.0,
    "Bone meal":                0.35,
    "Multifeed":                2.20,
    # Organic — much cheaper
    "Compost":                  0.04,
    "Cattle manure":            0.02,
    "Fermented plant juice":    0.50,
}


# ── INPUT / OUTPUT DATA CLASSES ───────────────────────────────────────────────

@dataclass
class PlanningInput:
    crop_id:         str
    farm_size_ha:    float          # total farm area being planted
    budget_level:    str            # "low" | "medium" | "high"
    has_irrigation:  bool
    planting_month:  int            # 1–12
    market_price_override: Optional[float] = None  # USD/kg — overrides dataset price

    def validate(self):
        if not self.crop_id:
            raise ValueError("crop_id is required")
        if self.farm_size_ha <= 0:
            raise ValueError("farm_size_ha must be positive")
        if self.budget_level not in ("low", "medium", "high"):
            raise ValueError("budget_level must be low / medium / high")
        if not (1 <= self.planting_month <= 12):
            raise ValueError("planting_month must be 1–12")
        if self.market_price_override is not None and self.market_price_override < 0:
            raise ValueError("market_price_override cannot be negative")


@dataclass
class CostLine:
    """A single line in the cost breakdown."""
    category:    str
    description: str
    unit:        str
    quantity:    float
    unit_cost:   float
    total_usd:   float

    def to_dict(self):
        return {
            "category":    self.category,
            "description": self.description,
            "unit":        self.unit,
            "quantity":    round(self.quantity, 2),
            "unit_cost":   round(self.unit_cost, 3),
            "total_usd":   round(self.total_usd, 2),
        }


@dataclass
class HarvestPlan:
    """Harvest timing and market guidance."""
    days_to_harvest:         int
    harvest_window_days:     int    # how many days the window stays open
    recommended_market:      str
    storage_guidance:        str
    post_harvest_steps:      list
    rotation_suggestion:     str

    def to_dict(self):
        return {
            "days_to_harvest":     self.days_to_harvest,
            "harvest_window_days": self.harvest_window_days,
            "recommended_market":  self.recommended_market,
            "storage_guidance":    self.storage_guidance,
            "post_harvest_steps":  self.post_harvest_steps,
            "rotation_suggestion": self.rotation_suggestion,
        }


@dataclass
class PlanningResult:
    """Complete financial plan for one crop season."""

    # Identity
    crop_id:          str
    crop_name:        str
    farm_size_ha:     float
    budget_level:     str

    # Yield projection
    expected_yield_kg:     float
    expected_yield_t_ha:   float
    yield_confidence:      str     # "conservative" | "moderate" | "optimistic"

    # Revenue
    market_price_usd_kg:   float
    gross_revenue_usd:     float

    # Cost breakdown
    cost_lines:            list    # list of CostLine objects
    total_cost_usd:        float
    cost_per_ha:           float

    # Profit
    net_profit_usd:        float
    profit_per_ha:         float
    roi_pct:               float

    # Risk indicators
    break_even_yield_kg:   float   # minimum yield to cover all costs
    break_even_pct:        float   # break-even yield as % of expected yield
    margin_of_safety_pct:  float   # how far above break-even expected yield is

    # Harvest plan
    harvest_plan:          HarvestPlan

    # Scenario comparison
    scenarios:             dict    # low / medium / high input comparison

    def to_dict(self):
        return {
            "crop_id":             self.crop_id,
            "crop_name":           self.crop_name,
            "farm_size_ha":        self.farm_size_ha,
            "budget_level":        self.budget_level,
            "expected_yield_kg":   round(self.expected_yield_kg, 1),
            "expected_yield_t_ha": round(self.expected_yield_t_ha, 2),
            "yield_confidence":    self.yield_confidence,
            "market_price_usd_kg": round(self.market_price_usd_kg, 3),
            "gross_revenue_usd":   round(self.gross_revenue_usd, 2),
            "cost_lines":          [c.to_dict() for c in self.cost_lines],
            "total_cost_usd":      round(self.total_cost_usd, 2),
            "cost_per_ha":         round(self.cost_per_ha, 2),
            "net_profit_usd":      round(self.net_profit_usd, 2),
            "profit_per_ha":       round(self.profit_per_ha, 2),
            "roi_pct":             round(self.roi_pct, 1),
            "break_even_yield_kg": round(self.break_even_yield_kg, 1),
            "break_even_pct":      round(self.break_even_pct, 1),
            "margin_of_safety_pct":round(self.margin_of_safety_pct, 1),
            "harvest_plan":        self.harvest_plan.to_dict(),
            "scenarios":           self.scenarios,
        }


# ── COST CALCULATORS ─────────────────────────────────────────────────────────

def _calc_seed_cost(crop: dict, inp: PlanningInput) -> CostLine:
    """Calculate seed / planting material cost."""
    # Select variety matching budget level
    budget_map = {"low": "low", "medium": "medium", "high": "high"}
    target = budget_map[inp.budget_level]

    selected_variety = None
    for v in crop["varieties"]:
        if v["input_level"] == target:
            selected_variety = v
            break
    if not selected_variety:
        selected_variety = crop["varieties"][0]

    variety_type = selected_variety.get("type", "open_pollinated")
    price_per_kg = SEED_COST_USD_PER_KG.get(variety_type, 2.00)
    seeding_rate = SEEDING_RATE_KG_PER_HA.get(crop["id"], 20)

    total = price_per_kg * seeding_rate * inp.farm_size_ha

    return CostLine(
        category    = "seed",
        description = f"{selected_variety['name']} ({variety_type})",
        unit        = "kg/ha" if seeding_rate < 500 else "units/ha",
        quantity    = seeding_rate * inp.farm_size_ha,
        unit_cost   = price_per_kg,
        total_usd   = total,
    )


def _calc_fertiliser_costs(crop: dict, inp: PlanningInput) -> list:
    """Calculate all fertiliser costs from the crop's schedule."""
    lines = []

    # Decide which schedule to use based on budget
    schedule = crop.get("fertiliser_schedule", [])
    if inp.budget_level == "low" and crop.get("organic_alternatives"):
        schedule = crop["organic_alternatives"]

    for item in schedule:
        product = item.get("product", "Unknown")
        kg_per_ha = item.get("kg_per_ha", item.get("litres_per_ha", 0))
        price = FERTILISER_PRICES_USD_PER_KG.get(product, 0.40)
        total = price * kg_per_ha * inp.farm_size_ha

        lines.append(CostLine(
            category    = "fertiliser",
            description = f"{product} — {item.get('phase', 'application')}",
            unit        = "kg/ha",
            quantity    = kg_per_ha * inp.farm_size_ha,
            unit_cost   = price,
            total_usd   = total,
        ))

    return lines


def _calc_labour_costs(crop: dict, inp: PlanningInput) -> list:
    """Calculate total labour costs across all operations."""
    lines = []

    # Determine which operations apply
    operations = dict(LABOUR_DAYS_PER_HA)

    # Adjust for budget level (low budget = more hand labour = more days)
    if inp.budget_level == "low":
        operations["land_preparation"] += 2.0  # extra manual work
        operations["weeding_1"]        += 1.0
        operations["weeding_2"]        += 1.0
    elif inp.budget_level == "high":
        operations["land_preparation"] -= 1.0  # mechanised
        operations["harvesting"]       -= 1.5  # mechanised assist

    # Group into one line per category
    field_ops = {k: v for k, v in operations.items()
                 if k in ("land_preparation", "planting", "weeding_1", "weeding_2")}
    crop_ops  = {k: v for k, v in operations.items()
                 if k in ("top_dress_1", "top_dress_2", "pest_scouting", "pest_application")}
    harvest_ops = {k: v for k, v in operations.items()
                   if k in ("harvesting", "threshing_drying")}

    for group_name, ops in [
        ("Field preparation & planting", field_ops),
        ("Crop management", crop_ops),
        ("Harvest & post-harvest", harvest_ops),
    ]:
        total_days = sum(ops.values()) * inp.farm_size_ha
        total_cost = total_days * LABOUR_RATE_USD_PER_DAY
        lines.append(CostLine(
            category    = "labour",
            description = group_name,
            unit        = "person-days",
            quantity    = total_days,
            unit_cost   = LABOUR_RATE_USD_PER_DAY,
            total_usd   = total_cost,
        ))

    return lines


def _calc_irrigation_cost(crop: dict, inp: PlanningInput) -> Optional[CostLine]:
    """Calculate irrigation cost if applicable."""
    if not inp.has_irrigation:
        return None

    water_mm = crop["irrigation"].get("water_mm_per_season", 0)
    if water_mm == 0:
        return None

    total = IRRIGATION_COST_USD_PER_MM_HA * water_mm * inp.farm_size_ha

    return CostLine(
        category    = "irrigation",
        description = f"Irrigation water ({water_mm} mm/season)",
        unit        = "mm/ha",
        quantity    = water_mm * inp.farm_size_ha,
        unit_cost   = IRRIGATION_COST_USD_PER_MM_HA,
        total_usd   = total,
    )


def _calc_chemical_costs(inp: PlanningInput) -> CostLine:
    """Calculate pesticide / fungicide / herbicide costs."""
    cost_per_ha = CHEMICAL_COSTS_USD_PER_HA[inp.budget_level]
    total = cost_per_ha * inp.farm_size_ha

    desc_map = {
        "low":    "Minimal pest/disease programme (organic options)",
        "medium": "Standard pest and disease programme",
        "high":   "Full preventative + curative programme",
    }

    return CostLine(
        category    = "chemicals",
        description = desc_map[inp.budget_level],
        unit        = "USD/ha",
        quantity    = inp.farm_size_ha,
        unit_cost   = cost_per_ha,
        total_usd   = total,
    )


def _calc_contingency(subtotal: float) -> CostLine:
    """Add contingency buffer for unexpected costs."""
    amount = subtotal * CONTINGENCY_PCT
    return CostLine(
        category    = "contingency",
        description = f"Contingency buffer ({CONTINGENCY_PCT*100:.0f}% of subtotal)",
        unit        = "lump sum",
        quantity    = 1,
        unit_cost   = amount,
        total_usd   = amount,
    )


# ── YIELD PROJECTOR ───────────────────────────────────────────────────────────

def _project_yield(crop: dict, inp: PlanningInput) -> tuple:
    """
    Return (yield_t_ha, confidence_label).
    Uses a conservative 85% of the dataset yield figure to account
    for real-world variability (weather, pests, management gaps).
    """
    yield_key = f"{inp.budget_level}_input"
    base_yield = crop["yield_t_ha"].get(yield_key, crop["yield_t_ha"]["low_input"])

    # Apply irrigation bonus — irrigation boosts yield 15–25% for supplemental crops
    if inp.has_irrigation and crop["irrigation"]["required"] == "supplemental":
        base_yield *= 1.18
    elif inp.has_irrigation and crop["irrigation"]["required"] == "rain_fed":
        base_yield *= 1.05  # minor bonus — irrigation on rain-fed crop

    # Conservative discount — better to under-promise
    conservative_yield = base_yield * 0.85

    # Confidence label
    if inp.budget_level == "low":
        confidence = "conservative"
    elif inp.budget_level == "medium":
        confidence = "moderate"
    else:
        confidence = "optimistic"

    return round(conservative_yield, 2), confidence


# ── HARVEST PLAN BUILDER ──────────────────────────────────────────────────────

def _build_harvest_plan(crop: dict, inp: PlanningInput) -> HarvestPlan:
    """Build harvest timing, market, and storage guidance."""

    # Days to harvest from planting
    maturity = crop["planting"].get("days_to_maturity", {})
    if inp.budget_level == "high" and "short_season" in maturity:
        days = maturity.get("short_season", maturity.get("medium_season", 90))
    elif inp.budget_level == "low" and "long_season" in maturity:
        days = maturity.get("long_season", maturity.get("medium_season", 120))
    else:
        days = maturity.get("medium_season", maturity.get("long_season",
               maturity.get("short_season", 90)))

    # Harvest window
    window_days = 14 if crop["type"] in ("cereal", "legume") else 7

    # Market recommendation
    demand = crop["market"].get("demand", "medium")
    price  = crop["market"]["price_usd_per_kg"]
    if demand in ("very_high", "high"):
        market_rec = f"Sell within 2–4 weeks of harvest. High demand means good price ({price:.2f} USD/kg). Local markets and grain buyers recommended."
    else:
        market_rec = f"Store if price is low and sell when market price improves. Current average: {price:.2f} USD/kg."

    # Storage guidance
    crop_type = crop["type"]
    storage_map = {
        "cereal":     "Store in hermetic bags or metal silos with Actellic Super dust. Keep dry below 13% moisture. Inspect monthly.",
        "legume":     "Store in airtight bags below 12% moisture. Add bay leaves as natural insect repellent. Inspect monthly.",
        "cash_crop":  "Follow buyer grading and storage instructions. Deliver to market or buyer within agreed timeframe.",
        "vegetable":  "Most vegetables do not store well. Sell within 3–5 days of harvest. Consider value-adding (drying, processing).",
        "root_tuber": "Cure in shade before storage. Keep in cool, ventilated location. Check weekly for rot.",
        "fruit":      "Harvest at correct maturity. Ripen at room temperature. Sell quickly — most tropical fruits store 1–3 weeks maximum.",
        "oilseed":    "Dry to below 9% moisture. Store in clean bags away from sunlight and heat. Oil quality deteriorates quickly in moisture.",
    }
    storage = storage_map.get(crop_type, "Store in clean, dry conditions away from pests and moisture.")

    # Post-harvest steps
    post_steps = [
        "Weigh and record total yield for farm records.",
        "Sort and grade — separate damaged or poor-quality produce.",
        "Dry to safe storage moisture before bagging.",
        "Label all bags with: crop name, variety, date, weight.",
        "Record input costs and final yield for next season planning.",
    ]
    if crop_type in ("cereal", "legume"):
        post_steps.insert(2, "Treat with appropriate grain protectant before storage.")

    # Rotation suggestion
    rotation_partners = crop.get("rotation_partners", [])
    if rotation_partners:
        from crop_engine.crop_dataset import CROP_BY_ID as CBD
        names = [CBD[r]["name"] for r in rotation_partners if r in CBD]
        rotation = f"Recommended rotation crops: {', '.join(names[:2])}. Rotating with legumes restores soil nitrogen."
    else:
        rotation = "Rest the field or plant a cover crop for soil recovery."

    return HarvestPlan(
        days_to_harvest     = days,
        harvest_window_days = window_days,
        recommended_market  = market_rec,
        storage_guidance    = storage,
        post_harvest_steps  = post_steps,
        rotation_suggestion = rotation,
    )


# ── SCENARIO COMPARISON ───────────────────────────────────────────────────────

def _build_scenarios(crop: dict, inp: PlanningInput, market_price: float) -> dict:
    """Compare low / medium / high input scenarios side by side."""
    scenarios = {}
    for level in ("low", "medium", "high"):
        level_inp = PlanningInput(
            crop_id       = inp.crop_id,
            farm_size_ha  = inp.farm_size_ha,
            budget_level  = level,
            has_irrigation= inp.has_irrigation,
            planting_month= inp.planting_month,
        )
        y_t_ha, _ = _project_yield(crop, level_inp)
        y_kg = y_t_ha * 1000 * inp.farm_size_ha
        rev = y_kg * market_price

        # Quick cost estimate (no detail — just for comparison)
        fert_total = sum(
            FERTILISER_PRICES_USD_PER_KG.get(item["product"], 0.40) *
            item.get("kg_per_ha", 0) * inp.farm_size_ha
            for item in (crop["organic_alternatives"] if level == "low" and crop.get("organic_alternatives")
                         else crop.get("fertiliser_schedule", []))
        )
        seed_rate = SEEDING_RATE_KG_PER_HA.get(crop["id"], 20)
        variety_for_level = next(
            (v for v in crop["varieties"] if v["input_level"] == level),
            crop["varieties"][0]
        )
        seed_cost = SEED_COST_USD_PER_KG.get(
            variety_for_level.get("type", "open_pollinated"), 2.0
        ) * seed_rate * inp.farm_size_ha

        labour_days = sum(LABOUR_DAYS_PER_HA.values()) * inp.farm_size_ha
        labour_cost = labour_days * LABOUR_RATE_USD_PER_DAY
        chem_cost   = CHEMICAL_COSTS_USD_PER_HA[level] * inp.farm_size_ha
        irrig_cost  = (IRRIGATION_COST_USD_PER_MM_HA *
                       crop["irrigation"].get("water_mm_per_season", 0) *
                       inp.farm_size_ha) if inp.has_irrigation else 0.0

        total_cost = (fert_total + seed_cost + labour_cost +
                      chem_cost + irrig_cost) * (1 + CONTINGENCY_PCT)
        net = rev - total_cost
        roi = ((net / total_cost) * 100) if total_cost > 0 else 0

        scenarios[level] = {
            "yield_t_ha":     round(y_t_ha, 2),
            "yield_kg":       round(y_kg, 1),
            "revenue_usd":    round(rev, 2),
            "total_cost_usd": round(total_cost, 2),
            "net_profit_usd": round(net, 2),
            "roi_pct":        round(roi, 1),
        }

    return scenarios


# ── MAIN PLANNING FUNCTION ────────────────────────────────────────────────────

def generate_plan(inp: PlanningInput) -> PlanningResult:
    """
    Generate a complete financial plan for one crop season.

    Args:
        inp: PlanningInput — validated farm and crop parameters

    Returns:
        PlanningResult — full structured plan with cost breakdown and profit
    """
    inp.validate()

    crop = CROP_BY_ID.get(inp.crop_id)
    if not crop:
        raise ValueError(f"Crop '{inp.crop_id}' not found in dataset.")

    # ── Yield projection
    yield_t_ha, confidence = _project_yield(crop, inp)
    yield_kg = yield_t_ha * 1000 * inp.farm_size_ha

    # ── Market price
    market_price = (inp.market_price_override
                    if inp.market_price_override is not None
                    else crop["market"]["price_usd_per_kg"])

    # ── Revenue
    gross_revenue = yield_kg * market_price

    # ── Build cost lines
    cost_lines = []

    seed_line = _calc_seed_cost(crop, inp)
    cost_lines.append(seed_line)

    fert_lines = _calc_fertiliser_costs(crop, inp)
    cost_lines.extend(fert_lines)

    labour_lines = _calc_labour_costs(crop, inp)
    cost_lines.extend(labour_lines)

    irrig_line = _calc_irrigation_cost(crop, inp)
    if irrig_line:
        cost_lines.append(irrig_line)

    chem_line = _calc_chemical_costs(inp)
    cost_lines.append(chem_line)

    subtotal = sum(c.total_usd for c in cost_lines)
    contingency = _calc_contingency(subtotal)
    cost_lines.append(contingency)

    total_cost = subtotal + contingency.total_usd
    cost_per_ha = total_cost / inp.farm_size_ha

    # ── Profit
    net_profit   = gross_revenue - total_cost
    profit_per_ha = net_profit / inp.farm_size_ha
    roi_pct      = ((net_profit / total_cost) * 100) if total_cost > 0 else 0

    # ── Break-even analysis
    break_even_kg = total_cost / market_price if market_price > 0 else float("inf")
    break_even_pct = (break_even_kg / yield_kg * 100) if yield_kg > 0 else float("inf")
    margin_of_safety = max(0, 100 - break_even_pct)

    # ── Harvest plan
    harvest_plan = _build_harvest_plan(crop, inp)

    # ── Scenario comparison
    scenarios = _build_scenarios(crop, inp, market_price)

    return PlanningResult(
        crop_id              = crop["id"],
        crop_name            = crop["name"],
        farm_size_ha         = inp.farm_size_ha,
        budget_level         = inp.budget_level,
        expected_yield_kg    = round(yield_kg, 1),
        expected_yield_t_ha  = yield_t_ha,
        yield_confidence     = confidence,
        market_price_usd_kg  = market_price,
        gross_revenue_usd    = round(gross_revenue, 2),
        cost_lines           = cost_lines,
        total_cost_usd       = round(total_cost, 2),
        cost_per_ha          = round(cost_per_ha, 2),
        net_profit_usd       = round(net_profit, 2),
        profit_per_ha        = round(profit_per_ha, 2),
        roi_pct              = round(roi_pct, 1),
        break_even_yield_kg  = round(break_even_kg, 1),
        break_even_pct       = round(break_even_pct, 1),
        margin_of_safety_pct = round(margin_of_safety, 1),
        harvest_plan         = harvest_plan,
        scenarios            = scenarios,
    )
