"""
MDUMENI — Crop Dataset
All 30 Zimbabwean crops with full agronomic profiles.

Each crop record contains:
  - Identity: id, name, local names, type
  - Soil requirements: pH range, moisture range, soil texture
  - Climate requirements: temperature range, rainfall, altitude
  - Planting: months by agro-ecological region, days to maturity
  - Varieties: name, type, maturity, yield, input level
  - Irrigation: requirement type, water needs
  - Yield: tonnes/ha at low / medium / high input levels
  - Fertiliser schedule: phase, timing, product, rate
  - Organic alternatives: phase, product, rate
  - Pest & disease links: IDs referencing pest database
  - Companion & rotation partners: crop IDs
  - Market: price USD/kg, demand level

Agro-ecological regions (Zimbabwe):
  1 = Highveld / Eastern Highlands (>1000mm rain, well-watered)
  2 = Mashonaland / Midlands North (750-1000mm, reliable rain)
  3 = Midlands / parts of Manicaland (500-750mm, semi-reliable)
  4 = Masvingo / Matabeleland North (450-600mm, marginal)
  5 = Lowveld / Matabeleland South (<450mm, drought-prone)

Irrigation types:
  rain_fed       = survives on rainfall alone
  supplemental   = rain-fed but benefits from occasional irrigation
  full           = requires consistent irrigation to yield well
"""

