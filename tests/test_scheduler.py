"""Behavioural guarantees of the scheduler and the FIFO-vs-circadian benchmark."""
from datetime import datetime, timedelta

from circadian.benchmark import run, throughput
from circadian.model import Chronotype
from circadian.scheduler import Slot, Task, plan_day, score_slot


def _day(wake=7.0, end=22.0):
    base = datetime(2026, 1, 1)
    return [Slot(base + timedelta(hours=wake), base + timedelta(hours=end))]


def test_no_double_booking():
    tasks = [Task(f"t{i}", f"task {i}", 60, cognitive_demand=0.5) for i in range(6)]
    scheduled, _ = plan_day(tasks, _day(), Chronotype.INTERMEDIATE)
    intervals = sorted((s.start, s.end) for s in scheduled)
    for (s1, e1), (s2, e2) in zip(intervals, intervals[1:]):
        assert e1 <= s2  # no overlap


def test_oversized_task_is_unscheduled():
    tasks = [Task("big", "10h task", 600, cognitive_demand=0.5)]
    free = [Slot(datetime(2026, 1, 1, 9), datetime(2026, 1, 1, 11))]  # only 2h
    scheduled, unscheduled = plan_day(tasks, free, Chronotype.INTERMEDIATE)
    assert not scheduled
    assert len(unscheduled) == 1


def test_demand_zero_is_timing_indifferent():
    light = Task("l", "light", 30, cognitive_demand=0.0)
    base = datetime(2026, 1, 1)
    early = score_slot(base.replace(hour=10), light, Chronotype.INTERMEDIATE)
    late = score_slot(base.replace(hour=16), light, Chronotype.INTERMEDIATE)
    assert early == late == 1.0  # a**0 == 1 everywhere


def test_hard_task_scores_higher_at_peak():
    hard = Task("h", "hard", 60, cognitive_demand=0.95)
    base = datetime(2026, 1, 1)
    peak = score_slot(base.replace(hour=10), hard, Chronotype.INTERMEDIATE)
    night = score_slot(base.replace(hour=23), hard, Chronotype.INTERMEDIATE)
    assert peak > night


def test_scheduler_is_deterministic():
    tasks = [Task(f"t{i}", f"t{i}", 45, cognitive_demand=(i % 3) / 2) for i in range(8)]
    a, _ = plan_day(tasks, _day(), Chronotype.OWL, wake_hour=8.0)
    b, _ = plan_day(tasks, _day(), Chronotype.OWL, wake_hour=8.0)
    assert [(s.task.id, s.start) for s in a] == [(s.task.id, s.start) for s in b]


def test_circadian_beats_fifo_on_throughput():
    # the headline claim: aligning hard work with the alertness peak raises
    # modelled cognitive throughput versus clock-blind FIFO.
    for ct in Chronotype:
        result = run(ct, wake_hour=7.0)
        assert result["throughput_circadian"] >= result["throughput_fifo"]


def test_benchmark_throughput_nonnegative():
    result = run(Chronotype.LARK, wake_hour=6.0)
    assert result["throughput_circadian"] >= 0.0
    assert result["improvement_pct"] >= 0.0
