// Throwaway proof sheet: segment-label treatments inside the Original box.
#import "tokens.typ": *

#let recipes = json("recipes.json")
#let r = recipes.find(r => r.slug == "zeinabs-khachapuri")
#let ru = r.original.at(0)
#let ka = r.original.at(1)
// just the seam: last lines of the Russian segment, then the Georgian note
#let ru-tail = ru.text.split("\n").slice(-4)
#let ka-lines = ka.text.split("\n")

#let label-text(content, fill: color-label) = text(
  font: font-sans, size: size-label, fill: fill,
  tracking: label-tracking, weight: "medium", upper(content),
)

#let box-sample(seg-label) = block(fill: color-field, inset: 12pt, width: 100%, {
  label-text("Original")
  v(space-label-gap * 1.6)
  set text(size: size-small, fill: color-muted, font: (font-serif, font-serif-georgian), lang: "ru")
  for line in ru-tail { block(above: 4pt, below: 0pt, line) }
  seg-label
  for line in ka-lines { block(above: 5pt, below: 0pt, line) }
})

#let variants = (
  ("L1", "current: same small caps as the box header",
    block(above: 9pt, below: 8pt, label-text(ka.label))),
  ("L2", "accent small caps",
    block(above: 9pt, below: 8pt, label-text(ka.label, fill: color-accent))),
  ("L3", "serif italic, sentence case, no tracking",
    block(above: 9pt, below: 8pt, text(font: font-serif, style: "italic",
      size: size-small, fill: color-muted, "Georgian note (mid-page, between the recipes)"))),
  ("L4", "demoted caps: smaller, darker",
    block(above: 9pt, below: 8pt, text(font: font-sans, size: 6.5pt, fill: color-body,
      tracking: label-tracking, weight: "medium", upper(ka.label)))),
  ("L5", "small caps + trailing hairline",
    block(above: 9pt, below: 8pt, grid(columns: (auto, 1fr), column-gutter: 8pt,
      align: horizon, label-text(ka.label), line(length: 100%, stroke: 0.5pt + color-label)))),
  ("L6", "bold serif, like recto sub-group labels",
    block(above: 9pt, below: 8pt, text(font: font-serif, weight: "bold", size: size-small,
      fill: color-body, "Georgian note (mid-page, between the recipes):"))),
)

#set page(width: 210mm, height: auto, margin: 36pt, fill: white)
#set text(font: font-serif, size: size-body, fill: color-body)
#set par(leading: 0.65em, justify: false)

#grid(columns: (1fr, 1fr), column-gutter: 28pt, row-gutter: 30pt,
  ..variants.map(((code, name, lbl)) => {
    block(below: 8pt, text(font: font-sans, size: 9pt, weight: "bold", fill: color-ink,
      code + "  ") + text(font: font-sans, size: 9pt, fill: color-muted, name))
    box-sample(lbl)
  })
)
