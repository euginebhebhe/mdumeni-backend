"""
MDUMENI — Farming Calendar Engine
===================================
Phase-based state machine that generates a complete farming calendar
for any crop from planting day to harvest.

Given:
  - The crop (from crop_dataset)
  - The planting date
  - Live sensor readings (updated daily)
  - Farmer profile (including agro_region for Pfumvudza awareness)

The engine returns:
  - Current phase and progress
  - Today's exact tasks (region-aware for land preparation)
  - Upcoming tasks for the next 7 days
  - Any sensor-triggered alerts (critical or warning)
  - Days to next phase, days to harvest

Architecture:
  Each crop has a CALENDAR with 6 phases:
    Phase 1 — Land Preparation  (REGION-AWARE: Pfumvudza for Regions 4 & 5)
    Phase 2 — Planting & Germination
    Phase 3 — Vegetative Growth
    Phase 4 — Flowering / Pollination / Heading
    Phase 5 — Grain Fill / Fruit Development / Maturation
    Phase 6 — Harvest & Post-Harvest
"""

from dataclasses import dataclass, field
from typing import Optional
from calendar_engine.crop_calendars import CALENDARS


# ── DATA CLASSES ──────────────────────────────────────────────────────────────

@dataclass
class CalendarInput:
    """All data required to generate a daily guidance update."""
    crop_id:            str            # e.g. "CROP_001"
    days_since_planting:int            # 0 = planting day
    soil_ph:            float          # live sensor reading
    soil_moisture_pct:  float          # live sensor reading
    soil_temp_c:        float          # live sensor reading
    has_irrigation:     bool
    budget_level:       str            # "low" | "medium" | "high"
    planting_month:     int            # 1–12

    # Optional
    farm_size_ha:       Optional[float] = None
    agro_region:        Optional[int]   = None  # 1–5; drives Pfumvudza vs conventional

    def validate(self):
        if self.days_since_planting < 0:
            raise ValueError("days_since_planting cannot be negative")
        if not (3.0 <= self.soil_ph <= 9.0):
            raise ValueError(f"soil_ph {self.soil_ph} out of range")
        if not (0 <= self.soil_moisture_pct <= 100):
            raise ValueError(f"soil_moisture_pct out of range")
        if self.budget_level not in ("low", "medium", "high"):
            raise ValueError(f"budget_level must be low / medium / high")
        if not (1 <= self.planting_month <= 12):
            raise ValueError(f"planting_month must be 1–12")


@dataclass
class Alert:
    severity:   str    # "critical" | "warning" | "info"
    message:    str
    field:      str    # which sensor triggered it
    value:      float  # actual sensor reading
    threshold:  float  # threshold that was crossed

    def to_dict(self):
        return {
            "severity":  self.severity,
            "message":   self.message,
            "field":     self.field,
            "value":     self.value,
            "threshold": self.threshold,
        }


@dataclass
class Task:
    day:      int
    type:     str     # "instruction" | "fertiliser" | "irrigation" | "pest_check" | "harvest"
    message:  str
    overdue:  bool = False

    def to_dict(self):
        return {
            "day":     self.day,
            "type":    self.type,
            "message": self.message,
            "overdue": self.overdue,
        }


@dataclass
class PhaseInfo:
    phase_number: int
    phase_name:   str
    start_day:    int
    end_day:      int


@dataclass
class DailyGuidance:
    """Complete daily output for the farmer."""
    crop_id:             str
    crop_name:           str
    day:                 int
    total_days:          int
    progress_pct:        int

    current_phase:       PhaseInfo
    next_phase:          Optional[PhaseInfo]
    days_to_next_phase:  Optional[int]
    days_to_harvest:     int

    tasks_today:         list   # Task objects due today or overdue
    tasks_upcoming:      list   # Task objects due in next 7 days
    alerts:              list   # Alert objects from sensor rules

    season_complete:     bool
    harvest_ready:       bool

    def to_dict(self):
        return {
            "crop_id":            self.crop_id,
            "crop_name":          self.crop_name,
            "day":                self.day,
            "total_days":         self.total_days,
            "progress_pct":       self.progress_pct,
            "current_phase": {
                "number": self.current_phase.phase_number,
                "name":   self.current_phase.phase_name,
                "start":  self.current_phase.start_day,
                "end":    self.current_phase.end_day,
            },
            "next_phase":          {
                "number": self.next_phase.phase_number,
                "name":   self.next_phase.phase_name,
            } if self.next_phase else None,
            "days_to_next_phase":  self.days_to_next_phase,
            "days_to_harvest":     self.days_to_harvest,
            "tasks_today":         [t.to_dict() for t in self.tasks_today],
            "tasks_upcoming":      [t.to_dict() for t in self.tasks_upcoming],
            "alerts":              [a.to_dict() for a in self.alerts],
            "season_complete":     self.season_complete,
            "harvest_ready":       self.harvest_ready,
        }


