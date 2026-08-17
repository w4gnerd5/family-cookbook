// Family cookbook — editorial hybrid template.
// Verso: "band" layout (photo field, white band, scan cards straddling the seam);
// 3+ scans fall back to "snapshot" (full field, scattered cards).
// Build: typst compile --root .. --font-path ../assets/fonts cookbook.typ cookbook.pdf
#import "tokens.typ": *

#let B = space-bleed          // 0 for proofs; 3mm for production runs
#let M = space-page-margin
#let PW = 210mm + 2 * B
#let PH = 297mm + 2 * B

#set text(font: font-serif, size: size-body, fill: color-body, lang: "en")
#set par(leading: 0.72em, justify: false)

#let label-text(content, fill: color-label) = text(
  font: font-sans, size: size-label, fill: fill,
  tracking: label-tracking, weight: "medium", upper(content),
)

// hymnal model: SECTION · NUMBER is the finding aid; the slug is the web address
#let footer-line(r) = context {
  let id = label-text(r.section + "  ·  " + str(r.number), fill: color-accent)
  let slug = label-text("family-cookbook / " + r.slug)
  if calc.even(here().page()) {
    grid(columns: (auto, 1fr), id, align(right, slug))
  } else {
    grid(columns: (1fr, auto), slug, align(right, id))
  }
}

#let G = space-gutter         // inner margin: ring-punch strip + buffer
#set page(width: PW, height: PH, fill: color-paper, binding: left,
  margin: (inside: G + B, outside: M + B, bottom: M + B, top: M + B))

#let md(s) = eval(s, mode: "markup")

#let subhead(content) = block(above: space-block, below: space-label-gap, label-text(content))

// scans arrive from md_to_data in render order (first = bottom of the stack),
// each with path/scale/tilt resolved; tilt defaults are seeded per scan
#let card(e, base) = rotate(e.tilt * 1deg, image("cards/" + e.path.split("/").last(), width: base * e.scale))

#let title-block(r) = {
  label-text(r.section, fill: color-accent)
  v(space-label-gap)
  text(size: size-title, fill: color-ink, r.title)
  v(space-label-gap)
  text(size: size-description, style: "italic", fill: color-muted, md(r.description))
}

// ---------- verso layouts ----------
#let verso-band(r) = {
  // photo field top 62%, white band below, 1-2 cards straddle the seam
  if r.photo != "" {
    place(top + left, image("../" + r.photo, width: 100%, height: 62%, fit: "cover"))
  } else {
    place(top + left, rect(width: 100%, height: 62%, fill: color-field))
  }
  place(bottom + left, dx: B + M, dy: -(B + M * 0.9),
    block(width: 50% - M, title-block(r)))
  // 2 scans stack as a deck (underneath card peeks out) so the title zone stays clear;
  // verso is bound on its right edge: keep cards clear of the punch strip
  let n = r.scans.len()
  for (j, e) in r.scans.enumerate() {
    let k = n - 1 - j          // 0 = topmost (reading page 1)
    // tall scans are height-capped so the deck can't crash into the title block
    let w = calc.min(290pt, 340pt * e.aspect)
    place(top + right, dx: -(B + G) - k * 48pt, dy: 62% - 215pt + k * 30pt,
      card(e, w))
  }
}

#let verso-snapshot(r) = {
  // photo field with cards scattered over it; text stays on the white band below
  if r.photo != "" {
    place(top + left, image("../" + r.photo, width: 100%, height: 68%, fit: "cover"))
  } else {
    place(top + left, rect(width: 100%, height: 68%, fill: color-field))
  }
  let n = r.scans.len()
  let w = if n == 3 { 245pt } else { 205pt }
  for (j, e) in r.scans.enumerate() {
    let k = n - 1 - j          // reading page 1 takes the first grid slot, on top
    let col = calc.rem(k, 2)
    let row = calc.floor(k / 2)
    // bound on the right: scatter starts at the outside edge, stays clear of the gutter
    place(top + left,
      dx: B + M * 0.5 + col * (w + 26pt) + row * 20pt,
      dy: B + M * 0.8 + row * (w * 0.72) + col * 18pt,
      card(e, w))
  }
  place(bottom + left, dx: B + M, dy: -(B + M * 0.9),
    block(width: 60% - M, title-block(r)))
}

#let verso(r) = {
  pagebreak(to: "even", weak: true)
  page(margin: 0pt, footer: none, {
    if r.scans.len() <= 2 { verso-band(r) } else { verso-snapshot(r) }
    place(bottom + left, dx: B + M, dy: -(B + 24pt),
      block(width: PW - M - G - 2 * B, footer-line(r)))
  })
}

// ---------- recto ----------
#let ing-item(it) = if type(it) == dictionary {
  block(above: space-block * 0.7, below: 3pt, text(weight: "bold", size: size-small, it.group + ":"))
} else {
  block(above: 2.5pt, below: 0pt, md(it))
}

#let recto(r) = {
  block(breakable: false, {
    subhead("Ingredients")
    set text(size: size-small)
    for it in r.ingredients { ing-item(it) }
  })
  subhead("Method")
  // a single-step method reads as prose; numbering starts earning its keep at 2
  let steps = r.instructions.filter(it => type(it) != dictionary)
  if steps.len() == 1 and r.instructions.len() == 1 {
    block(above: 4pt, md(steps.at(0)))
  } else {
    let n = 0
    for it in r.instructions {
      if type(it) == dictionary {
        ing-item(it)
      } else {
        n += 1
        block(above: 4pt, grid(columns: (14pt, 1fr), column-gutter: 4pt,
          text(font: font-sans, size: size-small, fill: color-accent, str(n)), md(it)))
      }
    }
  }
  if r.notes.len() > 0 {
    subhead("Notes")
    set text(size: size-small)
    for it in r.notes { ing-item(it) }
  }
  // English recipes: the verso scan IS the original; the retyped text stays
  // archival in the .md but does not print. Revisit if a bilingual edition happens.
  if r.original != "" and r.language != "english" {
    v(space-block)
    block(breakable: true, stroke: (left: 1.5pt + color-accent), inset: (left: 10pt, y: 2pt), {
      label-text("Original")
      v(space-label-gap)
      set text(size: size-small, fill: color-muted, font: (font-serif, font-serif-georgian), lang: "ru")
      for line in r.original.split("\n") { block(above: 2.5pt, below: 0pt, line) }
    })
  }
}

// ---------- book ----------
#for r in json("recipes.json") {
  verso(r)
  {
    set page(footer: pad(bottom: B, footer-line(r)))
    recto(r)
  }
}
