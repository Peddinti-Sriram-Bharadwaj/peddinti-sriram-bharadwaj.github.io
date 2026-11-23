"""Generate the aged-paper background: old drawing paper with a hand-ruled sepia grid.
No drawings and no text: just the sheet.

usage: python3 tools/make_paper.py [seed]
writes src/assets/paper.jpg
needs: pip install numpy pillow

Layers, broad to fine: cloudy uneven ageing, soft tide-line stains, foxing specks,
faint drag streaks, browned edges, paper grain, and a grid ruled by hand in sepia
ink (wavering, pressure-varying, with the odd skip where the nib lifted).
Tune the weights in `darkness` and the GRID_* settings below.
"""
import sys, pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 2400, 1650                     # large enough to stay crisp on retina screens
BASE = (236, 226, 206)                # the paper: warm grey-beige, as in Leonardo's sheets (matches --paper)
AGE = (112, 82, 54)                   # the brown that paper turns
INK = (118, 58, 28)                   # sepia ink for the grid (red-brown, like Leonardo's pen work)
GRID_STEP = 78                        # px between grid lines (at 2400 px wide; ≈40 px on a laptop screen)
GRID_ALPHA = (.07, .19)               # min / max ink opacity along a stroke (kept light so text stays readable)

OUT = pathlib.Path(__file__).resolve().parent.parent / "src" / "assets"
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 23)


def upscale(a, w, h):
    return np.asarray(Image.fromarray(a.astype(np.float32)).resize((w, h), Image.BICUBIC), np.float32)


def fbm(w, h, octaves, base, aniso=(1, 1), persist=.55):
    """Fractal value noise in [0, 1]. aniso=(x, y) stretches features along x."""
    out = np.zeros((h, w), np.float32); amp, tot = 1.0, 0.0
    for o in range(octaves):
        sx = max(2, int(base * 2**o / aniso[0])); sy = max(2, int(base * 2**o / aniso[1]))
        out += amp * upscale(rng.random((sy, sx)), w, h); tot += amp; amp *= persist
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-9)


def blur(a, r):
    lo, hi = float(a.min()), float(a.max()); s = (hi - lo) or 1.0
    img = Image.fromarray(((a - lo) / s * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))
    return np.asarray(img, np.float32) / 255 * s + lo


def tide_stains(n):
    out = np.zeros((H, W), np.float32)
    for _ in range(n):
        f = fbm(W, H, 5, 1.6, persist=.58)
        inside = (f > np.quantile(f, rng.uniform(.90, .94))).astype(np.float32)
        rim = np.clip(blur(inside, 4) - blur(inside, 20), 0, None)
        rim = blur(rim, 3); rim /= rim.max() + 1e-6
        out += .3 * rim + .12 * blur(inside, 40)
    return out


def foxing(n, clusters):
    out = np.zeros((H, W), np.float32)
    centers = [(rng.integers(0, W), rng.integers(0, H)) for _ in range(clusters)]
    for _ in range(n):
        cx, cy = centers[rng.integers(clusters)] if rng.random() < .75 else (rng.integers(0, W), rng.integers(0, H))
        x = int(np.clip(cx + rng.normal(0, 120), 0, W - 1)); y = int(np.clip(cy + rng.normal(0, 90), 0, H - 1))
        r = rng.gamma(1.3, 2.6) + 1; s = int(r * 4) + 2
        yy, xx = np.ogrid[max(0, y - s):min(H, y + s), max(0, x - s):min(W, x + s)]
        ang, e = rng.uniform(0, np.pi), rng.uniform(1, 1.8); dx, dy = xx - x, yy - y
        u = (dx * np.cos(ang) + dy * np.sin(ang)) / e; v = -dx * np.sin(ang) + dy * np.cos(ang)
        out[yy, xx] += np.exp(-(u * u + v * v) / (r * r)) * rng.uniform(.2, .7)
    return blur(out, 1.2)


def edges():
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W / 2)) ** 2 * .85 + ((yy - H / 2) / (H / 2)) ** 2
    return np.clip(v - .3, 0, None) ** 1.35 * (.65 + .7 * fbm(W, H, 3, 4))


