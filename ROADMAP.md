# Roadmap

Working plan for the family cookbook: A4 ring-binder book plus a GitHub Pages site,
both built from the `.md` files. Checked items are done; file PRs against anything here.

## 1. Content QC (blocks print)

- [ ] **Curate recipe order within each section.** Current order is accession order
  (English tree first, then Georgian, by scan number). Numbers renumber ONCE after
  curation, then freeze forever (they go in print, the ToC, and footers).
- [ ] Fix the two structural gaps: `choux-pastry-shu` (ingredients/instructions
  did not parse), `easter-paska-kulich` (no description)
- [ ] QC English transcriptions against scans (35 recipes; spot-check at minimum)
- [ ] Spot-check Georgian translations against scans
- [ ] Resolve flagged section calls: Beef Bourguignon (Soups vs Mains),
  Paska (Desserts vs Breads), the 1237 puff-pastry series
- [ ] Decide the fate of the four beef stews and two no-knead breads (keep all?)
- [x] Duplicates atticed, meta notes out of printable prose, em dashes swept

## 2. Typography and layout

- [ ] Raise the default card size on the verso (current default reads small)
- [ ] Art-direction pass over all 87 versos using the scans schema
  (`scale` / `tilt` / `z` / `hide`); satsivi wants `scale`, pork-and-watermelon's
  blank page 4 wants `hide`
- [ ] Tune the 3+ scan snapshot composition (gap between card cluster and title)
- [ ] Full seam pass over all 177 pages: widows, orphans, stranded subheads,
  long-recipe spillover
- [ ] Method-number baseline alignment; ingredient list leading
- [ ] Multi-sheet footer suffix for recipes spanning sheets (`MAINS · 7 · 2/3`)
- [x] D band verso + B snapshot fallback, gutter margins, hymnal footers,
  seeded tilts, alpha-silhouette card shadows

## 3. Pictures

- [ ] Source dish photos: free libraries first (Unsplash, Pexels), AI renders
  where no usable photo exists; `photo:` + `photo_source:` frontmatter per recipe
- [ ] Colophon line disclosing illustrative images
- [ ] Verso title band scrim or placement logic once real photos sit behind text
- 87 of 87 recipes currently have no photo; collaborators replace via PR

## 4. Book furniture

- [ ] Title page and half-title
- [ ] Table of contents: sections in order, recipes by number (hymnal model)
- [ ] Section divider pages (tab-ready for the binder)
- [ ] Colophon: credits, the one QR code to the site, image disclosure
- [ ] Decide: cluster-language or keep interleaved sections (decided: interleaved)

## 5. Website

- [ ] Static generator reading `recipes.json` + `web/tokens.css` (same visual grammar)
- [ ] GitHub Pages deploy; slugs become live URLs (footer slugs already printed)
- [ ] Contribution guide: how to PR a photo, a recipe, a correction
- [ ] Full-text search over transcriptions (the archival Original Text earns its keep)

## 6. Production

- [ ] Flip bleed token to 3mm; verify full-bleed at the chosen print service
- [ ] Decide card cache resolution (PDF is ~350 MB; MAX_DIM 1200 halves it)
- [ ] Test print on binder stock: punch clearance, field color on paper, shadow density
- [ ] Custom domain decision for the printed QR (github.io URL is tied to the
  username; a CNAME future-proofs printed links)
