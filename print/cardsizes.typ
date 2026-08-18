// Card-size comparison. Each page renders the same verso at a different
// default card cap. Tag in the corner names the setting.
#import "tokens.typ": *
#let B = space-bleed
#let M = space-page-margin
#let G = space-gutter
#let PW = 210mm
#let PH = 297mm
#set page(width: PW, height: PH, margin: 0pt, fill: color-paper)
#set text(font: font-serif, size: size-body, fill: color-body)

#let lab(c, fill: color-label) = text(font: font-sans, size: size-label, fill: fill,
  tracking: label-tracking, weight: "medium", upper(c))
#let card(e, base) = rotate(e.tilt * 1deg,
  image("cards/" + e.path.split("/").last(), width: base * e.scale))

#let verso(r, cap, ref) = {
  place(top + left, image("../" + r.photo, width: 100%, height: 62%, fit: "cover"))
  place(bottom + left, dx: M, dy: -(M * 0.9), block(width: 50% - M, {
    lab(r.section, fill: color-accent); v(space-label-gap)
    text(size: size-title, fill: color-ink, r.title); v(space-label-gap)
    text(size: size-description, style: "italic", fill: color-muted,
      eval(r.description, mode: "markup"))
  }))
  for e in r.scans {
    let k = e.slot
    let w = calc.min(cap, ref * e.aspect)
    place(top + right, dx: -(G) - k * 48pt, dy: 62% - 215pt + k * 30pt, card(e, w))
  }
  place(top + right, dx: -8pt, dy: 8pt,
    box(fill: color-accent, inset: 5pt, text(font: font-sans, size: 8pt, fill: white,
      "cap " + str(int(cap / 1pt)) + "pt")))
}

#let data = json("cardproof.json")
#for r in data {
  for (cap, ref) in ((250pt, 295pt), (290pt, 340pt), (330pt, 385pt), (370pt, 430pt)) {
    page(verso(r, cap, ref))
  }
}
