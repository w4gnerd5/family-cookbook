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
- [ ] Art-direction pass over all 75 versos: `scale` / `tilt` / `z` / `dx` / `dy`
  on scans, `|` in the title to force a safe wrap. Expect many to need a nudge
  up or right at 330pt; multi-card versos are the fiddly ones. Satsivi wants
  `scale`; pork-and-watermelon's blank page 4 wants `hide`
- [ ] Tune the 3+ scan snapshot composition (gap between card cluster and title)
- [ ] Full seam pass over all 177 pages: widows, orphans, stranded subheads,
  long-recipe spillover
- [ ] Method-number baseline alignment; ingredient list leading
- [ ] Multi-sheet footer suffix for recipes spanning sheets (`MAINS · 7 · 2/3`)
- [x] D band verso + B snapshot fallback, gutter margins, hymnal footers,
  seeded tilts, alpha-silhouette card shadows
- [ ] fix mixed fonts for recipe ol and uls and prose
- [ ] Normalize line spacing



## 3. Pictures

- [x] Source dish photos from free libraries (81/87 done, all attributed in
  frontmatter and CREDITS.md; 4 agents, Wikimedia Commons almost throughout)
- [ ] Fill the 6 photo gaps: bazhe, Ideal cake, Eskimo cake (nothing faithful on
  free sources — Paul finds or we generate), conversions table + 2 continuation
  pages (need no photo)
- [ ] Photo quality swaps flagged by agents: 1278 crock-pot chicken (portrait,
  800px), 1280 breakfast strata (weak aesthetics), 1162 stroganoff (mediocre)
- [ ] Colophon line disclosing illustrative images
- [x] Full-bleed snapshot verso: `inverse: true` flips text to white and adds
  a bottom gradient scrim (decided; apply per photo during the art-direction pass)

- Collaborators replace any photo via PR; CREDITS.md regenerates from frontmatter



## 4. Book furniture

- [ ] Title page and half-title
- [ ] Table of contents: sections in order, recipes by number (hymnal model)
- [ ] Section divider pages (tab-ready for the binder)
- [ ] Colophon: credits, the one QR code to the site, image disclosure, and a
  paragraph stating how the book is ordered (an order this deliberate is
  invisible unless stated)
- [ ] Dedication page: Zeinab's Georgian note from IMG_1241, facing the colophon
- [ ] Scribe index at the back: follow one hand end to end
- [ ] Decide: cluster-language or keep interleaved sections (decided: interleaved)



## 5. Website

- [ ] Static generator reading `recipes.json` + `web/tokens.css` (same visual grammar)
- [ ] GitHub Pages deploy; slugs become live URLs (footer slugs already printed)
- [ ] Contribution guide: how to PR a photo, a recipe, a correction
- [ ] Full-text search over transcriptions (the archival Original Text earns its keep)



## 6. Alpha release

- [ ] Print a dummy copy for Nino to mark up
- [ ] Nino's duplicate pass: several suspected dupes remain visible in print
  (her call, deferred until she has the dummy in hand)
- [ ] Fold her marks back in; only then is the order beyond provisional

## 7. Production

- [ ] Flip bleed token to 3mm; verify full-bleed at the chosen print service
- [ ] Decide card cache resolution (PDF is ~350 MB; MAX_DIM 1200 halves it)
- [ ] Test print on binder stock: punch clearance, field color on paper, shadow
  density, and gradient-scrim banding (include an inverse verso in the test set)
- [ ] Custom domain decision for the printed QR (github.io URL is tied to the
  username; a CNAME future-proofs printed links)
- [ ] Decide how inserts are numbered: a ring binder invites added sheets, but
  per-section numbers are frozen and variants sit in adjacency blocks, so a
  khachapuri added later cannot join its block without a suffix scheme

