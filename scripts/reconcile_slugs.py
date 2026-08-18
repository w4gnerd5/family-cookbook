#!/usr/bin/env python3
"""Reconcile hand-edited slugs.

Paul edits `slug:` in any recipe frontmatter. This script diffs those slugs
against the baseline recorded in curation-state.json (keyed by recipe ID, which
never changes), then:

  - rewrites every see_also: reference that pointed at an old slug
  - refreshes the ledger baseline and the dashboard slug table
  - reports anything it could not resolve

Dry run by default; pass --apply to write.

Slugs are the frozen identity behind printed footers, QR links and website URLs.
Editing them is only free until something is printed or published.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "curation-state.json"


def slug_of(text):
    m = re.search(r"^slug: (\S+)$", text, re.M)
    return m.group(1) if m else None


def main():
    apply = "--apply" in sys.argv
    state = json.loads(LEDGER.read_text())
    baseline = {r["id"]: r["slug"] for r in state["inventory"]}

    files = {p.stem: p for p in sorted(set(ROOT.glob("assets/*/**/*.md")))}
    renames, unknown = {}, []
    for rid, p in files.items():
        new = slug_of(p.read_text())
        if new is None:
            continue
        old = baseline.get(rid)
        if old is None:
            unknown.append(f"{rid} ({new}) is not in the ledger baseline")
        elif old != new:
            renames[old] = new

    if not renames:
        print("no slug changes since the last reconcile")
    for old, new in sorted(renames.items()):
        print(f"RENAME  {old}  ->  {new}")
    for u in unknown:
        print(f"NOTE    {u}")

    # collisions: two recipes now claiming one slug
    live = [slug_of(p.read_text()) for p in files.values()]
    dupes = {s for s in live if s and live.count(s) > 1}
    if dupes:
        print("\nERROR: duplicate slugs in the collection:", ", ".join(sorted(dupes)))
        return 1

    # rewrite see_also references that point at renamed slugs
    fixed = 0
    for rid, p in files.items():
        t = p.read_text()
        orig = t
        for old, new in renames.items():
            t = re.sub(rf"^(\s+- slug: ){re.escape(old)}$", rf"\g<1>{new}", t, flags=re.M)
        if t != orig:
            fixed += 1
            print(f"RELINK  {rid}")
            if apply:
                p.write_text(t)

    # refresh ledger baseline so the next run diffs against current state
    if apply:
        for r in state["inventory"]:
            p = files.get(r["id"])
            if p:
                s = slug_of(p.read_text())
                if s:
                    r["slug"] = s
        LEDGER.write_text(json.dumps(state, ensure_ascii=False, indent=1))

    print(f"\n{len(renames)} renamed, {fixed} files relinked"
          + ("" if apply else "\nDry run. Re-run with --apply to write."))
    if apply:
        print("Then run: md_to_data (validates every see_also), build_index, "
              "build_credits, refresh_slug_table, typst compile.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
