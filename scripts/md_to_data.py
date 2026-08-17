#!/usr/bin/env python3
"""Parse recipe .md files into print/recipes.json for the Typst template.

Usage: python3 scripts/md_to_data.py [batch-1]
With a batch argument, only recipes whose frontmatter batch matches are included.
Recipes are ordered by section (controlled vocabulary order), then filename.
"""
import json
import random

from PIL import Image
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = [
    "Breads & Doughs", "Soups & Stews", "Mains", "Sides & Salads",
    "Preserves & Sauces", "Desserts & Sweets", "Drinks", "Pantry",
]


def parse_md(path):
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
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
    fm = {k: ("" if v == [] and k != "scans" else v) for k, v in fm.items()}
    body = text[m.end():]

    def section(name):
        m = re.search(rf"^#{{2,3}} {name}[^\n]*\n(.*?)(?=^#{{1,3}} |\Z)", body, re.S | re.M)
        return m.group(1).strip() if m else ""

    desc_m = re.search(r"^# [^\n]+\n+(.*?)(?=^## |\Z)", body, re.S | re.M)
    orig_m = re.search(r"^### Original [^\n]*\n(.*?)\Z", body, re.S | re.M)

    def conv(s):
        """Markdown inline -> Typst markup (evaluated with eval(mode: "markup"))."""
        s = s.replace("\\", "\\\\")
        for ch in "#$@~`":
            s = s.replace(ch, "\\" + ch)
        s = re.sub(r"\*\*(.+?)\*\*", "\x00\\1\x00", s)  # bold -> placeholder
        s = re.sub(r"\*(.+?)\*", r"_\1_", s)              # italic -> typst emph
        s = s.replace("\x00", "*")                        # placeholder -> typst strong
        # safety net: an unpaired delimiter would break Typst's eval of this string
        if s.count("*") % 2:
            s = s.replace("*", "\\*")
        if s.count("_") % 2:
            s = s.replace("_", "\\_")
        return s

    def items(block, marker):
        out = []
        for line in block.splitlines():
            line = line.strip()
            if re.match(r"^\*\*.+:?\*\*:?$", line):
                out.append({"group": line.strip("*:").strip("*")})
            elif re.match(rf"^{marker}", line):
                out.append(conv(re.sub(rf"^{marker}\s*", "", line)))
        return out

    # normalize scan entries to dicts with art-direction defaults; tilt is
    # deterministic per scan (seeded by slug+path) so builds are reproducible
    slug = fm.get("slug", "") or ""
    scans = []
    for entry in (fm.get("scans") if isinstance(fm.get("scans"), list) else []):
        e = {"path": entry} if isinstance(entry, str) else dict(entry)
        if str(e.get("hide", "")).lower() == "true":
            continue
        rng = random.Random(f"{slug}:{e['path']}")
        e.setdefault("scale", 1.0)
        e.setdefault("tilt", round(rng.choice([-1, 1]) * rng.uniform(1.2, 3.4), 2))
        e["scale"] = float(e["scale"])
        e["tilt"] = float(e["tilt"])
        w, h = Image.open(ROOT / e["path"]).size
        e["aspect"] = round(w / h, 4)
        scans.append(e)
    # render order: reversed reading order puts scan 1 on top; z overrides that
    render = list(reversed([e for e in scans if e.get("z") != "bottom"]))
    render = [e for e in scans if e.get("z") == "bottom"] +         [e for e in render if e.get("z") != "top"] +         [e for e in render if e.get("z") == "top"]
    scans = render

    return {
        "file": str(path.relative_to(ROOT)),
        "scans": scans,
        "title": fm.get("title", ""),
        "language": fm.get("language", ""),
        "section": fm.get("section", ""),
        "batch": fm.get("batch", ""),
        "number": int(fm.get("number", 0)),
        "image": scans[-1]["path"] if scans else "",
        "photo": fm.get("photo", "") or "",
        "slug": fm.get("slug", "") or "",
        "description": conv(desc_m.group(1).strip()) if desc_m else "",
        "ingredients": items(section("Ingredients"), r"\*"),
        "instructions": items(section("Instructions"), r"\d+\."),
        "notes": items(section("Notes"), r"\*"),
        "original": orig_m.group(1).strip() if orig_m else "",
    }


def main():
    batch = sys.argv[1] if len(sys.argv) > 1 else None
    recipes = []
    for path in sorted(set(ROOT.glob("assets/*/**/*.md"))):
        r = parse_md(path)
        if not r:
            continue
        if batch and r["batch"] != batch:
            continue
        recipes.append(r)
    seen = {r["file"] for r in recipes}
    assert len(seen) == len(recipes), "duplicate recipe files"
    recipes.sort(key=lambda r: (SECTIONS.index(r["section"]) if r["section"] in SECTIONS else 99, r["number"]))
    out = ROOT / "print" / "recipes.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(recipes, ensure_ascii=False, indent=1))
    print(f"wrote {out.relative_to(ROOT)}: {len(recipes)} recipes")


if __name__ == "__main__":
    main()
