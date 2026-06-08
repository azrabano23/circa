"""Run the RhythmRX real-data analysis on the ShanghaiT2DM CGM dataset.

    python scripts/analyze_shanghai.py            # all patients (downloads ~3.7MB once)
    python scripts/analyze_shanghai.py --limit 20 # quick subset

Prints the circadian glucose profile (the dawn phenomenon), cohort stats, and the
per-patient peak-time spread that motivates personalized dosing.
"""
from __future__ import annotations

import argparse
import json

from missions.real_analysis import cohort_summary, hourly_profile
from missions.shanghai_data import load_all_cgm


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=None)
    args = p.parse_args()

    patients = load_all_cgm(limit=args.limit)
    all_readings = [r for _, rs in patients for r in rs]
    profile = hourly_profile(all_readings)

    print("# mean glucose by hour of day (real ShanghaiT2DM patients)")
    for h in range(24):
        if h in profile:
            bar = "#" * max(0, int((profile[h] - 100) / 3))
            print(f"{h:02d}:00  {profile[h]:6.1f}  {bar}")
    print()
    print(json.dumps(cohort_summary(patients), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
