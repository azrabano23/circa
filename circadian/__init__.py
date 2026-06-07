"""circadian — a transparent, chronotype-aware scheduling core.

This package is the decision layer behind Circa: given a person's chronotype and
wake time, it models when they are biologically most alert across the day (a
two-process alertness model), then places cognitively demanding tasks into the
hours where that alertness is highest, subject to their fixed calendar.

It is deliberately dependency-light (standard library only) and deterministic, so
every recommendation is attributable to an explicit, inspectable model rather than
an opaque call to an LLM. The FastAPI application in `backend/` wraps this core;
the science lives here.
"""
from circadian.model import (
    Chronotype,
    alertness,
    alertness_curve,
    peak_hour,
)
from circadian.scheduler import (
    Task,
    Slot,
    ScheduledTask,
    score_slot,
    plan_day,
)

__version__ = "0.1.0"

__all__ = [
    "Chronotype",
    "alertness",
    "alertness_curve",
    "peak_hour",
    "Task",
    "Slot",
    "ScheduledTask",
    "score_slot",
    "plan_day",
]
