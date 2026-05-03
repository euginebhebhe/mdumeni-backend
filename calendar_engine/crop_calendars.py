"""
MDUMENI — Crop Calendar Definitions
======================================
Complete 6-phase farming calendars for all 30 Zimbabwean crops.

Each calendar contains:
  crop_id, crop_name, total_days
  phases: list of 6 phase objects

Each phase contains:
  phase_number (1–6)
  phase_name
  start_day / end_day
  tasks: list of time-based instructions
  sensor_rules: list of condition-based alert rules

Task structure:
  {
    "day":        int,    # day number relative to planting (0 = planting day)
    "type":       str,    # "instruction" | "fertiliser" | "irrigation" |
                          # "pest_check" | "harvest" | "observation"
    "message":    str,    # plain English instruction for the farmer
    "applies_to": list,   # ["low", "medium", "high"] — omit = applies to all
  }

Sensor rule structure:
  {
    "field":     str,   # "soil_moisture_pct" | "soil_ph" | "soil_temp_c"
    "operator":  str,   # "<" | ">" | "<=" | ">="
    "threshold": float,
    "severity":  str,   # "critical" | "warning" | "info"
    "message":   str,   # plain English alert for the farmer
  }
"""

# ── HELPER: build a standard 6-phase calendar skeleton ──────────────────────

def _phase(number, name, start, end, tasks, sensor_rules=None):
    return {
        "phase_number": number,
        "phase_name":   name,
        "start_day":    start,
        "end_day":      end,
        "tasks":        tasks,
        "sensor_rules": sensor_rules or [],
    }


# ══════════════════════════════════════════════════════════════════════════════
# CROP_001 — MAIZE (120-day medium season)
# ══════════════════════════════════════════════════════════════════════════════
MAIZE_CALENDAR = {
    "crop_id":    "CROP_001",
    "crop_name":  "Maize",
    "total_days": 120,
    "phases": [

        _phase(1, "Land preparation", 0, 7, tasks=[
            {"day": 0, "type": "instruction",
             "message": "Clear all crop residues and weeds. Plough to 20–25 cm depth."},
            {"day": 2, "type": "instruction",
             "message": "Disc harrow to break clods. Aim for a fine, firm seedbed."},
            {"day": 5, "type": "fertiliser",
             "message": "Apply basal fertiliser: Compound D 200 kg/ha. Incorporate into top 10 cm.",
             "applies_to": ["medium", "high"]},
            {"day": 5, "type": "fertiliser",
             "message": "Low-input option: apply 5,000 kg/ha of compost or 3,000 kg/ha cattle manure.",
             "applies_to": ["low"]},
            {"day": 7, "type": "instruction",
             "message": "Mark out rows: 90 cm between rows, 30 cm between plants. Make planting pockets."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 30,
             "severity": "warning",
             "message": "Soil too dry for land preparation. Wait for rain or light pre-irrigation before ploughing."},
        ]),

        _phase(2, "Planting & germination", 8, 21, tasks=[
            {"day": 8,  "type": "instruction",
             "message": "Plant 2–3 seeds per station, 5 cm deep. Cover firmly. Rows: 90 cm, plants: 30 cm."},
            {"day": 10, "type": "observation",
             "message": "Check for germination. First shoots expected in 4–7 days after planting."},
            {"day": 14, "type": "instruction",
             "message": "Thin to 1 plant per station once seedlings reach 10 cm. Remove weakest plants."},
            {"day": 21, "type": "instruction",
             "message": "Check plant stand. Replant any gaps. Target 44,000 plants/ha (90×30 cm spacing)."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 40,
             "severity": "critical",
             "message": "Moisture too low for germination — seeds may fail. Water lightly (15–20 mm) if irrigation is available."},
            {"field": "soil_temp_c", "operator": ">", "threshold": 35,
             "severity": "warning",
             "message": "Soil temperature very high. Plant in early morning. Mulch after planting to cool soil."},
            {"field": "soil_temp_c", "operator": "<", "threshold": 15,
             "severity": "warning",
             "message": "Soil too cold for maize germination. Delay planting until temperature exceeds 16°C."},
        ]),

        _phase(3, "Vegetative growth", 22, 55, tasks=[
            {"day": 22, "type": "instruction",
             "message": "First weeding. Hoe or hand-weed between rows. Keep field weed-free until canopy closes."},
            {"day": 28, "type": "fertiliser",
             "message": "First top dress: Ammonium Nitrate 150 kg/ha. Place 5 cm from plant stem, cover with soil.",
             "applies_to": ["medium", "high"]},
            {"day": 28, "type": "fertiliser",
             "message": "Low-input top dress: apply 3,000 kg/ha cattle manure or 1,500 kg/ha compost around plants.",
             "applies_to": ["low"]},
            {"day": 35, "type": "pest_check",
             "message": "Scout for Fall Armyworm. Check whorl of each plant for frass and feeding damage. Treat if >30% plants are infested."},
            {"day": 42, "type": "instruction",
             "message": "Second weeding. Apply herbicide or hand-hoe. Canopy should close shortly — last weeding chance."},
            {"day": 45, "type": "fertiliser",
             "message": "Second top dress: Ammonium Nitrate 100 kg/ha. Plants should now be knee-height.",
             "applies_to": ["high"]},
            {"day": 50, "type": "pest_check",
             "message": "Scout for stalk borers at plant base. Check for entry holes and frass. Treat if >15% infestation."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 45,
             "severity": "critical",
             "message": "Water stress during vegetative growth. Irrigate 30 mm immediately if available. Stressed plants at this stage lose 20–30% yield potential."},
            {"field": "soil_ph", "operator": "<", "threshold": 5.2,
             "severity": "warning",
             "message": "pH too acidic for optimal maize growth. Apply 200 kg/ha agricultural lime and incorporate. Takes 4–6 weeks to act."},
            {"field": "soil_temp_c", "operator": ">", "threshold": 36,
             "severity": "warning",
             "message": "Heat stress. Water early morning and late afternoon. Mulch between rows to conserve moisture."},
        ]),

        _phase(4, "Tasselling & pollination", 56, 80, tasks=[
            {"day": 56, "type": "instruction",
             "message": "Tasselling beginning. This is the most critical water period. Do NOT allow wilting at any point."},
            {"day": 63, "type": "observation",
             "message": "Silk visible on cobs. Avoid any pesticide application during pollination to protect beneficial insects."},
            {"day": 70, "type": "pest_check",
             "message": "Check for ear worms on developing cobs. Check silk for fresh feeding damage. Treat only if severely infested."},
            {"day": 75, "type": "observation",
             "message": "Silks turning brown — pollination mostly complete. Cobs now filling with grain."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 55,
             "severity": "critical",
             "message": "CRITICAL: Drought stress during pollination directly causes barren cobs and zero yield. Irrigate 40 mm immediately. This is the most important watering of the season."},
            {"field": "soil_temp_c", "operator": ">", "threshold": 38,
             "severity": "critical",
             "message": "Extreme heat during pollination kills pollen. Irrigate immediately to cool canopy. Risk of complete yield loss."},
        ]),

        _phase(5, "Grain fill & maturation", 81, 110, tasks=[
            {"day": 81, "type": "instruction",
             "message": "Grain fill underway. Maintain soil moisture above 50%. Reduce nitrogen applications — only water needed now."},
            {"day": 90, "type": "pest_check",
             "message": "Check cobs for ear rot. Remove and destroy any cobs showing mould. Do not store infected grain."},
            {"day": 95, "type": "observation",
             "message": "Check grain filling. Run thumbnail across kernels — milk stage is normal. Hard stage means nearing maturity."},
            {"day": 100, "type": "instruction",
             "message": "Begin reducing irrigation to harden grain. Allow moisture to gradually drop toward 40%."},
            {"day": 108, "type": "observation",
             "message": "Husks should be drying and turning brown. Kernels should be denting at crown (dent stage)."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 40,
             "severity": "warning",
             "message": "Low moisture during grain fill. If cobs are still milky, apply 20 mm irrigation. If near maturity, this is acceptable."},
            {"field": "soil_temp_c", "operator": ">", "threshold": 35,
             "severity": "warning",
             "message": "High temperatures accelerating maturity. Monitor cobs closely — harvest date may arrive 5–7 days early."},
        ]),

        _phase(6, "Harvest & post-harvest", 111, 120, tasks=[
            {"day": 111, "type": "harvest",
             "message": "Harvest test: husk back a cob — kernels should be hard, dry, and fully dented. Husks dry and brown."},
            {"day": 113, "type": "harvest",
             "message": "Harvest cobs. Dehusk immediately. Dry in shade or solar dryer until grain moisture is below 13%."},
            {"day": 116, "type": "instruction",
             "message": "Shell grain when fully dry. Winnow to remove debris and light grains."},
            {"day": 118, "type": "instruction",
             "message": "Store grain in clean hermetic bags or metal silos with Actellic Super dust (1 g/kg). Label bags with crop, date, variety."},
            {"day": 120, "type": "instruction",
             "message": "Field is clear. Record yield weight. Rest field or plant a rotation legume (sugar beans, groundnuts). Plan next season inputs."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": ">", "threshold": 70,
             "severity": "warning",
             "message": "Field too wet for harvest operations. Wait 2–3 days for soil to firm up before using machinery."},
            {"field": "soil_temp_c", "operator": ">", "threshold": 34,
             "severity": "info",
             "message": "Hot conditions — harvest in early morning to reduce grain breakage and kernel heat damage."},
        ]),
    ]
}


