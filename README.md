# Circa — a chronotype-aware scheduler

[![tests](https://github.com/azrabano23/circa/actions/workflows/tests.yml/badge.svg)](https://github.com/azrabano23/circa/actions/workflows/tests.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Circa schedules your hardest work for the hours your brain is actually sharpest.** It models when you are most alert across the day — from your chronotype and wake time — and places cognitively demanding tasks into those windows, around your fixed calendar. The scheduling intelligence is a small, dependency-light, tested Python package (`circadian/`); a FastAPI + React app (`backend/`, `frontend/`) wraps it into a product.

The premise is borrowed from the most extreme case of circadian disruption there is: **astronaut performance**. NASA studies sleep and circadian misalignment intensively because a foggy crew at the wrong point in their biological day is a safety problem — alertness, reaction time, and error rates all track the circadian curve. The same science applies to shift workers, students, and anyone whose calendar ignores their biology. Circa is the consumer-scale version of that idea, built on an explicit, inspectable alertness model rather than vibes.

---

## The problem

Calendars are clock-blind. They know *that* you have three hours free; they have no idea that, for you, 9am is groggy and 2pm is razor-sharp — or the reverse if you're an evening type. So demanding work lands wherever there's a gap, which for many people means doing their hardest thinking during their worst hours. The cost is invisible but real: the same task done off-peak takes longer, produces more errors, and burns more willpower.

This is worst for **evening types ("owls")**, who are routinely forced onto morning-shaped schedules and pay for it all day. Any tool that wants to help has to (a) know *when* you're sharp, and (b) be willing to move work to that time — not just fill gaps front-to-back.

## The approach

Circa separates the *science* from the *app*. The science lives in `circadian/`, a standard-library-only package with no framework or database dependencies, so every recommendation is attributable to an explicit model you can read, test, and plot.

**1. An alertness model** (`circadian/model.py`) — a transparent two-process model (Borbély, 1982):

- **Process C (circadian):** a cosine alertness rhythm peaking in the early-to-mid afternoon, with its *phase shifted by chronotype* — larks peak earlier, owls later. Chronotype is a coarse class derived from a Morningness–Eveningness Questionnaire score.
- **Process S (homeostatic):** alertness erodes roughly linearly with hours awake.
- **Sleep inertia:** a short grogginess penalty in the ~90 minutes after waking.

Net alertness `A(t) = C(t) − pressure(t) − inertia(t)`, clamped to `[0, 1]`. For an intermediate type waking at 7am this peaks around **1:30pm**; for a lark around **11:30am**; for an owl around **4pm** — ordered exactly as chronotype predicts.

**2. A scheduler** (`circadian/scheduler.py`) — greedy by priority and deadline, it searches candidate start times *within* each free slot (not just the front) and places each task where it scores best. The score is deliberately simple: `A(t) ** demand`. Raising alertness to the task's cognitive demand sharpens the pull toward peak hours as demand rises, while a demand of 0 makes a task timing-indifferent so it fills the gaps. A late-night guard rail penalises the biological night. The scheduler never double-books and is fully deterministic.

## Results

The honest question for any scheduler like this is: *does aligning work with the alertness curve actually buy anything, or does ordinary front-to-back planning already get there by accident?* To answer it, `circadian/benchmark.py` runs the **same task set into the same free day** under two schedulers — FIFO (priority order, clock-blind, front-packed) and Circa — and measures **realised cognitive throughput** = Σ `demand × alertness(scheduled_time)`. The only difference between the two is *when* each task is placed, so the gap is attributable purely to circadian-aware timing.

`circa-circadian bench-all` (7 mixed tasks, free day 07:00–22:00):

| chronotype | alertness peak | FIFO throughput | Circa throughput | improvement |
|---|---:|---:|---:|---:|
| lark | 11:30 | 2.58 | 3.25 | **+26%** |
| intermediate | 13:30 | 1.83 | 3.11 | **+70%** |
| owl | 16:00 | 0.97 | 2.93 | **+203%** |

FIFO front-loads the three demanding tasks to 07:00–09:30 for *everyone*; Circa moves them to each chronotype's actual peak (the owl's hard work shifts to 15:00–17:30). **The benefit scales with how badly the default schedule fights your biology** — larks lose least from clock-blind planning, owls lose most, which is exactly the lived experience the tool is built to fix.

**Read this honestly.** This is a *model-internal* result: it proves the scheduler does what it claims under its own alertness model, on a synthetic workload. It is **not** a claim about real human output — that requires a user study measuring actual task completion and error rates against scheduled vs. self-chosen timing. What the benchmark establishes is that the mechanism is sound and the gains are concentrated exactly where theory says they should be. Validating the alertness model against wearable data (sleep, HRV) is the next step.

## Reproducibility

Everything in `circadian/` is deterministic and dependency-free (standard library only). `pytest -q` runs 13 tests covering the model (alertness bounded in `[0,1]`; zero before waking; chronotype orders the peak lark < intermediate < owl; MEQ mapping; night below peak) and the scheduler (no double-booking; oversized tasks left unscheduled; demand-0 tasks timing-indifferent; demanding tasks score higher at peak; determinism; and the headline claim that Circa ≥ FIFO on throughput for every chronotype). CI runs on Python 3.10 and 3.12.

```bash
pip install -e ".[dev]"

circa-circadian curve --chronotype owl --wake 8     # ASCII plot of the alertness curve
circa-circadian bench --chronotype intermediate     # FIFO vs Circa, JSON metrics
circa-circadian bench-all                            # all three chronotypes
pytest -q
```

```python
from datetime import datetime
from circadian import Chronotype, Task, Slot, plan_day

base = datetime(2026, 1, 1)
free = [Slot(base.replace(hour=9), base.replace(hour=17))]
tasks = [Task("t1", "hard proof", 90, cognitive_demand=0.95, priority="high")]
scheduled, unscheduled = plan_day(tasks, free, Chronotype.OWL, wake_hour=8.0)
print(scheduled[0].start, scheduled[0].reason)   # placed near the owl's afternoon peak
```

## The application

`backend/` (FastAPI, SQLAlchemy, JWT auth) and `frontend/` (React + TypeScript + Tailwind) wrap the core into a usable product: account/onboarding, a chronotype quiz that sets your model parameters, task and event management, a daily optimised plan, and integration scaffolding (Google Calendar, Canvas LMS import). Run it with `docker-compose up`.

**Status, honestly.** The `circadian/` core and the account/task/event/dashboard APIs work end to end. The LLM-assisted features (natural-language task import, an OpenAI-backed scheduler variant) and the Google Calendar OAuth round-trip are scaffolded but not production-hardened — they need credential setup and error handling before they're reliable. The deterministic core is the part to evaluate; the app is the delivery vehicle around it.

## Business model & go-to-market

- **Who it's for:** first, students and knowledge workers who already feel the mismatch between their schedule and their energy (the "I'm useless before noon" / "I do my best work at midnight" crowd). Later, employers and universities that schedule shift or rotation work.
- **Wedge:** a free personal scheduler that visibly improves your day, monetised on a Pro tier (wearable integration for a *personalised* alertness curve, team scheduling, calendar write-back).
- **Defensible part:** not the calendar UI — the *validated alertness model*. Once it's calibrated against a user's own sleep/HRV data, the chronotype profile and the longitudinal record of what they actually completed when become the moat.
- **Why now:** consumer wearables now expose the sleep and heart-rate signals needed to personalise the circadian model, and frontier LLMs make natural-language task capture cheap — so the friction that used to kill scheduling tools is gone.

## Roadmap & limitations

The alertness model is a defensible but simplified two-process model; it does not yet ingest real sleep debt, light exposure, caffeine, or the post-lunch dip as a distinct feature. The scheduler is greedy, not optimal, and assumes tasks are atomic. The benchmark is model-internal on synthetic tasks. Next: calibrate the model against wearable data, add a held-out evaluation of predicted vs. self-reported alertness, model the post-lunch dip and split-shift days, and run a small user study on scheduled-vs-chosen task timing.

## License

MIT — see [LICENSE](LICENSE). Author: **Azra Bano**.
