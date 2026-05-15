"""Race-track geometry for the turtle race.

Each track is rendered as `n` discrete paths (one per racer) rather than
a single centerline with runtime perpendicular offsets — this avoids visual
discontinuities at corners. A path is a list of `(heading_deg, length_px)`
legs starting from `start = (x, y)`. The lane index convention:

    lane 0 = OUTERMOST (leftmost relative to initial heading)
    lane n-1 = INNERMOST

For STRAIGHT the lanes are parallel and equal-length. For RECTANGULAR and
SPIRAL the lanes are nested with different perimeters, so the race uses a
fractional progress parameter (see `main.run_race`) to keep it bias-free.
"""

from __future__ import annotations

import math
from constants import (
    TRACK_PADDING,
    LANE_SPACING,
    SPIRAL_STEP,
    WINDOW_WIDTH as _DEFAULT_W,
    WINDOW_HEIGHT as _DEFAULT_H,
)

STRAIGHT = "straight"
RECTANGULAR = "rectangular"
SPIRAL = "spiral"

TRACK_NAMES = (STRAIGHT, RECTANGULAR, SPIRAL)
TRACK_LABELS = {
    STRAIGHT: "Straight",
    RECTANGULAR: "Rectangular",
    SPIRAL: "Spiral",
}

# Runtime window size — main.py calls set_window_size() once it knows the
# actual screen dimensions. Falls back to the constants for tests.
_window_w: float = float(_DEFAULT_W)
_window_h: float = float(_DEFAULT_H)


def set_window_size(width: float, height: float) -> None:
    global _window_w, _window_h
    _window_w = float(width)
    _window_h = float(height)


def _window() -> tuple[float, float]:
    return _window_w, _window_h


def _lane_coefficient(lane_idx: int, n: int) -> float:
    """Signed offset multiplier. Lane 0 = +(n-1)/2 (outermost), lane n-1 = -(n-1)/2."""
    return (n - 1) / 2.0 - lane_idx


def _move(x: float, y: float, heading: float, length: float) -> tuple[float, float]:
    rad = math.radians(heading)
    return x + length * math.cos(rad), y + length * math.sin(rad)


def _straight_lane(lane_idx: int, n: int) -> dict:
    W, _H = _window()
    coeff = _lane_coefficient(lane_idx, n)
    y = coeff * LANE_SPACING
    x0 = -W / 2 + TRACK_PADDING
    length = W - 2 * TRACK_PADDING
    return {"start": (x0, y), "legs": [(0, length)]}


def _rectangular_lane(lane_idx: int, n: int) -> dict:
    """Each lane is a nested rectangle.

    Lane starts are staggered both horizontally (each lane on its own rect's
    left edge) and vertically (Y offset proportional to the lane's outward
    offset), so the 4 starts form a "ladder" — diagonal staircase — matching
    the staggered-start convention of real racing tracks. The path is 5 legs:
    N up to TL, E across top, S down right, W across bottom to BL, then N
    along the left edge UP TO THE FINISH BAR Y (not back to the lane's start).
    Every corner is a right turn, every lane. Each turtle physically reaches
    the finish bar on its left edge when its path completes.
    """
    W, H = _window()
    o = _lane_coefficient(lane_idx, n) * LANE_SPACING
    bl_x = -W / 2 + TRACK_PADDING - o
    bl_y = -H / 2 + TRACK_PADDING - o
    w = (W - 2 * TRACK_PADDING) + 2 * o
    h = (H - 2 * TRACK_PADDING) + 2 * o
    start_x = bl_x
    start_y = o                                 # ladder stagger: lane 0 top, lane n-1 bottom
    first_leg = (H / 2 - TRACK_PADDING + o) - start_y   # = H/2 - P (same for all lanes)
    closing_leg = _rectangular_finish_y(n) - bl_y        # BL up to the finish bar

    return {
        "start": (start_x, start_y),
        "legs": [
            (90, first_leg),
            (0, w),
            (270, h),
            (180, w),
            (90, closing_leg),
        ],
    }


