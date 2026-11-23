"""Generate the faint notebook sketches that sit behind the site, in the manner of
Leonardo's pages: watch mechanisms, a small neural network, and handwritten RL maths.

usage: python3 tools/make_sketches.py [seed]
writes src/assets/sketches.svg (same 2400×1650 frame as paper.jpg and grid.svg)
needs: matplotlib (for turning the handwriting font into outlines), numpy

Drawing style: contours re-traced 2–3 times with slight misses, left-handed
hatching (top-left to bottom-right, as Leonardo drew), faint construction circles.
Clusters sit mostly in the side margins and the centre is kept nearly clear, so the
text column stays readable; the script prints the share of the frame the clusters cover.
Handwriting: La Belle Aurore (OFL, tools/fonts/). Greek letters and maths symbols,
which the font lacks, are drawn as pen strokes below.
"""
import sys, pathlib, math
import numpy as np
from matplotlib.textpath import TextPath, text_to_path
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path

W, H = 2400, 1650
INK = "#4a2210"
LAYER_OPACITY = .46          # how present the whole sketch layer is
ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = FontProperties(fname=str(ROOT / "tools" / "fonts" / "LaBelleAurore.ttf"))
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 5)

out = []            # SVG elements
defs = []           # clip paths
boxes = []          # cluster bounding boxes, for the coverage report


# ---------------------------------------------------------------- pen primitives
def catmull(pts, k=10):
    """Smooth a list of control points into a dense curve."""
    p = np.asarray(pts, float)
    if len(p) < 3:
        return p
    p = np.vstack([p[0], p, p[-1]]); res = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0, 1, k, endpoint=False):
            t2, t3 = t * t, t * t * t
            res.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    res.append(p[-2])
    return np.array(res)


def waver(p, amp=1.0, freq=3):
    """Low-frequency hand tremor along a polyline."""
    n = len(p)
    if n < 2:
        return p
    t = np.linspace(0, 1, n)
    d = np.gradient(p, axis=0); nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    phase = rng.uniform(0, 6.3, 2)
    off = amp * (np.sin(2 * np.pi * freq * t + phase[0]) * .6 + np.sin(2 * np.pi * freq * 2.3 * t + phase[1]) * .4)
    return p + nrm * off[:, None] + rng.normal(0, amp * .15, p.shape)


def stroke(p, w=1.8, o=.85, extra=""):
    p = np.asarray(p, float)
    if len(p) < 2:
        return
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in p)
    out.append(f'<path d="{d}" stroke-width="{w:.2f}" stroke-opacity="{o:.2f}"{extra}/>')


def sketchy(p, w=1.8, o=.85, repeats=3, amp=1.6, extra=""):
    """Leonardo's searching line: one full pass, then shorter passes that wander off the
    contour and back, so edges look found rather than ruled."""
    p = np.asarray(p, float); n = len(p)
    for r in range(repeats):
        if r == 0:
            a, b = int(rng.uniform(0, .05) * n), n - int(rng.uniform(0, .05) * n)
        else:
            L = int(n * rng.uniform(.25, .7)); a = int(rng.uniform(0, max(1, n - L))); b = a + L
        q = p[a:max(a + 2, b)]
        q = waver(q + rng.normal(0, amp * (.6 if r == 0 else 1.4), 2), amp * (1 if r == 0 else 1.6))
        stroke(q, w * (1 if r == 0 else rng.uniform(.5, .8)), o * (1 if r == 0 else rng.uniform(.35, .6)), extra)


def arc(cx, cy, r, a0=0, a1=2 * math.pi, n=None):
    n = n or max(16, int(abs(a1 - a0) * r / 6))
    t = np.linspace(a0, a1, n)
    return np.stack([cx + r * np.cos(t), cy + r * np.sin(t)], 1)


def circle(cx, cy, r, w=1.6, o=.8, repeats=2):
    a0 = rng.uniform(0, 6.3)
    sketchy(arc(cx, cy, r, a0, a0 + 2 * math.pi + rng.uniform(.05, .35)), w, o, repeats, amp=max(.6, r * .012))


