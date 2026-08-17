#!/usr/bin/env python3
"""
Add frontmatter to the first 20 Georgian recipe .md files and generate batch-1.csv.
Run from the repo root: python3 scripts/add_frontmatter_batch1.py
"""

import os
import re
import csv

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEORGIAN_DIR = os.path.join(REPO_ROOT, "assets", "georgian")
BATCHES_DIR = os.path.join(REPO_ROOT, "batches")

# Metadata for the first 20 recipes
BATCH1_METADATA = [
    {
        "filename": "IMG_1161",
        "path": GEORGIAN_DIR,
        "title": "Dumpling Dough with Boiling Water (Super)",
        "language": "georgian",
        "section": "Breads & Doughs",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1162",
        "path": GEORGIAN_DIR,
        "title": "Lyudmila's Beef Stroganoff",
        "language": "georgian",
        "section": "Mains",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1168",
        "path": GEORGIAN_DIR,
        "title": "Traditional Georgian Bread Shaping Instructions",
        "language": "georgian",
        "section": "Breads & Doughs",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1170",
        "path": GEORGIAN_DIR,
        "title": "Khachapuri Recipe by Gia Agirba",
        "language": "georgian",
        "section": "Breads & Doughs",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1175",
        "path": GEORGIAN_DIR,
        "title": "Zeinab's Shu",
        "language": "georgian",
        "section": "Desserts & Sweets",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1176",
        "path": GEORGIAN_DIR,
        "title": "Bazhe (Georgian Walnut Sauce)",
        "language": "georgian",
        "section": "Preserves & Sauces",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1178",
        "path": GEORGIAN_DIR,
        "title": "Rusiko's Cutlets",
        "language": "georgian",
        "section": "Mains",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1180",
        "path": GEORGIAN_DIR,
        "title": "Vareniki Dough (Dumpling Dough)",
        "language": "georgian",
        "section": "Breads & Doughs",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1184",
        "path": GEORGIAN_DIR,
        "title": "Russian Pirozhki with Scalded Yeast Dough (Yields 30)",
        "language": "georgian",
        "section": "Breads & Doughs",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1185",
        "path": GEORGIAN_DIR,
        "title": "Ami's Khinkali",
        "language": "georgian",
        "section": "Mains",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1186",
        "path": GEORGIAN_DIR,
        "title": "Kefir Pancakes (Blini) with Baking Soda",
        "language": "georgian",
        "section": "Breads & Doughs",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1189",
        "path": GEORGIAN_DIR,
        "title": "Pirozhki with Scalded Yeast Dough",
        "language": "georgian",
        "section": "Breads & Doughs",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1190",
        "path": GEORGIAN_DIR,
        "title": "Czech Baklava",
        "language": "georgian",
        "section": "Desserts & Sweets",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1192",
        "path": GEORGIAN_DIR,
        "title": "Zeinab's Khachapuri",
        "language": "georgian",
        "section": "Breads & Doughs",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1195",
        "path": GEORGIAN_DIR,
        "title": "Adjarian Khachapuri",
        "language": "georgian",
        "section": "Breads & Doughs",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1198",
        "path": GEORGIAN_DIR,
        "title": "Vareniki with Boiling Water Dough",
        "language": "georgian",
        "section": "Breads & Doughs",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1199",
        "path": GEORGIAN_DIR,
        "title": "Soft Ginger Cookies",
        "language": "georgian",
        "section": "Desserts & Sweets",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1200",
        "path": GEORGIAN_DIR,
        "title": "New Seasons Market Cheesy Chilaquiles Casserole",
        "language": "georgian",
        "section": "Mains",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1201",
        "path": GEORGIAN_DIR,
        "title": "Vegetable Enchilada Casserole",
        "language": "georgian",
        "section": "Mains",
        "batch": "batch-1",
    },
    {
        "filename": "IMG_1202",
        "path": GEORGIAN_DIR,
        "title": "Zainab's Khachapuri",
        "language": "georgian",
        "section": "Breads & Doughs",
        "batch": "batch-1",
    },
]


def build_frontmatter(meta, source_image_rel):
    lines = ["---"]
    lines.append(f'title: "{meta["title"]}"')
    lines.append(f'language: {meta["language"]}')
    lines.append(f'section: "{meta["section"]}"')
    lines.append(f'batch: {meta["batch"]}')
    lines.append(f'page:')
    lines.append(f'source_image: {source_image_rel}')
    lines.append("---")
    return "\n".join(lines)


