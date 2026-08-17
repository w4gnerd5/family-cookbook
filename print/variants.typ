// Verso layout variants for noodling — one per page.
// typst compile --root .. --font-path ../assets/fonts variants.typ
#import "tokens.typ": *

#set page(paper: "a4", margin: 0pt, fill: color-paper)
#set text(font: font-serif, size: size-body, fill: color-body)

#let r = json("recipes.json").at(0)
#let card = "cards/IMG_1161.png"
#let M = space-page-margin

#let lab(content, fill: color-label) = text(
  font: font-sans, size: size-label, fill: fill,
  tracking: label-tracking, weight: "medium", upper(content))

#let title-block(align-center: false) = {
  set align(if align-center { center } else { left })
  lab(r.section, fill: color-accent)
  v(space-label-gap)
  text(size: size-title, fill: color-ink, r.title)
  v(space-label-gap)
  text(size: size-description, style: "italic", fill: color-muted, eval(r.description, mode: "markup"))
}

#let footer-slug = place(bottom + left, dx: M, dy: -24pt,
  lab("family-cookbook / dumpling-dough  ·  12"))

#let tag(name) = place(top + right, dx: -8pt, dy: 8pt,
  box(fill: color-accent, inset: 5pt, text(font: font-sans, size: 8pt, fill: white, name)))

// A — anchor: title top-left, card bottom-right (status quo, baked shadow)
#page({
  place(top + left, rect(width: 100%, height: 100%, fill: color-field))
  place(top + left, dx: M, dy: M, block(width: 100% - 2 * M, title-block()))
  place(bottom + right, dx: -M * 0.6, dy: -M * 0.6, image(card, width: 300pt))
  footer-slug
  tag("A  anchor")
})

// B — snapshot: big tilted card upper-right, text lower-left
#page({
  place(top + left, rect(width: 100%, height: 100%, fill: color-field))
  place(top + right, dx: -M * 0.5, dy: M * 0.7, rotate(-2.5deg, image(card, width: 330pt)))
  place(bottom + left, dx: M, dy: -M * 1.6, block(width: 55% - M, title-block()))
  footer-slug
  tag("B  snapshot")
})

// C — museum: centered artifact, centered type, maximum air
#page({
  place(top + center, dy: M * 1.2, block(width: 70%, title-block(align-center: true)))
  place(center + horizon, dy: 40pt, image(card, width: 290pt))
  footer-slug
  tag("C  museum")
})

// D — band: photo field top, white band below the seam, card straddles it
#page({
  place(top + left, rect(width: 100%, height: 62%, fill: color-field))
  place(bottom + left, dx: M, dy: -M * 0.9, block(width: 52% - M, title-block()))
  place(top + right, dx: -M * 0.7, dy: 62% - 190pt, rotate(1.8deg, image(card, width: 260pt)))
  footer-slug
  tag("D  band")
})

// E — gallery: card owns the left half, text column right
#page({
  place(top + left, rect(width: 48%, height: 100%, fill: color-field))
  place(horizon + left, dx: M * 0.5, image(card, width: 44%))
  place(top + left, dx: 52%, dy: M, block(width: 48% - M - 12pt, title-block()))
  footer-slug
  tag("E  gallery")
})