# ══════════════════════════════════════════════════════════════════════════════
# CROP_002 — SORGHUM (120-day calendar)
# ══════════════════════════════════════════════════════════════════════════════
SORGHUM_CALENDAR = {
    "crop_id": "CROP_002", "crop_name": "Sorghum", "total_days": 120,
    "phases": [
        _phase(1, "Land preparation", 0, 7, tasks=[
            {"day": 0, "type": "instruction", "message": "Plough to 20 cm. Sorghum tolerates poor soils but deep cultivation improves root anchorage against lodging."},
            {"day": 5, "type": "fertiliser", "message": "Apply Compound D 150 kg/ha as basal. Incorporate well.", "applies_to": ["medium", "high"]},
            {"day": 7, "type": "instruction", "message": "Prepare fine seedbed. Sorghum seed is small — clods will prevent germination."},
        ]),
        _phase(2, "Planting & germination", 8, 21, tasks=[
            {"day": 8,  "type": "instruction", "message": "Plant at 2–3 cm depth. Row spacing 75 cm, plant spacing 25 cm. 3–4 seeds per station."},
            {"day": 12, "type": "observation", "message": "Check germination. Sorghum germinates in 5–10 days. Thin to 2 plants per station."},
            {"day": 21, "type": "instruction", "message": "Thin to 1 plant per station. Fill gaps. Target 50,000 plants/ha."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 30, "severity": "critical",
             "message": "Soil too dry for germination. Sorghum is drought-tolerant but needs moisture to sprout. Wait for rain."},
            {"field": "soil_temp_c", "operator": "<", "threshold": 18, "severity": "warning",
             "message": "Soil too cold for sorghum germination. Delay planting until soil temperature exceeds 20°C."},
        ]),
        _phase(3, "Vegetative growth", 22, 60, tasks=[
            {"day": 22, "type": "instruction", "message": "First weeding. Sorghum is slow to establish — weed competition is the biggest early risk."},
            {"day": 28, "type": "fertiliser", "message": "Top dress: Ammonium Nitrate 100 kg/ha. Place in furrow beside plants.", "applies_to": ["medium", "high"]},
            {"day": 40, "type": "pest_check", "message": "Scout for shootfly and stalk borer. Check growing points. Treat if >20% plants affected."},
            {"day": 50, "type": "instruction", "message": "Weed if needed. Canopy may not fully close — keep rows clear until heading."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 30, "severity": "warning",
             "message": "Sorghum tolerates dry conditions but growth is slowed below 30% moisture. Yield penalty if prolonged."},
        ]),
        _phase(4, "Heading & flowering", 61, 85, tasks=[
            {"day": 61, "type": "observation", "message": "Panicle (head) beginning to emerge from flag leaf. Maintain moisture for grain set."},
            {"day": 70, "type": "pest_check", "message": "Scout for head bugs and bird damage. Head bugs cause grain shrivelling. Net traps can deter birds."},
            {"day": 80, "type": "observation", "message": "Grain setting visible on head. Milky grain stage. Monitor moisture carefully."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 35, "severity": "critical",
             "message": "Drought at heading causes empty panicles and severely reduces grain count. Irrigate if available."},
        ]),
        _phase(5, "Grain fill & maturation", 86, 110, tasks=[
            {"day": 86, "type": "observation", "message": "Grain filling. Heads turning colour from green to the variety colour (white, red, brown)."},
            {"day": 100, "type": "pest_check", "message": "Bird damage peaks during dough stage. Monitor continuously. Scare devices or net cages help."},
            {"day": 108, "type": "observation", "message": "Check grain moisture. Squeeze kernels — hard and dry means near harvest."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": ">", "threshold": 80, "severity": "warning",
             "message": "Excessive moisture at maturity risks grain mould on panicles. Improve air circulation if possible."},
        ]),
        _phase(6, "Harvest & post-harvest", 111, 120, tasks=[
            {"day": 111, "type": "harvest", "message": "Harvest when heads are fully dry and grain is hard. Cut heads first, then stalks."},
            {"day": 114, "type": "instruction", "message": "Thresh on clean tarpaulin. Sun-dry threshed grain to below 12% moisture."},
            {"day": 118, "type": "instruction", "message": "Store in airtight bags with grain protectant. Sorghum stores well — up to 2 years if dry and clean."},
        ]),
    ]
}


