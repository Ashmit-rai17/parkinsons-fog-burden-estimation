# 04 — Evidence Matrix

**Status:** LIVE — update when any claim changes · **Last updated:** 14 October 2026

> Every substantive claim this project makes is listed here with its evidence
> class. If a claim is not in this table, it should not appear in the
> presentation, the video, or the README.
>
> This document exists because the failure mode of a digital-twin project is
> not a bad model. It is a plausible idea that quietly becomes a stated fact.

---

## Evidence classes

| Label | Meaning |
|---|---|
| **VERIFIED — DATA** | Directly observed in the source dataset by our own analysis |
| **VERIFIED — LITERATURE** | Established in peer-reviewed published research |
| **PREPRINT** | Reported in a non-peer-reviewed preprint; treated as weaker than VERIFIED |
| **INFERRED** | Reasonable conclusion derived from evidence, not directly stated by it |
| **ASSUMED** | Necessary modelling assumption; not empirically established |
| **SYNTHETIC** | Artificially generated component |
| **UNKNOWN** | Evidence unavailable |
| **CONTRADICTION** | Sources disagree |

---

## 1. Clinical claims

| Claim | Class | Note |
|---|---|---|
| FoG is an episodic impairment of effective forward stepping despite intention to walk | VERIFIED — LITERATURE | Use the current international consensus phrasing, not older descriptions |
| FoG commonly occurs at gait initiation, turning, destination approach, narrow spaces, dual-task load | VERIFIED — LITERATURE | |
| FoG is heterogeneous in presentation and highly context-dependent | VERIFIED — LITERATURE | |
| FoG is associated with falls, impaired mobility, functional dependency, reduced quality of life | VERIFIED — LITERATURE | |
| FoG prevalence increases with disease duration and severity | VERIFIED — LITERATURE | |
| A single FoG prevalence figure | **UNKNOWN** | Estimates vary widely by population and assessment method. **Do not quote one number.** |
| FoG arises from dysfunction across distributed neural networks | VERIFIED — LITERATURE | Conservative formulation; do not attribute to a single circuit |
| Individual FoG episodes show 3–8 Hz leg oscillation with distal-to-proximal progression | VERIFIED — LITERATURE | |
| Stride length progressively decreases in the strides preceding a freeze | VERIFIED — LITERATURE | |
| Future FoG onset is a legitimate prognostic problem over multi-year horizons | VERIFIED — LITERATURE | Multiple prospective cohorts and a meta-analysis |
| Days-to-weeks FoG risk is a clinically validated endpoint | **UNKNOWN** | No established horizon. This is why it is not our target. |
| Parkinson's disease prevalence in India: Kolkata door-to-door survey of 100,802 people, age-adjusted prevalence 52.85 per 100,000 (World Standard Population) | VERIFIED — LITERATURE | Das SK, Misra AK, Ray BK, et al. *Neurology*. 2010;75(15):1362–1369. doi:10.1212/WNL.0b013e3181f735a7. One city, one method; Indian estimates vary widely by region and method, so do not present it as a national figure. Do **not** cite the Bombay Parsi community figure: an ethnically distinct population that does not generalise. |

## 2. Prediction-horizon claims

| Claim | Class | Note |
|---|---|---|
| FoG can be detected from lower-back accelerometry | VERIFIED — LITERATURE | Large existing literature |
| Wearable signals contain information preceding individual FoG episodes | VERIFIED — LITERATURE | |
| Seconds-scale FoG prediction performance remains stable to roughly 2 s before onset, declining from ~2.5 s | **PREPRINT** | Li M, Shi B, Tay A, Au WL, Tan DML, Chia NSY, Yen S-C. *Freezing Prediction Horizon: Quantifying Advanced Warning for Predicting Freezing of Gait in Parkinson's Disease.* medRxiv, posted 22 January 2026. DOI [10.64898/2026.01.21.26344382](https://www.medrxiv.org/content/10.64898/2026.01.21.26344382v1). 63 recruited, 55 with at least one freezing episode. **Explicitly not peer reviewed — must be labelled as such wherever cited.** |
| Substantial patient heterogeneity in acute predictability; age, disease duration and FOGQ do not explain it | **PREPRINT** | Li M, Shi B, Tay A, Au WL, Tan DML, Chia NSY, Yen S-C. *Freezing Prediction Horizon: Quantifying Advanced Warning for Predicting Freezing of Gait in Parkinson's Disease.* medRxiv, posted 22 January 2026. DOI [10.64898/2026.01.21.26344382](https://www.medrxiv.org/content/10.64898/2026.01.21.26344382v1). At the 2 s horizon 43 subjects were analysed and 6 (14.0%) fell below a 75% Macro F1 threshold. **Explicitly not peer reviewed.** |
| Our own FoG-burden estimation on held-out patients | **VERIFIED — DATA** | Spearman ρ = 0.51, p = 0.003; Pearson r = 0.65, p = 0.0001. See `RESULTS.md`. Concurrent estimation, not prospective forecasting; n = 31, single cohort, correlational, no external validation. Spearman is the headline statistic. Pearson is leverage-sensitive to one high-burden patient; excluding it gives r = 0.387, p = 0.035. The association remains significant in every single-patient deletion (r = 0.39–0.71, all p < 0.05). |
| Our own reported horizon curve | VERIFIED — DATA | Closed. See `RESULTS.md`; this is a weak secondary result, reported against prevalence. |
| Clinical fusion for acute forecasting | VERIFIED — DATA | Null; see `RESULTS.md`. |
| Personal baseline for acute forecasting | VERIFIED — DATA | Null; see `RESULTS.md`. |
| Per-patient thresholding for acute forecasting | VERIFIED — DATA | Null; see `RESULTS.md`. |
| LOSO shrinkage for acute forecasting | VERIFIED — DATA | Null; see `RESULTS.md`. |
| Wearable data predict long-term FoG progression | **UNKNOWN** | Not established. Do not claim. |

