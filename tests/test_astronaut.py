"""Tests for the astronaut circadian model: CBTmin recovery, drift, countermeasure."""
from missions.astronaut import (
    estimate_cbtmin,
    simulate_mission,
    synth_core_temp,
    crew_alertness_at,
    _NOMINAL_CBTMIN,
)
from missions.benchmark_astronaut import run


def test_cbtmin_recovered_from_clean_signal():
    # generate core temp for a known CBTmin, then recover it
    for true_cbtmin in (3.0, 5.0, 7.5):
        hours = [0, 3, 6, 9, 12, 15, 18, 21]
        samples = synth_core_temp(true_cbtmin, hours)
        est = estimate_cbtmin(samples)
        diff = abs(est - true_cbtmin) % 24.0
        assert min(diff, 24.0 - diff) < 0.3   # within ~18 min


def test_cbtmin_robust_to_noise():
    hours = [1, 4, 7, 10, 13, 16, 19, 22]
    samples = synth_core_temp(5.0, hours, noise=0.1, rng_seed=7)
    est = estimate_cbtmin(samples)
    diff = abs(est - 5.0) % 24.0
    assert min(diff, 24.0 - diff) < 1.0


def test_needs_enough_samples():
    try:
        estimate_cbtmin([(0.0, 36.8), (12.0, 37.2)])
        assert False, "should require >= 3 samples"
    except ValueError:
        pass


def test_uncontrolled_schedule_drifts_more_than_countermeasure():
    unc = simulate_mission(14, policy="uncontrolled")
    cm = simulate_mission(14, policy="countermeasure")

    def drift(traj):
        d = abs(traj[-1].cbtmin - _NOMINAL_CBTMIN) % 24.0
        return min(d, 24.0 - d)

    assert drift(unc) > drift(cm)


def test_countermeasure_preserves_more_work_alertness():
    r = run(14)
    assert r["countermeasure"]["mean_work_alertness"] >= r["uncontrolled"]["mean_work_alertness"]
    assert r["alertness_gain_pct"] >= 0


def test_alertness_bounded():
    for h in range(24):
        a = crew_alertness_at(float(h), cbtmin=5.0)
        assert 0.0 <= a <= 1.0
