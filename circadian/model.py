"""Two-process model of daytime alertness.

Alertness across the waking day is well described by the interaction of two
processes (Borbely, 1982; Achermann, 2004), plus sleep inertia:

  - Process C (circadian): a roughly sinusoidal oscillation driven by the
    suprachiasmatic nucleus, with an alertness peak in the early-to-mid
    afternoon and a trough in the small hours. Its *phase* shifts with
    chronotype: morning types ("larks") peak earlier, evening types ("owls")
    peak later. We model C as a cosine whose phase is anchored to the person's
    chronotype.

  - Process S (homeostatic sleep pressure): alertness erodes roughly linearly
    the longer one has been awake.

  - Sleep inertia: a short-lived grogginess in the first ~90 minutes after
    waking, modelled as a fast-decaying penalty.

Net alertness is C minus sleep pressure minus inertia, clamped to [0, 1].

This is a model, not a measurement. The point is not biological exactness but
that scheduling decisions follow from an explicit, inspectable alertness curve
that we can test, plot, and reason about — instead of hard-coded "mornings are
good" bonuses.
"""
from __future__ import annotations

import math
from enum import Enum


class Chronotype(str, Enum):
    """Coarse chronotype classes (cf. the Morningness-Eveningness Questionnaire).

    The value is the circadian phase shift in hours relative to an
    intermediate type: larks run ahead (negative shift -> earlier peak),
    owls run behind (positive shift -> later peak).
    """

    LARK = "lark"
    INTERMEDIATE = "intermediate"
    OWL = "owl"

    @property
    def phase_shift_hours(self) -> float:
        return {"lark": -2.0, "intermediate": 0.0, "owl": 2.5}[self.value]

    @classmethod
    def from_meq(cls, meq_score: int) -> "Chronotype":
        """Map a Morningness-Eveningness Questionnaire score (16-86) to a class.

        Standard MEQ cutoffs: <= 41 evening, 42-58 intermediate, >= 59 morning.
        """
        if meq_score >= 59:
            return cls.LARK
        if meq_score <= 41:
            return cls.OWL
        return cls.INTERMEDIATE


# The circadian alertness rhythm peaks in the early-to-mid afternoon for an
# intermediate type; chronotype shifts this peak earlier (larks) or later (owls).
_BASE_PEAK_HOUR = 14.0
_CIRCADIAN_PERIOD = 24.0

# Homeostatic sleep pressure: alertness lost per hour awake.
_SLEEP_PRESSURE_PER_HOUR = 0.020

# Sleep inertia: grogginess just after waking (amplitude and decay timescale in h).
_INERTIA_AMPLITUDE = 0.35
_INERTIA_DECAY_HOURS = 0.7


def _circadian_component(hour: float, chronotype: Chronotype) -> float:
    """Process C in [0, 1]: cosine peaking at the chronotype-shifted peak hour."""
    peak = _BASE_PEAK_HOUR + chronotype.phase_shift_hours
    phase = 2.0 * math.pi * (hour - peak) / _CIRCADIAN_PERIOD
    return 0.5 * (1.0 + math.cos(phase))


def _sleep_inertia(hours_awake: float) -> float:
    """Grogginess penalty in [0, amplitude], largest at wake, fading over ~90 min."""
    return _INERTIA_AMPLITUDE * math.exp(-hours_awake / _INERTIA_DECAY_HOURS)


def alertness(hour: float, chronotype: Chronotype, wake_hour: float = 7.0) -> float:
    """Predicted alertness at clock `hour` in [0, 1].

    Circadian oscillation (phase-shifted by chronotype), minus homeostatic sleep
    pressure that builds over the day, minus a short sleep-inertia penalty right
    after waking. Hours before waking return 0.
    """
    hours_awake = hour - wake_hour
    if hours_awake < 0:
        return 0.0

    circadian = _circadian_component(hour, chronotype)
    pressure = _SLEEP_PRESSURE_PER_HOUR * hours_awake
    inertia = _sleep_inertia(hours_awake)

    value = circadian - pressure - inertia
    return max(0.0, min(1.0, value))


def alertness_curve(
    chronotype: Chronotype, wake_hour: float = 7.0, step: float = 0.5
) -> list[tuple[float, float]]:
    """Sample the alertness curve across the waking day as (hour, alertness)."""
    out: list[tuple[float, float]] = []
    h = wake_hour
    while h <= 24.0:
        out.append((round(h, 2), round(alertness(h, chronotype, wake_hour), 4)))
        h += step
    return out


def peak_hour(chronotype: Chronotype, wake_hour: float = 7.0) -> float:
    """Hour of maximum predicted alertness for this chronotype/wake time."""
    return max(alertness_curve(chronotype, wake_hour, step=0.25), key=lambda p: p[1])[0]
