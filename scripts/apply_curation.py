#!/usr/bin/env python3
"""Apply Paul's edits from curation-state.json back to the recipe files.

Reads curation-state.json (the dashboard ledger):
- ACTION=cut: recipe folder moves to attic/<language>/ (git mv), never deleted
- NEW_SECTION: frontmatter section is rewritten
- NEW_ORDER: recipes are renumbered per section — marked rows first in the
  given order, unmarked rows after in current-number order

Prints every change and any NOTES verbatim. Dry run by default; pass --apply
to write. After applying, run the normal build chain.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = [
    "Breads & Doughs", "Soups & Stews", "Mains", "Sides & Salads",
    "Preserves & Sauces", "Desserts & Sweets", "Drinks", "Pantry",
]


def set_fm(path, key, value):
    t = path.read_text()
    t2, n = re.subn(rf'^{key}: .*$', f'{key}: {value}', t, count=1, flags=re.M)
    assert n == 1, f"{key} not found in {path}"
    path.write_text(t2)


def main():
    apply = "--apply" in sys.argv
    import json
    state = json.loads((ROOT / "curation-state.json").read_text())
    by_id = {p.stem: p for p in sorted(set(ROOT.glob("assets/*/**/*.md")))}

    rows = []
    for r in state["inventory"]:
        rows.append(dict(rid=r["id"], section=r["section"], num=r["num"],
                         title=r["title"], slug=r["slug"],
                         new_sec=r["new_section"], new_ord=r["new_order"],
                         cut=bool(r["cut"]), notes=r["notes"]))

    for r in rows:
        if r["notes"]:
            print(f"NOTE  {r['rid']} {r['slug']}: {r['notes']}")

    # cuts
    for r in [x for x in rows if x["cut"]]:
        p = by_id[r["rid"]]
        dest = ROOT / "attic" / p.parent.parent.name / p.parent.name
        print(f"CUT   {r['slug']} -> {dest.relative_to(ROOT)}")
        if apply:
            dest.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "mv", str(p.parent), str(dest)], check=True, cwd=ROOT)

    # scribe attribution sync (adds the keys if a file lacks them)
    for r in state["inventory"]:
        if not r.get("scribe"):
            continue
        p2 = by_id[r["id"]]
        t2 = p2.read_text()
        if "scribe:" not in t2:
            t2 = re.sub(r"^(language: .+)$", rf"\1\nscribe: {r['scribe']}\nscribe_confidence: {r.get('scribe_conf') or 0}", t2, count=1, flags=re.M)
            if apply:
                p2.write_text(t2)
            print(f"SCRIBE {r['id']}: {r['scribe']} ({r.get('scribe_conf')})")
        else:
            if apply:
                set_fm(p2, "scribe", str(r["scribe"]))
                set_fm(p2, "scribe_confidence", str(r.get("scribe_conf") or 0))

    kept = [r for r in rows if not r["cut"]]
    for r in kept:
        if r["new_sec"] and r["new_sec"] != r["section"]:
            print(f"MOVE  {r['slug']}: {r['section']} -> {r['new_sec']}")
            if apply:
                set_fm(by_id[r["rid"]], "section", f'"{r["new_sec"]}"')
        r["final_sec"] = r["new_sec"] or r["section"]

    # renumber per final section
    for sec in SECTIONS:
        group = [r for r in kept if r["final_sec"] == sec]
        marked = sorted([r for r in group if r["new_ord"]], key=lambda x: float(x["new_ord"]))
        rest = sorted([r for r in group if not r["new_ord"]], key=lambda x: int(x["num"]))
        for n, r in enumerate(marked + rest, 1):
            if n != r["num"] or r["new_sec"]:
                print(f"NUM   {sec} · {r['num']} -> {n}  {r['slug']}")
            if apply:
                set_fm(by_id[r["rid"]], "number", str(n))

    if not apply:
        print("\nDry run. Re-run with --apply to write.")
    else:
        print("\nApplied. Now run: md_to_data, build_index, build_credits, typst compile.")


if __name__ == "__main__":
    main()
