"""
MDUMENI — Extended Crop Dataset
30 additional Zimbabwean crops (CROP_031 to CROP_060)

Includes:
  - Indigenous/traditional crops underrepresented in modern agronomy tools
  - High-value export crops for Region 1 (Eastern Highlands)
  - Drought-resilient crops for Regions 4 & 5
  - Vegetables and fruits critical for food security and household income
  - Cover crops and multipurpose trees important for soil health

All agronomic data sourced from:
  - AGRITEX crop production guidelines (Zimbabwe)
  - CIMMYT and ICRISAT regional variety trials
  - FAO country profiles for Zimbabwe
  - Seed Co Zimbabwe and Pannar variety catalogues
  - Department of Research & Specialist Services (DRSS) Zimbabwe
"""

CROPS_EXTENDED = [

    # ── CROP_031: Finger millet (Zviyo / Uphoko) ─────────────────────────────
    # Critical traditional cereal. More drought-tolerant than sorghum in
    # Regions 4-5. High nutritional value — rich in calcium and iron.
    # Stores for up to 5 years without fumigation. Severely underrepresented
    # in modern agricultural advisory systems.
    {
        "id": "CROP_031",
        "name": "Finger millet",
        "local_names": {"shona": "Zviyo", "ndebele": "Uphoko"},
        "type": "cereal",
        "agro_regions": [2, 3, 4, 5],
        "soil": {
            "ph_min": 5.0, "ph_max": 7.5, "ph_optimal": 6.0,
            "moisture_min": 25, "moisture_max": 65, "moisture_optimal": 45,
            "texture": ["sandy_loam", "loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 35, "temp_optimal_c": 27,
            "rainfall_min_mm": 350, "rainfall_max_mm": 900,
            "altitude_min_m": 400, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"2": [11, 12], "3": [10, 11], "4": [10, 11], "5": [10]},
            "days_to_maturity": {"short_season": 90, "medium_season": 120}
        },
        "varieties": [
            {"name": "Zviyo Local", "type": "open_pollinated", "maturity_days": 105, "yield_t_ha": 1.2, "input_level": "low"},
            {"name": "Gulu-E", "type": "improved_opv", "maturity_days": 110, "yield_t_ha": 2.5, "input_level": "medium"},
            {"name": "ML-365", "type": "improved_opv", "maturity_days": 95, "yield_t_ha": 2.0, "input_level": "low"}
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 350},
        "yield_t_ha": {"low_input": 0.8, "medium_input": 1.8, "high_input": 3.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound S", "kg_per_ha": 100},
            {"phase": "top_dress", "days_after_planting": 30, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 50}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 3000},
            {"phase": "top_dress", "product": "Cattle manure", "kg_per_ha": 2000}
        ],
        "pests": ["PEST_001", "PEST_006"],
        "diseases": [],
        "companion_crops": ["CROP_009", "CROP_033"],
        "rotation_partners": ["CROP_007", "CROP_009"],
        "market": {"price_usd_per_kg": 0.38, "price_updated": "2026-01", "demand": "medium"}
    },

    # ── CROP_032: Bambara groundnut (Nyimo beans) ─────────────────────────────
    # One of Zimbabwe's most important traditional legumes — both food and
    # cultural significance. Fixes nitrogen, extremely drought-tolerant,
    # grows on poor soils where groundnuts fail. Hugely underserved by
    # modern agri advisory. Critical for Regions 4-5 food security.
    {
        "id": "CROP_032",
        "name": "Bambara groundnut",
        "local_names": {"shona": "Nyimo", "ndebele": "Izindlubu"},
        "type": "legume",
        "agro_regions": [2, 3, 4, 5],
        "soil": {
            "ph_min": 5.0, "ph_max": 7.0, "ph_optimal": 6.0,
            "moisture_min": 25, "moisture_max": 60, "moisture_optimal": 45,
            "texture": ["sandy_loam", "loam", "sandy"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 35, "temp_optimal_c": 28,
            "rainfall_min_mm": 300, "rainfall_max_mm": 800,
            "altitude_min_m": 400, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"2": [11, 12], "3": [10, 11], "4": [10, 11], "5": [10]},
            "days_to_maturity": {"medium_season": 140, "long_season": 180}
        },
        "varieties": [
            {"name": "Nyimo Red", "type": "open_pollinated", "maturity_days": 150, "yield_t_ha": 0.8, "input_level": "low"},
            {"name": "Nyimo Cream", "type": "open_pollinated", "maturity_days": 140, "yield_t_ha": 1.0, "input_level": "low"},
            {"name": "S19-3", "type": "improved_opv", "maturity_days": 130, "yield_t_ha": 1.5, "input_level": "medium"}
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 300},
        "yield_t_ha": {"low_input": 0.6, "medium_input": 1.2, "high_input": 2.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Single Superphosphate", "kg_per_ha": 150}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 3000}
        ],
        "pests": ["PEST_006", "PEST_012"],
        "diseases": [],
        "companion_crops": ["CROP_004", "CROP_031"],
        "rotation_partners": ["CROP_001", "CROP_002"],
        "market": {"price_usd_per_kg": 1.20, "price_updated": "2026-01", "demand": "high"}
    },

    # ── CROP_033: Pigeon peas (Nhunguru) ──────────────────────────────────────
    # Perennial / annual legume. Fixes 40-200 kg N/ha/year. Drought tolerant.
    # Deep taproot breaks hardpans. Residues improve soil structure.
    # Major food and income crop in Region 3-5. Often intercropped with maize.
    {
        "id": "CROP_033",
        "name": "Pigeon peas",
        "local_names": {"shona": "Nhunguru", "ndebele": "Amandumbe amancane"},
        "type": "legume",
        "agro_regions": [3, 4, 5],
        "soil": {
            "ph_min": 5.0, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 30, "moisture_max": 65, "moisture_optimal": 50,
            "texture": ["loam", "sandy_loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 38, "temp_optimal_c": 27,
            "rainfall_min_mm": 400, "rainfall_max_mm": 1000,
            "altitude_min_m": 400, "altitude_max_m": 1500
        },
        "planting": {
            "months_by_region": {"3": [11, 12], "4": [11, 12], "5": [10, 11]},
            "days_to_maturity": {"short_season": 120, "medium_season": 180, "long_season": 240}
        },
        "varieties": [
            {"name": "ICPL 87119 (Asha)", "type": "improved_opv", "maturity_days": 120, "yield_t_ha": 1.5, "input_level": "low"},
            {"name": "ICEAP 00557", "type": "improved_opv", "maturity_days": 180, "yield_t_ha": 2.0, "input_level": "medium"},
            {"name": "Local Long Duration", "type": "open_pollinated", "maturity_days": 240, "yield_t_ha": 1.0, "input_level": "low"}
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 400},
        "yield_t_ha": {"low_input": 0.8, "medium_input": 1.5, "high_input": 2.5},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Single Superphosphate", "kg_per_ha": 200}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 2000}
        ],
        "pests": ["PEST_006", "PEST_008"],
        "diseases": [],
        "companion_crops": ["CROP_001", "CROP_002"],
        "rotation_partners": ["CROP_001", "CROP_004"],
        "market": {"price_usd_per_kg": 0.75, "price_updated": "2026-01", "demand": "medium"}
    },

    # ── CROP_034: Lablab (Dolichos bean) ──────────────────────────────────────
    # Multipurpose — food, fodder, green manure. Smothers weeds. Drought
    # tolerant. Important in push-pull systems alongside desmodium. Well
    # adapted to Zimbabwe's drier regions. Fixes up to 100 kg N/ha.
    {
        "id": "CROP_034",
        "name": "Lablab",
        "local_names": {"shona": "Nyemba dema", "ndebele": "Ibhontshisi elimnyama"},
        "type": "legume",
        "agro_regions": [2, 3, 4, 5],
        "soil": {
            "ph_min": 5.0, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 25, "moisture_max": 65, "moisture_optimal": 45,
            "texture": ["loam", "sandy_loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 35, "temp_optimal_c": 28,
            "rainfall_min_mm": 300, "rainfall_max_mm": 900,
            "altitude_min_m": 400, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"2": [11, 12], "3": [10, 11], "4": [10, 11], "5": [10]},
            "days_to_maturity": {"short_season": 90, "medium_season": 150}
        },
        "varieties": [
            {"name": "Highworth", "type": "improved_opv", "maturity_days": 90, "yield_t_ha": 1.0, "input_level": "low"},
            {"name": "Rongai", "type": "improved_opv", "maturity_days": 150, "yield_t_ha": 1.5, "input_level": "low"}
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 350},
        "yield_t_ha": {"low_input": 0.6, "medium_input": 1.2, "high_input": 2.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Single Superphosphate", "kg_per_ha": 150}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 2000}
        ],
        "pests": ["PEST_006"],
        "diseases": [],
        "companion_crops": ["CROP_001", "CROP_002"],
        "rotation_partners": ["CROP_001"],
        "market": {"price_usd_per_kg": 0.65, "price_updated": "2026-01", "demand": "low"}
    },

    # ── CROP_035: Green peas ──────────────────────────────────────────────────
    # High-value cool-season legume. Region 1 and high-altitude Region 2.
    # Important for smallholder income and export. Requires cool temperatures
    # for pod setting — best in dry season with irrigation.
    {
        "id": "CROP_035",
        "name": "Green peas",
        "local_names": {"shona": "Pizi", "ndebele": "Amapizi"},
        "type": "legume",
        "agro_regions": [1, 2],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 50, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 10, "temp_max_c": 25, "temp_optimal_c": 16,
            "rainfall_min_mm": 600, "rainfall_max_mm": 1200,
            "altitude_min_m": 900, "altitude_max_m": 2300
        },
        "planting": {
            "months_by_region": {"1": [4, 5, 6, 7], "2": [4, 5, 6]},
            "days_to_maturity": {"short_season": 60, "medium_season": 90}
        },
        "varieties": [
            {"name": "Greenfeast", "type": "open_pollinated", "maturity_days": 70, "yield_t_ha": 5.0, "input_level": "medium"},
            {"name": "Meteor", "type": "open_pollinated", "maturity_days": 60, "yield_t_ha": 4.0, "input_level": "low"},
            {"name": "Sugar Snap", "type": "open_pollinated", "maturity_days": 70, "yield_t_ha": 6.0, "input_level": "high"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 400},
        "yield_t_ha": {"low_input": 3.0, "medium_input": 5.0, "high_input": 8.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 200},
            {"phase": "top_dress", "days_after_planting": 28, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 50}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 4000}
        ],
        "pests": ["PEST_006"],
        "diseases": ["DIS_009"],
        "companion_crops": ["CROP_039", "CROP_040"],
        "rotation_partners": ["CROP_001", "CROP_013"],
        "market": {"price_usd_per_kg": 1.50, "price_updated": "2026-01", "demand": "high"}
    },

    # ── CROP_036: Okra (Derere) ───────────────────────────────────────────────
    # One of Zimbabwe's most popular vegetables. Extremely heat tolerant.
    # Used fresh and dried. Mucilage used in traditional cooking (derere).
    # High demand in both rural and urban markets. Short growing cycle
    # makes it excellent for kitchen gardens and quick income.
    {
        "id": "CROP_036",
        "name": "Okra",
        "local_names": {"shona": "Derere", "ndebele": "Isigwagwa"},
        "type": "vegetable",
        "agro_regions": [2, 3, 4, 5],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 40, "moisture_max": 75, "moisture_optimal": 60,
            "texture": ["loam", "clay_loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 38, "temp_optimal_c": 30,
            "rainfall_min_mm": 400, "rainfall_max_mm": 900,
            "altitude_min_m": 400, "altitude_max_m": 1600
        },
        "planting": {
            "months_by_region": {"2": [9, 10, 11], "3": [9, 10, 11], "4": [9, 10], "5": [9, 10]},
            "days_to_maturity": {"short_season": 55, "medium_season": 70}
        },
        "varieties": [
            {"name": "Clemson Spineless", "type": "open_pollinated", "maturity_days": 58, "yield_t_ha": 8.0, "input_level": "low"},
            {"name": "Pusa Sawani", "type": "open_pollinated", "maturity_days": 55, "yield_t_ha": 7.0, "input_level": "low"},
            {"name": "Local Green", "type": "open_pollinated", "maturity_days": 70, "yield_t_ha": 5.0, "input_level": "low"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 400},
        "yield_t_ha": {"low_input": 5.0, "medium_input": 8.0, "high_input": 14.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 200},
            {"phase": "top_dress", "days_after_planting": 30, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000},
            {"phase": "top_dress", "product": "Liquid manure", "kg_per_ha": 2000}
        ],
        "pests": ["PEST_006", "PEST_009"],
        "diseases": [],
        "companion_crops": ["CROP_013", "CROP_030"],
        "rotation_partners": ["CROP_001", "CROP_007"],
        "market": {"price_usd_per_kg": 0.90, "price_updated": "2026-01", "demand": "high"}
    },

    # ── CROP_037: Covo / Swiss chard ─────────────────────────────────────────
    # Zimbabwe's most popular leafy green. Known locally as "covo" — eaten
    # daily across all income levels. Grows year-round with irrigation.
    # Extremely fast (40 days to first cut), very high nutritional value.
    # One of the best crops for household nutrition and quick cash income.
    {
        "id": "CROP_037",
        "name": "Covo (Swiss chard)",
        "local_names": {"shona": "Covo / Mowa", "ndebele": "Ikhowe"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3, 4],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 6.8,
            "moisture_min": 50, "moisture_max": 85, "moisture_optimal": 70,
            "texture": ["loam", "clay_loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 8, "temp_max_c": 30, "temp_optimal_c": 18,
            "rainfall_min_mm": 500, "rainfall_max_mm": 1500,
            "altitude_min_m": 300, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [1,2,3,4,5,6,7,8,9,10,11,12], "2": [1,2,3,4,5,6,7,8,9,10,11,12], "3": [3,4,5,6,7,8,9], "4": [4,5,6,7,8]},
            "days_to_maturity": {"short_season": 40, "medium_season": 60}
        },
        "varieties": [
            {"name": "Fordhook Giant", "type": "open_pollinated", "maturity_days": 50, "yield_t_ha": 20.0, "input_level": "medium"},
            {"name": "Lucullus", "type": "open_pollinated", "maturity_days": 45, "yield_t_ha": 18.0, "input_level": "medium"},
            {"name": "Local Covo", "type": "open_pollinated", "maturity_days": 55, "yield_t_ha": 12.0, "input_level": "low"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 500},
        "yield_t_ha": {"low_input": 10.0, "medium_input": 20.0, "high_input": 35.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress", "days_after_planting": 21, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 150},
            {"phase": "top_dress_2", "days_after_planting": 45, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 8000},
            {"phase": "top_dress", "product": "Liquid manure", "kg_per_ha": 3000}
        ],
        "pests": ["PEST_017", "PEST_020"],
        "diseases": ["DIS_017", "DIS_018"],
        "companion_crops": ["CROP_038", "CROP_039"],
        "rotation_partners": ["CROP_013", "CROP_007"],
        "market": {"price_usd_per_kg": 0.45, "price_updated": "2026-01", "demand": "very_high"}
    },

    # ── CROP_038: Spinach ─────────────────────────────────────────────────────
    {
        "id": "CROP_038",
        "name": "Spinach",
        "local_names": {"shona": "Sipinashi", "ndebele": "Isipinashi"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 55, "moisture_max": 85, "moisture_optimal": 70,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 5, "temp_max_c": 24, "temp_optimal_c": 16,
            "rainfall_min_mm": 500, "rainfall_max_mm": 1200,
            "altitude_min_m": 600, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [1,2,3,4,5,6,7,8,9,10,11,12], "2": [3,4,5,6,7,8,9], "3": [4,5,6,7,8]},
            "days_to_maturity": {"short_season": 40, "medium_season": 55}
        },
        "varieties": [
            {"name": "Viroflay", "type": "open_pollinated", "maturity_days": 45, "yield_t_ha": 15.0, "input_level": "medium"},
            {"name": "Bloomsdale", "type": "open_pollinated", "maturity_days": 48, "yield_t_ha": 14.0, "input_level": "medium"},
            {"name": "F1 Hector", "type": "hybrid", "maturity_days": 40, "yield_t_ha": 20.0, "input_level": "high"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 450},
        "yield_t_ha": {"low_input": 8.0, "medium_input": 14.0, "high_input": 22.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress", "days_after_planting": 21, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 120}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 6000}
        ],
        "pests": ["PEST_017", "PEST_006"],
        "diseases": ["DIS_018"],
        "companion_crops": ["CROP_037", "CROP_039"],
        "rotation_partners": ["CROP_013", "CROP_014"],
        "market": {"price_usd_per_kg": 0.55, "price_updated": "2026-01", "demand": "high"}
    },

    # ── CROP_039: Carrots ─────────────────────────────────────────────────────
    {
        "id": "CROP_039",
        "name": "Carrots",
        "local_names": {"shona": "Kheroti", "ndebele": "Amakaridi"},
        "type": "root_tuber",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 55, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["sandy_loam", "loam"]
        },
        "climate": {
            "temp_min_c": 10, "temp_max_c": 24, "temp_optimal_c": 16,
            "rainfall_min_mm": 500, "rainfall_max_mm": 1000,
            "altitude_min_m": 800, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [3,4,5,6,7,8,9], "2": [4,5,6,7,8], "3": [5,6,7]},
            "days_to_maturity": {"short_season": 70, "medium_season": 90}
        },
        "varieties": [
            {"name": "Chantenay Red Core", "type": "open_pollinated", "maturity_days": 75, "yield_t_ha": 25.0, "input_level": "medium"},
            {"name": "Nantes", "type": "open_pollinated", "maturity_days": 70, "yield_t_ha": 22.0, "input_level": "medium"},
            {"name": "Kuroda", "type": "open_pollinated", "maturity_days": 85, "yield_t_ha": 28.0, "input_level": "high"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 500},
        "yield_t_ha": {"low_input": 15.0, "medium_input": 25.0, "high_input": 40.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress", "days_after_planting": 35, "product": "Potassium Chloride (MOP)", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Well-rotted compost", "kg_per_ha": 6000}
        ],
        "pests": ["PEST_006"],
        "diseases": [],
        "companion_crops": ["CROP_038", "CROP_014"],
        "rotation_partners": ["CROP_013", "CROP_015"],
        "market": {"price_usd_per_kg": 0.65, "price_updated": "2026-01", "demand": "high"}
    },

    # ── CROP_040: Beetroot ────────────────────────────────────────────────────
    {
        "id": "CROP_040",
        "name": "Beetroot",
        "local_names": {"shona": "Bitriti", "ndebele": "Ibhitiruti"},
        "type": "root_tuber",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 50, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 10, "temp_max_c": 25, "temp_optimal_c": 18,
            "rainfall_min_mm": 500, "rainfall_max_mm": 1000,
            "altitude_min_m": 600, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [1,2,3,4,5,6,7,8,9,10,11,12], "2": [3,4,5,6,7,8,9], "3": [4,5,6,7,8]},
            "days_to_maturity": {"short_season": 55, "medium_season": 70}
        },
        "varieties": [
            {"name": "Detroit Dark Red", "type": "open_pollinated", "maturity_days": 60, "yield_t_ha": 20.0, "input_level": "medium"},
            {"name": "Boltardy", "type": "open_pollinated", "maturity_days": 55, "yield_t_ha": 18.0, "input_level": "low"},
            {"name": "Moneta F1", "type": "hybrid", "maturity_days": 60, "yield_t_ha": 28.0, "input_level": "high"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 450},
        "yield_t_ha": {"low_input": 12.0, "medium_input": 22.0, "high_input": 35.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 250},
            {"phase": "top_dress", "days_after_planting": 30, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000}
        ],
        "pests": ["PEST_006"],
        "diseases": [],
        "companion_crops": ["CROP_039", "CROP_015"],
        "rotation_partners": ["CROP_013", "CROP_001"],
        "market": {"price_usd_per_kg": 0.70, "price_updated": "2026-01", "demand": "medium"}
    },

    # ── CROP_041: Cucumber ────────────────────────────────────────────────────
    {
        "id": "CROP_041",
        "name": "Cucumber",
        "local_names": {"shona": "Guriri", "ndebele": "Ikukumba"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3, 4],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 55, "moisture_max": 85, "moisture_optimal": 70,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 35, "temp_optimal_c": 25,
            "rainfall_min_mm": 500, "rainfall_max_mm": 1200,
            "altitude_min_m": 400, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [9,10,11], "2": [9,10,11], "3": [9,10], "4": [9,10]},
            "days_to_maturity": {"short_season": 50, "medium_season": 65}
        },
        "varieties": [
            {"name": "Ashley", "type": "open_pollinated", "maturity_days": 65, "yield_t_ha": 20.0, "input_level": "medium"},
            {"name": "Marketmore", "type": "open_pollinated", "maturity_days": 58, "yield_t_ha": 22.0, "input_level": "medium"},
            {"name": "Paladin F1", "type": "hybrid", "maturity_days": 50, "yield_t_ha": 35.0, "input_level": "high"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 550},
        "yield_t_ha": {"low_input": 12.0, "medium_input": 22.0, "high_input": 40.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress", "days_after_planting": 21, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 150}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 6000}
        ],
        "pests": ["PEST_021", "PEST_009"],
        "diseases": ["DIS_020"],
        "companion_crops": ["CROP_030", "CROP_013"],
        "rotation_partners": ["CROP_001", "CROP_008"],
        "market": {"price_usd_per_kg": 0.80, "price_updated": "2026-01", "demand": "high"}
    },

    # ── CROP_042: Eggplant / Brinjal (Rabhodhi) ───────────────────────────────
    {
        "id": "CROP_042",
        "name": "Eggplant (Brinjal)",
        "local_names": {"shona": "Rabhodhi", "ndebele": "Ilabhodhi"},
        "type": "vegetable",
        "agro_regions": [2, 3, 4],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.0, "ph_optimal": 6.0,
            "moisture_min": 50, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "clay_loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 35, "temp_optimal_c": 27,
            "rainfall_min_mm": 500, "rainfall_max_mm": 1100,
            "altitude_min_m": 400, "altitude_max_m": 1600
        },
        "planting": {
            "months_by_region": {"2": [9,10,11], "3": [9,10,11], "4": [9,10]},
            "days_to_maturity": {"short_season": 70, "medium_season": 90}
        },
        "varieties": [
            {"name": "Black Beauty", "type": "open_pollinated", "maturity_days": 75, "yield_t_ha": 15.0, "input_level": "medium"},
            {"name": "Bonica F1", "type": "hybrid", "maturity_days": 70, "yield_t_ha": 25.0, "input_level": "high"},
            {"name": "Local Purple", "type": "open_pollinated", "maturity_days": 90, "yield_t_ha": 10.0, "input_level": "low"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 500},
        "yield_t_ha": {"low_input": 8.0, "medium_input": 16.0, "high_input": 28.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress", "days_after_planting": 30, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 150},
            {"phase": "top_dress_2", "days_after_planting": 60, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 6000}
        ],
        "pests": ["PEST_017", "PEST_009"],
        "diseases": [],
        "companion_crops": ["CROP_013", "CROP_030"],
        "rotation_partners": ["CROP_001", "CROP_007"],
        "market": {"price_usd_per_kg": 0.85, "price_updated": "2026-01", "demand": "medium"}
    },

    # ── CROP_043: Green beans / French beans ──────────────────────────────────
    # Important export crop from Region 1 (Nyanga, Vumba highlands). Grown
    # under contract for European supermarkets via Fresh from the Farm and
    # other exporters. High value but requires strict quality control.
    {
        "id": "CROP_043",
        "name": "Green beans",
        "local_names": {"shona": "Mbatata dema / Bhinzi", "ndebele": "Ibhontshisi eliluhlaza"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 55, "moisture_max": 80, "moisture_optimal": 68,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 14, "temp_max_c": 28, "temp_optimal_c": 20,
            "rainfall_min_mm": 600, "rainfall_max_mm": 1200,
            "altitude_min_m": 900, "altitude_max_m": 2200
        },
        "planting": {
            "months_by_region": {"1": [3,4,5,6,7,8], "2": [4,5,6,7], "3": [5,6,7]},
            "days_to_maturity": {"short_season": 55, "medium_season": 65}
        },
        "varieties": [
            {"name": "Amy", "type": "hybrid", "maturity_days": 55, "yield_t_ha": 12.0, "input_level": "high"},
            {"name": "Paulista", "type": "hybrid", "maturity_days": 58, "yield_t_ha": 10.0, "input_level": "high"},
            {"name": "Contender", "type": "open_pollinated", "maturity_days": 65, "yield_t_ha": 7.0, "input_level": "medium"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 500},
        "yield_t_ha": {"low_input": 4.0, "medium_input": 8.0, "high_input": 14.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress", "days_after_planting": 28, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000}
        ],
        "pests": ["PEST_011", "PEST_006"],
        "diseases": ["DIS_009"],
        "companion_crops": ["CROP_039", "CROP_038"],
        "rotation_partners": ["CROP_013", "CROP_001"],
        "market": {"price_usd_per_kg": 1.80, "price_updated": "2026-01", "demand": "high"}
    },

    # ── CROP_044: Lettuce ─────────────────────────────────────────────────────
    {
        "id": "CROP_044",
        "name": "Lettuce",
        "local_names": {"shona": "Raticha", "ndebele": "Irathisi"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 60, "moisture_max": 85, "moisture_optimal": 72,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 7, "temp_max_c": 24, "temp_optimal_c": 16,
            "rainfall_min_mm": 500, "rainfall_max_mm": 1200,
            "altitude_min_m": 700, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [1,2,3,4,5,6,7,8,9,10,11,12], "2": [3,4,5,6,7,8,9], "3": [5,6,7]},
            "days_to_maturity": {"short_season": 40, "medium_season": 55}
        },
        "varieties": [
            {"name": "Great Lakes", "type": "open_pollinated", "maturity_days": 55, "yield_t_ha": 20.0, "input_level": "medium"},
            {"name": "Black Seeded Simpson", "type": "open_pollinated", "maturity_days": 40, "yield_t_ha": 15.0, "input_level": "low"},
            {"name": "Lollo Rossa", "type": "open_pollinated", "maturity_days": 50, "yield_t_ha": 18.0, "input_level": "medium"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 400},
        "yield_t_ha": {"low_input": 10.0, "medium_input": 20.0, "high_input": 30.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 250},
            {"phase": "top_dress", "days_after_planting": 21, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000}
        ],
        "pests": ["PEST_006", "PEST_009"],
        "diseases": [],
        "companion_crops": ["CROP_037", "CROP_039"],
        "rotation_partners": ["CROP_013", "CROP_014"],
        "market": {"price_usd_per_kg": 0.90, "price_updated": "2026-01", "demand": "medium"}
    },

    # ── CROP_045: Sweet corn ──────────────────────────────────────────────────
    # Different market from grain maize — sold fresh, higher price point.
    # Popular at roadside stands and supermarkets. Short cycle (65-75 days).
    {
        "id": "CROP_045",
        "name": "Sweet corn",
        "local_names": {"shona": "Chibage chinotapira", "ndebele": "Umbila omtoti"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 5.8, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 50, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "sandy_loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 16, "temp_max_c": 32, "temp_optimal_c": 24,
            "rainfall_min_mm": 500, "rainfall_max_mm": 900,
            "altitude_min_m": 600, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [9,10,11], "2": [9,10,11], "3": [9,10]},
            "days_to_maturity": {"short_season": 65, "medium_season": 75}
        },
        "varieties": [
            {"name": "Jubilee", "type": "open_pollinated", "maturity_days": 75, "yield_t_ha": 8.0, "input_level": "medium"},
            {"name": "Golden Bantam", "type": "open_pollinated", "maturity_days": 70, "yield_t_ha": 7.0, "input_level": "low"},
            {"name": "Challenger F1", "type": "hybrid", "maturity_days": 65, "yield_t_ha": 12.0, "input_level": "high"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 450},
        "yield_t_ha": {"low_input": 5.0, "medium_input": 9.0, "high_input": 14.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound D", "kg_per_ha": 200},
            {"phase": "top_dress", "days_after_planting": 28, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 150}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000}
        ],
        "pests": ["PEST_001", "PEST_003"],
        "diseases": ["DIS_001"],
        "companion_crops": ["CROP_008", "CROP_019"],
        "rotation_partners": ["CROP_008", "CROP_007"],
        "market": {"price_usd_per_kg": 0.50, "price_updated": "2026-01", "demand": "high"}
    },

    # ── CROP_046: Citrus (Orange) ─────────────────────────────────────────────
    # Mazowe, Karoi, and the Lowveld are Zimbabwe's major citrus belts.
    # Valencia oranges are the main export variety. High value, long-term
    # investment (4-5 years to first commercial harvest, 20-year lifespan).
    {
        "id": "CROP_046",
        "name": "Citrus (Orange)",
        "local_names": {"shona": "Muchungwa", "ndebele": "I-orinja"},
        "type": "fruit",
        "agro_regions": [2, 3, 4],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.0, "ph_optimal": 6.0,
            "moisture_min": 45, "moisture_max": 75, "moisture_optimal": 60,
            "texture": ["sandy_loam", "loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 15, "temp_max_c": 35, "temp_optimal_c": 25,
            "rainfall_min_mm": 600, "rainfall_max_mm": 1200,
            "altitude_min_m": 400, "altitude_max_m": 1500
        },
        "planting": {
            "months_by_region": {"2": [9,10,11], "3": [9,10,11], "4": [9,10,11]},
            "days_to_maturity": {"long_season": 1825}
        },
        "varieties": [
            {"name": "Valencia Late", "type": "improved_opv", "maturity_days": 1825, "yield_t_ha": 25.0, "input_level": "high"},
            {"name": "Washington Navel", "type": "improved_opv", "maturity_days": 1460, "yield_t_ha": 20.0, "input_level": "high"},
            {"name": "Navelate", "type": "improved_opv", "maturity_days": 1550, "yield_t_ha": 22.0, "input_level": "high"}
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 1200},
        "yield_t_ha": {"low_input": 10.0, "medium_input": 20.0, "high_input": 35.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 200},
            {"phase": "top_dress", "days_after_planting": 60, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 150},
            {"phase": "top_dress_2", "days_after_planting": 120, "product": "Potassium Chloride (MOP)", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000}
        ],
        "pests": ["PEST_009", "PEST_006"],
        "diseases": [],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 0.40, "price_updated": "2026-01", "demand": "very_high"}
    },

    # ── CROP_047: Guava ───────────────────────────────────────────────────────
    # Extremely common across Zimbabwe — grows semi-wild in many communal
    # areas. High vitamin C. Can be processed into juice, jam, dried fruit.
    # Very drought tolerant once established. High nutritional value for
    # food security.
    {
        "id": "CROP_047",
        "name": "Guava",
        "local_names": {"shona": "Gwabha", "ndebele": "I-gwava"},
        "type": "fruit",
        "agro_regions": [2, 3, 4, 5],
        "soil": {
            "ph_min": 4.5, "ph_max": 7.5, "ph_optimal": 6.0,
            "moisture_min": 30, "moisture_max": 75, "moisture_optimal": 55,
            "texture": ["loam", "sandy_loam", "clay_loam", "sandy"]
        },
        "climate": {
            "temp_min_c": 15, "temp_max_c": 38, "temp_optimal_c": 28,
            "rainfall_min_mm": 400, "rainfall_max_mm": 1200,
            "altitude_min_m": 400, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"2": [9,10,11], "3": [9,10,11], "4": [9,10,11], "5": [9,10]},
            "days_to_maturity": {"medium_season": 1095}
        },
        "varieties": [
            {"name": "Beaumont", "type": "improved_opv", "maturity_days": 1095, "yield_t_ha": 25.0, "input_level": "low"},
            {"name": "Fan Retief", "type": "improved_opv", "maturity_days": 1095, "yield_t_ha": 30.0, "input_level": "medium"},
            {"name": "Local Guava", "type": "open_pollinated", "maturity_days": 1095, "yield_t_ha": 15.0, "input_level": "low"}
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 600},
        "yield_t_ha": {"low_input": 10.0, "medium_input": 22.0, "high_input": 40.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 150},
            {"phase": "top_dress", "days_after_planting": 90, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 3000}
        ],
        "pests": ["PEST_009", "PEST_025"],
        "diseases": [],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 0.35, "price_updated": "2026-01", "demand": "medium"}
    },

    # ── CROP_048: Passion fruit ───────────────────────────────────────────────
    {
        "id": "CROP_048",
        "name": "Passion fruit",
        "local_names": {"shona": "Paseni", "ndebele": "Iphasifudi"},
        "type": "fruit",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 50, "moisture_max": 80, "moisture_optimal": 65,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 16, "temp_max_c": 30, "temp_optimal_c": 23,
            "rainfall_min_mm": 700, "rainfall_max_mm": 1500,
            "altitude_min_m": 900, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [9,10,11], "2": [9,10,11], "3": [9,10]},
            "days_to_maturity": {"medium_season": 365}
        },
        "varieties": [
            {"name": "Purple Granadilla", "type": "open_pollinated", "maturity_days": 365, "yield_t_ha": 15.0, "input_level": "medium"},
            {"name": "Yellow Granadilla", "type": "open_pollinated", "maturity_days": 365, "yield_t_ha": 20.0, "input_level": "high"},
            {"name": "Kaveri", "type": "hybrid", "maturity_days": 365, "yield_t_ha": 22.0, "input_level": "high"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 800},
        "yield_t_ha": {"low_input": 8.0, "medium_input": 15.0, "high_input": 25.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress", "days_after_planting": 60, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 150},
            {"phase": "top_dress_2", "days_after_planting": 120, "product": "Potassium Chloride (MOP)", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000}
        ],
        "pests": ["PEST_009", "PEST_006"],
        "diseases": [],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 1.80, "price_updated": "2026-01", "demand": "high"}
    },

    # ── CROP_049: Lemon ───────────────────────────────────────────────────────
    {
        "id": "CROP_049",
        "name": "Lemon",
        "local_names": {"shona": "Reimoni", "ndebele": "Ilamula"},
        "type": "fruit",
        "agro_regions": [2, 3, 4],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.0, "ph_optimal": 6.0,
            "moisture_min": 45, "moisture_max": 75, "moisture_optimal": 60,
            "texture": ["sandy_loam", "loam"]
        },
        "climate": {
            "temp_min_c": 14, "temp_max_c": 35, "temp_optimal_c": 25,
            "rainfall_min_mm": 500, "rainfall_max_mm": 1200,
            "altitude_min_m": 400, "altitude_max_m": 1500
        },
        "planting": {
            "months_by_region": {"2": [9,10,11], "3": [9,10,11], "4": [9,10]},
            "days_to_maturity": {"long_season": 1460}
        },
        "varieties": [
            {"name": "Eureka", "type": "improved_opv", "maturity_days": 1460, "yield_t_ha": 20.0, "input_level": "high"},
            {"name": "Lisbon", "type": "improved_opv", "maturity_days": 1460, "yield_t_ha": 18.0, "input_level": "medium"},
            {"name": "Villafranca", "type": "improved_opv", "maturity_days": 1460, "yield_t_ha": 22.0, "input_level": "high"}
        ],
        "irrigation": {"required": "full", "water_mm_per_season": 1000},
        "yield_t_ha": {"low_input": 8.0, "medium_input": 18.0, "high_input": 30.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 200},
            {"phase": "top_dress", "days_after_planting": 60, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 120}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 4000}
        ],
        "pests": ["PEST_009", "PEST_006"],
        "diseases": [],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 0.60, "price_updated": "2026-01", "demand": "high"}
    },

    # ── CROP_050: Coffee (Arabica) ─────────────────────────────────────────────
    # Zimbabwe's Eastern Highlands (Chipinge, Honde Valley, Nyanga) produce
    # some of Africa's finest Arabica coffee. Zimbabwe AA is internationally
    # recognised. High-value, long-term crop. Chipinge Coffee Growers
    # Association provides support. Requires altitude 1000-2000m, cool
    # temperatures — Region 1 only.
    {
        "id": "CROP_050",
        "name": "Coffee (Arabica)",
        "local_names": {"shona": "Kofi", "ndebele": "I-khoffi"},
        "type": "cash_crop",
        "agro_regions": [1],
        "soil": {
            "ph_min": 5.5, "ph_max": 6.5, "ph_optimal": 6.0,
            "moisture_min": 55, "moisture_max": 80, "moisture_optimal": 70,
            "texture": ["loam", "clay_loam", "volcanic_loam"]
        },
        "climate": {
            "temp_min_c": 15, "temp_max_c": 24, "temp_optimal_c": 19,
            "rainfall_min_mm": 1200, "rainfall_max_mm": 2000,
            "altitude_min_m": 1000, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [9, 10, 11]},
            "days_to_maturity": {"long_season": 1460}
        },
        "varieties": [
            {"name": "Bourbon", "type": "improved_opv", "maturity_days": 1460, "yield_t_ha": 2.0, "input_level": "medium"},
            {"name": "Catimor", "type": "improved_opv", "maturity_days": 1460, "yield_t_ha": 3.0, "input_level": "high"},
            {"name": "K7", "type": "improved_opv", "maturity_days": 1460, "yield_t_ha": 2.5, "input_level": "medium"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 800},
        "yield_t_ha": {"low_input": 1.0, "medium_input": 2.0, "high_input": 4.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress", "days_after_planting": 90, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 200},
            {"phase": "top_dress_2", "days_after_planting": 180, "product": "Potassium Chloride (MOP)", "kg_per_ha": 150}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 6000}
        ],
        "pests": ["PEST_009"],
        "diseases": [],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 4.50, "price_updated": "2026-01", "demand": "very_high"}
    },

    # ── CROP_051: Macadamia ───────────────────────────────────────────────────
    # Growing commercial sector in Zimbabwe's Eastern Highlands. Long-term
    # investment (7 years to commercial production, 40-year lifespan).
    # Premium export price — Australian market. Increasing smallholder
    # adoption through outgrower schemes.
    {
        "id": "CROP_051",
        "name": "Macadamia",
        "local_names": {"shona": "Makademia", "ndebele": "I-macademia"},
        "type": "cash_crop",
        "agro_regions": [1, 2],
        "soil": {
            "ph_min": 5.0, "ph_max": 6.5, "ph_optimal": 5.5,
            "moisture_min": 55, "moisture_max": 80, "moisture_optimal": 68,
            "texture": ["loam", "clay_loam", "well_drained"]
        },
        "climate": {
            "temp_min_c": 12, "temp_max_c": 28, "temp_optimal_c": 20,
            "rainfall_min_mm": 1000, "rainfall_max_mm": 1800,
            "altitude_min_m": 800, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [9, 10, 11], "2": [9, 10, 11]},
            "days_to_maturity": {"long_season": 2555}
        },
        "varieties": [
            {"name": "816 (A4)", "type": "improved_opv", "maturity_days": 2555, "yield_t_ha": 3.5, "input_level": "high"},
            {"name": "788 (A16)", "type": "improved_opv", "maturity_days": 2555, "yield_t_ha": 4.0, "input_level": "high"},
            {"name": "Beaumont (695)", "type": "improved_opv", "maturity_days": 2555, "yield_t_ha": 3.0, "input_level": "medium"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 700},
        "yield_t_ha": {"low_input": 1.5, "medium_input": 3.0, "high_input": 5.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 250},
            {"phase": "top_dress", "days_after_planting": 90, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 150}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 5000}
        ],
        "pests": ["PEST_009"],
        "diseases": [],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 5.00, "price_updated": "2026-01", "demand": "very_high"}
    },

    # ── CROP_052: Tea ─────────────────────────────────────────────────────────
    # Eastern Highlands (Honde Valley) is Zimbabwe's tea growing region.
    # Tanganda Tea is one of Africa's largest tea estates. Smallholder
    # outgrower schemes exist. Requires high altitude, high rainfall,
    # cool temperatures. Very long-term investment (3 years to first harvest).
    {
        "id": "CROP_052",
        "name": "Tea",
        "local_names": {"shona": "Tiyi", "ndebele": "Itiye"},
        "type": "cash_crop",
        "agro_regions": [1],
        "soil": {
            "ph_min": 4.5, "ph_max": 6.0, "ph_optimal": 5.0,
            "moisture_min": 65, "moisture_max": 90, "moisture_optimal": 78,
            "texture": ["loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 13, "temp_max_c": 25, "temp_optimal_c": 18,
            "rainfall_min_mm": 1400, "rainfall_max_mm": 2500,
            "altitude_min_m": 1200, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [9, 10, 11]},
            "days_to_maturity": {"long_season": 1095}
        },
        "varieties": [
            {"name": "Zimbabwe Local Clone", "type": "improved_opv", "maturity_days": 1095, "yield_t_ha": 2.5, "input_level": "high"},
            {"name": "SFS 150", "type": "improved_opv", "maturity_days": 1095, "yield_t_ha": 3.0, "input_level": "high"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 900},
        "yield_t_ha": {"low_input": 1.5, "medium_input": 2.5, "high_input": 4.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress", "days_after_planting": 90, "product": "Ammonium Sulphate", "kg_per_ha": 200}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 6000}
        ],
        "pests": ["PEST_009"],
        "diseases": [],
        "companion_crops": [],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 2.50, "price_updated": "2026-01", "demand": "very_high"}
    },

    # ── CROP_053: Moringa ─────────────────────────────────────────────────────
    # Called "the miracle tree" — leaves have more vitamin C than oranges,
    # more calcium than milk, more iron than spinach. Extremely drought
    # tolerant. Grows in all 5 regions. Leaves, pods, seeds all edible.
    # Water purification from seeds. Huge potential for nutrition and income.
    # Under-exploited across Zimbabwe.
    {
        "id": "CROP_053",
        "name": "Moringa",
        "local_names": {"shona": "Moringa / Mupindu", "ndebele": "I-moringa"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3, 4, 5],
        "soil": {
            "ph_min": 5.0, "ph_max": 8.5, "ph_optimal": 6.5,
            "moisture_min": 20, "moisture_max": 65, "moisture_optimal": 45,
            "texture": ["loam", "sandy_loam", "sandy", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 40, "temp_optimal_c": 28,
            "rainfall_min_mm": 250, "rainfall_max_mm": 1500,
            "altitude_min_m": 300, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [9,10,11], "2": [9,10,11], "3": [9,10,11], "4": [9,10,11], "5": [9,10]},
            "days_to_maturity": {"short_season": 60, "medium_season": 365}
        },
        "varieties": [
            {"name": "Moringa oleifera Local", "type": "open_pollinated", "maturity_days": 60, "yield_t_ha": 20.0, "input_level": "low"},
            {"name": "PKM-1 (leaf production)", "type": "improved_opv", "maturity_days": 60, "yield_t_ha": 35.0, "input_level": "medium"}
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 300},
        "yield_t_ha": {"low_input": 15.0, "medium_input": 25.0, "high_input": 40.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 100},
            {"phase": "top_dress", "days_after_planting": 45, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 50}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 3000}
        ],
        "pests": [],
        "diseases": [],
        "companion_crops": ["CROP_037", "CROP_036"],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 2.00, "price_updated": "2026-01", "demand": "growing"}
    },

    # ── CROP_054: Castor bean ─────────────────────────────────────────────────
    # Well adapted to Region 4-5. Oil used in pharmaceuticals, cosmetics,
    # lubricants, biodiesel. Drought tolerant. Grows on marginal soils.
    # Potential bioenergy crop for Zimbabwe's drier areas.
    {
        "id": "CROP_054",
        "name": "Castor bean",
        "local_names": {"shona": "Mupfure", "ndebele": "Ikhastali"},
        "type": "oilseed",
        "agro_regions": [3, 4, 5],
        "soil": {
            "ph_min": 5.0, "ph_max": 7.5, "ph_optimal": 6.0,
            "moisture_min": 25, "moisture_max": 60, "moisture_optimal": 45,
            "texture": ["sandy_loam", "loam", "sandy"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 38, "temp_optimal_c": 28,
            "rainfall_min_mm": 350, "rainfall_max_mm": 900,
            "altitude_min_m": 400, "altitude_max_m": 1500
        },
        "planting": {
            "months_by_region": {"3": [10, 11], "4": [10, 11], "5": [10]},
            "days_to_maturity": {"medium_season": 120, "long_season": 180}
        },
        "varieties": [
            {"name": "Aruna", "type": "improved_opv", "maturity_days": 120, "yield_t_ha": 1.5, "input_level": "low"},
            {"name": "GCH 4", "type": "hybrid", "maturity_days": 120, "yield_t_ha": 2.5, "input_level": "medium"},
            {"name": "Local Tall", "type": "open_pollinated", "maturity_days": 180, "yield_t_ha": 1.0, "input_level": "low"}
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 400},
        "yield_t_ha": {"low_input": 0.8, "medium_input": 1.5, "high_input": 2.5},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound S", "kg_per_ha": 150},
            {"phase": "top_dress", "days_after_planting": 35, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 75}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 2000}
        ],
        "pests": ["PEST_006"],
        "diseases": [],
        "companion_crops": ["CROP_004", "CROP_009"],
        "rotation_partners": ["CROP_002", "CROP_009"],
        "market": {"price_usd_per_kg": 0.55, "price_updated": "2026-01", "demand": "medium"}
    },

    # ── CROP_055: Safflower ───────────────────────────────────────────────────
    # Drought-tolerant oilseed for Regions 3-5. Grows on poor soils.
    # Oil is high in linoleic acid — good cooking and industrial oil.
    # Petals used as food colouring (poor man's saffron). Short season.
    {
        "id": "CROP_055",
        "name": "Safflower",
        "local_names": {"shona": "Safirawo", "ndebele": "I-safflower"},
        "type": "oilseed",
        "agro_regions": [3, 4, 5],
        "soil": {
            "ph_min": 5.5, "ph_max": 8.0, "ph_optimal": 6.5,
            "moisture_min": 20, "moisture_max": 55, "moisture_optimal": 40,
            "texture": ["loam", "clay_loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 15, "temp_max_c": 38, "temp_optimal_c": 26,
            "rainfall_min_mm": 300, "rainfall_max_mm": 700,
            "altitude_min_m": 500, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"3": [10, 11], "4": [10, 11], "5": [10]},
            "days_to_maturity": {"short_season": 90, "medium_season": 120}
        },
        "varieties": [
            {"name": "Thilak", "type": "improved_opv", "maturity_days": 100, "yield_t_ha": 1.2, "input_level": "low"},
            {"name": "HUS 305", "type": "hybrid", "maturity_days": 95, "yield_t_ha": 1.8, "input_level": "medium"},
            {"name": "Local", "type": "open_pollinated", "maturity_days": 120, "yield_t_ha": 0.8, "input_level": "low"}
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 350},
        "yield_t_ha": {"low_input": 0.6, "medium_input": 1.2, "high_input": 2.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound S", "kg_per_ha": 100},
            {"phase": "top_dress", "days_after_planting": 30, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 50}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 2000}
        ],
        "pests": ["PEST_006"],
        "diseases": [],
        "companion_crops": ["CROP_009", "CROP_004"],
        "rotation_partners": ["CROP_002", "CROP_007"],
        "market": {"price_usd_per_kg": 0.48, "price_updated": "2026-01", "demand": "low"}
    },

    # ── CROP_056: Ginger ──────────────────────────────────────────────────────
    # High-value spice crop. Under-exploited in Zimbabwe. Grows well in
    # Region 1-3 under shade or intercropped. Fresh ginger commands premium
    # prices at urban markets. Can be dried and exported.
    {
        "id": "CROP_056",
        "name": "Ginger",
        "local_names": {"shona": "Chinjinji / Tangawisi", "ndebele": "I-jingi"},
        "type": "root_tuber",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 5.5, "ph_max": 6.5, "ph_optimal": 6.0,
            "moisture_min": 60, "moisture_max": 85, "moisture_optimal": 75,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 20, "temp_max_c": 30, "temp_optimal_c": 25,
            "rainfall_min_mm": 700, "rainfall_max_mm": 1500,
            "altitude_min_m": 600, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"1": [9, 10, 11], "2": [9, 10, 11], "3": [9, 10]},
            "days_to_maturity": {"medium_season": 210, "long_season": 270}
        },
        "varieties": [
            {"name": "Rio De Janeiro", "type": "open_pollinated", "maturity_days": 240, "yield_t_ha": 15.0, "input_level": "medium"},
            {"name": "Maran", "type": "open_pollinated", "maturity_days": 210, "yield_t_ha": 12.0, "input_level": "medium"},
            {"name": "China Ginger", "type": "open_pollinated", "maturity_days": 270, "yield_t_ha": 10.0, "input_level": "low"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 800},
        "yield_t_ha": {"low_input": 8.0, "medium_input": 15.0, "high_input": 25.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 300},
            {"phase": "top_dress", "days_after_planting": 45, "product": "Potassium Chloride (MOP)", "kg_per_ha": 150},
            {"phase": "top_dress_2", "days_after_planting": 90, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Well-rotted manure", "kg_per_ha": 8000}
        ],
        "pests": ["PEST_009"],
        "diseases": [],
        "companion_crops": ["CROP_023", "CROP_022"],
        "rotation_partners": ["CROP_013", "CROP_001"],
        "market": {"price_usd_per_kg": 2.50, "price_updated": "2026-01", "demand": "high"}
    },

    # ── CROP_057: Jatropha ────────────────────────────────────────────────────
    # Biofuel/multipurpose shrub. Grows on degraded land in Regions 4-5.
    # Seeds yield 30-40% oil — can power diesel generators. Soap from oil.
    # Kernel meal is organic fertiliser. Drought tolerant. Good for
    # rehabilitating degraded soils and providing income on marginal land.
    {
        "id": "CROP_057",
        "name": "Jatropha",
        "local_names": {"shona": "Mupfura", "ndebele": "IJatropha"},
        "type": "cash_crop",
        "agro_regions": [3, 4, 5],
        "soil": {
            "ph_min": 5.0, "ph_max": 8.0, "ph_optimal": 6.5,
            "moisture_min": 20, "moisture_max": 60, "moisture_optimal": 40,
            "texture": ["sandy", "sandy_loam", "loam", "rocky"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 40, "temp_optimal_c": 28,
            "rainfall_min_mm": 250, "rainfall_max_mm": 1000,
            "altitude_min_m": 300, "altitude_max_m": 1800
        },
        "planting": {
            "months_by_region": {"3": [10, 11], "4": [10, 11], "5": [10]},
            "days_to_maturity": {"long_season": 1095}
        },
        "varieties": [
            {"name": "Jatropha curcas (non-toxic)", "type": "improved_opv", "maturity_days": 1095, "yield_t_ha": 2.0, "input_level": "low"},
            {"name": "Jatropha curcas (local)", "type": "open_pollinated", "maturity_days": 1095, "yield_t_ha": 1.2, "input_level": "low"}
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 350},
        "yield_t_ha": {"low_input": 0.8, "medium_input": 1.5, "high_input": 3.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound S", "kg_per_ha": 100}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 2000}
        ],
        "pests": [],
        "diseases": [],
        "companion_crops": ["CROP_004", "CROP_009"],
        "rotation_partners": [],
        "market": {"price_usd_per_kg": 0.40, "price_updated": "2026-01", "demand": "low"}
    },

    # ── CROP_058: Amaranth (Mowa) ─────────────────────────────────────────────
    # Traditional leafy vegetable and grain. Indigenous to Southern Africa.
    # Nutritionally superior to most cereals — high protein, iron, calcium.
    # Drought tolerant. Very short cycle (30 days to first leaf harvest).
    # The grain variety is increasingly recognised as a superfood globally.
    # Both food and income potential across all regions.
    {
        "id": "CROP_058",
        "name": "Amaranth",
        "local_names": {"shona": "Mowa / Donje", "ndebele": "Imbuya"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3, 4, 5],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 7.0,
            "moisture_min": 30, "moisture_max": 75, "moisture_optimal": 55,
            "texture": ["loam", "sandy_loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 16, "temp_max_c": 38, "temp_optimal_c": 28,
            "rainfall_min_mm": 300, "rainfall_max_mm": 1200,
            "altitude_min_m": 300, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [9,10,11,12], "2": [9,10,11,12], "3": [9,10,11], "4": [9,10,11], "5": [9,10]},
            "days_to_maturity": {"short_season": 30, "medium_season": 90}
        },
        "varieties": [
            {"name": "Amaranthus hybridus (leaf type)", "type": "open_pollinated", "maturity_days": 35, "yield_t_ha": 25.0, "input_level": "low"},
            {"name": "Amaranthus cruentus (grain type)", "type": "open_pollinated", "maturity_days": 90, "yield_t_ha": 2.5, "input_level": "medium"},
            {"name": "RVI (Rapid Vegetable Improvement)", "type": "improved_opv", "maturity_days": 30, "yield_t_ha": 30.0, "input_level": "low"}
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 350},
        "yield_t_ha": {"low_input": 15.0, "medium_input": 25.0, "high_input": 40.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 150},
            {"phase": "top_dress", "days_after_planting": 21, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 75}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 4000}
        ],
        "pests": ["PEST_006"],
        "diseases": [],
        "companion_crops": ["CROP_037", "CROP_053"],
        "rotation_partners": ["CROP_001", "CROP_007"],
        "market": {"price_usd_per_kg": 0.50, "price_updated": "2026-01", "demand": "growing"}
    },

    # ── CROP_059: Cowpea update → Lima bean (Dovi) ───────────────────────────
    # Lima beans are a distinct high-value legume from cowpeas. Grown
    # across Zimbabwe's drier regions. Drought tolerant. Both dry seeds
    # and green pods sold at market. Important protein source.
    {
        "id": "CROP_059",
        "name": "Lima bean",
        "local_names": {"shona": "Rupiza / Nyemba", "ndebele": "Ibhontshisi elikhulu"},
        "type": "legume",
        "agro_regions": [2, 3, 4],
        "soil": {
            "ph_min": 5.5, "ph_max": 7.0, "ph_optimal": 6.5,
            "moisture_min": 35, "moisture_max": 70, "moisture_optimal": 55,
            "texture": ["loam", "sandy_loam", "clay_loam"]
        },
        "climate": {
            "temp_min_c": 18, "temp_max_c": 32, "temp_optimal_c": 25,
            "rainfall_min_mm": 400, "rainfall_max_mm": 900,
            "altitude_min_m": 400, "altitude_max_m": 1600
        },
        "planting": {
            "months_by_region": {"2": [11, 12], "3": [10, 11], "4": [10, 11]},
            "days_to_maturity": {"medium_season": 120, "long_season": 150}
        },
        "varieties": [
            {"name": "Henderson Bush", "type": "open_pollinated", "maturity_days": 120, "yield_t_ha": 1.0, "input_level": "low"},
            {"name": "King of the Garden", "type": "open_pollinated", "maturity_days": 150, "yield_t_ha": 1.5, "input_level": "medium"},
            {"name": "Local Flat White", "type": "open_pollinated", "maturity_days": 130, "yield_t_ha": 0.8, "input_level": "low"}
        ],
        "irrigation": {"required": "rain_fed", "water_mm_per_season": 450},
        "yield_t_ha": {"low_input": 0.6, "medium_input": 1.2, "high_input": 2.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Single Superphosphate", "kg_per_ha": 150}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 3000}
        ],
        "pests": ["PEST_012", "PEST_006"],
        "diseases": ["DIS_009"],
        "companion_crops": ["CROP_001", "CROP_002"],
        "rotation_partners": ["CROP_001", "CROP_004"],
        "market": {"price_usd_per_kg": 0.80, "price_updated": "2026-01", "demand": "medium"}
    },

    # ── CROP_060: Herb garden pack — Coriander ────────────────────────────────
    # Fast-growing herb with consistent urban demand. Both leaves and seeds
    # sold. Region 1-3. Good for kitchen gardens and intensive urban plots.
    # Frequently requested at Harare and Bulawayo markets.
    {
        "id": "CROP_060",
        "name": "Coriander",
        "local_names": {"shona": "Kolianda", "ndebele": "I-khorianda"},
        "type": "vegetable",
        "agro_regions": [1, 2, 3],
        "soil": {
            "ph_min": 6.0, "ph_max": 7.5, "ph_optimal": 6.5,
            "moisture_min": 55, "moisture_max": 80, "moisture_optimal": 68,
            "texture": ["loam", "sandy_loam"]
        },
        "climate": {
            "temp_min_c": 10, "temp_max_c": 28, "temp_optimal_c": 18,
            "rainfall_min_mm": 500, "rainfall_max_mm": 1200,
            "altitude_min_m": 700, "altitude_max_m": 2000
        },
        "planting": {
            "months_by_region": {"1": [1,2,3,4,5,6,7,8,9,10,11,12], "2": [3,4,5,6,7,8,9], "3": [4,5,6,7]},
            "days_to_maturity": {"short_season": 35, "medium_season": 60}
        },
        "varieties": [
            {"name": "Slow Bolt", "type": "open_pollinated", "maturity_days": 45, "yield_t_ha": 8.0, "input_level": "low"},
            {"name": "Long Standing", "type": "open_pollinated", "maturity_days": 60, "yield_t_ha": 6.0, "input_level": "low"}
        ],
        "irrigation": {"required": "supplemental", "water_mm_per_season": 400},
        "yield_t_ha": {"low_input": 4.0, "medium_input": 8.0, "high_input": 14.0},
        "fertiliser_schedule": [
            {"phase": "basal", "days_after_planting": 0, "product": "Compound C", "kg_per_ha": 200},
            {"phase": "top_dress", "days_after_planting": 21, "product": "Ammonium Nitrate (34.5%N)", "kg_per_ha": 75}
        ],
        "organic_alternatives": [
            {"phase": "basal", "product": "Compost", "kg_per_ha": 3000}
        ],
        "pests": ["PEST_006"],
        "diseases": [],
        "companion_crops": ["CROP_038", "CROP_037"],
        "rotation_partners": ["CROP_013", "CROP_039"],
        "market": {"price_usd_per_kg": 3.00, "price_updated": "2026-01", "demand": "high"}
    },

]
