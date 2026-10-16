# 00 — Project Workflow and Status

**Team Asha · Sir M. Visvesvaraya Institute of Technology, Bengaluru**
**Digital Twin Challenge 2026 — Happiest Health**

**Status date:** 11 October 2026 · **Submission closes:** 20 October 2026,
06:30 PDT (19:00 IST)

> This document is the single source of truth for what has been decided, what
> has been built, and what remains. `RESULTS.md` is the source of truth for
> reported metrics.

---

## 1. Status at a glance

| Stage | State |
|---|---|
| Condition selection | **FROZEN** — Parkinson's disease, freezing of gait |
| Dataset selection | **FROZEN** — TLVMC Parkinson's FoG (Kaggle) |
| Data audit | **COMPLETE** — label-quality gate passed |
| Preprocessing & windowing | **COMPLETE** — verified by assertion |
| Personal baseline profiler | **COMPLETE** — 36/36 patients |
| Seed-averaged model + ablation | **COMPLETE — FROZEN.** Final run complete; no further modelling. |
| Burden estimation | **COMPLETE** — final held-out analysis. |
| Personalisation experiments | **COMPLETE** — four mechanisms, four nulls. |
| Results figures | **COMPLETE** — 5 PNG + `RESULTS.md`. |
| Dashboard | **COMPLETE** — self-contained offline dashboard built. |
| Synthetic demo patient | **COMPLETE** — visibly labelled and excluded from cohort statistics. |
| Architecture diagram (PDF) | **NOT STARTED** |
| Presentation (PDF/PPT) | **NOT STARTED** |
| 20-minute video | **NOT STARTED** ← critical path |
| Public repo assembled | **COMPLETE** — folder `Team Asha_Sir MVIT`, pushed to a public GitHub repository. |

The dashboard, synthetic demonstration and public repository are complete.
Remaining work is the architecture diagram, presentation and video.

---

## 2. Decisions that are frozen

These are settled. Reopening any of them costs days we do not have.

| # | Decision | Reason |
|---|---|---|
| 1 | Condition is **Parkinson's FoG** | Only candidate where static clinical state, continuous sensor data and a future adverse event exist for the *same* patients in obtainable data |
| 2 | Primary validated output is **concurrent burden estimation** | Acute forecasting is retained as a weak secondary analysis; burden estimation is reported with its caveats in `RESULTS.md` |
| 3 | Longitudinal layer is **exploratory only** | n=25, and the Visit 1 → Visit 2 interval is undocumented |
| 4 | **Model C is the submitted model** | It is the only arm that ingests both required data streams. A and B are ablation arms. Do not ship A because its number is marginally higher — that would fail a stated requirement for a difference inside fold variance. |
| 5 | Positives use a **lead-time band**, not "any onset within h" | Cumulative labelling makes the degradation curve uninterpretable |
| 6 | Onsets come from **class-specific** transitions | `fog_any` merges consecutive typed events into one run |
| 7 | **No cross-cohort patient fusion** (AMP-PD, MIMIC, Telemonitoring) | No patient-level linkage exists; merging would fabricate patients |
| 8 | Synthetic data is permitted for **demonstration only** | Never enters a reported evaluation metric |
| 9 | Label-quality gate is **closed and passed** | 97.0% alignment, all discrepancies explained; no further diagnostics |
| 10 | Modelling is **frozen** | Four mechanisms were tested and all were null |

---

## 3. Data

### 3.1 Cohorts and their roles

| Cohort | Files | Subjects | Rate | Units | Role in the twin |
|---|---|---|---|---|---|
| `tdcsfog` | 833 | 62 | 128 Hz | m/s² | Not used in the reported models. No tdcsfog subject has a personal baseline, so none is in the modelling cohort. |
| `defog` | 91 | 45 | 100 Hz | g | Evaluation arm (with `Valid`/`Task`) |
| `notype` | 46 | — | 100 Hz | g | Evaluation arm, generic `Event` label only |
| `daily` | 65 | 65 | 100 Hz | g | **Unlabelled** personal baseline |

91 + 46 = 137, which reconciles with the 137 defog recordings in the metadata.

Totals: 136 subjects, 1,035 recordings, 3,544 annotated events, 2,817 task
windows.

### 3.2 Verified linkage

