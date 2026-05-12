"""Generate the 3 track-preview PNGs shown in the track-selection dialog.

Run once when the design changes; the resulting PNGs are committed to the repo.

    python tools/generate_track_previews.py
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageOps

# Make the project root importable so we can pull the canvas size constants.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from constants import TRACK_PREVIEW_H, TRACK_PREVIEW_W  # noqa: E402

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
LAWN_PATH = os.path.join(PROJECT_ROOT, "lawn.jpg")

STROKE = (255, 255, 255)              # bold white reads cleanly over grass
STROKE_SHADOW = (20, 50, 20)          # very dark green, drawn 1 px offset for legibility
SHADOW_OFFSET = (1, 1)
FRAME = (180, 180, 180)
LINE_WIDTH = 4
ARROW_SIZE = 12
INSET = 16


_lawn_tile_cache: Image.Image | None = None


def _load_lawn_tile() -> Image.Image:
    global _lawn_tile_cache
    if _lawn_tile_cache is None:
        src = Image.open(LAWN_PATH).convert("RGB")
        _lawn_tile_cache = ImageOps.fit(
            src,
            (TRACK_PREVIEW_W, TRACK_PREVIEW_H),
            method=Image.LANCZOS,
        )
    return _lawn_tile_cache.copy()


def _new_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = _load_lawn_tile()
    draw = ImageDraw.Draw(img)
    # Subtle frame around the canvas so each tile reads as a "scene".
    draw.rectangle(
        [(0, 0), (TRACK_PREVIEW_W - 1, TRACK_PREVIEW_H - 1)],
        outline=FRAME,
        width=1,
    )
    return img, draw


def _stroke_line(
    draw: ImageDraw.ImageDraw,
    p0: tuple[float, float],
    p1: tuple[float, float],
    width: int = LINE_WIDTH,
) -> None:
    sx, sy = SHADOW_OFFSET
    draw.line(
        [(p0[0] + sx, p0[1] + sy), (p1[0] + sx, p1[1] + sy)],
        fill=STROKE_SHADOW,
        width=width,
    )
    draw.line([p0, p1], fill=STROKE, width=width)


def _stroke_polygon(
    draw: ImageDraw.ImageDraw,
    pts: list[tuple[float, float]],
) -> None:
    sx, sy = SHADOW_OFFSET
    draw.polygon([(p[0] + sx, p[1] + sy) for p in pts], fill=STROKE_SHADOW)
    draw.polygon(pts, fill=STROKE)


def _arrowhead(
    draw: ImageDraw.ImageDraw,
    tip: tuple[float, float],
    heading_deg: float,
    size: int = ARROW_SIZE,
) -> None:
    """Filled triangular arrowhead at `tip` pointing along `heading_deg`.

    Convention: heading 0 = east, 90 = north (PIL y grows DOWN, so we flip).
    """
    rad = math.radians(heading_deg)
    bx = tip[0] - size * math.cos(rad)
    by = tip[1] + size * math.sin(rad)
    perp = rad + math.pi / 2
    half = size * 0.6
    p1 = (bx + half * math.cos(perp), by - half * math.sin(perp))
    p2 = (bx - half * math.cos(perp), by + half * math.sin(perp))
    _stroke_polygon(draw, [tip, p1, p2])


def make_straight() -> Image.Image:
    img, draw = _new_canvas()
    y = TRACK_PREVIEW_H // 2
    x_start = INSET + 6
    x_end = TRACK_PREVIEW_W - INSET - 6
    _stroke_line(draw, (x_start, y), (x_end, y))
    _arrowhead(draw, (x_end, y), heading_deg=0)
    return img


def make_rectangular() -> Image.Image:
    img, draw = _new_canvas()
    left = INSET
    right = TRACK_PREVIEW_W - INSET
    top = INSET
    bottom = TRACK_PREVIEW_H - INSET
    # Loop outline (4 sides)
    _stroke_line(draw, (left, top), (right, top))
    _stroke_line(draw, (right, top), (right, bottom))
    _stroke_line(draw, (right, bottom), (left, bottom))
    _stroke_line(draw, (left, bottom), (left, top))
    # Three arrowheads showing the clockwise travel direction.
    mid_x = (left + right) // 2
    mid_y = (top + bottom) // 2
    _arrowhead(draw, (mid_x, top), heading_deg=0)        # top edge -> east
    _arrowhead(draw, (right, mid_y), heading_deg=270)    # right edge -> south
    _arrowhead(draw, (mid_x, bottom), heading_deg=180)   # bottom edge -> west
    return img


def make_spiral() -> Image.Image:
    img, draw = _new_canvas()
    left = INSET
    right = TRACK_PREVIEW_W - INSET
    top = INSET
    bottom = TRACK_PREVIEW_H - INSET
    w = right - left
    h = bottom - top
    step = 14
    # Continuous CW rectangular spiral, starting at bottom-left going north.
    # Mirrors the heading sequence in tracks.py (N, E, S, W) where each pair
    # shrinks by `step`. PIL y grows DOWN, so N = (0, -1), S = (0, +1).
    deltas = ((0, -1), (1, 0), (0, 1), (-1, 0))
    headings_deg = (90, 0, 270, 180)
    x, y = left, bottom
    legs: list[tuple[tuple[float, float], tuple[float, float], int]] = []
    for n in range(40):
        pair_idx = n // 2
        length = (h if n % 2 == 0 else w) - pair_idx * step
        if length < step:
            break
        dx, dy = deltas[n % 4]
        nx, ny = x + dx * length, y + dy * length
        legs.append(((x, y), (nx, ny), headings_deg[n % 4]))
        x, y = nx, ny
    # Two passes so each shadow stays behind the white pass and corners stay clean.
    sox, soy = SHADOW_OFFSET
    for p0, p1, _ in legs:
        draw.line(
            [(p0[0] + sox, p0[1] + soy), (p1[0] + sox, p1[1] + soy)],
            fill=STROKE_SHADOW,
            width=LINE_WIDTH,
        )
    for p0, p1, _ in legs:
        draw.line([p0, p1], fill=STROKE, width=LINE_WIDTH)
    if legs:
        # Start arrowhead a short way up the first leg, pointing in its direction.
        (sx0, sy0), _, h0 = legs[0]
        rad0 = math.radians(h0)
        start_tip = (sx0 + 20 * math.cos(rad0), sy0 - 20 * math.sin(rad0))
        _arrowhead(draw, start_tip, heading_deg=h0)
        # End arrowhead at the spiral's inner endpoint, pointing in the final leg direction.
        _, end_pt, h_end = legs[-1]
        _arrowhead(draw, end_pt, heading_deg=h_end)
    return img


def main() -> None:
    os.makedirs(ASSETS_DIR, exist_ok=True)
    outputs = {
        "track_straight.png": make_straight(),
        "track_rectangular.png": make_rectangular(),
        "track_spiral.png": make_spiral(),
    }
    for name, img in outputs.items():
        path = os.path.join(ASSETS_DIR, name)
        img.save(path, "PNG")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
