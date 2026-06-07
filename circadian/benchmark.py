"""Does circadian-aware placement actually help? A controlled comparison.

We define a task's realised *cognitive throughput* as its cognitive demand times
the modelled alertness at the time it was scheduled: doing hard work while alert
is worth more than doing it while foggy. We then compare two schedulers on the
same tasks and the same free day:

  - FIFO: place tasks front-to-back in priority order, ignoring the clock.
  - circadian: place each task in its best-scoring slot (this package).

Both schedule the identical task set into the identical slots; the only
difference is *when*. The throughput gap is therefore attributable purely to
circadian-aware placement. This is a model-internal result — it shows the
scheduler does what it claims under its own alertness model, not that it
improves real human output (that needs a user study; see the README).
"""
from __future__ import annotations

from datetime import datetime, timedelta

from circadian.model import Chronotype, alertness, peak_hour
from circadian.scheduler import ScheduledTask, Slot, Task, plan_day


def _hour_of(dt: datetime) -> float:
    return dt.hour + dt.minute / 60.0


def throughput(scheduled: list[ScheduledTask], chronotype: Chronotype, wake_hour: float) -> float:
    """Sum of cognitive_demand * alertness(placed_time) over scheduled tasks."""
    total = 0.0
    for s in scheduled:
        a = alertness(_hour_of(s.start), chronotype, wake_hour)
        total += s.task.cognitive_demand * a
    return round(total, 4)


def _fifo(tasks: list[Task], slots: list[Slot]) -> list[ScheduledTask]:
    """Front-to-back placement in priority order, blind to alertness."""
    from circadian.scheduler import _PRIORITY  # local import: internal helper

    ordered = sorted(
        tasks,
        key=lambda t: (-_PRIORITY.get(t.priority.lower(), 2), t.due or datetime.max),
    )
    slots = sorted(slots, key=lambda s: s.start)
    out: list[ScheduledTask] = []
    for task in ordered:
        for i, slot in enumerate(slots):
            if slot.minutes >= task.duration_min:
                start = slot.start
                end = start + timedelta(minutes=task.duration_min)
                out.append(ScheduledTask(task, start, end, 0.0, "fifo"))
                rest = []
                if end < slot.end:
                    rest.append(Slot(end, slot.end))
                slots = slots[:i] + rest + slots[i + 1 :]
                slots.sort(key=lambda s: s.start)
                break
    return out


def _free_day(wake_hour: float = 7.0, end_hour: float = 22.0, day: datetime | None = None) -> list[Slot]:
    base = (day or datetime(2026, 1, 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    start = base + timedelta(hours=wake_hour)
    end = base + timedelta(hours=end_hour)
    return [Slot(start, end)]


def _sample_tasks() -> list[Task]:
    """A realistic mixed workload: a few hard tasks, several light ones."""
    return [
        Task("t1", "Write the proof / hard analysis", 90, cognitive_demand=0.95, priority="high"),
        Task("t2", "Debug the tricky failure", 60, cognitive_demand=0.9, priority="high"),
        Task("t3", "Design review", 60, cognitive_demand=0.8, priority="medium"),
        Task("t4", "Answer emails", 30, cognitive_demand=0.2, priority="medium"),
        Task("t5", "File expenses", 30, cognitive_demand=0.1, priority="low"),
        Task("t6", "Read a paper", 45, cognitive_demand=0.6, priority="medium"),
        Task("t7", "Tidy the backlog", 30, cognitive_demand=0.2, priority="low"),
    ]


def run(chronotype: Chronotype = Chronotype.INTERMEDIATE, wake_hour: float = 7.0) -> dict:
    """Run the FIFO-vs-circadian comparison and return a summary dict."""
    tasks = _sample_tasks()
    slots = _free_day(wake_hour)

    fifo = _fifo(tasks, slots)
    smart, _ = plan_day(tasks, slots, chronotype, wake_hour)

    t_fifo = throughput(fifo, chronotype, wake_hour)
    t_smart = throughput(smart, chronotype, wake_hour)
    gain = round(100.0 * (t_smart - t_fifo) / t_fifo, 1) if t_fifo else float("inf")

    return {
        "chronotype": chronotype.value,
        "wake_hour": wake_hour,
        "alertness_peak_hour": peak_hour(chronotype, wake_hour),
        "throughput_fifo": t_fifo,
        "throughput_circadian": t_smart,
        "improvement_pct": gain,
        "hard_task_hours": {
            "fifo": [round(_hour_of(s.start), 1) for s in fifo if s.task.cognitive_demand >= 0.8],
            "circadian": [round(_hour_of(s.start), 1) for s in smart if s.task.cognitive_demand >= 0.8],
        },
    }
