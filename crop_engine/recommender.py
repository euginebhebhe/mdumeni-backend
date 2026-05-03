"""
MDUMENI — Crop Recommendation Engine
=====================================
Scores all 30 Zimbabwean crops against live sensor data and farmer
profile, returns a ranked list of viable recommendations with full
score breakdowns, selected variety, and agronomic reasoning.

Usage:
    from crop_engine.recommender import recommend_crops, CropInput

    result = recommend_crops(CropInput(
        soil_ph=6.1,
        soil_moisture_pct=62,
        soil_temp_c=24,
        agro_region=2,
        has_irrigation=False,
        budget_level="low",
        planting_month=11
    ))
    for r in result.recommendations:
        print(r.crop_name, r.score, r.selected_variety["name"])
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from crop_engine.crop_dataset import CROPS


# ── SCORING WEIGHTS ───────────────────────────────────────────────────────────
# Must sum to 1.0
WEIGHTS = {
    "soil_ph":       0.20,
    "soil_moisture": 0.20,
    "region_fit":    0.25,  # highest — wrong region is a near-disqualifier
    "temperature":   0.15,
    "irrigation_fit":0.10,
    "budget_fit":    0.10,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"


# ── INPUT / OUTPUT DATA CLASSES ───────────────────────────────────────────────

@dataclass
class CropInput:
    """All data required to run the crop recommendation engine."""

    # Sensor readings
    soil_ph:           float        # e.g. 6.1  (valid: 3.0–9.0)
    soil_moisture_pct: float        # e.g. 62   (valid: 0–100)
    soil_temp_c:       float        # e.g. 24   (valid: 0–50)

    # Farmer profile
    agro_region:       int          # 1–5  (Zimbabwe agro-ecological region)
    has_irrigation:    bool         # True / False
    budget_level:      str          # "low" | "medium" | "high"
    planting_month:    int          # 1–12 (current month)

    # Optional context
    farm_size_ha:      Optional[float] = None
    notes:             Optional[str]   = None

    def validate(self):
        """Raise ValueError if any field is out of expected range."""
        if not (3.0 <= self.soil_ph <= 9.0):
            raise ValueError(f"soil_ph {self.soil_ph} out of range [3.0, 9.0]")
        if not (0 <= self.soil_moisture_pct <= 100):
            raise ValueError(f"soil_moisture_pct {self.soil_moisture_pct} out of range [0, 100]")
        if not (0 <= self.soil_temp_c <= 50):
            raise ValueError(f"soil_temp_c {self.soil_temp_c} out of range [0, 50]")
        if self.agro_region not in (1, 2, 3, 4, 5):
            raise ValueError(f"agro_region must be 1–5, got {self.agro_region}")
        if self.budget_level not in ("low", "medium", "high"):
            raise ValueError(f"budget_level must be 'low', 'medium', or 'high'")
        if not (1 <= self.planting_month <= 12):
            raise ValueError(f"planting_month must be 1–12, got {self.planting_month}")


@dataclass
class ScoreBreakdown:
    """Per-factor scores for a single crop, all in [0.0, 1.0]."""
    soil_ph:        float
    soil_moisture:  float
    region_fit:     float
    temperature:    float
    irrigation_fit: float
    budget_fit:     float

    def to_dict(self) -> dict:
        return {
            "soil_ph":        round(self.soil_ph, 3),
            "soil_moisture":  round(self.soil_moisture, 3),
            "region_fit":     round(self.region_fit, 3),
            "temperature":    round(self.temperature, 3),
            "irrigation_fit": round(self.irrigation_fit, 3),
            "budget_fit":     round(self.budget_fit, 3),
        }


@dataclass
class CropRecommendation:
    """A single ranked crop recommendation."""
    rank:              int
    crop_id:           str
    crop_name:         str
    local_name_shona:  str
    local_name_ndebele:str
    crop_type:         str
    score:             float            # 0.0–1.0 composite weighted score
    score_pct:         int              # score × 100, rounded
    viable:            bool             # passes all hard disqualifiers
    in_season:         bool             # planting month is in recommended window
    breakdown:         ScoreBreakdown
    selected_variety:  dict             # best variety for this farmer's budget
    disqualifiers:     list             # list of reason strings if not viable
    agronomic_notes:   list             # plain-language advisory notes
    expected_yield_t_ha: float          # yield at farmer's budget level
    market_price_usd_kg: float
    market_demand:     str

    def to_dict(self) -> dict:
        return {
            "rank":               self.rank,
            "crop_id":            self.crop_id,
            "crop_name":          self.crop_name,
            "local_name_shona":   self.local_name_shona,
            "local_name_ndebele": self.local_name_ndebele,
            "crop_type":          self.crop_type,
            "score":              round(self.score, 4),
            "score_pct":          self.score_pct,
            "viable":             self.viable,
            "in_season":          self.in_season,
            "breakdown":          self.breakdown.to_dict(),
            "selected_variety":   self.selected_variety,
            "disqualifiers":      self.disqualifiers,
            "agronomic_notes":    self.agronomic_notes,
            "expected_yield_t_ha":self.expected_yield_t_ha,
            "market_price_usd_kg":self.market_price_usd_kg,
            "market_demand":      self.market_demand,
        }


@dataclass
class RecommendationResult:
    """Full output of the recommendation engine for one farm session."""
    input_summary:    dict
    recommendations:  list           # list of CropRecommendation (viable, ranked)
    excluded:         list           # list of CropRecommendation (not viable, unranked)
    generated_at:     str

    def to_dict(self) -> dict:
        return {
            "input_summary":   self.input_summary,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "excluded_count":  len(self.excluded),
            "generated_at":    self.generated_at,
        }


# ── SCORING FUNCTIONS ─────────────────────────────────────────────────────────

def _range_score(value: float, mn: float, mx: float, optimal: float) -> float:
    """
    Returns a score in [0.0, 1.0].
    - 0.0  : value is outside [mn, mx] — completely unsuitable
    - 1.0  : value equals optimal
    - Scales linearly to 0.6 at the edges of [mn, mx]

    The 0.4 taper means a crop at its tolerance edge still scores 0.6,
    not 0 — it can survive, just not thrive.
    """
    if value < mn or value > mx:
        return 0.0
    max_distance = max(optimal - mn, mx - optimal)
    if max_distance == 0:
        return 1.0
    distance = abs(value - optimal)
    return round(1.0 - (distance / max_distance) * 0.4, 4)


def _score_soil_ph(crop: dict, inp: CropInput) -> float:
    s = crop["soil"]
    return _range_score(inp.soil_ph, s["ph_min"], s["ph_max"], s["ph_optimal"])


def _score_moisture(crop: dict, inp: CropInput) -> float:
    s = crop["soil"]
    return _range_score(
        inp.soil_moisture_pct,
        s["moisture_min"],
        s["moisture_max"],
        s["moisture_optimal"]
    )


def _score_region(crop: dict, inp: CropInput) -> float:
    return 1.0 if inp.agro_region in crop["agro_regions"] else 0.0


def _score_temperature(crop: dict, inp: CropInput) -> float:
    c = crop["climate"]
    return _range_score(
        inp.soil_temp_c,
        c["temp_min_c"],
        c["temp_max_c"],
        c["temp_optimal_c"]
    )


def _score_irrigation(crop: dict, inp: CropInput) -> float:
    req = crop["irrigation"]["required"]
    has = inp.has_irrigation
    if req == "rain_fed":
        return 1.0                      # always fine — doesn't need irrigation
    elif req == "supplemental":
        return 1.0 if has else 0.65     # can survive rain-fed, irrigation helps
    elif req == "full":
        return 1.0 if has else 0.0      # cannot do without irrigation
    return 0.5


def _score_budget(crop: dict, inp: CropInput) -> float:
    """
    Score how well the crop performs at the farmer's input level.
    Normalises yield at farmer's budget against the crop's maximum possible yield.
    """
    yield_map = crop["yield_t_ha"]
    farmer_yield = yield_map.get(f"{inp.budget_level}_input", yield_map.get("low_input", 0))
    max_yield = max(yield_map.values())
    if max_yield == 0:
        return 0.0
    return round(min(farmer_yield / max_yield, 1.0), 4)


# ── VARIETY SELECTOR ─────────────────────────────────────────────────────────

def _select_variety(crop: dict, budget_level: str) -> dict:
    """
    Return the best variety for the farmer's budget.
    Prefers an exact match on input_level; falls back to the closest available.
    """
    budget_priority = {"low": ["low", "medium", "high"],
                       "medium": ["medium", "low", "high"],
                       "high": ["high", "medium", "low"]}
    for target in budget_priority.get(budget_level, ["low"]):
        for variety in crop["varieties"]:
            if variety["input_level"] == target:
                return variety
    return crop["varieties"][0]  # ultimate fallback


# ── AGRONOMIC NOTES GENERATOR ─────────────────────────────────────────────────

def _generate_notes(crop: dict, inp: CropInput, breakdown: ScoreBreakdown) -> list:
    """
    Generate plain-language advisory notes for the farmer based on
    the score breakdown and current conditions.
    """
    notes = []
    s = crop["soil"]

    # pH advice
    if inp.soil_ph < s["ph_min"]:
        lime_kg = round((s["ph_optimal"] - inp.soil_ph) * 500)
        notes.append(
            f"Soil is too acidic (pH {inp.soil_ph:.1f}). "
            f"Apply approximately {lime_kg} kg/ha of agricultural lime to raise pH "
            f"toward {s['ph_optimal']:.1f}. Allow 4–6 weeks before planting."
        )
    elif inp.soil_ph > s["ph_max"]:
        notes.append(
            f"Soil pH ({inp.soil_ph:.1f}) is above the ideal range for {crop['name']}. "
            f"Incorporate compost or sulphur to gradually reduce pH."
        )
    elif breakdown.soil_ph < 0.8:
        notes.append(
            f"pH ({inp.soil_ph:.1f}) is within tolerance but not optimal — "
            f"target {s['ph_optimal']:.1f} for best results."
        )

    # Moisture advice
    if inp.soil_moisture_pct < s["moisture_min"]:
        notes.append(
            f"Soil moisture ({inp.soil_moisture_pct:.0f}%) is below the minimum "
            f"({s['moisture_min']}%) needed for {crop['name']}. "
            f"Irrigate before planting or wait for rain."
        )
    elif inp.soil_moisture_pct > s["moisture_max"]:
        notes.append(
            f"Soil moisture ({inp.soil_moisture_pct:.0f}%) is too high — risk of "
            f"root rot and damping-off. Improve drainage before planting."
        )

    # Irrigation mismatch
    if crop["irrigation"]["required"] == "full" and not inp.has_irrigation:
        notes.append(
            f"{crop['name']} requires consistent irrigation. "
            f"Without irrigation, yield will be severely reduced or crop will fail."
        )
    elif crop["irrigation"]["required"] == "supplemental" and not inp.has_irrigation:
        notes.append(
            f"{crop['name']} performs best with supplemental irrigation during dry spells. "
            f"Rain-fed production is possible but yields will be lower."
        )

    # Budget / variety note
    if inp.budget_level == "low":
        notes.append(
            f"At low-input level, use open-pollinated varieties and save seed for next season."
        )

    # Organic alternatives available
    if crop.get("organic_alternatives"):
        notes.append(
            f"Organic input alternatives are available — ask the guide for details."
        )

    return notes


# ── HARD DISQUALIFIERS ────────────────────────────────────────────────────────

def _get_disqualifiers(crop: dict, inp: CropInput, breakdown: ScoreBreakdown) -> list:
    """
    Return a list of disqualifier strings. If list is non-empty, crop is not viable.
    """
    disq = []

    # Wrong agro-ecological region
    if inp.agro_region not in crop["agro_regions"]:
        regions_str = ", ".join(str(r) for r in crop["agro_regions"])
        disq.append(
            f"Not suited to Region {inp.agro_region}. "
            f"{crop['name']} grows in Regions: {regions_str}."
        )

    # pH completely out of range
    if breakdown.soil_ph == 0.0:
        disq.append(
            f"Soil pH ({inp.soil_ph:.1f}) is outside the survivable range "
            f"[{crop['soil']['ph_min']}, {crop['soil']['ph_max']}] for {crop['name']}."
        )

    # Full irrigation crop without irrigation
    if crop["irrigation"]["required"] == "full" and not inp.has_irrigation:
        disq.append(
            f"{crop['name']} requires full irrigation. Not viable without a water source."
        )

    return disq


# ── MAIN RECOMMENDATION FUNCTION ─────────────────────────────────────────────

def recommend_crops(
    inp: CropInput,
    top_n: int = 5,
    include_all: bool = False
) -> RecommendationResult:
    """
    Run all 30 crops through the scoring engine and return ranked results.

    Args:
        inp:         CropInput — validated farmer + sensor data
        top_n:       How many viable crops to return (default 5)
        include_all: If True, include excluded crops in result

    Returns:
        RecommendationResult with ranked viable crops and any excluded crops
    """
    inp.validate()

    scored = []

    for crop in CROPS:
        # Score each factor
        breakdown = ScoreBreakdown(
            soil_ph        = _score_soil_ph(crop, inp),
            soil_moisture  = _score_moisture(crop, inp),
            region_fit     = _score_region(crop, inp),
            temperature    = _score_temperature(crop, inp),
            irrigation_fit = _score_irrigation(crop, inp),
            budget_fit     = _score_budget(crop, inp),
        )

        # Weighted composite score
        score = (
            breakdown.soil_ph        * WEIGHTS["soil_ph"]       +
            breakdown.soil_moisture  * WEIGHTS["soil_moisture"]  +
            breakdown.region_fit     * WEIGHTS["region_fit"]     +
            breakdown.temperature    * WEIGHTS["temperature"]    +
            breakdown.irrigation_fit * WEIGHTS["irrigation_fit"] +
            breakdown.budget_fit     * WEIGHTS["budget_fit"]
        )

        # Hard disqualifiers
        disqualifiers = _get_disqualifiers(crop, inp, breakdown)
        viable = len(disqualifiers) == 0

        # Planting season check
        months_for_region = crop["planting"]["months_by_region"].get(
            str(inp.agro_region), []
        )
        in_season = inp.planting_month in months_for_region

        # Variety selection
        selected_variety = _select_variety(crop, inp.budget_level)

        # Expected yield at farmer's budget
        yield_key = f"{inp.budget_level}_input"
        expected_yield = crop["yield_t_ha"].get(yield_key, crop["yield_t_ha"]["low_input"])

        # Agronomic notes
        notes = _generate_notes(crop, inp, breakdown)

        rec = CropRecommendation(
            rank               = 0,  # assigned after sorting
            crop_id            = crop["id"],
            crop_name          = crop["name"],
            local_name_shona   = crop["local_names"].get("shona", ""),
            local_name_ndebele = crop["local_names"].get("ndebele", ""),
            crop_type          = crop["type"],
            score              = round(score, 4),
            score_pct          = round(score * 100),
            viable             = viable,
            in_season          = in_season,
            breakdown          = breakdown,
            selected_variety   = selected_variety,
            disqualifiers      = disqualifiers,
            agronomic_notes    = notes,
            expected_yield_t_ha= expected_yield,
            market_price_usd_kg= crop["market"]["price_usd_per_kg"],
            market_demand      = crop["market"]["demand"],
        )
        scored.append(rec)

    # Sort viable crops:
    # 1. In-season crops always rank above out-of-season
    # 2. Then by composite score descending
    viable_crops = [r for r in scored if r.viable]
    excluded_crops = [r for r in scored if not r.viable]

    viable_crops.sort(key=lambda r: (not r.in_season, -r.score))

    # Assign ranks
    for i, rec in enumerate(viable_crops[:top_n], start=1):
        rec.rank = i

    result = RecommendationResult(
        input_summary={
            "soil_ph":           inp.soil_ph,
            "soil_moisture_pct": inp.soil_moisture_pct,
            "soil_temp_c":       inp.soil_temp_c,
            "agro_region":       inp.agro_region,
            "has_irrigation":    inp.has_irrigation,
            "budget_level":      inp.budget_level,
            "planting_month":    inp.planting_month,
            "farm_size_ha":      inp.farm_size_ha,
        },
        recommendations=viable_crops[:top_n],
        excluded=excluded_crops if include_all else [],
        generated_at=datetime.utcnow().isoformat() + "Z",
    )

    return result