CROPS = [

    # ── CEREALS ──────────────────────────────────────────────────────────

    {
        "id": "CROP_001",
        "name": "Maize",
        "local_names": {"shona": "Chibage", "ndebele": "Umbila"},
        "type": "cereal",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.0, "ph_optimal": 6.2,
            "moisture_min": 40, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "clay_loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 32, "temp_optimal_c": 25,
            "rainfall_min_mm": 500, "rainfall_max_mm": 900,
            "altitude_min_m": 600, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [11, 12], "2": [11, 12], "3": [10, 11], "4": [10, 11], "5": [10]},
            "days_to_maturity": {"short_season": 90, "medium_season": 120, "long_season": 150}
        },
        "varieties": [
            {"name": "ZM521", "type": "open_pollinated", "maturity_days": 120, "yield_t_ha": 4.5, "input_level": "low"},
            {"name": "SC403", "type": "hybrid", "maturity_days": 90, "yield_t_ha": 8.0, "input_level": "medium"},
            {"name": "SC627", "type": "hybrid", "maturity_days": 120, "yield_t_ha": 10.0, "input_level": "high"},
            {"name": "DKC80-33", "type": "hybrid", "maturity_days": 130, "yield_t_ha": 12.0, "input_level": "high"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 350},
        "yield_t_ha": {"low_input": 2.5, "medium_input": 5.5, "high_input": 9.5},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 200},
            {"phase": "top_dress_1", "days_after_planting": 21, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 150},
            {"phase": "top_dress_2", "days_after_planting": 45, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000},
            {"phase": "top_dress", "product": "Cattle manure", "kg_per_ha": 3000},
        ],
        "pests": ["PEST_001", "PEST_002", "PEST_003"],
        "diseases": ["DIS_001", "DIS_002"],
        "companion_crops": ["CROP_008", "CROP_012"],
        "rotation_partners": ["CROP_008", "CROP_015"],
        "market": {"price_usd_per_kg": 0.28, "price_updated": "2026-01", "demand": "very_high"}
    },

    {
        "id": "CROP_002",
        "name": "Sorghum",
        "local_names": {"shona": "Mapfunde", "ndebele": "Amabele"},
        "type": "cereal",
        "agro_regions": [2, 3, 4, 5],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 25, "moisture_max": 65, "moisture_optimal": 45,
            "texture": ["loam", "clay", "sandy_loam", "sandy"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 40, "temp_optimal_c": 30,
            "rainfall_min_mm": 300, "rainfall_max_mm": 750,
            "altitude_min_m": 200, "altitude_max_m": 1400
        },
        "planting": {
            "months_by_region": {"2": [11, 12], "3": [10, 11], "4": [10, 11], "5": [9, 10]},
            "days_to_maturity": {"short_season": 90, "medium_season": 120}
        },
        "varieties": [
            {"name": "SV1", "type": "open_pollinated", "maturity_days": 120, "yield_t_ha": 2.0, "input_level": "low"},
            {"name": "PAN 8816", "type": "hybrid", "maturity_days": 110, "yield_t_ha": 4.5, "input_level": "medium"},
            {"name": "Milestone", "type": "hybrid", "maturity_days": 100, "yield_t_ha": 5.5, "input_level": "high"},
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 250},
        "yield_t_ha": {"low_input": 1.5, "medium_input": 3.0, "high_input": 5.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 150},
            {"phase": "top_dress_1", "days_after_planting": 28, "product": "Ammonium Nitrate", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 3000},
        ],
        "pests": ["PEST_004", "PEST_005"],
        "diseases": ["DIS_003"],
        "companion_crops": ["CROP_008"],
        "rotation_partners": ["CROP_008", "CROP_009"],
        "market": {"price_usd_per_kg": 0.22, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_003",
        "name": "Wheat",
        "local_names": {"shona": "Gorosi", "ndebele": "Ukolwi"},
        "type": "cereal",
        "agro_regions": [1, 2],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 6.8,
            "moisture_min": 50, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 10, "temp_max_c": 25, "temp_optimal_c": 18,
            "rainfall_min_mm": 450, "rainfall_max_mm": 800,
            "altitude_min_m": 900, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [4, 5, 6], "2": [4, 5, 6]},
            "days_to_maturity": {"medium_season": 120, "long_season": 150}
        },
        "varieties": [
            {"name": "Robin", "type": "open_pollinated", "maturity_days": 130, "yield_t_ha": 3.5, "input_level": "low"},
            {"name": "Dande", "type": "improved", "maturity_days": 120, "yield_t_ha": 5.5, "input_level": "medium"},
            {"name": "Romany", "type": "improved", "maturity_days": 125, "yield_t_ha": 7.0, "input_level": "high"},
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 500},
        "yield_t_ha": {"low_input": 2.0, "medium_input": 4.5, "high_input": 7.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 250},
            {"phase": "top_dress_1", "days_after_planting": 30, "product": "Ammonium Nitrate", "kg_per_ha": 200},
            {"phase": "top_dress_2", "days_after_planting": 60, "product": "Ammonium Nitrate", "kg_per_ha": 150},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 6000},
        ],
        "pests": ["PEST_006"],
        "diseases": ["DIS_004", "DIS_005"],
        "companion_crops": [],
        "rotation_partners": ["CROP_008", "CROP_015"],
        "market": {"price_usd_per_kg": 0.38, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_004",
        "name": "Pearl millet",
        "local_names": {"shona": "Mhunga", "ndebele": "Inyawuthi"},
        "type": "cereal",
        "agro_regions": [3, 4, 5],
        "soil": {
            "ph_min": 5.0, "ph_max": 7.5, "ph_optimal": 6.0,
            "moisture_min": 20, "moisture_max": 60, "moisture_optimal": 40,
            "texture": ["sandy", "sandy_loam", "loam"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 42, "temp_optimal_c": 32,
            "rainfall_min_mm": 250, "rainfall_max_mm": 600,
            "altitude_min_m": 100, "altitude_max_m": 1200
        },
        "planting": {
            "months_by_region": {"3": [10, 11], "4": [10, 11], "5": [9, 10]},
            "days_to_maturity": {"short_season": 75, "medium_season": 100}
        },
        "varieties": [
            {"name": "SDMV 89004", "type": "open_pollinated", "maturity_days": 90, "yield_t_ha": 1.5, "input_level": "low"},
            {"name": "Okashana 1", "type": "improved", "maturity_days": 85, "yield_t_ha": 2.5, "input_level": "medium"},
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 180},
        "yield_t_ha": {"low_input": 1.0, "medium_input": 2.0, "high_input": 3.5},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 100},
            {"phase": "top_dress_1", "days_after_planting": 25, "product": "Ammonium Nitrate", "kg_per_ha": 80},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Cattle manure", "kg_per_ha": 2000},
        ],
        "pests": ["PEST_007"],
        "diseases": ["DIS_006"],
        "companion_crops": ["CROP_008"],
        "rotation_partners": ["CROP_008"],
        "market": {"price_usd_per_kg": 0.20, "price_updated": "2026-01", "demand": "medium"}
    },

    {
        "id": "CROP_005",
        "name": "Barley",
        "local_names": {"shona": "Barley", "ndebele": "Barley"},
        "type": "cereal",
        "agro_regions": [1],
        "soil": {
            "ph_min": 6.0, "ph_max": 8.0, "ph_optimal": 7.0,
            "moisture_min": 45, "moisture_max": 75, "moisture_optimal": 60,
            "texture": ["loam", "clay_loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 8, "temp_max_c": 24, "temp_optimal_c": 16,
            "rainfall_min_mm": 400, "rainfall_max_mm": 700,
            "altitude_min_m": 1200, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [4, 5]},
            "days_to_maturity": {"medium_season": 110, "long_season": 140}
        },
        "varieties": [
            {"name": "Capricorn", "type": "improved", "maturity_days": 120, "yield_t_ha": 4.0, "input_level": "medium"},
            {"name": "Stirling", "type": "improved", "maturity_days": 115, "yield_t_ha": 5.5, "input_level": "high"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 400},
        "yield_t_ha": {"low_input": 1.5, "medium_input": 3.5, "high_input": 6.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 200},
            {"phase": "top_dress_1", "days_after_planting": 28, "product": "Ammonium Nitrate", "kg_per_ha": 150},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 4000},
        ],
        "pests": ["PEST_006"],
        "diseases": ["DIS_004"],
        "companion_crops": [],
        "rotation_partners": ["CROP_008"],
        "market": {"price_usd_per_kg": 0.35, "price_updated": "2026-01", "demand": "medium"}
    },

    # ── LEGUMES ───────────────────────────────────────────────────────────

    {
        "id": "CROP_006",
        "name": "Soybeans",
        "local_names": {"shona": "Soya Bhinzi", "ndebele": "Soybeans"},
        "type": "legume",
        "agro_regions": [1, 2],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 45, "moisture_max": 75, "moisture_optimal": 60,
            "texture": ["loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 30, "temp_optimal_c": 24,
            "rainfall_min_mm": 500, "rainfall_max_mm": 800,
            "altitude_min_m": 800, "altitude_max_m": 1600
        },
        "planting": {
            "months_by_region": {"1": [11, 12], "2": [11, 12]},
            "days_to_maturity": {"medium_season": 110, "long_season": 130}
        },
        "varieties": [
            {"name": "Ocepara-4", "type": "open_pollinated", "maturity_days": 120, "yield_t_ha": 2.0, "input_level": "low"},
            {"name": "Duiker", "type": "improved", "maturity_days": 110, "yield_t_ha": 3.0, "input_level": "medium"},
            {"name": "SC Serenade", "type": "hybrid", "maturity_days": 115, "yield_t_ha": 4.5, "input_level": "high"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 320},
        "yield_t_ha": {"low_input": 1.2, "medium_input": 2.5, "high_input": 4.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Single Super Phosphate", "kg_per_ha": 150},
            {"phase": "inoculant", "days_after_planting": 0, "product": "Rhizobium inoculant", "kg_per_ha": 0.2},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Bone meal", "kg_per_ha": 300},
        ],
        "pests": ["PEST_008", "PEST_009"],
        "diseases": ["DIS_007"],
        "companion_crops": ["CROP_001"],
        "rotation_partners": ["CROP_001", "CROP_003"],
        "market": {"price_usd_per_kg": 0.55, "price_updated": "2026-01", "demand": "very_high"}
    },

    {
        "id": "CROP_007",
        "name": "Groundnuts",
        "local_names": {"shona": "Nzungu", "ndebele": "Amazambane"},
        "type": "legume",
        "agro_regions": [2, 3, 4],
        "soil": {
            "ph_min": 5.8, "ph_max": 6.5, "ph_optimal": 6.0,
            "moisture_min": 35, "moisture_max": 70, "moisture_optimal": 55,
            "texture": ["sandy_loam", "loam", "sandy"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 35, "temp_optimal_c": 28,
            "rainfall_min_mm": 400, "rainfall_max_mm": 700,
            "altitude_min_m": 400, "altitude_max_m": 1400
        },
        "planting": {
            "months_by_region": {"2": [11, 12], "3": [10, 11], "4": [10, 11]},
            "days_to_maturity": {"short_season": 100, "medium_season": 130}
        },
        "varieties": [
            {"name": "Nyanda", "type": "open_pollinated", "maturity_days": 115, "yield_t_ha": 1.8, "input_level": "low"},
            {"name": "Falcon", "type": "improved", "maturity_days": 110, "yield_t_ha": 2.5, "input_level": "medium"},
            {"name": "Jl 24", "type": "improved", "maturity_days": 100, "yield_t_ha": 3.2, "input_level": "high"},
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 280},
        "yield_t_ha": {"low_input": 1.0, "medium_input": 1.8, "high_input": 3.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Single Super Phosphate", "kg_per_ha": 150},
            {"phase": "calcium", "days_after_planting": 40, "product": "Agricultural lime", "kg_per_ha": 200},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Bone meal", "kg_per_ha": 250},
        ],
        "pests": ["PEST_010"],
        "diseases": ["DIS_008"],
        "companion_crops": ["CROP_001", "CROP_002"],
        "rotation_partners": ["CROP_001", "CROP_002"],
        "market": {"price_usd_per_kg": 0.60, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_008",
        "name": "Sugar beans",
        "local_names": {"shona": "Shuga Bhinzi", "ndebele": "Ubhontshisi obomvu"},
        "type": "legume",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.0, "ph_optimal": 6.2,
            "moisture_min": 40, "moisture_max": 75, "moisture_optimal": 58,
            "texture": ["loam", "clay_loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 15, "temp_max_c": 28, "temp_optimal_c": 22,
            "rainfall_min_mm": 400, "rainfall_max_mm": 700,
            "altitude_min_m": 600, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [11, 12], "2": [11, 12], "3": [10, 11]},
            "days_to_maturity": {"short_season": 65, "medium_season": 90}
        },
        "varieties": [
            {"name": "Chivaura", "type": "open_pollinated", "maturity_days": 75, "yield_t_ha": 1.2, "input_level": "low"},
            {"name": "Gloria", "type": "improved", "maturity_days": 70, "yield_t_ha": 2.0, "input_level": "medium"},
            {"name": "Lyskamm", "type": "improved", "maturity_days": 68, "yield_t_ha": 2.8, "input_level": "high"},
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 250},
        "yield_t_ha": {"low_input": 0.8, "medium_input": 1.5, "high_input": 2.5},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Single Super Phosphate", "kg_per_ha": 120},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 3000},
        ],
        "pests": ["PEST_011"],
        "diseases": ["DIS_009"],
        "companion_crops": ["CROP_001"],
        "rotation_partners": ["CROP_001", "CROP_002"],
        "market": {"price_usd_per_kg": 0.70, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_009",
        "name": "Cowpeas",
        "local_names": {"shona": "Nyemba", "ndebele": "Indumba"},
        "type": "legume",
        "agro_regions": [3, 4, 5],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.0, "ph_optimal": 6.0,
            "moisture_min": 25, "moisture_max": 65, "moisture_optimal": 45,
            "texture": ["sandy", "sandy_loam", "loam"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 38, "temp_optimal_c": 28,
            "rainfall_min_mm": 300, "rainfall_max_mm": 600,
            "altitude_min_m": 200, "altitude_max_m": 1200
        },
        "planting": {
            "months_by_region": {"3": [11, 12], "4": [10, 11], "5": [10, 11]},
            "days_to_maturity": {"short_season": 60, "medium_season": 90}
        },
        "varieties": [
            {"name": "IT82D-889", "type": "improved", "maturity_days": 65, "yield_t_ha": 1.5, "input_level": "low"},
            {"name": "Bechuana white", "type": "open_pollinated", "maturity_days": 75, "yield_t_ha": 1.0, "input_level": "low"},
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 180},
        "yield_t_ha": {"low_input": 0.8, "medium_input": 1.4, "high_input": 2.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Single Super Phosphate", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 2000},
        ],
        "pests": ["PEST_012"],
        "diseases": ["DIS_010"],
        "companion_crops": ["CROP_002"],
        "rotation_partners": ["CROP_002", "CROP_004"],
        "market": {"price_usd_per_kg": 0.55, "price_updated": "2026-01", "demand": "medium"}
    },

    # ── CASH CROPS ────────────────────────────────────────────────────────

    {
        "id": "CROP_010",
        "name": "Cotton",
        "local_names": {"shona": "Donje", "ndebele": "Ukotshini"},
        "type": "cash_crop",
        "agro_regions": [3, 4, 5],
        "soil": {
            "ph_min": 5.8, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 40, "moisture_max": 70, "moisture_optimal": 55,
            "texture": ["loam", "clay_loam", "clay"]
        },
        "climate": {
            "temp_min_c": 22, "temp_max_c": 40, "temp_optimal_c": 32,
            "rainfall_min_mm": 450, "rainfall_max_mm": 800,
            "altitude_min_m": 300, "altitude_max_m": 1200
        },
        "planting": {
            "months_by_region": {"3": [11, 12], "4": [11, 12], "5": [10, 11]},
            "days_to_maturity": {"medium_season": 150, "long_season": 180}
        },
        "varieties": [
            {"name": "SZ9314", "type": "hybrid", "maturity_days": 160, "yield_t_ha": 1.5, "input_level": "low"},
            {"name": "IAN 338", "type": "hybrid", "maturity_days": 155, "yield_t_ha": 2.5, "input_level": "medium"},
            {"name": "Delta Opal", "type": "hybrid", "maturity_days": 160, "yield_t_ha": 3.5, "input_level": "high"},
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 600},
        "yield_t_ha": {"low_input": 0.8, "medium_input": 1.8, "high_input": 3.2},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound L", "kg_per_ha": 200},
            {"phase": "top_dress_1", "days_after_planting": 30, "product": "Ammonium Nitrate", "kg_per_ha": 150},
            {"phase": "top_dress_2", "days_after_planting": 60, "product": "Potassium Sulphate", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000},
        ],
        "pests": ["PEST_013", "PEST_014"],
        "diseases": ["DIS_011"],
        "companion_crops": [],
        "rotation_partners": ["CROP_007", "CROP_008"],
        "market": {"price_usd_per_kg": 0.85, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_011",
        "name": "Tobacco",
        "local_names": {"shona": "Fodya", "ndebele": "Ugwayi"},
        "type": "cash_crop",
        "agro_regions": [1, 2],
        "soil": {
            "ph_min": 5.5, "ph_max": 6.5, "ph_optimal": 6.0,
            "moisture_min": 40, "moisture_max": 70, "moisture_optimal": 55,
            "texture": ["sandy_loam", "loam"]
        },
        "climate": {
            "temp_min_c": 16, "temp_max_c": 30, "temp_optimal_c": 24,
            "rainfall_min_mm": 600, "rainfall_max_mm": 900,
            "altitude_min_m": 900, "altitude_max_m": 1600
        },
        "planting": {
            "months_by_region": {"1": [8, 9], "2": [8, 9]},
            "days_to_maturity": {"long_season": 150}
        },
        "varieties": [
            {"name": "T66", "type": "flue_cured", "maturity_days": 150, "yield_t_ha": 2.0, "input_level": "medium"},
            {"name": "KRK 26", "type": "flue_cured", "maturity_days": 148, "yield_t_ha": 3.0, "input_level": "high"},
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 550},
        "yield_t_ha": {"low_input": 1.2, "medium_input": 2.2, "high_input": 3.5},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound S", "kg_per_ha": 300},
            {"phase": "top_dress_1", "days_after_planting": 21, "product": "Calcium Nitrate", "kg_per_ha": 200},
            {"phase": "top_dress_2", "days_after_planting": 42, "product": "Potassium Nitrate", "kg_per_ha": 150},
        ],
        "organic_alternatives": [],
        "pests": ["PEST_015"],
        "diseases": ["DIS_012"],
        "companion_crops": [],
        "rotation_partners": ["CROP_001", "CROP_006"],
        "market": {"price_usd_per_kg": 2.50, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_012",
        "name": "Sunflower",
        "local_names": {"shona": "Sunflower", "ndebele": "Ilanga"},
        "type": "cash_crop",
        "agro_regions": [2, 3, 4],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 6.8,
            "moisture_min": 30, "moisture_max": 65, "moisture_optimal": 50,
            "texture": ["loam", "sandy_loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 35, "temp_optimal_c": 27,
            "rainfall_min_mm": 400, "rainfall_max_mm": 700,
            "altitude_min_m": 400, "altitude_max_m": 1400
        },
        "planting": {
            "months_by_region": {"2": [11, 12, 1], "3": [11, 12], "4": [11, 12]},
            "days_to_maturity": {"short_season": 100, "medium_season": 120}
        },
        "varieties": [
            {"name": "Maravilla", "type": "open_pollinated", "maturity_days": 115, "yield_t_ha": 1.0, "input_level": "low"},
            {"name": "PAN 7057", "type": "hybrid", "maturity_days": 108, "yield_t_ha": 1.8, "input_level": "medium"},
            {"name": "Agsun 5672 CL", "type": "hybrid", "maturity_days": 105, "yield_t_ha": 2.5, "input_level": "high"},
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 300},
        "yield_t_ha": {"low_input": 0.8, "medium_input": 1.5, "high_input": 2.5},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 150},
            {"phase": "top_dress_1", "days_after_planting": 28, "product": "Ammonium Nitrate", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 3000},
        ],
        "pests": ["PEST_016"],
        "diseases": ["DIS_013"],
        "companion_crops": ["CROP_001"],
        "rotation_partners": ["CROP_001", "CROP_007"],
        "market": {"price_usd_per_kg": 0.48, "price_updated": "2026-01", "demand": "high"}
    },

    # ── VEGETABLES ────────────────────────────────────────────────────────

    {
        "id": "CROP_013",
        "name": "Tomatoes",
        "local_names": {"shona": "Tomato", "ndebele": "Amatamatisi"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 55, "moisture_max": 85, "moisture_optimal": 70,
            "texture": ["loam", "clay_loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 15, "temp_max_c": 30, "temp_optimal_c": 22,
            "rainfall_min_mm": 400, "rainfall_max_mm": 700,
            "altitude_min_m": 400, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [3, 4, 7, 8], "2": [3, 4, 7, 8], "3": [3, 4, 7, 8]},
            "days_to_maturity": {"short_season": 70, "medium_season": 90}
        },
        "varieties": [
            {"name": "Roma VF", "type": "open_pollinated", "maturity_days": 75, "yield_t_ha": 20.0, "input_level": "low"},
            {"name": "Tengeru 97", "type": "improved", "maturity_days": 80, "yield_t_ha": 35.0, "input_level": "medium"},
            {"name": "Rodade", "type": "hybrid", "maturity_days": 75, "yield_t_ha": 55.0, "input_level": "high"},
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 450},
        "yield_t_ha": {"low_input": 15.0, "medium_input": 30.0, "high_input": 55.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress_1", "days_after_planting": 21, "product": "LAN (28%N)", "kg_per_ha": 200},
            {"phase": "top_dress_2", "days_after_planting": 42, "product": "Potassium Nitrate", "kg_per_ha": 150},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 8000},
            {"phase": "foliar", "product": "Fermented plant juice", "litres_per_ha": 10},
        ],
        "pests": ["PEST_017", "PEST_018"],
        "diseases": ["DIS_014", "DIS_015"],
        "companion_crops": ["CROP_014"],
        "rotation_partners": ["CROP_001", "CROP_008"],
        "market": {"price_usd_per_kg": 0.35, "price_updated": "2026-01", "demand": "very_high"}
    },

    {
        "id": "CROP_014",
        "name": "Onions",
        "local_names": {"shona": "Hanyanisi", "ndebele": "Uyanyanisi"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 50, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 12, "temp_max_c": 28, "temp_optimal_c": 20,
            "rainfall_min_mm": 400, "rainfall_max_mm": 650,
            "altitude_min_m": 600, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [3, 4, 5, 6], "2": [4, 5, 6], "3": [4, 5, 6]},
            "days_to_maturity": {"medium_season": 100, "long_season": 130}
        },
        "varieties": [
            {"name": "Texas Grano", "type": "open_pollinated", "maturity_days": 110, "yield_t_ha": 18.0, "input_level": "low"},
            {"name": "Pyramid", "type": "hybrid", "maturity_days": 100, "yield_t_ha": 35.0, "input_level": "medium"},
            {"name": "Rosanna F1", "type": "hybrid", "maturity_days": 95, "yield_t_ha": 55.0, "input_level": "high"},
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 400},
        "yield_t_ha": {"low_input": 12.0, "medium_input": 25.0, "high_input": 50.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 250},
            {"phase": "top_dress_1", "days_after_planting": 28, "product": "LAN", "kg_per_ha": 180},
            {"phase": "top_dress_2", "days_after_planting": 56, "product": "Potassium Chloride", "kg_per_ha": 120},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 6000},
        ],
        "pests": ["PEST_019"],
        "diseases": ["DIS_016"],
        "companion_crops": ["CROP_013"],
        "rotation_partners": ["CROP_001"],
        "market": {"price_usd_per_kg": 0.42, "price_updated": "2026-01", "demand": "very_high"}
    },

    {
        "id": "CROP_015",
        "name": "Cabbages",
        "local_names": {"shona": "Kabheji", "ndebele": "Ikhabishi"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 6.8,
            "moisture_min": 55, "moisture_max": 85, "moisture_optimal": 70,
            "texture": ["loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 10, "temp_max_c": 25, "temp_optimal_c": 18,
            "rainfall_min_mm": 400, "rainfall_max_mm": 700,
            "altitude_min_m": 600, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [3, 4, 5, 6, 7], "2": [4, 5, 6, 7], "3": [4, 5, 6]},
            "days_to_maturity": {"medium_season": 80, "long_season": 110}
        },
        "varieties": [
            {"name": "Star 3301 F1", "type": "hybrid", "maturity_days": 88, "yield_t_ha": 40.0, "input_level": "medium"},
            {"name": "Copenhagen Market", "type": "open_pollinated", "maturity_days": 95, "yield_t_ha": 20.0, "input_level": "low"},
            {"name": "Conquistador F1", "type": "hybrid", "maturity_days": 82, "yield_t_ha": 60.0, "input_level": "high"},
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 400},
        "yield_t_ha": {"low_input": 18.0, "medium_input": 38.0, "high_input": 60.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress_1", "days_after_planting": 21, "product": "LAN", "kg_per_ha": 200},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 7000},
        ],
        "pests": ["PEST_020"],
        "diseases": ["DIS_017"],
        "companion_crops": ["CROP_014"],
        "rotation_partners": ["CROP_001", "CROP_008"],
        "market": {"price_usd_per_kg": 0.25, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_016",
        "name": "Rape / Leaf vegetable",
        "local_names": {"shona": "Rape", "ndebele": "Rape"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3, 4],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 45, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "clay_loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 10, "temp_max_c": 28, "temp_optimal_c": 18,
            "rainfall_min_mm": 350, "rainfall_max_mm": 700,
            "altitude_min_m": 400, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [1,2,3,4,5,6,7,8,9,10,11,12], "2": [3,4,5,6,7,8,9,10], "3": [4,5,6,7,8,9], "4": [4,5,6,7,8]},
            "days_to_maturity": {"short_season": 45, "medium_season": 60}
        },
        "varieties": [
            {"name": "Giant Rape", "type": "open_pollinated", "maturity_days": 50, "yield_t_ha": 8.0, "input_level": "low"},
            {"name": "Canola", "type": "improved", "maturity_days": 55, "yield_t_ha": 14.0, "input_level": "medium"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 200},
        "yield_t_ha": {"low_input": 6.0, "medium_input": 12.0, "high_input": 20.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 200},
            {"phase": "top_dress_1", "days_after_planting": 14, "product": "LAN", "kg_per_ha": 150},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000},
        ],
        "pests": ["PEST_020"],
        "diseases": ["DIS_018"],
        "companion_crops": [],
        "rotation_partners": ["CROP_001"],
        "market": {"price_usd_per_kg": 0.30, "price_updated": "2026-01", "demand": "very_high"}
    },

    {
        "id": "CROP_017",
        "name": "Watermelon",
        "local_names": {"shona": "Vise/Nwiwa", "ndebele": "Ikhabe"},
        "type": "vegetable",
        "agro_regions": [2, 3, 4, 5],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 40, "moisture_max": 75, "moisture_optimal": 60,
            "texture": ["sandy_loam", "loam", "sandy"]
        },
        "climate": {
            "temp_min_c": 22, "temp_max_c": 38, "temp_optimal_c": 30,
            "rainfall_min_mm": 350, "rainfall_max_mm": 650,
            "altitude_min_m": 200, "altitude_max_m": 1200
        },
        "planting": {
            "months_by_region": {"2": [10,11], "3": [10,11], "4": [10,11], "5": [9,10]},
            "days_to_maturity": {"medium_season": 80, "long_season": 100}
        },
        "varieties": [
            {"name": "Sugar Baby", "type": "open_pollinated", "maturity_days": 80, "yield_t_ha": 20.0, "input_level": "low"},
            {"name": "Crimson Sweet", "type": "improved", "maturity_days": 85, "yield_t_ha": 35.0, "input_level": "medium"},
            {"name": "Charleston Grey", "type": "open_pollinated", "maturity_days": 90, "yield_t_ha": 30.0, "input_level": "medium"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 350},
        "yield_t_ha": {"low_input": 15.0, "medium_input": 28.0, "high_input": 40.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 200},
            {"phase": "top_dress_1", "days_after_planting": 21, "product": "LAN", "kg_per_ha": 120},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000},
        ],
        "pests": ["PEST_021"],
        "diseases": ["DIS_019"],
        "companion_crops": [],
        "rotation_partners": ["CROP_001"],
        "market": {"price_usd_per_kg": 0.22, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_018",
        "name": "Butternut squash",
        "local_names": {"shona": "Bhonzo", "ndebele": "Iselwa"},
        "type": "vegetable",
        "agro_regions": [2, 3, 4],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.0, "ph_optimal": 6.2,
            "moisture_min": 40, "moisture_max": 75, "moisture_optimal": 60,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 35, "temp_optimal_c": 27,
            "rainfall_min_mm": 400, "rainfall_max_mm": 650,
            "altitude_min_m": 400, "altitude_max_m": 1400
        },
        "planting": {
            "months_by_region": {"2": [10,11], "3": [10,11], "4": [10,11]},
            "days_to_maturity": {"medium_season": 90, "long_season": 110}
        },
        "varieties": [
            {"name": "Waltham Butternut", "type": "open_pollinated", "maturity_days": 95, "yield_t_ha": 18.0, "input_level": "low"},
            {"name": "Metro F1", "type": "hybrid", "maturity_days": 88, "yield_t_ha": 30.0, "input_level": "medium"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 300},
        "yield_t_ha": {"low_input": 12.0, "medium_input": 22.0, "high_input": 35.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 180},
            {"phase": "top_dress_1", "days_after_planting": 28, "product": "LAN", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 4000},
        ],
        "pests": ["PEST_021"],
        "diseases": ["DIS_020"],
        "companion_crops": [],
        "rotation_partners": ["CROP_001", "CROP_008"],
        "market": {"price_usd_per_kg": 0.28, "price_updated": "2026-01", "demand": "high"}
    },

    # ── ROOT & TUBER CROPS ────────────────────────────────────────────────

    {
        "id": "CROP_019",
        "name": "Sweet potato",
        "local_names": {"shona": "Mbambaira", "ndebele": "Imbambayila"},
        "type": "root_tuber",
        "agro_regions": [2, 3, 4],
        "soil": {
            "ph_min": 5.5, "ph_max": 6.5, "ph_optimal": 6.0,
            "moisture_min": 45, "moisture_max": 75, "moisture_optimal": 62,
            "texture": ["sandy_loam", "loam", "sandy"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 32, "temp_optimal_c": 25,
            "rainfall_min_mm": 500, "rainfall_max_mm": 750,
            "altitude_min_m": 400, "altitude_max_m": 1400
        },
        "planting": {
            "months_by_region": {"2": [10,11,12], "3": [10,11], "4": [10,11]},
            "days_to_maturity": {"medium_season": 90, "long_season": 120}
        },
        "varieties": [
            {"name": "Mugande", "type": "open_pollinated", "maturity_days": 100, "yield_t_ha": 10.0, "input_level": "low"},
            {"name": "Brondal", "type": "improved", "maturity_days": 95, "yield_t_ha": 18.0, "input_level": "medium"},
            {"name": "Beauregard", "type": "improved", "maturity_days": 90, "yield_t_ha": 28.0, "input_level": "high"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 320},
        "yield_t_ha": {"low_input": 8.0, "medium_input": 15.0, "high_input": 25.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 150},
            {"phase": "top_dress_1", "days_after_planting": 30, "product": "Potassium Chloride", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 4000},
        ],
        "pests": ["PEST_022"],
        "diseases": ["DIS_021"],
        "companion_crops": [],
        "rotation_partners": ["CROP_001", "CROP_008"],
        "market": {"price_usd_per_kg": 0.18, "price_updated": "2026-01", "demand": "very_high"}
    },

    {
        "id": "CROP_020",
        "name": "Cassava",
        "local_names": {"shona": "Mufarinya", "ndebele": "Umfarinya"},
        "type": "root_tuber",
        "agro_regions": [3, 4, 5],
        "soil": {
            "ph_min": 4.5, "ph_max": 7.0, "ph_optimal": 5.8,
            "moisture_min": 25, "moisture_max": 70, "moisture_optimal": 50,
            "texture": ["sandy", "sandy_loam", "loam"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 38, "temp_optimal_c": 28,
            "rainfall_min_mm": 400, "rainfall_max_mm": 800,
            "altitude_min_m": 100, "altitude_max_m": 1200
        },
        "planting": {
            "months_by_region": {"3": [10,11], "4": [10,11], "5": [9,10]},
            "days_to_maturity": {"long_season": 270, "very_long": 365}
        },
        "varieties": [
            {"name": "Nhema", "type": "local", "maturity_days": 300, "yield_t_ha": 12.0, "input_level": "low"},
            {"name": "IITA TMS 30572", "type": "improved", "maturity_days": 270, "yield_t_ha": 20.0, "input_level": "medium"},
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 300},
        "yield_t_ha": {"low_input": 8.0, "medium_input": 15.0, "high_input": 25.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 120},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 3000},
        ],
        "pests": ["PEST_023"],
        "diseases": ["DIS_022"],
        "companion_crops": ["CROP_009"],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 0.15, "price_updated": "2026-01", "demand": "medium"}
    },

    {
        "id": "CROP_021",
        "name": "Irish potato",
        "local_names": {"shona": "Mbatatisi/Magwiri", "ndebele": "Amagwili/Amagabhade"},
        "type": "root_tuber",
        "agro_regions": [1, 2],
        "soil": {
            "ph_min": 5.0, "ph_max": 6.5, "ph_optimal": 5.8,
            "moisture_min": 55, "moisture_max": 85, "moisture_optimal": 72,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 10, "temp_max_c": 24, "temp_optimal_c": 16,
            "rainfall_min_mm": 500, "rainfall_max_mm": 800,
            "altitude_min_m": 1000, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [2,3,8,9], "2": [3,4,8,9]},
            "days_to_maturity": {"short_season": 75, "medium_season": 100}
        },
        "varieties": [
            {"name": "BP1", "type": "improved", "maturity_days": 85, "yield_t_ha": 15.0, "input_level": "low"},
            {"name": "Mnandi", "type": "improved", "maturity_days": 80, "yield_t_ha": 25.0, "input_level": "medium"},
            {"name": "Mondial", "type": "improved", "maturity_days": 75, "yield_t_ha": 40.0, "input_level": "high"},
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 450},
        "yield_t_ha": {"low_input": 12.0, "medium_input": 22.0, "high_input": 40.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress_1", "days_after_planting": 28, "product": "LAN", "kg_per_ha": 200},
            {"phase": "top_dress_2", "days_after_planting": 50, "product": "Potassium Chloride", "kg_per_ha": 150},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 8000},
        ],
        "pests": ["PEST_024"],
        "diseases": ["DIS_023", "DIS_024"],
        "companion_crops": [],
        "rotation_partners": ["CROP_001", "CROP_008"],
        "market": {"price_usd_per_kg": 0.32, "price_updated": "2026-01", "demand": "very_high"}
    },

    # ── FRUIT CROPS ───────────────────────────────────────────────────────

    {
        "id": "CROP_022",
        "name": "Papaya",
        "local_names": {"shona": "Papaya", "ndebele": "Ipapazi"},
        "type": "fruit",
        "agro_regions": [2, 3, 4, 5],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 50, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 38, "temp_optimal_c": 30,
            "rainfall_min_mm": 500, "rainfall_max_mm": 1000,
            "altitude_min_m": 100, "altitude_max_m": 1000
        },
        "planting": {
            "months_by_region": {"2": [10,11], "3": [10,11], "4": [10,11], "5": [10]},
            "days_to_maturity": {"long_season": 210}
        },
        "varieties": [
            {"name": "Solo", "type": "improved", "maturity_days": 210, "yield_t_ha": 40.0, "input_level": "low"},
            {"name": "Sunrise Solo", "type": "hybrid", "maturity_days": 200, "yield_t_ha": 60.0, "input_level": "medium"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 400},
        "yield_t_ha": {"low_input": 25.0, "medium_input": 45.0, "high_input": 65.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 200},
            {"phase": "top_dress_1", "days_after_planting": 60, "product": "LAN", "kg_per_ha": 150},
            {"phase": "top_dress_2", "days_after_planting": 120, "product": "Potassium Nitrate", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000},
        ],
        "pests": ["PEST_025"],
        "diseases": ["DIS_025"],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 0.30, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_023",
        "name": "Mango",
        "local_names": {"shona": "Mango", "ndebele": "Mango"},
        "type": "fruit",
        "agro_regions": [3, 4, 5],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 40, "moisture_max": 75, "moisture_optimal": 58,
            "texture": ["loam", "clay_loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 22, "temp_max_c": 42, "temp_optimal_c": 32,
            "rainfall_min_mm": 400, "rainfall_max_mm": 800,
            "altitude_min_m": 100, "altitude_max_m": 900
        },
        "planting": {
            "months_by_region": {"3": [10,11], "4": [10,11], "5": [9,10]},
            "days_to_maturity": {"perennial_first_fruit": 1095}
        },
        "varieties": [
            {"name": "Sensation", "type": "improved", "maturity_days": 1095, "yield_t_ha": 8.0, "input_level": "low"},
            {"name": "Tommy Atkins", "type": "improved", "maturity_days": 1095, "yield_t_ha": 12.0, "input_level": "medium"},
            {"name": "Kent", "type": "improved", "maturity_days": 1095, "yield_t_ha": 18.0, "input_level": "high"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 350},
        "yield_t_ha": {"low_input": 5.0, "medium_input": 10.0, "high_input": 18.0},
        "fertiliser_schedule": [
            {"phase": "annual_basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 150},
            {"phase": "annual_top_dress", "days_after_planting": 90, "product": "LAN", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "annual_basal", "product": "Compost", "kg_per_ha": 4000},
        ],
        "pests": ["PEST_026"],
        "diseases": ["DIS_026"],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 0.40, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_024",
        "name": "Avocado",
        "local_names": {"shona": "Avokado", "ndebele": "Avocado"},
        "type": "fruit",
        "agro_regions": [1, 2],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 55, "moisture_max": 80, "moisture_optimal": 68,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 15, "temp_max_c": 30, "temp_optimal_c": 22,
            "rainfall_min_mm": 700, "rainfall_max_mm": 1200,
            "altitude_min_m": 800, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [10,11], "2": [10,11]},
            "days_to_maturity": {"perennial_first_fruit": 1460}
        },
        "varieties": [
            {"name": "Fuerte", "type": "improved", "maturity_days": 1460, "yield_t_ha": 6.0, "input_level": "low"},
            {"name": "Hass", "type": "improved", "maturity_days": 1460, "yield_t_ha": 10.0, "input_level": "medium"},
            {"name": "Pinkerton", "type": "improved", "maturity_days": 1460, "yield_t_ha": 14.0, "input_level": "high"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 500},
        "yield_t_ha": {"low_input": 4.0, "medium_input": 8.0, "high_input": 14.0},
        "fertiliser_schedule": [
            {"phase": "annual_basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 200},
            {"phase": "annual_foliar", "days_after_planting": 60, "product": "Multifeed", "kg_per_ha": 5},
        ],
        "organic_alternatives": [
            {"phase": "annual_basal", "product": "Compost", "kg_per_ha": 6000},
        ],
        "pests": ["PEST_027"],
        "diseases": ["DIS_027"],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 0.85, "price_updated": "2026-01", "demand": "very_high"}
    },

    {
        "id": "CROP_025",
        "name": "Bananas",
        "local_names": {"shona": "Bhanana", "ndebele": "Ubhanana"},
        "type": "fruit",
        "agro_regions": [2, 3, 4, 5],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 60, "moisture_max": 90, "moisture_optimal": 75,
            "texture": ["loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 38, "temp_optimal_c": 28,
            "rainfall_min_mm": 700, "rainfall_max_mm": 1500,
            "altitude_min_m": 100, "altitude_max_m": 1000
        },
        "planting": {
            "months_by_region": {"2": [10,11], "3": [10,11], "4": [10,11], "5": [10]},
            "days_to_maturity": {"first_bunch": 300}
        },
        "varieties": [
            {"name": "Williams", "type": "improved", "maturity_days": 300, "yield_t_ha": 25.0, "input_level": "low"},
            {"name": "Grand Nain", "type": "improved", "maturity_days": 280, "yield_t_ha": 45.0, "input_level": "medium"},
            {"name": "FHIA-01", "type": "hybrid", "maturity_days": 290, "yield_t_ha": 60.0, "input_level": "high"},
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 700},
        "yield_t_ha": {"low_input": 18.0, "medium_input": 35.0, "high_input": 60.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 250},
            {"phase": "top_dress_1", "days_after_planting": 60, "product": "Potassium Chloride", "kg_per_ha": 300},
            {"phase": "top_dress_2", "days_after_planting": 120, "product": "LAN", "kg_per_ha": 200},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 8000},
        ],
        "pests": ["PEST_028"],
        "diseases": ["DIS_028"],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 0.28, "price_updated": "2026-01", "demand": "very_high"}
    },

    # ── OILSEEDS ──────────────────────────────────────────────────────────

    {
        "id": "CROP_026",
        "name": "Sugar cane",
        "local_names": {"shona": "Nzimbe", "ndebele": "Umoba"},
        "type": "cash_crop",
        "agro_regions": [4, 5],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 6.8,
            "moisture_min": 55, "moisture_max": 90, "moisture_optimal": 75,
            "texture": ["clay_loam", "loam", "clay"]
        },
        "climate": {
            "temp_min_c": 22, "temp_max_c": 40, "temp_optimal_c": 32,
            "rainfall_min_mm": 600, "rainfall_max_mm": 1200,
            "altitude_min_m": 100, "altitude_max_m": 800
        },
        "planting": {
            "months_by_region": {"4": [9,10,11], "5": [9,10]},
            "days_to_maturity": {"long_season": 365, "very_long": 540}
        },
        "varieties": [
            {"name": "N12", "type": "improved", "maturity_days": 400, "yield_t_ha": 80.0, "input_level": "medium"},
            {"name": "N36", "type": "improved", "maturity_days": 380, "yield_t_ha": 110.0, "input_level": "high"},
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 1200},
        "yield_t_ha": {"low_input": 50.0, "medium_input": 85.0, "high_input": 120.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound L", "kg_per_ha": 400},
            {"phase": "top_dress_1", "days_after_planting": 90, "product": "Ammonium Nitrate", "kg_per_ha": 300},
        ],
        "organic_alternatives": [],
        "pests": ["PEST_029"],
        "diseases": ["DIS_029"],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 0.06, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_027",
        "name": "Sesame",
        "local_names": {"shona": "Runinga", "ndebele": "Isibuywana"},
        "type": "oilseed",
        "agro_regions": [3, 4, 5],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 20, "moisture_max": 60, "moisture_optimal": 40,
            "texture": ["sandy_loam", "loam", "sandy"]
        },
        "climate": {
            "temp_min_c": 22, "temp_max_c": 40, "temp_optimal_c": 30,
            "rainfall_min_mm": 300, "rainfall_max_mm": 600,
            "altitude_min_m": 100, "altitude_max_m": 1000
        },
        "planting": {
            "months_by_region": {"3": [11,12], "4": [11,12], "5": [10,11]},
            "days_to_maturity": {"short_season": 85, "medium_season": 100}
        },
        "varieties": [
            {"name": "E8", "type": "open_pollinated", "maturity_days": 90, "yield_t_ha": 0.5, "input_level": "low"},
            {"name": "Saro-14", "type": "improved", "maturity_days": 88, "yield_t_ha": 0.9, "input_level": "medium"},
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 200},
        "yield_t_ha": {"low_input": 0.4, "medium_input": 0.7, "high_input": 1.2},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 2000},
        ],
        "pests": ["PEST_030"],
        "diseases": ["DIS_030"],
        "companion_crops": ["CROP_009"],
        "rotation_partners": ["CROP_002", "CROP_004"],
        "market": {"price_usd_per_kg": 1.20, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_028",
        "name": "Pumpkin",
        "local_names": {"shona": "Manhanga", "ndebele": "Ithanga"},
        "type": "vegetable",
        "agro_regions": [2, 3, 4],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.0, "ph_optimal": 6.0,
            "moisture_min": 40, "moisture_max": 75, "moisture_optimal": 58,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 35, "temp_optimal_c": 26,
            "rainfall_min_mm": 400, "rainfall_max_mm": 650,
            "altitude_min_m": 300, "altitude_max_m": 1400
        },
        "planting": {
            "months_by_region": {"2": [10,11], "3": [10,11], "4": [10,11]},
            "days_to_maturity": {"medium_season": 90, "long_season": 120}
        },
        "varieties": [
            {"name": "Flat White Boer", "type": "open_pollinated", "maturity_days": 100, "yield_t_ha": 15.0, "input_level": "low"},
            {"name": "Hercules F1", "type": "hybrid", "maturity_days": 90, "yield_t_ha": 28.0, "input_level": "medium"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 280},
        "yield_t_ha": {"low_input": 10.0, "medium_input": 20.0, "high_input": 32.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 160},
            {"phase": "top_dress_1", "days_after_planting": 28, "product": "LAN", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 4000},
        ],
        "pests": ["PEST_021"],
        "diseases": ["DIS_031"],
        "companion_crops": ["CROP_001"],
        "rotation_partners": ["CROP_001"],
        "market": {"price_usd_per_kg": 0.15, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_029",
        "name": "Garlic",
        "local_names": {"shona": "Gariki", "ndebele": "Igaliki"},
        "type": "vegetable",
        "agro_regions": [1, 2],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 50, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 10, "temp_max_c": 25, "temp_optimal_c": 18,
            "rainfall_min_mm": 400, "rainfall_max_mm": 700,
            "altitude_min_m": 800, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [3,4,5,6], "2": [4,5,6]},
            "days_to_maturity": {"medium_season": 150, "long_season": 180}
        },
        "varieties": [
            {"name": "Elephant garlic", "type": "open_pollinated", "maturity_days": 165, "yield_t_ha": 6.0, "input_level": "low"},
            {"name": "Printanor", "type": "improved", "maturity_days": 150, "yield_t_ha": 10.0, "input_level": "medium"},
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 380},
        "yield_t_ha": {"low_input": 4.0, "medium_input": 8.0, "high_input": 14.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 200},
            {"phase": "top_dress_1", "days_after_planting": 30, "product": "LAN", "kg_per_ha": 150},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000},
        ],
        "pests": ["PEST_019"],
        "diseases": ["DIS_032"],
        "companion_crops": ["CROP_013"],
        "rotation_partners": ["CROP_001", "CROP_015"],
        "market": {"price_usd_per_kg": 1.50, "price_updated": "2026-01", "demand": "high"}
    },

    {
        "id": "CROP_030",
        "name": "Chillies / Peppers",
        "local_names": {"shona": "Mhiripiri", "ndebele": "Ipepula"},
        "type": "vegetable",
        "agro_regions": [2, 3, 4],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 50, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "sandy_loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 35, "temp_optimal_c": 26,
            "rainfall_min_mm": 450, "rainfall_max_mm": 750,
            "altitude_min_m": 300, "altitude_max_m": 1400
        },
        "planting": {
            "months_by_region": {"2": [10,11], "3": [10,11], "4": [10,11]},
            "days_to_maturity": {"medium_season": 90, "long_season": 120}
        },
        "varieties": [
            {"name": "Piri Piri local", "type": "local", "maturity_days": 100, "yield_t_ha": 5.0, "input_level": "low"},
            {"name": "California Wonder", "type": "open_pollinated", "maturity_days": 90, "yield_t_ha": 12.0, "input_level": "medium"},
            {"name": "Yolo Wonder F1", "type": "hybrid", "maturity_days": 85, "yield_t_ha": 20.0, "input_level": "high"},
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 350},
        "yield_t_ha": {"low_input": 4.0, "medium_input": 10.0, "high_input": 20.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 250},
            {"phase": "top_dress_1", "days_after_planting": 28, "product": "LAN", "kg_per_ha": 150},
            {"phase": "top_dress_2", "days_after_planting": 56, "product": "Potassium Nitrate", "kg_per_ha": 100},
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 6000},
        ],
        "pests": ["PEST_017", "PEST_018"],
        "diseases": ["DIS_033"],
        "companion_crops": ["CROP_013"],
        "rotation_partners": ["CROP_001", "CROP_008"],
        "market": {"price_usd_per_kg": 0.80, "price_updated": "2026-01", "demand": "very_high"}
    },

]

# Quick lookup by ID
CROP_BY_ID = {c["id"]: c for c in CROPS}
