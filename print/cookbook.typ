// Family cookbook — editorial hybrid template.
// Verso: "band" layout (photo field, white band, scan cards straddling the seam);
// 3+ scans fall back to "snapshot" (full field, scattered cards).
// Build: typst compile --root .. --font-path ../assets/fonts cookbook.typ cookbook.pdf
#import "tokens.typ": *

#let B = space-bleed          // 0 for proofs; 3mm for production runs
#let M = space-page-margin
#let PW = 210mm + 2 * B
#let PH = 297mm + 2 * B

// Georgian fallback rides in the base stack so stray Mkhedruli in any list or
// prose (e.g. the Paul Bread note) matches the Original box instead of hitting
// Typst's emergency fallback font
#set text(font: (font-serif, font-serif-georgian), size: size-body, fill: color-body, lang: "en")
// Rhythm cascades from here, stylesheet-style: leading is the wrapped-line gap,
// and every deliberate new line (any block without an explicit override) gets
// the same paragraph gap, always >= leading. Overrides below are exceptions:
// section labels (headings, not paragraphs) and the facsimile lines inside the
// Original box (kept tight so long originals fit one keep-together column).
#set par(leading: 0.65em, justify: false, spacing: 0.85em)
// breakable: false = no paragraph ever splits across a page break; it moves
// whole to the next page (safe: no single paragraph approaches a full column)
#set block(above: 0.85em, below: 0pt, breakable: false)

#let label-text(content, fill: color-label, size: size-label) = text(
  font: font-sans, size: size, fill: fill,
  tracking: label-tracking, weight: "medium", upper(content),
)

// hymnal model: SECTION · NUMBER is the finding aid; the slug is the web address.
// Every footer carries page-within-recipe (MAINS · 7 · 2/3) so a pulled-apart
// binder reassembles. Start/end metadata markers bound each recipe; trailing
// parity blanks fall outside the end marker and never count.
#let footer-line(r, on-photo: false) = context {
  let inv = on-photo   // on a photo the footer is always white, like the title
  let p = here().page()
  let starts = query(<recipe-start>).map(m => m.location().page())
  let ends = query(<recipe-end>).map(m => m.location().page())
  let mine = starts.filter(s => s <= p)
  let suffix = if mine.len() > 0 {
    let start = mine.last()
    let after = ends.filter(e => e >= start)
    let end = if after.len() > 0 { after.first() } else { p }
    "  ·  " + str(p - start + 1) + "/" + str(end - start + 1)
  } else { "" }
  let id = label-text(r.section + "  ·  " + str(r.number) + suffix,
    fill: if inv { white } else { color-accent }, size: size-footer)
  let slug = label-text("family-cookbook / " + r.slug,
    fill: if inv { rgb(255, 255, 255, 75%) } else { color-label }, size: size-footer)
  if calc.even(here().page()) {
    grid(columns: (auto, 1fr), column-gutter: 16pt, id, align(right, slug))
  } else {
    grid(columns: (1fr, auto), column-gutter: 16pt, slug, align(right, id))
  }
}

#let G = space-gutter         // inner margin: ring-punch strip + buffer
#set page(width: PW, height: PH, fill: color-paper, binding: left,
  margin: (inside: G + B, outside: M + B, bottom: M + B, top: M + B))

#let md(s) = eval(s, mode: "markup")

// sticky = a label never strands at a page foot; it travels with its content.
// Subheads get double the base block space above; below stays tight so the
// label hugs its own content.
#let subhead(content) = block(above: space-block * 2, below: space-label-gap, sticky: true, label-text(content))

// scans arrive from md_to_data in render order (first = bottom of the stack),
// each with path/scale/tilt resolved; tilt defaults are seeded per scan
#let card(e, base) = rotate(e.tilt * 1deg, image("cards/" + e.path.split("/").last(), width: base * e.scale))

// Text over a full-bleed photo is ALWAYS white (inv comes from the layout, not
// frontmatter — the scrim guarantees contrast) and a touch heavier: white type
// on a photo reads optically thinner than dark type on paper.
#let title-block(r, inv: false) = {
  set text(weight: "medium") if inv
  label-text(r.section, fill: if inv { white } else { color-accent })
  v(space-label-gap)
  // `|` in the frontmatter title forces the wrap here rather than wherever it lands
  text(size: size-title, fill: if inv { white } else { color-ink },
    r.at("title_print", default: r.title).split("|").map(s => s.trim()).join(linebreak()))
  v(space-label-gap)
  text(size: size-description, style: "italic",
    fill: if inv { rgb(255, 255, 255, 94%) } else { color-muted }, md(r.description))
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
  // 2 scans stack as a deck so the title zone stays clear. The deck steps by
  // LEFT edges: a smaller under-card peeks out past the card above it instead
  // of hiding inside its footprint. Cards may reach card-gutter-intrude into
  // the gutter (verso is bound on its right edge).
  let ordered = r.scans.sorted(key: e => e.slot)
  let lefts = (:)
  for (i, e) in ordered.enumerate() {
    // tall scans are height-capped so the deck can't crash into the title block
    let w = calc.min(card-cap, card-ref * e.aspect) * e.scale
    let x = if i == 0 { PW - (B + G - card-gutter-intrude) - w }
      else { lefts.at(ordered.at(i - 1).path) - 48pt }
    lefts.insert(e.path, x + e.dx * 1pt)
  }
  for e in r.scans {   // layout slot = reading position; array order = stacking
    place(top + left,
      dx: lefts.at(e.path),
      dy: 62% - 215pt + e.slot * 30pt + e.dy * 1pt,
      card(e, calc.min(card-cap, card-ref * e.aspect)))
  }
}

