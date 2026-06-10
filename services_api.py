"""
MDUMENI — Agricultural Services API
=====================================
Provides GPS-accurate nearby-services search backed by the same province
JSON files that are bundled in the mobile app.

Endpoints:
  POST /services/nearby   — nearest services to a GPS point
  GET  /services/province — all services in a province (with optional type filter)
  GET  /services/district — AGRITEX office + services for a specific district

Province JSON files live in data/provinces/ alongside this file on the server.
When the mobile app is online it calls /services/nearby for GPS-sorted results.
Offline, the app uses the bundled JSON directly via provinceIndex.ts.
Both use the same data — single source of truth.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/services", tags=["Agricultural Services"])

# ── Province data loading ─────────────────────────────────────────────────────
# JSON files live at data/provinces/ relative to this module's directory.
_DATA_DIR = Path(__file__).parent / "data" / "provinces"

_province_cache: dict[str, dict] = {}

_PROVINCE_FILES: dict[str, str] = {
    "Harare":              "province_harare.json",
    "Bulawayo":            "province_bulawayo.json",
    "Manicaland":          "province_manicaland.json",
    "Mashonaland Central": "province_mashonaland_central.json",
    "Mashonaland East":    "province_mashonaland_east.json",
    "Mashonaland West":    "province_mashonaland_west.json",
    "Masvingo":            "province_masvingo.json",
    "Matabeleland North":  "province_matabeleland_north.json",
    "Matabeleland South":  "province_matabeleland_south.json",
    "Midlands":            "province_midlands.json",
}


def _load_province(province: str) -> dict | None:
    """Load and cache a province data file."""
    if province in _province_cache:
        return _province_cache[province]

    filename = _PROVINCE_FILES.get(province)
    if not filename:
        return None

    filepath = _DATA_DIR / filename
    if not filepath.exists():
        return None

    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        _province_cache[province] = data
        return data
    except (json.JSONDecodeError, OSError):
        return None


# ── Haversine distance ────────────────────────────────────────────────────────

def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(d_lng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Request / response models ─────────────────────────────────────────────────

class NearbyRequest(BaseModel):
    lat:       float  = Field(..., ge=-90,  le=90)
    lng:       float  = Field(..., ge=-180, le=180)
    province:  str    = Field(..., min_length=1)
    types:     Optional[list[str]] = None     # filter by service type(s)
    crop_id:   Optional[str]       = None     # filter to services relevant to crop
    radius_km: float               = Field(default=100.0, ge=1, le=500)
    limit:     int                 = Field(default=15, ge=1, le=50)


class ServiceResult(BaseModel):
    id:           str
    name:         str
    type:         str
    province:     str
    district:     str
    town:         str
    address:      str
    phone:        Optional[str]
    lat:          float
    lng:          float
    products:     list[str]
    seed_brands:  list[str]
    crops_served: list[str]
    open_hours:   Optional[str]
    notes:        Optional[str]
    verified:     bool
    distance_km:  float            # added by this endpoint


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/nearby", response_model=list[ServiceResult])
def services_nearby(req: NearbyRequest):
    """
    Return agricultural services near a GPS point, sorted by distance.
    Uses province JSON data files for zero-database, offline-friendly lookups.
    """
    data = _load_province(req.province)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"Province '{req.province}' not found. "
                   f"Valid provinces: {list(_PROVINCE_FILES.keys())}"
        )

    services = data.get("services", [])

    # Type filter
    if req.types:
        services = [s for s in services if s.get("type") in req.types]

    # Crop filter — services with empty crops_served serve all crops
    if req.crop_id:
        services = [
            s for s in services
            if not s.get("crops_served") or req.crop_id in s.get("crops_served", [])
        ]

    # Distance calculation, radius filter, and sort
    results: list[ServiceResult] = []
    for s in services:
        s_lat = s.get("lat")
        s_lng = s.get("lng")
        if s_lat is None or s_lng is None:
            continue
        dist = _haversine_km(req.lat, req.lng, s_lat, s_lng)
        if dist > req.radius_km:
            continue
        results.append(ServiceResult(
            id=s.get("id", ""),
            name=s.get("name", ""),
            type=s.get("type", ""),
            province=s.get("province", ""),
            district=s.get("district", ""),
            town=s.get("town", ""),
            address=s.get("address", ""),
            phone=s.get("phone"),
            lat=s_lat,
            lng=s_lng,
            products=s.get("products", []),
            seed_brands=s.get("seed_brands", []),
            crops_served=s.get("crops_served", []),
            open_hours=s.get("open_hours"),
            notes=s.get("notes"),
            verified=s.get("verified", False),
            distance_km=round(dist, 1),
        ))

    results.sort(key=lambda x: x.distance_km)
    return results[:req.limit]


@router.get("/nearby", response_model=list[ServiceResult])
def services_nearby_get(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    province: str = Query(..., min_length=1),
    types: Optional[list[str]] = Query(default=None),
    crop_id: Optional[str] = None,
    radius_km: float = Query(default=100.0, ge=1, le=500),
    limit: int = Query(default=15, ge=1, le=50),
):
    """
    GET-compatible nearby-services endpoint for browser/frontend query requests.
    Reuses the POST implementation so filtering and validation stay identical.
    """
    req = NearbyRequest(
        lat=lat,
        lng=lng,
        province=province,
        types=types,
        crop_id=crop_id,
        radius_km=radius_km,
        limit=limit,
    )
    return services_nearby(req)


@router.get("/province/{province_name}")
def services_by_province(
    province_name: str,
    type: Optional[str] = None,
):
    """Return all services in a province, optionally filtered by type."""
    data = _load_province(province_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Province '{province_name}' not found.")

    services = data.get("services", [])
    if type:
        services = [s for s in services if s.get("type") == type]

    return {
        "province":  province_name,
        "count":     len(services),
        "services":  services,
    }


@router.get("/district/{province_name}/{district_name}")
def services_by_district(province_name: str, district_name: str):
    """
    Return AGRITEX office and key services for a specific district.
    Used in the app's Settings 'Nearby services' card.
    """
    data = _load_province(province_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Province '{province_name}' not found.")

    services = data.get("services", [])
    district_lower = district_name.lower()

    # AGRITEX office for this district
    agritex = next(
        (s for s in services
         if s.get("type") == "agritex_office"
         and s.get("district", "").lower() == district_lower),
        None
    )

    # Other services in this district (first 5, sorted by type priority)
    TYPE_PRIORITY = [
        "agro_dealer", "gmb_depot", "seed_company",
        "fresh_market", "specialty_buyer", "financial_service",
        "research_station", "cooperative",
    ]
    district_services = [
        s for s in services
        if s.get("district", "").lower() == district_lower
        and s.get("type") != "agritex_office"
    ]
    district_services.sort(
        key=lambda s: TYPE_PRIORITY.index(s["type"]) if s["type"] in TYPE_PRIORITY else 99
    )

    # District info
    district_info = next(
        (d for d in data.get("districts", [])
         if d.get("name", "").lower() == district_lower),
        None
    )

    return {
        "province":       province_name,
        "district":       district_name,
        "district_info":  district_info,
        "agritex_office": agritex,
        "services":       district_services[:6],
    }


@router.get("/provinces")
def list_provinces():
    """List all available provinces and their agro-ecological regions."""
    result = []
    for name in _PROVINCE_FILES:
        data = _load_province(name)
        if data:
            result.append({
                "name":        name,
                "code":        data.get("code"),
                "agro_regions":data.get("agro_regions", []),
                "districts":   [d["name"] for d in data.get("districts", [])],
                "service_count": len(data.get("services", [])),
            })
    return result
