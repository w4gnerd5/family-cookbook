#!/usr/bin/env python3
"""Generate CREDITS.md from photo_source frontmatter.

photo_source format: "<source page URL> | <license> | <author>"
Feeds the book colophon and the website credits page. CC BY and CC BY-SA
photos require this attribution wherever the images appear.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    rows = []
    for p in sorted(set(ROOT.glob("assets/*/**/*.md"))):
        t = p.read_text()
        title = re.search(r"^title: (.+)$", t, re.M)
        src = re.search(r'^photo_source: "(.+)"$', t, re.M)
        if not src:
            continue
        parts = [s.strip() for s in src.group(1).split("|")]
        url, license_, author = (parts + ["", "", ""])[:3]
        rows.append((title.group(1).strip('"'), author, license_, url))

    lines = [
        "# Photo Credits",
        "",
        "Generated from `photo_source:` frontmatter by `scripts/build_credits.py`.",
        "Dish photographs are illustrative, from free-license libraries; scans of",
        "the original recipe cards are family material.",
        "",
    ]
    for title, author, license_, url in rows:
        lines.append(f"- **{title}** — photo by {author}, {license_} ({url})")
    n_missing = 87 - len(rows)
    lines += ["", f"{len(rows)} recipes with sourced photos; {n_missing} awaiting photos."]
    (ROOT / "CREDITS.md").write_text("\n".join(lines) + "\n")
    print(f"wrote CREDITS.md: {len(rows)} credited")


if __name__ == "__main__":
    main()
