# 03 — Data Mapping, Prediction Target, and Leakage Rules

**Status:** FROZEN · **Last updated:** 9 October 2026

> This is the operational document. If you are writing code, read this one.

---

## Conclusion

Three cohorts within the TLVMC Parkinson's FoG dataset play three distinct
roles: `tdcsfog` is not used in the reported models (no tdcsfog subject has a
personal baseline, so none is in the modelling cohort), `defog` is the
evaluation arm, and `daily` supplies the unlabelled personal baseline. **31 Subject × Visit
combinations carry clinical state, controlled FoG recording, and a full week of
home recording simultaneously** — that triple overlap is the twin cohort.

No patient identities are merged across datasets. Anywhere real linkage is
absent, we say so rather than synthesising it.

---

## 1. Source

TLVMC Parkinson's Freezing of Gait dataset — Center for the Study of Movement,
Cognition and Mobility, Neurological Institute, Tel Aviv Sourasky Medical
Center. Public, open-source, used under its published terms.

Three cohorts, collected under different circumstances:

| Cohort | Setting | Subjects | Recordings | Rate | Units | Labels |
|---|---|---|---|---|---|---|
| `tdcsfog` | Lab, FoG-provoking protocol | 62 | 833 | 128 Hz | m/s² | StartHesitation, Turn, Walking |
| `defog` | Home, FoG-provoking protocol | 45 | 137 | 100 Hz | g | + `Valid`, `Task` |
| `notype` | From defog, no event types | — | 46 files | 100 Hz | g | `Event` only |
| `daily` | Home, 24/7 continuous | 65 | 65 | 100 Hz | g | **none** |

Totals across cohorts: 136 subjects, 1,035 recordings, 3,544 expert-annotated
events, 2,817 task windows.

## 2. Cohort roles in the twin

| Cohort | Role | Why |
|---|---|---|
| `tdcsfog` | Not used in the reported models | No tdcsfog subject has a personal baseline, so none is in the modelling cohort. |
| `defog` | Evaluation arm | Carries `Task` and `Valid` annotations, and 36 of its subjects also have daily recordings. |
| `daily` | Personal baseline | ~1 week continuous per subject. **Unlabelled — cannot leak the target.** |
| `notype` | Evaluation arm, with `defog` | Generic `Event` labels only, so not usable for type-level analysis. No pretraining is done on any cohort. |

## 3. Verified linkage

| Overlap | Count |
|---|---|
| Daily ∩ Clinical (subjects) | 65 / 65 |
| Daily ∩ DeFOG (subjects) | 36 |
| Daily ∩ DeFOG ∩ Clinical (subjects) | 36 |
| **Daily × DeFOG × Clinical, exact Subject × Visit** | **31** |
| — of which at Visit 1 | 27 |
| — of which at Visit 2 | 4 |
| Subjects in all three cohorts incl. tdcsfog | **0** |

The last row matters: `tdcsfog` subjects do not appear in the paired clinical
cohort. This is why tdcsfog is not used in the reported models: no tdcsfog
subject has a personal baseline, so none is in the modelling cohort.

## 4. Static clinical variables

From `subjects.csv`, per Subject × Visit: Age, Sex, YearsSinceDx, UPDRSIII_On,
UPDRSIII_Off, NFOGQ. Medication state (on/off) comes from the recording
metadata files.

Across the 37 subjects with both clinical visits: Age and YearsSinceDx are
constant as expected; UPDRS-III On changed in 35/37, UPDRS-III Off in 35/37,
NFOGQ in 30/37. Clinical state genuinely evolves.

## 5. The temporal limitation — read this before claiming any horizon

**The elapsed time between Visit 1 and Visit 2 is not documented anywhere in
the dataset.** We verified this directly:

- `subjects.csv`, `defog_metadata.csv`, `daily_metadata.csv`,
  `tdcsfog_metadata.csv` contain no date, timestamp, or interval field.
- Raw `Time` is a recording-relative integer sample index starting at 0 in
  every file; it resets per recording.
- Recording IDs are 10-character hashes with no temporal encoding.
- No documentation in the dataset package defines what Visit 1 and Visit 2
  mean for the defog cohort.

The `tdcsfog` metadata does define its Visit variable as protocol stages
(baseline, two post-treatment assessments, follow-up) — but tdcsfog visits run
2, 3, 4, 5, 13, 19, 20 and do not correspond to the defog Visit 1 → Visit 2
structure. That documentation cannot be transferred.

**Rule: Visit 1 → Visit 2 is an ordinal ordering with UNKNOWN elapsed time.**
Never describe any result as "6-month" or "1-year" prediction. Never infer the
interval from the visit numbers.

## 6. Prediction targets

### 6.1 Primary — acute FoG onset (validated)

