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



def unquote(v):
    """Strip surrounding double quotes only as a matching pair, so a value like
    '"Eskimo" Cake' survives verbatim."""
    v = v.strip()
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        return v[1:-1]
    return v

def smart_quotes(t):
    """Curl straight double-quote pairs for print ("Eskimo" -> “Eskimo”)."""
    return re.sub(r'"([^"]+)"', "“\\1”", t)


def bind_orphan(t):
    """Join the last two words with a non-breaking space so a paragraph can
    never end in a single-word orphan line; the pair wraps together."""
    i = t.rstrip().rfind(" ")
    if i > 0:
        t = t[:i] + "\u00a0" + t[i + 1:]
    return t


def clean_original(text):
    """Original blocks print verbatim, so markdown-isms in the .md would print
    literally. Split into labeled segments and strip transcription markup:
    `#### IMG_NNNN` lines are scan provenance (never printed), other `####`
    lines label a segment, `---` breaks a segment without a label, and
    bullet/bold markers are transcription conventions not in the manuscript."""
    segs, label, cur = [], "", []

    def flush(next_label):
        nonlocal label, cur
        body = "\n".join(cur).strip("\n")
        if body.strip() or label:
            segs.append({"label": label, "text": body})
        label, cur = next_label, []

    for line in text.splitlines():
        s = line.strip()
        if re.fullmatch(r"#{3,4} IMG_\d+", s):
            continue
        m = re.fullmatch(r"#{3,4} (.+)", s)
        if m:
            flush(m.group(1))
            continue
        if s == "---":
            flush("")
            continue
        line = re.sub(r"^(\s*)\* ", r"\1", line)
        cur.append(re.sub(r"\*\*(.+?)\*\*", r"\1", line))
    flush("")
    # Mkhedruli fills its line box much more than Cyrillic/Latin, so the
    # template gives Georgian segments extra line spacing to look equally airy
    for seg in segs:
        seg["georgian"] = bool(re.search(r"[ა-ჿ]", seg["text"]))
    return segs


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
                fm[key].append({k2.strip(): unquote(v2)})
            else:
                fm[key].append(item)
        elif line.startswith("    ") and key and fm[key] and isinstance(fm[key][-1], dict):
            k2, v2 = line.strip().split(":", 1)
            fm[key][-1][k2.strip()] = unquote(v2)
        elif ":" in line:
            k, v = line.split(":", 1)
            k, v = k.strip(), unquote(v)
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
            if line.startswith("- "):
                print(f"warn: {path.name} uses '-' bullets — the standard is '*' "
                      "(run scripts/normalize_md.py); item would not print")
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
        e["slot"] = len(scans)          # reading position drives layout slot
        e["dx"] = float(e.get("dx", 0))  # optional art-direction nudge (pt)
        e["dy"] = float(e.get("dy", 0))
        scans.append(e)
    # render order: reversed reading order puts scan 1 on top; z overrides that
    render = list(reversed([e for e in scans if e.get("z") != "bottom"]))
    render = [e for e in scans if e.get("z") == "bottom"] +         [e for e in render if e.get("z") != "top"] +         [e for e in render if e.get("z") == "top"]
    scans = render

    return {
        "file": str(path.relative_to(ROOT)),
        "scans": scans,
        # A `|` in the title is a print-only break hint: it wraps the title at a
        # chosen point on the verso. Every other consumer (index, ToC, web, see_also)
        # gets the clean title. Straight quote pairs curl for print; the .md
        # stays plain.
        "title": bind_orphan(smart_quotes(re.sub(r"\s*\|\s*", " ", fm.get("title", "")).strip())),
        "title_print": "|".join(bind_orphan(seg.strip())
            for seg in smart_quotes(fm.get("title", "").strip()).split("|")),
        "language": fm.get("language", ""),
        "section": fm.get("section", ""),
        "batch": fm.get("batch", ""),
        "number": int(fm.get("number", 0)),
        "image": scans[-1]["path"] if scans else "",
        # a photo mid-replacement (file deleted, regen pending) must not break
        # the build: fall back to the field color and warn
        "photo": (fm.get("photo", "") or "") if (ROOT / (fm.get("photo") or "x")).is_file() else
                 (print(f"warn: missing photo for {path.name}, rendering field color") or ""),
        "inverse": str(fm.get("inverse", "")).lower() == "true",
        "see_also": [e if isinstance(e, dict) else {"slug": e} for e in (fm.get("see_also") or []) if e],
        "scribe": fm.get("scribe", "") or "",
        "scribe_confidence": int(fm.get("scribe_confidence", 0) or 0),
        "slug": fm.get("slug", "") or "",
        "description": bind_orphan(conv(desc_m.group(1).strip())) if desc_m else "",
        "ingredients": items(section("Ingredients"), r"\*"),
        "instructions": items(section("Instructions"), r"\d+\."),
        "notes": items(section("Notes"), r"\*"),
        "original": clean_original(orig_m.group(1).strip()) if orig_m else [],
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

    # Resolve see_also slugs -> section/number/title at BUILD time. Slugs are frozen;
    # numbers are not, so nothing downstream ever stores a number.
    by_slug = {r["slug"]: r for r in recipes}
    broken = []
    for r in recipes:
        for ref in r["see_also"]:
            tgt = by_slug.get(ref["slug"])
            if tgt is None:
                broken.append(f'{r["slug"]} -> {ref["slug"]}')
                continue
            ref["section"] = tgt["section"]
            ref["number"] = tgt["number"]
            ref["title"] = tgt["title"]
    if broken:
        raise SystemExit("broken see_also references:\n  " + "\n  ".join(broken))
    out = ROOT / "print" / "recipes.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(recipes, ensure_ascii=False, indent=1))
    print(f"wrote {out.relative_to(ROOT)}: {len(recipes)} recipes")


if __name__ == "__main__":
    main()