def line(x0, y0, x1, y1, w=1.4, o=.7, repeats=1, amp=.8):
    n = max(4, int(math.hypot(x1 - x0, y1 - y0) / 8))
    sketchy(np.stack([np.linspace(x0, x1, n), np.linspace(y0, y1, n)], 1), w, o, repeats, amp)


def construction(cx, cy, r):
    """Faint construction circle and centre lines, as a draughtsman would leave them."""
    stroke(arc(cx, cy, r), .8, .35, ' stroke-dasharray="6 5"')
    e = r * 1.25
    stroke([(cx - e, cy), (cx + e, cy)], .7, .3)
    stroke([(cx, cy - e), (cx, cy + e)], .7, .3)


def hatch_circle(cx, cy, r, side=1, spacing=6, o=.55, inner=0, cross=False):
    """Left-handed hatching (top-left to bottom-right) across one side of a disc."""
    cid = f"c{len(defs)}"
    defs.append(f'<clipPath id="{cid}"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"/></clipPath>')
    g = []
    for k in np.arange(-r, r, spacing):
        if side * k < r * .05 or abs(k) < inner:
            continue
        # direction (1, 1)/√2, offset k along normal (1, -1)/√2
        ox, oy = cx + k / math.sqrt(2), cy - k / math.sqrt(2)
        L = math.sqrt(max(r * r - k * k, 0)) * rng.uniform(.75, 1.05)
        s0 = rng.uniform(-.1, .1) * r
        x0, y0 = ox - (L - s0) / math.sqrt(2), oy - (L - s0) / math.sqrt(2)
        x1, y1 = ox + (L + s0) / math.sqrt(2), oy + (L + s0) / math.sqrt(2)
        p = waver(np.stack([np.linspace(x0, x1, 8), np.linspace(y0, y1, 8)], 1), .6, 1)
        g.append(f'<path d="M{p[0,0]:.1f},{p[0,1]:.1f} ' + " ".join(f"L{x:.1f},{y:.1f}" for x, y in p[1:]) +
                 f'" stroke-width="{rng.uniform(.8, 1.3):.2f}" stroke-opacity="{o * rng.uniform(.6, 1):.2f}"/>')
    if cross:   # a second, sparser pass the other way in the darkest part
        for k in np.arange(r * .35, r, spacing * 1.6):
            ox, oy = cx + k / math.sqrt(2), cy + k / math.sqrt(2)
            L = math.sqrt(max(r * r - k * k, 0)) * rng.uniform(.5, .9)
            p = waver(np.stack([np.linspace(ox - L / math.sqrt(2), ox + L / math.sqrt(2), 6), np.linspace(oy + L / math.sqrt(2), oy - L / math.sqrt(2), 6)], 1), .6, 1)
            g.append(f'<path d="M{p[0,0]:.1f},{p[0,1]:.1f} ' + " ".join(f"L{x:.1f},{y:.1f}" for x, y in p[1:]) +
                     f'" stroke-width="{rng.uniform(.7, 1.1):.2f}" stroke-opacity="{o * .7:.2f}"/>')
    out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")


# ---------------------------------------------------------------- mechanisms
def gear(cx, cy, r, teeth, spokes=5, shade=True, rot=0):
    depth = r * .09
    pts = []
    for i in range(teeth):
        a = rot + 2 * math.pi * i / teeth; s = 2 * math.pi / teeth
        for frac, rr in ((0, r - depth), (.18, r - depth), (.3, r + depth * .9), (.62, r + depth * .9), (.74, r - depth)):
            pts.append((cx + rr * math.cos(a + frac * s), cy + rr * math.sin(a + frac * s)))
    pts.append(pts[0])
    construction(cx, cy, r)
    sketchy(pts, 1.6, .85, 2, amp=.8)
    circle(cx, cy, r * .72, 1.5, .8)
    circle(cx, cy, r * .2, 1.6, .85)
    circle(cx, cy, r * .06, 1.2, .8, 1)
    for i in range(spokes):
        a = rot + .4 + 2 * math.pi * i / spokes; dx, dy = math.cos(a), math.sin(a); px, py = -dy, dx
        for side in (-1, 1):
            o = side * r * .045
            line(cx + dx * r * .2 + px * o, cy + dy * r * .2 + py * o, cx + dx * r * .72 + px * o * 1.6, cy + dy * r * .72 + py * o * 1.6, 1.3, .75)
    if shade:
        hatch_circle(cx, cy, r * .98, side=1, spacing=max(4.5, r * .038), o=.5, cross=r > 120)


