"""Does timing the dose to the patient's clock actually help — and for whom?

We take a **phase-delayed patient** (cortisol peaks at 11:00, not the textbook
08:00 — a late chronotype or shift worker), measure their phase from saliva, and
compare two once-daily dosing strategies on an identical day of meals:

  - **Clinic default**: "take it with breakfast" — a fixed 08:00 dose, the same
    advice everyone gets.
  - **RhythmRX personalized**: dose at the time that best matches *this* patient's
    insulin-sensitivity rhythm.

The metric is the **hyperglycemia burden** (glucose area over the 140 mg/dL
threshold) across the day. The whole RhythmRX thesis is that the gap is largest
exactly for the people whose clocks are shifted — and the clinic default can't see
that because it never measured their rhythm.
"""
from __future__ import annotations

from missions.rhythmrx import (
    CortisolSample,
    estimate_circadian_phase,
    optimal_dose_time,
    simulate_day,
)

# A standard day of meals: (hour, carb load)
MEALS = [(8.0, 55.0), (13.0, 70.0), (19.0, 60.0)]


def run() -> dict:
    # phase-delayed patient: saliva cortisol peaking ~11:00
    true_phase = 11.0
    samples = [
        CortisolSample(8.0, 0.62),   # still rising
        CortisolSample(11.0, 1.00),  # peak
        CortisolSample(14.0, 0.78),
        CortisolSample(20.0, 0.20),
    ]
    est_phase = estimate_circadian_phase(samples)

    clinic_dose = 8.0
    personalized_dose = optimal_dose_time(est_phase, MEALS)

    clinic = simulate_day(MEALS, clinic_dose, est_phase)
    personalized = simulate_day(MEALS, personalized_dose, est_phase)

    a0 = clinic["hyperglycemia_auc"]
    a1 = personalized["hyperglycemia_auc"]
    return {
        "patient": "phase-delayed (cortisol peak ~11:00)",
        "estimated_phase_h": est_phase,
        "clinic_default": {"dose_hour": clinic_dose, **clinic},
        "rhythmrx_personalized": {"dose_hour": personalized_dose, **personalized},
        "hyperglycemia_reduction_pct": round(100.0 * (a0 - a1) / a0, 1) if a0 else 0.0,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