# ── PFUMVUDZA / CONSERVATION AGRICULTURE ─────────────────────────────────────
#
# Zimbabwe's agro-ecological regions require fundamentally different land
# preparation methods:
#
# Regions 1, 2, 3 — adequate to high rainfall (>650 mm):
#   Conventional ploughing to 20-25 cm, discing, row marking. Sufficient
#   rainfall means soil moisture retention is less critical.
#
# Regions 4, 5 — semi-arid to arid (<650 mm):
#   Pfumvudza (Conservation Agriculture Basin System).
#   DO NOT plough — ploughing destroys soil structure and increases
#   evaporation in low-rainfall areas.
#   Instead: dig individual basins (15cm × 15cm × 15cm) on a 90cm × 60cm
#   grid. Basins concentrate both water and nutrients exactly at the root
#   zone, reducing evaporation by up to 30% vs conventional tillage.
#   Results from CIMMYT/AGRITEX trials: 60-120% yield increase vs
#   conventional tillage in Region 4-5 conditions.
#
# Reference: AGRITEX Pfumvudza Programme; CIMMYT Conservation Agriculture

# Crops where Pfumvudza applies — cereals and legumes planted in rows.
# Perennials, vegetables, and tree crops use their own land prep regardless.
_PFUMVUDZA_ELIGIBLE = {
    "CROP_001",  # Maize
    "CROP_002",  # Sorghum
    "CROP_004",  # Pearl millet
    "CROP_006",  # Soybeans
    "CROP_007",  # Groundnuts
    "CROP_008",  # Sugar beans
    "CROP_009",  # Cowpeas
    "CROP_031",  # Finger millet (Zviyo)
    "CROP_032",  # Bambara groundnut (Nyimo)
    "CROP_033",  # Pigeon peas
    "CROP_034",  # Lablab
    "CROP_054",  # Castor bean
    "CROP_055",  # Safflower
}

# Pfumvudza task schedule — replaces conventional land prep for Region 4 & 5
_PFUMVUDZA_TASKS = [
    {
        "day": 0,
        "type": "instruction",
        "applies_to": ["low", "medium", "high"],
        "message": (
            "PFUMVUDZA — DO NOT PLOUGH. Your agro-ecological region (4 or 5) "
            "receives too little rainfall for conventional tillage to work. Ploughing "
            "destroys soil structure and increases evaporation. "
            "Today: mark out rows every 90 cm across the entire field. Use a rope "
            "or stick to keep rows straight. This is the baseline for your basin grid."
        ),
    },
    {
        "day": 1,
        "type": "instruction",
        "applies_to": ["low", "medium", "high"],
        "message": (
            "Dig basins along each row. Spacing: one basin every 60 cm within each row. "
            "Each basin: 15 cm long × 15 cm wide × 15 cm deep. "
            "Heap the dug soil on the DOWNHILL side of the basin — this acts as a berm "
            "and traps additional runoff. "
            "For 1 hectare you need approximately 18,500 basins. Work systematically. "
            "Basins must be level — not tilted, or water will run out."
        ),
    },
    {
        "day": 2,
        "type": "instruction",
        "applies_to": ["low", "medium", "high"],
        "message": (
            "Continue digging basins. Check yesterday's basins: press your hand flat "
            "into each basin floor — it should be level and firm, not loose. "
            "Do not disturb the soil BETWEEN basins. Leave it firm and undisturbed — "
            "this reduces evaporation significantly. If you have last season's crop "
            "residue, spread it between basins as mulch."
        ),
    },
    {
        "day": 3,
        "type": "fertiliser",
        "applies_to": ["low", "medium", "high"],
        "message": (
            "Add basal inputs to each completed basin. "
            "LOW INPUT: 1 small tin (250 ml) of well-rotted manure or compost per basin — "
            "mix into the bottom 5 cm. "
            "MEDIUM/HIGH INPUT: add 1 bottle-cap (approx. 15 g) of Compound D per basin "
            "IN ADDITION to manure. "
            "Do not use full ha-rate fertiliser in basins — concentrating nutrients at "
            "root level is more efficient than broadcasting."
        ),
    },
    {
        "day": 5,
        "type": "instruction",
        "applies_to": ["low", "medium", "high"],
        "message": (
            "Basins are now ready. Final check: walk the field and confirm all basins "
            "are level, correctly spaced (90 cm × 60 cm), and have been amended with "
            "manure or fertiliser. "
            "Do NOT plant yet. Wait for the first meaningful rain of 20 mm or more. "
            "Planting into dry basins wastes seed — Pfumvudza works by combining "
            "the basin water-harvesting effect with timely planting."
        ),
    },
    {
        "day": 7,
        "type": "instruction",
        "applies_to": ["low", "medium", "high"],
        "message": (
            "PLANTING — when first rains of 20 mm or more arrive, plant immediately. "
            "Place 2–3 seeds per basin at 3–5 cm depth. Cover and firm gently. "
            "After germination (7–10 days), thin to 2 plants per basin — this is the "
            "Pfumvudza standard. Do not thin to 1 plant; 2 per basin consistently "
            "outperforms 1 per basin in low-rainfall trials across Zimbabwe. "
            "First top-dressing: apply when plants are knee-high (approx. 4–6 weeks)."
        ),
    },
]


