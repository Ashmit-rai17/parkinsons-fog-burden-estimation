# 01 — Clinical Problem Definition

**Status:** FROZEN · **Last updated:** 9 October 2026

---

## Conclusion

We are building a digital twin for **freezing of gait (FoG) in Parkinson's
disease**, with the demonstrated prediction task being the **onset of an acute
freezing episode**, predicted early enough to permit a cueing intervention.

FoG was selected over more obvious chronic conditions because it is the one
candidate we found where the entire causal chain — static clinical state →
continuously observed movement → evolving patient state → future adverse event
— is supported by real, linked, patient-level data rather than by assembling
unrelated datasets and asserting that they describe the same person.

---

## 1. How we arrived at Parkinson's

We deliberately did not start from the conditions named as examples in the
challenge brief. We evaluated more than twenty chronic and lifestyle
conditions — type 2 diabetes, hypertension, atrial fibrillation, heart failure,
asthma, COPD, obstructive sleep apnoea, epilepsy, multiple sclerosis, ALS,
migraine, inflammatory bowel disease, rheumatoid arthritis, sickle cell
disease, chronic kidney disease, and others — against a single test:

> Does the **same patient** have static clinical information, repeated dynamic
> physiological observation, and a genuinely future clinical outcome, in data
> we can actually obtain and publish against?

Most candidates failed not for lack of research interest but on that test. A
condition can have excellent wearable literature and excellent clinical
registries and still have no dataset in which both belong to the same people on
a shared timeline.

Type 2 diabetes is instructive. It is the most accessible option and the most
obvious given the brief. But a 30–120 minute glucose forecast is dominated by
recent glucose, which is the same signal used as input. The static clinical
state contributes little, and the result is personalised time-series
forecasting wearing the name of a digital twin. We wanted the prediction
problem itself to justify a twin.

Parkinson's survived because its static and dynamic streams describe genuinely
different things — the clinical state describes where the patient is in their
disease; the movement stream describes how that state is expressing itself in
daily life — and because FoG provides a discrete, expert-annotated, clinically
meaningful adverse event rather than another reading of the input signal.

## 2. What FoG is

Freezing of gait is a brief, episodic inability to produce effective forward
stepping despite the intention to walk. It commonly occurs at gait initiation,
during turning, when approaching a destination, in narrow spaces, and under
cognitive or dual-task load.

It is heterogeneous. It can present as trembling of the legs, very short steps,
complete motor blocks, or hesitation, and its occurrence is strongly
context-dependent. We therefore do not treat FoG as a single generic binary
phenomenon; the twin represents *when, how, and under what conditions* a
particular patient freezes.

We avoid the colloquial "feet glued to the floor" framing in technical
documentation — that is the patient's description of the experience, not a
physiological definition.

## 3. Why it matters clinically

FoG is associated with falls, impaired mobility, loss of independence,
functional dependency, and reduced quality of life, and becomes more prominent
with disease duration and severity.

Reported prevalence varies considerably with the population studied and the
assessment method used — questionnaire-based estimates run substantially higher
than clinical-rating-scale estimates, and prevalence rises markedly with
disease duration. **We do not quote a single prevalence figure**, because the
literature does not support one. The defensible statement is:

> FoG is common in Parkinson's disease, with prevalence increasing
> substantially with disease duration and severity, although reported estimates
> vary considerably according to population and assessment method.

The clinical motivation chain is:

```
FoG → mobility impairment → falls / functional dependency → loss of independence
```

## 4. The measurable physiology

FoG is not only a clinical observation. It has a documented sensor signature,
which is what makes prediction from accelerometry tractable:

- High-frequency leg oscillation in the **3–8 Hz** band during freezing, with
  documented distal-to-proximal progression (foot → shank → thigh → back).
- A measurable lag between sensor-detected oscillation and clinically observed
  onset.
- Progressive shortening of stride in the strides immediately preceding a
  freeze.

Note carefully: these describe the *transition into an individual episode*.
They do not establish that today's gait predicts freezing next week. That
distinction drives our choice of prediction layer (see §6).

On mechanism, we use the conservative formulation: FoG is thought to arise from
dysfunction across distributed neural networks involved in gait initiation,
automatic locomotion, motor set maintenance and cognitive-motor integration. We
do not commit the project to any single mechanistic hypothesis.

## 5. The three temporal scales

This is the organising insight of the project. FoG is not one prediction
problem; it is the same phenomenon observed at three timescales.

```
                    PARKINSON'S MOTOR STATE
                              |
         +--------------------+--------------------+
         |                    |                    |
      SECONDS              DAYS/WEEKS          MONTHS/YEARS
         |                    |                    |
   Pre-FoG transition   Changing FoG burden    FoG onset /
                                               progression
```

A conventional model operates on one of these. The twin represents all three,
and that is what the "digital twin" label is earning.

## 6. Why the acute layer carries the demonstrated experiment

The twin spans all three scales, but one layer must carry the experiment we
actually validate. We selected the **acute layer**, for reasons of evidence
rather than convenience:

| Layer | Evidence for prediction | Data we hold |
|---|---|---|
| Acute (seconds) | Demonstrated — forecasting, not merely detection | Dense, expert-annotated, large |
| Intermediate (days/weeks) | Not established at any specific horizon | None at this resolution |
| Long-term (months/years) | Strong prospective cohort evidence | n=25 pairs, interval **unknown** |

The intermediate horizon is conceptually the most attractive twin formulation
and we considered it at length. We rejected it as the primary endpoint because
no clinically validated prediction horizon exists at days-to-weeks scale, and
our data cannot establish one. Choosing it would have required inventing an
endpoint and then defending synthetic trajectories as if they were evidence.

The long-term layer is clinically well supported but, in the data available to
us, rests on 25 subjects with sensor recordings at two clinical visits whose
**elapsed interval is not documented anywhere in the dataset**. We retain it as
an explicitly exploratory secondary panel (see `03_data_and_target.md`, §6) and
never as a headline result.

The acute layer is the only one where the evidence, the data, and the twin
formulation all hold simultaneously.

## 7. Relevance to India

The challenge asks for a condition prevalent in India. Parkinson's is less
commonly cited than diabetes or hypertension, so this must be argued
explicitly rather than assumed.

The argument has three parts:

1. **Burden.** Parkinson's prevalence rises sharply with age, and India's
   population is ageing rapidly. → *[VERIFY: cite an Indian or ICMR/GBD
   prevalence estimate with its source. Do not state a figure without one.]*
2. **Consequence.** Falls in elderly patients drive hip fracture,
   hospitalisation, and permanent loss of independence — outcomes that are
   particularly costly where long-term rehabilitative care is limited and
   family caregiving bears the load.
3. **Access.** FoG is episodic, context-dependent and often absent in the
   clinic, so it is systematically under-detected in short, infrequent
   specialist appointments. In a setting with few movement-disorder
   specialists relative to population, a continuously monitoring twin
   addresses a real access gap rather than duplicating a service that already
   exists.

→ **ACTION:** this section needs one verified Indian burden statistic before
submission. Leaving it unsourced is worse than omitting it.

## 8. Problem statement (final wording)

> We estimate an individual Parkinson's patient's evolving motor and
> freezing-of-gait state from their clinical history and continuously observed
> real-world movement, and use that personalised state to predict impending
> freezing episodes with sufficient advance warning for intervention.

Note what this sentence does: the prediction is conditioned on a *personalised
state*, not on a movement window. That is the whole design.
