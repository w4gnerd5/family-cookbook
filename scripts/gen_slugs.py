#!/usr/bin/env python3
"""One-time slug generation. Adds slug: to frontmatter where missing.

Slugs are FROZEN once written — they go into printed QR/footer URLs.
This script never overwrites an existing slug.
"""
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def slugify(title):
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"['\u2019]", "", s)  # possessives: Zeinab's -> zeinabs, not zeinab-s
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s


def main():
    taken = set()
    files = sorted(set(ROOT.glob("assets/*/**/*.md")))
    # first pass: respect existing slugs
    for p in files:
        m = re.search(r"^slug: (\S+)$", p.read_text(), re.M)
        if m:
            taken.add(m.group(1).strip('"'))
    for p in files:
        t = p.read_text()
        if re.search(r"^slug: \S", t, re.M):
            continue
        m = re.search(r"^title: (.+)$", t, re.M)
        base = slugify(m.group(1).strip('"')) or p.parent.name
        slug, n = base, 2
        while slug in taken:
            slug, n = f"{base}-{n}", n + 1
        taken.add(slug)
        t = re.sub(r"^(title: .+)$", rf"\1\nslug: {slug}", t, count=1, flags=re.M)
        t = re.sub(r"^slug: \"\"\n", "", t, flags=re.M)  # drop an empty placeholder if present
        p.write_text(t)
        print(f"{slug}  <-  {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
