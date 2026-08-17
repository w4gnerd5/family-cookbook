#!/usr/bin/env python3
"""
Normalize Georgian recipe .md files before CSV generation.

Transformations applied:
  1. Frontmatter: add if missing (requires metadata dict); skip if present
  2. Headings: strip trailing colons from ## and ### lines
  3. Ingredients: strip blockquote '>' prefixes; ensure each item is '* ...'
  4. Instructions: strip blockquote '>' prefixes; ensure each step is '1. ...' (renumbered)
  5. Notes: strip blockquote '>' prefixes; ensure each item is '* ...'
  6. Original Text: strip blockquote '>' prefixes; leave as plain text
  7. Trim multiple consecutive blank lines to one; ensure single trailing newline

Usage:
    python3 scripts/normalize_md.py [file1.md file2.md ...]
    # or pass no args to dry-run on all georgian .md files
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text):
    """Return (frontmatter_dict, body_text) or ({}, full_text) if none."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    fm = {}
    for line in fm_block.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"')
    return fm, body


def render_frontmatter(fm):
    """Render a frontmatter dict back to a YAML block."""
    lines = ["---"]
    for k, v in fm.items():
        # Quote values that contain special chars or are empty
        if v == "" or any(c in v for c in ':#&*?|>{}"\''):
            lines.append(f'{k}: "{v}"')
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section parsing
# ---------------------------------------------------------------------------

def split_sections(body):
    """
    Split body into a list of (heading_line, content_lines) tuples.
    heading_line is the raw heading string (e.g. '## Ingredients') or None
    for the preamble before the first heading.
    """
    sections = []
    current_heading = None
    current_lines = []

    for line in body.splitlines():
        m = re.match(r"^(#{1,3}) (.+)", line)
        if m:
            sections.append((current_heading, current_lines))
            current_heading = line
            current_lines = []
        else:
            current_lines.append(line)

    sections.append((current_heading, current_lines))
    return sections


def heading_level(heading_line):
    if heading_line is None:
        return 0
    m = re.match(r"^(#{1,3}) ", heading_line)
    return len(m.group(1)) if m else 0


def heading_name(heading_line):
    """Return heading text with trailing colon stripped."""
    if heading_line is None:
        return ""
    text = re.sub(r"^#{1,3} ", "", heading_line).rstrip(":")
    return text.strip()


# ---------------------------------------------------------------------------
# Line-level normalizers
# ---------------------------------------------------------------------------

def strip_blockquote(line):
    """Remove leading '> ' or '>' from a line."""
    return re.sub(r"^>\s?", "", line)


def is_blank(line):
    return line.strip() == ""


def is_bold_label(line):
    """Lines like '**Stage I:**' or '**For the Cream:**' — sub-group labels.
    Also catches inline-bold-label instructions like '**Stage I:** Do the thing...'
    that are the only content on a step line (i.e. the label IS the step text).
    """
    return bool(re.match(r"^\*\*.+\*\*:?\s*$", line.strip()))


def normalize_ingredients(lines):
    """
    Strip blockquotes, keep bold sub-group labels as-is,
    ensure every item line starts with '* '.

    Handles these source patterns:
      > * **Label:**       → **Label:**   (bold bullet used as sub-group header)
      >   * item           → * item       (indented sub-item)
      > * item             → * item       (regular item)
      > **Label:**         → **Label:**   (bare bold label)
    """
    out = []
    for line in lines:
        stripped = strip_blockquote(line)
        if is_blank(stripped):
            continue

        # "* **Label:**" — bold label wrapped in a list bullet
        m_labeled_bullet = re.match(r"^[\*\-]\s+(\*\*.+\*\*:?)\s*$", stripped)
        if m_labeled_bullet:
            label = re.sub(r":?\*\*:?\s*$", ":**", m_labeled_bullet.group(1).rstrip())
            out.append("")
            out.append(label)
            continue

        # Bare bold label line e.g. "**Stage I:**"
        if is_bold_label(stripped):
            label = re.sub(r":?\*\*:?\s*$", ":**", stripped.rstrip())
            out.append("")
            out.append(label)
            continue

        # Everything else — strip all leading bullet/indent chars, re-add '* '
        item = re.sub(r"^[\s\*\-•]+", "", stripped).strip()
        if item:
            out.append(f"* {item}")

    while out and out[0] == "":
        out.pop(0)
    return out


