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
BASE = (232, 217, 178)                # the paper: aged ochre, as in Leonardo's sheets (matches --paper)
AGE = (96, 74, 36)                    # the olive-brown that paper turns
RUST = (162, 92, 44)                  # foxing: iron in the paper oxidising to rust-red
STAIN = .80                           # overall strength of ageing, stains and foxing

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
        inside = (f > np.quantile(f, rng.uniform(.915, .955))).astype(np.float32)
        inside *= .55 + .45 * fbm(W, H, 4, 12)                    # the water didn't soak evenly
        rim = np.clip(blur(inside, 3) - blur(inside, 16), 0, None)
        rim = blur(rim, 2.5); rim /= rim.max() + 1e-6
        out += .42 * rim * (.5 + .5 * fbm(W, H, 3, 20)) + .16 * blur(inside, 28)
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


def rust_foxing():
    """Rust-red foxing: small sharp spots with darker cores, crowding toward the edges,
    plus a few larger blooms. Returned as coverage in [0, 1]."""
    out = np.zeros((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    edge_w = np.clip(np.maximum(np.abs(xx / W - .5) * 2, np.abs(yy / H - .5) * 2) - .35, 0, 1) / .65
    cdf = (edge_w ** 1.6 + .04).ravel(); cdf = np.cumsum(cdf / cdf.sum())
    for _ in range(650):
        i = int(np.searchsorted(cdf, rng.random())); y, x = divmod(i, W)
        big = rng.random() < .09
        r = rng.gamma(1.5, 4 if big else 1.4) + (6 if big else .8); s = int(r * 3) + 2
        ys, xs = slice(max(0, y - s), min(H, y + s)), slice(max(0, x - s), min(W, x + s))
        d = np.hypot(xx[ys, xs] - x, (yy[ys, xs] - y) * rng.uniform(.8, 1.3)) / r
        spot = np.exp(-d ** 2) * (.5 + .5 * np.exp(-(d * 2.2) ** 2))           # halo + core
        out[ys, xs] = np.maximum(out[ys, xs], spot * rng.uniform(.45, 1))
    breakup = np.clip((fbm(W, H, 4, 140, persist=.7) - .3) * 2.2, 0, 1)   # spots are ragged, not round
    out = out * (.25 + .75 * breakup)
    halo = blur(out, 6) * .5                                          # a faint brown cloud around each cluster
    return np.clip(blur(out, .5) + halo, 0, 1)


def creases():
    """Two old folds: a dark line in the valley and a pale highlight beside it."""
    dark = np.zeros((H, W), np.float32); light = np.zeros((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    for pos, vertical in ((H * .5, False), (W * .5, True), (H * .25, False)):   # folded in half, then again
        along = (yy if vertical else xx).astype(np.float32)
        wob = 9 * np.sin(along / 310 + rng.uniform(0, 6)) + 3 * np.sin(along / 67) + 14 * (along / along.max() - .5)
        d = ((xx if vertical else yy) - pos - wob)
        strength = .55 + .45 * fbm(W, H, 3, 6)
        # a real fold: a sharp valley line, a shadowed slope on one side, a lit slope on the other
        dark += np.exp(-(d / 2.5) ** 2) * .38 * strength                       # the crease itself
        dark += np.clip(-d, 0, None) / 70 * np.exp(-(d / 70) ** 2) * .6 * strength    # shadow side
        dark += np.exp(-(d / 140) ** 2) * .05                                   # the paper sags along it
        light += np.clip(d, 0, None) / 45 * np.exp(-(d / 45) ** 2) * .55 * strength  # lit side
        light += np.exp(-((d - 4) / 2.5) ** 2) * .35 * strength                 # the ridge catching light
    return dark, light


def scratches(n=70):
    """Fine abrasions: short pale scuffs where the surface has worn."""
    img = Image.new("L", (W, H), 0); from PIL import ImageDraw as D; d = D.Draw(img)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H); a = rng.uniform(0, np.pi); L = rng.uniform(20, 120)
        pts = [(x + t * L * np.cos(a) + rng.normal(0, 1.2), y + t * L * np.sin(a) + rng.normal(0, 1.2)) for t in np.linspace(0, 1, 6)]
        d.line(pts, fill=int(rng.uniform(60, 160)), width=1)
    return np.asarray(img, np.float32) / 255


def worn_edges():
    """Edges darkened by handling: strongest at the corners, ragged rather than smooth."""
    yy, xx = np.mgrid[0:H, 0:W]
    ex, ey = np.abs(xx / W - .5) * 2, np.abs(yy / H - .5) * 2
    v = np.clip(np.maximum(ex, ey) - .72 + .22 * (fbm(W, H, 5, 9) - .5), 0, None) / .28
    corner = np.clip(ex * ey - .55, 0, None) * 2.2
    return np.clip((v ** 1.3 + corner) * (.6 + .6 * fbm(W, H, 4, 14)), 0, 1.2)


def centre_relief():
    """Stains are allowed everywhere, but weaker behind the text column so reading stays easy."""
    x = np.linspace(-1, 1, W)[None, :]
    return (.45 + .55 * np.clip(np.abs(x) * 1.6, 0, 1) ** 1.5).astype(np.float32)


def make_sheet():
    grime = np.clip((.6 * fbm(W, H, 7, 2.0, persist=.68) + .4 * fbm(W, H, 6, 7, persist=.6) - .3) * 1.5, 0, 1)
    dark_c, light_c = creases()
    darkness = (
        .55 * grime                                # mottled, uneven ageing
        + .10 * fbm(W, H, 4, 25)                   # finer blotching
        + 1.0 * tide_stains(3) * centre_relief()
        + .35 * foxing(90, 8)                      # brown specks
        + .10 * np.clip((fbm(W, H, 5, 5, aniso=(20, 1)) - .5) * 2.2, 0, 1)   # drag streaks
        + .55 * worn_edges()
        + .36 * edges()                            # the broad vignette: the sheet darkens toward its edges
        + .16 * grain()
        + dark_c
    )
    darkness = np.clip(darkness - np.quantile(darkness, .03), 0, 1.3)[..., None]
    base, age, rust = (np.array(c, np.float32) / 255 for c in (BASE, AGE, RUST))
    paper = base * (1 - darkness * (1 - age) * STAIN)
    olive = np.array((150, 140, 92), np.float32) / 255           # greenish cast in places, as old rag paper gets
    tint = (np.clip(fbm(W, H, 5, 3) - .45, 0, None) * 1.4)[..., None]
    paper = paper * (1 - tint * .35) + paper * olive / olive.max() * tint * .35
    fox = rust_foxing()[..., None]
    paper = paper * (1 - fox * (1 - rust) * .72)                   # rust spots multiply into the sheet
    paper = paper + (1 - paper) * (.30 * light_c + .25 * scratches())[..., None]   # pale crease ridges and scuffs
    Image.fromarray(np.clip(paper * 255, 0, 255).astype(np.uint8)).save(
        OUT / "paper.jpg", quality=84, optimize=True, progressive=True)
    c = paper[H // 2 - 300:H // 2 + 300, W // 2 - 500:W // 2 + 500].mean(axis=(0, 1)) * 255
    print("wrote", OUT / "paper.jpg", "centre colour", c.astype(int))


# ---------------------------------------------------------------- tears
def make_tears():
    """Torn-away paper as a transparent overlay (it sits above the grid and sketches):
    a missing corner, rips and nicks along the borders, and a small slit. Where paper is
    missing you see a dark backing; along each tear, a band of pale torn fibres."""
    from PIL import ImageDraw
    missing = Image.new("L", (W, H), 0); dm = ImageDraw.Draw(missing)

    def ragged(p0, p1, n=60, amp=14):
        t = np.linspace(0, 1, n)
        x = p0[0] + (p1[0] - p0[0]) * t; y = p0[1] + (p1[1] - p0[1]) * t
        nx, ny = -(p1[1] - p0[1]), p1[0] - p0[0]; L = np.hypot(nx, ny) + 1e-9
        off = (fbm(n, 1, 5, 5, persist=.6)[0] - .5) * 2 * amp + rng.normal(0, amp * .08, n)   # torn paper wanders; it isn't a saw blade
        return list(zip(x + nx / L * off, y + ny / L * off))

    # a corner torn away (top right)
    edge = ragged((W - 330, -10), (W + 10, 250), 90, 18)
    dm.polygon(edge + [(W + 10, -10)], fill=255)
    # a bite out of the bottom-left corner
    edge = ragged((-10, H - 170), (210, H + 10), 70, 14)
    dm.polygon(edge + [(-10, H + 10)], fill=255)
    # nicks along the borders: small triangular rips
    for _ in range(6):
        side = rng.integers(4); depth = rng.uniform(14, 40); width = rng.uniform(30, 80)
        if side in (0, 1):
            x = rng.uniform(150, W - 450); y0 = -5 if side == 0 else H + 5; sgn = 1 if side == 0 else -1
            pts = ragged((x, y0), (x + width * .4, y0 + sgn * depth), 14, 4) + ragged((x + width * .4, y0 + sgn * depth), (x + width, y0), 14, 4)
        else:
            y = rng.uniform(300, H - 300); x0 = -5 if side == 2 else W + 5; sgn = 1 if side == 2 else -1
            pts = ragged((x0, y), (x0 + sgn * depth, y + width * .4), 14, 4) + ragged((x0 + sgn * depth, y + width * .4), (x0, y + width), 14, 4)
        dm.polygon(pts, fill=255)
    # a slit tear running in from the left edge, a few millimetres open
    a = ragged((-5, H * .64), (230, H * .64 + 55), 50, 5); b = ragged((230, H * .64 + 55), (-5, H * .64 + 16), 50, 5)
    dm.polygon(a + b, fill=255)

    m = np.asarray(missing, np.float32) / 255
    soft = blur(m, 1.2)
    fibres = np.clip(blur(m, 3.5) - m, 0, 1) * 2.2                            # a thin band just inside each tear
    fibres = np.clip(fibres * (.55 + .9 * fbm(W, H, 3, 160)), 0, 1)          # torn fibres are uneven and furry
    shadow = np.clip(blur(m, 9) - m, 0, 1) * 0                                # (backing sits below; no drop shadow outward)
    backing = np.array((46, 33, 22), np.float32) / 255
    back_tex = backing * (.8 + .4 * fbm(W, H, 4, 20))[..., None]
    inner_shade = np.clip(1 - blur(1 - m, 10), 0, 1)                          # backing darker near the paper's edge
    rgb = np.where(m[..., None] > .5, back_tex * (1 - .35 * inner_shade[..., None]), np.array((228, 212, 172), np.float32) / 255)   # torn fibres: paler than the aged face, not white
    alpha = np.clip(soft + fibres * .6 + shadow, 0, 1)
    rgba = np.dstack([np.clip(rgb * 255, 0, 255), alpha * 255]).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(OUT / "tears.png", optimize=True)
    print("wrote", OUT / "tears.png")


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
make_tears()
