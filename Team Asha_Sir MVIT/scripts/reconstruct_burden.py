#!/usr/bin/env python3
"""Reconstruct the burden per-patient rows from Kaggle artifacts and verify them.

This is a verifier, not a generator. It rebuilds ``burden.per_patient`` in
dashboard/twin_data.json from the outputs of notebooks/04_model_seeds.ipynb
under the four definitions recorded in docs/06_provenance.md:

  cohort          = windows_meta.parquet where has_baseline == 1
  evaluation mask = (y_2.0 == 1) | (y_neg == 1)
  estimate        = per-subject mean of oof_A_mean[:, 2.0 s] over that mask
  actual_rate     = per-subject mean of y_2.0 over the same mask

It prints a per-patient table and exits non-zero if any stored value differs
from its reconstruction by more than 0.001, or if the cohort does not match
the payload. It never writes to any file.

The rule that excludes 5 of the 36 subjects from the burden block is not
reproduced; those subjects are listed but not checked.

Usage: python3 scripts/reconstruct_burden.py --artifacts DIR
DIR must contain windows_meta.parquet and oof_A_mean.npy.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "dashboard" / "twin_data.json"
HORIZON = 2.0
TOLERANCE = 0.001
EXPECTED_MASKED = 33_051


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--artifacts", type=Path, required=True,
                        help="directory holding windows_meta.parquet and oof_A_mean.npy")
    args = parser.parse_args()

    missing = [f for f in ("windows_meta.parquet", "oof_A_mean.npy")
               if not (args.artifacts / f).is_file()]
    if missing:
        print(f"FAIL: missing from {args.artifacts}: {', '.join(missing)}")
        return 1

    data = json.loads(DATA_PATH.read_text())
    meta, burden = data["meta"], data["burden"]
    stored = {row["subject"]: row for row in burden["per_patient"]}
    failures: list[str] = []

    # Definition 1 — cohort.
    windows = pd.read_parquet(args.artifacts / "windows_meta.parquet")
    cohort = windows[windows["has_baseline"] == 1].reset_index(drop=True)
    oof = np.load(args.artifacts / "oof_A_mean.npy")
    if len(cohort) != len(oof):
        print(f"FAIL: cohort has {len(cohort)} windows but oof_A_mean has {len(oof)} rows")
        return 1
    if len(cohort) != meta["n_windows"]:
        failures.append(f"cohort windows {len(cohort)} != meta.n_windows {meta['n_windows']}")
    if cohort["subject"].nunique() != meta["n_patients"]:
        failures.append(f"cohort subjects {cohort['subject'].nunique()} != meta.n_patients {meta['n_patients']}")

    # Definition 2 — evaluation mask.
    mask = ((cohort[f"y_{HORIZON}"] == 1) | (cohort["y_neg"] == 1)).to_numpy()
    if int(mask.sum()) != EXPECTED_MASKED:
        failures.append(f"evaluation mask has {int(mask.sum())} windows, expected {EXPECTED_MASKED:,}")

    # Definitions 3 and 4 — per-subject estimate and actual_rate.
    column = data["horizons"].index(HORIZON)
    masked = cohort.loc[mask, ["subject", f"y_{HORIZON}"]].copy()
    masked["risk"] = oof[mask, column]
    if masked["risk"].isna().any():
        failures.append("oof_A_mean has NaN inside the evaluation mask")
    rebuilt = masked.groupby("subject").agg(estimate=("risk", "mean"),
                                            actual_rate=(f"y_{HORIZON}", "mean"))

    print(f"Cohort: {len(cohort):,} windows, {cohort['subject'].nunique()} subjects; "
          f"evaluation mask: {int(mask.sum()):,} windows; horizon {HORIZON} s, arm A")
    print()
    print(f"{'subject':<8} {'est stored':>10} {'est rebuilt':>11} {'|d|':>7}  "
          f"{'rate stored':>11} {'rate rebuilt':>12} {'|d|':>7}  status")
    print("-" * 82)
    for subject in sorted(set(rebuilt.index) | set(stored)):
        if subject not in rebuilt.index:
            print(f"{subject:<8} in payload but absent from the evaluation mask")
            failures.append(f"{subject}: in payload, not reconstructed")
            continue
        r = rebuilt.loc[subject]
        if subject not in stored:
            print(f"{subject:<8} {'—':>10} {r.estimate:>11.5f} {'':>7}  {'—':>11} "
                  f"{r.actual_rate:>12.5f} {'':>7}  excluded from burden block (rule not reproduced)")
            continue
        s = stored[subject]
        d_est = abs(s["estimate"] - r.estimate)
        d_rate = abs(s["actual_rate"] - r.actual_rate)
        ok = d_est <= TOLERANCE and d_rate <= TOLERANCE
        if not ok:
            failures.append(f"{subject}: estimate |d| = {d_est:.5f}, actual_rate |d| = {d_rate:.5f}")
        print(f"{subject:<8} {s['estimate']:>10.5f} {r.estimate:>11.5f} {d_est:>7.5f}  "
              f"{s['actual_rate']:>11.5f} {r.actual_rate:>12.5f} {d_rate:>7.5f}  {'ok' if ok else 'MISMATCH'}")

    checked = len(set(stored) & set(rebuilt.index))
    if checked != burden["n_patients"]:
        failures.append(f"{checked} patients checked, payload n_patients = {burden['n_patients']}")

    print()
    if failures:
        print(f"FAIL: {len(failures)} problem(s):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS: all {checked} payload patients reproduce within {TOLERANCE} on estimate and actual_rate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