def _should_use_pfumvudza(crop_id: str, agro_region: Optional[int]) -> bool:
    """True if this farmer's region and crop require Pfumvudza basins."""
    return agro_region in (4, 5) and crop_id in _PFUMVUDZA_ELIGIBLE


def _pfumvudza_tasks(day: int, budget_level: str) -> tuple:
    """
    Return (tasks_today, tasks_upcoming) from the Pfumvudza schedule.
    Mirrors the logic of _collect_tasks() so behaviour is identical.
    """
    today_tasks    = []
    upcoming_tasks = []

    for t in _PFUMVUDZA_TASKS:
        if budget_level not in t.get("applies_to", ["low", "medium", "high"]):
            continue
        task_day = t["day"]
        if task_day == day:
            today_tasks.append(Task(day=task_day, type=t["type"],
                                    message=t["message"], overdue=False))
        elif day - 3 <= task_day < day:
            today_tasks.append(Task(
                day=task_day, type=t["type"],
                message=f"[OVERDUE from Day {task_day}] {t['message']}",
                overdue=True,
            ))
        elif day < task_day <= day + 7:
            upcoming_tasks.append(Task(day=task_day, type=t["type"],
                                       message=t["message"], overdue=False))

    return today_tasks, upcoming_tasks


# ── SENSOR RULE EVALUATOR ─────────────────────────────────────────────────────

def _evaluate_sensor_rules(rules: list, inp: CalendarInput) -> list:
    sensor_map = {
        "soil_moisture_pct": inp.soil_moisture_pct,
        "soil_ph":           inp.soil_ph,
        "soil_temp_c":       inp.soil_temp_c,
    }
    alerts = []
    for rule in rules:
        field   = rule["field"]
        op      = rule["operator"]
        thresh  = rule["threshold"]
        value   = sensor_map.get(field)
        if value is None:
            continue
        triggered = (
            (op == "<"  and value < thresh) or
            (op == ">"  and value > thresh) or
            (op == "<=" and value <= thresh) or
            (op == ">=" and value >= thresh)
        )
        if triggered:
            alerts.append(Alert(
                severity  = rule["severity"],
                message   = rule["message"],
                field     = field,
                value     = round(value, 1),
                threshold = thresh,
            ))
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    alerts.sort(key=lambda a: severity_order.get(a.severity, 3))
    return alerts


# ── TASK COLLECTOR ────────────────────────────────────────────────────────────

def _collect_tasks(phase: dict, day: int, budget_level: str) -> tuple:
    today_tasks    = []
    upcoming_tasks = []
    for task in phase.get("tasks", []):
        task_day   = task["day"]
        applies_to = task.get("applies_to", ["low", "medium", "high"])
        if budget_level not in applies_to:
            continue
        if task_day == day:
            today_tasks.append(Task(
                day=task_day, type=task["type"],
                message=task["message"], overdue=False
            ))
        elif day - 3 <= task_day < day:
            today_tasks.append(Task(
                day=task_day, type=task["type"],
                message=f"[OVERDUE from Day {task_day}] {task['message']}",
                overdue=True
            ))
        elif day < task_day <= day + 7:
            upcoming_tasks.append(Task(
                day=task_day, type=task["type"],
                message=task["message"], overdue=False
            ))
    return today_tasks, upcoming_tasks


