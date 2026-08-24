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
book.yaml           Book-level content (title, colophon, dedication, labels,
                    footer prefix, see_also phrases) — read directly by Typst;
                    the web build will consume the same file. cookbook.typ is
                    layout only: a fork touches .md files, tokens.yaml, book.yaml
recipes-index.csv   Machine-readable index (generated)
RECIPES.md          Human-readable index table (generated)
```

**`assets/georgian/` and `assets/english/` are accession groups, not categories.** They record
which scanning run an item came from, which is provenance worth keeping. The semantic field is
`language:` in frontmatter, and that is the only thing the build reads. A recipe can legitimately
sit in `assets/georgian/` with `language: english` — it means the paper was among the Georgian
family material. Do not relocate folders to match `language:`.

**File conventions:** every recipe is a folder, named after its first scan's number (e.g. `assets/english/1222/`), holding exactly one `.md`, that recipe's scan PNGs, and (eventually) its dish photo. Asset taxonomy inside a folder:

- `IMG_XXXX.png` — original scanned pages; they keep their camera names forever (provenance)
- `dish.*` — photo of the finished dish (`photo:` frontmatter points at it; `photo_source:` records the license or `ai-generated`)
- Reading order of multi-page scans is defined by the `scans:` frontmatter list, never by filename sorting

The authoritative recipe list is `RECIPES.md` — do not maintain a duplicate table here.

## Frontmatter (Source of Truth)

```yaml
---
title: Dumpling Dough with|Boiling Water   # `|` = print-only line break in the verso
                                          #   title; stripped everywhere else
slug: dumpling-dough-with-boiling-water    # FROZEN identity: printed footer, QR, web URL
language: georgian        # georgian | english
scribe: Zeinab            # optional; who wrote the scan ("printed" for printouts)
scribe_confidence: 9      # optional; 1-10
section: "Breads & Doughs"
number: 6                 # FROZEN per-section hymnal number (see Numbering below)
batch: batch-1            # legacy Affinity grouping; may be retired
meta: "..."               # optional; archival/provenance notes. NEVER printed.
scans:                    # ordered list of scanned pages (reading order)
  - assets/georgian/1161/IMG_1161.png
  - path: assets/georgian/1161/IMG_1162.png   # optional per-scan art direction
    scale: 0.7            #   relative to the layout's base card width
    tilt: -4              #   degrees; default is seeded per scan, deterministic
    z: top                #   stacking override (top | bottom); does not move the card
    dx: 130               #   nudge in pt
    dy: -30
    exposure: 1.1         #   multiplies the auto white-point gain at card bake;
                          #   0 disables normalization for this scan
    hide: true            #   keep archival, do not render on the verso
photo: ""                 # optional; dish photo for the verso (dish.* in the folder)
photo_source: ""          # optional; "URL | license | author", feeds CREDITS.md
inverse: true             # RETIRED 2026-08-18: snapshot versos always render
                          #   white text over an always-on scrim; flag is ignored
see_also:                 # optional; cross-references BY SLUG, resolved at build time
  - slug: vareniki-with-boiling-water-dough
    rel: variant          #   variant | uses | pairs (default renders "See")
    note: same technique, more egg
