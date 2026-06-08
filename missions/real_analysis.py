"""What real CGM data says about circadian glucose — the evidence base for RhythmRX.

Run on the ShanghaiT2DM dataset (100 real type-2 patients), this computes:

  - the **circadian glucose profile** (mean glucose by hour of day) — which makes
    the textbook *dawn phenomenon* fall straight out of real data;
  - the **daily swing** and time-in-range of the cohort; and, most importantly,
  - the **spread of each patient's personal glucose-peak time** — the quantity that
    decides whether "take it at the same time as everyone" can possibly be right.

These are functions over already-loaded readings (see `shanghai_data.py`), so the
analysis is testable on a fixture without a network.
"""
from __future__ import annotations

import math
import statistics
from datetime import datetime


def hourly_profile(readings: list[tuple[datetime, float]]) -> dict[int, float]:
    """Mean glucose (mg/dL) by hour of day from (timestamp, glucose) readings."""
    sums: dict[int, float] = {}
    counts: dict[int, int] = {}
    for ts, g in readings:
        sums[ts.hour] = sums.get(ts.hour, 0.0) + g
        counts[ts.hour] = counts.get(ts.hour, 0) + 1
    return {h: sums[h] / counts[h] for h in sorted(sums)}


def acrophase(profile: dict[int, float]) -> float:
    """Hour of the glucose peak from a 24 h single-harmonic fit of an hourly profile."""
    items = sorted(profile.items())
    if len(items) < 12:
        raise ValueError("need most of the day represented to fit a phase")
    w = 2.0 * math.pi / 24.0
    m = sum(v for _, v in items) / len(items)
    a = sum((v - m) * math.cos(w * h) for h, v in items) * 2.0 / len(items)
    b = sum((v - m) * math.sin(w * h) for h, v in items) * 2.0 / len(items)
    return (math.atan2(b, a) / w) % 24.0


def time_in_range(readings: list[tuple[datetime, float]], lo: float = 70.0,
                  hi: float = 180.0) -> float:
    vals = [g for _, g in readings]
    return 100.0 * sum(1 for g in vals if lo <= g <= hi) / len(vals) if vals else 0.0


def dawn_rise(profile: dict[int, float]) -> float:
    """The dawn-phenomenon rise: glucose at 08:00 minus its overnight trough (0-5h)."""
    trough = min(profile[h] for h in range(0, 6) if h in profile)
    return profile.get(8, trough) - trough


def cohort_summary(patients: list[tuple[str, list[tuple[datetime, float]]]]) -> dict:
    """Aggregate the real-data findings across a list of (patient_id, readings)."""
    all_readings: list[tuple[datetime, float]] = []
    personal_peaks: list[float] = []
    for _pid, readings in patients:
        if not readings:
            continue
        all_readings.extend(readings)
        prof = hourly_profile(readings)
        if len(prof) >= 12:
            personal_peaks.append(acrophase(prof))

    profile = hourly_profile(all_readings)
    vals = [g for _, g in all_readings]
    return {
        "patients": len(personal_peaks),
        "cgm_readings": len(all_readings),
        "mean_glucose": round(sum(vals) / len(vals), 1),
        "time_in_range_pct": round(time_in_range(all_readings), 1),
        "daily_swing_mgdl": round(max(profile.values()) - min(profile.values()), 1),
        "dawn_rise_mgdl": round(dawn_rise(profile), 1),
        "population_peak_hour": round(acrophase(profile), 1),
        "personal_peak_spread_h": round(statistics.pstdev(personal_peaks), 1) if len(personal_peaks) > 1 else 0.0,
        "personal_peak_range_h": (round(min(personal_peaks), 1), round(max(personal_peaks), 1)) if personal_peaks else (0, 0),
    }
