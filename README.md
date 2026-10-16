# Parkinson's Freezing-of-Gait Digital Twin

**Digital Twin Challenge 2026 — Happiest Health**

| | |
|---|---|
| **Team** | Team Asha |
| **Institution** | Sir M. Visvesvaraya Institute of Technology (Sir MVIT), Bengaluru |
| **Team leader** | Ashmit Rai |
| **Condition** | Parkinson's disease — freezing of gait (FoG) |
| **Licence** | MIT (see `LICENSE`) |
| **Video demo** | [to be added before submission] |

---

## What this is

A digital twin of freezing of gait (FoG) in Parkinson's disease. The twin
maintains a patient state built from the two data streams the challenge
requires:

- **Static / historical** — demographics, years since diagnosis, UPDRS-III
  (on and off medication), NFOGQ, medication state at recording time.
- **Dynamic / real-time** — continuous tri-axial lower-back accelerometry,
  including approximately one week of uninterrupted 24/7 home recording per
  patient.

Two readouts are taken from that patient state (`docs/02_twin_spec.md`, §4):

1. **Adverse-event prediction — the readout the challenge asks for.** The
   probability that a freezing episode begins within a short horizon,
   evaluated from 0.5 to 5 s and reported at 2.0 s. The submitted model (C)
   reaches roughly 2.5× the prevalence floor at 2.0 s. That is above chance
   and not deployable: performance degrades with lead time, no operating
   point keeps the alarm off for most of the monitored time, and all four
   personalisation mechanisms tested were null. Operating points and
   limitations are in `RESULTS.md`.
2. **Concurrent freezing-burden estimation.** How much a patient is freezing
   now, estimated from movement the model has not seen from that patient. The
   burden estimator is movement-only: arm A, accelerometry alone. This
   is the readout with the stronger validation: on 31 held-out patients,
   Spearman ρ = 0.51 (p = 0.003) and Pearson r = 0.65 (p = 0.0001), while the
   standard NFOGQ questionnaire does not reach significance in the same cohort
   (r = 0.35, p = 0.051). The estimate keeps independent signal after
   controlling for NFOGQ (r = 0.61, p = 0.00035) and activity level (r = 0.66,
   p = 0.00008). Final values are in `RESULTS.md`.

These are two outputs of the twin's patient-state design, not competing
results. They come from different arms of the same ablation: the forecasting
result is measured on model C, and the burden estimate on the movement-only
arm A. The reconstruction of the burden block is recorded in
`docs/06_provenance.md`.

The submitted model is **Model C**: a fusion of the patient's movement history,
static clinical state, and continuous accelerometry. Model C is submitted even
though it does not outperform the accelerometry-only arm (A) in the ablation,
because it is the only arm that uses both required data streams, static
clinical state and dynamic accelerometry, and the challenge requires
two-stream fusion.

| Result | Model | Evaluation |
|---|---|---|
| Adverse-event prediction (FoG onset, 2 s horizon) | C — accelerometry + personal baseline + clinical state | out-of-fold, subject-level GroupKFold, 6 folds, 3 seeds |
| Burden estimation | A — accelerometry only, seed-averaged over 3 seeds | out-of-fold, patient-level, n = 31, over the 2.0 s evaluation mask |

The burden estimate is a mean predicted risk and the observed rate is a
positive-window fraction: different quantities on different scales, so the
reported association is rank-based.

![Held-out burden estimation](figures/fig5_burden_estimation.png)

### Burden-estimation caveats

- This is concurrent estimation, not prospective forecasting: the twin
  estimates how much a patient is freezing now from movement it has not seen
  from that patient. It does not predict future burden.
- The result is correlational, from one cohort of 31 patients, with no external
  validation.
- Statistical inference treats the 31 patients as the independent units (one
  estimate and one observed rate per patient), not the individual windows;
  `scripts/burden_analysis.py` recomputes every burden statistic from those 31
  per-patient rows.
- Spearman is the headline statistic because Pearson is leverage-sensitive:
  excluding the single highest-burden patient gives r = 0.387 (p = 0.035).
  Across all single-patient deletions r spans 0.387–0.712 and remains
  significant.

## Presentation and architecture

- [Submission deck (PDF)](docs/deck.pdf) — 10 slides.
- [Twin architecture (PDF)](docs/architecture.pdf) — four state layers, the
  latent state, and the two readouts.

## Why this is a twin and not a classifier

This is the question the design is built to answer, so we answer it first.

A conventional FoG model maps an accelerometer window to a label. It treats
every patient as the same patient.

Our model conditions each prediction on **that individual's own motor
baseline**, derived from their week of unlabelled home recording, so what the
model sees is not raw movement but *deviation from this person's normal*:

```
Deviation_i(t) = ObservedState_i(t) - PersonalBaseline_i
```

The baseline comes from the `daily` cohort, which carries **no FoG labels at
all**. Personalisation therefore cannot leak the target — the twin's patient
representation is learned from data that contains no answers.

