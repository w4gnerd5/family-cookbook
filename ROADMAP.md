# Roadmap

Working plan for the family cookbook: A4 ring-binder book plus a GitHub Pages site,
both built from the `.md` files. Checked items are done; file PRs against anything here.

## 1. Content QC (blocks print)

- [x] **Curate recipe order within each section.** Done by adversarial panel
  (cook / editor / archivist lenses, cross-critique, synthesis). Numbers are now
  FROZEN — they appear in print, the ToC, and footers.
- [~] Proof pass on the new order: order reads OK provisionally (Paul). Photos
  and small layout details still unsatisfying — folded into the layout work
  below and Nino's alpha pass, not blocking
- [x] Structural gaps fixed (shu parses; 1237 series rejoined into one recipe)
- [x] `easter-paska-kulich` description confirmed present and parsing
- [x] QC English transcriptions: ~10 spot-checked (Paul). Better than expected —
  the transcription pass had stripped self-references, weak wording and blog
  banter from the internet printouts
- [x] Georgian translations checked against scans (Paul, 2026-08-18)
- [x] Section calls resolved: current assignments stand
- [x] Duplicate hunt complete (M1-M7): 87 printed entries -> 75, nothing lost
- [x] Cross-references: `see_also:` frontmatter holds frozen SLUGS; the build
  resolves them to section + number, so renumbering can never strand a pointer
  and an unknown slug fails the build. Print shows "SECTION · N"; the website
  will render the same data as real links.
- [x] Slugs: apostrophes collapse (zeinabs, not zeinab-s); slugify fixed, all regenerated once
- [x] Slugs hand-fixed by Paul and reconciled (see_also references rewritten
  automatically). To change one later: edit `slug:`, run
  `scripts/reconcile_slugs.py` then `--apply`. Free only until something is
  printed or the site is live.
- [x] Duplicates atticed, meta notes out of printable prose, em dashes swept



## 2. Typography and layout

- [x] Default card size raised to 330pt cap (from 290). Cards may reach 30pt into
  the gutter, clear of the punch holes; title column narrowed to 44% so the
  default clears long titles
- [x] **Forgiving band-verso layout** (2026-08-18): deck steps by LEFT edges so
  under-cards peek out (b1d7ca1); gutter intrusion 55pt, punch may clip cards
  by design; title column fixed at 44% with `|` breaks; no reflow logic.
  Still open: per-recipe title column override if a recipe ever needs it.
- [ ] Art-direction pass over all 75 versos: `scale` / `tilt` / `z` / `dx` / `dy`
  on scans, `|` in the title to force a safe wrap. Expect many to need a nudge
  up or right at 330pt; multi-card versos are the fiddly ones. Satsivi wants
  `scale`; pork-and-watermelon's blank page 4 wants `hide`. Convention: small
  note scans ride on top like sticky notes offset down-right; full-size sheets
  stay full size, nudged so their writing peeks (Paul Bread done, b1d7ca1).
- [ ] Tune the 3+ scan snapshot composition (gap between card cluster and title)
- [ ] FIX THE VERSO EDITOR for bleed. It hardcodes `PW = 595.276` (A4 at trim)
  and assumes bleed 0, so since the 3mm flip its preview no longer matches the
  print: every card sits 8.5pt off in both axes and the title column is drawn
  narrow. It should read `space-bleed` from tokens.typ like it already reads the
  card tokens, and offset placement by B exactly as cookbook.typ does.
- [ ] RELATED, decide before touching it: `card.title_col` is a percentage of
  the *page* width, which now includes bleed, so the title column silently
  widened 207.9 -> 215.4pt when bleed went 0 -> 3mm and word wrap shifted with
  it. Arguably it should be a percentage of the TRIM width so bleed can never
  move text. But Paul re-noodled all 75 versos against the current (wider)
  column, so changing it now would invalidate that work. Leave it unless there
  is a reason, and if it changes, re-check his placements.
- [x] Full seam pass (2026-08-20, 201 pages): text-layer scan of every page
  boundary + visual check of all 37 spillover pages — clean. The rhythm
  guards (sticky labels, section-guard, unbreakable paragraphs,
  keep-together Original box) prevent the defect classes by construction
- [x] Method-number baseline alignment; ingredient list leading
- [x] Footer page suffix (`MAINS · 7 · 2/3`): page-within-recipe on every page,
  always shown; trailing parity blanks don't count
- [x] D band verso + B snapshot fallback, gutter margins, hymnal footers,
  seeded tilts, alpha-silhouette card shadows
- [x] fix mixed fonts for recipe ol and uls and prose (Georgian fallback now in
  the base text stack)
- [x] Normalize line spacing (leading 0.65em + one cascading 0.85em paragraph
  gap; sticky labels; Original box facsimile-tight with Georgian +25%)



