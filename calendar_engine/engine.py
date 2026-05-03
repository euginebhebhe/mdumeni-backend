"""
MDUMENI — Farming Calendar Engine
===================================
Phase-based state machine that generates a complete farming calendar
for any crop from planting day to harvest.

Given:
  - The crop (from crop_dataset)
  - The planting date
  - Live sensor readings (updated daily)
  - Farmer profile

The engine returns:
  - Current phase and progress
  - Today's exact tasks
  - Upcoming tasks for the next 7 days
  - Any sensor-triggered alerts (critical or warning)
  - Days to next phase, days to harvest

Architecture:
  Each crop has a CALENDAR with 6 phases:
    Phase 1 — Land Preparation
    Phase 2 — Planting & Germination
    Phase 3 — Vegetative Growth
    Phase 4 — Flowering / Pollination / Heading
    Phase 5 — Grain Fill / Fruit Development / Maturation
    Phase 6 — Harvest & Post-Harvest

  Each phase contains:
    - tasks:         time-based instructions (triggered by day number)
    - sensor_rules:  condition-based alerts (triggered by live readings)

  The engine evaluates:
    - Which phase is active today
    - Which tasks are due (exact day, or overdue within 3 days)
    - Which sensor rules are firing
    - What's coming up in the next 7 days

Usage:
    from calendar_engine.engine import get_daily_guidance, CalendarInput

    guidance = get_daily_guidance(CalendarInput(
        crop_id="CROP_001",
        days_since_planting=35,
        soil_ph=5.1,
        soil_moisture_pct=43,
        soil_temp_c=29,
        has_irrigation=False,
        budget_level="low",
        planting_month=11
    ))
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


# ── SENSOR RULE EVALUATOR ─────────────────────────────────────────────────────

def _evaluate_sensor_rules(rules: list, inp: CalendarInput) -> list:
    """
    Evaluate all sensor rules for the current phase.
    Returns a list of Alert objects for any triggered rules.
    """
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

    # Sort: critical first, then warning, then info
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    alerts.sort(key=lambda a: severity_order.get(a.severity, 3))
    return alerts


# ── TASK COLLECTOR ────────────────────────────────────────────────────────────

def _collect_tasks(phase: dict, day: int, budget_level: str) -> tuple:
    """
    Returns (tasks_today, tasks_upcoming) for the given day.
    - tasks_today:    tasks due exactly today, or overdue within 3 days
    - tasks_upcoming: tasks due in the next 7 days (exclusive of today)
    """
    today_tasks    = []
    upcoming_tasks = []

    for task in phase.get("tasks", []):
        task_day = task["day"]

        # Budget filter — skip tasks that don't apply to this budget level
        applies_to = task.get("applies_to", ["low", "medium", "high"])
        if budget_level not in applies_to:
            continue

        if task_day == day:
            today_tasks.append(Task(
                day=task_day, type=task["type"],
                message=task["message"], overdue=False
            ))
        elif day - 3 <= task_day < day:
            # Overdue — missed in the last 3 days
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
    """
    Generate complete daily guidance for a farmer on a specific crop.

    Args:
        inp: CalendarInput — validated sensor + farmer data

    Returns:
        DailyGuidance — full structured guidance for display in the app
    """
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

    # Season complete check
    if inp.days_since_planting > total_days:
        # Return a completed season summary
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

    # If between phases, use the last completed one
    if not current_phase_data:
        for phase in reversed(phases):
            if inp.days_since_planting >= phase["start_day"]:
                current_phase_data = phase
                break

    if not current_phase_data:
        current_phase_data = phases[0]

    # Find next phase
    current_idx = phases.index(current_phase_data)
    next_phase_data = phases[current_idx + 1] if current_idx + 1 < len(phases) else None

    # Tasks and alerts
    tasks_today, tasks_upcoming = _collect_tasks(
        current_phase_data, inp.days_since_planting, inp.budget_level
    )
    alerts = _evaluate_sensor_rules(
        current_phase_data.get("sensor_rules", []), inp
    )

    # Also check upcoming phase rules if within 5 days of transition
    if next_phase_data:
        days_to_next = next_phase_data["start_day"] - inp.days_since_planting
        if days_to_next <= 5:
            next_alerts = _evaluate_sensor_rules(
                next_phase_data.get("sensor_rules", []), inp
            )
            # Mark as early warnings
            for a in next_alerts:
                a.message = f"[UPCOMING PHASE] {a.message}"
                if a.severity == "critical":
                    a.severity = "warning"
            alerts.extend(next_alerts)
    else:
        days_to_next = None

    # Harvest ready check (last phase, last 20% of days)
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
