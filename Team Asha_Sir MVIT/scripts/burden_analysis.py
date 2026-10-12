#!/usr/bin/env python3
"""Recompute the burden-estimation statistics and verify them against the payload.

This is a verifier, not a generator. It reads dashboard/twin_data.json, recomputes
every statistic stored under ``burden`` from the per-patient rows published there,
prints a comparison table to stdout and exits non-zero if any value disagrees.
It never writes to any file.

Each stored value is compared at the precision the payload stores it with: the
recomputed value is rounded to the same number of decimal places as the stored
value (0.645 -> 3 places, 9e-05 -> 5 places) and the two must be equal.
"""

from __future__ import annotations

import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "dashboard" / "twin_data.json"


def partial_r(x: np.ndarray, y: np.ndarray, control: np.ndarray) -> tuple[float, float]:
    """Residualise x and y on the control with a linear fit, then Pearson the residuals.

    Degrees of freedom: a partial correlation with one control variable is tested
    on n - 3 df (n - 2 - number of controls), NOT the n - 2 that pearsonr assumes
    for the residuals. Using pearsonr's p here understates it. Do not change this
    back; ordinary correlations elsewhere in this script correctly use n - 2.
    """
    rx = x - np.polyval(np.polyfit(control, x, 1), control)
    ry = y - np.polyval(np.polyfit(control, y, 1), control)
    r = float(stats.pearsonr(rx, ry)[0])
    df = len(x) - 3
    t = r * np.sqrt(df / (1 - r * r))
    p = 2 * stats.t.sf(abs(t), df)
    return r, float(p)


def jackknife(x: np.ndarray, y: np.ndarray, subjects: list[str]) -> list[tuple[str, float, float]]:
    """Leave-one-patient-out Pearson.

    Definition: refit Pearson(estimate, actual_rate) on each of the n subsets that
    leave out exactly one patient. r_min and r_max are the extremes of r across
    those n refits; p_max is the largest p-value among the same n refits.
    """
    out = []
    for i, subject in enumerate(subjects):
        keep = np.arange(len(x)) != i
        r, p = stats.pearsonr(x[keep], y[keep])
        out.append((subject, float(r), float(p)))
    return out


def stored_places(value: float) -> int:
    return max(0, -Decimal(repr(value)).as_tuple().exponent)


def at_precision(value: float, places: int) -> Decimal:
    return Decimal(repr(float(value))).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def main() -> int:
    data = json.loads(DATA_PATH.read_text())
    burden = data["burden"]
    per_patient = burden["per_patient"]
    patients = data["patients"]

    print(f"source: {DATA_PATH.relative_to(ROOT)} (read-only)")
    print("burden keys:       ", sorted(burden))
    print("per_patient fields:", sorted({k for row in per_patient for k in row}))
    print("patients fields:   ", sorted({k for row in patients for k in row}))
    print()

    pp = pd.DataFrame(per_patient)
    pt = pd.DataFrame(patients)
    if "synthetic" not in pt:
        pt["synthetic"] = False
    if "synthetic" not in pp:
        pp["synthetic"] = False
    n_syn = int(pt["synthetic"].fillna(False).astype(bool).sum() + pp["synthetic"].fillna(False).astype(bool).sum())
    pt = pt[~pt["synthetic"].fillna(False).astype(bool)]
    pp = pp[~pp["synthetic"].fillna(False).astype(bool)]
    print(f"synthetic rows excluded: {n_syn}")

    failures: list[str] = []
    if pp["subject"].duplicated().any() or pt["subject"].duplicated().any():
        failures.append("duplicate subjects in per_patient or patients")

    cols = ["subject", "nfogq"] + (["activity_fraction"] if "activity_fraction" in pt else [])
    df = pp.merge(pt[cols], on="subject", how="left", suffixes=("_burden", ""), validate="one_to_one")
    missing = df.loc[df["nfogq"].isna(), "subject"].tolist()
    if missing:
        failures.append(f"per_patient subjects without a patients[] row: {missing}")
    if "nfogq_burden" in df:
        disagree = df.loc[df["nfogq_burden"] != df["nfogq"], "subject"].tolist()
        print(f"nfogq: per_patient vs patients[] disagree for {len(disagree)} subjects {disagree or ''}")
        if disagree:
            failures.append(f"nfogq differs between per_patient and patients[] for {disagree}")
    print()

    est = df["estimate"].to_numpy(float)
    act = df["actual_rate"].to_numpy(float)
    nfogq = df["nfogq"].to_numpy(float)

    computed: dict[str, float] = {"n_patients": len(df)}
    computed["spearman_r"], computed["spearman_p"] = map(float, stats.spearmanr(est, act))
    computed["pearson_r"], computed["pearson_p"] = map(float, stats.pearsonr(est, act))
    computed["nfogq_alone_r"], computed["nfogq_alone_p"] = map(float, stats.pearsonr(nfogq, act))
    computed["partial_r_nfogq"], computed["partial_p_nfogq"] = partial_r(est, act, nfogq)
    if "activity_fraction" in df and df["activity_fraction"].notna().all():
        activity = df["activity_fraction"].to_numpy(float)
        computed["partial_r_activity"], computed["partial_p_activity"] = partial_r(est, act, activity)
    else:
        print("activity_fraction unavailable for some real patients: partial_r_activity / partial_p_activity SKIPPED")

    jk = jackknife(est, act, df["subject"].tolist())
    computed["jackknife_r_min"] = min(r for _, r, _ in jk)
    computed["jackknife_r_max"] = max(r for _, r, _ in jk)
    computed["jackknife_p_max"] = max(p for _, _, p in jk)

    order = ["n_patients", "spearman_r", "spearman_p", "pearson_r", "pearson_p",
             "nfogq_alone_r", "nfogq_alone_p", "partial_r_activity", "partial_p_activity",
             "partial_r_nfogq", "partial_p_nfogq", "jackknife_r_min", "jackknife_r_max",
             "jackknife_p_max"]
    print(f"{'statistic':<20} {'recomputed (full)':>18} {'recomputed':>12} {'stored':>10}  match")
    print("-" * 72)
    for key in order:
        if key not in burden:
            print(f"{key:<20} {'':>18} {'':>12} {'ABSENT':>10}  not in payload")
            continue
        stored = burden[key]
        if key not in computed:
            print(f"{key:<20} {'':>18} {'SKIPPED':>12} {stored!r:>10}  not checked")
            continue
        places = stored_places(stored)
        got = at_precision(computed[key], places)
        ok = got == at_precision(stored, places)
        print(f"{key:<20} {computed[key]:>18.6g} {str(got):>12} {stored!r:>10}  {'yes' if ok else 'NO  <-- MISMATCH'}")
        if not ok:
            failures.append(f"{key}: recomputed {computed[key]:.6g} (= {got} at {places} dp), stored {stored!r}")

    unchecked = sorted(set(burden) - set(order) - {"per_patient", "note", "leverage_note"})
    if unchecked:
        print(f"\nstored but not recomputed: {unchecked}")

    print("\njackknife detail (leave-one-patient-out Pearson):")
    for label, row in (("r_min", min(jk, key=lambda t: t[1])),
                       ("r_max", max(jk, key=lambda t: t[1])),
                       ("p_max", max(jk, key=lambda t: t[2]))):
        print(f"  {label}: drop {row[0]} -> r = {row[1]:.4f}, p = {row[2]:.4g}")

    print()
    if failures:
        print(f"FAIL: {len(failures)} mismatch(es)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS: every recomputed statistic matches the stored value at stored precision.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
