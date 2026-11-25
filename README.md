# Can a Digital Twin Predict Freezing of Gait? A Negative Result

**Parkinson's Freezing-of-Gait Digital Twin · Team Asha · Happiest Health Digital Twin Challenge 2026**

> **Status: research prototype. Submitted to the challenge, not selected.**
> The central hypothesis (that personalising to each patient improves freezing prediction)
> was tested four ways and **failed all four**. One secondary result held up. This README
> reports both, with the evidence, and explains what I think went wrong.

---

## TL;DR

| Question | Answer |
|---|---|
| Does personalising the model to each patient improve FoG prediction? | **No.** Four mechanisms tested, all null. |
| Can we forecast a freezing episode seconds before it happens? | **Weakly.** ~2.5× chance at a 2 s horizon, but no clinically usable alarm setting. |
| Can a lower-back accelerometer rank patients by how often they freeze? | **Yes, in this cohort.** Spearman ρ = 0.514 (p = 0.0031, n = 31), better than the standard questionnaire. |

The thesis failed. The by-product, a movement-based **burden ranking**, is the part worth keeping.

---

## 1 · The hypothesis

Freezing of gait (FoG) is a brief, episodic inability to step forward despite trying to walk.
It is linked to falls, loss of independence and reduced quality of life. It is also badly
measured: a neurologist sees the patient for about 20 minutes every 3–6 months, usually in the
ON state, in a wide corridor. Those are exactly the conditions under which freezing is least
likely to appear.

A conventional FoG model maps an accelerometer window to a label and treats every patient as
the same patient. Our bet was that a **digital twin**, a model conditioned on each person's own
motor baseline, would do better:

```
Deviation_i(t) = ObservedState_i(t) − PersonalBaseline_i
```

**Hypothesis:** for the same raw reading, one patient may be far outside their normal while
another is exactly at theirs. A model that knows each patient's baseline should therefore
predict freezing better than one that doesn't.

---

## 2 · Data

Four cohorts from the **TLVMC Parkinson's Freezing of Gait** dataset (Kaggle). The data are
**linked, not redistributed**, and no patient data were collected by this team.

| Cohort | Subjects | Role |
|---|---:|---|
| `defog` | 45 | Lab, 100 Hz, with Valid/Task masks. **Evaluation arm** |
| `daily` | 65 | ~1 week of continuous home recording, **unlabelled**. Source of the personal baseline |
| `tdcsfog` | 62 | Lab, 128 Hz. Not used in the reported models, because no subject has a personal baseline |
| `notype` | — | Generic event labels only |

**Linkage:** 31 exact Subject × Visit matches with clinical, lab and home data from the same
person at the same visit. Other public datasets had no patient-level link, so we did not fuse
them, because merging would invent patients. Label-alignment agreement: 97.0%, with all 74
discrepancies accounted for.

---

## 3 · Method

**Model:** a 1-D temporal CNN over raw tri-axial lower-back accelerometry.

- **Input:** 4 s windows at 100 Hz, 0.5 s stride. Labels are index-mapped, never resampled.
- **Encoder:** 4 × Conv1d blocks (3→32→64→96→128 channels, BatchNorm + GELU, stride 2), followed by adaptive average pooling.
- **Side branch:** personal baseline (11-d, from the unlabelled home week) and clinical state, projected to 64-d.
- **Head:** 8 logits, one per warning horizon (0.5–5 s), trained with masked binary cross-entropy.

**Ablation arms:** the test of the hypothesis.

| Arm | Inputs |
|---|---|
| **A** | accelerometry only |
| **B** | A + personal baseline + deviation |
| **C** | A + personal baseline + deviation + static clinical state |

**Evaluation:**
- Subject-level `GroupKFold` with 6 folds (no patient appears in two folds; asserted in code), repeated over 3 seeds.
- Cohort: 36 patients, 45,224 windows.
- **No accuracy is reported.** At ~4.6% event prevalence, a model that predicts "never freezes" is ~95% accurate and useless. AUPRC is reported against prevalence as the chance baseline.
- The personal baseline comes from the **unlabelled** home cohort, so personalisation cannot leak the target.

---

## 4 · Results

### ❌ The hypothesis: personalisation does not help

| Mechanism | Change in AUPRC | Wins |
|---|---:|---:|
| Clinical fusion (C vs A) | −0.0023 | 50/144 |
| Personal baseline (B vs A) | −0.0120 | 46/144 |
| Per-patient threshold | −0.0005 | 11/20 |
| LOSO shrinkage | −0.0105 | 8/20 |

Model ordering: **A ≈ C > B**. The plain accelerometry model is as good as anything we added.
The seed-to-seed spread for arm C is **0.0295**, ten times larger than the 0.0023 effect of
adding clinical data. Even if fusion helped, this sample size could not detect it.

### ⚠️ Episode forecasting: above chance, not usable

| Horizon | AUPRC (C) | Chance (prevalence) |
|---:|---:|---:|
| 0.5 s | 0.140 | 0.050 |
| **2.0 s** | **0.116** | **0.046** |
| 5.0 s | 0.083 | 0.034 |

The model scores about 2.5× chance at 2 s, and the score decays with lead time. The cost of
acting on it:

| Recall target | Time in alarm state | Precision |
|---:|---:|---:|
| 30% | 10.6% | 0.127 |
| 50% | 19.5% | 0.114 |
| 70% | 33.3% | 0.094 |

**No setting is clinically viable.** Even the most permissive one leaves the alarm on for about
one minute in ten, and ~87% of alarms are false. The model also does not transfer evenly: 9 of
27 patients fall below twice their own event rate, and their optimal thresholds span
0.106–0.9998.