# ══════════════════════════════════════════════════════════════════════════════
# CROP_006 — SOYBEANS (115-day calendar)
# ══════════════════════════════════════════════════════════════════════════════
SOYBEANS_CALENDAR = {
    "crop_id": "CROP_006", "crop_name": "Soybeans", "total_days": 115,
    "phases": [
        _phase(1, "Land preparation", 0, 7, tasks=[
            {"day": 0, "type": "instruction", "message": "Plough to 20 cm. Soybeans are sensitive to waterlogging — ensure good drainage."},
            {"day": 4, "type": "fertiliser", "message": "Apply Single Super Phosphate 150 kg/ha as basal. Do NOT apply nitrogen — soybeans fix their own.", "applies_to": ["medium", "high"]},
            {"day": 6, "type": "instruction", "message": "Prepare fine seedbed. Check pH — soybeans need pH 6.0–7.0 for nodulation."},
        ], sensor_rules=[
            {"field": "soil_ph", "operator": "<", "threshold": 5.8, "severity": "warning",
             "message": "Low pH will prevent Rhizobium nodulation — soybeans won't fix nitrogen. Apply lime before planting."},
        ]),
        _phase(2, "Planting & germination", 8, 21, tasks=[
            {"day": 8, "type": "instruction", "message": "CRITICAL: Treat seed with Rhizobium inoculant just before planting. Do not expose inoculant to direct sunlight."},
            {"day": 8, "type": "instruction", "message": "Plant at 3–4 cm depth. Row spacing 45 cm, plant spacing 5 cm (or 8–10 seeds/m row)."},
            {"day": 14, "type": "observation", "message": "Check nodule formation on roots of a few seedlings. Pink/red nodules = active nitrogen fixation. White = inactive — re-inoculate."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 45, "severity": "critical",
             "message": "Soil too dry for soybean germination and nodule formation. Irrigate lightly before planting."},
        ]),
        _phase(3, "Vegetative growth", 22, 55, tasks=[
            {"day": 22, "type": "instruction", "message": "First weeding. Soybeans compete poorly with weeds in early growth."},
            {"day": 35, "type": "pest_check", "message": "Scout for pod borers, aphids and red spider mite. Check leaf undersides. Treat at economic threshold."},
            {"day": 45, "type": "observation", "message": "Plant should be branching well. Note: yellowing leaves on lower canopy is normal. Yellowing throughout = nitrogen deficiency — check nodules."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 45, "severity": "warning",
             "message": "Moisture stress slowing vegetative growth. Irrigate if available — yield potential being lost."},
        ]),
        _phase(4, "Flowering & pod set", 56, 80, tasks=[
            {"day": 56, "type": "observation", "message": "Flowering begins. Small purple/white flowers on branches. Do NOT apply broad-spectrum insecticides — will kill pollinators."},
            {"day": 65, "type": "pest_check", "message": "Scout for pod borers intensively. This is peak infestation risk. Check developing pods for entry holes."},
            {"day": 75, "type": "observation", "message": "Pods clearly visible and filling. Count pods per plant — target 40+ pods for good yield."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 50, "severity": "critical",
             "message": "Drought at flowering causes flower and pod drop — directly reduces pod count. Irrigate 30 mm immediately."},
        ]),
        _phase(5, "Pod fill & maturation", 81, 105, tasks=[
            {"day": 81, "type": "observation", "message": "Seeds swelling in pods. Maintain moisture. Reduce nitrogen inputs."},
            {"day": 95, "type": "observation", "message": "Pods beginning to yellow and rattle. Leaves yellowing and dropping is normal at maturity."},
            {"day": 100, "type": "instruction", "message": "Stop irrigation now. Dry conditions needed for harvest. Combine harvesting requires pods to be dry."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": ">", "threshold": 75, "severity": "warning",
             "message": "Excessive moisture may delay pod drying and cause seed mould. Withhold irrigation at this stage."},
        ]),
        _phase(6, "Harvest & post-harvest", 106, 115, tasks=[
            {"day": 106, "type": "harvest", "message": "Harvest when 95% of pods are yellow-brown and leaves have dropped. Shake plants — rattle sound means ready."},
            {"day": 108, "type": "instruction", "message": "Thresh gently. Soybeans split easily. Sun-dry seed to below 12% moisture immediately after threshing."},
            {"day": 112, "type": "instruction", "message": "Bag in clean sacks. Store in cool, dry place. Soybeans deteriorate quickly in moisture — check monthly."},
        ]),
    ]
}


# ══════════════════════════════════════════════════════════════════════════════
# CROP_007 — GROUNDNUTS (115-day calendar)
# ══════════════════════════════════════════════════════════════════════════════
GROUNDNUTS_CALENDAR = {
    "crop_id": "CROP_007", "crop_name": "Groundnuts", "total_days": 115,
    "phases": [
        _phase(1, "Land preparation", 0, 7, tasks=[
            {"day": 0, "type": "instruction", "message": "Plough to 25 cm. Groundnuts peg into the soil — loose, friable soil is essential for pod formation."},
            {"day": 4, "type": "fertiliser", "message": "Apply Single Super Phosphate 150 kg/ha. Groundnuts need phosphorus and calcium, not nitrogen.", "applies_to": ["medium", "high"]},
            {"day": 7, "type": "instruction", "message": "Prepare fine, well-tilled seedbed. Remove large clods — they prevent pod penetration."},
        ], sensor_rules=[
            {"field": "soil_ph", "operator": "<", "threshold": 5.5, "severity": "warning",
             "message": "pH below optimum for groundnuts. Apply agricultural lime at 200 kg/ha to raise pH toward 6.0."},
        ]),
        _phase(2, "Planting & germination", 8, 21, tasks=[
            {"day": 8, "type": "instruction", "message": "Shell seed just before planting — never plant cracked or split kernels. Plant at 5 cm depth, 45×15 cm spacing."},
            {"day": 12, "type": "observation", "message": "Germination check. Groundnuts emerge in 5–10 days. Check for damping-off in wet conditions."},
            {"day": 21, "type": "instruction", "message": "Weed early — groundnuts are very sensitive to early weed competition."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 35, "severity": "critical",
             "message": "Soil too dry for germination. Groundnuts need consistent moisture to sprout. Irrigate lightly if available."},
        ]),
        _phase(3, "Vegetative growth", 22, 55, tasks=[
            {"day": 22, "type": "instruction", "message": "Weed carefully — avoid disturbing roots and pegs. Use hand-hoe, not heavy equipment."},
            {"day": 35, "type": "pest_check", "message": "Scout for leaf spots and rust. Check leaves for orange pustules (rust) or circular brown spots. Spray if early signs found."},
            {"day": 40, "type": "instruction", "message": "Earth up (mound soil) lightly around base of plants to encourage pegging into soil."},
            {"day": 45, "type": "observation", "message": "Yellow flowers appearing at base of plant. Pegs (gynophores) will grow from these into the soil."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 40, "severity": "warning",
             "message": "Moisture stress during vegetative growth reduces flower set. Irrigate if available."},
        ]),
        _phase(4, "Pegging & pod set", 56, 80, tasks=[
            {"day": 56, "type": "observation", "message": "Pegging underway. Yellow stalks growing from flower bases are penetrating soil. Do NOT disturb soil around plants."},
            {"day": 60, "type": "fertiliser", "message": "Side-dress calcium: 200 kg/ha agricultural lime or gypsum applied close to plant base. Critical for pod fill.", "applies_to": ["medium", "high"]},
            {"day": 70, "type": "pest_check", "message": "Check for aphids and thrips on young pods. Treat with a contact insecticide if severe."},
            {"day": 75, "type": "observation", "message": "Lift a plant carefully to check pod formation. Pods should be swelling underground."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 45, "severity": "critical",
             "message": "Drought during pegging causes failed pod set — this is the most critical water period. Irrigate 25 mm immediately."},
            {"field": "soil_moisture_pct", "operator": ">", "threshold": 80, "severity": "warning",
             "message": "Waterlogging risks peg rot and aflatoxin infection in developing pods. Improve drainage urgently."},
        ]),
        _phase(5, "Pod fill & maturation", 81, 105, tasks=[
            {"day": 81, "type": "observation", "message": "Pods filling underground. Leaves beginning to yellow naturally. This is normal."},
            {"day": 90, "type": "instruction", "message": "Reduce irrigation. Pods need to dry slightly for good shell quality."},
            {"day": 100, "type": "instruction", "message": "Harvest test: uproot a plant and check pods. Inner seed coat should show variety colour. Shell mesh pattern should be clearly visible."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": ">", "threshold": 75, "severity": "warning",
             "message": "Excessive moisture at maturity risks aflatoxin contamination. Stop irrigation and allow field to dry."},
        ]),
        _phase(6, "Harvest & post-harvest", 106, 115, tasks=[
            {"day": 106, "type": "harvest", "message": "Harvest when most leaves have yellowed. Uproot plants and leave in windrows for 3–5 days to field-dry."},
            {"day": 110, "type": "instruction", "message": "Thresh after field drying. Clean and sort pods. Discard any with mould, discolouration, or damage."},
            {"day": 113, "type": "instruction", "message": "CRITICAL: Dry pods to below 9% moisture before storage to prevent aflatoxin. Store in well-ventilated bags or cribs."},
        ]),
    ]
}


