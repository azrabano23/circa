"""Astronaut circadian alignment — the NASA SpaceTech application of Circa.

## What's actually measured (and where Circa's inputs come from)

NASA does not read a "circadian clock" directly; it *infers* one from wearables.
On the ISS each crew member wears an **Actiwatch Spectrum** on the non-dominant
wrist, which logs, in 1-minute epochs:
  - **activity** (accelerometer) -> rest/wake state, and
  - **ambient light** (color photodiodes) -> the zeitgeber driving the clock.
Core body temperature is captured separately (e.g. ESA's non-invasive Thermo-Mini
headband). From actigraphy + photometry NASA estimates each astronaut's
**core-body-temperature minimum (CBTmin)** — the gold-standard marker of circadian
phase — using its Circadian Performance Simulation Software. (Actigraphy +
photometry have been collected on 21 astronauts over 3,248 mission-days.)

The operational problem: on the ISS the crew sees **16 sunrises/sunsets per day**,
so without a carefully engineered light schedule the clock drifts, CBTmin wanders
out of the sleep window, and alertness during work hours collapses — which is a
flight-safety issue.

## What this module does

It is a small, dependency-free model of that loop:
  1. synthesize the core-temperature signal a wearable would see (`synth_core_temp`);
  2. recover CBTmin from noisy samples the way NASA does in spirit — by fitting a
     24 h sinusoid (`estimate_cbtmin`);
  3. evolve the clock day-by-day under a **light policy**, using a simplified
     phase-response curve (`simulate_mission`); and
  4. score crew alertness during the work block under the resulting phase.

The point is to show, on synthetic-but-realistic data, that a circadian-aware
light/scheduling policy keeps CBTmin parked under the sleep block and preserves
on-shift alertness, where an uncontrolled schedule lets it drift.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from circadian.model import Chronotype, alertness

_PERIOD = 24.0
# Healthy entrained CBTmin sits ~5:00; core temp peaks ~12 h later (~17:00).
_NOMINAL_CBTMIN = 5.0
_CBT_MEAN = 36.8     # deg C
_CBT_AMPL = 0.45     # deg C peak-to-mean


def synth_core_temp(cbtmin_hour: float, sample_hours: list[float], noise: float = 0.0,
                    rng_seed: int = 0) -> list[tuple[float, float]]:
    """Core body temperature a wearable would log, given the current CBTmin.

    CBT(t) = mean - amplitude * cos(2pi (t - cbtmin)/24): minimal at cbtmin,
    maximal ~12 h later. `noise` adds deterministic pseudo-jitter (no RNG state,
    so the model stays reproducible)."""
    out: list[tuple[float, float]] = []
    for i, t in enumerate(sample_hours):
        phase = 2.0 * math.pi * (t - cbtmin_hour) / _PERIOD
        temp = _CBT_MEAN - _CBT_AMPL * math.cos(phase)
        if noise:
            # deterministic jitter from a hash of (seed, i): reproducible, no globals
            jitter = (((rng_seed * 2654435761 + i * 40503) % 1000) / 1000.0 - 0.5)
            temp += noise * jitter
        out.append((t, round(temp, 4)))
    return out


def estimate_cbtmin(samples: list[tuple[float, float]]) -> float:
    """Recover CBTmin (hour, 0-24) from (hour, temperature) samples.

    Fits a single 24 h sinusoid by projecting onto sin/cos basis (the standard
    closed-form single-harmonic fit) and returns the hour of the minimum. Needs
    >= 3 samples spread across the day; robust to the noise a wearable carries.
    """
    if len(samples) < 3:
        raise ValueError("need at least 3 samples across the day to fit phase")
    n = len(samples)
    w = 2.0 * math.pi / _PERIOD
    mean = sum(v for _, v in samples) / n
    a = sum((v - mean) * math.cos(w * t) for t, v in samples) * 2.0 / n
    b = sum((v - mean) * math.sin(w * t) for t, v in samples) * 2.0 / n
    # temp(t) ~ mean + a cos(w t) + b sin(w t) = mean + A cos(w(t - acrophase))
    acrophase = (math.atan2(b, a) / w) % _PERIOD   # hour of maximum temp
    cbtmin = (acrophase + 12.0) % _PERIOD          # minimum is a half-period away
    return round(cbtmin, 3)


def _phase_response(light_hour: float, cbtmin_hour: float) -> float:
    """Simplified light phase-response curve (hours of shift per bright-light pulse).

    Classic shape: bright light *after* CBTmin advances the clock (negative shift,
    earlier), light *before* CBTmin delays it (positive shift, later); light far
    from CBTmin (subjective day) has little effect. Modeled as a sine of the time
    since CBTmin, which captures the advance/delay zero-crossing at CBTmin."""
    hours_since_min = ((light_hour - cbtmin_hour) % _PERIOD)
    # +sin -> the dead zone in subjective day, delay region pre-min, advance post-min
    return -1.2 * math.sin(2.0 * math.pi * hours_since_min / _PERIOD)


@dataclass
class CrewDay:
    day: int
    cbtmin: float
    work_alertness: float   # mean alertness across the work block [0,1]


def _bright_light_hours(policy: str, cbtmin: float, target: float = _NOMINAL_CBTMIN) -> list[float]:
    """When the crew gets its dominant bright-light exposure under a policy.

    'countermeasure' is a closed-loop light *controller*: when the clock runs late
    (CBTmin past target) it delivers bright light in the biological morning to
    *advance* it; when it runs early, evening light to *delay* it — holding CBTmin
    near the target the way an engineered ISS lighting protocol does. 'uncontrolled'
    is fixed evening module light, which sits in the delay zone and pushes late.
    """
    if policy == "countermeasure":
        error = ((cbtmin - target + 12.0) % _PERIOD) - 12.0   # +ve = running late
        if error >= 0:
            return [(cbtmin + 3.0) % _PERIOD]    # morning light -> advance (corrects late)
        return [(cbtmin + 15.0) % _PERIOD]       # evening light -> delay (corrects early)
    return [22.0]


def simulate_mission(days: int = 14, policy: str = "uncontrolled",
                     start_cbtmin: float = _NOMINAL_CBTMIN,
                     work_block: tuple[float, float] = (9.0, 17.0)) -> list[CrewDay]:
    """Evolve CBTmin over a mission under a light `policy` and score work alertness.

    policy='uncontrolled' lets evening light drift the clock later each day;
    policy='countermeasure' applies a phase-holding light pulse. Alertness during
    the fixed work block is computed from the (drifting) phase: we map CBTmin to an
    equivalent wake time (~2 h after CBTmin) and reuse the validated alertness model.
    """
    cbtmin = start_cbtmin % _PERIOD
    out: list[CrewDay] = []
    w0, w1 = work_block
    for d in range(days):
        # daily phase shift = sum of light pulses' PRC contributions
        shift = sum(_phase_response(h, cbtmin) for h in _bright_light_hours(policy, cbtmin))
        cbtmin = (cbtmin + shift) % _PERIOD
        # CBTmin ~2 h before habitual wake; invert to an effective wake hour
        wake = (cbtmin + 2.0) % _PERIOD
        # mean alertness across the work block
        samples = [w0 + 0.5 * k for k in range(int((w1 - w0) * 2) + 1)]
        mean_alert = sum(alertness(h, Chronotype.INTERMEDIATE, wake) for h in samples) / len(samples)
        out.append(CrewDay(day=d + 1, cbtmin=round(cbtmin, 3), work_alertness=round(mean_alert, 4)))
    return out


def crew_alertness_at(hour: float, cbtmin: float) -> float:
    """Predicted crew alertness at a clock `hour` given current CBTmin."""
    wake = (cbtmin + 2.0) % _PERIOD
    return alertness(hour, Chronotype.INTERMEDIATE, wake)
