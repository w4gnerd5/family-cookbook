#!/usr/bin/env python3
"""Regenerate recipes-index.csv and RECIPES.md from .md frontmatter."""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["filename", "title", "language", "section", "number", "slug", "batch", "source_image"]


def frontmatter(path):
    m = re.match(r"---\n(.*?)\n---\n", path.read_text(), re.S)
    if not m:
        return None
    fm, key = {}, None
    for line in m.group(1).splitlines():
        if line.startswith("  - ") and key:
            item = line[4:].strip()
            if item.endswith(":") or ": " in item:
                k2, v2 = item.split(":", 1)
                fm[key].append({k2.strip(): v2.strip().strip('"')})
            else:
                fm[key].append(item)
        elif line.startswith("    ") and key and fm[key] and isinstance(fm[key][-1], dict):
            k2, v2 = line.strip().split(":", 1)
            fm[key][-1][k2.strip()] = v2.strip().strip('"')
        elif ":" in line:
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip().strip('"')
            if v == "":
                fm[k], key = [], k
            else:
                fm[k], key = v, None
    fm = {k: (v if not isinstance(v, list) or v else "") for k, v in fm.items()}
    return fm


def main():
    rows = []
    for path in sorted(set(ROOT.glob("assets/*/**/*.md"))):
        fm = frontmatter(path)
        if fm is None:
            print(f"WARNING: no frontmatter: {path.relative_to(ROOT)}")
            continue
        rows.append({
            "filename": str(path.relative_to(ROOT)),
            "title": re.sub(r"\s*\|\s*", " ", fm.get("title", "")).strip(),
            "language": fm.get("language", ""),
            "section": fm.get("section", ""),
            "number": fm.get("number", ""),
            "slug": fm.get("slug", ""),
            "batch": fm.get("batch", ""),
            "source_image": next((s["path"] if isinstance(s, dict) else s for s in fm.get("scans") or []), "") if isinstance(fm.get("scans"), list) else fm.get("source_image", ""),
        })
        for field in ("title", "language", "section"):
            if not rows[-1][field]:
                print(f"WARNING: missing {field}: {path.relative_to(ROOT)}")

    order = {s: i for i, s in enumerate(
        ["Breads & Doughs", "Soups & Stews", "Mains", "Sides & Salads",
         "Preserves & Sauces", "Desserts & Sweets", "Drinks", "Pantry"])}
    rows.sort(key=lambda r: (order.get(r["section"], 99), int(r["number"] or 0)))
    with open(ROOT / "recipes-index.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    lines = [
        "# Recipe Index",
        "",
        "Generated from frontmatter by `scripts/build_index.py` — do not edit manually.",
        "",
        f"{len(rows)} recipes.",
        "",
        "| Section | # | Title | Language | Slug | File |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['section']} | {r['number']} | {r['title']} | "
            f"{r['language']} | {r['slug']} | {r['filename']} |"
        )
    (ROOT / "RECIPES.md").write_text("\n".join(lines) + "\n")
    print(f"wrote recipes-index.csv and RECIPES.md: {len(rows)} recipes")


if __name__ == "__main__":
    main()