# ══════════════════════════════════════════════════════════════════════════════
# CROP_008 — SUGAR BEANS (75-day calendar)
# ══════════════════════════════════════════════════════════════════════════════
SUGAR_BEANS_CALENDAR = {
    "crop_id": "CROP_008", "crop_name": "Sugar beans", "total_days": 75,
    "phases": [
        _phase(1, "Land preparation", 0, 5, tasks=[
            {"day": 0, "type": "instruction", "message": "Plough to 15–20 cm. Beans follow well after maize on residual soil moisture."},
            {"day": 3, "type": "fertiliser", "message": "Apply Single Super Phosphate 120 kg/ha as basal. Do not apply nitrogen.", "applies_to": ["medium", "high"]},
        ]),
        _phase(2, "Planting & germination", 6, 18, tasks=[
            {"day": 6, "type": "instruction", "message": "Plant 3–4 cm deep. Row spacing 45 cm, plants 10 cm apart. Plant in rows for easy weeding."},
            {"day": 10, "type": "observation", "message": "Germination check — beans emerge in 4–7 days. Check for cutworm damage at base of stems."},
            {"day": 18, "type": "instruction", "message": "First weeding. Beans are short-season — weeds rob yield very quickly."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 40, "severity": "critical",
             "message": "Dry soil will prevent bean germination. Irrigate 15–20 mm before planting."},
        ]),
        _phase(3, "Vegetative growth", 19, 40, tasks=[
            {"day": 19, "type": "instruction", "message": "First weeding. Remove all weeds between rows and within row."},
            {"day": 28, "type": "pest_check", "message": "Scout for bean fly, aphids and spider mites. Check undersides of leaves. Treat promptly if found."},
            {"day": 35, "type": "instruction", "message": "Second weeding if needed. Beans flower early — stay out of field during flowering to avoid pod damage."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 40, "severity": "warning",
             "message": "Moisture stress reducing vegetative growth. Irrigate 20–25 mm if available."},
        ]),
        _phase(4, "Flowering & pod set", 41, 58, tasks=[
            {"day": 41, "type": "observation", "message": "Flowering begins. Small white or purple flowers. Avoid walking in field — disturbs flowers and pollinators."},
            {"day": 50, "type": "pest_check", "message": "Pod borer risk peaks. Check pod surfaces for small holes and frass. Spray pyrethroid if needed."},
            {"day": 55, "type": "observation", "message": "Pods forming rapidly. Count pods per plant — target 8–15 pods for good yield."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 45, "severity": "critical",
             "message": "Drought at flowering causes flower drop and pod abortion. Irrigate 25 mm immediately."},
        ]),
        _phase(5, "Pod fill & maturation", 59, 68, tasks=[
            {"day": 59, "type": "observation", "message": "Seeds swelling in pods. Stop nitrogen applications. Reduce irrigation."},
            {"day": 65, "type": "observation", "message": "Pods yellowing and drying on plant. Leaves beginning to drop — harvest approaching."},
        ]),
        _phase(6, "Harvest & post-harvest", 69, 75, tasks=[
            {"day": 69, "type": "harvest", "message": "Harvest when 90% of pods are dry and papery. Pull plants or cut at base. Field-dry for 2–3 days."},
            {"day": 72, "type": "instruction", "message": "Thresh on tarpaulin. Beat plants gently. Winnow to separate seed from debris."},
            {"day": 75, "type": "instruction", "message": "Dry seed to below 12% moisture. Store in airtight bags. Beans store for 6–12 months if dry."},
        ]),
    ]
}


# ══════════════════════════════════════════════════════════════════════════════
# CROP_013 — TOMATOES (85-day calendar)
# ══════════════════════════════════════════════════════════════════════════════
TOMATOES_CALENDAR = {
    "crop_id": "CROP_013", "crop_name": "Tomatoes", "total_days": 85,
    "phases": [
        _phase(1, "Land preparation", 0, 7, tasks=[
            {"day": 0, "type": "instruction", "message": "Deep plough to 30 cm. Tomatoes are heavy feeders — good soil preparation is essential."},
            {"day": 3, "type": "fertiliser", "message": "Incorporate Compound C 300 kg/ha + compost 5,000 kg/ha as pre-plant base.", "applies_to": ["medium", "high"]},
            {"day": 6, "type": "instruction", "message": "Mark beds. Single rows on flat ground or raised beds in high-rainfall areas to prevent root diseases."},
        ], sensor_rules=[
            {"field": "soil_ph", "operator": "<", "threshold": 5.5, "severity": "warning",
             "message": "Low pH causes blossom end rot (calcium deficiency) in tomatoes. Apply lime before planting."},
        ]),
        _phase(2, "Transplanting & establishment", 8, 21, tasks=[
            {"day": 8, "type": "instruction", "message": "Transplant seedlings at 6–8 true leaf stage. Space 60×45 cm. Water transplants immediately. Plant in late afternoon to reduce transplant shock."},
            {"day": 10, "type": "irrigation", "message": "Water every 2 days for the first 2 weeks to establish roots. Keep soil evenly moist, not saturated."},
            {"day": 14, "type": "observation", "message": "Check establishment. Wilted plants at midday are normal. Wilted plants in morning = roots failing — check for root disease."},
            {"day": 18, "type": "instruction", "message": "Install stakes or trellis wire for indeterminate varieties before plants get too large."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 55, "severity": "critical",
             "message": "Transplants must not dry out during establishment. Irrigate immediately — transplant failure risk."},
        ]),
        _phase(3, "Vegetative growth", 22, 42, tasks=[
            {"day": 22, "type": "fertiliser", "message": "First top dress: LAN 200 kg/ha. Side-dress and water in immediately.", "applies_to": ["medium", "high"]},
            {"day": 25, "type": "instruction", "message": "Begin suckering for indeterminate varieties: remove side shoots growing in leaf axils. Keep to 1 or 2 main stems."},
            {"day": 30, "type": "pest_check", "message": "Scout for whitefly, aphids, and leaf miners. Check undersides of leaves. Spray with systemic insecticide if high numbers found."},
            {"day": 35, "type": "pest_check", "message": "Scout for early blight (brown rings on lower leaves) and bacterial spot. Remove affected leaves. Spray copper fungicide if spreading."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 60, "severity": "warning",
             "message": "Soil drying — tomatoes are thirsty. Irrigate 25 mm. Moisture fluctuations cause blossom end rot."},
            {"field": "soil_temp_c", "operator": ">", "threshold": 32, "severity": "warning",
             "message": "High soil temperature. Mulch between rows with dry grass or straw to cool root zone."},
        ]),
        _phase(4, "Flowering & fruit set", 43, 62, tasks=[
            {"day": 43, "type": "observation", "message": "First flower clusters appearing. Tap flower clusters gently each morning to improve pollination in tunnels or calm conditions."},
            {"day": 48, "type": "fertiliser", "message": "Second top dress: Potassium Nitrate 150 kg/ha. Potassium is critical for fruit quality and shelf life.", "applies_to": ["medium", "high"]},
            {"day": 52, "type": "pest_check", "message": "Scout for tomato fruit borer (Helicoverpa). Check inside flowers for caterpillars. Treat immediately — causes massive crop loss."},
            {"day": 58, "type": "observation", "message": "First fruits setting. Remove misshapen or diseased fruitlets early. 4–6 fruits per truss is ideal."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 60, "severity": "critical",
             "message": "Drought stress at flowering causes blossom drop and blossom end rot. Irrigate immediately. Consistent moisture is essential."},
            {"field": "soil_moisture_pct", "operator": ">", "threshold": 85, "severity": "warning",
             "message": "Overwatering during fruit set causes root suffocation and fruit cracking. Reduce irrigation frequency."},
        ]),
        _phase(5, "Fruit development & maturation", 63, 78, tasks=[
            {"day": 63, "type": "observation", "message": "Fruits sizing up rapidly. Maintain consistent watering — fluctuations now cause fruit cracking."},
            {"day": 70, "type": "pest_check", "message": "Continue scouting for fruit borers and late blight. Late blight is devastating — brown lesions spreading rapidly. Spray Ridomil or Mancozeb immediately."},
            {"day": 75, "type": "observation", "message": "First fruits beginning to colour. Harvest at breaker stage (first blush of colour) for market transport, or vine-ripe for local sale."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": ">", "threshold": 80, "severity": "warning",
             "message": "Excess moisture at fruiting causes fruit cracking and disease. Reduce irrigation. Allow surface to dry slightly between waterings."},
        ]),
        _phase(6, "Harvest & post-harvest", 79, 85, tasks=[
            {"day": 79, "type": "harvest", "message": "Begin harvesting at breaker stage for transport. Pick every 2–3 days — do not allow fruits to over-ripen on plant."},
            {"day": 82, "type": "instruction", "message": "Handle fruit carefully — stack no more than 3 layers deep. Transport in ventilated crates. Do not expose to direct sun after harvest."},
            {"day": 85, "type": "instruction", "message": "After final harvest, remove all plant debris and burn or bury. Do not compost diseased material. Rest bed before replanting."},
        ]),
    ]
}


