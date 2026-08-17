// Family cookbook — editorial hybrid template.
// Build: typst compile --root .. print/cookbook.typ print/cookbook.pdf
#import "tokens.typ": *

#set page(paper: "a4", margin: (x: space-page-margin, y: space-page-margin), fill: color-paper)
#set text(font: font-serif, size: size-body, fill: color-body, lang: "en")
#set par(leading: 0.72em, justify: false)

#let data = json("recipes.json")

#let label-text(content, fill: color-label) = text(
  font: font-sans, size: size-label, fill: fill,
  tracking: label-tracking, weight: "medium", upper(content),
)

#let subhead(content) = block(above: space-block, below: space-label-gap, label-text(content))

#let md(s) = eval(s, mode: "markup")

#let card-shadow(img) = context {
  let s = measure(img)
  box(width: s.width + 5pt, height: s.height + 5pt, {
    place(dx: 5pt, dy: 5pt, rect(width: s.width, height: s.height, fill: rgb(0, 0, 0, 22%)))
    place(box(stroke: 0.5pt + color-field.darken(15%), img))
  })
}

// ---------- verso: photo field, floating scan card, title & description ----------
#let verso(r) = {
  pagebreak(to: "even", weak: true)
  page(margin: 0pt, {
    // dish photo, or the fallback field
    if r.photo != "" {
      place(top + left, image("../" + r.photo, width: 100%, height: 100%, fit: "cover"))
    } else {
      place(top + left, rect(width: 100%, height: 100%, fill: color-field))
    }
    // title block, top of page on its own band
    place(top + left, dx: space-page-margin, dy: space-page-margin, block(width: 100% - 2 * space-page-margin, {
      label-text(r.section, fill: color-accent)
      v(space-label-gap)
      text(size: size-title, fill: color-ink, weight: "regular", r.title)
      v(space-label-gap)
      text(size: size-description, style: "italic", fill: color-muted, md(r.description))
    }))
    // scan card, offset low, drop shadow
    if r.image != "" {
      place(bottom + right, dx: -space-page-margin, dy: -space-page-margin,
        card-shadow(image("../" + r.image, width: 250pt)))
    }
  })
}

// ---------- recto: ingredients, method, notes, original text ----------
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
  if r.notes.len() > 0 {
    subhead("Notes")
    set text(size: size-small)
    for it in r.notes { ing-item(it) }
  }
  if r.original != "" {
    v(space-block)
    block(breakable: true, stroke: (left: 1.5pt + color-accent), inset: (left: 10pt, y: 2pt), {
      label-text("Original")
      v(space-label-gap)
      set text(size: size-small, fill: color-muted, font: font-serif-georgian, lang: "ru")
      for line in r.original.split("\n") { block(above: 2.5pt, below: 0pt, line) }
    })
  }
}

// ---------- book ----------
#for (i, r) in data.enumerate() {
  verso(r)
  recto(r)
}