#let verso-snapshot(r) = {
  // full-bleed photo, cards scattered over it, text on the image
  // (inverse: true in frontmatter flips the text to white for dark photos)
  if r.photo != "" {
    place(top + left, image("../" + r.photo, width: 100%, height: 100%, fit: "cover"))
  } else {
    place(top + left, rect(width: 100%, height: 100%, fill: color-field))
  }
  // legibility scrim, always on: aggressive enough that white text wins on any
  // photo, easing in so the photo's midfield stays clean
  place(bottom + left, rect(width: 100%, height: 48%,
    fill: gradient.linear(dir: ttb, (rgb(0, 0, 0, 0%), 0%),
      (rgb(0, 0, 0, 32%), 40%), (rgb(0, 0, 0, 74%), 100%))))
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
    block(width: card-title-col-snapshot - M, title-block(r, inv: true)))
}

#let verso(r) = {
  pagebreak(to: "even", weak: true)
  page(margin: 0pt, footer: none, {
    [#metadata(r.slug)<recipe-start>]
    if r.scans.len() <= 2 { verso-band(r) } else { verso-snapshot(r) }
    place(bottom + left, dx: B + M, dy: -(B + 24pt),
      block(width: PW - M - G - 2 * B, footer-line(r, on-photo: r.scans.len() > 2)))
  })
}

// ---------- recto ----------
#let ing-item(it) = if type(it) == dictionary {
  block(above: space-block * 0.7, below: 3pt, sticky: true, text(weight: "bold", size: size-small, it.group + ":"))
} else {
  block(md(it))
}

// Section break policy: the first two items ride with the header (so at least
// three lines stand before any break), the last two items bind together (so a
// lone item can never sit alone overleaf), and a section of <= 4 items never
// breaks at all. The wrapper blocks inherit breakable: false from the cascade.
#let section-guard(items) = if items.len() <= 4 {
  block(items.join())
} else {
  block(items.slice(0, 2).join())
  items.slice(2, items.len() - 2).join()
  block(items.slice(items.len() - 2).join())
}

#let recto(r) = {
  block(breakable: false, {
    subhead("Ingredients")
    // ingredients and method both read at body size; notes/see-also demure
    for it in r.ingredients { ing-item(it) }
  })
  subhead("Instructions")
  // a single-step method reads as prose; numbering starts earning its keep at 2
  let steps = r.instructions.filter(it => type(it) != dictionary)
  if steps.len() == 1 and r.instructions.len() == 1 {
    block(md(steps.at(0)))
  } else {
    let n = 0
    let rendered = ()
    for it in r.instructions {
      if type(it) == dictionary {
        rendered.push(ing-item(it))
      } else {
        n += 1
        rendered.push(block(grid(columns: (10.5pt, 1fr), column-gutter: 3.5pt,
          text(font: font-sans, size: size-small, fill: color-accent, str(n)), md(it))))
      }
    }
    section-guard(rendered)
  }
  if r.notes.len() > 0 {
    subhead("Notes")
    set text(size: size-small)
    section-guard(r.notes.map(ing-item))
  }
  // Cross-references: authored as frozen slugs in frontmatter, resolved to
  // section + number at build time so renumbering can never strand a pointer.
  if r.see_also.len() > 0 {
    let phrase = (
      variant: "Another version",
      uses: "Made with",
      pairs: "Goes with",
    )
    subhead("See also")
    set text(size: size-small)
    section-guard(r.see_also.map(ref => {
      let lead = phrase.at(ref.at("rel", default: ""), default: "See")
      block({
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
    }))
  }
  // English recipes: the verso scan IS the original; the retyped text stays
  // archival in the .md but does not print. Revisit if a bilingual edition happens.
  if r.original.len() > 0 and r.language != "english" {
    v(space-block)
    // keep-together: the box never breaks; it pushes whole to the next page.
    // Safe while no original exceeds one text column (longest today: shu, ~650pt).
    block(breakable: false, fill: color-original-bg, inset: 12pt, width: 100%, {
      label-text("Original")
      v(space-label-gap * 1.6)
      set text(size: size-small, fill: color-muted, font: (font-serif, font-serif-georgian), lang: "ru")
      // segments come from md_to_data: #### labels in the .md become styled
      // sub-labels here; --- breaks a segment without one. Line gaps stay fixed
      // (facsimile, outside the paragraph rhythm); Georgian gets 25% more
      // because Mkhedruli fills its line box and looks tighter at equal gaps.
      for (i, seg) in r.original.enumerate() {
        let gap = if seg.at("georgian", default: false) { 5pt } else { 4pt }
        if i > 0 { v(7pt) }
        // block spacing collapses to max(below, next.above), so the label's
        // below must EXCEED the line gap or it does nothing.
        // Bold serif + colon, matching the recto sub-group label convention.
        if seg.label != "" {
          block(above: 9pt, below: gap + 3pt, sticky: true,
            text(weight: "bold", fill: color-body, seg.label + ":"))
        }
        for line in seg.text.split("\n") { block(above: gap, below: 0pt, line) }
      }
    })
  }
}

// ---------- front matter ----------
// Sheet plan: 1 half-title / 2 blank · 3 title / 4 colophon · 5 dedication
// (facing the colophon across the spread) / 6 blank · 7+ contents.
// BOOK-TITLE is a working title; Paul decides the real one.
#let BOOK-TITLE = "Family Cookbook"

#page({
  align(center + horizon, label-text(BOOK-TITLE, fill: color-label))
})

