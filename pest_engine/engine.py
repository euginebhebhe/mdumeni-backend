"""
MDUMENI — Pest & Disease Engine
Three modes: crop_threats, diagnose, get_treatment_plan
"""

from dataclasses import dataclass
from typing import Optional
from pest_engine.pest_disease_db import (
    PESTS, DISEASES,
    PEST_BY_ID, DISEASE_BY_ID,
    PESTS_BY_CROP, DISEASES_BY_CROP,
)

PRODUCT_COSTS = {
    "emamectin": 35.0, "proclaim": 35.0,
    "chlorpyrifos": 8.0, "dursban": 8.0,
    "lambda": 12.0, "karate": 12.0,
    "carbofuran": 15.0, "furadan": 15.0,
    "spinosad": 45.0, "tracer": 45.0,
    "propiconazole": 18.0, "tilt": 18.0,
    "azoxystrobin": 22.0, "amistar": 22.0,
    "mancozeb": 5.0, "dithane": 5.0,
    "chlorothalonil": 8.0, "bravo": 8.0,
    "metalaxyl": 20.0, "ridomil": 22.0,
    "copper": 4.5, "cuprox": 4.5,
    "imidacloprid": 25.0, "confidor": 25.0,
    "abamectin": 30.0, "dynamec": 30.0,
    "dimethoate": 7.0, "pirimicarb": 28.0,
    "indoxacarb": 32.0, "steward": 32.0,
    "tebuconazole": 20.0, "folicur": 20.0,
    "spirotetramat": 38.0, "movento": 38.0,
    "cymoxanil": 18.0, "curzate": 18.0,
    "sulphur": 3.0, "iprodione": 22.0,
    "bt": 12.0, "dipel": 12.0,
    "neem": 5.5, "pyrethrin": 8.0,
    "soap": 3.0, "mineral oil": 2.0,
    "kaolin": 4.0, "surround": 4.0,
    "wood ash": 0.5, "kocide": 8.0,
    "bicarbonate": 1.0, "beauveria": 15.0,
}

SEVERITY_WEIGHTS = {"critical": 4.0, "high": 3.0, "medium": 2.0, "low": 1.0}

_STOPWORDS = {
    "the","a","an","and","or","of","in","on","at","to","with","by",
    "is","are","has","have","be","been","from","than","more","less",
    "per","for","this","that","which","when","where","what","how",
    "may","can","will","not","no","some","all","any","very","most","also",
}

def _tokenise(text: str) -> set:
    words = text.lower().replace("-"," ").replace(","," ").replace("."," ").split()
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}

def _score_symptoms(record: dict, query_tokens: set) -> tuple:
    if not query_tokens:
        return 0.0, []
    matched, total_overlap = [], 0
    for symptom in record.get("symptoms", []):
        overlap = len(query_tokens & _tokenise(symptom))
        if overlap > 0:
            matched.append(symptom)
            total_overlap += overlap
    score = total_overlap / len(query_tokens)
    return round(score, 4), matched

def _filter_treatments(treatments: list, budget_level: str) -> list:
    organic  = [t for t in treatments if t.get("type") == "organic"]
    chemical = [t for t in treatments if t.get("type") == "chemical"]
    cultural = [t for t in treatments if t.get("type") == "cultural"]
    if budget_level == "low":
        return organic + cultural if organic else chemical[:1] + cultural
    elif budget_level == "medium":
        return chemical[:1] + organic[:1] + cultural
    else:
        return chemical + organic[:1] + cultural

def _estimate_product_cost(product_name: str) -> float:
    name_lower = product_name.lower()
    for key, cost in PRODUCT_COSTS.items():
        if key in name_lower:
            return cost
    return 10.0

def _parse_rate_to_amount(rate_str: str, farm_size_ha: float) -> float:
    import re
    match = re.search(r"([\d.]+)\s*(mL|L|g|kg)", rate_str, re.IGNORECASE)
    if not match:
        return 1.0
    amount = float(match.group(1))
    unit = match.group(2).lower()
    if unit in ("ml",):
        amount /= 1000
    elif unit in ("g",):
        amount /= 1000
    return amount * farm_size_ha