At time *t*, using only data available at *t*, estimate P(FoG onset within
horizon *h*).

**Onset.** The first sample of a contiguous run where any event indicator
(`StartHesitation`, `Turn`, `Walking`, or `Event` for notype) transitions
0 → 1.

**Positive windows.** A window of length *W* ending exactly *h* seconds before
an onset, for h ∈ {0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0}.

**Negative windows.** Sampled **only** from regions where `Task == True` and no
onset occurs within ±10 s.

**Window length.** *W* = 4 s, 50% overlap. Tune only if the horizon curve is
unstable.

**Exclusions.** Events with `Valid == False` are excluded from positives —
these are annotator-ambiguous cases where akinetic FoG could not be
distinguished from a voluntary stop.

**Evaluation.** Macro-F1 and AUPRC reported *as a function of h*, not pooled.
Per-subject breakdown reported alongside, including subjects where the model
fails.

Event duration is highly skewed (median ≈ 2.68 s, mean ≈ 8.19 s, max ≈ 582 s);
we predict onset, not duration, so this affects sampling but not the target.

### 6.2 Secondary — longitudinal trajectory (exploratory)

Visit-1 clinical state + Visit-1 defog sensor state → Visit-2 UPDRS-III On.

**n = 25.** Within that cohort: 16 worsened, 7 improved, 2 stable, mean
Δ = +3.64, median Δ = +2.

Target ranking within this panel:

| Target | Assessment |
|---|---|
| ΔUPDRS-III On | Best available — balanced |
| ΔUPDRS-III Off | Secondary — 11 worsened / 13 improved |
| NFOGQ continuous change | Weak — only 3/25 worsened |
| NFOGQ binary worsening | **Not viable** — 1–6 positives depending on threshold |

**Mandatory caveats whenever this panel is shown:** n=25; elapsed interval
unknown; exploratory, not a validated endpoint. NFOGQ additionally has a
minimal detectable change larger than most observed changes here, so it is not
used as a primary ground truth.

## 7. Leakage rules — non-negotiable

1. **Subject-level splits only.** `GroupKFold` grouped by Subject. A subject
   appears in exactly one fold. Never split by recording; most subjects have
   multiple recordings (up to 24 in tdcsfog).
2. **No future information in the window.** The window ends at *t*; nothing
   after *t* enters any feature.
3. **Personal baselines computed within-subject from `daily` only.** Never from
   labelled defog or tdcsfog data, and never pooled across the training set in
   a way that lets test subjects influence their own baseline.
4. **Normalisation statistics fit on training folds only.**
5. **No cross-cohort patient identity.** A tdcsfog subject is not a defog
   subject.
6. **Negatives only from `Task == True`.** `Task == False` regions are
   unannotated, not confirmed FoG-free. Sampling them is silent label noise
   that will inflate reported performance.
7. **`Valid == False` events excluded from positives.**

## 8. Preprocessing

**Harmonisation** (do this first, once):

- Resample tdcsfog 128 Hz → 100 Hz.
- Convert tdcsfog m/s² → g (divide by 9.80665).
- After this, all three cohorts share frame and units.

**Daily profiler.** 65 parquet files, ~63.6 GB total, 0.24–1.64 GB each,
60–69M rows each (≈7–8 days at 100 Hz). Process **chunked**, and only for the
31–36 overlap subjects. Cache per-subject baseline vectors to a small parquet
and never re-read the raw archive.

Recording duration varies; do not claim every daily recording is exactly 7
days. The sampled files ranged ~7–8 days.

**Baseline features per subject** (distribution statistics, not point values):

- activity fraction, active/inactive period structure
- movement magnitude and jerk percentiles
- movement fragmentation
- band power in 0.5–3 Hz (locomotor) and 3–8 Hz (FoG-associated)
- variability and regularity measures

Current window features are then z-scored against the subject's own
distribution to produce `Deviation_i(t)`.

## 9. Class balance

FoG is rare in continuous recording. Use focal loss, or cap the
negative:positive ratio at roughly 5:1 **per subject** so that subjects with
long recordings do not dominate.

## 10. Known data quirks

- Label density varies enormously by cohort and recording. In tdcsfog overall:
  StartHesitation 304,790 samples, Turn 1,678,782, Walking 207,838 — Turn
  dominates heavily.
- StartHesitation appears in only 7 defog recordings.
- 1,042 of 3,544 events have `Type == NaN` (the notype series).
- 411 event recordings have no corresponding task annotation; events.csv spans
  a broader recording set (535 IDs) than the task-annotated defog recordings
  (137 IDs).
- Accelerometer channels: `AccV` (vertical), `AccML` (mediolateral), `AccAP`
  (anteroposterior), lower back.
