"""Tests for RhythmRX: phase recovery from cortisol, sensitivity rhythm, dose timing."""
from missions.rhythmrx import (
    CortisolSample,
    estimate_circadian_phase,
    insulin_sensitivity,
    optimal_dose_time,
    simulate_day,
)
from missions.benchmark_rhythmrx import run, MEALS


def test_phase_recovered_from_cortisol():
    # cortisol peaking at a known hour should be recovered
    for peak in (8.0, 11.0, 6.0):
        import math
        samples = [
            CortisolSample(h, 0.5 * (1 + math.cos(2 * math.pi * (h - peak) / 24)))
            for h in (6, 9, 12, 15, 18, 21)
        ]
        est = estimate_circadian_phase(samples)
        diff = abs(est - peak) % 24.0
        assert min(diff, 24.0 - diff) < 0.3


def test_phase_needs_three_samples():
    try:
        estimate_circadian_phase([CortisolSample(8, 1.0), CortisolSample(20, 0.2)])
        assert False
    except ValueError:
        pass


def test_sensitivity_bounded():
    for h in range(24):
        assert 0.0 <= insulin_sensitivity(float(h), 8.0) <= 1.0


def test_sensitivity_peak_tracks_phase():
    def peak_hour(phase):
        return max(range(0, 240), key=lambda k: insulin_sensitivity(k / 10.0, phase)) / 10.0
    assert peak_hour(11.0) > peak_hour(8.0)   # delayed phase -> later sensitivity peak


def test_personalized_beats_clinic_default_for_shifted_patient():
    r = run()
    assert r["rhythmrx_personalized"]["hyperglycemia_auc"] <= r["clinic_default"]["hyperglycemia_auc"]
    assert r["hyperglycemia_reduction_pct"] >= 0


def test_optimal_dose_is_a_valid_time():
    t = optimal_dose_time(11.0, MEALS)
    assert 6.0 <= t <= 20.0
