# Build Summary: Plan 2.1

## Status: complete

## Tasks Completed

### Task 1 — Add N=3/N=4 parametrized geometry tests to tests/test_tracks.py

Added 5 new parametrized test functions at the bottom of `tests/test_tracks.py`, covering
all 6 `(track, n)` pairs `{STRAIGHT, RECTANGULAR, SPIRAL} x {3, 4}`:

1. `test_n_start_positions_are_distinct` — asserts `len(paths) == n` and `len(set(starts)) == n`
2. `test_n_start_positions_within_canvas_bounds` — asserts each start (x, y) is within
   `+-WINDOW_WIDTH/2, +-WINDOW_HEIGHT/2`
3. `test_straight_lanes_n_spaced_by_lane_spacing` — asserts sorted Y diffs equal `LANE_SPACING`
4. `test_spiral_n_lanes_all_end_at_origin` — asserts each spiral lane's final position is
   approximately `(0, 0)` (tol=1e-6)
5. `test_finish_line_segment_count` — parametrized over 6 `(track, n, expected)` tuples
   per RESEARCH.md Section 7 Test 5

Also added a module-level docstring noting the parametrize usage convention.

New test invocations: 22 (6+6+2+2+6). All passed immediately; tracks.py was already N-agnostic.

### Task 2 — Refactor race.py (generalize from turtles-only to N racers)

(1) Import: dropped TURTLE_NAMES, added SPECIES.
(2) create_turtles(color_list) -> create_racers(species: str): reads SPECIES[species]["names"]
    and ["colors"], returns [{'name': ..., 'color': ..., 'o': Turtle(...)}].
(3) place_turtles_on_track -> place_racers_on_track(racers, track_name): n=len(racers),
    tortuga -> racer, passes n to tracks.lane_start_pose.
(4) run_race: turtles_list -> racers (14 sites), n=len(racers), build_lane_paths gets n.
(5) TURTLE_NAMES logging -> racers[i]['name'] (lines 181, 228; fallback removed).
(6) tortuga -> racer in show_podium (lines 247-248).
(7) draw_start_line(track_name, n), draw_boundary_stones(track_name, n),
    draw_finish_line(track_name, n) — all forward n to tracks.* calls.
(8) show_podium/announce_result: turtles_list -> racers.

## Files Modified

- tests/test_tracks.py
- race.py
- .shipyard/phases/2/results/SUMMARY-2.1.md

## Decisions Made

1. Module docstring vs inline comment: used a docstring (first string literal in file).
2. Inner `turtle` loop variable in show_podium kept as `turtle` per CONTEXT-2.md Decision 5.
3. announce_result emoji (turtle-specific) replaced with "racer" for species-agnostic output.

## Issues Encountered

None. All renames were mechanical.

## End State

- pytest: 76 passed, 0 failed (54 baseline + 22 new)
- python main.py: intentionally broken (Plan 3.1 fixes main.py)
- grep turtles_list|create_turtles|place_turtles_on_track|tortuga race.py: zero matches
- grep TURTLE_NAMES race.py: zero matches
- SPECIES imported in race.py: confirmed

## Verification Results

Task 1 verify: pytest tests/test_tracks.py -v -k "..." -> 22 passed, 42 deselected
Task 1 full: pytest tests/test_tracks.py -> 64 passed in 0.12s
Task 2 verify: pytest (full) -> 76 passed in 0.10s
Task 2 verify: python -c "import race; assert hasattr(race, 'create_racers')..." -> renames complete
Task 2: banned-identifier grep -> zero matches
Task 2: TURTLE_NAMES grep -> zero matches
