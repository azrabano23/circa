"""RhythmRX — chronotherapy for diabetes: time the medication to the patient's clock.

## The thesis

A diabetes pill taken at the wrong point in your biological day is a weaker pill.
Insulin sensitivity and glucose tolerance are under circadian control (the SCN
master clock), so the body's ability to clear glucose — and to use a drug that
helps it — rises and falls across the day. "Chronotherapy" means dosing in step
with that rhythm. The problem is that **nobody measures *your* rhythm**: the clinic
says "take it with breakfast," which assumes everyone's clock is the same and
entrained to the same schedule. Shift workers, late chronotypes, and the sleep-
disrupted are exactly the people whose clocks are *shifted* — and who therefore
get the least from a one-size clock-time.

## Where the data comes from (the input)

The practical, low-cost circadian phase marker is **salivary cortisol**, which
rises to a peak shortly after waking and declines across the day. From a few
timed saliva samples (the RhythmRX "spit strip": morning / afternoon / evening)
we fit the cortisol rhythm and recover the patient's circadian **phase**. On
Earth that phase can also be refined with wearable signals (Apple Watch / Fitbit
sleep, skin temperature, heart-rate rhythm) and continuous glucose monitor data.

## What this module does

1. **`estimate_circadian_phase`** — recover the patient's phase (cortisol acrophase)
   from timed saliva samples by fitting a 24 h sinusoid.
2. **`insulin_sensitivity`** — a circadian insulin-sensitivity rhythm anchored to
   that phase (higher in the biological day, lower in the biological evening,
   consistent with documented evening glucose intolerance).
3. **`optimal_dose_time`** — the once-daily dose time that best matches the drug's
   action window to the patient's sensitivity rhythm.
4. **`simulate_day` / `benchmark.py`** — simulate a day of meals + medication and
   score glycemic burden (hyperglycemia area-over-threshold), comparing a fixed
   clinic time against the personalized time.

## Honest framing

Circadian regulation of glucose and the *direction* of the chronotherapy effect
are well established in the literature (reviews below). The specific magnitude
this simulator reports is **model-internal and illustrative**, not a clinical
result, and some widely-quoted single-trial percentages in this space are
contested — RhythmRX's claim is the robust one: *timing to the individual's
measured rhythm beats a fixed clock time*, most for the people whose clocks are
shifted. This is decision support; it does not replace a clinician.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

_PERIOD = 24.0
_TARGET = 100.0       # mg/dL baseline
_HYPER = 140.0        # mg/dL post-meal hyperglycemia threshold


@dataclass(frozen=True)
class CortisolSample:
    hour: float        # clock hour of the saliva sample
    value: float       # relative cortisol (any consistent unit)


def _solve3(A: list[list[float]], y: list[float]) -> list[float]:
    """Solve a 3x3 linear system by Gaussian elimination (stdlib)."""
    M = [row[:] + [y[i]] for i, row in enumerate(A)]
    for col in range(3):
        piv = max(range(col, 3), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        if abs(M[col][col]) < 1e-12:
            raise ValueError("degenerate fit (samples not spread across the day)")
        for r in range(3):
            if r != col:
                f = M[r][col] / M[col][col]
                M[r] = [M[r][k] - f * M[col][k] for k in range(4)]
    return [M[i][3] / M[i][i] for i in range(3)]


def estimate_circadian_phase(samples: list[CortisolSample]) -> float:
    """Recover circadian phase = cortisol acrophase (hour of peak) from saliva.

    Least-squares fit of `value ~ m + a*cos(wt) + b*sin(wt)` (works with the few
    *daytime-only* samples a real spit-strip provides — not the full-day uniform
    sampling a naive projection assumes). A normally entrained person peaks ~08:00;
    a phase-delayed person peaks later, and that later peak is exactly what a fixed
    'take with breakfast' rule ignores.
    """
    if len(samples) < 3:
        raise ValueError("need at least 3 timed saliva samples")
    w = 2.0 * math.pi / _PERIOD
    # normal equations for [m, a, b]
    A = [[0.0] * 3 for _ in range(3)]
    yv = [0.0, 0.0, 0.0]
    for s in samples:
        basis = [1.0, math.cos(w * s.hour), math.sin(w * s.hour)]
        for i in range(3):
            yv[i] += basis[i] * s.value
            for j in range(3):
                A[i][j] += basis[i] * basis[j]
    _, a, b = _solve3(A, yv)
    acrophase = (math.atan2(b, a) / w) % _PERIOD
    return round(acrophase, 3)


def insulin_sensitivity(hour: float, phase: float) -> float:
    """Insulin sensitivity in [0,1] at clock `hour` for a patient with this phase.

    Peaks in the biological day (~5 h after the cortisol peak) and troughs in the
    biological evening/night — the shape behind documented evening glucose
    intolerance. Anchored to the patient's measured phase, so a shifted clock
    moves the whole curve.
    """
    sens_peak = (phase + 5.0) % _PERIOD
    return 0.5 * (1.0 + math.cos(2.0 * math.pi * (hour - sens_peak) / _PERIOD))


def _meal_excursion(t: float, meal_hour: float, carbs: float,
                    tau: float = 1.2, scale: float = 1.3) -> float:
    """Glucose rise at time t from a meal at meal_hour.

    Normalized gamma kernel peaking `tau` h after the meal at height carbs*scale
    mg/dL (so a 70 g meal spikes ~+90, glucose ~190 — a realistic diabetic post-
    meal excursion), with a multi-hour tail."""
    dt = t - meal_hour
    if dt < 0:
        return 0.0
    return carbs * scale * (dt / tau) * math.exp(1.0 - dt / tau)


def _med_clearance(t: float, dose_hour: float, phase: float, potency: float) -> float:
    """Glucose-lowering from a once-daily dose taken at dose_hour.

    Active over ~14 h after the dose; its strength scales with the patient's
    insulin sensitivity *at the time it is taken* — the chronotherapy mechanism:
    a dose given when the body is most insulin-sensitive does more work.
    """
    dt = t - dose_hour
    if dt < 0 or dt > 14.0:
        return 0.0
    sens = insulin_sensitivity(dose_hour, phase)
    window = math.sin(math.pi * dt / 14.0)   # smooth on/off over the action window
    return potency * sens * window


def simulate_day(meals: list[tuple[float, float]], dose_hour: float, phase: float,
                 potency: float = 70.0, step: float = 0.25) -> dict:
    """Simulate one day of glucose and return the hyperglycemia burden.

    glucose(t) = baseline + sum(meal excursions) - medication clearance, clamped at
    baseline. Returns area-over-threshold (hyperglycemia AUC) and time-in-range.
    """
    t = 6.0
    auc_over = 0.0
    in_range = 0
    total = 0
    while t <= 24.0:
        g = _TARGET
        for mh, c in meals:
            g += _meal_excursion(t, mh, c)
        g -= _med_clearance(t, dose_hour, phase, potency)
        g = max(_TARGET * 0.7, g)
        auc_over += max(0.0, g - _HYPER) * step
        total += 1
        if 70.0 <= g <= _HYPER:
            in_range += 1
        t += step
    return {
        "hyperglycemia_auc": round(auc_over, 1),
        "time_in_range_pct": round(100.0 * in_range / total, 1),
    }


def optimal_dose_time(phase: float, meals: list[tuple[float, float]],
                      potency: float = 70.0) -> float:
    """Search dose times and return the one minimizing hyperglycemia burden."""
    best_t, best_auc = 6.0, float("inf")
    t = 6.0
    while t <= 20.0:
        auc = simulate_day(meals, t, phase, potency)["hyperglycemia_auc"]
        if auc < best_auc:
            best_auc, best_t = auc, t
        t += 0.5
    return round(best_t, 2)
