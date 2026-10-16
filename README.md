# Parkinson's Freezing-of-Gait Digital Twin

**Happiest Health Digital Twin Challenge 2026**

A personalised, time-evolving computational representation of a Parkinson's
patient's motor and freezing-of-gait state, built from two linked data streams
and read out as a clinical-decision-support dashboard.

---

## Team details

| | |
|---|---|
| **Team name** | Team Asha |
| **Team leader** | Ashmit Rai |
| **Team member** | Krishnaditya Prakash|
| **Contact** | ashmitrai1706@gmail.com |

## College / Incubator information

**Sir M. Visvesvaraya Institute of Technology (Sir MVIT), Bengaluru, Karnataka, India**
Department of Data Science.
No incubator affiliation.

## Project title

**A Digital Twin for Freezing of Gait in Parkinson's Disease**

## Problem statement

> We estimate an individual Parkinson's patient's evolving motor and
> freezing-of-gait state from their clinical history and continuously observed
> real-world movement, and use that personalised state to predict impending
> freezing episodes with sufficient advance warning for intervention.

Freezing of gait (FoG) is a brief, episodic inability to produce effective
forward stepping despite the intention to walk. It occurs at gait initiation,
during turning, when approaching a destination, in narrow spaces, and under
cognitive or dual-task load. It is associated with falls, impaired mobility,
functional dependency and reduced quality of life, and becomes more prominent
with disease duration and severity.

Reported prevalence varies considerably with the population studied and the
assessment method used, so **no single prevalence figure is quoted anywhere in
this repository** — the literature does not support one.

## Healthcare use case

**The gap: there is no objective measure of how often a given patient freezes
in their own life.**

A movement-disorder neurologist sees the patient for roughly twenty minutes
every three to six months, usually in the ON state, in a wide corridor, with no
dual-task load and no doorways — precisely the conditions under which freezing
is least likely to appear. The clinician therefore relies on three sources:
direct observation (wrong context, wrong time), patient and carer report
(recall-limited, arrives as an impression rather than a quantity), and the
NFOGQ questionnaire (validated, but a single retrospective self-report number
insensitive to change over the intervals that matter).

Freezing burden is the input to several real decisions: whether levodopa dose
and timing are adequate or freezing is breaking through at end-of-dose; whether
to escalate to adjunct medication, physiotherapy and cueing referral, or a DBS
discussion; how to stratify fall risk, which drives home modification, gait
aids and carer education; and, after any intervention, whether it worked.

Each of those currently rests on a questionnaire score and an anecdote.

**Relevance to India.** Community-based prevalence estimates for Parkinson's
disease in India vary widely by region, case definition and age adjustment. The
largest general-population survey — a door-to-door study of 100,802 people in
Kolkata (2003–2007) — reported an age-adjusted prevalence of 52.85 per 100,000
(World Standard Population).¹ Estimates rise steeply with age and India's
population is ageing rapidly. FoG is episodic and context-dependent, and is
systematically under-detected in short, infrequent specialist appointments;
where movement-disorder specialists are few relative to population, continuous
monitoring addresses a real access gap rather than duplicating an existing
service.

¹ Das SK, Misra AK, Ray BK, et al. *Epidemiology of Parkinson disease in the
city of Kolkata, India: a community-based study.* Neurology.
2010;75(15):1362–1369. doi:10.1212/WNL.0b013e3181f735a7

## Technical stack

- **Language / framework** — Python, PyTorch
- **Data processing** — NumPy, pandas, SciPy, pyarrow
- **Evaluation** — scikit-learn (`GroupKFold`, `average_precision_score`)
- **Compute** — Kaggle notebooks, NVIDIA T4 GPU
- **Dashboard** — a single self-contained HTML page (`dashboard/index.html`).
  The canonical data payload is embedded at build time, so the page needs no
  server, no CDN, no remote fonts and no network request. It opens directly
  from `file://`.