| Overlap | Count |
|---|---|
| Daily ∩ Clinical | 65 / 65 subjects |
| Daily ∩ DeFOG | 36 subjects |
| **Daily × DeFOG × Clinical, exact Subject × Visit** | **31** (27 at Visit 1, 4 at Visit 2) |
| Subjects present in all cohorts incl. tdcsfog | **0** |

**Resolved:** the dataset description says 45 daily subjects also have defog
series, "some in the training split and some in the test split." We observe 36;
the other 9 have their defog recordings in the hidden test split. Not a data
problem.

### 3.3 The temporal limitation

**The elapsed time between Visit 1 and Visit 2 is not recorded anywhere.** No
date, timestamp or interval field exists in `subjects.csv`,
`defog_metadata.csv`, `daily_metadata.csv` or `tdcsfog_metadata.csv`. `Time` is
a recording-relative sample index resetting at 0. Recording IDs are
non-temporal hashes.

→ Visit 1 → Visit 2 is an **ordinal ordering with unknown elapsed time**. Never
describe any result as "6-month" or "1-year" prediction.

---

## 4. The pipeline, stage by stage

### Stage 1 — Harmonisation
- tdcsfog resampled 128 → 100 Hz via polyphase (`resample_poly`).
- tdcsfog converted m/s² → g (÷ 9.80665).
- Label columns are **not** resampled. Onset indices are computed at source
  rate and index-mapped, so onset timestamps are never smeared.

### Stage 2 — Label audit *(gate: PASSED)*
- 2,428 / 2,502 event annotations aligned to class-specific label transitions
  within 50 ms (**97.0%**). Mean timing error **0.004 s**.
- The 74 unmatched are explained and are not defects:
  - 38 tdcsfog Turn events — consecutive same-class episodes inside one
    continuous positive run give multiple `events.csv` rows and one 0→1
    transition.
  - ~30 DeFOG — annotation-mask boundaries behaving per dataset semantics.
  - 2 — event timestamps outside the recording range, documented as a footnote.
- **No pipeline change was made to force a 1:1 match**, as that would distort
  the label representation.

### Stage 3 — Window generation
- Window 4 s (400 samples), stride 0.5 s.
- **Onset** = first sample of a contiguous run where a class label goes 0 → 1.
- **Positive for horizon *h*** if the next onset falls in
  `(t + h − 0.25, t + h + 0.25]` — a lead-time band, so each horizon is an
  independent question and bands tile without overlap.
- Horizons: 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0 s.
- **Negatives** sampled only where `Task == True` with no onset within ±10 s.
- `Valid == False` events excluded from positives.
- Each window is stored **once** with its time-to-next-onset; the eight labels
  are derived from that single value.

**Output:** 105,097 windows → 100,923 after per-subject trimming
(defog 37,936 · notype 24,988 · tdcsfog 42,173).

**Verification:** 405 assertions against raw onsets — all pass. No window
contains its own onset.

### Stage 4 — Personal baseline profiler
- Streams 36 daily parquet files (~64 GB) in chunks; only the overlap subjects.
- Per 4 s window, 10 features: magnitude mean/std/abs-deviation, jerk RMS and
  max, mean per-axis std, log power in 0.5–3 Hz (locomotor) and 3–8 Hz
  (FoG-associated), FoG-band ratio, locomotor fraction.
- Baseline = distribution statistics (mean, std, p10, p50, p90) over that
  subject's **active** windows only, plus activity fraction.
- **Result:** 36/36 profiled, zero failures. 151,198–215,999 windows per
  subject = **7.0–10.0 days**. Activity fraction 0.02–0.25 (median ~0.13),
  consistent with 24/7 wear.
- `7b2e84` has a thin baseline (0.02 active) — flag it in the per-patient panel.

> This closes an open evidence-matrix item: daily duration is now
> **VERIFIED — DATA across 36 files**, not 3.

### Stage 5 — Deviation features
`Deviation_i(t) = (window features − that subject's baseline mean) / baseline std`

The baseline comes from **unlabelled** data, so personalisation cannot leak the
target. Baselines are available for the defog and notype subjects; tdcsfog
subjects have none, as expected. Cohort counts are recorded in `RESULTS.md`.

### Stage 6 — Model and ablation
- Shared 1D temporal CNN encoder (3 → 32 → 64 → 96 → 128, stride 2 each),
  global average pool, optional side MLP, **8 sigmoid heads** (one per horizon).
