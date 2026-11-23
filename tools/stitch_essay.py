"""Turn a PDF of overlapping iPad Notes screenshots into web tiles.

usage: python3 tools/stitch_essay.py "<essay.pdf>" <slug> [first_page_top]
Works with dark- or light-mode Notes (light pages are inverted to white-on-black;
the site CSS turns them back into ink on paper).
writes assets/essays/<slug>/{1..n}.jpg, cover.jpg and prints tile sizes.
needs: pip install pymupdf pillow numpy
"""
import io, sys, pathlib
import numpy as np
import pymupdf
from PIL import Image, ImageDraw

TOP = 190          # height of the Notes status bar + toolbar at native res
WEB_W = 1100       # published width
TILE = 2000        # target tile height


BOTTOM = 320      # floating pencil button / tool palette on the last page


def to_dark(im):
    """Light-mode Notes (black ink on white) -> white ink on black, keeping hues."""
    inv = Image.fromarray(255 - np.asarray(im))
    h, s, v = inv.convert("HSV").split()
    h = h.point(lambda x: (x + 128) % 256)
    return Image.merge("HSV", (h, s, v)).convert("RGB")


def pages(pdf):
    d = pymupdf.open(pdf)
    for p in d:
        x = p.get_images()[0][0]
        im = Image.open(io.BytesIO(d.extract_image(x)["image"])).convert("RGB")
        if np.asarray(im.convert("L")).mean() > 128:
            im = to_dark(im)
        yield im


def overlap(a, b):
    """y in page a where page b's content (below the toolbar) begins, or None."""
    A = np.asarray(a.convert("L"), np.float32)
    B = np.asarray(b.convert("L"), np.float32)
    best = None
    for H in (300, 150, 100):
        strip = B[TOP:TOP + H:2, ::4]
        if strip.max() < 40:            # blank strip carries no signal
            continue
        e, y = min((np.mean((A[y:y + H:2, ::4] - strip) ** 2), y)
                   for y in range(TOP, A.shape[0] - H))
        if best is None or e < best[0]:
            best = (e, y)
        if e < 200:
            break
    return best[1] if best and best[0] < 200 else None


def main(pdf, slug, first_top=TOP):
    """first_top: crop for page 1 when Notes shows a title/date header (e.g. 300)."""
    out_dir = pathlib.Path(__file__).resolve().parent.parent / "assets" / "essays" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    ims = list(pages(pdf))
    parts = []
    for k, im in enumerate(ims):
        end = overlap(im, ims[k + 1]) if k + 1 < len(ims) else None
        print(f"page {k + 1}: overlap with next at {end}")
        top = first_top if k == 0 else TOP
        parts.append(im.crop((0, top, im.width, end or im.height - BOTTOM)))
    W = parts[0].width
    full = Image.new("RGB", (W, sum(p.height for p in parts)))
    y = 0
    for p in parts:
        full.paste(p, (0, y)); y += p.height
    ImageDraw.Draw(full).rectangle((W - 40, 0, W, full.height), fill=(0, 0, 0))  # scrollbar
    g = np.asarray(full.convert("L"))
    rows = np.where(g.max(1) > 60)[0]
    full = full.crop((0, 0, W, rows.max() + 60))

    web = full.resize((WEB_W, round(full.height * WEB_W / W)), Image.LANCZOS)
    blank = np.asarray(web.convert("L")).max(1) < 50
    cuts = [0]
    while web.height - cuts[-1] > TILE * 1.3:
        t = cuts[-1] + TILE
        cand = [y for y in range(t - 400, min(t + 400, web.height)) if blank[y]]
        cuts.append(min(cand, key=lambda y: abs(y - t)) if cand else t)
    cuts.append(web.height)
    for i in range(len(cuts) - 1):
        h = cuts[i + 1] - cuts[i]
        web.crop((0, cuts[i], WEB_W, cuts[i + 1])).save(out_dir / f"{i + 1}.jpg", quality=82, optimize=True, progressive=True)
        print(f'<img src="../assets/essays/{slug}/{i + 1}.jpg" alt="" width="{WEB_W}" height="{h}" loading="lazy">')
    cw = 660
    web.crop((0, 0, WEB_W, int(WEB_W * .62))).resize((cw, int(cw * .62)), Image.LANCZOS).save(out_dir / "cover.jpg", quality=82, optimize=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(int(a) for a in sys.argv[3:4]))
