# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Family cookbook archive (Paul & Nino Wagner) preserving recipes from Georgian, Russian, Ukrainian, and Armenian family traditions alongside modern recipes. This is a document/media archive plus a lightweight publishing pipeline — no tests or linting.

**Production pipeline:** `.md` companion files (source of truth) → `scripts/md_to_data.py` → `print/recipes.json` → Typst (`print/cookbook.typ`) → print-ready PDF. A static website built from the same `.md` files is planned; `tokens.yaml` drives the visual grammar of both outputs.

## Repository Structure

```
artifacts/          Raw JPEG scans (source material, not used in layout)
assets/             Processed PNGs + companion .md files (the working dataset)
  georgian/         48 PNGs, 51 .md
  english/          55 PNGs, 37 .md
attic/              Removed-but-preserved items (duplicates, superseded copies).
                    Never feeds any build. See attic/README.md for provenance.
batches/            Legacy CSVs from the abandoned Affinity Data Merge workflow
print/              Typst book: cookbook.typ, tokens.typ + recipes.json (generated)
web/                tokens.css (generated); static site to come
tokens.yaml         Design tokens — single source for print and web styling
recipes-index.csv   Machine-readable index (generated)
RECIPES.md          Human-readable index table (generated)
```

**File conventions:** every recipe is a folder, named after its first scan's number (e.g. `assets/english/1222/`), holding exactly one `.md`, that recipe's scan PNGs, and (eventually) its dish photo. Asset taxonomy inside a folder:

- `IMG_XXXX.png` — original scanned pages; they keep their camera names forever (provenance)
- `dish.*` — photo of the finished dish (`photo:` frontmatter points at it; `photo_source:` records the license or `ai-generated`)
- Reading order of multi-page scans is defined by the `scans:` frontmatter list, never by filename sorting

The authoritative recipe list is `RECIPES.md` — do not maintain a duplicate table here.

## Frontmatter (Source of Truth)

```yaml
---
title: Dumpling Dough with Boiling Water
language: georgian        # georgian | english
section: "Breads & Doughs"
batch: batch-1            # legacy Affinity grouping; may be retired
page: ""                  # print page number, filled after a layout run
scans:                    # ordered list of original scanned pages (reading order)
  - assets/georgian/1161/IMG_1161.png
meta: "..."               # optional; archival/provenance notes. NEVER printed.
photo: ""                 # optional; dish photo for the verso (path)
photo_source: ""          # optional; library URL + license, or "ai-generated"
slug: ""                  # optional; frozen URL slug for the website/QR — never regenerate
---
```

**Controlled vocabulary for `section`:** Breads & Doughs · Soups & Stews · Mains · Sides & Salads · Preserves & Sauces · Desserts & Sweets · Drinks · Pantry

**Printable vs meta:** everything in the `.md` body (description, ingredients, instructions, notes, original text) is printable content. Scan provenance, duplicate/superseded cross-references, and continuation bookkeeping belong in the `meta` frontmatter field, not in `## Notes`. Continuation notes are unnecessary — all scans in a recipe folder render on the verso automatically.

## Markdown Companion File Format

```markdown
# Recipe Title

Brief description with historical or cultural context.

## Ingredients

* Ingredient 1

## Instructions

1. Step one

## Notes

* **Label:** detail

### Original [Language] Text

[original text preserved verbatim for reference]
```

**Sub-group labels** (multi-component recipes): a bare bold line like `**For the Dough:**` above the items, never a heading. Canonical examples: `assets/georgian/IMG_1161.md`, `assets/georgian/IMG_1162.md`.

## Build Pipeline

Run from the repo root, in order, after editing `.md` files:

```
python3 scripts/normalize_md.py <files>      # idempotent cleanup (bullets, numbering, blank lines)
python3 scripts/md_to_data.py [batch-1]      # -> print/recipes.json (optionally one batch)
python3 scripts/build_tokens.py              # only if tokens.yaml changed -> print/tokens.typ, web/tokens.css
typst compile --root . --font-path assets/fonts print/cookbook.typ print/cookbook.pdf
python3 scripts/build_index.py               # -> recipes-index.csv, RECIPES.md (also warns on missing frontmatter)
```

Proof pages for visual inspection:
`typst compile --root . --font-path assets/fonts --format png --ppi 110 --pages 2-5 print/cookbook.typ 'page-{p}.png'`

Always look at rendered proofs after layout changes — check spreads, page breaks, widows/orphans — before reporting done.

## Print Design (print/cookbook.typ)

Editorial-hybrid direction: serif recipe text, small uppercase sans wayfinding labels, terracotta accent. Each recipe opens on a verso (left page): dish photo (or fallback field), floating scan card(s) with drop shadow, section label, title, description. Recto (right page): ingredients, accent-numbered method, notes, original-language text in an accent-ruled block; long recipes spill recto-onward. Fonts are vendored in `assets/fonts/` (OFL): Spectral (serif, Latin + Cyrillic), Inter (sans), Noto Serif Georgian. Single-step methods render as prose, not a one-item list. English recipes do not print their Original Text block (the verso scan is the original); the retyped text stays archival in the .md.

## Legacy: Affinity Publisher

The `.af` files and `batches/` CSVs are from the abandoned Affinity Data Merge workflow. Do not build on them; they are kept for reference only.
