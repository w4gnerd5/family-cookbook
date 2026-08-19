#!/usr/bin/env python3
"""Bake scan PNGs into print-ready cards: alpha-silhouette drop shadow, downsampled.

Reads print/recipes.json, writes print/cards/<IMG_XXXX>.png (gitignored cache).
Skips cards whose source is older than the cached output.
"""
import json
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "print" / "cards"
MAX_DIM = 1800          # px, plenty for a half-page card at 300dpi
BLUR = 22               # shadow softness (px, post-resize)
OFFSET = (6, 16)        # shadow displacement
OPACITY = 80            # 0-255
WHITE_TARGET = 247      # the paper of a scan should bake to about this
WHITE_PCT = 0.97        # luminance percentile treated as "the paper"
MAX_GAIN = 1.6          # cap so a genuinely dark scan doesn't blow out


def normalize(im, exposure=1.0):
    """White-point normalization: camera scans render gray paper; stretch each
    card so its paper reads near-white. exposure multiplies the computed gain
    (frontmatter per-scan override); exposure 0 disables normalization."""
    if not exposure:
        return im
    hist = im.convert("L").histogram()
    total = sum(hist)
    acc, white = 0, 255
    for v, count in enumerate(hist):
        acc += count
        if acc >= total * WHITE_PCT:
            white = max(v, 1)
            break
    gain = min(WHITE_TARGET / white, MAX_GAIN) * exposure
    if abs(gain - 1.0) < 0.02:
        return im
    r, g, b, a = im.split()
    lut = [min(255, round(i * gain)) for i in range(256)]
    return Image.merge("RGBA", (r.point(lut), g.point(lut), b.point(lut), a))


def bake(src: Path, dst: Path, exposure=1.0):
    im = Image.open(src).convert("RGBA")
    im.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)
    im = normalize(im, exposure)
    pad = BLUR * 2 + max(OFFSET)
    canvas = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    shadow = Image.new("L", canvas.size, 0)
    shadow.paste(im.getchannel("A").point(lambda a: a * OPACITY // 255),
                 (pad + OFFSET[0], pad + OFFSET[1]))
    shadow = shadow.filter(ImageFilter.GaussianBlur(BLUR))
    canvas.putalpha(shadow)          # black canvas + blurred alpha = soft shadow
    canvas.paste(im, (pad, pad), im)
    canvas.save(dst, optimize=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    recipes = json.loads((ROOT / "print" / "recipes.json").read_text())
    n = 0
    stamp = Path(__file__).stat().st_mtime   # script changes invalidate the cache
    for r in recipes:
        for scan in r["scans"]:
            path = scan["path"] if isinstance(scan, dict) else scan
            exposure = float(scan.get("exposure", 1.0)) if isinstance(scan, dict) else 1.0
            src = ROOT / path
            dst = OUT / Path(path).name
            if dst.exists() and dst.stat().st_mtime >= max(src.stat().st_mtime, stamp):
                continue
            bake(src, dst, exposure)
            n += 1
    print(f"baked {n} cards into {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
