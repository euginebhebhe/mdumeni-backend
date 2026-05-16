# mdumeni-backend/market_api.py
# Market intelligence endpoints — prices, suppliers, profit calculator
# These are imported and registered in main.py

import os
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/market", tags=["Market Intelligence"])

def get_db():
    from db import get_db as _get_db
    return _get_db()

# ── Models ────────────────────────────────────────────────────────────────────

class PriceReportRequest(BaseModel):
    farmer_id:   str
    report_type: str = Field(..., pattern="^(crop_sell|input_buy)$")
    crop_id:     Optional[str] = None
    product_id:  Optional[str] = None
    market_id:   Optional[str] = None
    supplier_id: Optional[str] = None
    price_usd:   float = Field(..., gt=0)
    unit:        str = "kg"
    notes:       Optional[str] = None

class ProfitCalcRequest(BaseModel):
    crop_id:      str
    crop_name:    str
    farm_size_ha: float = Field(..., gt=0)
    budget_level: str = Field("low", pattern="^(low|medium|high)$")
    agro_region:  int = Field(..., ge=1, le=5)
    has_irrigation: bool = False
    planting_month: int = Field(..., ge=1, le=12)

# ── Crop prices ───────────────────────────────────────────────────────────────

@router.get("/prices/crops")
def get_crop_prices(
    crop_id:  Optional[str] = Query(None),
    province: Optional[str] = Query(None),
    limit:    int = Query(50, le=200),
):
    """
    Get today's best sell prices for all crops across all markets.
    Optionally filter by crop_id or province.
    """
    db = get_db()

    try:
        query = db.table("market_prices") \
            .select("*, markets(id, name, type, province, district, lat, lng, payment_methods, min_quantity_kg)") \
            .gte("price_date", str(date.today() - timedelta(days=3))) \
            .order("price_usd_kg", desc=True) \
            .limit(limit)

        if crop_id:
            query = query.eq("crop_id", crop_id)

        result = query.execute()
        prices = result.data or []

        # If province filter — filter after fetch
        if province and prices:
            prices = [p for p in prices
                      if p.get("markets", {}).get("province", "").lower() == province.lower()]

        # Add 7-day change from older prices
        return {"prices": prices, "date": str(date.today()), "count": len(prices)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price fetch error: {str(e)}")


@router.get("/prices/crops/best")
def get_best_crop_prices():
    """
    Best price per crop across all markets today — one row per crop.
    Used for the Market tab overview.
    """
    db = get_db()
    try:
        result = db.table("market_prices") \
            .select("crop_id, crop_name, price_usd_kg, market_id, markets(name, type, province, district)") \
            .gte("price_date", str(date.today() - timedelta(days=3))) \
            .order("price_usd_kg", desc=True) \
            .execute()

        # Keep only best price per crop
        seen = {}
        best = []
        for row in (result.data or []):
            cid = row["crop_id"]
            if cid not in seen:
                seen[cid] = True
                best.append(row)

        return {"prices": best, "date": str(date.today())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price fetch error: {str(e)}")


@router.get("/prices/crops/{crop_id}/trend")
def get_crop_price_trend(crop_id: str, days: int = Query(30, le=90)):
    """
    Price trend for a specific crop over N days — for chart display.
    """
    db = get_db()
    try:
        since = str(date.today() - timedelta(days=days))
        result = db.table("market_prices") \
            .select("price_usd_kg, price_date, market_id, markets(name)") \
            .eq("crop_id", crop_id) \
            .gte("price_date", since) \
            .order("price_date", desc=False) \
            .execute()

        data = result.data or []

        # Aggregate: average price per day
        by_date: dict = {}
        for row in data:
            d = row["price_date"]
            if d not in by_date:
                by_date[d] = []
            by_date[d].append(row["price_usd_kg"])

        trend = [
            {"date": d, "avg_price": round(sum(v) / len(v), 4), "min": min(v), "max": max(v)}
            for d, v in sorted(by_date.items())
        ]

        # Calculate trend direction
        if len(trend) >= 7:
            recent  = sum(t["avg_price"] for t in trend[-7:]) / 7
            earlier = sum(t["avg_price"] for t in trend[:7]) / 7
            change_pct = round((recent - earlier) / earlier * 100, 1) if earlier > 0 else 0
        else:
            change_pct = 0

        return {"crop_id": crop_id, "days": days, "trend": trend,
                "change_pct": change_pct,
                "recommendation": "Hold — price rising" if change_pct > 5
                                  else "Sell now — price falling" if change_pct < -5
                                  else "Market stable"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend fetch error: {str(e)}")


@router.get("/prices/crops/{crop_id}/buyers")
def get_crop_buyers(
    crop_id:     str,
    farmer_lat:  Optional[float] = Query(None),
    farmer_lng:  Optional[float] = Query(None),
    min_price:   Optional[float] = Query(None),
):
    """
    All buyers for a specific crop today, sorted by price (highest first).
    Used for the 'Where to sell' feature.
    """
    db = get_db()
    try:
        result = db.table("market_prices") \
            .select("price_usd_kg, quality_grade, markets(id, name, type, province, district, lat, lng, phone, payment_methods, min_quantity_kg)") \
            .eq("crop_id", crop_id) \
            .gte("price_date", str(date.today() - timedelta(days=3))) \
            .order("price_usd_kg", desc=True) \
            .execute()

        buyers = result.data or []

        if min_price:
            buyers = [b for b in buyers if b["price_usd_kg"] >= min_price]

        # Add distance if farmer location provided
        if farmer_lat and farmer_lng:
            import math
            for b in buyers:
                m = b.get("markets", {})
                if m.get("lat") and m.get("lng"):
                    dlat = math.radians(m["lat"] - farmer_lat)
                    dlng = math.radians(m["lng"] - farmer_lng)
                    a = math.sin(dlat/2)**2 + math.cos(math.radians(farmer_lat)) * \
                        math.cos(math.radians(m["lat"])) * math.sin(dlng/2)**2
                    b["distance_km"] = round(6371 * 2 * math.asin(math.sqrt(a)), 1)
                else:
                    b["distance_km"] = None

        return {"crop_id": crop_id, "buyers": buyers, "count": len(buyers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Buyer fetch error: {str(e)}")


# ── Input prices ──────────────────────────────────────────────────────────────

@router.get("/prices/inputs")
def get_input_prices(
    category:   Optional[str] = Query(None),  # fertiliser|seed|chemical|machinery|equipment
    product_id: Optional[str] = Query(None),
    district:   Optional[str] = Query(None),
    limit:      int = Query(100, le=500),
):
    """
    Input prices from all suppliers today.
    Returns cheapest option per product first.
    """
    db = get_db()
    try:
        query = db.table("input_prices") \
            .select("*, suppliers(id, name, branch, province, district, lat, lng, phone)") \
            .gte("price_date", str(date.today() - timedelta(days=3))) \
            .eq("is_available", True) \
            .order("price_usd", desc=False) \
            .limit(limit)

        if category:
            query = query.eq("category", category)
        if product_id:
            query = query.eq("product_id", product_id)

        result = query.execute()
        inputs = result.data or []

        if district:
            inputs = [i for i in inputs
                      if i.get("suppliers", {}).get("district", "").lower() == district.lower()]

        # Group by product_id with cheapest first
        grouped: dict = {}
        for item in inputs:
            pid = item["product_id"]
            if pid not in grouped:
                grouped[pid] = {"product_id": pid, "product_name": item["product_name"],
                                "category": item["category"], "unit": item["unit"],
                                "unit_size": item["unit_size"], "options": []}
            grouped[pid]["options"].append({
                "price_usd":    item["price_usd"],
                "supplier":     item.get("suppliers", {}),
                "source":       item["source"],
                "price_date":   item["price_date"],
            })

        return {"inputs": list(grouped.values()), "date": str(date.today())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Input price fetch error: {str(e)}")


@router.get("/prices/inputs/cheapest")
def get_cheapest_inputs(category: Optional[str] = Query(None)):
    """
    Single cheapest option per product across all suppliers today.
    Used for the Plan tab cost calculation.
    """
    db = get_db()
    try:
        query = db.table("input_prices") \
            .select("product_id, product_name, category, price_usd, unit, unit_size, suppliers(name, branch, district, phone)") \
            .gte("price_date", str(date.today() - timedelta(days=3))) \
            .eq("is_available", True) \
            .order("price_usd", desc=False)

        if category:
            query = query.eq("category", category)

        result = query.execute()
        inputs = result.data or []

        # Keep cheapest per product
        seen: dict = {}
        cheapest = []
        for item in inputs:
            pid = item["product_id"]
            if pid not in seen:
                seen[pid] = True
                cheapest.append(item)

        return {"inputs": cheapest, "date": str(date.today())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cheapest input fetch error: {str(e)}")


# ── Profit calculator ─────────────────────────────────────────────────────────

@router.post("/profit/calculate")
def calculate_profit(req: ProfitCalcRequest):
    """
    Full profit calculation using today's live market prices.
    Input costs pulled from cheapest supplier.
    Revenue based on best market price.
    """
    db = get_db()
    try:
        # ── Get best sell price for this crop ────────────────────────────────
        price_result = db.table("market_prices") \
            .select("price_usd_kg, markets(name, type)") \
            .eq("crop_id", req.crop_id) \
            .gte("price_date", str(date.today() - timedelta(days=3))) \
            .order("price_usd_kg", desc=True) \
            .limit(1) \
            .execute()

        best_price_row = price_result.data[0] if price_result.data else None
        sell_price_kg = best_price_row["price_usd_kg"] if best_price_row else None

        # ── Get cheapest input prices for this crop/budget ────────────────────
        input_result = db.table("input_prices") \
            .select("product_id, product_name, category, price_usd, unit, unit_size") \
            .gte("price_date", str(date.today() - timedelta(days=3))) \
            .eq("is_available", True) \
            .order("price_usd", desc=False) \
            .execute()

        inputs_raw = input_result.data or []

        # Build cheapest map
        cheapest: dict = {}
        for item in inputs_raw:
            pid = item["product_id"]
            if pid not in cheapest:
                cheapest[pid] = item

        # ── Calculate input costs per hectare ─────────────────────────────────
        # Standard input packages by crop and budget level
        CROP_INPUTS = {
            "CROP_001": {  # Maize
                "low":    [("INP_COMP_D_50", 4, "Compound D 4 bags/ha"),
                           ("INP_AN_345_50", 4, "AN 34.5% 4 bags/ha"),
                           ("INP_SEED_ZM521", 2.5, "ZM521 seed 25kg/ha")],
                "medium": [("INP_COMP_D_50", 4, "Compound D 4 bags/ha"),
                           ("INP_AN_345_50", 4, "AN 34.5% 4 bags/ha"),
                           ("INP_SEED_SC403", 2.5, "SC403 seed 25kg/ha"),
                           ("INP_ATRAZINE_1L", 2.5, "Atrazine 2.5L/ha"),
                           ("INP_CHLORPYR_1L", 1.5, "Insecticide 1.5L/ha")],
                "high":   [("INP_COMP_D_50", 4, "Compound D 4 bags/ha"),
                           ("INP_AN_345_50", 4, "AN 34.5% 4 bags/ha"),
                           ("INP_SEED_SC627", 2.5, "SC627 seed 25kg/ha"),
                           ("INP_ATRAZINE_1L", 2.5, "Atrazine 2.5L/ha"),
                           ("INP_NICOSULF_1L", 1, "Nicosulfuron 1L/ha"),
                           ("INP_CHLORPYR_1L", 1.5, "Insecticide 1.5L/ha")],
            },
            "CROP_002": {  # Sugar beans
                "low":    [("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_SEED_SB_1KG", 80, "Sugar bean seed 80kg/ha")],
                "medium": [("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_SEED_SB_PAN", 80, "PAN 9216 seed 80kg/ha"),
                           ("INP_MANCOZEB_1KG", 2, "Fungicide 2kg/ha"),
                           ("INP_CHLORPYR_1L", 1, "Insecticide 1L/ha")],
                "high":   [("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_AN_345_50", 1, "AN 34.5% 1 bag/ha"),
                           ("INP_SEED_SB_PAN", 80, "PAN 9216 seed 80kg/ha"),
                           ("INP_MANCOZEB_1KG", 3, "Fungicide 3kg/ha"),
                           ("INP_DIMETHOATE_1L", 1, "Aphid control 1L/ha"),
                           ("INP_CHLORPYR_1L", 1, "Insecticide 1L/ha")],
            },
            "CROP_003": {  # Groundnuts
                "low":    [("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_SEED_GN_1KG", 80, "Groundnut seed 80kg/ha")],
                "medium": [("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_SEED_GN_1KG", 80, "Groundnut seed 80kg/ha"),
                           ("INP_CHLORPYR_1L", 1, "Insecticide 1L/ha"),
                           ("INP_MANCOZEB_1KG", 2, "Fungicide 2kg/ha")],
                "high":   [("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_AN_345_50", 1, "AN 34.5% 1 bag/ha"),
                           ("INP_SEED_GN_1KG", 80, "Groundnut seed 80kg/ha"),
                           ("INP_CHLORPYR_1L", 1.5, "Insecticide 1.5L/ha"),
                           ("INP_MANCOZEB_1KG", 3, "Fungicide 3kg/ha")],
            },

        # Sorghum
            "CROP_006": {
                "low":    [("INP_SEED_SG_1KG", 10, "Sorghum seed 10kg/ha"),
                           ("INP_COMP_D_50", 2, "Compound D 2 bags/ha")],
                "medium": [("INP_SEED_SG_1KG", 10, "Sorghum seed 10kg/ha"),
                           ("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_AN_345_50", 2, "AN 34.5% 2 bags/ha"),
                           ("INP_CHLORPYR_1L", 1, "Insecticide 1L/ha")],
                "high":   [("INP_SEED_SG_1KG", 10, "Sorghum seed 10kg/ha"),
                           ("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_AN_345_50", 2, "AN 34.5% 2 bags/ha"),
                           ("INP_CHLORPYR_1L", 1.5, "Insecticide 1.5L/ha"),
                           ("INP_MANCOZEB_1KG", 1, "Fungicide 1kg/ha")],
            },
            # Soybeans
            "CROP_009": {
                "low":    [("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_SEED_SB_1KG", 80, "Soybean seed 80kg/ha")],
                "medium": [("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_SEED_SB_1KG", 80, "Soybean seed 80kg/ha"),
                           ("INP_CHLORPYR_1L", 1, "Insecticide 1L/ha"),
                           ("INP_GLYPHOSATE_1L", 1, "Herbicide 1L/ha")],
                "high":   [("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_AN_345_50", 1, "AN 34.5% 1 bag/ha"),
                           ("INP_SEED_SB_1KG", 80, "Soybean seed 80kg/ha"),
                           ("INP_CHLORPYR_1L", 1.5, "Insecticide 1.5L/ha"),
                           ("INP_MANCOZEB_1KG", 2, "Fungicide 2kg/ha"),
                           ("INP_GLYPHOSATE_1L", 1, "Herbicide 1L/ha")],
            },
            # Tomatoes
            "CROP_019": {
                "low":    [("INP_COMP_D_50", 3, "Compound D 3 bags/ha"),
                           ("INP_CHLORPYR_1L", 2, "Insecticide 2L/ha"),
                           ("INP_MANCOZEB_1KG", 3, "Fungicide 3kg/ha")],
                "medium": [("INP_COMP_D_50", 3, "Compound D 3 bags/ha"),
                           ("INP_AN_345_50", 2, "AN 34.5% 2 bags/ha"),
                           ("INP_CHLORPYR_1L", 3, "Insecticide 3L/ha"),
                           ("INP_MANCOZEB_1KG", 4, "Fungicide 4kg/ha"),
                           ("INP_DIMETHOATE_1L", 1, "Aphid control 1L/ha")],
                "high":   [("INP_COMP_D_50", 4, "Compound D 4 bags/ha"),
                           ("INP_AN_345_50", 3, "AN 34.5% 3 bags/ha"),
                           ("INP_CHLORPYR_1L", 4, "Insecticide 4L/ha"),
                           ("INP_MANCOZEB_1KG", 6, "Fungicide 6kg/ha"),
                           ("INP_DIMETHOATE_1L", 2, "Aphid control 2L/ha"),
                           ("INP_LAMBDA_1L", 1, "Lambda 1L/ha")],
            },
            # Onions
            "CROP_020": {
                "low":    [("INP_COMP_D_50", 3, "Compound D 3 bags/ha"),
                           ("INP_CHLORPYR_1L", 1, "Insecticide 1L/ha")],
                "medium": [("INP_COMP_D_50", 3, "Compound D 3 bags/ha"),
                           ("INP_AN_345_50", 2, "AN 34.5% 2 bags/ha"),
                           ("INP_CHLORPYR_1L", 2, "Insecticide 2L/ha"),
                           ("INP_MANCOZEB_1KG", 3, "Fungicide 3kg/ha")],
                "high":   [("INP_COMP_D_50", 4, "Compound D 4 bags/ha"),
                           ("INP_AN_345_50", 3, "AN 34.5% 3 bags/ha"),
                           ("INP_CHLORPYR_1L", 3, "Insecticide 3L/ha"),
                           ("INP_MANCOZEB_1KG", 4, "Fungicide 4kg/ha"),
                           ("INP_DIMETHOATE_1L", 2, "Aphid control 2L/ha")],
            },
            # Sunflower
            "CROP_010": {
                "low":    [("INP_COMP_D_50", 2, "Compound D 2 bags/ha")],
                "medium": [("INP_COMP_D_50", 2, "Compound D 2 bags/ha"),
                           ("INP_AN_345_50", 2, "AN 34.5% 2 bags/ha"),
                           ("INP_CHLORPYR_1L", 1, "Insecticide 1L/ha")],
                "high":   [("INP_COMP_D_50", 3, "Compound D 3 bags/ha"),
                           ("INP_AN_345_50", 3, "AN 34.5% 3 bags/ha"),
                           ("INP_CHLORPYR_1L", 1.5, "Insecticide 1.5L/ha"),
                           ("INP_MANCOZEB_1KG", 2, "Fungicide 2kg/ha")],
            },
            # Cotton
            "CROP_011": {
                "low":    [("INP_COMP_D_50", 4, "Compound D 4 bags/ha"),
                           ("INP_CHLORPYR_1L", 3, "Insecticide 3L/ha")],
                "medium": [("INP_COMP_D_50", 4, "Compound D 4 bags/ha"),
                           ("INP_AN_345_50", 3, "AN 34.5% 3 bags/ha"),
                           ("INP_CHLORPYR_1L", 4, "Insecticide 4L/ha"),
                           ("INP_LAMBDA_1L", 2, "Lambda 2L/ha")],
                "high":   [("INP_COMP_D_50", 4, "Compound D 4 bags/ha"),
                           ("INP_AN_345_50", 4, "AN 34.5% 4 bags/ha"),
                           ("INP_CHLORPYR_1L", 5, "Insecticide 5L/ha"),
                           ("INP_LAMBDA_1L", 3, "Lambda 3L/ha"),
                           ("INP_DIMETHOATE_1L", 2, "Aphid control 2L/ha")],
            },
        }

        # Additional yield table entries
        YIELD_TABLE.update({
            "CROP_006": {1:{1:5.0,2:3.5,3:2.0},2:{1:6.0,2:4.0,3:2.5},
                         3:{1:3.5,2:2.5,3:1.5},4:{1:2.5,2:1.8,3:1.2},5:{1:1.5,2:1.0,3:0.7}},
            "CROP_009": {1:{1:4.0,2:3.0,3:1.8},2:{1:5.0,2:3.5,3:2.0},
                         3:{1:3.0,2:2.0,3:1.3},4:{1:2.0,2:1.4,3:0.9},5:{1:1.0,2:0.7,3:0.5}},
            "CROP_019": {1:{1:50.0,2:35.0,3:20.0},2:{1:60.0,2:40.0,3:25.0},
                         3:{1:40.0,2:28.0,3:18.0},4:{1:25.0,2:18.0,3:12.0},5:{1:15.0,2:10.0,3:7.0}},
            "CROP_020": {1:{1:30.0,2:22.0,3:14.0},2:{1:35.0,2:25.0,3:16.0},
                         3:{1:25.0,2:18.0,3:12.0},4:{1:18.0,2:13.0,3:8.0},5:{1:12.0,2:8.0,3:5.0}},
            "CROP_010": {1:{1:3.0,2:2.2,3:1.4},2:{1:3.5,2:2.5,3:1.6},
                         3:{1:2.5,2:1.8,3:1.1},4:{1:1.8,2:1.3,3:0.8},5:{1:1.0,2:0.7,3:0.5}},
            "CROP_011": {1:{1:4.0,2:3.0,3:2.0},2:{1:5.0,2:3.5,3:2.2},
                         3:{1:3.5,2:2.5,3:1.6},4:{1:2.5,2:1.8,3:1.2},5:{1:1.5,2:1.0,3:0.7}},
        })

                # Default input package for crops not in map
        DEFAULT_INPUTS = {
            "low":    [("INP_COMP_D_50", 3, "Compound D 3 bags/ha")],
            "medium": [("INP_COMP_D_50", 3, "Compound D 3 bags/ha"),
                       ("INP_AN_345_50", 2, "AN 34.5% 2 bags/ha")],
            "high":   [("INP_COMP_D_50", 4, "Compound D 4 bags/ha"),
                       ("INP_AN_345_50", 4, "AN 34.5% 4 bags/ha")],
        }

        crop_pkg = CROP_INPUTS.get(req.crop_id, DEFAULT_INPUTS)
        pkg = crop_pkg.get(req.budget_level, crop_pkg.get("low", []))

        # Calculate input cost per hectare
        input_lines = []
        input_cost_per_ha = 0.0
        for product_id, qty_per_ha, label in pkg:
            price_item = cheapest.get(product_id)
            if price_item:
                line_cost = price_item["price_usd"] * qty_per_ha
                input_cost_per_ha += line_cost
                input_lines.append({
                    "product":    label,
                    "product_id": product_id,
                    "qty":        qty_per_ha,
                    "unit_price": price_item["price_usd"],
                    "total":      round(line_cost, 2),
                })

        # Labour cost (standard Zimbabwe rate)
        LABOUR = {"low": 18, "medium": 22, "high": 28}
        labour_per_ha = LABOUR.get(req.budget_level, 18)

        # Land prep
        land_prep_per_ha = 55.0  # tractor plough + disc

        # Contingency 8%
        subtotal = input_cost_per_ha + labour_per_ha + land_prep_per_ha
        contingency = round(subtotal * 0.08, 2)
        total_cost_per_ha = subtotal + contingency

        # Scale to farm size
        total_cost = round(total_cost_per_ha * req.farm_size_ha, 2)

        # ── Yield estimates (t/ha by region and budget) ───────────────────────
        YIELD_TABLE = {
            "CROP_001": {1: {1: 6.0, 2: 4.5, 3: 3.0}, 2: {1: 8.0, 2: 6.0, 3: 4.5},
                         3: {1: 4.0, 2: 3.0, 3: 2.0}, 4: {1: 2.5, 2: 2.0, 3: 1.5},
                         5: {1: 1.5, 2: 1.2, 3: 0.8}},
            "CROP_002": {1: {1: 2.0, 2: 1.5, 3: 0.9}, 2: {1: 2.5, 2: 1.8, 3: 1.0},
                         3: {1: 1.8, 2: 1.2, 3: 0.7}, 4: {1: 1.2, 2: 0.9, 3: 0.6},
                         5: {1: 0.8, 2: 0.6, 3: 0.4}},
            "CROP_003": {1: {1: 3.0, 2: 2.2, 3: 1.4}, 2: {1: 3.5, 2: 2.5, 3: 1.6},
                         3: {1: 2.5, 2: 1.8, 3: 1.2}, 4: {1: 1.8, 2: 1.4, 3: 0.9},
                         5: {1: 1.2, 2: 0.9, 3: 0.6}},
        }

        budget_num = {"low": 3, "medium": 2, "high": 1}[req.budget_level]
        region = min(max(req.agro_region, 1), 5)
        crop_yield_table = YIELD_TABLE.get(req.crop_id, YIELD_TABLE["CROP_001"])
        yield_t_ha = crop_yield_table.get(region, {}).get(budget_num, 2.0)
        total_yield_kg = round(yield_t_ha * 1000 * req.farm_size_ha, 0)

        # ── Revenue and profit ────────────────────────────────────────────────
        if sell_price_kg:
            gross_revenue = round(total_yield_kg * sell_price_kg, 2)
            net_profit    = round(gross_revenue - total_cost, 2)
            roi_pct       = round((net_profit / total_cost) * 100, 1) if total_cost > 0 else 0
            break_even_kg = round(total_cost / sell_price_kg, 0) if sell_price_kg > 0 else None
        else:
            gross_revenue = None
            net_profit    = None
            roi_pct       = None
            break_even_kg = None

        return {
            "crop_id":       req.crop_id,
            "crop_name":     req.crop_name,
            "farm_size_ha":  req.farm_size_ha,
            "budget_level":  req.budget_level,
            "agro_region":   req.agro_region,
            "price_date":    str(date.today()),

            # Yield
            "yield_t_ha":      yield_t_ha,
            "total_yield_kg":  total_yield_kg,

            # Prices
            "best_sell_price_kg": sell_price_kg,
            "best_market":        best_price_row["markets"]["name"] if best_price_row else None,

            # Costs
            "input_lines":       input_lines,
            "input_cost_per_ha": round(input_cost_per_ha, 2),
            "labour_per_ha":     labour_per_ha,
            "land_prep_per_ha":  land_prep_per_ha,
            "contingency_8pct":  contingency,
            "total_cost_per_ha": round(total_cost_per_ha, 2),
            "total_cost":        total_cost,

            # Revenue
            "gross_revenue":  gross_revenue,
            "net_profit":     net_profit,
            "roi_pct":        roi_pct,
            "break_even_kg":  break_even_kg,

            # Summary
            "is_profitable":  net_profit > 0 if net_profit is not None else None,
            "verdict": (
                f"Profitable — ${net_profit:,.0f} net profit at {roi_pct:.0f}% ROI"
                if net_profit and net_profit > 0
                else "Not profitable at current prices — consider a different crop"
                if net_profit is not None and net_profit <= 0
                else "Cannot calculate — no sell price data available"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profit calculation error: {str(e)}")


# ── Markets ───────────────────────────────────────────────────────────────────

@router.get("/markets")
def get_markets(
    type:     Optional[str] = Query(None),
    province: Optional[str] = Query(None),
):
    """All active markets, optionally filtered by type or province."""
    db = get_db()
    try:
        query = db.table("markets").select("*").eq("is_active", True).order("name")
        if type:
            query = query.eq("type", type)
        if province:
            query = query.eq("province", province)
        result = query.execute()
        return {"markets": result.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suppliers")
def get_suppliers(
    type:     Optional[str] = Query(None),
    province: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
):
    """All active suppliers, optionally filtered."""
    db = get_db()
    try:
        query = db.table("suppliers").select("*").eq("is_active", True).order("name")
        if type:
            query = query.eq("type", type)
        if province:
            query = query.eq("province", province)
        if district:
            query = query.eq("district", district)
        result = query.execute()
        return {"suppliers": result.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Price reporting (crowdsource) ─────────────────────────────────────────────

@router.post("/prices/report")
def report_price(req: PriceReportRequest):
    """
    Farmer submits a price they saw at their local market.
    Feeds the crowd-sourced price network.
    """
    db = get_db()
    try:
        # Save the report
        db.table("price_reports").insert({
            "farmer_id":   req.farmer_id,
            "report_type": req.report_type,
            "crop_id":     req.crop_id,
            "product_id":  req.product_id,
            "market_id":   req.market_id,
            "supplier_id": req.supplier_id,
            "price_usd":   req.price_usd,
            "unit":        req.unit,
            "notes":       req.notes,
        }).execute()

        # Auto-add to market_prices if crop_sell and market provided
        if req.report_type == "crop_sell" and req.crop_id and req.market_id:
            # Get crop name from existing prices
            existing = db.table("market_prices") \
                .select("crop_name").eq("crop_id", req.crop_id).limit(1).execute()
            crop_name = existing.data[0]["crop_name"] if existing.data else req.crop_id

            db.table("market_prices").insert({
                "crop_id":      req.crop_id,
                "crop_name":    crop_name,
                "market_id":    req.market_id,
                "price_usd_kg": req.price_usd,
                "source":       "crowdsourced",
                "reporter_id":  req.farmer_id,
                "price_date":   str(date.today()),
            }).execute()

        # Auto-add to input_prices if input_buy and supplier provided
        if req.report_type == "input_buy" and req.product_id and req.supplier_id:
            existing = db.table("input_prices") \
                .select("product_name, category, unit, unit_size") \
                .eq("product_id", req.product_id).limit(1).execute()
            if existing.data:
                p = existing.data[0]
                db.table("input_prices").insert({
                    "product_id":   req.product_id,
                    "product_name": p["product_name"],
                    "category":     p["category"],
                    "supplier_id":  req.supplier_id,
                    "price_usd":    req.price_usd,
                    "unit":         p.get("unit", req.unit),
                    "unit_size":    p.get("unit_size"),
                    "source":       "crowdsourced",
                    "price_date":   str(date.today()),
                }).execute()

        return {"status": "reported", "message": "Thank you — your price helps all farmers."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price report error: {str(e)}")


# ── Market summary for home screen ───────────────────────────────────────────

@router.get("/summary")
def get_market_summary():
    """
    Quick market summary for the Home screen top tiles.
    Returns top 5 crops with best price and 24h change.
    """
    db = get_db()
    try:
        today    = str(date.today())
        yesterday = str(date.today() - timedelta(days=1))

        today_result = db.table("market_prices") \
            .select("crop_id, crop_name, price_usd_kg") \
            .gte("price_date", str(date.today() - timedelta(days=3))) \
            .order("price_usd_kg", desc=True) \
            .execute()

        # Best price per crop today
        seen_today: dict = {}
        for row in (today_result.data or []):
            cid = row["crop_id"]
            if cid not in seen_today:
                seen_today[cid] = row

        # Yesterday prices for change calc
        yest_result = db.table("market_prices") \
            .select("crop_id, price_usd_kg") \
            .lt("price_date", today) \
            .gte("price_date", str(date.today() - timedelta(days=5))) \
            .execute()

        seen_yest: dict = {}
        for row in (yest_result.data or []):
            cid = row["crop_id"]
            if cid not in seen_yest:
                seen_yest[cid] = row

        summary = []
        PRIORITY = ["CROP_002","CROP_001","CROP_003","CROP_016","CROP_019","CROP_020","CROP_009","CROP_006"]
        for cid in PRIORITY:
            if cid in seen_today:
                t = seen_today[cid]
                y = seen_yest.get(cid)
                change_pct = None
                if y and y["price_usd_kg"]:
                    change_pct = round(
                        (t["price_usd_kg"] - y["price_usd_kg"]) / y["price_usd_kg"] * 100, 1
                    )
                summary.append({
                    "crop_id":     t["crop_id"],
                    "crop_name":   t["crop_name"],
                    "price_usd_kg": t["price_usd_kg"],
                    "change_pct":  change_pct,
                    "trend":       "up" if change_pct and change_pct > 0
                                   else "down" if change_pct and change_pct < 0
                                   else "flat",
                })

        return {"summary": summary[:6], "date": today}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary error: {str(e)}")


# ── Price alerts ──────────────────────────────────────────────────────────────

class AlertRequest(BaseModel):
    farmer_id:     str
    alert_type:    str = Field(..., pattern="^(crop_sell|input_buy)$")
    crop_id:       Optional[str] = None
    product_id:    Optional[str] = None
    condition:     str = Field(..., pattern="^(above|below)$")
    threshold_usd: float = Field(..., gt=0)

@router.post("/alerts")
def create_alert(req: AlertRequest):
    """Farmer sets a price alert threshold."""
    db = get_db()
    try:
        result = db.table("price_alerts").insert({
            "farmer_id":     req.farmer_id,
            "alert_type":    req.alert_type,
            "crop_id":       req.crop_id,
            "product_id":    req.product_id,
            "condition":     req.condition,
            "threshold_usd": req.threshold_usd,
            "is_active":     True,
        }).execute()
        return {"status": "created", "id": result.data[0]["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/{farmer_id}")
def get_alerts(farmer_id: str):
    """Get all active price alerts for a farmer."""
    db = get_db()
    try:
        result = db.table("price_alerts") \
            .select("*").eq("farmer_id", farmer_id).eq("is_active", True) \
            .order("created_at", desc=True).execute()
        return {"alerts": result.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: str):
    """Deactivate a price alert."""
    db = get_db()
    try:
        db.table("price_alerts").update({"is_active": False}).eq("id", alert_id).execute()
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/check/{farmer_id}")
def check_alerts(farmer_id: str):
    """
    Check if any of the farmer's price alerts have been triggered today.
    Called by the mobile app on startup and after each price refresh.
    Returns triggered alerts with the current price.
    """
    db = get_db()
    try:
        # Get farmer's active alerts
        alerts_r = db.table("price_alerts") \
            .select("*").eq("farmer_id", farmer_id).eq("is_active", True).execute()
        alerts = alerts_r.data or []
        if not alerts:
            return {"triggered": []}

        triggered = []
        for alert in alerts:
            if alert["alert_type"] == "crop_sell" and alert.get("crop_id"):
                # Get current best price for this crop
                price_r = db.table("market_prices") \
                    .select("price_usd_kg, crop_name, markets(name)") \
                    .eq("crop_id", alert["crop_id"]) \
                    .gte("price_date", str(date.today() - timedelta(days=3))) \
                    .order("price_usd_kg", desc=True).limit(1).execute()

                if price_r.data:
                    current = price_r.data[0]["price_usd_kg"]
                    threshold = alert["threshold_usd"]
                    market = price_r.data[0].get("markets", {}).get("name", "")
                    crop_name = price_r.data[0]["crop_name"]

                    triggered_flag = (
                        (alert["condition"] == "above" and current >= threshold) or
                        (alert["condition"] == "below" and current <= threshold)
                    )
                    if triggered_flag:
                        triggered.append({
                            "alert_id":     alert["id"],
                            "crop_name":    crop_name,
                            "condition":    alert["condition"],
                            "threshold":    threshold,
                            "current_price": current,
                            "market":       market,
                            "message": (
                                f"{crop_name} is now ${current:.3f}/kg at {market} — "
                                f"{'above' if alert['condition'] == 'above' else 'below'} "
                                f"your ${threshold:.3f} alert."
                            ),
                        })

        return {"triggered": triggered, "checked_at": str(date.today())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