## 3. Pictures

- [x] Source dish photos from free libraries (81/87 done, all attributed in
  frontmatter and CREDITS.md; 4 agents, Wikimedia Commons almost throughout)
- [x] Photo gaps closed (2026-08-18, stock-first order per Paul: curated free
  sites before Commons): bazhe + Ideal cake from Pexels, Eskimo cake is an AI
  render Paul generated (photo_source: ai-generated)
- [x] Photo quality swaps done: 1280 and 1162 replaced during the photo review;
  1278 no longer exists (atticed)
- [x] Card exposure: white-point normalization in make_cards.py (97th
  percentile -> ~247, gain capped 1.6x), per-scan `exposure:` frontmatter
  override for stubborn scans; whole cache rebaked
- [x] Colophon line disclosing illustrative images (in book.yaml colophon P3)
- [x] Full-bleed snapshot verso: white text + gradient scrim, always on
  (inverse: frontmatter flag retired 2026-08-18)

- Collaborators replace any photo via PR; CREDITS.md regenerates from frontmatter



## 4. Book furniture

- [x] Title page and half-title (BOOK-TITLE is a working placeholder — Paul
  decides the real title)
- [x] Table of contents: one recto page, two columns, numbers not page numbers
- [x] Section divider pages (odd/recto, name at outer edge; the divider's back
  is the first recipe's photo verso — revisit if tabs need a blank back)
- [x] Colophon: ordering paragraph, image disclosure, QR placeholder (real QR
  blocks on the domain decision in Production)
- [x] Dedication page: Zeinab's Georgian note, verbatim, facing the colophon
- [~] BACKLOG: scribe index at the back (follow one hand end to end). Blocked
  on attribution coverage, not on layout: 11 recipes carry a named hand
  (Zeinab 9, Rusiko 1, Nino 1), 34 are "printed", and 30 have no scribe at
  all. Worth printing after a second attribution pass with Nino
- [x] Decide: cluster-language or keep interleaved sections (decided: interleaved)



## 5. Website

- [ ] Static generator reading `recipes.json` + `web/tokens.css` (same visual grammar)
- [ ] GitHub Pages deploy; slugs become live URLs (footer slugs already printed)
- [ ] Contribution guide: how to PR a photo, a recipe, a correction
- [ ] Full-text search over transcriptions (the archival Original Text earns its keep)



## 6. Alpha release

- [x] Pre-print orphan/widow sweep: binding now covers titles (cap 10), body
  text, list items, see_also notes, and wrapped Original lines. Detected in the
  rendered PDF: 38 orphan lines -> 5, and those 5 are long words
  (consistency, proportions, khachapuri) that fill their line by design
- [ ] Print a dummy copy for Nino to mark up
- [ ] Nino's duplicate pass: several suspected dupes remain visible in print
  (her call, deferred until she has the dummy in hand)
- [ ] Fold her marks back in; only then is the order beyond provisional

## 6.5 Post-alpha cleanup (Paul, 2026-08-20)

- [ ] Consolidate the three dashboards (curation :8765, verso editor :8766,
  photo review :8767) into one master app — one server, one page, tabs
- [x] Semver for the book: version stamped in book.yaml, shown in the colophon;
  tag releases (alpha = 0.x). `scripts/release.sh`; v0.1.0 cut 2026-11-05
- [x] Central CHANGELOG.md at the root, versioned with the book
- [x] Per-recipe changelogs are NOT files — they live in git
  (`git log --follow assets/<group>/<n>/<file>.md`); the website can render
  them from history later (decided, nothing to build)

## 7. Production

- [ ] Flip bleed token to 3mm; verify full-bleed at the chosen print service
- [x] Card cache resolution decided: stay at 1800 (full quality, ~286 dpi at the
  330pt card width). File size is not worth trading for scan detail; the one
  real constraint is a printer's upload cap. `CARD_MAX_DIM` lowers it on demand,
  measured tradeoffs in README "Card resolution"
- [ ] Resolution pass for the production run: ~32 dish photos from the original
  Commons pass are 1920-class (roughly 110-150 dpi at full-bleed A4). Fine for
  the alpha dummy; for production, re-source larger originals or accept the
  softness deliberately
- [ ] Test print on binder stock: punch clearance, field color on paper, shadow
  density, and gradient-scrim banding (include an inverse verso in the test set)
- [ ] Custom domain decision for the printed QR (github.io URL is tied to the
  username; a CNAME future-proofs printed links)
- [ ] Decide how inserts are numbered: a ring binder invites added sheets, but
  per-section numbers are frozen and variants sit in adjacency blocks, so a
  khachapuri added later cannot join its block without a suffix scheme