#pagebreak(to: "odd", weak: true)
#page({
  align(center + horizon, {
    label-text("The " + lower(BOOK-TITLE) + " of")
    v(14pt)
    text(size: 34pt, fill: color-ink, "Paul & Nino Wagner")
    v(14pt)
    label-text("Georgian · Russian · Ukrainian · Armenian", fill: color-accent)
  })
})

// colophon lands on the title sheet's back (verso) by natural flow
#page({
  set text(size: size-small, fill: color-muted)
  set par(leading: 0.65em, spacing: 0.85em)
  align(bottom, block(width: 80%, {
    par[Family recipes from Georgian, Russian, Ukrainian, and Armenian
      kitchens, collected from handwritten cards, notebooks, and internet
      printouts. Scanned, transcribed, and typeset in 2026.]
    par[Recipes are numbered within their section, and a number never changes
      once printed. The order is deliberate. Variants of the same dish sit
      next to each other, and Zeinab's notebook runs through the whole book
      rather than sitting in one block. Sheets added to the binder later
      take the next free number in their section.]
    par[Dish photographs are illustrative. Most come from free photo
      libraries and are credited at the address below; a few are AI
      renderings where no faithful photograph exists. The scans are the
      real thing.]
    v(6pt)
    // QR placeholder until the domain decision lands (roadmap: Production)
    rect(width: 44pt, height: 44pt, stroke: 0.5pt + color-label,
      align(center + horizon, label-text("QR")))
    v(2pt)
    label-text("family-cookbook — domain pending")
  }))
})

// dedication: Zeinab's Georgian note from IMG_1241, verbatim, facing the colophon
#page({
  align(center + horizon, block(width: 75%, {
    set text(font: (font-serif, font-serif-georgian), size: size-description)
    set par(leading: 0.85em)
    align(center, [
      ჩემო სიცოცხლე და სიყვარულო. \
      ეს ვეფხისტყაოსანს ჰგავს, მაგრამ \
      ყველაფერი დაწვრილებით ჩაგიწერე, \
      თორემ ძნელი სულ არ არის. \
      აბა შენ იცი, არ შემარცხვინო.
    ])
    v(14pt)
    set text(size: size-small, style: "italic", fill: color-muted)
    align(center, [My life and my love. This looks like the Vepkhistqaosani,
      but I wrote everything out for you in detail; it really isn't
      difficult. Now it's up to you — don't embarrass me.])
    v(10pt)
    align(center, label-text("Zeinab, mid-page in her notebook, between recipes"))
  }))
})

// ---------- table of contents ----------
#pagebreak(to: "odd", weak: true)
#page({
  let recipes = json("recipes.json")
  // the label rides in the top margin band (place = no flow height), because
  // the two-column list needs the full text column to fit on one page
  place(top + left, dy: -26pt, label-text("Contents"))
  set text(size: size-small)
  columns(2, gutter: 24pt, {
    let cur = ""
    for r in recipes {
      if r.section != cur {
        cur = r.section
        block(above: space-block, below: space-label-gap, sticky: true,
          label-text(cur, fill: color-accent))
      }
      block(grid(columns: (16pt, 1fr), column-gutter: 6pt,
        text(font: font-sans, size: size-footer, fill: color-accent, str(r.number)),
        text(fill: color-body, r.title)))
    }
  })
})

// ---------- book ----------
#let divider(section) = {
  pagebreak(to: "odd", weak: true)
  page(footer: none, {
    // tab position: name at the outer (left, since dividers land on rectos'
    // odd pages... they bind right) edge, vertically upper third
    place(right + top, dy: 25%,
      align(right, text(size: 30pt, fill: color-ink, section)))
  })
}

#let recipes = json("recipes.json")
#for (i, r) in recipes.enumerate() {
  if i == 0 or recipes.at(i - 1).section != r.section {
    divider(r.section)
  }
  verso(r)
  {
    set page(footer: pad(bottom: B, footer-line(r)))
    recto(r)
    [#metadata(r.slug)<recipe-end>]   // marks the last content page
  }
}
