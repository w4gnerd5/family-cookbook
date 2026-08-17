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


def bake(src: Path, dst: Path):
    im = Image.open(src).convert("RGBA")
    im.thumbnail((MAX_DIM, MAX_DIM), Image.LANCZOS)
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
    for r in recipes:
        for scan in r["scans"]:
            src = ROOT / scan
            dst = OUT / Path(scan).name
            if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
                continue
            bake(src, dst)
            n += 1
    print(f"baked {n} cards into {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
