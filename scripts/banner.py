# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10"]
# ///
"""Generate the profile banner: troy.blog-style halftone dots, cyberpunk palette.

Usage: uv run scripts/banner.py [--seed N]
Writes assets/banner.png. Needs JetBrains Mono installed in ~/Library/Fonts.
"""

import argparse
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1500, 400          # logical size
S = 2                     # render at 2x for crisp retina display
CELL = 9                  # dot grid spacing (logical px)
DOT = 2.4                 # max dot radius (logical px)

FONT_DIR = Path.home() / "Library/Fonts"
FONT_BOLD = FONT_DIR / "JetBrainsMono-Bold.ttf"
FONT_REG = FONT_DIR / "JetBrainsMono-Regular.ttf"

BG = (10, 11, 20)
CYAN, MAGENTA = (0, 229, 255), (255, 46, 151)
BLACK = (0, 0, 0)

TITLE = "ethan troy."
TAGLINE = "> i just click buttons"


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def value_noise(rng, cell=120, octaves=4):
    """Smooth fractal value noise in [0,1]; drives the shape of the dot clouds."""
    layers = []
    for o in range(octaves):
        c = cell / (2 ** o)
        gw, gh = int(W / c) + 3, int(H / c) + 3
        grid = [[rng.random() for _ in range(gw)] for _ in range(gh)]
        layers.append((c, grid, 0.5 ** o))
    norm = sum(w for _, _, w in layers)

    def smooth(t):
        return t * t * (3 - 2 * t)

    def f(x, y):
        v = 0.0
        for c, g, w in layers:
            gx, gy = x / c, y / c
            ix, iy = int(gx), int(gy)
            tx, ty = smooth(gx - ix), smooth(gy - iy)
            a = g[iy][ix] + (g[iy][ix + 1] - g[iy][ix]) * tx
            b = g[iy + 1][ix] + (g[iy + 1][ix + 1] - g[iy + 1][ix]) * tx
            v += w * (a + (b - a) * ty)
        return v / norm

    return f


def text_mask(x, y):
    """0 inside the title block, easing to 1 outside it, so dots never sit under the text."""
    dist = max((x - 650) / 200, (abs(y - 200) - 90) / 110)
    t = min(1.0, max(0.0, dist))
    return t * t * (3 - 2 * t)


def render(seed):
    rng = random.Random(seed)
    noise = value_noise(rng)

    dots = Image.new("RGB", (W * S, H * S), BLACK)
    dd = ImageDraw.Draw(dots)
    hot = Image.new("RGB", dots.size, BLACK)  # bright accent dots, these get bloom
    hd = ImageDraw.Draw(hot)

    # halftone clouds: stochastic dither over the noise field, cyan -> magenta across the frame
    for gy in range(0, H + CELL, CELL):
        for gx in range(0, W + CELL, CELL):
            v = min(1.0, max(0.0, (noise(gx, gy) - 0.40) / 0.3) ** 1.4 * text_mask(gx, gy))
            if rng.random() > v:
                continue
            hue = mix(CYAN, MAGENTA, min(1.0, max(0.0, (gx - 700) / 800 + (gy - 200) / 900)))
            r = DOT * (0.6 + 0.4 * v) * S
            x, y = gx * S, gy * S
            box = (x - r, y - r, x + r, y + r)
            if v > 0.45 and rng.random() < 0.05:
                hd.rounded_rectangle(box, radius=r * 0.35, fill=hue)
            else:
                dd.rounded_rectangle(box, radius=r * 0.35, fill=mix(BLACK, hue, 0.18 + 0.32 * v))

    # glitch: shift a few horizontal slices of the dot layer sideways
    for _ in range(5):
        y0 = rng.randrange(0, H - 12) * S
        hgt = rng.choice([CELL, CELL * 2]) * S
        dx = rng.choice([-1, 1]) * rng.randint(2, 6) * CELL * S
        band = dots.crop((0, y0, W * S, y0 + hgt))
        dots.paste(BLACK, (0, y0, W * S, y0 + hgt))
        dots.paste(band, (dx, y0))

    out = ImageChops.add(Image.new("RGB", dots.size, BG), dots)
    out = ImageChops.add(out, hot.filter(ImageFilter.GaussianBlur(6 * S)))
    out = ImageChops.add(out, hot)

    # title with chromatic aberration: magenta ghost left, cyan ghost right, near-white core
    title_font = ImageFont.truetype(str(FONT_BOLD), 84 * S)
    tag_font = ImageFont.truetype(str(FONT_REG), 30 * S)
    x0, ty, tagy = 90 * S, 125 * S, 238 * S
    ghosts = Image.new("RGB", dots.size, BLACK)
    for dx, col in ((-3, MAGENTA), (3, CYAN)):
        layer = Image.new("RGB", dots.size, BLACK)
        ImageDraw.Draw(layer).text((x0 + dx * S, ty), TITLE, font=title_font, fill=mix(BLACK, col, 0.75))
        ghosts = ImageChops.add(ghosts, layer)
    out = ImageChops.add(out, ghosts.filter(ImageFilter.GaussianBlur(10 * S)).point(lambda p: p // 2))
    out = ImageChops.screen(out, ghosts)

    d = ImageDraw.Draw(out)
    d.text((x0, ty), TITLE, font=title_font, fill=(236, 240, 255))
    d.text((x0 + 4 * S, tagy), TAGLINE, font=tag_font, fill=(130, 150, 185))
    d.text((x0 + 4 * S + d.textlength(TAGLINE, font=tag_font), tagy), "_", font=tag_font, fill=MAGENTA)

    # scanlines: darken one thin row out of every three
    lines = Image.new("L", out.size, 255)
    ld = ImageDraw.Draw(lines)
    for y in range(0, H * S, 3 * S):
        ld.rectangle((0, y, W * S, y + S - 1), fill=215)
    return Image.composite(out, Image.new("RGB", out.size, BLACK), lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=7, help="re-roll the dot layout")
    p.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "assets" / "banner.png")
    args = p.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    render(args.seed).save(args.out, optimize=True)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
