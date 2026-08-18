// Throwaway proof sheet: method text size candidates. Not part of the book.
#import "tokens.typ": *

#let recipes = json("recipes.json")
#let r = recipes.find(r => r.slug == "zeinabs-khachapuri")

#let label-text(content, fill: color-label) = text(
  font: font-sans, size: size-label, fill: fill,
  tracking: label-tracking, weight: "medium", upper(content),
)
#let subhead(content) = block(above: space-block, below: space-label-gap, label-text(content))
#let md(s) = eval(s, mode: "markup")

#let sample(method-size) = {
  set par(leading: 0.65em, justify: false)
  set text(font: font-serif, size: size-body, fill: color-body)
  subhead("Ingredients")
  {
    set text(size: size-small)
    for it in r.ingredients { block(above: 0.65em, below: 0pt, md(it)) }
  }
  subhead("Method")
  {
    set text(size: method-size)
    let n = 0
    for it in r.instructions {
      n += 1
      block(above: 0.8em, grid(columns: (14pt, 1fr), column-gutter: 4pt,
        text(font: font-sans, size: size-small, fill: color-accent, str(n)), md(it)))
    }
  }
  subhead("Notes")
  {
    set text(size: size-small)
    for it in r.notes.slice(0, 2) { block(above: 0.65em, below: 0pt, md(it)) }
  }
}

#set page(width: 210mm, height: auto, margin: 36pt, fill: white)

#let tile(code, name, body) = {
  block(below: 8pt, text(font: font-sans, size: 9pt, weight: "bold", fill: color-ink,
    code + "  ") + text(font: font-sans, size: 9pt, fill: color-muted, name))
  body
}

#grid(columns: (1fr, 1fr), column-gutter: 28pt,
  tile("M1", "method at body 10.5pt (current)", sample(size-body)),
  tile("M2", "method at small 9pt (matches ingredients/notes)", sample(size-small)),
)
