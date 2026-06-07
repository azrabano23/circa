"""Command line for the circadian core.

    circa-circadian curve   --chronotype owl --wake 8     # print the alertness curve
    circa-circadian bench    --chronotype lark --wake 6    # FIFO vs circadian throughput
    circa-circadian bench-all                              # all chronotypes
"""
from __future__ import annotations

import argparse
import json

from circadian.benchmark import run
from circadian.model import Chronotype, alertness_curve, peak_hour


def _chronotype(name: str) -> Chronotype:
    return Chronotype(name.lower())


def _cmd_curve(args: argparse.Namespace) -> int:
    ct = _chronotype(args.chronotype)
    curve = alertness_curve(ct, args.wake)
    print(f"# alertness curve — {ct.value}, wake {args.wake}:00, peak {peak_hour(ct, args.wake)}:00")
    for hour, a in curve:
        bar = "#" * int(round(a * 40))
        print(f"{hour:5.1f}  {a:5.3f}  {bar}")
    return 0


def _cmd_bench(args: argparse.Namespace) -> int:
    print(json.dumps(run(_chronotype(args.chronotype), args.wake), indent=2))
    return 0


def _cmd_bench_all(args: argparse.Namespace) -> int:
    for ct in Chronotype:
        print(json.dumps(run(ct, args.wake), indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="circa-circadian")
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("curve", help="print the alertness curve")
    pc.add_argument("--chronotype", default="intermediate")
    pc.add_argument("--wake", type=float, default=7.0)
    pc.set_defaults(func=_cmd_curve)

    pb = sub.add_parser("bench", help="FIFO vs circadian throughput")
    pb.add_argument("--chronotype", default="intermediate")
    pb.add_argument("--wake", type=float, default=7.0)
    pb.set_defaults(func=_cmd_bench)

    pa = sub.add_parser("bench-all", help="benchmark across all chronotypes")
    pa.add_argument("--wake", type=float, default=7.0)
    pa.set_defaults(func=_cmd_bench_all)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