# ══════════════════════════════════════════════════════════════════════════════
# CROP_016 — RAPE / LEAF VEGETABLE (50-day calendar — fast cycle)
# ══════════════════════════════════════════════════════════════════════════════
RAPE_CALENDAR = {
    "crop_id": "CROP_016", "crop_name": "Rape / Leaf vegetable", "total_days": 50,
    "phases": [
        _phase(1, "Land preparation", 0, 4, tasks=[
            {"day": 0, "type": "instruction", "message": "Prepare fine, moist seedbed. Rake to remove large clods — rape seed is tiny."},
            {"day": 2, "type": "fertiliser", "message": "Apply Compound C 200 kg/ha or compost 5,000 kg/ha. Rake into top 5 cm.", "applies_to": ["medium", "high"]},
        ]),
        _phase(2, "Planting & germination", 5, 14, tasks=[
            {"day": 5, "type": "instruction", "message": "Broadcast seed at 1–2 kg/ha, or drill in rows 30 cm apart at 0.5 cm depth. Cover lightly with fine soil."},
            {"day": 8, "type": "observation", "message": "Germination check. Rape emerges in 3–5 days. Should have dense green cover."},
            {"day": 14, "type": "instruction", "message": "Thin if sown too densely. Target 10 cm between plants for large heads. Closer for cut-and-come-again."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 50, "severity": "critical",
             "message": "Rape needs moist conditions to germinate. Water immediately — tiny seed has no moisture reserves."},
        ]),
        _phase(3, "Rapid vegetative growth", 15, 35, tasks=[
            {"day": 15, "type": "fertiliser", "message": "Top dress: LAN 150 kg/ha for rapid leafy growth. This is the key yield-building application.", "applies_to": ["medium", "high"]},
            {"day": 20, "type": "pest_check", "message": "Scout for diamondback moth caterpillars and aphid colonies. Check undersides of leaves. Spray neem or pyrethrin if severe."},
            {"day": 28, "type": "instruction", "message": "Outer leaves can be harvested now (cut-and-come-again). Leave growing point intact for continued production."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 50, "severity": "warning",
             "message": "Rape needs consistent moisture for rapid leafy growth. Water every 2 days in dry conditions."},
        ]),
        _phase(4, "Maturation & harvest", 36, 50, tasks=[
            {"day": 36, "type": "harvest", "message": "Whole-head harvest: cut plant at base when head is tight and firm. Grade by size for market."},
            {"day": 40, "type": "instruction", "message": "For succession planting: replant immediately after harvest to maintain continuous supply."},
            {"day": 50, "type": "instruction", "message": "Clear field completely. Incorporate residues. Prepare for next crop immediately."},
        ], sensor_rules=[
            {"field": "soil_temp_c", "operator": ">", "threshold": 30, "severity": "warning",
             "message": "Hot conditions accelerate bolting (going to seed). Harvest heads immediately before they open."},
        ]),
    ]
}


# ══════════════════════════════════════════════════════════════════════════════
# CROP_019 — SWEET POTATO (100-day calendar)
# ══════════════════════════════════════════════════════════════════════════════
SWEET_POTATO_CALENDAR = {
    "crop_id": "CROP_019", "crop_name": "Sweet potato", "total_days": 100,
    "phases": [
        _phase(1, "Land preparation", 0, 7, tasks=[
            {"day": 0, "type": "instruction", "message": "Make ridges 30 cm high, 90 cm apart. Sweet potatoes need well-drained, loose ridges for tuber expansion."},
            {"day": 4, "type": "fertiliser", "message": "Apply Compound D 150 kg/ha in furrow before ridging. Sweet potato needs potassium for tuber quality.", "applies_to": ["medium", "high"]},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": ">", "threshold": 80, "severity": "warning",
             "message": "Waterlogged soil causes vine rot and tuber disease. Improve drainage before planting."},
        ]),
        _phase(2, "Planting & establishment", 8, 21, tasks=[
            {"day": 8, "type": "instruction", "message": "Plant vine cuttings (30 cm long, 3–4 nodes) on ridges. Bury 2–3 nodes, leave 1–2 above soil. Plant in late afternoon."},
            {"day": 14, "type": "irrigation", "message": "Water every 2–3 days for first 2 weeks until established. Wilting in first week is normal."},
            {"day": 21, "type": "observation", "message": "Check establishment. New leaves emerging means roots formed successfully. Replace any dead cuttings."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 50, "severity": "critical",
             "message": "Vine cuttings must not dry out during establishment. Irrigate immediately."},
        ]),
        _phase(3, "Vine growth", 22, 55, tasks=[
            {"day": 22, "type": "instruction", "message": "First weeding. Sweet potato vines spread — keep competition-free for first 5 weeks."},
            {"day": 35, "type": "instruction", "message": "Lift vines and reposition to prevent rooting at nodes (reduces tuber size at main root). Flip and replace every 2 weeks."},
            {"day": 45, "type": "pest_check", "message": "Scout for sweet potato weevil. Check vine bases for entry holes. Mound ridges higher to prevent weevil access to tubers."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 45, "severity": "warning",
             "message": "Moisture stress reducing vine growth. Irrigate 25 mm. Stress now reduces tuber initiation."},
        ]),
        _phase(4, "Tuber initiation & development", 56, 85, tasks=[
            {"day": 56, "type": "observation", "message": "Tubers initiating underground. Avoid soil disturbance near ridge base. Tubers are expanding — protect from weevil."},
            {"day": 65, "type": "fertiliser", "message": "Side-dress Potassium Chloride 100 kg/ha along ridges for tuber size and quality.", "applies_to": ["medium", "high"]},
            {"day": 75, "type": "instruction", "message": "Reduce irrigation slightly. Slight water stress now actually improves tuber sugar content."},
            {"day": 80, "type": "observation", "message": "Test harvest: dig into one ridge base. Tubers should be 5–10 cm diameter. Skin should be firm, not soft."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": ">", "threshold": 80, "severity": "warning",
             "message": "Excess moisture causes tuber cracking and rot. Allow ridges to dry between irrigations."},
        ]),
        _phase(5, "Maturation", 86, 95, tasks=[
            {"day": 86, "type": "observation", "message": "Vines beginning to yellow. Tubers mature. Test: slice a small tuber — flesh colour should be uniform."},
            {"day": 92, "type": "instruction", "message": "Withhold all irrigation for 7 days before harvest. Curing skin: dry conditions toughen skin for storage."},
        ]),
        _phase(6, "Harvest & post-harvest", 96, 100, tasks=[
            {"day": 96, "type": "harvest", "message": "Harvest on a dry day. Cut vines 30 cm from ridge, then dig carefully with fork from the side."},
            {"day": 98, "type": "instruction", "message": "Cure tubers in shade for 5–7 days (25°C) to heal skin wounds before storage. Do not wash before curing."},
            {"day": 100, "type": "instruction", "message": "Store in cool, dark, dry ventilated location. Do not stack more than 3 layers. Consume or sell within 4–6 weeks."},
        ]),
    ]
}


