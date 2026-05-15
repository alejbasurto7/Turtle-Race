import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from constants import (
    LANE_SPACING,
    N_LANES,
    SPIRAL_STEP,
    TRACK_PADDING,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
import tracks
from tracks import (
    RECTANGULAR,
    SPIRAL,
    STRAIGHT,
    TRACK_NAMES,
    _boundary_paths,
    _build_spiral_legs,
    boundary_stones,
    build_lane_paths,
    finish_line_segments,
    lane_start_pose,
    path_length,
    position_at_arc,
    start_line_segments,
)


def _approx(a, b, tol=1e-6):
    return math.isclose(a, b, abs_tol=tol)


# ---- track names / registry ----

def test_track_names_are_complete():
    assert set(TRACK_NAMES) == {STRAIGHT, RECTANGULAR, SPIRAL}


@pytest.mark.parametrize("track", TRACK_NAMES)
def test_build_lane_paths_returns_one_per_lane(track):
    paths = build_lane_paths(track)
    assert len(paths) == N_LANES
    for p in paths:
        assert "start" in p and "legs" in p
        assert len(p["legs"]) >= 1


# ---- straight track ----

def test_straight_lane_length_matches_window_minus_padding():
    paths = build_lane_paths(STRAIGHT)
    expected = WINDOW_WIDTH - 2 * TRACK_PADDING
    for p in paths:
        assert _approx(path_length(p), expected)


def test_straight_lanes_share_x_differ_in_y():
    paths = build_lane_paths(STRAIGHT)
    xs = {p["start"][0] for p in paths}
    ys = sorted(p["start"][1] for p in paths)
    assert len(xs) == 1
    # Adjacent lanes spaced exactly LANE_SPACING apart.
    diffs = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
    for d in diffs:
        assert _approx(d, LANE_SPACING)


# ---- rectangular track ----

def test_rectangular_average_lane_length_close_to_centerline_perimeter():
    # The 4 lane lengths are symmetric around the centerline-rect perimeter
    # minus a constant offset equal to |finish_y|: each lane's closing leg
    # goes from BL up to the finish bar (not all the way back to start), so
    # every lane is shorter than its full rectangle by |finish_y - start_y|,
    # and averaging over the lanes cancels the per-lane start_y stagger.
    from tracks import _rectangular_finish_y
    paths = build_lane_paths(RECTANGULAR)
    lengths = [path_length(p) for p in paths]
    avg = sum(lengths) / len(lengths)
    centerline = 2 * (WINDOW_WIDTH - 2 * TRACK_PADDING) + 2 * (WINDOW_HEIGHT - 2 * TRACK_PADDING)
    expected = centerline + _rectangular_finish_y()  # finish_y < 0, so lanes are shorter
    assert _approx(avg, expected)


def test_rectangular_lane_ends_at_finish_bar():
    # Each lane should end on the LEFT EDGE at the finish bar's Y, so the
    # turtle physically reaches the drawn finish line.
    paths = build_lane_paths(RECTANGULAR)
    end_ys = []
    for lane_idx, path in enumerate(paths):
        sx, _sy = path["start"]
        ex, ey, _ = position_at_arc(path, path_length(path))
        assert _approx(ex, sx), f"lane {lane_idx} ends at same X as start (left edge)"
        end_ys.append(round(ey, 6))
    # All lanes terminate at the SAME Y (the finish bar Y).
    assert len(set(end_ys)) == 1, f"expected all end Ys equal, got {end_ys}"
    finish_bar = finish_line_segments(RECTANGULAR)[0]
    assert _approx(end_ys[0], finish_bar[0][1]), "end Y matches finish bar Y"


def test_rectangular_lane_first_heading_is_north():
    for lane_idx in range(N_LANES):
        _, _, h = lane_start_pose(RECTANGULAR, lane_idx)
        assert h == 90


def test_rectangular_corner_headings_are_right_turns():
    # First 4 legs are the canonical CW lap: N, E, S, W. A short 5th closing
    # leg returns each lane to its start (N for outer lanes, S for inner).
    path = build_lane_paths(RECTANGULAR)[0]
    headings = [h for h, _ in path["legs"]]
    assert headings[:4] == [90, 0, 270, 180]
    assert headings[4] in (90, 270)


def test_rectangular_outer_lane_is_longer_than_inner():
    paths = build_lane_paths(RECTANGULAR)
    # lane 0 outermost (longest), lane N-1 innermost (shortest)
    lengths = [path_length(p) for p in paths]
    for i in range(len(lengths) - 1):
        assert lengths[i] > lengths[i + 1], f"lane {i} should be longer than lane {i+1}"


def test_rectangular_lane_start_points_staggered_diagonally():
    # Lane starts form a "ladder": each lane offset both horizontally (its
    # own rect's left edge) and vertically (so the start ticks don't all
    # stack at y=0). X strictly increases from outermost to innermost; Y
    # strictly decreases (lane 0 highest, lane N-1 lowest).
    paths = build_lane_paths(RECTANGULAR)
    xs = [p["start"][0] for p in paths]
    ys = [p["start"][1] for p in paths]
    assert xs == sorted(xs)
    assert ys == sorted(ys, reverse=True)
    assert len(set(ys)) == N_LANES


def test_rectangular_lane_fits_inside_screen():
    paths = build_lane_paths(RECTANGULAR)
    half_w = WINDOW_WIDTH / 2
    half_h = WINDOW_HEIGHT / 2
    for p in paths:
        x, y = p["start"]
        # walk all legs and ensure all points stay inside the window
        for heading, length in p["legs"]:
            rad = math.radians(heading)
            x += length * math.cos(rad)
            y += length * math.sin(rad)
            assert -half_w <= x <= half_w
            assert -half_h <= y <= half_h


# ---- spiral track ----

def test_spiral_lane_start_points_staggered():
    # Each lane now starts at its own BL corner — different X AND Y per lane
    # so the start ticks appear as a staggered diagonal pattern.
    paths = build_lane_paths(SPIRAL)
    xs = [p["start"][0] for p in paths]
    ys = [p["start"][1] for p in paths]
    assert len(set(xs)) == N_LANES
    assert len(set(ys)) == N_LANES


def test_spiral_lanes_all_end_at_origin():
    paths = build_lane_paths(SPIRAL)
    for lane_idx, p in enumerate(paths):
        x, y, _ = position_at_arc(p, path_length(p))
        assert _approx(x, 0.0, tol=1e-6), f"lane {lane_idx} x={x}"
        assert _approx(y, 0.0, tol=1e-6), f"lane {lane_idx} y={y}"


def test_spiral_legs_decreasing():
    # Skip the first leg (truncated by the staggered-start head-start, so it
    # no longer fits the canonical shrinking pattern) and the final 2 homing
    # legs (vertical + horizontal, used to bring the lane orthogonally to the
    # origin). The canonical shrinking-spiral pattern only applies in between.
    paths = build_lane_paths(SPIRAL)
    for p in paths:
        legs = p["legs"][1:-2]
        # After dropping the first vertical leg, leg 0 is now horizontal.
        horizontal = [length for i, (_, length) in enumerate(legs) if i % 2 == 0]
        vertical = [length for i, (_, length) in enumerate(legs) if i % 2 == 1]
        for i in range(len(vertical) - 1):
            assert vertical[i] > vertical[i + 1]
        for i in range(len(horizontal) - 1):
            assert horizontal[i] > horizontal[i + 1]


def test_spiral_terminates_near_center():
    # Endpoint should land near the center; inner lanes overshoot slightly more
    # because their last partial pair of legs is shorter than the step. Allow
    # up to 2 * SPIRAL_STEP in either axis.
    paths = build_lane_paths(SPIRAL)
    for lane_idx, p in enumerate(paths):
        x, y, _ = position_at_arc(p, path_length(p))
        assert abs(x) <= 2 * SPIRAL_STEP, f"lane {lane_idx} x={x}"
        assert abs(y) <= 2 * SPIRAL_STEP, f"lane {lane_idx} y={y}"


def test_spiral_headings_repeat_n_e_s_w():
    legs = _build_spiral_legs(400, 300, 50)
    headings = [h for h, _ in legs]
    expected = [90, 0, 270, 180]
    for i, h in enumerate(headings):
        assert h == expected[i % 4]


def test_spiral_first_heading_is_north():
    for lane_idx in range(N_LANES):
        _, _, h = lane_start_pose(SPIRAL, lane_idx)
        assert h == 90


# ---- position_at_arc ----

def test_position_at_arc_zero_returns_start():
    for track in TRACK_NAMES:
        for lane_idx in range(N_LANES):
            path = build_lane_paths(track)[lane_idx]
            x, y, h = position_at_arc(path, 0)
            assert _approx(x, path["start"][0])
            assert _approx(y, path["start"][1])
            assert h == path["legs"][0][0]


def test_position_at_arc_clamps_past_end():
    path = build_lane_paths(STRAIGHT)[0]
    L = path_length(path)
    x_end, y_end, _ = position_at_arc(path, L)
    x_over, y_over, _ = position_at_arc(path, L + 1000)
    assert _approx(x_end, x_over)
    assert _approx(y_end, y_over)


def test_position_at_arc_walks_correctly_through_corners():
    path = build_lane_paths(RECTANGULAR)[0]
    leg0_len = path["legs"][0][1]
    # Just before the first corner, heading should still be 90 (N).
    _, _, h = position_at_arc(path, leg0_len - 1)
    assert h == 90
    # Just after the first corner, heading should be 0 (E).
    _, _, h = position_at_arc(path, leg0_len + 1)
    assert h == 0


# ---- start line ----

def test_straight_start_line_is_perpendicular_to_heading():
    # Straight returns a single connecting bar (lane 0 to lane N-1, extended).
    # That bar should be perpendicular to the initial east heading.
    bars = start_line_segments(STRAIGHT)
    assert len(bars) == 1
    (x0, y0), (x1, y1) = bars[0]
    _, _, h0 = lane_start_pose(STRAIGHT, 0)
    vx, vy = x1 - x0, y1 - y0
    rad = math.radians(h0)
    dx, dy = math.cos(rad), math.sin(rad)
    assert _approx(vx * dx + vy * dy, 0, tol=1e-6)


def test_spiral_start_returns_one_tick_per_lane():
    bars = start_line_segments(SPIRAL)
    assert len(bars) == N_LANES


def test_rectangular_finish_is_single_horizontal_bar_below_starts():
    # Closed loop, but we still draw a cosmetic finish bar below the ladder
    # of staggered starts so the two visually separate on screen.
    bars = finish_line_segments(RECTANGULAR)
    assert len(bars) == 1
    (x0, y0), (x1, y1) = bars[0]
    # Horizontal bar: both endpoints at the same Y.
    assert _approx(y0, y1)
    # Below the lowest lane start (which is the most-negative Y).
    paths = build_lane_paths(RECTANGULAR)
    min_start_y = min(p["start"][1] for p in paths)
    assert y0 < min_start_y


def test_straight_finish_segments_share_x_and_span_lanes():
    bars = finish_line_segments(STRAIGHT)
    assert len(bars) == N_LANES
    # Every bar's two endpoints share the same X (vertical bar, perpendicular
    # to the east heading), and that X is the same across all bars.
    xs = set()
    for p0, p1 in bars:
        assert _approx(p0[0], p1[0])
        xs.add(round(p0[0], 6))
    assert len(xs) == 1


def test_spiral_finish_is_single_bar_centered_on_origin():
    bars = finish_line_segments(SPIRAL)
    assert len(bars) == 1
    (x0, y0), (x1, y1) = bars[0]
    # Vertical bar with both endpoints at x == 0, centered on the origin
    # (where every lane terminates).
    assert _approx(x0, 0.0)
    assert _approx(x1, 0.0)
    ys = sorted([y0, y1])
    assert ys[0] < 0
    assert ys[1] > 0
    assert _approx(ys[0], -ys[1])


def test_straight_start_returns_one_connecting_bar():
    bars = start_line_segments(STRAIGHT)
    assert len(bars) == 1
    (x0, y0), (x1, y1) = bars[0]
    outer_x, outer_y, _ = lane_start_pose(STRAIGHT, 0)
    inner_x, inner_y, _ = lane_start_pose(STRAIGHT, N_LANES - 1)
    span_min_x = min(x0, x1)
    span_max_x = max(x0, x1)
    span_min_y = min(y0, y1)
    span_max_y = max(y0, y1)
    for x, y in [(outer_x, outer_y), (inner_x, inner_y)]:
        assert span_min_x - 1e-6 <= x <= span_max_x + 1e-6
        assert span_min_y - 1e-6 <= y <= span_max_y + 1e-6


def test_rectangular_start_returns_one_tick_per_lane():
    bars = start_line_segments(RECTANGULAR)
    assert len(bars) == N_LANES


# ---- boundary stones ----

@pytest.mark.parametrize("track", TRACK_NAMES)
def test_boundary_stones_nonempty_for_each_track(track):
    points = boundary_stones(track)
    assert len(points) > 4


def test_straight_boundary_stones_form_two_parallel_rows():
    points = boundary_stones(STRAIGHT)
    ys = {round(y, 6) for _, y in points}
    expected = {
        round((N_LANES / 2.0) * LANE_SPACING, 6),
        round(-(N_LANES / 2.0) * LANE_SPACING, 6),
    }
    assert ys == expected


def test_rectangular_boundary_stones_bracket_the_racing_band():
    # Every stone must sit either outside lane 0's bbox (outer boundary) or
    # inside lane (N-1)'s bbox (inner boundary), each by ~LANE_SPACING/2.
    eps = 1e-6
    margin = LANE_SPACING / 2.0 - eps

    o_outer = (N_LANES - 1) / 2.0 * LANE_SPACING
    bl_x = -WINDOW_WIDTH / 2 + TRACK_PADDING - o_outer
    bl_y = -WINDOW_HEIGHT / 2 + TRACK_PADDING - o_outer
    tr_x = bl_x + (WINDOW_WIDTH - 2 * TRACK_PADDING) + 2 * o_outer
    tr_y = bl_y + (WINDOW_HEIGHT - 2 * TRACK_PADDING) + 2 * o_outer

    o_inner = -(N_LANES - 1) / 2.0 * LANE_SPACING
    in_bl_x = -WINDOW_WIDTH / 2 + TRACK_PADDING - o_inner
    in_bl_y = -WINDOW_HEIGHT / 2 + TRACK_PADDING - o_inner
    in_tr_x = in_bl_x + (WINDOW_WIDTH - 2 * TRACK_PADDING) + 2 * o_inner
    in_tr_y = in_bl_y + (WINDOW_HEIGHT - 2 * TRACK_PADDING) + 2 * o_inner

    for x, y in boundary_stones(RECTANGULAR):
        outside_outer = (
            x <= bl_x - margin
            or x >= tr_x + margin
            or y <= bl_y - margin
            or y >= tr_y + margin
        )
        inside_inner = (
            in_bl_x + margin <= x <= in_tr_x - margin
            and in_bl_y + margin <= y <= in_tr_y - margin
        )
        assert outside_outer or inside_inner, (
            f"stone ({x:.3f}, {y:.3f}) inside the racing band"
        )


def test_rectangular_returns_outer_and_inner_boundary_paths():
    paths = _boundary_paths(RECTANGULAR)
    assert len(paths) == 2
    # Outer is larger than inner: bigger total perimeter.
    assert path_length(paths[0]) > path_length(paths[1])


def test_spiral_boundary_first_stone_near_outer_bl_corner():
    # The first stone of the spiral boundary should sit at the boundary's
    # BL corner — one LANE_SPACING/2 outside lane 0's BL.
    path = _boundary_paths(SPIRAL)[0]
    expected_x, expected_y = path["start"]
    first_x, first_y = boundary_stones(SPIRAL)[0]
    assert _approx(first_x, expected_x)
    assert _approx(first_y, expected_y)


@pytest.mark.parametrize("track", TRACK_NAMES)
def test_boundary_stones_fit_inside_screen(track):
    half_w = WINDOW_WIDTH / 2
    half_h = WINDOW_HEIGHT / 2
    for x, y in boundary_stones(track):
        assert -half_w <= x <= half_w, f"{track}: x={x} out of range"
        assert -half_h <= y <= half_h, f"{track}: y={y} out of range"


@pytest.mark.parametrize("track", TRACK_NAMES)
def test_boundary_stones_count_matches_path_length(track):
    # Sampling at fixed arc-length intervals produces exactly
    # floor(total / spacing) + 1 stones per boundary path.
    spacing = 10.0
    expected_total = 0
    for path in _boundary_paths(track):
        expected_total += int(path_length(path) // spacing) + 1
    assert len(boundary_stones(track, spacing=spacing)) == expected_total