# ── MAIN ENGINE FUNCTION ──────────────────────────────────────────────────────

def get_daily_guidance(inp: CalendarInput) -> DailyGuidance:
    inp.validate()

    calendar = CALENDARS.get(inp.crop_id)
    if not calendar:
        raise ValueError(
            f"No calendar found for crop '{inp.crop_id}'. "
            f"Available: {list(CALENDARS.keys())}"
        )

    total_days = calendar["total_days"]
    crop_name  = calendar["crop_name"]
    phases     = calendar["phases"]

    if inp.days_since_planting > total_days:
        last_phase = phases[-1]
        return DailyGuidance(
            crop_id=inp.crop_id, crop_name=crop_name,
            day=inp.days_since_planting, total_days=total_days,
            progress_pct=100,
            current_phase=PhaseInfo(
                last_phase["phase_number"], last_phase["phase_name"],
                last_phase["start_day"], last_phase["end_day"]
            ),
            next_phase=None, days_to_next_phase=None,
            days_to_harvest=0,
            tasks_today=[], tasks_upcoming=[], alerts=[],
            season_complete=True, harvest_ready=False,
        )

    # Find current phase
    current_phase_data = None
    for phase in phases:
        if phase["start_day"] <= inp.days_since_planting <= phase["end_day"]:
            current_phase_data = phase
            break
    if not current_phase_data:
        for phase in reversed(phases):
            if inp.days_since_planting >= phase["start_day"]:
                current_phase_data = phase
                break
    if not current_phase_data:
        current_phase_data = phases[0]

    current_idx     = phases.index(current_phase_data)
    next_phase_data = phases[current_idx + 1] if current_idx + 1 < len(phases) else None

    # ── Tasks — Pfumvudza override for Region 4 & 5, Phase 1 only ────────────
    if (
        current_phase_data.get("phase_number") == 1
        and _should_use_pfumvudza(inp.crop_id, inp.agro_region)
    ):
        tasks_today, tasks_upcoming = _pfumvudza_tasks(
            inp.days_since_planting, inp.budget_level
        )
    else:
        tasks_today, tasks_upcoming = _collect_tasks(
            current_phase_data, inp.days_since_planting, inp.budget_level
        )

    alerts = _evaluate_sensor_rules(
        current_phase_data.get("sensor_rules", []), inp
    )

    if next_phase_data:
        days_to_next = next_phase_data["start_day"] - inp.days_since_planting
        if days_to_next <= 5:
            next_alerts = _evaluate_sensor_rules(
                next_phase_data.get("sensor_rules", []), inp
            )
            for a in next_alerts:
                a.message = f"[UPCOMING PHASE] {a.message}"
                if a.severity == "critical":
                    a.severity = "warning"
            alerts.extend(next_alerts)
    else:
        days_to_next = None

    harvest_ready = (
        current_idx == len(phases) - 1 and
        inp.days_since_planting >= current_phase_data["start_day"] + (
            (current_phase_data["end_day"] - current_phase_data["start_day"]) * 0.6
        )
    )

    return DailyGuidance(
        crop_id=inp.crop_id,
        crop_name=crop_name,
        day=inp.days_since_planting,
        total_days=total_days,
        progress_pct=round((inp.days_since_planting / total_days) * 100),
        current_phase=PhaseInfo(
            current_phase_data["phase_number"],
            current_phase_data["phase_name"],
            current_phase_data["start_day"],
            current_phase_data["end_day"],
        ),
        next_phase=PhaseInfo(
            next_phase_data["phase_number"],
            next_phase_data["phase_name"],
            next_phase_data["start_day"],
            next_phase_data["end_day"],
        ) if next_phase_data else None,
        days_to_next_phase=days_to_next,
        days_to_harvest=max(0, total_days - inp.days_since_planting),
        tasks_today=tasks_today,
        tasks_upcoming=tasks_upcoming,
        alerts=alerts,
        season_complete=False,
        harvest_ready=harvest_ready,
    )