def escapement(cx, cy, r, teeth=15):
    pts = []
    for i in range(teeth):
        a = 2 * math.pi * i / teeth; s = 2 * math.pi / teeth
        pts += [(cx + r * .82 * math.cos(a), cy + r * .82 * math.sin(a)),
                (cx + r * math.cos(a + s * .15), cy + r * math.sin(a + s * .15)),
                (cx + r * .97 * math.cos(a + s * .32), cy + r * .97 * math.sin(a + s * .32)),
                (cx + r * .82 * math.cos(a + s * .9), cy + r * .82 * math.sin(a + s * .9))]
    pts.append(pts[0])
    construction(cx, cy, r)
    sketchy(pts, 1.6, .85, 2, amp=.8)
    circle(cx, cy, r * .62, 1.4, .75)
    circle(cx, cy, r * .14, 1.5, .85)
    for i in range(4):
        a = .3 + i * math.pi / 2
        line(cx + r * .14 * math.cos(a), cy + r * .14 * math.sin(a), cx + r * .62 * math.cos(a), cy + r * .62 * math.sin(a), 1.4, .75)
    hatch_circle(cx, cy, r * .8, side=1, spacing=6, o=.4)
    # the pallet fork above it
    px, py = cx + r * .15, cy - r * 1.45
    circle(px, py, r * .1, 1.5, .85)
    arm = [(px - r * .75, py + r * .55), (px - r * .45, py + r * .2), (px, py), (px + r * .45, py + r * .22), (px + r * .72, py + r * .58)]
    sketchy(catmull(arm, 6), 1.8, .85, 2)
    sketchy([(px - r * .78, py + r * .5), (px - r * .7, py + r * .66)], 2.2, .85, 1)
    sketchy([(px + r * .68, py + r * .52), (px + r * .76, py + r * .7)], 2.2, .85, 1)
    line(px, py, px - r * .05, py - r * .65, 1.5, .8, 2)                       # the fork stem


def balance_spring(cx, cy, turns=6.5, r_end=95):
    t = np.linspace(0, turns * 2 * math.pi, int(turns * 70))
    r = 6 + (r_end - 6) * t / t[-1]
    p = np.stack([cx + r * np.cos(t), cy + r * np.sin(t) * .96], 1)
    sketchy(p, 1.4, .8, 2, amp=.7)
    circle(cx, cy, r_end * 1.25, 1.6, .7)
    stroke(arc(cx, cy, r_end * 1.12, .3, 2.2), 1, .4)


