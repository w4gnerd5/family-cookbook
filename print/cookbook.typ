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

#let cur-slug = state("slug", "")

#let label-text(content, fill: color-label) = text(
  font: font-sans, size: size-label, fill: fill,
  tracking: label-tracking, weight: "medium", upper(content),
)

#let footer-line = context {
  let slug = cur-slug.get()
  let pg = counter(page).display()
  let line = label-text("family-cookbook / " + slug + "  ·  " + pg)
  if calc.even(here().page()) { align(left, line) } else { align(right, line) }
}

#set page(width: PW, height: PH, fill: color-paper,
  margin: (x: M + B, bottom: M + B, top: M + B),
  footer: pad(bottom: B, footer-line))

#let md(s) = eval(s, mode: "markup")

#let subhead(content) = block(above: space-block, below: space-label-gap, label-text(content))

#let card-img(scan, width) = image("cards/" + scan.split("/").last(), width: width)

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
  // 2 scans stack as a deck (underneath card peeks out) so the title zone stays clear
  let tilts = (1.8deg, -2.6deg)
  for (i, s) in r.scans.enumerate().rev() {
    place(top + right, dx: -(B + M * 0.7) - i * 48pt, dy: 62% - 215pt + i * 30pt,
      rotate(tilts.at(calc.rem(i, 2)), card-img(s, 255pt)))
  }
}

#let verso-snapshot(r) = {
  // full field, cards scattered loosely, text lower-left
  if r.photo != "" {
    place(top + left, image("../" + r.photo, width: 100%, height: 100%, fit: "cover"))
  } else {
    place(top + left, rect(width: 100%, height: 100%, fill: color-field))
  }
  let n = r.scans.len()
  let w = if n == 3 { 235pt } else { 195pt }
  let tilts = (-3deg, 2.4deg, -1.6deg, 3.2deg, -2.2deg)
  for (i, s) in r.scans.enumerate() {
    let col = calc.rem(i, 2)
    let row = calc.floor(i / 2)
    place(top + left,
      dx: B + M * 0.8 + col * (w + 30pt) + row * 22pt,
      dy: B + M * 0.8 + row * (w * 0.72) + col * 18pt,
      rotate(tilts.at(calc.rem(i, 5)), card-img(s, w)))
  }
  place(bottom + left, dx: B + M, dy: -(B + M * 0.9),
    block(width: 55% - M, title-block(r)))
}

#let verso(r) = {
  pagebreak(to: "even", weak: true)
  page(margin: 0pt, footer: none, {
    if r.scans.len() <= 2 { verso-band(r) } else { verso-snapshot(r) }
    place(bottom + left, dx: B + M, dy: -(B + 24pt),
      label-text("family-cookbook / " + r.slug + "  ·  ") + context label-text(counter(page).display()))
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
  cur-slug.update(r.slug)
  verso(r)
  recto(r)
}