# ── DATA CLASSES ──────────────────────────────────────────────────────────────

@dataclass
class TreatmentPlan:
    pest_disease_id:    str
    name:               str
    category:           str
    severity:           str
    farm_size_ha:       float
    budget_level:       str
    recommended_products: list
    total_cost_usd:     float
    application_notes:  list
    organic_only:       bool

    def to_dict(self):
        return {
            "pest_disease_id":      self.pest_disease_id,
            "name":                 self.name,
            "category":             self.category,
            "severity":             self.severity,
            "farm_size_ha":         self.farm_size_ha,
            "budget_level":         self.budget_level,
            "recommended_products": self.recommended_products,
            "total_cost_usd":       round(self.total_cost_usd, 2),
            "application_notes":    self.application_notes,
            "organic_only":         self.organic_only,
        }


# ── MODE 1: CROP THREATS ──────────────────────────────────────────────────────

def crop_threats(crop_id: str, month: int) -> dict:
    if not crop_id:
        raise ValueError("crop_id is required")
    if not (1 <= month <= 12):
        raise ValueError("month must be 1–12")

    def summarise(record, category):
        in_season = (category == "disease") or (month in record.get("season_risk", list(range(1,13))))
        organic   = any(t.get("type") == "organic" for t in record.get("treatments", []))
        return {
            "id":               record["id"],
            "category":         category,
            "name":             record["common_name"],
            "severity":         record["severity"],
            "in_season":        in_season,
            "symptoms_preview": record.get("symptoms", [])[:2],
            "treatment_count":  len(record.get("treatments", [])),
            "organic_options":  organic,
        }

    def sort_key(t):
        return (not t["in_season"], -SEVERITY_WEIGHTS.get(t["severity"], 1.0))

    pest_summaries    = sorted([summarise(p,"pest")    for p in PESTS_BY_CROP.get(crop_id,[])],    key=sort_key)
    disease_summaries = sorted([summarise(d,"disease") for d in DISEASES_BY_CROP.get(crop_id,[])], key=sort_key)

    return {
        "crop_id":       crop_id,
        "month":         month,
        "pests":         pest_summaries,
        "diseases":      disease_summaries,
        "total_threats": len(pest_summaries) + len(disease_summaries),
    }


# ── MODE 2: DIAGNOSE ──────────────────────────────────────────────────────────

def diagnose(
    crop_id:      str,
    symptoms:     list,
    month:        int,
    budget_level: str = "medium",
    top_n:        int = 3,
) -> list:
    if not crop_id:
        raise ValueError("crop_id is required")
    if not symptoms:
        raise ValueError("symptoms list cannot be empty")
    if budget_level not in ("low", "medium", "high"):
        raise ValueError("budget_level must be low / medium / high")

    query_tokens = set()
    for s in symptoms:
        query_tokens |= _tokenise(s)

    candidates = []
    urgency_map = {"critical": "immediate", "high": "monitor", "medium": "low", "low": "low"}

    for pest in PESTS_BY_CROP.get(crop_id, []):
        score, matched = _score_symptoms(pest, query_tokens)
        if score == 0 or not matched:
            continue
        in_season   = month in pest.get("season_risk", list(range(1,13)))
        sev_weight  = SEVERITY_WEIGHTS.get(pest["severity"], 1.0)
        season_boost= 1.3 if in_season else 0.7
        weighted    = score * sev_weight * season_boost
        candidates.append({
            "id":               pest["id"],
            "category":         "pest",
            "name":             pest["common_name"],
            "scientific_name":  pest.get("scientific_name",""),
            "confidence_pct":   min(99, round(weighted * 35)),
            "matched_symptoms": matched,
            "severity":         pest["severity"],
            "in_season":        in_season,
            "scouting_method":  pest.get("scouting_method",""),
            "treatments":       _filter_treatments(pest.get("treatments",[]), budget_level),
            "prevention":       pest.get("prevention",[]),
            "urgency":          urgency_map.get(pest["severity"], "low"),
        })

    for disease in DISEASES_BY_CROP.get(crop_id, []):
        score, matched = _score_symptoms(disease, query_tokens)
        if score == 0 or not matched:
            continue
        sev_weight = SEVERITY_WEIGHTS.get(disease["severity"], 1.0)
        weighted   = score * sev_weight
        candidates.append({
            "id":               disease["id"],
            "category":         "disease",
            "name":             disease["common_name"],
            "scientific_name":  disease.get("scientific_name",""),
            "confidence_pct":   min(99, round(weighted * 35)),
            "matched_symptoms": matched,
            "severity":         disease["severity"],
            "in_season":        True,
            "scouting_method":  disease.get("scouting_method",""),
            "treatments":       _filter_treatments(disease.get("treatments",[]), budget_level),
            "prevention":       disease.get("prevention",[]),
            "urgency":          urgency_map.get(disease["severity"], "low"),
        })

    urgency_order = {"immediate": 0, "monitor": 1, "low": 2}
    candidates.sort(key=lambda c: (-c["confidence_pct"], urgency_order.get(c["urgency"],3)))
    return candidates[:top_n]


