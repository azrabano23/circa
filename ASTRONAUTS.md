# Circa for astronauts — circadian alignment as a flight-safety countermeasure

> Branch: `astronauts`. This is the NASA SpaceTech line of Circa (the project that
> won **1st place nationally** at the NASA SpaceTech pitch competition, Fall 2025,
> with a grant to continue development).

## The problem

On the International Space Station the crew sees **16 sunrises and sunsets per
day**. The human circadian clock — the thing that decides when you're alert and
when you're useless — can't entrain to that, so without intervention it drifts.
When the **core-body-temperature minimum (CBTmin)**, the body's clock hand, wanders
out from under the sleep block, the crew is doing high-stakes work at the wrong
biological time. Circadian misalignment in spaceflight is documented to worsen
sleep and *increase sleep-medication use* ([Flynn-Evans et al., npj Microgravity
2016](https://www.nature.com/articles/npjmgrav201519)). On a lunar or Mars transit
there is no ground crew to catch a foggy mistake — alignment is a safety system.

## Where the data actually comes from (the inputs)

NASA never reads the clock directly; it **infers** it from wearables. Each ISS
crew member wears an **Actiwatch Spectrum** on the non-dominant wrist, logging in
1-minute epochs:

- **activity** (accelerometer) → rest/wake, and
- **ambient light** (color photodiodes) → the zeitgeber driving the clock.

Core body temperature is captured separately (e.g. ESA's non-invasive **Thermo-Mini**
headband). From actigraphy + photometry NASA estimates each astronaut's **CBTmin**
using its *Circadian Performance Simulation Software*. This is not hypothetical —
actigraphy + photometry have been collected on **21 astronauts over 3,248
mission-days** ([NASA, Wearable Tech for Space Station Research](https://www.nasa.gov/missions/station/iss-research/wearable-tech-for-space-station-research/);
[NASA LSDA: Lighting Effects](https://lsda.jsc.nasa.gov/Experiment/exper/13815)).

So Circa's astronaut inputs are exactly those signals: **wrist actigraphy + light
+ core temperature → estimated CBTmin → predicted alertness**.

## What this module does (`missions/astronaut.py`)

A dependency-free model of that loop on synthetic-but-realistic data:

1. **`synth_core_temp`** — generates the core-temperature signal a wearable would
   log for a given CBTmin (minimal at CBTmin, peaking ~12 h later).
2. **`estimate_cbtmin`** — recovers CBTmin from noisy samples by fitting a 24 h
   sinusoid (closed-form single-harmonic fit), the spirit of NASA's estimation.
   Tested to recover a known CBTmin within ~18 minutes from clean data and within
   an hour under wearable-grade noise.
3. **`simulate_mission`** — evolves CBTmin day-by-day under a **light policy**,
   using a simplified light **phase-response curve** (morning light advances the
   clock, evening light delays it).
4. **`benchmark_astronaut.py`** — runs the same 14-day mission with uncontrolled
   evening light vs. an engineered, closed-loop light countermeasure, and scores
   on-shift alertness.

## Result

`python -m missions.benchmark_astronaut` (14-day mission, 09:00–17:00 work block):

| Light policy | Final CBTmin | Phase drift | Mean on-shift alertness |
|---|---|---:|---:|
| Uncontrolled (evening module light) | 09:58 | **4.97 h** | 0.61 |
| Circadian countermeasure | 05:00 | **0.00 h** | **0.76** |

The countermeasure **holds CBTmin under the sleep block and recovers +25% on-shift
alertness** over a two-week mission. Both crews fly the identical schedule; only the
light policy differs, so the gap is attributable purely to circadian engineering —
NASA's countermeasure thesis, reproduced in miniature.

**Honest scope.** This is a *model-internal* result on synthetic data: it
demonstrates the mechanism (recover phase from wearable signals → keep it aligned →
protect alertness), not a flight outcome. The phase-response curve is a simplified
single-harmonic model, not NASA's full simulation. The natural next steps are
calibrating against the published actigraphy/photometry distributions and adding a
melatonin/light-dose model.

## Run it

```bash
python -m missions.benchmark_astronaut        # uncontrolled vs countermeasure
pytest tests/test_astronaut.py -q             # 6 tests: CBTmin recovery, drift, countermeasure
```

## References

- Flynn-Evans, E. et al. (2016). *Circadian misalignment affects sleep and medication use before and during spaceflight.* npj Microgravity 2, 15019.
- NASA. *Wearable Tech for Space Station Research* (Actiwatch Spectrum).
- NASA Life Sciences Data Archive — *Lighting Effects* experiment (ISS circadian lighting).
