"""Circadian-aware day scheduler.

Given a set of tasks and the day's fixed events, place each task into the open
slot where the person's *modelled alertness* best matches the task's cognitive
demand. Hard tasks are pulled toward the alertness peak; light tasks are
indifferent and fill the gaps. The scheduler is greedy by priority and deadline,
deterministic, and never double-books.

The scoring is deliberately simple and inspectable: a task placed at hour `h`
scores `alertness(h) ** demand` — raising alertness to the task's cognitive
demand sharpens the preference for peak hours as demand rises, while a demand of
0 makes the task indifferent to timing. A late-night guard rail penalises slots
in the biological night regardless of the curve.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from circadian.model import Chronotype, alertness

_PRIORITY = {"urgent": 4, "high": 3, "medium": 2, "low": 1}


@dataclass(frozen=True)
class Task:
    """A unit of work to place. `cognitive_demand` in [0, 1]; `duration_min` minutes."""

    id: str
    title: str
    duration_min: int
    cognitive_demand: float = 0.5
    priority: str = "medium"
    due: datetime | None = None


@dataclass(frozen=True)
class Slot:
    """A contiguous free interval in the day."""

    start: datetime
    end: datetime

    @property
    def minutes(self) -> float:
        return (self.end - self.start).total_seconds() / 60.0


@dataclass(frozen=True)
class ScheduledTask:
    task: Task
    start: datetime
    end: datetime
    score: float
    reason: str


def _hour_of(dt: datetime) -> float:
    return dt.hour + dt.minute / 60.0


def score_slot(
    start: datetime,
    task: Task,
    chronotype: Chronotype,
    wake_hour: float = 7.0,
) -> float:
    """Score placing `task` at `start` in [0, 1]. Higher is better.

    alertness(h) ** demand: sharpens preference for peak hours as demand rises;
    demand 0 -> flat (timing-indifferent). Biological-night slots are floored low.
    """
    h = _hour_of(start)
    a = alertness(h, chronotype, wake_hour)
    if h >= 22.0 or h < 6.0:
        a *= 0.25  # late-night / pre-dawn guard rail
    demand = max(0.0, min(1.0, task.cognitive_demand))
    # a in [0,1]; a**demand is monotone in a and flattens as demand -> 0.
    return round(a ** demand, 4)


def _reason(start: datetime, task: Task, chronotype: Chronotype, wake_hour: float) -> str:
    h = _hour_of(start)
    a = alertness(h, chronotype, wake_hour)
    bits = []
    if a >= 0.75:
        bits.append("near your alertness peak")
    elif a >= 0.5:
        bits.append("solid alertness window")
    else:
        bits.append("off-peak, but it fits")
    if task.cognitive_demand >= 0.7:
        bits.append("demanding task placed at high alertness")
    if h >= 22.0 or h < 6.0:
        bits.append("biological night (penalised)")
    return "; ".join(bits)


def _split(slot: Slot, start: datetime, end: datetime) -> list[Slot]:
    """Remove [start, end) from `slot`, returning 0-2 remaining sub-slots."""
    out: list[Slot] = []
    if start > slot.start:
        out.append(Slot(slot.start, start))
    if end < slot.end:
        out.append(Slot(end, slot.end))
    return out


def plan_day(
    tasks: list[Task],
    free_slots: list[Slot],
    chronotype: Chronotype,
    wake_hour: float = 7.0,
) -> tuple[list[ScheduledTask], list[Task]]:
    """Greedily place tasks (priority, then deadline) into their best-scoring slot.

    Returns (scheduled, unscheduled). Deterministic; no task is double-booked.
    """
    ordered = sorted(
        tasks,
        key=lambda t: (
            -_PRIORITY.get(t.priority.lower(), 2),
            t.due or datetime.max,
        ),
    )
    slots = list(free_slots)
    scheduled: list[ScheduledTask] = []
    unscheduled: list[Task] = []
    candidate_step = timedelta(minutes=15)

    for task in ordered:
        best: tuple[float, int, datetime] | None = None  # (score, slot_idx, start)
        for i, slot in enumerate(slots):
            if slot.minutes < task.duration_min:
                continue
            # Search candidate start times across the slot (not just its front),
            # so a demanding task can be pulled toward the alertness peak rather
            # than greedily front-packed. Tie-break toward earlier starts.
            latest_start = slot.end - timedelta(minutes=task.duration_min)
            start = slot.start
            while start <= latest_start:
                score = score_slot(start, task, chronotype, wake_hour)
                if best is None or score > best[0]:
                    best = (score, i, start)
                start += candidate_step

        if best is None:
            unscheduled.append(task)
            continue

        score, idx, start = best
        end = start + timedelta(minutes=task.duration_min)
        scheduled.append(
            ScheduledTask(
                task=task,
                start=start,
                end=end,
                score=score,
                reason=_reason(start, task, chronotype, wake_hour),
            )
        )
        slot = slots.pop(idx)
        for sub in _split(slot, start, end):
            slots.append(sub)
        slots.sort(key=lambda s: s.start)

    return scheduled, unscheduled