def add_frontmatter_to_file(md_path, frontmatter_str):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Skip if already has frontmatter
    if content.startswith("---"):
        print(f"  SKIP (already has frontmatter): {os.path.basename(md_path)}")
        return content
    new_content = frontmatter_str + "\n\n" + content
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  Added frontmatter: {os.path.basename(md_path)}")
    return new_content


def strip_markdown(text):
    """Strip markdown formatting for plain-text CSV output.

    - Removes bullet prefixes (* / -)
    - Removes numbered list prefixes (1. / 2. etc.)
    - Removes bold/italic markers (** / *)
    - Collapses multiple blank lines to one
    Items are separated by single newlines; sub-group labels retain their text.
    """
    lines = text.splitlines()
    out = []
    for line in lines:
        # Strip bullet prefixes: "* item" or "- item"
        line = re.sub(r"^[\*\-]\s+", "", line)
        # Strip numbered list prefixes: "1. item", "  1. item" (indented sub-lists)
        line = re.sub(r"^\s*\d+\.\s+", "", line)
        # Strip bold/italic markers: **text** or *text*
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
        line = re.sub(r"\*(.+?)\*", r"\1", line)
        out.append(line)
    # Collapse 2+ consecutive blank lines to one
    result = re.sub(r"\n{3,}", "\n\n", "\n".join(out))
    return result.strip()


def parse_section(content, section_heading):
    """Extract content under a given ## heading (normalized plain text, no blockquotes)."""
    pattern = rf"## {re.escape(section_heading)}:?\s*\n((?:(?!^##).)*)"
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    if not match:
        return ""
    raw = match.group(1)
    # Strip any residual blockquote markers for safety
    lines = [re.sub(r"^>\s?", "", line) for line in raw.splitlines()]
    return "\n".join(lines).strip()


def parse_description(content):
    """Extract the descriptive paragraph(s) between the h1 and the first ##."""
    # Remove frontmatter first
    body = re.sub(r"^---\n.*?---\n\n?", "", content, flags=re.DOTALL)
    # Remove h1
    body = re.sub(r"^# .+\n", "", body).lstrip("\n")
    # Take everything before first ##
    match = re.search(r"^##", body, re.MULTILINE)
    if match:
        desc = body[: match.start()].strip()
    else:
        desc = body.strip()
    return desc


def parse_notes(content):
    """Extract Notes section (not blockquoted — plain bullet list)."""
    match = re.search(r"## Notes:?\s*\n((?:[^#]|\n(?!#))*)", content)
    if not match:
        return ""
    raw = match.group(1)
    # Stop at next heading
    raw = re.split(r"\n##", raw)[0]
    return raw.strip()


def parse_original_text(content):
    """Extract Original text section."""
    match = re.search(r"### Original.*?\n((?:.|\n)*?)(?=\n##|\Z)", content)
    if not match:
        return ""
    return match.group(1).strip()


def parse_md(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {
        "description": strip_markdown(parse_description(content)),
        "ingredients": strip_markdown(parse_section(content, "Ingredients")),
        "instructions": strip_markdown(parse_section(content, "Instructions")),
        "notes": strip_markdown(parse_notes(content)),
        "original_text": parse_original_text(content),  # preserve as-is (source text)
    }


def main():
    os.makedirs(BATCHES_DIR, exist_ok=True)
    csv_path = os.path.join(BATCHES_DIR, "batch-1.csv")

    rows = []
    for meta in BATCH1_METADATA:
        md_path = os.path.join(meta["path"], meta["filename"] + ".md")
        png_path = os.path.join(meta["path"], meta["filename"] + ".png")

        if not os.path.exists(md_path):
            print(f"WARNING: {md_path} not found — skipping")
            continue
        if not os.path.exists(png_path):
            print(f"WARNING: {png_path} not found — image missing")

        # Relative path from repo root for source_image frontmatter
        source_image_rel = os.path.relpath(png_path, REPO_ROOT)

        fm = build_frontmatter(meta, source_image_rel)
        content_after = add_frontmatter_to_file(md_path, fm)

        parsed = parse_md(md_path)

        rows.append({
            "image_path": png_path,  # absolute path for Affinity Data Merge
            "title": meta["title"],
            "language": meta["language"],
            "section": meta["section"],
            "description": parsed["description"],
            "ingredients": parsed["ingredients"],
            "instructions": parsed["instructions"],
            "notes": parsed["notes"],
            "original_text": parsed["original_text"],
        })

    fieldnames = [
        "image_path", "title", "language", "section",
        "description", "ingredients", "instructions", "notes", "original_text"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {csv_path}")


if __name__ == "__main__":
    main()