- Masked BCE: head *h* learns only from its own positives and the clean
  (>10 s) negatives. Pre-FoG windows at other lead times are excluded from that
  head — otherwise the negative class mixes "far from FoG" with "near FoG,
  wrong lead time" and the curve stops meaning anything.
- `GroupKFold`, 6 folds, grouped by Subject. Verified: no subject spans folds.
- Arms: **A** accelerometer only · **B** + personal baseline + deviation ·
  **C** + clinical state (Age, Sex, YearsSinceDx, UPDRS-III on/off, NFOGQ,
  medication, with missingness indicators).
- All three run on the same subjects and the same folds.

---

## 5. Results

`RESULTS.md`, generated from the canonical `dashboard/twin_data.json`, is the
sole results record. It reports the horizon curve against its prevalence floor,
the four personalisation nulls, between-patient heterogeneity, and operating
points.

The horizon curve degrades monotonically with increasing lead time. Feature
conditioning, per-patient thresholding, and LOSO shrinkage are all null
results. Patients remain substantially heterogeneous, so a single population
threshold does not fit everyone. The results are not deployable.

`docs/06_provenance.md` records which payload values a fresh run of
`notebooks/04_model_seeds.ipynb` reproduces, including the burden block, and
which remain open because their producing code is not in the repository.

### 5.1 Alarm-rate accounting — known limitation

- **Windows overlap.** Windows are 4 s long at a 0.5 s stride, so one real
  episode spans several consecutive windows. Consecutive threshold crossings
  are therefore not independent alarms, and a per-window count overstates how
  often a patient would be alerted.
- **What the payload reports.** `operating_points` in `twin_data.json` gives
  `pct_time_alarming` and `alarm_episodes_per_hour` at recall targets of 30%,
  50% and 70%. These are recall targets, not score thresholds. Dividing alarming
  windows per hour (`pct_time_alarming` × 7,200 windows/h) by
  `alarm_episodes_per_hour` gives about 5.1, 5.8 and 6.7 windows per episode.
  That is consistent with consecutive crossings having been merged into
  episodes.
- **The grouping rule cannot be verified.** The notebook that produced
  `alarm_episodes_per_hour` was lost. A search of the repo and both notebooks
  found no code that groups crossings into episodes. The merge rule (gap
  tolerance, minimum length, and whether true alarms are included) is
  **unknown**, and every episode-based alarm rate carries this limitation.
  The field remains in the payload but is no longer reported in `RESULTS.md`
  or the dashboard, because its computation cannot be reproduced.
- **Why the old notebook output differed.** The figure cell in
  `02_preprocessing.ipynb` computes per-window "false alarms per hour": false-
  positive windows (`tp·(1−precision)/precision`) divided by masked windows ×
  0.5 s. Its now-cleared output (689 / 1,275 / 2,364) was 4.6×, 5.3× and 6.6×
  the payload's episode rates. It came from an earlier run, so the two are not
  directly comparable beyond that order of magnitude.
- **No operating point is clinically viable.** Even the lowest rate, at 30%
  recall, is an alarm episode roughly every 24 seconds of monitored time, with
  the alarm active for about a tenth of that time. These rates come from
  FoG-provoking protocol segments, not free-living monitoring, and are not
  evidence of deployability.

---

## 6. Rules that must not be broken

**Leakage**
1. Subject-level splits only. Never split by recording.
2. No future information in a window. The window ends at *t*.
3. Personal baselines from `daily` only, within-subject.
4. Normalisation statistics fit on training folds only.
5. No cross-cohort patient identity.
6. Negatives only from `Task == True`.
7. `Valid == False` events excluded from positives.

**Claims**
8. Every claim appears in `04_evidence_matrix.md` with its evidence class, or
   it is not said on camera.
9. PREPRINT / ASSUMED / UNKNOWN qualifiers are spoken aloud.
10. Never quote a single FoG prevalence figure.
11. Never describe the longitudinal layer with a time interval.
12. Synthetic content is labelled SYNTHETIC in the UI and in the docs, and
    never enters a reported metric.
13. Never report accuracy. Report AUPRC against prevalence, and the operating
    point as percentage of monitored time in an alarm state, not raw false
    alarms per hour. Caveat that evaluation is on FoG-provoking protocol
    segments, not free-living monitoring.

---

## 7. Remaining work