def _rectangular_finish_y(n: int) -> float:
    """Y coordinate of the rectangular track's finish bar.

    One LANE_SPACING below the lowest start tick (lane n-1, at y = -(n-1)/2 * LANE_SPACING),
    giving clear visual separation between the start ladder and the finish line.
    """
    return -((n - 1) / 2.0 + 1) * LANE_SPACING


def _spiral_lane(lane_idx: int, n: int) -> dict:
    """Each lane is a nested rectangular spiral.

    Each lane starts on its own outermost-lap left edge, shifted NORTH along
    that edge by a per-lane head-start (outer lanes get the largest shift,
    innermost gets none) so the start ticks form a pronounced staircase
    rising toward the outer lane — the standard staggered-start convention
    of real racing tracks. The path then runs the standard CW spiral inward
    and finishes with a "homing" leg from the spiral's natural endpoint to
    the canvas origin (0, 0) so every lane terminates at the same point and
    the finish line can be drawn as a single straight bar there.

    Spiral pair-count is capped via `_spiral_pair_cap()` so all lanes run
    the same number of spiral legs (keeps natural endpoints clustered, so
    the homing legs are similar in length across lanes).
    """
    W, H = _window()
    o = _lane_coefficient(lane_idx, n) * LANE_SPACING
    bl_x = -W / 2 + TRACK_PADDING - o
    bl_y = -H / 2 + TRACK_PADDING - o
    w = (W - 2 * TRACK_PADDING) + 2 * o
    h = (H - 2 * TRACK_PADDING) + 2 * o

    full_spiral = _build_spiral_legs(w, h, SPIRAL_STEP, max_pairs=_spiral_pair_cap(n))
    if not full_spiral:
        return {"start": (bl_x, bl_y), "legs": []}

    # Walk the spiral from BL to find the natural endpoint, then home to
    # (0, 0) via TWO orthogonal legs (vertical first, then horizontal) so
    # the path stays on N/E/S/W grid lines instead of cutting diagonally.
    cx, cy = bl_x, bl_y
    for heading, length in full_spiral:
        rad = math.radians(heading)
        cx += length * math.cos(rad)
        cy += length * math.sin(rad)

    legs = list(full_spiral)
    vert_heading = 270 if cy > 0 else 90        # S (270) if north of origin, else N (90)
    legs.append((vert_heading, abs(cy)))
    horiz_heading = 180 if cx > 0 else 0        # W (180) if east of origin, else E (0)
    legs.append((horiz_heading, abs(cx)))

    # Staggered start: shift each lane's start up its first (north) leg by an
    # amount proportional to its outer-ness, then shorten the first leg by
    # the same amount. The leg's endpoint — and therefore every leg after it
    # and the natural endpoint — stays put, so the homing legs above remain
    # correct without recomputation.
    pre_distance = (n - 1 - lane_idx) * (LANE_SPACING * 2)
    first_heading, first_length = legs[0]
    pre_distance = min(pre_distance, max(first_length - 1, 0))
    legs[0] = (first_heading, first_length - pre_distance)
    return {"start": (bl_x, bl_y + pre_distance), "legs": legs}


