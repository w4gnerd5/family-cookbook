#!/usr/bin/env python3
"""Apply Paul's edits from curation.xlsx back to the recipe files.

Reads the yellow columns (NEW_SECTION, NEW_ORDER, ACTION, NOTES):
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

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = [
    "Breads & Doughs", "Soups & Stews", "Mains", "Sides & Salads",
    "Preserves & Sauces", "Desserts & Sweets", "Drinks", "Pantry",
]
HDR = 7


def set_fm(path, key, value):
    t = path.read_text()
    t2, n = re.subn(rf'^{key}: .*$', f'{key}: {value}', t, count=1, flags=re.M)
    assert n == 1, f"{key} not found in {path}"
    path.write_text(t2)


def main():
    apply = "--apply" in sys.argv
    ws = load_workbook(ROOT / "curation.xlsx")["Inventory"]
    by_id = {p.stem: p for p in sorted(set(ROOT.glob("assets/*/**/*.md")))}

    rows = []
    for r in ws.iter_rows(min_row=HDR + 1, values_only=True):
        rid, section, num, title, lang, _d, _s, _p, slug, new_sec, new_ord, action, notes = r[:13]
        if not rid:
            continue
        rows.append(dict(rid=rid, section=section, num=num, title=title, slug=slug,
                         new_sec=new_sec, new_ord=new_ord,
                         cut=(str(action or "").strip().lower() == "cut"),
                         notes=notes))

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