# ── MODE 3: TREATMENT PLAN ────────────────────────────────────────────────────

def get_treatment_plan(
    pest_disease_id: str,
    budget_level:    str,
    farm_size_ha:    float,
) -> TreatmentPlan:
    if budget_level not in ("low", "medium", "high"):
        raise ValueError("budget_level must be low / medium / high")
    if farm_size_ha <= 0:
        raise ValueError("farm_size_ha must be positive")

    record = PEST_BY_ID.get(pest_disease_id) or DISEASE_BY_ID.get(pest_disease_id)
    if not record:
        raise ValueError(f"ID '{pest_disease_id}' not found in pest or disease database.")

    category   = "pest" if pest_disease_id.startswith("PEST") else "disease"
    treatments = _filter_treatments(record.get("treatments",[]), budget_level)
    if not treatments:
        treatments = record.get("treatments", [])

    recommended, total_cost = [], 0.0
    for t in treatments:
        product  = t.get("product","Unknown")
        rate_str = t.get("rate","")
        unit_cost= _estimate_product_cost(product)
        amount   = _parse_rate_to_amount(rate_str, farm_size_ha)
        cost     = unit_cost * amount
        recommended.append({
            "type":                t.get("type","chemical"),
            "product":             product,
            "rate":                rate_str,
            "timing":              t.get("timing",""),
            "notes":               t.get("notes",""),
            "estimated_cost_usd":  round(cost, 2),
        })
        total_cost += cost

    severity = record.get("severity","medium")
    notes = []
    if severity == "critical":
        notes.append("URGENT: Apply treatment within 24 hours. Delay risks significant crop loss.")
    notes += [
        "Apply in early morning or late afternoon — heat reduces product effectiveness.",
        "Ensure good spray coverage — wet all leaf surfaces including undersides.",
        f"Calibrate sprayer for {farm_size_ha:.1f} ha. Incorrect calibration wastes product.",
        "Use clean water. Alkaline water reduces effectiveness of many pesticides.",
    ]
    if any(t.get("type") == "chemical" for t in record.get("treatments",[])):
        notes.append("Wear full PPE: gloves, goggles, respirator during application.")
        notes.append("Observe pre-harvest interval (PHI) from product label.")
    notes.append("Record date, product, rate, and weather in your farm diary.")
    et = record.get("economic_threshold","")
    if et:
        notes.append(f"Retreat if: {et}")

    return TreatmentPlan(
        pest_disease_id     = pest_disease_id,
        name                = record.get("common_name","Unknown"),
        category            = category,
        severity            = severity,
        farm_size_ha        = farm_size_ha,
        budget_level        = budget_level,
        recommended_products= recommended,
        total_cost_usd      = total_cost,
        application_notes   = notes,
        organic_only        = (budget_level == "low"),
    )
