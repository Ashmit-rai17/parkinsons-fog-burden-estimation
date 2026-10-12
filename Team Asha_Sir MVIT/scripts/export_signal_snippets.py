#!/usr/bin/env python3
"""Export observed, recording-order pre-freeze signal windows for the twin."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import decimate


FS = 100
DISPLAY_FS = 50
WIN_N = 400
HORIZON_S = 2.0
WINDOW_S = 4.0
REQUIRED = ("windows_meta.parquet", "windows_X.npy")
SIGNAL_NOTE = (
    "Measured tri-axial lower-back accelerometry. Whole contiguous 4.0 s windows, "
    "recorded at 100 Hz and anti-alias decimated to 50 Hz for display. Up to 3 "
    "pre-freeze windows per subject at the 2.0 s horizon, selected by recording "
    "order — not by model output. Not a continuous stream."
)


def missing_files(directory: Path) -> list[str]:
    return [name for name in REQUIRED if not (directory / name).is_file()]


def default_artifacts(root: Path) -> Path:
    candidates = sorted(path for path in root.parent.iterdir() if path.is_dir() and path != root)
    complete = [path for path in candidates if not missing_files(path)]
    if complete:
        return complete[0]
    looked = "\n  ".join(
        f"{path}: missing {', '.join(missing_files(path))}" for path in candidates
    ) or "(no sibling directories)"
    raise FileNotFoundError(
        "Could not find a sibling artifact directory containing "
        + ", ".join(REQUIRED) + f"\nSiblings checked:\n  {looked}"
    )


def selected_windows(meta: pd.DataFrame) -> dict[str, list[int]]:
    """Return the first three 2.0-second-horizon windows per subject.

    Metadata rows retain the source recording order.  This deliberately does
    not inspect risk predictions: it filters the explicit 2.0 s horizon label
    and keeps the earliest three rows for each subject.
    """
    label = f"y_{HORIZON_S}"
    if label not in meta:
        raise ValueError(f"windows_meta.parquet is missing required column: {label}")
    selected: dict[str, list[int]] = defaultdict(list)
    for index, row in meta.iterrows():
        if int(row[label]) == 1 and len(selected[str(row.subject)]) < 3:
            selected[str(row.subject)].append(index)
    return dict(selected)


def signal_entry(x: np.ndarray, index: int) -> dict:
    """Take one contiguous 4 s observed window and anti-alias decimate to 50 Hz."""
    displayed = decimate(np.asarray(x[index], dtype=np.float32), 2, axis=0, zero_phase=True)
    if displayed.shape != (int(WINDOW_S * DISPLAY_FS), 3):
        raise ValueError(f"expected {(int(WINDOW_S * DISPLAY_FS), 3)} display samples, got {displayed.shape}")
    return {
        "fs": DISPLAY_FS,
        "accv": [round(float(value), 4) for value in displayed[:, 0]],
        "accml": [round(float(value), 4) for value in displayed[:, 1]],
        "accap": [round(float(value), 4) for value in displayed[:, 2]],
    }


def export(artifacts: Path, data_path: Path) -> dict[str, list[dict]]:
    missing = missing_files(artifacts)
    if missing:
        raise FileNotFoundError(f"Artifact directory {artifacts} is missing: {', '.join(missing)}")
    meta = pd.read_parquet(artifacts / "windows_meta.parquet")
    required_columns = {"subject", f"y_{HORIZON_S}"}
    absent = sorted(required_columns - set(meta.columns))
    if absent:
        raise ValueError(f"windows_meta.parquet is missing required columns: {', '.join(absent)}")
    x = np.load(artifacts / "windows_X.npy", mmap_mode="r")
    if len(meta) != len(x) or x.shape[1:] != (WIN_N, 3):
        raise ValueError(f"windows metadata/signals are not aligned: {len(meta)} rows, {x.shape} windows")

    snippets = {subject: [signal_entry(x, index) for index in indices]
                for subject, indices in selected_windows(meta).items()}
    data = json.loads(data_path.read_text())
    data["signal_snippets"] = snippets
    data["signal_note"] = SIGNAL_NOTE
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return snippets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, help="Directory containing the signal artifacts")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    artifacts = args.artifacts.resolve() if args.artifacts else default_artifacts(root)
    snippets = export(artifacts, root / "dashboard" / "twin_data.json")
    print(f"signal_snippets: {len(snippets)} subjects, {sum(map(len, snippets.values()))} events")


if __name__ == "__main__":
    main()
