#!/usr/bin/env python3
"""
Standardize headings across batch-1 .md files:
- Remove trailing colons from ## and ### headings
Run from repo root: python3 scripts/standardize_headings.py
"""

import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEORGIAN_DIR = os.path.join(REPO_ROOT, "assets", "georgian")

BATCH1_FILES = [
    "IMG_1161.md", "IMG_1162.md", "IMG_1168.md", "IMG_1170.md", "IMG_1175.md",
    "IMG_1176.md", "IMG_1178.md", "IMG_1180.md", "IMG_1184.md", "IMG_1185.md",
    "IMG_1186.md", "IMG_1189.md", "IMG_1190.md", "IMG_1192.md", "IMG_1195.md",
    "IMG_1198.md", "IMG_1199.md", "IMG_1200.md", "IMG_1201.md", "IMG_1202.md",
]

def fix_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Remove trailing colons from ## and ### headings
    content = re.sub(r"^(#{2,3} [^\n]+?):(\s*)$", r"\1\2", content, flags=re.MULTILINE)

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        # Show which headings changed
        orig_headings = [l for l in original.splitlines() if re.match(r"^#{2,3} ", l)]
        new_headings = [l for l in content.splitlines() if re.match(r"^#{2,3} ", l)]
        changes = [(o, n) for o, n in zip(orig_headings, new_headings) if o != n]
        for o, n in changes:
            print(f"  {os.path.basename(path)}: '{o}' → '{n}'")
    else:
        print(f"  {os.path.basename(path)}: no changes")

def main():
    for filename in BATCH1_FILES:
        path = os.path.join(GEORGIAN_DIR, filename)
        if os.path.exists(path):
            fix_file(path)
        else:
            print(f"  MISSING: {filename}")

if __name__ == "__main__":
    main()