def grain():
    speck = np.abs(rng.normal(0, 1, (H, W))).astype(np.float32)
    speck = blur(speck, .7); speck /= speck.max()
    fibres = np.clip(fbm(W, H, 4, 50, aniso=(8, 1)) - .55, 0, None) * 2
    return .55 * speck + .45 * fibres


def hand_ruled_grid():
    """Ink coverage in [0, 1] for a grid ruled by hand: each line wavers a little,
    drifts off true, thickens and thins with pen pressure, and sometimes skips."""
    S = 2                                             # supersample for clean anti-aliasing
    ink = Image.new("F", (W * S, H * S), 0.0)
    d = ImageDraw.Draw(ink)

    def stroke(points, alphas, widths):
        for (p0, p1, a, w) in zip(points[:-1], points[1:], alphas, widths):
            d.line([p0, p1], fill=float(a), width=max(1, int(round(w * S))))

    def pen_stroke(a, b, horizontal, pos):
        """One stroke of the pen from a to b along the rule: tapered ends, its own
        slight angle, a low wobble, and pressure that swells and fades."""
        L = b - a; n = max(8, int(L / 6))
        t = np.linspace(0, 1, n)
        tilt = rng.normal(0, 3.0) * (t - .5)                  # each stroke slightly off true
        bow = rng.normal(0, 1.6) * np.sin(np.pi * t)          # a gentle curve of the wrist
        wobble = (fbm(n, 1, 3, max(2, n // 25))[0] - .5) * 2.2
        offset = pos + tilt + bow + wobble
        pressure = (.6 + .4 * fbm(n, 1, 2, 3)[0]) * np.clip(np.minimum(t, 1 - t) / .08, .25, 1)   # taper
        alpha = GRID_ALPHA[0] + (GRID_ALPHA[1] - GRID_ALPHA[0]) * pressure
        width = .8 + 1.4 * pressure
        along = a + t * L
        pts = [(x * S, o * S) for x, o in zip(along, offset)] if horizontal else [(o * S, y * S) for y, o in zip(along, offset)]
        stroke(pts, alpha, width)

    def rule(length, horizontal, pos):
        """A full grid line, ruled as several overlapping strokes like a hand-drawn line."""
        x = -rng.uniform(0, 60)
        while x < length:
            seg = rng.uniform(260, 720)
            if rng.random() > .06:                            # now and then the nib skips a stretch
                pen_stroke(x, min(length + 20, x + seg), horizontal, pos + rng.normal(0, 1.4))
            x += seg - rng.uniform(8, 40)                     # strokes overlap a little at the joins

    jitter = lambda: rng.normal(0, 1.6)
    for y in np.arange(GRID_STEP / 2, H, GRID_STEP):
        rule(W, True, y + jitter())
    for x in np.arange(GRID_STEP / 2, W, GRID_STEP):
        rule(H, False, x + jitter())
    ink = np.asarray(ink.resize((W, H), Image.LANCZOS), np.float32)
    return np.clip(blur(np.clip(ink, 0, 1), .5), 0, 1)       # ink bleeds a little into the paper


darkness = (
    .30 * fbm(W, H, 7, 2.2, persist=.65)      # cloudy, uneven ageing, as in the reference sheet
    + .12 * fbm(W, H, 5, 10)
    + .55 * tide_stains(2)
    + .40 * foxing(80, 7)
    + .08 * np.clip((fbm(W, H, 5, 5, aniso=(20, 1)) - .5) * 2.2, 0, 1)   # streaks
    + .36 * edges()
    + .12 * grain()
)
darkness = np.clip(darkness - np.quantile(darkness, .03), 0, 1)[..., None]
base, age, ink = (np.array(c, np.float32) / 255 for c in (BASE, AGE, INK))
paper = base * (1 - darkness * (1 - age) * .62)

grid = hand_ruled_grid()[..., None]
paper = paper * (1 - grid) + paper * ink * grid        # ink multiplies into the paper

Image.fromarray(np.clip(paper * 255, 0, 255).astype(np.uint8)).save(OUT / "paper.jpg", quality=84, optimize=True, progressive=True)
print("wrote", OUT / "paper.jpg")
