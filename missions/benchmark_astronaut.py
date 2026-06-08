"""Does circadian-aware light scheduling actually protect crew alertness?

Run the identical 14-day mission twice — once with uncontrolled evening light,
once with an engineered phase-holding light pulse — and compare two things the
flight surgeon cares about:

  - **phase drift**: how far CBTmin wanders from its healthy ~05:00 slot, and
  - **on-shift alertness**: mean modelled alertness across the 09:00-17:00 work block.

Both crews fly the same schedule; only the *light policy* differs, so any gap is
attributable to circadian engineering — which is exactly NASA's countermeasure
thesis. This is a model-internal result on synthetic data: it demonstrates the
mechanism, not a flight outcome.
"""
from __future__ import annotations

from missions.astronaut import simulate_mission, _NOMINAL_CBTMIN


def run(days: int = 14) -> dict:
    uncontrolled = simulate_mission(days, policy="uncontrolled")
    countermeasure = simulate_mission(days, policy="countermeasure")

    def drift(traj):
        # circular distance of final CBTmin from the healthy nominal
        d = abs(traj[-1].cbtmin - _NOMINAL_CBTMIN) % 24.0
        return round(min(d, 24.0 - d), 2)

    def mean_alert(traj):
        return round(sum(c.work_alertness for c in traj) / len(traj), 4)

    a0 = mean_alert(uncontrolled)
    a1 = mean_alert(countermeasure)
    return {
        "days": days,
        "uncontrolled": {
            "final_cbtmin": uncontrolled[-1].cbtmin,
            "phase_drift_h": drift(uncontrolled),
            "mean_work_alertness": a0,
        },
        "countermeasure": {
            "final_cbtmin": countermeasure[-1].cbtmin,
            "phase_drift_h": drift(countermeasure),
            "mean_work_alertness": a1,
        },
        "alertness_gain_pct": round(100.0 * (a1 - a0) / a0, 1) if a0 else float("inf"),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