## 3. Dataset claims — all verified by our own analysis

| Claim | Class |
|---|---|
| Three cohorts: tdcsfog (lab), defog (home protocol), daily (24/7 continuous) | VERIFIED — DATA |
| 136 subjects, 1,035 recordings total | VERIFIED — DATA |
| tdcsfog: 62 subjects, 833 recordings, 128 Hz, m/s² | VERIFIED — DATA |
| defog: 45 subjects, 137 recordings, 100 Hz, g | VERIFIED — DATA |
| daily: 65 subjects, ~1 week continuous each, 100 Hz, unlabelled | VERIFIED — DATA |
| 3,544 expert-annotated events; 2,817 task windows | VERIFIED — DATA |
| Daily ∩ Clinical = 65/65 subjects | VERIFIED — DATA |
| Daily ∩ DeFOG = 36 subjects | VERIFIED — DATA |
| **Daily × DeFOG × Clinical exact Subject×Visit overlap = 31** | VERIFIED — DATA |
| No subject appears in all three cohorts including tdcsfog | VERIFIED — DATA |
| 37 subjects have paired clinical visits; 25 of these have defog at both | VERIFIED — DATA |
| UPDRS-III On changed in 35/37 paired subjects | VERIFIED — DATA |
| Raw `Time` is a recording-relative index starting at 0 | VERIFIED — DATA |
| Daily recordings span ~7–8 days, duration varies | VERIFIED — DATA (36 files inspected) |
| Daily recordings are continuous with no gaps | VERIFIED — DATA (36 files inspected) |
| **Elapsed time between Visit 1 and Visit 2** | **UNKNOWN** | No date, interval or timestamp field exists in any metadata file. Verified by direct inspection. |
| tdcsfog Visit = protocol stages (baseline, two post-treatment, follow-up) | VERIFIED — DATA | Dataset documentation. **Does not transfer to defog Visit 1 → 2.** |

## 4. Modelling assumptions — stated, not hidden

| Assumption | Class | Why |
|---|---|---|
| A patient's personal motor baseline can be estimated from ~1 week of unlabelled home accelerometry | **ASSUMED** | Reasonable, not established. The ablation tests it empirically. |
| Deviation from personal baseline carries information about impending FoG beyond the raw signal | **ASSUMED** | This is the project's central hypothesis. The ablation is what decides it — and a null result is reported as a null result. |
| Representations learned from lab recordings (tdcsfog) transfer to home recordings (defog) after harmonisation | **ASSUMED** | Different device, rate and environment. Pretraining is tested against a no-pretraining control. |
| `Task == True` regions with no nearby onset are genuinely FoG-free | **ASSUMED** | Follows the annotation protocol; the safest available assumption |
| 4 s windows capture the relevant pre-FoG dynamics | **ASSUMED** | Starting choice informed by the documented pre-FoG timescale |
| Excluding `Valid == False` events improves label quality | **INFERRED** | Dataset documents these as annotator-ambiguous |

## 5. Synthetic data — scope and boundary

The challenge explicitly permits synthetic data ("Teams may use synthetic
patient generation tools (like Synthea)... or generate their own synthetic
time-series data"). We use it, within one hard boundary.

| Use | Status |
|---|---|
| Dashboard demo patient — a fully synthetic patient with clinical state, personal baseline and risk trace, using only the twin's declared data streams (no labs, genetic markers, medications or dated visits) | **SYNTHETIC** — labelled as such in the UI |
| Demonstrating longitudinal state evolution across simulated visits | **Not used.** Removed so no Visit 1 → Visit 2 interval is implied. |
| Augmentation of rare pre-FoG windows | **SYNTHETIC** — optional; not used in reported metrics |
| Any number in the results table | **Never synthetic.** Every reported metric comes from real held-out subjects. |

**The rule, stated in the video and the deck:** synthetic data enters
demonstration and the dashboard; it never enters a reported evaluation metric.

### What we do NOT do

| | |
|---|---|
| Cross-cohort patient merging | **Not used.** No evidence any two cohorts contain the same individuals. |
| AMP-PD / Telemonitoring fusion | **Not used.** No patient-level linkage to the FoG cohort exists, so attaching those clinical records to TLVMC sensor subjects would fabricate patients. |

A synthetic patient generated end to end and labelled as synthetic is honest.
A real sensor subject wearing someone else's clinical record is not. That is
the distinction, and it is the one a clinical jury will test.

## 6. Open gaps before submission

- [ ] Indian burden statistic for Parkinson's, with source (`01_problem.md` §7) — source verified and recorded above; `01_problem.md` §7 text still to be updated
- [x] Horizon curve results → VERIFIED — DATA in `RESULTS.md`
- [x] Ablation results → recorded in `RESULTS.md`, including null results
- [x] Per-subject failure analysis → recorded in `RESULTS.md`
- [x] Daily-recording continuity → verified across 36 files
- [x] Final licence choice recorded in README and `LICENSE` (MIT)

## 7. Rule for the video and deck

If a statement is not in this table, it does not get said on camera.

If it is **PREPRINT**, **ASSUMED** or **UNKNOWN**, the qualifier is said out
loud. A jury that catches an unqualified claim discounts everything else;
a jury that hears you qualify your own evidence trusts the rest.
