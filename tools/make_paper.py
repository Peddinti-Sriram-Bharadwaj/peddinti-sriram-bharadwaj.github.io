"""Generate the aged-paper background: old drawing paper plus a grid scratched on by hand.
No drawings and no text: just the sheet.

usage: python3 tools/make_paper.py [seed]
writes src/assets/paper.jpg (the sheet) and src/assets/grid.svg (the ruled grid)
needs: pip install numpy pillow

The sheet is a raster image: cloudy uneven ageing, tide-line water stains, foxing
specks, faint drag streaks, browned edges and paper grain.

The grid is a separate vector layer so its lines stay razor-sharp at any screen
size: fine nib hairlines that jitter a little, drift off true, start with the odd
hook, sometimes double where the point slipped, and skip where it lifted.
Both layers share the same 2400×1650 frame and are scaled with `cover`, so they line up.
Tune the weights in `darkness` and the GRID_* settings below.
"""
import sys, pathlib
import numpy as np
from PIL import Image, ImageFilter

W, H = 2400, 1650
BASE = (236, 225, 203)                # the paper: warm grey-beige, as in Leonardo's sheets (matches --paper)
AGE = (108, 74, 44)                   # the brown that paper turns
STAIN = .82                           # overall strength of ageing, stains and foxing

GRID_STEP = 78                        # frame units between grid lines (≈40 CSS px on a laptop)
GRID_INK = "#5e2c12"                  # dark sepia
GRID_OPACITY = (.20, .46)             # per-stroke opacity range
GRID_WIDTH = (.55, 1.05)              # stroke width in *screen* pixels (non-scaling), so always a hairline

OUT = pathlib.Path(__file__).resolve().parent.parent / "src" / "assets"
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 23)


# ---------------------------------------------------------------- noise helpers
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


# ---------------------------------------------------------------- the sheet
def tide_stains(n):
    """Water stains: a faint fill with a darker tide line at the rim, fading inward."""
    out = np.zeros((H, W), np.float32)
    for _ in range(n):
        f = fbm(W, H, 5, 1.6, persist=.58)
        inside = (f > np.quantile(f, rng.uniform(.90, .945))).astype(np.float32)
        rim = np.clip(blur(inside, 3) - blur(inside, 18), 0, None)
        rim = blur(rim, 2); rim /= rim.max() + 1e-6
        out += .55 * rim + .13 * blur(inside, 35)
    return out


def foxing(n, clusters):
    out = np.zeros((H, W), np.float32)
    centers = [(rng.integers(0, W), rng.integers(0, H)) for _ in range(clusters)]
    for _ in range(n):
        cx, cy = centers[rng.integers(clusters)] if rng.random() < .75 else (rng.integers(0, W), rng.integers(0, H))
        x = int(np.clip(cx + rng.normal(0, 120), 0, W - 1)); y = int(np.clip(cy + rng.normal(0, 90), 0, H - 1))
        r = rng.gamma(1.3, 2.8) + 1.2; s = int(r * 4) + 2
        yy, xx = np.ogrid[max(0, y - s):min(H, y + s), max(0, x - s):min(W, x + s)]
        ang, e = rng.uniform(0, np.pi), rng.uniform(1, 1.8); dx, dy = xx - x, yy - y
        u = (dx * np.cos(ang) + dy * np.sin(ang)) / e; v = -dx * np.sin(ang) + dy * np.cos(ang)
        out[yy, xx] += np.exp(-(u * u + v * v) / (r * r)) * rng.uniform(.3, .9)
    return blur(out, 1.0)


def edges():
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W / 2)) ** 2 * .85 + ((yy - H / 2) / (H / 2)) ** 2
    return np.clip(v - .28, 0, None) ** 1.3 * (.65 + .7 * fbm(W, H, 3, 4))


def grain():
    speck = np.abs(rng.normal(0, 1, (H, W))).astype(np.float32)
    speck = blur(speck, .7); speck /= speck.max()
    fibres = np.clip(fbm(W, H, 4, 50, aniso=(8, 1)) - .55, 0, None) * 2
    return .55 * speck + .45 * fibres