We report an ablation (raw encoder → + deviation → + clinical state) so the
contribution of the twin's state representation is measured, not asserted.

## Adverse-event prediction — episode forecasting

At time *t*, using only information available at *t*, estimate the probability
of FoG onset within a horizon *h*.

We report performance **as a function of *h*** across 0.5–5 s. This readout
remains weak, at roughly 2–3× chance; four personalisation mechanisms
were tested and all four were null. Full values are in `RESULTS.md`.

Full specification, including leakage rules: `docs/03_data_and_target.md`.

## What the twin does NOT claim

Stated up front rather than buried. The twin does not claim:

- to reproduce the patient's whole physiology;
- that a predicted episode will certainly occur;
- that it forecasts future burden;
- that it prevents falls;
- that the warning horizon has been shown to improve clinical outcomes;
- that any cross-cohort patient identities are linked;
- that synthetic or derived components constitute clinical evidence.

Extended version: `docs/02_twin_spec.md`, §7.

## Documentation

| Document | Contents |
|---|---|
| `docs/01_problem.md` | Clinical problem, why FoG, relevance to India |
| `docs/02_twin_spec.md` | Patient-state model, state layers, boundaries |
| `docs/03_data_and_target.md` | Dataset roles, linkage, target, leakage rules |
| `docs/00_workflow.md` | **Start here** — decisions, pipeline, results, remaining work |
| `docs/04_evidence_matrix.md` | Every claim with its evidence class and source |
| `docs/06_provenance.md` | Which payload values are reproduced from the notebooks, and which are open |

Every substantive claim is traceable in `docs/04_evidence_matrix.md`, labelled
VERIFIED — DATA, VERIFIED — LITERATURE, PREPRINT, INFERRED, ASSUMED, SYNTHETIC
or UNKNOWN, with its source. Nothing is stated more strongly than its evidence
supports.

## Technical stack

- Python, PyTorch
- 1D temporal convolutional encoder over raw tri-axial accelerometry
- Fusion head over three branches: window encoder, personal-baseline deviation
  vector, static clinical state
- Evaluation: subject-level `GroupKFold` — no subject appears in more than one
  fold
- Dashboard: a single self-contained HTML page (`dashboard/index.html`). The
  canonical payload is embedded at build time, so the page needs no network
  request, no server and no `fetch()`.

## Data

All data are open-source and used under their published terms. No real patient
data were collected by this team. Dataset provenance and cohort structure are
documented in `docs/03_data_and_target.md`.

## Repository layout

```
Team Asha_Sir MVIT/
├── README.md                 this file — submission entry point
├── CLAUDE.md                 working rules for contributors
├── LICENSE                   MIT
├── RESULTS.md                generated results summary (from twin_data.json)
├── docs/
│   ├── 00_workflow.md        start here — decisions, pipeline, status
│   ├── 01_problem.md
│   ├── 02_twin_spec.md
│   ├── 03_data_and_target.md
│   ├── 04_evidence_matrix.md
│   ├── 06_provenance.md      what is reproduced from the notebooks, what is open
│   ├── architecture.pdf      twin architecture diagram
│   └── deck.pdf              submission deck
├── dashboard/
│   ├── README.md
│   ├── index.html            self-contained dashboard (built)
│   ├── _template.html        dashboard UI template
│   ├── twin_data.json        canonical results payload
│   └── synthetic_patient.json
├── figures/
│   ├── fig1_horizon_curve.png
│   ├── fig2_per_patient.png
│   ├── fig3_operating_point.png
│   ├── fig4_personalisation_nulls.png
│   └── fig5_burden_estimation.png
├── notebooks/
│   ├── README.md
│   ├── 02_preprocessing.ipynb
│   └── 04_model_seeds.ipynb
└── scripts/
    ├── build_dashboard.py
    ├── burden_analysis.py
    ├── export_signal_snippets.py
    ├── make_results.py
    ├── make_synthetic_patient.py
    ├── merge_signal_fragment.py
    └── reconstruct_burden.py
```

## Reproducing

The pipeline runs on Kaggle, where the dataset is hosted.

1. `notebooks/02_preprocessing.ipynb` — harmonisation, event-alignment audit,
   window generation, daily-baseline profiling, deviation features.
   Run as **Save & Run All (Commit)**, GPU T4. ~1.5 h.
2. `notebooks/04_model_seeds.ipynb` — multi-seed ablation. Add the output of
   step 1 as an input dataset. ~45 min.

Outputs land in `/kaggle/working` and are bundled as `asha_outputs.zip`.

## Dashboard build

The committed `dashboard/index.html` is self-contained and works when opened
directly with `file://`; evaluators do not need a server or build step. To
regenerate it after changing the canonical data:

1. `python3 scripts/make_synthetic_patient.py`
2. `python3 scripts/build_dashboard.py`

The build embeds `dashboard/twin_data.json` and the clearly labelled synthetic
demo patient. The synthetic record is asserted to be absent from all reported
cohort statistics.
