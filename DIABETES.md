# RhythmRX — chronotherapy for diabetes

> Branch: `diabetes`. The chronotherapy engine behind **RhythmRX**: a low-cost way
> to measure a patient's circadian phase and time their diabetes medication to it.

## The problem

Insulin sensitivity and glucose tolerance are under circadian control — the body's
ability to handle glucose, and to use a drug that helps, rises and falls across the
biological day ([Stenvers et al., *Nat Rev Endocrinol* 2019, "Circadian clocks and
insulin resistance"](https://www.nature.com/articles/s41574-018-0122-1); [Marcheva
et al.; reviews in *Front. Endocrinol.* 2023](https://www.frontiersin.org/journals/endocrinology/articles/10.3389/fendo.2023.1156757/full)).
"Chronotherapy" means dosing in step with that rhythm.

The catch: **nobody measures *your* rhythm.** The clinic says "take it with
breakfast" — a fixed clock time that assumes every patient's clock is identical and
entrained to a 9-to-5. The people for whom that's most wrong are shift workers, late
chronotypes, and the sleep-disrupted — whose clocks are *shifted*, and who therefore
get the least from a one-size-fits-all dosing time. Globally that's a large
population: the IDF counts **~537 million adults with diabetes**.

## Where the data comes from (the input)

The practical, cheap circadian phase marker is **salivary cortisol**, which peaks
shortly after waking and declines across the day. From a few timed saliva samples —
the RhythmRX "spit strip", morning / afternoon / evening — we fit the cortisol
rhythm and recover the patient's circadian **phase**. On Earth that estimate can be
sharpened with consumer wearables (Apple Watch / Fitbit sleep, skin temperature,
heart-rate rhythm) and continuous glucose-monitor data — i.e. the same sensing layer
[Circa](README.md) uses, pointed at a clinical endpoint.

## What this module does (`missions/rhythmrx.py`)

1. **`estimate_circadian_phase`** — least-squares fit of the cortisol rhythm from a
   few *daytime-only* saliva samples → the patient's phase. (Tested to recover a
   known phase from sparse samples.)
2. **`insulin_sensitivity`** — a circadian sensitivity curve anchored to that phase
   (higher in the biological day, lower in the evening — the shape behind documented
   evening glucose intolerance).
3. **`optimal_dose_time`** — the once-daily dose time that best matches the drug's
   action window to the patient's sensitivity rhythm.
4. **`simulate_day` / `benchmark_rhythmrx.py`** — simulate a day of meals + medication
   and score the hyperglycemia burden (glucose area over 140 mg/dL), comparing the
   clinic's fixed time against the personalized time.

## Result

`python -m missions.benchmark_rhythmrx` — a **phase-delayed patient** (cortisol peak
~11:00), identical day of meals, once-daily medication:

| Dosing strategy | Dose time | Hyperglycemia AUC | Time in range |
|---|---|---:|---:|
| Clinic default ("with breakfast") | 08:00 | 192 | 56% |
| **RhythmRX personalized** | 12:00 | **102** | **74%** |

Timing the dose to *this* patient's measured rhythm cuts the hyperglycemia burden
**~47%** and lifts time-in-range from 56% to 74% — same drug, same dose, different
hour. The benefit comes precisely from the patient being phase-shifted, which the
clinic's fixed time can't see because it never measured the rhythm.

## Real-data evidence (ShanghaiT2DM — 100 real patients)

The simulation above is the *mechanism*. The **evidence that the mechanism is real**
comes from the [ShanghaiT2DM dataset](https://doi.org/10.1038/s41597-023-01940-7)
(Zhao et al., *Sci Data* 2023): 15-minute CGM over 3–14 days for **100 real type-2
patients** with timestamped meals and medication. `scripts/analyze_shanghai.py`
runs `missions/real_analysis.py` over **all 109 recording sessions / 112,462 real
CGM readings**:

| Finding (real patients) | Value |
|---|---|
| Mean glucose | 140 mg/dL |
| Time in range (70–180) | 79% |
| **Dawn phenomenon** (overnight trough → 08:00) | **+55 mg/dL** |
| Daily glucose swing (peak hour − trough hour) | 55 mg/dL |
| **Spread of each patient's personal glucose-peak time** | **σ = 3.1 h, range 02:00–23:30** |

Two things matter. First, glucose in real patients is **strongly circadian** — the
textbook dawn phenomenon (glucose climbing ~55 mg/dL into the morning before a bite
of breakfast) falls straight out of the data. Second, and decisively for RhythmRX:
**each patient's peak time is different**, spread across the *entire clock* (σ 3.1 h).
That is the quantitative death of "take it the same time as everyone" — there is no
universal best hour, so a tool that doesn't measure *your* rhythm is guessing for most
people. This is the real-world signal the personalized-dosing model exploits.

```bash
pip install -e ".[data]"                 # pandas + xlrd for the .xls files
python scripts/analyze_shanghai.py       # downloads ~3.7 MB once, then analyzes 100 patients
```

## Honest framing

The circadian regulation of glucose, and the *direction* of the chronotherapy
effect, are well established. The **magnitude** this simulator reports is
**model-internal and illustrative** — not a clinical result — and some widely
quoted single-trial percentages in this field (e.g. specific bedtime-dosing
cardiovascular figures) are **contested or under review**, so they are deliberately
not asserted here. RhythmRX's claim is the robust one: *dosing to the individual's
measured rhythm beats a fixed clock time, most for the people whose clocks are
shifted.* This is decision support; it does not replace a clinician or a trial.

## The product this engine powers

RhythmRX packages the engine as a **$5 cortisol spit-strip + app**: spit three times
in a day, scan with your phone, and the app estimates your rhythm and tells you when
to take your medication — with an optional wearable band for adherence reminders and
the same phase data unlocking sleep/focus/fertility-window insights. The health-equity
case is the point (UN **SDG 3** good health, **SDG 10** reduced inequality): precision
chronotherapy today means a $10k concierge workup; a $5 strip democratizes it.

## Run it

```bash
python -m missions.benchmark_rhythmrx       # clinic-default vs personalized dosing
pytest tests/test_rhythmrx.py -q            # 6 tests: phase recovery, sensitivity, dosing
```

## References

- Stenvers, D.J. et al. (2019). *Circadian clocks and insulin resistance.* Nature Reviews Endocrinology 15, 75–89.
- *The circadian rhythm: an influential soundtrack in the diabetes story.* Front. Endocrinol. (2023).
- International Diabetes Federation, *IDF Diabetes Atlas* (10th ed.) — global prevalence.
