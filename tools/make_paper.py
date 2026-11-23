"""Generate the aged-paper background textures (no drawings, no text: just paper).

usage: python3 tools/make_paper.py [seed]
writes src/assets/paper-light.jpg
needs: pip install numpy pillow

Layers, from broad to fine: uneven ageing (mottling), tide-line water stains,
clustered foxing specks, faint horizontal drag streaks, one soft fold, browned
edges, and paper fibre grain. Change the weights in `darkness` to taste.
"""
import sys, pathlib
import numpy as np
from PIL import Image, ImageFilter

W, H = 1600, 1100
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
        inside = (f > np.quantile(f, rng.uniform(.88, .93))).astype(np.float32)
        rim = np.clip(blur(inside, 3) - blur(inside, 14), 0, None)   # dark edge fading inward
        rim = blur(rim, 2); rim /= rim.max() + 1e-6
        out += .35 * rim + .12 * blur(inside, 30)
    return out


def foxing(n, clusters):
    out = np.zeros((H, W), np.float32)
    centers = [(rng.integers(0, W), rng.integers(0, H)) for _ in range(clusters)]
    for _ in range(n):
        cx, cy = centers[rng.integers(clusters)] if rng.random() < .75 else (rng.integers(0, W), rng.integers(0, H))
        x = int(np.clip(cx + rng.normal(0, 80), 0, W - 1)); y = int(np.clip(cy + rng.normal(0, 60), 0, H - 1))
        r = rng.gamma(1.3, 2.0) + .7; s = int(r * 4) + 2
        yy, xx = np.ogrid[max(0, y - s):min(H, y + s), max(0, x - s):min(W, x + s)]
        ang, e = rng.uniform(0, np.pi), rng.uniform(1, 1.8); dx, dy = xx - x, yy - y
        u = (dx * np.cos(ang) + dy * np.sin(ang)) / e; v = -dx * np.sin(ang) + dy * np.cos(ang)
        out[yy, xx] += np.exp(-(u * u + v * v) / (r * r)) * rng.uniform(.25, .9)
    return blur(out, 1.0)


def fold():
    yy = np.arange(H)[:, None]; wob = 5 * np.sin(np.linspace(0, 6, W))[None, :]
    return np.exp(-((yy - H * .47 - wob) / 7.0) ** 2) * .16 + np.exp(-((yy - H * .47 - wob) / 60.0) ** 2) * .08


def edges():
    yy, xx = np.mgrid[0:H, 0:W]
    v = ((xx - W / 2) / (W / 2)) ** 2 * .85 + ((yy - H / 2) / (H / 2)) ** 2
    return np.clip(v - .28, 0, None) ** 1.35 * (.65 + .7 * fbm(W, H, 3, 4))


def grain():
    """Fine fibres at full size (no tiling, so no seams)."""
    speck = np.abs(rng.normal(0, 1, (H, W))).astype(np.float32)
    speck = blur(speck, .6); speck /= speck.max()
    fibres = np.clip(fbm(W, H, 4, 40, aniso=(8, 1)) - .55, 0, None) * 2
    return .55 * speck + .45 * fibres


darkness = (
    .22 * fbm(W, H, 6, 2.5, persist=.62)    # uneven ageing
    + .10 * fbm(W, H, 4, 9)
    + .90 * tide_stains(2)
    + .50 * foxing(90, 7)
    + .14 * np.clip((fbm(W, H, 5, 5, aniso=(20, 1)) - .5) * 2.2, 0, 1)   # streaks
    + fold()
    + .42 * edges()
    + .10 * grain()
)
darkness = np.clip(darkness - np.quantile(darkness, .02), 0, 1)[..., None]
age = np.array([118, 70, 28], np.float32) / 255           # the brown that paper turns


def bake(base_rgb, strength, name):
    base = np.array(base_rgb, np.float32) / 255
    img = base * (1 - darkness * (1 - age) * .85 * strength)
    Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8)).save(OUT / name, quality=84, optimize=True, progressive=True)
    print("wrote", OUT / name)


bake((232, 215, 180), 1.0, "paper-light.jpg")   # matches --paper in style.css

