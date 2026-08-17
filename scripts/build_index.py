#!/usr/bin/env python3
"""Regenerate recipes-index.csv and RECIPES.md from .md frontmatter."""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["filename", "title", "language", "section", "batch", "page", "source_image"]


def frontmatter(path):
    m = re.match(r"---\n(.*?)\n---\n", path.read_text(), re.S)
    if not m:
        return None
    fm, key = {}, None
    for line in m.group(1).splitlines():
        if line.startswith("  - ") and key:
            fm[key].append(line[4:].strip())
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
            "title": fm.get("title", ""),
            "language": fm.get("language", ""),
            "section": fm.get("section", ""),
            "batch": fm.get("batch", ""),
            "page": fm.get("page", ""),
            "source_image": (fm.get("scans") or [""])[0] if isinstance(fm.get("scans"), list) else fm.get("source_image", ""),
        })
        for field in ("title", "language", "section"):
            if not rows[-1][field]:
                print(f"WARNING: missing {field}: {path.relative_to(ROOT)}")

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
        "| Title | Language | Section | Batch | Page | File |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['title']} | {r['language']} | {r['section']} | "
            f"{r['batch']} | {r['page']} | {r['filename']} |"
        )
    (ROOT / "RECIPES.md").write_text("\n".join(lines) + "\n")
    print(f"wrote recipes-index.csv and RECIPES.md: {len(rows)} recipes")


if __name__ == "__main__":
    main()