- **Source data** — TLVMC Parkinson's Freezing of Gait dataset (Kaggle),
  open-source and used under its published terms. The dataset is **linked, not
  redistributed**; no real patient data were collected by this team.

## AI/ML model or framework details

**Architecture.** A 1-D temporal convolutional encoder over raw tri-axial
accelerometry, with a fusion head over up to three branches.

- Encoder: four Conv1d blocks (channels 3→32→64→96→128; kernels 7, 5, 5, 3;
  stride 2 each), each with BatchNorm and GELU, then adaptive average pooling.
- Side branch: a linear projection of the personal-baseline and clinical-state
  vectors into 64 dimensions.
- Head: 128 → 128 → 8 logits, one per prediction horizon, with dropout 0.3.
- Loss: **masked binary cross-entropy** — each horizon head learns only from
  its own positives plus clean (> 10 s) negatives.

**Input.** 4-second windows of lower-back tri-axial accelerometry at 100 Hz,
advanced on a 0.5 s stride. `tdcsfog` recordings are harmonised 128 → 100 Hz
and m/s² converted to g; **labels are index-mapped, never resampled**.

**Personal baseline — 11 dimensions.** The mean of each of ten movement
features over the subject's week of unlabelled home recording, plus
`activity_fraction`. Because this baseline is computed from a cohort carrying
**no FoG labels at all**, personalisation cannot leak the prediction target.

**Ablation arms.**

| Arm | Inputs |
|---|---|
| A | accelerometry only |
| B | A + personal baseline + deviation |
| C | A + personal baseline + deviation + static clinical state |

**Evaluation.** Subject-level `GroupKFold`, **6 folds** — no subject appears in
more than one fold, asserted in code. Results are averaged over **3 seeds**
(0, 1, 2). Cohort: **36 patients, 45,224 windows**.

**We never report accuracy.** At an event prevalence of roughly 4.6%, a model
that predicts "never freezes" is about 95% accurate and useless. We report
AUPRC against prevalence as the chance baseline.

---

## Results

### Which model produces which result

| Result | Model | Evaluation |
|---|---|---|
| **Adverse-event prediction** (FoG onset, 2 s horizon) | **C** — accelerometry + personal baseline + clinical state | out-of-fold, subject-level GroupKFold, 6 folds, 3 seeds |
| **Burden estimation** | **A** — accelerometry only, seed-averaged | out-of-fold, patient-level, n = 31, over the 2.0 s evaluation mask |

### Primary readout — freezing-burden estimation (n = 31)

The movement-derived estimate tracks each patient's held-out observed freezing
rate better than the standard questionnaire does **in this cohort**:

| | |
|---|---|
| Spearman ρ | **0.514** (p = 0.0031) — headline statistic |
| Pearson r | 0.645 (p = 9 × 10⁻⁵) |
| NFOGQ questionnaire alone | 0.353 (p = 0.051, **not significant**) |
| Partial r, controlling activity level | 0.658 |
| Partial r, controlling NFOGQ | 0.609 |

**What ρ = 0.514 buys.** A ranking instrument, not a measuring one. It can
answer *which of my patients freeze most, and is this one getting worse*. It
cannot answer *this patient froze twenty-three times last week*. Triage and
change-detection, not quantification.

**Leverage caveat, stated here rather than left to be found.** Pearson is
leverage-sensitive: excluding the single highest-burden patient gives
r = 0.387 (p = 0.035). Across all 31 single-patient deletions r spans
**0.387–0.712**, worst-case p = 0.035. The association holds in every refit,
but how strong it looks depends noticeably on who is in the sample. That is
why Spearman is the headline and why we report a range rather than a point
estimate.

### Secondary readout — short-horizon episode forecasting

AUPRC as a function of warning horizon, model C, seed-averaged, against
prevalence as the chance baseline:

| Horizon (s) | AUPRC (C) | Prevalence | SD across seeds |
|---:|---:|---:|---:|
| 0.5 | 0.1396 | 0.0495 | 0.0179 |
| 1.0 | 0.1354 | 0.0489 | 0.0175 |
| 1.5 | 0.1261 | 0.0477 | 0.0177 |
| **2.0** | **0.1158** | **0.0460** | **0.0155** |
| 2.5 | 0.1096 | 0.0444 | 0.0146 |
| 3.0 | 0.1038 | 0.0423 | 0.0141 |
| 4.0 | 0.0919 | 0.0377 | 0.0119 |
| 5.0 | 0.0834 | 0.0338 | 0.0091 |

Roughly 2.5 times chance at the 2 s horizon, decaying with lead time. **This
readout is weak and we report it as weak.**

### Four personalisation mechanisms tested, all four null

| Mechanism | Change | Wins |
|---|---:|---:|
| Clinical fusion (C vs A) | −0.0023 | 50/144 |
| Personal baseline (B vs A) | −0.0120 | 46/144 |
| Per-patient threshold | −0.0005 | 11/20 |
| LOSO shrinkage | −0.0105 | 8/20 |

Model ordering: **A ≈ C > B**. Seed-to-seed spread for arm C is **0.0295** — an
order of magnitude larger than the 0.0023 effect of adding clinical data. Even
if fusion helped, we could not detect it at this sample size.

The personalisation branches are the twin's design rationale. Whether they
improve prediction is an empirical question; we tested it four ways and report
all four results.

### What an alarm would cost the patient

| Recall target | Time in alarm state | Precision |
|---:|---:|---:|
| 30% | 10.6% | 0.127 |
| 50% | 19.5% | 0.114 |
| 70% | 33.3% | 0.094 |

These are **recall targets, not score thresholds**. No operating point tested
is clinically viable: even the most permissive leaves the alarm active for
roughly one minute in ten at a precision of 0.127. Evaluation is on
FoG-provoking protocol segments, not free-living monitoring.

### Heterogeneity

9 of 27 evaluated patients fall below twice their own event rate at the 2.0 s
horizon. Per-patient optimal thresholds span 0.106 to 0.9998. The model does
not transfer uniformly across patients.

---

## Demo video

**[LINK — unlisted YouTube, 15–20 minutes, to be added before submission]**

## Open-source license details

**MIT License** — see [`LICENSE`](LICENSE).

All source code, documentation, figures and the dashboard in this repository
are released under the MIT License. The TLVMC Parkinson's Freezing of Gait
dataset is **not** redistributed here; it is used under its own published terms
and linked from [`notebooks/README.md`](notebooks/README.md).

## Architecture diagram

**[`docs/Twin_architecture.pdf`](docs/Twin_architecture.pdf)** — four state
layers feeding one latent patient state, with both readouts drawn from it.

## Presentation

**[`docs/Team_Asha_Deck.pdf`](docs/Team_Asha_Deck.pdf)** — project details and
outcomes.

## Accessibility

All files and links in this repository are publicly accessible without
additional permissions. The repository is public, the dashboard opens directly
in a browser from `file://` with no server or build step, and the demo video is
an unlisted YouTube link requiring no sign-in.

---

## Why this is a twin and not a classifier

A conventional FoG model maps an accelerometer window to a label. It treats
every patient as the same patient.

The twin conditions each judgement on **that individual's own motor baseline**,
derived from their week of unlabelled home recording, so what the model sees is
deviation from this person's normal:

```
Deviation_i(t) = ObservedState_i(t) − PersonalBaseline_i
```

For an identical raw reading, one patient may be far outside their normal while
another is exactly at theirs. A classifier cannot tell those two situations
apart.

The baseline comes from the `daily` cohort, which carries **no FoG labels at
all**, so personalisation cannot leak the prediction target. Whether it
improves prediction is reported above — honestly, including the nulls.

## Data

Four cohorts from the TLVMC Parkinson's Freezing of Gait dataset:

| Cohort | Subjects | Files | Role |
|---|---:|---:|---|
| `tdcsfog` | 62 | 833 | Lab, 128 Hz, m/s². **Not used in the reported models** — no tdcsfog subject has a personal baseline |
| `defog` | 45 | 91 | Lab, 100 Hz, g, with Valid/Task masks. Evaluation arm |
| `notype` | — | 46 | Generic event labels only |
| `daily` | 65 | — | ~1 week continuous, **unlabelled**. Source of the personal baseline |

**Verified linkage:** daily ∩ clinical 65/65; daily ∩ defog 36; **31 exact
Subject × Visit matches** with clinical, defog and daily data on the same
person at the same visit. **Zero** subjects span `tdcsfog` and the paired
clinical cohort. Other public datasets offered no patient-level link, so we did
not fuse them — merging would invent patients.

Label-alignment agreement: 97.0%, with 74 discrepancies all accounted for.

**Visit 1 precedes Visit 2, and the elapsed interval is undocumented in this
dataset.** No duration is ever attached to the longitudinal layer anywhere in
this project.

## What the twin does NOT claim

- It does not diagnose Parkinson's disease, and is not clinically validated,
  approved or trial-ready.
- It does not prevent falls, and has not been shown to improve any clinical
  outcome.
- Burden estimation is a **concurrent estimate, not a forecast** — it describes
  the week just recorded, not the month ahead.
- Ground truth is lab-derived, not home-derived; the home cohort carries no
  labels.
- The dashboard's body figure is a schematic state indicator keyed to model
  risk, never reconstructed limb motion. A single lower-back IMU cannot recover
  joint kinematics.
- No patient identities are merged across datasets.
- No synthetic or derived component constitutes clinical evidence. The
  dashboard's synthetic demonstration patient is visibly labelled SYNTHETIC and
  is asserted in the build script to be absent from every reported statistic.
- Online state updating is specified in `docs/02_twin_spec.md` but is **not
  implemented** in this prototype: the encoder is feed-forward and carries no
  state between windows.

## Documentation

| Document | Contents |
|---|---|
| [`docs/00_workflow.md`](docs/00_workflow.md) | **Start here** — frozen decisions, pipeline, results, remaining work |
| [`docs/01_problem.md`](docs/01_problem.md) | Clinical problem, why FoG, relevance to India |
| [`docs/02_twin_spec.md`](docs/02_twin_spec.md) | Patient-state model, state layers, boundaries |
| [`docs/03_data_and_target.md`](docs/03_data_and_target.md) | Dataset roles, linkage, target definition, leakage rules |
| [`docs/04_evidence_matrix.md`](docs/04_evidence_matrix.md) | Every claim with its evidence class and source |
| [`docs/06_provenance.md`](docs/06_provenance.md) | What regenerates from committed code, and what does not |
| [`RESULTS.md`](RESULTS.md) | Generated from `dashboard/twin_data.json` — do not edit by hand |

Every substantive claim in this repository is labelled with its evidence class
in `docs/04_evidence_matrix.md`. Nothing is stated more strongly than its
evidence supports.

## Reproducing

The pipeline runs on Kaggle, where the dataset is hosted.

1. `notebooks/02_preprocessing.ipynb` — harmonisation, event-alignment audit,
   window generation, daily-baseline profiling, deviation features.
   Run as **Save & Run All (Commit)**, GPU T4. Approximately 1.5 h.
2. `notebooks/04_model_seeds.ipynb` — multi-seed ablation. Attach the output of
   step 1 as an input dataset.

Verification, from the repository root:

```bash
python3 scripts/burden_analysis.py                      # recomputes all 14 burden statistics
python3 scripts/reconstruct_burden.py --artifacts DIR   # rebuilds the 31 per-patient rows
python3 scripts/make_results.py                         # regenerates RESULTS.md
python3 scripts/build_dashboard.py                      # rebuilds dashboard/index.html
```

`*.npy` and `*.parquet` intermediates are gitignored by design and must be
regenerated from the notebooks. See
[`docs/06_provenance.md`](docs/06_provenance.md) for exactly which reported
values regenerate from committed code and which do not.
