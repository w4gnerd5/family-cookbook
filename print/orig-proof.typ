// Throwaway proof sheet: Original-block treatment candidates. Not part of the book.
#import "tokens.typ": *

#let recipes = json("recipes.json")
#let r = recipes.find(r => r.slug == "zeinabs-khachapuri")

// trim the long Russian segment so tiles stay comparable at a glance
#let segs = {
  let s = ()
  for seg in r.original {
    let lines = seg.text.split("\n")
    if lines.len() > 8 {
      s.push((label: seg.label, text: lines.slice(0, 8).join("\n") + "\n…"))
    } else { s.push(seg) }
  }
  s
}

#let label-text(content, fill: color-label) = text(
  font: font-sans, size: size-label, fill: fill,
  tracking: label-tracking, weight: "medium", upper(content),
)

#let orig-body = {
  set text(size: size-small, fill: color-muted, font: (font-serif, font-serif-georgian), lang: "ru")
  for (i, seg) in segs.enumerate() {
    if i > 0 { v(5pt) }
    if seg.label != "" { block(above: 5pt, below: 1pt, label-text(seg.label)) }
    for line in seg.text.split("\n") { block(above: 2.5pt, below: 0pt, line) }
  }
}

// warm tints mixed on white so they stay printable
#let tint-field = color-field                       // #F1ECE1 as-is
#let tint-light = rgb("#F8F5EE")                    // field at ~half strength
#let tint-accent = rgb("#FAF2EE")                   // terracotta wash ~8%

#let v1 = block(stroke: (left: 1.5pt + color-accent), inset: (left: 10pt, y: 2pt), {
  label-text("Original"); v(space-label-gap); orig-body })

#let v2 = block(fill: tint-field, inset: 12pt, width: 100%, {
  label-text("Original"); v(space-label-gap); orig-body })

#let v3 = block(fill: tint-light, stroke: 0.5pt + rgb("#DDD5C4"), inset: 12pt, width: 100%, {
  label-text("Original"); v(space-label-gap); orig-body })

#let v4 = block(fill: tint-accent, inset: 12pt, width: 100%, {
  label-text("Original", fill: color-accent); v(space-label-gap); orig-body })

#let v5 = block(stroke: (top: 0.5pt + color-label, bottom: 0.5pt + color-label),
  inset: (y: 10pt), width: 100%, {
  label-text("Original"); v(space-label-gap); orig-body })

#let v6 = stack(
  block(fill: color-accent, inset: (x: 8pt, y: 4pt), label-text("Original", fill: white)),
  block(fill: tint-field, inset: 12pt, width: 100%, orig-body),
)

#set page(width: 210mm, height: auto, margin: 36pt, fill: white)
#set text(font: font-serif, size: size-body, fill: color-body)

#let tile(code, name, v) = {
  block(below: 8pt, text(font: font-sans, size: 9pt, weight: "bold", fill: color-ink,
    code + "  ") + text(font: font-sans, size: 9pt, fill: color-muted, name))
  v
}

#grid(columns: (1fr, 1fr), column-gutter: 28pt, row-gutter: 34pt,
  tile("O1", "current: accent left rule", v1),
  tile("O2", "field-cream box, flat", v2),
  tile("O3", "half-strength cream box + hairline border", v3),
  tile("O4", "terracotta wash box, accent label", v4),
  tile("O5", "hairline rules top + bottom, no fill", v5),
  tile("O6", "field box with accent tab label", v6),
)