### ✅ What survived: burden estimation (n = 31)

| | |
|---|---|
| **Spearman ρ** | **0.514** (p = 0.0031), the headline statistic |
| Pearson r | 0.645 (p = 9 × 10⁻⁵) |
| NFOGQ questionnaire alone | 0.353 (p = 0.051, **not significant**) |
| Partial r, controlling for NFOGQ | 0.609 |
| Partial r, controlling for activity level | 0.658 |

**What this means:** this is a **ranking** instrument, not a measuring one. It can answer "which
of my patients freeze most, and is this one getting worse?" It cannot answer "this patient froze
23 times last week."

**Leverage caveat:** excluding the single highest-burden patient drops Pearson r to 0.387
(p = 0.035). Across all 31 single-patient deletions, r spans 0.387–0.712. The association holds
in every refit, but its strength depends on who is in the sample.

---

## 5 · Why I think it failed

These are post-hoc hypotheses, not tested conclusions:

1. **The sample was too small for the question.** With 31–36 patients, seed noise (0.0295) swamped the effect we were looking for. A null here means "not detectable", not "proven absent".
2. **The baseline came from a different context.** Personal baselines were computed from a week at home, while evaluation was on lab protocol segments built to provoke freezing. "Normal at home" may simply not be the right reference for "about to freeze in a lab corridor".
3. **The twin had no memory.** Online state updating is specified in `docs/02_twin_spec.md` but not implemented: the encoder is feed-forward and carries nothing between windows. A twin that cannot evolve over time is mostly a classifier with extra inputs.
4. **The challenge constrained the design.** Model C was submitted even though it does not beat arm A, because the challenge required two-stream fusion. We chose to report that honestly rather than hide the ablation.

---

## 6 · What I would do next

- **Run a power analysis first.** Estimate how many patients are needed to detect a personalisation effect of the size that would matter clinically, before building anything.
- **Implement the stateful twin** that the spec describes (a recurrent or state-space model carrying patient state across windows), then retest the hypothesis.
- **Match contexts.** Build baselines and evaluation from the same setting, ideally labelled free-living data.
- **Pre-train on the unlabelled home cohort.** Use self-supervised learning on the `daily` data instead of hand-averaged baseline features.
- **Treat burden ranking as the product.** It is the one result that held up, and it answers a question clinicians actually ask.

---

## What this project does NOT claim

- It does not diagnose Parkinson's disease, and it is not clinically validated, approved or trial-ready.
- It does not prevent falls or improve any clinical outcome.
- Burden estimation is a **concurrent estimate, not a forecast**: it describes the week just recorded, not the month ahead.
- Ground truth comes from the lab, not from home. The home cohort has no labels.
- No patient identities are merged across datasets.
- The dashboard's synthetic demo patient is clearly labelled SYNTHETIC and is asserted absent from every reported statistic.

Every claim in this repository is tagged with its evidence class in
[`docs/04_evidence_matrix.md`](Team%20Asha_Sir%20MVIT/docs/04_evidence_matrix.md).

---

## Stack

Python · PyTorch · NumPy · pandas · SciPy · pyarrow · scikit-learn (`GroupKFold`, AUPRC) ·
Kaggle T4 GPU · a self-contained HTML dashboard (no server, CDN or network calls; opens from `file://`)

## Reproducing

The pipeline runs on Kaggle, where the dataset is hosted.

1. `notebooks/02_preprocessing.ipynb`: harmonisation, event-alignment audit, windowing, home-baseline profiling. GPU T4, about 1.5 h.
2. `notebooks/04_model_seeds.ipynb`: the multi-seed ablation. Attach step 1's output as an input dataset.

Then run these from the repository root:

```bash
python3 scripts/burden_analysis.py                      # recomputes all 14 burden statistics
python3 scripts/reconstruct_burden.py --artifacts DIR   # rebuilds the 31 per-patient rows
python3 scripts/make_results.py                         # regenerates RESULTS.md
python3 scripts/build_dashboard.py                      # rebuilds dashboard/index.html
```

See [`docs/06_provenance.md`](Team%20Asha_Sir%20MVIT/docs/06_provenance.md) for exactly which
values regenerate from committed code.

## Links

| | |
|---|---|
| 🎥 Demo video | https://youtu.be/B4q3eYMGLPI |
| 📊 Full results | [`RESULTS.md`](Team%20Asha_Sir%20MVIT/RESULTS.md) |
| 🧭 Start here | [`docs/00_workflow.md`](Team%20Asha_Sir%20MVIT/docs/00_workflow.md) |
| 🧬 Twin spec | [`docs/02_twin_spec.md`](Team%20Asha_Sir%20MVIT/docs/02_twin_spec.md) |
| 🗂 Data & leakage rules | [`docs/03_data_and_target.md`](Team%20Asha_Sir%20MVIT/docs/03_data_and_target.md) |
| 🏗 Architecture | [`docs/architecture.pdf`](Team%20Asha_Sir%20MVIT/docs/architecture.pdf) |
| 📑 Deck | [`docs/deck.pdf`](Team%20Asha_Sir%20MVIT/docs/deck.pdf) |

## Team

**Team Asha**, Department of Data Science, Sir M. Visvesvaraya Institute of Technology, Bengaluru

- **Ashmit Rai**, team lead · ashmitrai1706@gmail.com
- **Krishnaditya Prakash**

## License

MIT. See [`LICENSE`](Team%20Asha_Sir%20MVIT/LICENSE). The TLVMC dataset is not redistributed
and is used under its own published terms.
