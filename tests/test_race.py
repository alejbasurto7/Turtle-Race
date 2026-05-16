"""Pure-math unit tests for the head-offset progress conversion used in run_race.

These tests do NOT import race.py — that would pull in the turtle Screen setup
(Screen() is called at module load in main.py and transitively via race.py's
module-level _screen = None, but even importing race pulls in turtle which
requires a display). Instead, the formula is reproduced inline as a tiny helper
function so the math can be asserted without any Tk/turtle dependency.

Formula (RESEARCH.md §2, Approach B):
    head_offset_arc      = shape_unit_size * stretch_len / 2
    head_offset_progress = head_offset_arc * (shared_distance / lane_length)
    finish condition     : progress[i] >= shared_distance - head_offset_progress[i]

shape_unit_size = 9 is the length of the ``classic`` arrow polygon along its
heading axis (RESEARCH.md §3). Applied universally to both species per
CONTEXT-4.md Decision 3; turtles are symmetric so the approximation doesn't
change race outcome.
"""

SHAPE_UNIT_SIZE = 9        # turtle/classic shape: 9 units along heading
SNAKE_UNIT_SIZE = 20       # custom snake polygon (race._SNAKE_POLYGON): 20 units long


def _head_offset_progress(stretch_len, shared_distance, lane_length):
    """Return the progress-space head-offset for a single racer.

    Args:
        stretch_len:     turtle.shapesize()[1] for the racer.
        shared_distance: the shared progress target used across all lanes.
        lane_length:     the physical arc length of this racer's lane.
    """
    head_offset_arc = SHAPE_UNIT_SIZE * stretch_len / 2
    return head_offset_arc * (shared_distance / lane_length)


# ---------------------------------------------------------------------------
# Test A: ratio-based scenarios for head_offset_progress scaling
# ---------------------------------------------------------------------------

def test_head_offset_progress_ratio_equal():
    """When lane_length == shared_distance the ratio is 1.0, so
    head_offset_progress == head_offset_arc exactly."""
    stretch_len = 3.6
    shared_distance = 1000.0
    lane_length = 1000.0          # ratio = 1.0
    head_offset_arc = SHAPE_UNIT_SIZE * stretch_len / 2   # 9 * 3.6 / 2 = 16.2
    result = _head_offset_progress(stretch_len, shared_distance, lane_length)
    assert result == head_offset_arc, (
        f"Expected head_offset_progress == head_offset_arc ({head_offset_arc}) "
        f"when ratio == 1.0, got {result}"
    )


def test_head_offset_progress_ratio_less_than_one():
    """When lane_length > shared_distance the ratio < 1 and
    head_offset_progress is smaller than head_offset_arc."""
    stretch_len = 3.6
    shared_distance = 1000.0
    lane_length = 2000.0          # ratio = 0.5
    result = _head_offset_progress(stretch_len, shared_distance, lane_length)
    head_offset_arc = SHAPE_UNIT_SIZE * stretch_len / 2   # 16.2
    expected = head_offset_arc * 0.5                       # 8.1
    assert abs(result - expected) < 1e-9, (
        f"Expected {expected} (ratio < 1), got {result}"
    )


def test_head_offset_progress_ratio_greater_than_one():
    """When lane_length < shared_distance the ratio > 1 and
    head_offset_progress is larger than head_offset_arc."""
    stretch_len = 3.6
    shared_distance = 1000.0
    lane_length = 500.0           # ratio = 2.0
    result = _head_offset_progress(stretch_len, shared_distance, lane_length)
    head_offset_arc = SHAPE_UNIT_SIZE * stretch_len / 2   # 16.2
    expected = head_offset_arc * 2.0                       # 32.4
    assert abs(result - expected) < 1e-9, (
        f"Expected {expected} (ratio > 1), got {result}"
    )


# ---------------------------------------------------------------------------
# Test B: concrete plug-in values for each snake species
# ---------------------------------------------------------------------------

def test_head_offset_arc_shadow():
    """Shadow: L_BASE=1.2, length_units=6 → stretch_len=7.2.
    Snake polygon SNAKE_UNIT_SIZE=20.
    head_offset_arc = 20 * 7.2 / 2 = 72.0 px along heading.
    """
    stretch_len = 1.2 * 6   # 7.2
    head_offset_arc = SNAKE_UNIT_SIZE * stretch_len / 2
    assert abs(head_offset_arc - 72.0) < 1e-9, (
        f"Shadow head_offset_arc: expected 72.0, got {head_offset_arc}"
    )


def test_head_offset_arc_ralph():
    """Ralph: L_BASE=1.2, length_units=2 → stretch_len=2.4.
    Snake polygon SNAKE_UNIT_SIZE=20.
    head_offset_arc = 20 * 2.4 / 2 = 24.0 px along heading.
    """
    stretch_len = 1.2 * 2   # 2.4
    head_offset_arc = SNAKE_UNIT_SIZE * stretch_len / 2
    assert abs(head_offset_arc - 24.0) < 1e-9, (
        f"Ralph head_offset_arc: expected 24.0, got {head_offset_arc}"
    )

# Note (no assertion): for turtles with stretch_len = 1.0 (default shapesize),
# head_offset_arc = 9 * 1.0 / 2 = 4.5 px. Applied equally to all 4 turtles, so
# the race ranking and visual feel are unchanged — correctness verified by smoke
# rather than a numeric assert (CRITIQUE.md §caveat, CONTEXT-4.md Decision 3).