def _spiral_pair_cap(n: int) -> int:
    """Common max-pair count for every lane's spiral.

    Based on the innermost lane's shortest dimension and SPIRAL_STEP, minus
    one to drop the innermost pair (per user request — keeps finish lines
    clustered). Clamped to >=1 so small canvases still draw at least one
    pair of legs after the approach.
    """
    _W, H = _window()
    inner_o = -((n - 1) / 2.0) * LANE_SPACING  # most-negative offset = innermost
    inner_h = H - 2 * TRACK_PADDING + 2 * inner_o
    return max(1, int(inner_h // SPIRAL_STEP) - 1)


def _build_spiral_legs(w: float, h: float, step: float, max_pairs: int | None = None,
                       max_legs: int = 200) -> list[tuple[float, float]]:
    """Build a clockwise rectangular spiral starting at bottom-left going north.

    Heading sequence (N, E, S, W) repeating; length pairs decrease by `step`.
    `max_pairs` (if given) caps the number of full (vertical, horizontal)
    pairs traversed.
    """
    headings = (90, 0, 270, 180)
    legs: list[tuple[float, float]] = []
    for n in range(max_legs):
        pair_idx = n // 2
        if max_pairs is not None and pair_idx >= max_pairs:
            break
        length = (h if n % 2 == 0 else w) - pair_idx * step
        if length <= 0:
            break
        legs.append((headings[n % 4], length))
    return legs


_LANE_BUILDERS = {
    STRAIGHT: _straight_lane,
    RECTANGULAR: _rectangular_lane,
    SPIRAL: _spiral_lane,
}


def build_lane_paths(track_name: str, n: int) -> list[dict]:
    """Return one path dict per lane, indexed 0..n-1."""
    builder = _LANE_BUILDERS[track_name]
    return [builder(i, n) for i in range(n)]


def path_length(path: dict) -> float:
    return float(sum(length for _, length in path["legs"]))


def position_at_arc(path: dict, arc: float) -> tuple[float, float, float]:
    """Return (x, y, heading_deg) at arc-length `arc` along the path.

    `arc` is clamped to [0, path_length(path)].
    """
    x, y = path["start"]
    if arc <= 0:
        first_heading = path["legs"][0][0] if path["legs"] else 0
        return x, y, first_heading
    remaining = arc
    last_heading = path["legs"][-1][0]
    for heading, length in path["legs"]:
        if remaining <= length:
            x, y = _move(x, y, heading, remaining)
            return x, y, heading
        x, y = _move(x, y, heading, length)
        remaining -= length
        last_heading = heading
    return x, y, last_heading


def lane_start_pose(track_name: str, lane_idx: int, n: int) -> tuple[float, float, float]:
    """Where lane `lane_idx` begins: (x, y, initial_heading)."""
    path = _LANE_BUILDERS[track_name](lane_idx, n)
    x, y = path["start"]
    heading = path["legs"][0][0] if path["legs"] else 0
    return x, y, heading


def start_line_segments(track_name: str, n: int) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Return start-line segments to draw.

    STRAIGHT/RECTANGULAR: a single bar through the lane-0 and lane-(n-1)
    start points (perpendicular to the initial heading), since those lanes
    share a common starting Y/X and the bar tiles cleanly across them.
    SPIRAL: separate vertical tick marks, one per lane, since each lane
    begins at its own BL corner (staggered diagonally).
    """
    if track_name in (SPIRAL, RECTANGULAR):
        # Horizontal tick per lane (constant y, vary x). Lane starts are
        # diagonally staggered, so the ticks appear at different y values
        # and read as a visible staircase rather than merging into one bar.
        ext = LANE_SPACING / 2
        bars: list[tuple[tuple[float, float], tuple[float, float]]] = []
        for lane_idx in range(n):
            x, y, _ = lane_start_pose(track_name, lane_idx, n)
            bars.append(((x - ext, y), (x + ext, y)))
        return bars

    x0, y0, h0 = lane_start_pose(track_name, 0, n)
    x1, y1, _ = lane_start_pose(track_name, n - 1, n)
    rad = math.radians(h0)
    px, py = -math.sin(rad), math.cos(rad)  # perpendicular-left of initial heading
    ext = LANE_SPACING / 2
    return [((x0 + px * ext, y0 + py * ext), (x1 - px * ext, y1 - py * ext))]


def _boundary_paths(track_name: str, n: int) -> list[dict]:
    """Outer-boundary geometry used for stone placement.

    STRAIGHT returns two parallel single-leg paths (top and bottom edges of
    the lane stack). RECTANGULAR and SPIRAL return one path each: a single
    outer perimeter half a LANE_SPACING outside lane 0, built by plugging a
    larger offset `o` into the same generators used for lanes — no new
    perpendicular-offset math needed.
    """
    if track_name == STRAIGHT:
        W, _H = _window()
        x0 = -W / 2 + TRACK_PADDING
        length = W - 2 * TRACK_PADDING
        y_top = (n / 2.0) * LANE_SPACING
        y_bot = -(n / 2.0) * LANE_SPACING
        return [
            {"start": (x0, y_top), "legs": [(0, length)]},
            {"start": (x0, y_bot), "legs": [(0, length)]},
        ]

    W, H = _window()
    o = (n / 2.0) * LANE_SPACING            # half a lane outside lane 0
    bl_x = -W / 2 + TRACK_PADDING - o
    bl_y = -H / 2 + TRACK_PADDING - o
    w = (W - 2 * TRACK_PADDING) + 2 * o
    h = (H - 2 * TRACK_PADDING) + 2 * o

    if track_name == RECTANGULAR:
        # Outer boundary: half a lane outside lane 0 (closed loop, no
        # finish-bar gap unlike _rectangular_lane).
        outer = {"start": (bl_x, bl_y),
                 "legs": [(90, h), (0, w), (270, h), (180, w)]}
        # Inner boundary: half a lane INSIDE lane n-1 (the innermost lane).
        # Plug a negative `o` into the same formula.
        o_in = -(n / 2.0) * LANE_SPACING
        in_bl_x = -W / 2 + TRACK_PADDING - o_in
        in_bl_y = -H / 2 + TRACK_PADDING - o_in
        in_w = (W - 2 * TRACK_PADDING) + 2 * o_in
        in_h = (H - 2 * TRACK_PADDING) + 2 * o_in
        inner = {"start": (in_bl_x, in_bl_y),
                 "legs": [(90, in_h), (0, in_w), (270, in_h), (180, in_w)]}
        return [outer, inner]

    if track_name == SPIRAL:
        # Same shrinking-spiral generator as the lanes. Lanes use
        # _spiral_pair_cap() for cross-lane consistency (that cap is sized
        # for the INNERMOST lane), but the boundary is bigger and can fit
        # more loops naturally. Run it to its natural end, then drop the
        # innermost pair of legs so the boundary stones stop short of the
        # finish-line bar that's drawn through the origin.
        legs = _build_spiral_legs(w, h, SPIRAL_STEP)
        if len(legs) >= 4:
            legs = legs[:-2]
        return [{"start": (bl_x, bl_y), "legs": legs}]

    raise KeyError(track_name)


def boundary_stones(track_name: str, n: int, spacing: float = 10.0) -> list[tuple[float, float]]:
    """Return (x, y) center points for stones along the outer boundary.

    Samples each boundary path at fixed arc-length intervals of `spacing`
    pixels. The first stone of each path sits at the path's start.
    """
    points: list[tuple[float, float]] = []
    for path in _boundary_paths(track_name, n):
        total = path_length(path)
        i = 0
        while True:
            arc = i * spacing
            if arc > total:
                break
            x, y, _ = position_at_arc(path, arc)
            points.append((x, y))
            i += 1
    return points


def finish_line_segments(track_name: str, n: int) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Return finish-line bar endpoints.

    STRAIGHT: a perpendicular tick at each lane's endpoint. Lanes share an
    X coordinate and have adjacent Y centers, so the ticks tile into a
    single vertical line at the right edge.
    SPIRAL: every lane homes to (0, 0), so a single vertical bar through
    the origin is "the" finish line.
    RECTANGULAR: closed loop (path returns to start), so the finish bar is
    cosmetic — a single horizontal bar drawn below all the staggered start
    ticks so the start and finish don't visually collapse on top of each
    other.
    """
    if track_name == RECTANGULAR:
        W, _H = _window()
        y = _rectangular_finish_y(n)
        # Length spans the full ladder width plus a small extension on each side.
        center_x = -W / 2 + TRACK_PADDING
        half_len = (n * LANE_SPACING) / 2 + LANE_SPACING
        return [((center_x - half_len, y), (center_x + half_len, y))]

    if track_name == SPIRAL:
        # Vertical bar centered on the origin (where every lane terminates),
        # sitting in the empty inner area of the spiral.
        half_len = n * LANE_SPACING
        return [((0.0, -half_len), (0.0, half_len))]

    paths = build_lane_paths(track_name, n)
    bars: list[tuple[tuple[float, float], tuple[float, float]]] = []
    ext = LANE_SPACING / 2
    for p in paths:
        total = path_length(p)
        x, y, heading = position_at_arc(p, total)
        rad = math.radians(heading)
        px, py = -math.sin(rad), math.cos(rad)
        bars.append(((x + px * ext, y + py * ext), (x - px * ext, y - py * ext)))
    return bars