| Date | Deliverable | Owner | Blocks |
|---|---|---|---|
| **12 Oct** | Dashboard — patient state, personal baseline vs deviation, live risk trace, FoG burden, longitudinal visit trajectory | Ayush | video |
| **12 Oct** | Synthetic demo patient (EHR with labs, genetic markers, past diagnoses, two visits) | Ayush | dashboard |
| **13 Oct** | Architecture diagram → PDF | — | repo, deck |
| **13 Oct** | Indian Parkinson's burden statistic, sourced | — | deck, `01_problem.md` §7 |
| **14 Oct** | Repo assembled: `Team Asha_Sir MVIT`, README filled, docs updated with real numbers, MIT LICENSE, notebooks split into `02_` and `04_` | Ayush | — |
| **15–16 Oct** | Presentation PDF | Ashmit | video |
| **17 Oct** | Video script + rehearsal | Ashmit | — |
| **18 Oct** | Record the 20-minute video | both | — |
| **19 Oct** | **Submit** (one day of buffer) | Ashmit | — |

### Submission checklist (from the brief)

- [ ] Team details and college information
- [ ] Project title
- [ ] Problem statement and healthcare use case
- [ ] Technical stack, AI/ML model details
- [ ] **Minimum 20-minute video** explaining and demonstrating the prototype
- [x] Open-source licence details
- [ ] **Architecture diagram** in PDF/PPT *(separate file from the deck)*
- [ ] **Presentation** in PDF/PPT
- [x] **Conceptual UI dashboard**
- [x] Folder named `Team Asha_Sir MVIT`
- [ ] Repository public, all links accessible *(public and pushed; video link still to add)*
- [ ] Submit team leader's name, phone, email and the repo link

---

## 8. Narrative — how the result is presented

The twin maintains one patient state from the two required streams and is
read out in two ways (`docs/02_twin_spec.md`, §4). Present them in this order.

**Readout 1 — adverse-event prediction, the output the challenge asks for.**
FoG onset within a short horizon, reported at 2.0 s for the submitted model C:
roughly 2.5× the prevalence floor, degrading with lead time, with no
clinically usable operating point and four null personalisation mechanisms.
State it as measured; the exact values are in `RESULTS.md`.

**Readout 2 — concurrent burden estimation, the better-validated output.** The
movement-only estimator tracks a patient's current FoG burden on held-out
patients, while the standard NFOGQ questionnaire does not reach significance in
the same cohort. It retains independent signal after adjustment for NFOGQ and
activity level. The exact statistics are in `RESULTS.md`.

These are two readouts of the twin's state design, not competing results. Say
so, and say which arm each comes from: forecasting from the submitted model C,
burden estimation from the movement-only arm A. They are not the same trained
model.

This is **concurrent estimation, not prospective forecasting**: the twin
estimates how much a patient is freezing now from movement it has not seen from
that patient. It does not predict future burden. The result is correlational,
from one held-out cohort, with no external validation; the cohort size is in
`RESULTS.md`. Pearson is leverage-sensitive to one high-burden patient;
Spearman and the leave-one-patient-out analysis are stable and significant for
every single-patient deletion. The exact robustness range is in `RESULTS.md`.

Episode forecasting remains weak. The horizon curve degrades with increasing
lead time, and all four personalisation mechanisms are null. Those results are
reported honestly in `RESULTS.md`; they are not hidden behind the burden result.

The submission still demonstrates the required two-stream twin: continuous
accelerometry is fused with clinical state and each patient's movement history.

---

## 9. Known risks

| Risk | Severity | Mitigation |
|---|---|---|
| Dashboard and video not started; both mandatory | **High** | Start dashboard 12 Oct; hand deck and script to Ashmit in parallel |
| Non-technical jurors read four nulls as "nothing worked" | **High** | Frame burden estimation as the primary result in §8 |
| Absolute performance is weak | Medium | Report against prevalence and as % of monitored time in an alarm state; never quote accuracy |
| India relevance still unsourced | Medium | One sourced statistic, half a day |
| Kaggle session loss | Medium | Use Save & Run All (commit), download `asha_outputs.zip` immediately |
| 2 s horizon vs brief's 2 h examples | Medium | Dedicated slide, §8 |

---

## 10. Environment

- **Compute:** Kaggle (GPU T4). The full pipeline runs as a committed notebook,
  ~1–1.5 h end to end. Never run it interactively — sessions expire.
- **Local:** repo, dashboard, docs, diagram, deck. The dashboard needs only
  `twin_data.json`.
- **Do not** attempt to run the pipeline locally: no GPU, and the dataset is
  ~64 GB.
