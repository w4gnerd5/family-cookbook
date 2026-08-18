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
#let footer-line(r, on-photo: false) = context {
  let inv = on-photo and r.at("inverse", default: false)
  let id = label-text(r.section + "  ·  " + str(r.number),
    fill: if inv { white } else { color-accent })
  let slug = label-text("family-cookbook / " + r.slug,
    fill: if inv { rgb(255, 255, 255, 75%) } else { color-label })
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

// inverse palette for full-bleed photo versos where the text sits on the image
#let title-block(r) = {
  let inv = r.at("inverse", default: false)
  label-text(r.section, fill: if inv { white } else { color-accent })
  v(space-label-gap)
  // `|` in the frontmatter title forces the wrap here rather than wherever it lands
  text(size: size-title, fill: if inv { white } else { color-ink },
    r.at("title_print", default: r.title).split("|").map(s => s.trim()).join(linebreak()))
  v(space-label-gap)
  text(size: size-description, style: "italic",
    fill: if inv { rgb(255, 255, 255, 88%) } else { color-muted }, md(r.description))
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
    block(width: card-title-col - M, title-block(r)))
  // 2 scans stack as a deck (underneath card peeks out) so the title zone stays clear;
  // verso is bound on its right edge: keep cards clear of the punch strip
  for e in r.scans {
    let k = e.slot             // layout slot = reading position; array order = stacking
    // tall scans are height-capped so the deck can't crash into the title block.
    // Cards may reach card-gutter-intrude into the gutter: the punch holes sit
    // ~9-15mm from the bound edge, so this stays clear of them.
    let w = calc.min(card-cap, card-ref * e.aspect)
    place(top + right,
      dx: -(B + G - card-gutter-intrude) - k * 48pt + e.dx * 1pt,
      dy: 62% - 215pt + k * 30pt + e.dy * 1pt,
      card(e, w))
  }
}

#let verso-snapshot(r) = {
  // full-bleed photo, cards scattered over it, text on the image
  // (inverse: true in frontmatter flips the text to white for dark photos)
  if r.photo != "" {
    place(top + left, image("../" + r.photo, width: 100%, height: 100%, fit: "cover"))
    if r.at("inverse", default: false) {
      // legibility scrim: quiet dark gradient under the text zone
      place(bottom + left, rect(width: 100%, height: 42%,
        fill: gradient.linear(dir: ttb, rgb(0, 0, 0, 0%), rgb(0, 0, 0, 55%))))
    }
  } else {
    place(top + left, rect(width: 100%, height: 100%, fill: color-field))
  }
  let n = r.scans.len()
  let w = if n == 3 { card-snapshot-3 } else { card-snapshot-4 }
  for e in r.scans {
    let k = e.slot             // layout slot = reading position; array order = stacking
    let col = calc.rem(k, 2)
    let row = calc.floor(k / 2)
    // bound on the right: scatter starts at the outside edge, stays clear of the gutter
    place(top + left,
      dx: B + M * 0.5 + col * (w + 26pt) + row * (w * 0.5) + e.dx * 1pt,
      dy: B + M * 0.6 + row * (w * 0.85) + col * 18pt + e.dy * 1pt,
      card(e, w))
  }
  place(bottom + left, dx: B + M, dy: -(B + M * 0.9),
    block(width: card-title-col-snapshot - M, title-block(r)))
}

#let verso(r) = {
  pagebreak(to: "even", weak: true)
  page(margin: 0pt, footer: none, {
    if r.scans.len() <= 2 { verso-band(r) } else { verso-snapshot(r) }
    place(bottom + left, dx: B + M, dy: -(B + 24pt),
      block(width: PW - M - G - 2 * B, footer-line(r, on-photo: r.scans.len() > 2)))
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
  // Cross-references: authored as frozen slugs in frontmatter, resolved to
  // section + number at build time so renumbering can never strand a pointer.
  if r.see_also.len() > 0 {
    let phrase = (
      variant: "Another recording",
      uses: "Made with",
      pairs: "Goes with",
    )
    subhead("See also")
    set text(size: size-small)
    for ref in r.see_also {
      let lead = phrase.at(ref.at("rel", default: ""), default: "See")
      block(above: 2.5pt, below: 0pt, {
        text(fill: color-muted, lead + ": ")
        text(fill: color-ink, ref.title)
        text(fill: color-muted, "  ")
        text(font: font-sans, size: size-label, fill: color-accent,
          tracking: label-tracking, weight: "medium",
          upper(ref.section + " · " + str(ref.number)))
        if ref.at("note", default: "") != "" {
          text(fill: color-muted, "  " + ref.note)
        }
      })
    }
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
