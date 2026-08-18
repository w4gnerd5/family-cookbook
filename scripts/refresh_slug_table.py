#!/usr/bin/env python3
"""Rebuild the dashboard's Slugs table from current recipe data."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
d = json.loads((ROOT / "print" / "recipes.json").read_text())
state = json.loads((ROOT / "curation-state.json").read_text())

stems = {}
for r in d:
    stems.setdefault(re.sub(r"-\d+$", "", r["slug"]), []).append(r["slug"])

rows = []
for r in d:
    s = r["slug"]
    stem = re.sub(r"-\d+$", "", s)
    flags = []
    if re.search(r"-\d+$", s):
        flags.append("numeral suffix")
    if len(stems[stem]) > 1:
        flags.append(f"shares stem with {len(stems[stem]) - 1}")
    if len(s) > 40:
        flags.append("long")
    rows.append({"slug": s, "stem": stem, "title": r["title"], "section": r["section"],
                 "num": r["number"], "lang": r["language"], "scribe": r["scribe"],
                 "refs": len(r["see_also"]), "len": len(s), "flags": ", ".join(flags)})
rows.sort(key=lambda x: (x["stem"], x["slug"]))
state["slugs"] = rows
(ROOT / "curation-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=1))
print(f"slug table refreshed: {len(rows)} slugs, {sum(1 for r in rows if r['flags'])} flagged")
