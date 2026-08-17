#!/usr/bin/env python3
"""One-time hymnal-model recipe numbering. Adds number: to frontmatter where missing.

Numbers are per-section, FROZEN once written (they appear in print and the ToC).
New recipes take the next free number in their section. Never renumber.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = [
    "Breads & Doughs", "Soups & Stews", "Mains", "Sides & Salads",
    "Preserves & Sauces", "Desserts & Sweets", "Drinks", "Pantry",
]


def fm_get(text, key):
    m = re.search(rf"^{key}: (.+)$", text, re.M)
    return m.group(1).strip().strip('"') if m else None


def main():
    files = sorted(set(ROOT.glob("assets/*/**/*.md")))
    highest = {s: 0 for s in SECTIONS}
    todo = []
    for p in files:
        t = p.read_text()
        sec = fm_get(t, "section")
        num = fm_get(t, "number")
        if num:
            highest[sec] = max(highest[sec], int(num))
        else:
            todo.append((p, sec))
    # assign in book order: section order, then filename
    todo.sort(key=lambda x: (SECTIONS.index(x[1]), str(x[0])))
    for p, sec in todo:
        highest[sec] += 1
        t = p.read_text()
        t = re.sub(r"^(section: .+)$", rf"\1\nnumber: {highest[sec]}", t, count=1, flags=re.M)
        p.write_text(t)
        print(f"{sec} · {highest[sec]}  {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