# ══════════════════════════════════════════════════════════════════════════════
# CROP_012 — SUNFLOWER (110-day calendar)
# ══════════════════════════════════════════════════════════════════════════════
SUNFLOWER_CALENDAR = {
    "crop_id": "CROP_012", "crop_name": "Sunflower", "total_days": 110,
    "phases": [
        _phase(1, "Land preparation", 0, 7, tasks=[
            {"day": 0, "type": "instruction", "message": "Plough to 20 cm. Sunflower has deep taproot — loose subsoil improves drought tolerance."},
            {"day": 5, "type": "fertiliser", "message": "Apply Compound D 150 kg/ha. Sunflower responds well to phosphorus.", "applies_to": ["medium", "high"]},
        ]),
        _phase(2, "Planting & germination", 8, 18, tasks=[
            {"day": 8, "type": "instruction", "message": "Plant 3–4 cm deep. Row spacing 90 cm, plant spacing 30 cm (37,000 plants/ha). One seed per station for hybrids."},
            {"day": 12, "type": "observation", "message": "Germination check. Sunflower emerges in 4–7 days. Check for cutworm damage at stem base."},
            {"day": 18, "type": "instruction", "message": "Thin to 1 plant per station. Fill gaps. Large seeds can be replanted in gaps."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 35, "severity": "warning",
             "message": "Dry soil delays sunflower germination. Irrigate before planting if possible."},
        ]),
        _phase(3, "Vegetative growth", 19, 55, tasks=[
            {"day": 19, "type": "instruction", "message": "First weeding. Sunflower is allelopathic — it suppresses some weeds naturally, but early competition is still harmful."},
            {"day": 28, "type": "fertiliser", "message": "Top dress Ammonium Nitrate 100 kg/ha when plants reach 30 cm tall.", "applies_to": ["medium", "high"]},
            {"day": 40, "type": "pest_check", "message": "Scout for sunflower stem weevil and caterpillars. Check main stem for bore holes."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 35, "severity": "warning",
             "message": "Sunflower is drought-tolerant but growth is reduced below 35% moisture. Irrigate if extended dry spell."},
        ]),
        _phase(4, "Flowering", 56, 80, tasks=[
            {"day": 56, "type": "observation", "message": "Flower head (capitulum) forming. Head begins facing east. Critical water period begins now."},
            {"day": 65, "type": "observation", "message": "Full flowering. Heads attract bees — do not spray insecticides during flowering. Bees are essential for pollination."},
            {"day": 75, "type": "observation", "message": "Petals falling. Back of head beginning to yellow. Grain filling starting."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 40, "severity": "critical",
             "message": "Drought at flowering reduces seed set dramatically. Irrigate 30 mm immediately if available."},
        ]),
        _phase(5, "Seed fill & maturation", 81, 100, tasks=[
            {"day": 81, "type": "observation", "message": "Seeds developing in head. Back of head yellowing rapidly. Birds are now a threat — check field daily."},
            {"day": 90, "type": "pest_check", "message": "Bird damage peaks during seed fill. Deploy scare devices. Harvest as soon as seeds are physiologically mature."},
            {"day": 98, "type": "observation", "message": "Head and seeds turning brown. Back of head is yellow-brown. Seeds should be hard and dark. Test seed moisture."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": ">", "threshold": 75, "severity": "warning",
             "message": "Wet conditions risk head rot and seed mould. Harvest as soon as physiologically mature."},
        ]),
        _phase(6, "Harvest & post-harvest", 101, 110, tasks=[
            {"day": 101, "type": "harvest", "message": "Harvest when 90% of seeds are hard and dark. Cut heads with 30 cm of stem. Dry heads in sun for 3–5 days."},
            {"day": 105, "type": "instruction", "message": "Thresh heads by beating against a frame over a tarpaulin. Winnow to clean seeds."},
            {"day": 108, "type": "instruction", "message": "Dry seeds to below 9% moisture. Store in cool, dry bags away from sunlight. Oil quality deteriorates above 10% moisture."},
        ]),
    ]
}


