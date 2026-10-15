# 06 — Provenance of the results payload

**Last updated:** 15 October 2026

This document records which values in `dashboard/twin_data.json` have been
reproduced from the committed notebooks, and which have not. A value listed as
not reproduced is not known to be wrong. It means its producing code is not in
this repository, so it cannot be regenerated from it.

---

## 1. Reproduced by a fresh run of `notebooks/04_model_seeds.ipynb`

A fresh Kaggle run of the committed `notebooks/04_model_seeds.ipynb` reproduces
the following payload fields exactly:

| Field | Reproduced value |
|---|---|
| `horizon_curve` A / B / C | all horizons, to 4 decimal places |
| `prevalence` | all horizons |
| `nulls` — "Clinical fusion (C vs A)" | −0.0023, 50/144 wins |
| `nulls` — "Personal baseline (B vs A)" | −0.0120, 46/144 wins |
| `seed_spread` | A 0.0113 · B 0.0034 · C 0.0295 |
| `heterogeneity` | 9 of 27 patients below twice their own event rate |
| Cohort (`meta`) | 45,224 windows, 36 subjects |

### Burden block

`burden.per_patient` reproduces to 0.0000 on `estimate` and 0.0001 on
`actual_rate`, across all 31 patients, under these definitions:

| Quantity | Definition |
|---|---|
| Cohort | `windows_meta.parquet` where `has_baseline == 1` |
| Evaluation mask | `(y_2.0 == 1) \| (y_neg == 1)` — 33,051 windows |
| `estimate` | per-subject mean of `oof_A_mean[:, 2.0 s]` over that mask |
| `actual_rate` | per-subject mean of `y_2.0` over the same mask |
| Included | 31 of 36 subjects |

The burden estimator is therefore **arm A — accelerometry only**,
seed-averaged over 3 seeds. It is not the submitted model C.

`estimate` is a mean predicted risk; `actual_rate` is the fraction of
evaluation windows that are positive. They are different quantities on
different scales, so the reported association is rank-based.

`scripts/reconstruct_burden.py --artifacts DIR` checks these four definitions
against the payload from the notebook outputs (`windows_meta.parquet`,
`oof_A_mean.npy`). It prints a per-patient table, exits non-zero on any
difference over 0.001, and never writes to the payload.

---

## 2. Not reproduced — open

No code in this repository produces the following. They remain in the payload
as recorded; none has been derived or estimated here.

- `meta.threshold_global`
- `heterogeneity.threshold_min` and `heterogeneity.threshold_max`
- `meta.monitored_hours`
- `horizon_curve_sd`
- `operating_points`
- The `nulls` rows "Per-patient threshold" and "LOSO shrinkage"
- The rule that excludes subjects `0e3d49`, `1d7a0d`, `7b2e84`, `ab3b2e` and
  `c12ab3` from the burden block