def make_sheet():
    darkness = (
        .34 * fbm(W, H, 7, 2.2, persist=.65)      # cloudy, uneven ageing
        + .14 * fbm(W, H, 5, 10)
        + 1.0 * tide_stains(3)
        + .60 * foxing(110, 8)
        + .10 * np.clip((fbm(W, H, 5, 5, aniso=(20, 1)) - .5) * 2.2, 0, 1)   # drag streaks
        + .40 * edges()
        + .12 * grain()
    )
    darkness = np.clip(darkness - np.quantile(darkness, .03), 0, 1)[..., None]
    base, age = (np.array(c, np.float32) / 255 for c in (BASE, AGE))
    paper = base * (1 - darkness * (1 - age) * STAIN)
    Image.fromarray(np.clip(paper * 255, 0, 255).astype(np.uint8)).save(
        OUT / "paper.jpg", quality=84, optimize=True, progressive=True)
    print("wrote", OUT / "paper.jpg")


# ---------------------------------------------------------------- the scratched grid
def scratch(a, b, horizontal, pos):
    """One stroke of the nib along a rule, from a to b. Returns SVG path data."""
    L = b - a; n = max(6, int(L / 9))
    t = np.linspace(0, 1, n)
    off = (pos
           + rng.normal(0, 2.4) * (t - .5)                        # drifts off true
           + rng.normal(0, 1.1) * np.sin(np.pi * t)               # a slight bow
           + (fbm(n, 1, 2, max(2, n // 18))[0] - .5) * 1.6       # slow waver
           + rng.normal(0, .28, n))                               # the scratchy jitter of the nib
    along = a + t * L
    pts = list(zip(along, off)) if horizontal else list(zip(off, along))
    if rng.random() < .18:                                         # a small hook where the nib landed
        hx, hy = pts[0]; k = rng.uniform(3, 7) * rng.choice([-1, 1])
        pts.insert(0, (hx - 4, hy + k) if horizontal else (hx + k, hy - 4))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def rule(length, horizontal, pos, paths):
    x = -rng.uniform(0, 50)
    while x < length:
        seg = rng.uniform(220, 640)
        if rng.random() > .07:                                     # now and then the nib skips a stretch
            p = pos + rng.normal(0, 1.2)
            paths.append((scratch(x, min(length + 15, x + seg), horizontal, p),
                           rng.uniform(*GRID_OPACITY), rng.uniform(*GRID_WIDTH)))
            if rng.random() < .08:                                 # the point slipped: a faint doubled hairline
                s0 = x + rng.uniform(0, seg * .5)
                paths.append((scratch(s0, s0 + rng.uniform(40, 140), horizontal, p + rng.choice([-1, 1]) * rng.uniform(1.5, 3)),
                               GRID_OPACITY[0] * .8, GRID_WIDTH[0]))
        x += seg - rng.uniform(6, 30)                              # strokes overlap a little at the joins


def make_grid():
    paths = []
    for y in np.arange(GRID_STEP / 2, H, GRID_STEP):
        rule(W, True, y + rng.normal(0, 1.5), paths)
    for x in np.arange(GRID_STEP / 2, W, GRID_STEP):
        rule(H, False, x + rng.normal(0, 1.5), paths)
    body = "\n".join(
        f'<path d="{d}" stroke-opacity="{o:.2f}" stroke-width="{w:.2f}"/>' for d, o, w in paths)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">\n'
           f'<g fill="none" stroke="{GRID_INK}" stroke-linecap="butt" stroke-linejoin="round" vector-effect="non-scaling-stroke">\n'
           f'{body}\n</g>\n</svg>\n')
    # vector-effect must be on each path to take effect in all browsers
    svg = svg.replace("<path ", '<path vector-effect="non-scaling-stroke" ')
    (OUT / "grid.svg").write_text(svg)
    print("wrote", OUT / "grid.svg", f"({len(paths)} strokes, {len(svg)//1024} KB)")


make_sheet()
make_grid()