# ══════════════════════════════════════════════════════════════════════════════
# CROP_004 — PEARL MILLET (90-day calendar)
# ══════════════════════════════════════════════════════════════════════════════
PEARL_MILLET_CALENDAR = {
    "crop_id": "CROP_004", "crop_name": "Pearl millet", "total_days": 90,
    "phases": [
        _phase(1, "Land preparation", 0, 5, tasks=[
            {"day": 0, "type": "instruction", "message": "Minimum tillage is acceptable for millet. Plough if possible, or rip furrows. Millet is a pioneer crop for degraded soils."},
            {"day": 3, "type": "fertiliser", "message": "Apply Compound D 100 kg/ha if available. Millet responds even to small fertiliser amounts.", "applies_to": ["medium", "high"]},
        ]),
        _phase(2, "Planting & germination", 6, 15, tasks=[
            {"day": 6, "type": "instruction", "message": "Broadcast at 4–5 kg/ha or drill in rows 75 cm apart. Cover seed to 1–2 cm. Seed is very small."},
            {"day": 10, "type": "observation", "message": "Germination check. Millet emerges in 3–5 days. Very drought-tolerant at germination — can re-emerge after dry spell."},
            {"day": 15, "type": "instruction", "message": "Thin to 15–20 cm between plants or 2 plants per station if drilled."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 25, "severity": "warning",
             "message": "Even drought-tolerant millet needs some moisture to germinate. Wait for rain or irrigate lightly."},
        ]),
        _phase(3, "Vegetative growth", 16, 50, tasks=[
            {"day": 16, "type": "instruction", "message": "First weeding. Millet grows fast once established but early competition reduces tillering."},
            {"day": 25, "type": "fertiliser", "message": "Top dress Ammonium Nitrate 80 kg/ha when plants reach 30 cm.", "applies_to": ["medium", "high"]},
            {"day": 38, "type": "pest_check", "message": "Scout for stalk borer and grasshoppers. Millet is generally more pest-resistant than maize."},
        ]),
        _phase(4, "Heading & flowering", 51, 68, tasks=[
            {"day": 51, "type": "observation", "message": "Panicle (head) emerging from flag leaf. Cylinder-shaped head elongating rapidly."},
            {"day": 62, "type": "pest_check", "message": "Bird damage begins at flowering. Deploy scare devices immediately — quelea flocks are devastating."},
        ], sensor_rules=[
            {"field": "soil_moisture_pct", "operator": "<", "threshold": 28, "severity": "warning",
             "message": "Slight drought stress acceptable for millet at this stage. If prolonged, irrigate 15–20 mm to improve grain set."},
        ]),
        _phase(5, "Grain fill & maturation", 69, 82, tasks=[
            {"day": 69, "type": "observation", "message": "Grain filling in head. Seeds hard and round. Head stiffening."},
            {"day": 78, "type": "observation", "message": "Test grain hardness — press thumbnail. Hard = nearly ready. Check for any mould on heads."},
        ]),
        _phase(6, "Harvest & post-harvest", 83, 90, tasks=[
            {"day": 83, "type": "harvest", "message": "Harvest when most seeds are hard and head is dry. Cut heads first. Millet can be harvested slightly early to beat bird damage."},
            {"day": 86, "type": "instruction", "message": "Dry heads in sun for 5–7 days. Thresh by beating. Winnow to clean grain."},
            {"day": 90, "type": "instruction", "message": "Store in dry containers. Millet stores very well — up to 3 years in dry conditions."},
        ]),
    ]
}


# ══════════════════════════════════════════════════════════════════════════════
# GENERIC CALENDAR TEMPLATE — for remaining crops
# Covers: CROP_003 (Wheat), CROP_005 (Barley), CROP_009 (Cowpeas),
#         CROP_010 (Cotton), CROP_011 (Tobacco), CROP_014 (Onions),
#         CROP_015 (Cabbages), CROP_017 (Watermelon), CROP_018 (Butternut),
#         CROP_020 (Cassava), CROP_021 (Irish potato), CROP_022 (Papaya),
#         CROP_023 (Mango), CROP_024 (Avocado), CROP_025 (Bananas),
#         CROP_026 (Sugar cane), CROP_027 (Sesame), CROP_028 (Pumpkin),
#         CROP_029 (Garlic), CROP_030 (Chillies)
# ══════════════════════════════════════════════════════════════════════════════

def _generic_calendar(crop_id, crop_name, total_days,
                      basal_fert="Compound D", basal_rate=150,
                      td1_day=28, td1_fert="Ammonium Nitrate", td1_rate=100,
                      harvest_note=None):
    """
    Generates a complete 6-phase generic calendar for any crop.
    Used for crops that don't yet have a handcrafted calendar.
    Each phase is proportionally sized based on total_days.
    """
    p1_end  = max(5,  int(total_days * 0.06))
    p2_end  = max(15, int(total_days * 0.18))
    p3_end  = max(30, int(total_days * 0.45))
    p4_end  = max(45, int(total_days * 0.65))
    p5_end  = max(60, int(total_days * 0.88))
    p6_end  = total_days

    h_note = harvest_note or f"Harvest {crop_name} according to visual maturity signs. Refer to variety guide for specific indicators."

    return {
        "crop_id": crop_id, "crop_name": crop_name, "total_days": total_days,
        "phases": [
            _phase(1, "Land preparation", 0, p1_end, tasks=[
                {"day": 0, "type": "instruction",
                 "message": f"Plough field to 20–25 cm. Prepare fine, well-drained seedbed for {crop_name}."},
                {"day": max(2, p1_end - 2), "type": "fertiliser",
                 "message": f"Apply {basal_fert} {basal_rate} kg/ha as basal. Incorporate into topsoil.",
                 "applies_to": ["medium", "high"]},
            ], sensor_rules=[
                {"field": "soil_moisture_pct", "operator": "<", "threshold": 30,
                 "severity": "warning",
                 "message": f"Soil too dry for land preparation. Wait for rain before ploughing."},
            ]),
            _phase(2, "Planting & germination", p1_end + 1, p2_end, tasks=[
                {"day": p1_end + 1, "type": "instruction",
                 "message": f"Plant {crop_name} at recommended depth and spacing for your variety."},
                {"day": p1_end + 7, "type": "observation",
                 "message": "Check germination / establishment. Fill gaps where plants have failed."},
            ], sensor_rules=[
                {"field": "soil_moisture_pct", "operator": "<", "threshold": 40,
                 "severity": "critical",
                 "message": f"Insufficient moisture for {crop_name} germination. Irrigate before planting."},
            ]),
            _phase(3, "Vegetative growth", p2_end + 1, p3_end, tasks=[
                {"day": p2_end + 3, "type": "instruction",
                 "message": "First weeding. Keep field weed-free during active vegetative growth."},
                {"day": td1_day, "type": "fertiliser",
                 "message": f"Top dress: {td1_fert} {td1_rate} kg/ha. Apply close to plants and water in.",
                 "applies_to": ["medium", "high"]},
                {"day": p3_end - 5, "type": "pest_check",
                 "message": f"Scout field for common pests of {crop_name}. Check leaves and stems. Treat if at economic threshold."},
            ], sensor_rules=[
                {"field": "soil_moisture_pct", "operator": "<", "threshold": 40,
                 "severity": "warning",
                 "message": f"Moisture stress slowing {crop_name} growth. Irrigate 25 mm if available."},
                {"field": "soil_ph", "operator": "<", "threshold": 5.5,
                 "severity": "warning",
                 "message": f"Low pH may limit nutrient uptake for {crop_name}. Apply lime if possible."},
            ]),
            _phase(4, "Flowering / heading", p3_end + 1, p4_end, tasks=[
                {"day": p3_end + 2, "type": "observation",
                 "message": f"{crop_name} entering reproductive phase. Monitor closely for pests and disease."},
                {"day": p4_end - 5, "type": "pest_check",
                 "message": "Peak pest risk during reproductive stage. Increase scouting frequency."},
            ], sensor_rules=[
                {"field": "soil_moisture_pct", "operator": "<", "threshold": 45,
                 "severity": "critical",
                 "message": f"Drought during {crop_name} reproductive phase causes direct yield loss. Irrigate immediately."},
            ]),
            _phase(5, "Maturation", p4_end + 1, p5_end, tasks=[
                {"day": p4_end + 5, "type": "observation",
                 "message": f"Maturation underway. Reduce irrigation. Monitor for late-season pests."},
                {"day": p5_end - 5, "type": "observation",
                 "message": f"Conduct maturity checks. Refer to variety guide for harvest readiness indicators."},
            ], sensor_rules=[
                {"field": "soil_moisture_pct", "operator": ">", "threshold": 80,
                 "severity": "warning",
                 "message": "Excessive moisture near maturity risks disease and quality loss. Withhold irrigation."},
            ]),
            _phase(6, "Harvest & post-harvest", p5_end + 1, p6_end, tasks=[
                {"day": p5_end + 1, "type": "harvest", "message": h_note},
                {"day": p6_end - 3, "type": "instruction",
                 "message": f"After harvesting {crop_name}, clear field residues and plan rotation crop."},
            ]),
        ]
    }


