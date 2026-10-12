# 02 — Digital Twin Specification

**Status:** FROZEN · **Last updated:** 9 October 2026

---

## Conclusion

The twin is a **time-dependent patient-state representation**, not a prediction
model and not a digital copy of a patient. It maintains an evolving estimate of
one individual's motor and freezing-of-gait state by integrating baseline
characteristics, longitudinal clinical history, medication context, and
continuously observed movement.

Its defining property is **state evolution**: the twin at *t₂* is not identical
to the twin at *t₁*, because new observations have updated it.

---

## 1. Definition

> A personalised computational representation of a person with Parkinson's
> disease that maintains an evolving estimate of their motor and
> freezing-of-gait state by integrating longitudinal clinical history,
> patient-specific characteristics, medication context, and continuously
> observed movement behaviour.

Formally:

```
S_i(t) = [ B_i, C_i(t), M_i(t), G_i(t), F_i(t), Z_i(t) ]
```

| Symbol | Meaning |
|---|---|
| `B_i` | Baseline patient characteristics (slowly changing) |
| `C_i(t)` | Longitudinal clinical state |
| `M_i(t)` | Medication / treatment context |
| `G_i(t)` | Dynamic motor and gait state |
| `F_i(t)` | Freezing-of-gait state and burden |
| `Z_i(t)` | Estimated latent personalised motor state |

## 2. Scope

**Inside the boundary.** The evolving motor and FoG-related state of an
individual with Parkinson's disease:

```
patient characteristics → disease/motor state → gait state
  → FoG susceptibility → impending FoG
```

**Outside the boundary.** We are explicitly not modelling the entire
neurological disease, every Parkinson's symptom, treatment optimisation,
diagnosis, mortality, all future complications, or a complete physiological
replica.

Drawing this boundary is deliberate. It prevents the project from becoming an
arbitrary collection of Parkinson's datasets, and it is the honest answer to
the challenge's own observation that a whole-body twin is out of scope for a
short project.

## 3. The four state layers

### Layer 1 — Baseline state `B_i`

Relatively stable characteristics defining underlying susceptibility.

| Domain | Variables | Role |
|---|---|---|
| Demographics | Age, Sex | Baseline characteristics |
| Disease history | Years since diagnosis | Trajectory context |
| Baseline motor | UPDRS-III (on / off medication) | Motor severity |
| Baseline FoG | NFOGQ | Existing FoG susceptibility |

"Baseline" means *slowly changing or reference-state*, not immutable. Age
advances; years-since-diagnosis increases; UPDRS changes between visits.

### Layer 2 — Clinical state `C_i(t)`

Where the twin becomes longitudinal. The twin holds a trajectory, not a score:

```
not:  UPDRS = 32
but:  UPDRS trajectory → stable / worsening / improving
      FoG history → absent → emerging → recurrent → increasing burden
```

Answers: *how has this patient's clinical motor state been changing?*

### Layer 3 — Dynamic motor / gait state `G_i(t)`

The continuously updated layer, derived from accelerometry:

- **Movement** — acceleration statistics, magnitude, activity level,
  active/inactive periods, fragmentation, jerk characteristics
- **Gait** — stride characteristics where derivable, gait variability,
  movement regularity, changes in walking behaviour
- **FoG-related** — event frequency, duration, episode distribution, temporal
  clustering, pre-FoG movement characteristics

Answers: *what is this patient's movement doing right now?*

### Layer 4 — Acute FoG state `F_i(t)`

The shortest timescale. The twin continuously estimates whether the current
movement pattern is transitioning toward an impending freeze:

```
F_i(t) = P( FoG onset | S_i(t), X_{t-k:t} )
```

where `X_{t-k:t}` is the recent movement signal.

## 4. The latent state `Z_i(t)` — the central object

**The raw sensor stream is not the twin.** `accelerometer = digital twin` would
be wrong, and it is the error that turns a twin into a classifier.

```
Raw observations
      ↓
Movement features
      ↓
Motor / gait representation
      ↓
PATIENT LATENT STATE  Z_i(t)
      ↓                    ↓
Longitudinal        Acute FoG
trajectory          prediction
```

`Z_i(t)` is our computational representation of the patient's current motor
condition. It is the object that both outputs are read from.

## 5. State evolution

```
Z_i(t+1) = g( Z_i(t), X_i(t+1), C_i(t+1), M_i(t+1) )
```

Previous state + new observations → updated state. The twin therefore develops
a patient-specific trajectory rather than holding a static profile.

## 6. Patient-specificity — the design principle

This is the heart of the system.

We do not want: *"this movement pattern means FoG."*

We want: *"given this patient's historical motor state and observed movement
behaviour, this represents an increased deviation from their own normal and may
indicate impending FoG."*

Operationally:

```
Deviation_i(t) = ObservedState_i(t) - PersonalBaseline_i
```

The twin learns the patient's own motor baseline rather than treating every
patient as identical.

**Implementation note.** `PersonalBaseline_i` is computed from the subject's
week of continuous home recording, which carries no FoG labels. Personalisation
therefore cannot leak the prediction target. This is not an incidental
property — it is why the personalisation is credible rather than circular, and
it should be stated explicitly in the video.

## 7. What the twin does NOT claim

Stated explicitly so it cannot be read into the work by an evaluator.

The twin does not claim:

- that the model reproduces the patient's entire physiology;
- that any two source cohorts contain the same patients;
- that wearable movement alone predicts months or years of FoG;
- that the system diagnoses Parkinson's disease;
- that a predicted FoG event will definitely occur;
- that the system prevents falls;
- that the warning horizon has been shown to improve clinical outcomes;
- that any synthetic or derived component constitutes clinical evidence.

## 8. What the twin can answer

At any point in time:

| Question | From |
|---|---|
| Who is this patient? | `B_i` |
| How has their motor condition been changing? | `C_i(t)` |
| What does normal movement look like *for them*? | `PersonalBaseline_i` |
| What is happening to their movement now? | `G_i(t)` |
| How and when do they freeze? | `F_i(t)` burden |
| Are they approaching an episode? | `F_i(t)` acute |

That set of answers is what distinguishes this from "AI predicts freezing."

## 9. The loop

```
         PATIENT HISTORY
               ↓
          Baseline State
               ↓
          Clinical State
               ↓
      Dynamic Observations
               ↓
      PATIENT LATENT STATE Z(t)
               ↓
      +--------+--------+
      ↓                 ↓
 Longitudinal      Acute State
  trajectory            ↓
      |            Impending FoG
      |                 |
      +--------+--------+
               ↓
       UPDATED DIGITAL TWIN
```

## 10. Layer priority for this submission

The twin spans all four layers. For this prototype:

- **Primary, validated:** concurrent FoG-burden estimation from held-out
  patients' movement, using the twin state representation. This estimates
  current burden; it is not prospective forecasting of future burden.
- **Secondary, exploratory:** acute layer (`F_i(t)`), conditioned on `B_i`,
  `C_i(t)`, `M_i(t)` and `PersonalBaseline_i`; and the longitudinal trajectory,
  presented with its unknown time interval stated.

The burden result is correlational, from a single cohort without external
validation; Pearson is leverage-sensitive and is reported with its stable
Spearman and leave-one-patient-out checks. Acute forecasting is retained as an
honest secondary analysis. See `RESULTS.md` and `04_evidence_matrix.md`.