# ---------------------------------------------------------------- handwriting
def glyph_stroke(name, x, y, h):
    """Greek letters and symbols the font lacks, drawn as pen strokes. (x, y) = baseline start."""
    U = lambda pts: [(x + u * h, y - v * h) for u, v in pts]
    G = {
        "gamma": ([[(0, .52), (.12, .56), (.26, .42), (.36, .1), (.38, -.22), (.33, -.34), (.4, -.3), (.38, -.12)], [(.38, .05), (.48, .38), (.6, .53)]], .66),
        "sigma": ([[(.62, .5), (.32, .5), (.12, .38), (.08, .18), (.2, .02), (.38, .02), (.48, .18), (.44, .38), (.32, .5)]], .7),
        "omega": ([[(.06, .46), (.03, .2), (.14, .02), (.3, .06), (.38, .26), (.44, .08), (.58, .0), (.72, .14), (.7, .44)]], .8),
        "Sigma": ([[(.68, .74), (.05, .74), (.38, .36), (.05, -.04), (.7, -.04)]], .78),
        "partial": ([[(.18, .62), (.36, .74), (.54, .6), (.56, .3), (.44, .06), (.26, .0), (.12, .12), (.16, .3), (.34, .38), (.55, .3)]], .66),
        "inf": (None, .9),
        "leq": ([[(.6, .62), (.08, .4), (.6, .2)], [(.1, .1), (.62, -.04)]], .74),
        "norm": ([[(.08, -.12), (.1, .78)], [(.24, -.12), (.26, .78)]], .38),
        "arrow": ([[(.02, .3), (.9, .3)], [(.72, .44), (.92, .3), (.72, .16)]], 1.0),
        "Rarrow": ([[(.02, .38), (.75, .38)], [(.02, .22), (.75, .22)], [(.6, .52), (.92, .3), (.6, .08)]], 1.0),
    }
    strokes, adv = G[name]
    if name == "inf":
        t = np.linspace(0, 2 * math.pi, 60); s = 1 + np.sin(t) ** 2
        strokes = [list(zip(.42 + .38 * np.cos(t) / s, .26 + .32 * np.sin(t) * np.cos(t) / s))]
    for st in strokes:
        sketchy(catmull(U(st), 6) if len(st) > 2 else U(st), max(1.2, h * .045), .9, 1, amp=h * .012)
    return adv * h


