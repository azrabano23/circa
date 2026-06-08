"""Tests for the real-CGM analysis. Core math is checked on an offline fixture;
the full ShanghaiT2DM run is gated behind data being present (downloaded)."""
import math
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from missions.real_analysis import (
    acrophase,
    cohort_summary,
    dawn_rise,
    hourly_profile,
    time_in_range,
)


def _synthetic_patient(peak_hour: float, days: int = 3):
    """Readings whose hourly mean is a cosine peaking at peak_hour (+ dawn bump)."""
    out = []
    t0 = datetime(2021, 1, 1, 0, 0)
    for step in range(days * 24 * 4):       # 15-min cadence
        ts = t0 + timedelta(minutes=15 * step)
        h = ts.hour + ts.minute / 60.0
        g = 140 + 25 * math.cos(2 * math.pi * (h - peak_hour) / 24)
        out.append((ts, g))
    return out


def test_hourly_profile_and_acrophase():
    readings = _synthetic_patient(peak_hour=14.0)
    prof = hourly_profile(readings)
    assert len(prof) == 24
    est = acrophase(prof)
    diff = abs(est - 14.0) % 24.0
    assert min(diff, 24.0 - diff) < 0.5


def test_time_in_range():
    readings = [(datetime(2021, 1, 1, h), g) for h, g in
                [(0, 90), (1, 200), (2, 120), (3, 65)]]
    assert time_in_range(readings) == 50.0   # 90 and 120 in [70,180]


def test_dawn_rise_positive_when_morning_higher():
    # construct a profile with low night, high morning
    prof = {h: 110.0 for h in range(6)}
    prof[8] = 170.0
    assert dawn_rise(prof) == pytest.approx(60.0)


def test_cohort_spread_detects_differing_peaks():
    patients = [("a", _synthetic_patient(8.0)),
                ("b", _synthetic_patient(14.0)),
                ("c", _synthetic_patient(18.0))]
    s = cohort_summary(patients)
    assert s["patients"] == 3
    assert s["personal_peak_spread_h"] > 1.0     # differing clocks -> real spread


# --- gated: only runs if the real dataset has been downloaded ---
_DATA = Path(__file__).resolve().parent.parent / ".data_cache" / "shanghai" / "Shanghai_T2DM"


@pytest.mark.skipif(not _DATA.exists(), reason="ShanghaiT2DM not downloaded")
def test_real_shanghai_dawn_phenomenon():
    from missions.shanghai_data import load_all_cgm
    patients = load_all_cgm(limit=20)
    s = cohort_summary(patients)
    assert s["cgm_readings"] > 1000
    assert s["dawn_rise_mgdl"] > 20            # real dawn phenomenon is large
    assert s["personal_peak_spread_h"] > 1.0   # real patients differ
