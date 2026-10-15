#!/usr/bin/env python3
"""Embed canonical dashboard data into the offline dashboard HTML."""

import json
import pathlib


root = pathlib.Path(__file__).resolve().parents[1]
tpl = (root / "dashboard" / "_template.html").read_text()
data = json.loads((root / "dashboard" / "twin_data.json").read_text())
syn = root / "dashboard" / "synthetic_patient.json"
if syn.exists():
    s = json.loads(syn.read_text())
    s["patient"]["synthetic"] = True
    data["patients"].append(s["patient"])
    data["traces"][s["patient"]["subject"]] = s["trace"]
    assert not any(p["subject"] == s["patient"]["subject"]
                   for p in data["burden"]["per_patient"]), "synthetic leaked into burden stats"
TOKEN = "/*__TWIN_DATA__*/null"
assert tpl.count(TOKEN) == 1, f"expected exactly one {TOKEN} in _template.html, found {tpl.count(TOKEN)}"
out = tpl.replace(TOKEN, json.dumps(data, separators=(",", ":")))
assert TOKEN not in out, "token survived substitution"
(root / "dashboard" / "index.html").write_text(out)
print("wrote dashboard/index.html", len(out) // 1024, "KB")