def font_text(s, x, y, h, rot=0):
    """Draw text in the handwriting font as filled outlines. Returns the advance width."""
    width, _, _ = text_to_path.get_text_width_height_descent(s, FONT, ismath=False)
    width *= h / FONT.get_size_in_points()
    if not s.strip():
        return width or h * .3 * len(s)
    tp = TextPath((0, 0), s, size=h, prop=FONT)
    verts, codes = tp.vertices, tp.codes
    ca, sa = math.cos(rot), math.sin(rot)
    def T(v):
        px, py = v[0], -v[1]
        return x + px * ca - py * sa, y + px * sa + py * ca
    d, i = [], 0
    while i < len(codes):
        c = codes[i]
        if c == Path.MOVETO:
            d.append("M%.1f,%.1f" % T(verts[i])); i += 1
        elif c == Path.LINETO:
            d.append("L%.1f,%.1f" % T(verts[i])); i += 1
        elif c == Path.CURVE3:
            d.append("Q%.1f,%.1f %.1f,%.1f" % (*T(verts[i]), *T(verts[i + 1]))); i += 2
        elif c == Path.CURVE4:
            d.append("C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (*T(verts[i]), *T(verts[i + 1]), *T(verts[i + 2]))); i += 3
        else:
            d.append("Z"); i += 1
    if d:
        out.append(f'<path d="{"".join(d)}" fill="{INK}" fill-opacity="{rng.uniform(.75, .95):.2f}" stroke="none"/>')
    return width


def write(tokens, x, y, h, rot=0.0):
    """Typeset a line of handwritten maths. tokens: strings (font text), '@name' (drawn glyph),
    or ('_', [...]) / ('^', [...]) for sub- and superscripts. A slight drift keeps it hand-made."""
    x0 = x
    for tok in tokens:
        if isinstance(tok, tuple):
            kind, inner = tok
            dy = h * .28 if kind == "_" else -h * .42
            x += write(inner, x, y + dy, h * .6, rot)
            continue
        jy = y + rng.normal(0, h * .03) + (x - x0) * math.sin(rot)
        if tok.startswith("@"):
            x += glyph_stroke(tok[1:], x, jy, h) + h * .08
        else:
            x += font_text(tok, x, jy, h, rot) + h * .02
    return x - x0


def arrow_curve(pts, w=1.3, o=.75):
    c = catmull(pts, 8); sketchy(c, w, o, 2, .8)
    (x0, y0), (x1, y1) = c[-3], c[-1]; a = math.atan2(y1 - y0, x1 - x0)
    for s in (-1, 1):
        line(x1, y1, x1 - 14 * math.cos(a + s * .45), y1 - 14 * math.sin(a + s * .45), w, o)


def strays(x0, y0, x1, y1, n=6):
    """Loose construction lines and false starts around a cluster."""
    for _ in range(n):
        if rng.random() < .5:
            y = rng.uniform(y0, y1); xa = rng.uniform(x0 - 40, x0 + (x1 - x0) * .4); xb = xa + rng.uniform(120, (x1 - x0) * .9)
            line(xa, y, xb, y + rng.normal(0, 12), .8, rng.uniform(.2, .4), 1, 1.2)
        else:
            x = rng.uniform(x0, x1); ya = rng.uniform(y0 - 30, y0 + (y1 - y0) * .4)
            line(x, ya, x + rng.normal(0, 14), ya + rng.uniform(100, (y1 - y0) * .8), .8, rng.uniform(.2, .4), 1, 1.2)


def notes(lines, x, y, h, lead=1.45, rot=0.0):
    """A block of small cramped notes, each line a little skewed and indented."""
    for i, ln in enumerate(lines):
        write(ln if isinstance(ln, list) else [ln], x + rng.normal(0, h * .4), y + i * h * lead, h * rng.uniform(.92, 1.05), rot + rng.normal(0, .012))


def box(x0, y0, x1, y1):
    boxes.append((x0, y0, x1, y1))


# ---------------------------------------------------------------- neural net diagram
def neural_net(x, y, layers=(3, 4, 4, 2), dx=105, dy=62):
    pos = []
    for li, n in enumerate(layers):
        col = [(x + li * dx + rng.normal(0, 2), y + (j - (n - 1) / 2) * dy + rng.normal(0, 2)) for j in range(n)]
        pos.append(col)
    for a, b in zip(pos[:-1], pos[1:]):
        for p in a:
            for q in b:
                line(p[0] + 15, p[1], q[0] - 15, q[1], 1.0, .45, 1, .5)
    for col in pos:
        for (px, py) in col:
            circle(px, py, 15, 1.5, .85)
    for (px, py) in pos[0]:
        line(px - 70, py, px - 18, py, 1.2, .7)
        glyph_stroke("arrow", px - 40, py + 6, 18)
    for (px, py) in pos[-1]:
        line(px + 18, py, px + 70, py, 1.2, .7)
    return pos


# ================================================================= the page
# --- top-left: a gear train, the heart of a watch
gear(330, 330, 175, 30, 6)
gear(330 + 175 + 82, 330 + 85, 92, 16, 4, rot=.1)
gear(330 + 30, 330 + 175 + 120, 70, 12, 4, shade=False)
write(["ratio  30 : 16"], 600, 600, 30, -.05)
notes(["the pinion of 16 turns", "nearly twice for each", "turn of the great wheel"], 520, 650, 21, rot=.02)
strays(100, 70, 720, 700, 7)
write(["the train"], 130, 95, 34, .03)
line(130, 105, 270, 160, 1, .5)
box(100, 70, 720, 700)

# --- left, middle: the balance spring
balance_spring(300, 960)
write(["balance,"], 120, 1110, 30, .02)
write(["isochronous"], 120, 1150, 28, .02)
notes(["the spring breathes;", "each swing the same time"], 330, 1110, 19, rot=-.02)
strays(100, 830, 460, 1170, 4)
box(100, 830, 600, 1190)

# --- bottom-left: the Bellman optimality operator, and a small MDP
write(["(T", ("^", ["*"]), "Q)(s,a) = r(s,a) + ", "@gamma", " ", "@Sigma", ("_", ["s'"]), " P(s' | s,a) max", ("_", ["a'"]), " Q(s',a')"], 60, 1290, 34, -.02)
write(["Q", ("^", ["*"]), " = T", ("^", ["*"]), "Q", ("^", ["*"]), "   fixed point"], 110, 1360, 34, .01)
write(["@norm", "TQ - TQ'", "@norm", ("_", ["@inf"]), " ", "@leq", " ", "@gamma", " ", "@norm", "Q - Q'", "@norm", ("_", ["@inf"])], 90, 1430, 32, -.015)
for (sx, sy, lab) in ((240, 1530, "s"), (380, 1580, "s'"), (520, 1520, "s''")):
    circle(sx, sy, 26, 1.5, .8)
    write([lab], sx - 9, sy + 9, 26)
arrow_curve([(262, 1512), (310, 1482), (358, 1560)])
arrow_curve([(406, 1572), (455, 1596), (496, 1540)])
arrow_curve([(540, 1500), (600, 1440), (560, 1490), (534, 1496)])
notes(["contraction in the sup norm,", "so Q* exists and is unique;", "iterate T and it is found"], 600, 1530, 20, rot=-.03)
strays(50, 1250, 690, 1620, 5)
write(["a, r"], 290, 1490, 22)
box(50, 1250, 690, 1620)

# --- top-right: a small network and its equations
neural_net(1900, 290)
write(["h = ", "@sigma", "(W", ("_", ["1"]), "x + b", ("_", ["1"]), ")"], 1850, 115, 34, .02)
write(["y = softmax(W", ("_", ["2"]), "h)"], 1880, 520, 32, -.02)
write(["@partial", "L / ", "@partial", "W  = ", "@partial", "L/", "@partial", "h ", " . ", "@partial", "h/", "@partial", "W"], 1820, 580, 28, .01)
notes(["weights learn by the gradient,", "layer upon layer, as a train", "of wheels passes motion on"], 2020, 640, 20, rot=.02)
strays(1800, 80, 2370, 600, 6)
box(1800, 80, 2370, 700)

# --- right, middle: escapement wheel and pallet fork
escapement(2110, 1000, 150)
write(["escapement"], 1850, 1010, 32, -.08)
line(2010, 990, 1965, 1000, 1, .5)
write(["tick . tock"], 2200, 1190, 26, .04)
notes(["the wheel gives an impulse,", "the pallet takes it back"], 1840, 1080, 20, rot=-.04)
strays(1820, 720, 2300, 1200, 6)
box(1820, 720, 2300, 1200)

# --- bottom-right: the SOR fixed point
write(["Q", ("_", ["@omega"]), " = ", "@omega", "Q", ("^", ["*"]), " + (1 - ", "@omega", ") V", ("^", ["*"])], 1830, 1330, 36, -.02)
write(["@omega", " ", "@leq", " 1 / (1 - ", "@gamma", "p", ("_", ["min"]), ")"], 1880, 1400, 32, .015)
write(["gaps  ", "@Rarrow", "  ", "@omega", " . gap"], 1900, 1465, 28, -.01)
gear(2250, 1560, 60, 10, 3, shade=False)
notes(["over-relaxed, the target shifts:", "same policy, wider gaps"], 1840, 1530, 20, rot=.02)
strays(1810, 1280, 2370, 1630, 5)
box(1810, 1280, 2370, 1630)

# --- centre: only a whisper, so the text column stays clear
write(["@gamma", " < 1"], 1150, 1590, 26, .03)
box(1130, 1560, 1260, 1600)

# ---------------------------------------------------------------- write the SVG
covered = sum((x1 - x0) * (y1 - y0) for x0, y0, x1, y1 in boxes) / (W * H)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">\n'
       f'<defs>{"".join(defs)}</defs>\n'
       f'<g opacity="{LAYER_OPACITY}" fill="none" stroke="{INK}" stroke-linecap="round" stroke-linejoin="round">\n'
       + "\n".join(out) + "\n</g>\n</svg>\n")
dest = ROOT / "src" / "assets" / "sketches.svg"
dest.write_text(svg)
print(f"wrote {dest} ({len(svg)//1024} KB); clusters cover {covered:.0%} of the frame")