---
```

**Verso card sizing** lives in `tokens.yaml` under `card:` — `cap`/`ref` size the band-layout
cards, `gutter_intrude` lets a card reach into the gutter (the punch holes sit ~9-15mm from the
bound edge, so 30pt stays clear of them), `title_col` sets the title column width the card must
not overlap. Per-recipe exceptions use `scale`/`dx`/`dy` on the scan and `|` in the title.
Art direction for extra scans: small notes ride on top like a sticky note, offset down and
to the right so they clear the title; full-size sheets stay full size and are nudged so
their writing peeks out. Expect edge cases; handle them per-recipe, not with layout logic.

**Numbering (hymnal model):** recipes are numbered per section, not through the volume, so a
sheet added to the ring binder never renumbers the book. `SECTION · N` is the finding aid printed
in the footer. Numbers are FROZEN — never renumber. Cross-references store the frozen *slug*
and the build resolves it to a number, so reordering can never strand a pointer.

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

**List style is `*`, always.** `- ` bullets are invisible to the build (md_to_data
parses `*` only and warns); `scripts/normalize_md.py` converts strays.

**Sub-group labels** (multi-component recipes): a bare bold line like `**For the Dough:**` above the items, never a heading. Canonical examples: `assets/georgian/IMG_1161.md`, `assets/georgian/IMG_1162.md`.

## Build Pipeline

Run from the repo root, in order, after editing `.md` files:

```
python3 scripts/normalize_md.py <files>      # idempotent cleanup (bullets, numbering, blank lines)
python3 scripts/md_to_data.py [batch-1]      # -> print/recipes.json (optionally one batch)
python3 scripts/build_tokens.py              # only if tokens.yaml changed -> print/tokens.typ, web/tokens.css
typst compile --root . --font-path assets/fonts print/cookbook.typ print/cookbook.pdf
python3 scripts/build_index.py               # -> recipes-index.csv, RECIPES.md (also warns on missing frontmatter)
python3 scripts/build_credits.py             # -> CREDITS.md from photo_source
python3 scripts/make_cards.py                # bakes scan cards with drop shadows -> print/cards/
python3 scripts/refresh_slug_table.py        # dashboard slug audit table
```

Proof pages for visual inspection:
`typst compile --root . --font-path assets/fonts --format png --ppi 110 --pages 2-5 print/cookbook.typ 'page-{p}.png'`

Always look at rendered proofs after layout changes — check spreads, page breaks, widows/orphans — before reporting done.

## Print Design (print/cookbook.typ)

Editorial-hybrid direction: serif recipe text, small uppercase sans wayfinding labels, terracotta accent. Each recipe opens on a verso (left page): dish photo (or fallback field), floating scan card(s) with drop shadow, section label, title, description. Recto (right page): ingredients, accent-numbered method, notes, original-language text in an accent-ruled block; long recipes spill recto-onward. Fonts are vendored in `assets/fonts/` (OFL): Spectral (serif, Latin + Cyrillic), Inter (sans), Noto Serif Georgian. Single-step methods render as prose, not a one-item list. English recipes do not print their Original Text block (the verso scan is the original); the retyped text stays archival in the .md.

## Curation Tooling

Curation runs through a live dashboard, not a spreadsheet: `python3 scripts/curation_server.py`
serves `localhost:8765`, backed by the git-tracked ledger `curation-state.json` (inventory, merge
decisions, family questions, slug audit). Edits save instantly and the page polls, so it can stay
open. Never delete a ledger row — stamp its status `applied @ <commit>`.

- `scripts/verso_editor.py` — art-direction editor on `localhost:8766`: drag cards
  (dx/dy), wheel = tilt, shift+wheel = scale, z buttons; Save rewrites the recipe's
  `scans:` frontmatter (touched fields only) and reruns md_to_data. The preview
  renders the full title block (section, title, description) in the real fonts so
  card/title collisions are visible. "Proof PDF pages" saves then compiles just
  that recipe via `typst compile --input only=<slug>` (no front matter, no
  dividers) into print/preview/ and shows the pages in an overlay.
- `scripts/photo_review.py` — photo-swap review on `localhost:8767`, backed by the
  git-tracked round ledger `photo-review.json`: per recipe, each scout/judge round
  is a row with candidate thumbnails linked to their source pages, Paul's note
  telling Claude what to do, and Claude's after-action comment once done. Rounds
  are append-only; thumbs cache in `print/photo-cands/` (gitignored).
- `scripts/apply_curation.py` — executes ledger edits (cuts to `attic/`, section moves, renumbering)
- `scripts/reconcile_slugs.py` — after hand-edited slugs: diffs by recipe ID, rewrites `see_also:`
  references, blocks collisions, refreshes the baseline
- `attic/` holds everything removed from the collection, with provenance in `attic/README.md`.
  Nothing is ever deleted.

## Legacy: Affinity Publisher

The `.af` files and `batches/` CSVs are from the abandoned Affinity Data Merge workflow. Do not build on them; they are kept for reference only.
