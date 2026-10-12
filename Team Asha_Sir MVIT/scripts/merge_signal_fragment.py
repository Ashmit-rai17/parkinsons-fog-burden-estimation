#!/usr/bin/env python3
"""Merge a validated Kaggle signal fragment into dashboard/twin_data.json.

No file in this repository produces such a fragment: the in-repo export path is
scripts/export_signal_snippets.py, which writes signal_snippets directly into
dashboard/twin_data.json. This script exists only for fragments created outside
the repo (e.g. on Kaggle); nothing else here references it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


ALLOWED_FRAGMENT_KEYS = {"signal_snippets", "signal_note"}
AXES = ("accv", "accml", "accap")


def stable_hash(payload: dict) -> str:
    """Hash all canonical payload values except the two signal additions."""
    kept = {key: value for key, value in payload.items() if key not in ALLOWED_FRAGMENT_KEYS}
    encoded = json.dumps(kept, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def validate_event(subject: str, event: object) -> None:
    if not isinstance(event, dict) or event.get("fs") != 50:
        raise ValueError(f"{subject}: event must be an object with fs == 50")
    arrays = []
    for axis in AXES:
        values = event.get(axis)
        if not isinstance(values, list):
            raise ValueError(f"{subject}: missing {axis} array")
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
                   for value in values):
            raise ValueError(f"{subject}: {axis} contains a non-finite value")
        arrays.append(values)
    if len({len(values) for values in arrays}) != 1:
        raise ValueError(f"{subject}: axis arrays have different lengths")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fragment", type=Path, help="Kaggle-exported signal fragment JSON")
    parser.add_argument("--data", type=Path, help="Dashboard payload (defaults to dashboard/twin_data.json)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    data_path = args.data or root / "dashboard" / "twin_data.json"
    fragment = json.loads(args.fragment.read_text())
    if not isinstance(fragment, dict):
        raise ValueError("fragment root must be a JSON object")
    unexpected = sorted(set(fragment) - ALLOWED_FRAGMENT_KEYS)
    missing = sorted(ALLOWED_FRAGMENT_KEYS - set(fragment))
    if unexpected:
        raise ValueError("unexpected fragment top-level key(s): " + ", ".join(unexpected))
    if missing:
        raise ValueError("missing fragment top-level key(s): " + ", ".join(missing))
    if not isinstance(fragment["signal_note"], str):
        raise ValueError("signal_note must be a string")
    if not isinstance(fragment["signal_snippets"], dict):
        raise ValueError("signal_snippets must be an object")

    data = json.loads(data_path.read_text())
    before = stable_hash(data)
    cohort = {patient["subject"] for patient in data["patients"]}
    snippets: dict[str, list[dict]] = {}
    dropped = 0
    for subject, events in fragment["signal_snippets"].items():
        if subject not in cohort:
            dropped += 1
            continue
        if not isinstance(events, list):
            raise ValueError(f"{subject}: snippets must be a list")
        for event in events:
            validate_event(subject, event)
        snippets[subject] = events

    print(f"kept {len(snippets)}, dropped {dropped}")
    event_count = sum(len(events) for events in snippets.values())
    print(f"validated {len(snippets)} subjects, {event_count} events")
    data["signal_snippets"] = snippets
    data["signal_note"] = fragment["signal_note"]
    if not set(data["signal_snippets"]) <= cohort:
        raise AssertionError("signal_snippets contains a subject outside DATA.patients")
    after = stable_hash(data)
    if before != after:
        raise AssertionError("non-signal payload hash changed; refusing to write")
    print(f"non-signal payload SHA-256: {after} (passed)")

    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"merged {len(snippets)} subjects, {event_count} events")
    print(f"final file size: {data_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