def normalize_instructions(lines):
    """
    Strip blockquotes, keep bold sub-group labels as-is (only when the label
    is the entire line), renumber all step lines as '1. ', '2. ', etc.
    (restarting after each sub-group label).
    """
    out = []
    counter = 1
    for line in lines:
        stripped = strip_blockquote(line)
        if is_blank(stripped):
            continue
        if is_bold_label(stripped):
            # Pure label line (e.g. "**To Prepare the Cream:**") — treat as sub-heading
            label = re.sub(r":?\*\*:?\s*$", ":**", stripped.rstrip())
            out.append("")
            out.append(label)
            counter = 1
        else:
            # Strip any existing leading number like "1." or "1)" and/or bullet marker
            step = re.sub(r"^(\d+[\.\)]\s*)?([*\-]\s+)?", "", stripped).strip()
            if step:
                out.append(f"{counter}. {step}")
                counter += 1
    while out and out[0] == "":
        out.pop(0)
    return out


def normalize_notes(lines):
    """
    Strip blockquotes; ensure each note is a '* ' bullet.
    Loose paragraphs get wrapped as a single bullet.
    """
    out = []
    para_lines = []

    def flush_para():
        if para_lines:
            text = " ".join(para_lines).strip()
            if text:
                out.append(f"* {text}")
            para_lines.clear()

    for line in lines:
        stripped = strip_blockquote(line)
        if is_blank(stripped):
            flush_para()
            continue
        # Already a bullet?
        m_bullet = re.match(r"^[\*\-]\s+(.*)", stripped)
        if m_bullet:
            flush_para()
            out.append(f"* {m_bullet.group(1).strip()}")
        else:
            # Accumulate as paragraph
            para_lines.append(stripped)

    flush_para()
    return out


def normalize_original_text(lines):
    """Just strip blockquote markers; preserve everything else as-is."""
    return [strip_blockquote(l) for l in lines]


# ---------------------------------------------------------------------------
# Blank-line collapsing
# ---------------------------------------------------------------------------

def collapse_blanks(lines):
    """Collapse runs of 2+ blank lines to exactly one."""
    out = []
    prev_blank = False
    for line in lines:
        if is_blank(line):
            if not prev_blank:
                out.append("")
            prev_blank = True
        else:
            out.append(line)
            prev_blank = False
    return out


# ---------------------------------------------------------------------------
# Main normalization
# ---------------------------------------------------------------------------

SECTION_NORMALIZERS = {
    "Ingredients": normalize_ingredients,
    "Instructions": normalize_instructions,
    "Notes": normalize_notes,
}


def normalize_body(body):
    sections = split_sections(body)
    out_lines = []

    for heading_line, content_lines in sections:
        if heading_line is None:
            # Preamble (title + description)
            out_lines.extend(content_lines)
            continue

        # Normalize heading: strip trailing colon
        clean_heading = re.sub(r":(\s*)$", r"\1", heading_line).rstrip()
        out_lines.append(clean_heading)

        name = heading_name(heading_line)

        # Find the matching normalizer (partial match for "Original ... Text")
        normalizer = None
        for key, fn in SECTION_NORMALIZERS.items():
            if name == key:
                normalizer = fn
                break
        if normalizer is None and name.startswith("Original"):
            normalizer = normalize_original_text

        if normalizer:
            normalized = normalizer(content_lines)
            out_lines.append("")  # blank line after heading
            out_lines.extend(normalized)
            out_lines.append("")  # trailing blank
        else:
            # Unknown section — pass through as-is (sub-headings inside sections)
            out_lines.extend(content_lines)

    return collapse_blanks(out_lines)


def normalize_file(path, dry_run=False):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    fm, body = parse_frontmatter(original)
    normalized_lines = normalize_body(body)
    normalized_body = "\n".join(normalized_lines).strip() + "\n"

    new_text = render_frontmatter(fm) + "\n\n" + normalized_body

    if new_text == original:
        print(f"  OK (no changes): {os.path.basename(path)}")
        return False

    if dry_run:
        print(f"  WOULD CHANGE: {os.path.basename(path)}")
        # Show a diff summary
        orig_lines = original.splitlines()
        new_lines = new_text.splitlines()
        changes = sum(1 for a, b in zip(orig_lines, new_lines) if a != b)
        changes += abs(len(orig_lines) - len(new_lines))
        print(f"    ~{changes} lines differ")
        return True

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"  NORMALIZED: {os.path.basename(path)}")
    return True


def main():
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        # Default: all georgian .md files
        georgian_dir = os.path.join(REPO_ROOT, "assets", "georgian")
        paths = sorted(
            os.path.join(georgian_dir, f)
            for f in os.listdir(georgian_dir)
            if f.endswith(".md")
        )

    dry_run = "--dry-run" in paths
    paths = [p for p in paths if p != "--dry-run"]

    changed = 0
    for path in paths:
        if normalize_file(path, dry_run=dry_run):
            changed += 1

    print(f"\n{'Would change' if dry_run else 'Changed'} {changed}/{len(paths)} files.")


if __name__ == "__main__":
    main()
