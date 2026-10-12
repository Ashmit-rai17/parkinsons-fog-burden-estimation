#!/usr/bin/env python3
"""Write a clearly labelled synthetic patient for dashboard demonstration only."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dashboard" / "synthetic_patient.json"


def main() -> None:
    times = [round(i * 0.5, 1) for i in range(240)]
    onsets = {78, 161, 213}
    risk = [round(min(0.98, max(0.02, 0.12 + 0.08 * math.sin(i / 12) + sum(
        0.66 * math.exp(-((i - onset) / 7) ** 2) for onset in onsets
    ))), 4) for i in range(len(times))]
    payload = {
        "patient": {
            "subject": "SYN-001", "synthetic": True, "visit": 2, "age": 68,
            "sex": "F", "years_dx": 9, "updrs_on": 24, "updrs_off": 35,
            "nfogq": 18, "med_on": True, "n_windows": len(times),
            "event_rate": 0.041, "auprc": 0.168, "auprc_accel_only": 0.151,
            "threshold_personal": 0.49, "activity_fraction": 0.14,
            "baseline": {
                "mag_mean": 0.98, "mag_std": 0.09, "mag_absdev": 0.07,
                "jerk_rms": 4.5, "jerk_max": 30.2, "axis_std": 0.10,
                "logp_loco": 2.1, "logp_fog": 2.3, "fog_ratio": 3.4,
                "loco_frac": 0.39,
            },
        },
        "trace": {
            "rec_id": "SYNTHETIC", "t": times, "risk": risk,
            "label": [1 if i in onsets else 0 for i in range(len(times))],
            "dev": [round(0.45 * math.sin(i / 10), 3) for i in range(len(times))],
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