# ── BUILD ALL REMAINING CALENDARS ────────────────────────────────────────────

CALENDARS = {
    "CROP_001": MAIZE_CALENDAR,
    "CROP_002": SORGHUM_CALENDAR,
    "CROP_003": _generic_calendar("CROP_003", "Wheat", 130,
                   basal_fert="Compound C", basal_rate=250,
                   td1_day=30, td1_fert="Ammonium Nitrate", td1_rate=200,
                   harvest_note="Harvest wheat when grain is hard and straw is golden. Combine or cut and thresh manually."),
    "CROP_004": PEARL_MILLET_CALENDAR,
    "CROP_005": _generic_calendar("CROP_005", "Barley", 120,
                   basal_fert="Compound C", basal_rate=200,
                   td1_day=28, td1_fert="Ammonium Nitrate", td1_rate=150,
                   harvest_note="Harvest barley when grain is hard and heads are golden-dry. Avoid rain at harvest."),
    "CROP_006": SOYBEANS_CALENDAR,
    "CROP_007": GROUNDNUTS_CALENDAR,
    "CROP_008": SUGAR_BEANS_CALENDAR,
    "CROP_009": _generic_calendar("CROP_009", "Cowpeas", 75,
                   basal_fert="Single Super Phosphate", basal_rate=100,
                   td1_day=25, td1_fert="Single Super Phosphate", td1_rate=50,
                   harvest_note="Harvest cowpeas when pods are dry and seeds rattle inside. Pick before pods shatter on plant."),
    "CROP_010": _generic_calendar("CROP_010", "Cotton", 160,
                   basal_fert="Compound L", basal_rate=200,
                   td1_day=30, td1_fert="Ammonium Nitrate", td1_rate=150,
                   harvest_note="Pick cotton bolls when fully open and fluffy. Harvest in dry conditions only. Moisture ruins fibre quality."),
    "CROP_011": _generic_calendar("CROP_011", "Tobacco", 150,
                   basal_fert="Compound S", basal_rate=300,
                   td1_day=21, td1_fert="Calcium Nitrate", td1_rate=200,
                   harvest_note="Harvest tobacco leaves from bottom upward as they ripen (turn light green-yellow). Cure within 24 hours."),
    "CROP_012": SUNFLOWER_CALENDAR,
    "CROP_013": TOMATOES_CALENDAR,
    "CROP_014": _generic_calendar("CROP_014", "Onions", 110,
                   basal_fert="Compound C", basal_rate=250,
                   td1_day=28, td1_fert="LAN", td1_rate=180,
                   harvest_note="Harvest onions when tops fall over naturally. Lift and field-cure in shade for 2 weeks before storage."),
    "CROP_015": _generic_calendar("CROP_015", "Cabbages", 88,
                   basal_fert="Compound C", basal_rate=300,
                   td1_day=21, td1_fert="LAN", td1_rate=200,
                   harvest_note="Harvest cabbages when head is firm and solid. Cut at base. Delay risks head splitting."),
    "CROP_016": RAPE_CALENDAR,
    "CROP_017": _generic_calendar("CROP_017", "Watermelon", 85,
                   basal_fert="Compound D", basal_rate=200,
                   td1_day=21, td1_fert="LAN", td1_rate=120,
                   harvest_note="Harvest when tendril nearest fruit dries up, skin turns dull, and tapping gives hollow sound."),
    "CROP_018": _generic_calendar("CROP_018", "Butternut squash", 95,
                   basal_fert="Compound D", basal_rate=180,
                   td1_day=28, td1_fert="LAN", td1_rate=100,
                   harvest_note="Harvest when skin is hard, tan-coloured, and stem begins to cork and dry. Cure in sun for 7 days."),
    "CROP_019": SWEET_POTATO_CALENDAR,
    "CROP_020": _generic_calendar("CROP_020", "Cassava", 300,
                   basal_fert="Compound D", basal_rate=120,
                   td1_day=60, td1_fert="Ammonium Nitrate", td1_rate=80,
                   harvest_note="Harvest cassava at 9–12 months. Dig from the base outward. Consume or process within 24 hours — fresh roots do not store."),
    "CROP_021": _generic_calendar("CROP_021", "Irish potato", 85,
                   basal_fert="Compound C", basal_rate=300,
                   td1_day=28, td1_fert="LAN", td1_rate=200,
                   harvest_note="Harvest potatoes when tops die back. Lift on dry day. Cure in cool shade for 10 days before storage."),
    "CROP_022": _generic_calendar("CROP_022", "Papaya", 210,
                   basal_fert="Compound D", basal_rate=200,
                   td1_day=60, td1_fert="LAN", td1_rate=150,
                   harvest_note="Harvest papaya when skin shows first yellow colour change. Ripen at room temperature. Handle carefully."),
    "CROP_023": _generic_calendar("CROP_023", "Mango", 1095,
                   basal_fert="Compound D", basal_rate=150,
                   td1_day=90, td1_fert="LAN", td1_rate=100,
                   harvest_note="Harvest mango when fruit size is full and first fruit drops naturally. Colour change varies by variety."),
    "CROP_024": _generic_calendar("CROP_024", "Avocado", 1460,
                   basal_fert="Compound C", basal_rate=200,
                   td1_day=90, td1_fert="Multifeed", td1_rate=5,
                   harvest_note="Harvest avocado by maturity index — test by removing one fruit and allowing to ripen at room temperature. Ready in 7–10 days if mature."),
    "CROP_025": _generic_calendar("CROP_025", "Bananas", 300,
                   basal_fert="Compound D", basal_rate=250,
                   td1_day=60, td1_fert="Potassium Chloride", td1_rate=300,
                   harvest_note="Harvest banana bunch when fingers are well-rounded and colour is full green. Ripen off plant."),
    "CROP_026": _generic_calendar("CROP_026", "Sugar cane", 400,
                   basal_fert="Compound L", basal_rate=400,
                   td1_day=90, td1_fert="Ammonium Nitrate", td1_rate=300,
                   harvest_note="Harvest sugar cane when Brix (sugar content) exceeds 18%. Cut at base. Deliver to mill within 24 hours."),
    "CROP_027": _generic_calendar("CROP_027", "Sesame", 90,
                   basal_fert="Compound D", basal_rate=100,
                   td1_day=25, td1_fert="Ammonium Nitrate", td1_rate=60,
                   harvest_note="Harvest sesame when lowest seed capsules begin to crack open. Cut plants and dry in sheaves — capsules shatter easily."),
    "CROP_028": _generic_calendar("CROP_028", "Pumpkin", 100,
                   basal_fert="Compound D", basal_rate=160,
                   td1_day=28, td1_fert="LAN", td1_rate=100,
                   harvest_note="Harvest pumpkin when skin is hard and stem is corky and dry. Cure in sun for 10 days to extend storage."),
    "CROP_029": _generic_calendar("CROP_029", "Garlic", 160,
                   basal_fert="Compound C", basal_rate=200,
                   td1_day=30, td1_fert="LAN", td1_rate=150,
                   harvest_note="Harvest garlic when 50% of leaves are dry and fallen. Lift carefully. Cure in shade with good airflow for 3–4 weeks."),
    "CROP_030": _generic_calendar("CROP_030", "Chillies / Peppers", 100,
                   basal_fert="Compound C", basal_rate=250,
                   td1_day=28, td1_fert="LAN", td1_rate=150,
                   harvest_note="Harvest chillies at green stage for fresh market, or fully red/ripe for drying. Pick every 3–5 days to encourage continued fruiting."),
}
