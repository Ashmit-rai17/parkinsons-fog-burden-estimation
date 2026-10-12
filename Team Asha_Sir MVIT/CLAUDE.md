# Working on this repository

Read `docs/00_workflow.md` before doing anything. It holds the frozen
decisions, the real numbers, and what is left to build. If any other file
disagrees with it, it is newer and it wins.

## What this project is

A digital twin for freezing of gait (FoG) in Parkinson's disease, submitted to
the Happiest Health Digital Twin Challenge 2026. Its primary validated output
is concurrent estimation of current FoG burden on held-out patients; acute
episode forecasting remains a weak secondary analysis.

## Non-negotiable rules

These exist because a clinical jury will test them. Do not relax them to make
output look better.

1. **Never report accuracy.** Prevalence is ~4.5%, so a model that predicts
   "never" scores ~95%. Report AUPRC against the prevalence floor.
2. **State the numbers as they are.** The model reaches roughly 2–3× chance.
   It is not deployable. Four tested mechanisms were null. Say so.
3. **Synthetic data is labelled SYNTHETIC in the UI**, and never enters a
   reported metric.
4. **No claim appears anywhere** — UI, README, deck, video — unless it is in
   `docs/04_evidence_matrix.md` with its evidence class.
5. **Never attach a time interval to the longitudinal layer.** The gap between
   Visit 1 and Visit 2 is undocumented in the source data.
6. **Never quote a single FoG prevalence figure.** The literature does not
   support one.
7. The submitted model is **C** (accelerometry + personal baseline + clinical
   state), because it is the only arm that ingests both required data streams.
8. Detailed results numbers live only in `dashboard/twin_data.json` and the
   `RESULTS.md` generated from it. Narrative documents may carry the approved
   burden-estimation headline and its required caveats.

## Layout

```
README.md            submission entry point — every required field
docs/00_workflow.md  decisions, pipeline, remaining work  ← read first
docs/01..04          problem, twin spec, data & target, evidence matrix
dashboard/           self-contained HTML + twin_data.json
figures/             five result figures (PNG)
notebooks/           Kaggle notebooks (preprocessing, model seeds)
RESULTS.md           generated results summary
```

## The dashboard

One self-contained `dashboard/index.html`, no server. It embeds the canonical
`dashboard/twin_data.json` payload at build time (schema: `meta`, `horizons`, `horizon_curve`,
`prevalence`, `nulls`, `operating_points`, `heterogeneity`, `feature_names`,
`patients`, `traces`).

It must show, for a selected patient: baseline clinical state; their personal
movement baseline versus current deviation; a live risk trace over time with
ground-truth onsets marked; and FoG burden. Plus a cohort view carrying the
horizon curve, the per-patient panel and the operating point.

Report the operating point as **percentage of monitored time in an alarm
state**, not raw false alarms per hour, and caveat that evaluation is on
FoG-provoking protocol segments rather than free-living monitoring.

## What not to do

- Do not run the pipeline locally. No GPU, and the dataset is ~64 GB.
- Do not reopen the data audit. The label-quality gate is closed and passed.
- Do not add modelling experiments. Modelling is frozen.
