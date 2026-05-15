---
phase: 2-snakes-racer-mode
plan: 2.1
wave: 2
dependencies: [1.1]
must_haves:
  - Parametrized N=3 + N=4 geometry tests added to tests/test_tracks.py (Approach A — pytest.mark.parametrize, per RESEARCH.md Section 7 recommendation)
  - race.py refactored: turtles_list → racers (14 sites), tortuga → racer (4 sites)
  - create_turtles(color_list) → create_racers(species: str) — reads SPECIES[species]["names"] and ["colors"]; returns [{'o': ..., 'color': ..., 'name': ...}]
  - place_turtles_on_track → place_racers_on_track(racers, track_name) — derives n = len(racers) internally
  - draw_start_line / draw_boundary_stones / draw_finish_line take an explicit `n` parameter
  - Every tracks.* call from race.py passes n
  - TURTLE_NAMES import dropped from race.py; logging uses racer['name'] instead
  - SPECIES imported in race.py
  - Full pytest green at end of plan, including new N=3 + N=4 parametrized cases
files_touched:
  - tests/test_tracks.py
  - race.py
tdd: true
risk: medium
---

# Plan 2.1 — Add N=3 geometry tests + generalize race.py (TDD)

## Context

Wave 1 (Plan 1.1) parameterized tracks.py and updated existing tests to pass `n=4` explicitly. The test surface is unchanged from pre-Phase-2.

This plan does two coupled things that share the test file and exercise the same tracks.* code paths:

1. **TDD step:** Add parametrized N=3 + N=4 geometry tests to `tests/test_tracks.py` per RESEARCH.md Section 7. These tests run against the already-refactored tracks.py from Plan 1.1 — they should pass immediately because tracks.py is already N-agnostic. The point is to lock in N=3 geometry correctness *before* race.py starts passing N=3-sized racer lists in Phase 3+.

2. **Refactor step:** Rename and generalize race.py per CONTEXT-2.md Decisions 4, 5, 7 and RESEARCH.md Section 2. End state: race.py operates on a list of racers of arbitrary length, calls tracks.* with `n = len(racers)` everywhere, and reads names from `racer['name']` instead of the `TURTLE_NAMES` module-level constant.

Both steps land in one plan because they're tightly coupled (race.py refactor's correctness depends on the N=3 geometry tests passing; the test-file extension uses the same parametrize style we want for the long-haul). main.py is **NOT** touched here — it stays referencing `create_turtles`/`turtles_list`/etc., which means the test suite is green at the close of this plan but `python main.py` will be broken until Plan 3.1.

**Approach A (parametrize) is chosen** per RESEARCH.md Section 7 recommendation: the file already uses `@pytest.mark.parametrize("track", TRACK_NAMES)` at 4 sites, so this is not a true style break. Add a 1-line module comment noting the parametrize usage.

## Dependencies

- **Plan 1.1** — tracks.py must already take `n` explicitly; N_LANES must already be deleted.

## Tasks

<task id="1" files="tests/test_tracks.py" tdd="true">
  <action>Add new parametrized geometry tests for N ∈ {3, 4} to tests/test_tracks.py. Per RESEARCH.md Section 7, add these tests (place at the bottom of the file, after the existing tests, with a short comment introducing the parametrized-N block): (1) `test_n_start_positions_are_distinct(track, n)` over the 6 (track, n) pairs — asserts `len(build_lane_paths(track, n)) == n` AND `len(set(starts)) == n`. (2) `test_n_start_positions_within_canvas_bounds(track, n)` over the same 6 pairs — asserts each start (x, y) is within ±WINDOW_WIDTH/2, ±WINDOW_HEIGHT/2. (3) `test_straight_lanes_n_spaced_by_lane_spacing(n)` over n ∈ {3, 4} — asserts sorted Y diffs equal LANE_SPACING. (4) `test_spiral_n_lanes_all_end_at_origin(n)` over n ∈ {3, 4} — asserts each spiral lane's final position is approximately (0, 0). (5) `test_finish_line_segment_count(track, n, expected_count)` parametrized over the 6 (track, n, expected) tuples in RESEARCH.md Section 7 Test 5. Also add a 1-line module-level comment near the top: `# Note: parametrize is used below for N=3/N=4 coverage; the existing single-track parametrize precedent is at lines 44, 333, 400, 409.`</action>
  <verify>pytest tests/test_tracks.py -v -k "n_start_positions or spiral_n_lanes or finish_line_segment_count or straight_lanes_n_spaced"</verify>
  <done>All 5 new parametrized tests pass. Total of 18 new test invocations across the (track, n) pairs (6+6+2+2+6 = 22 per RESEARCH.md Section 7 counts; precise count documented in SUMMARY). Existing tests still pass: `pytest tests/test_tracks.py` is green.</done>
</task>

<task id="2" files="race.py" tdd="false">
  <action>Refactor race.py per CONTEXT-2.md Decisions 4, 5, 7 and RESEARCH.md Section 2. Specifically:
(1) Update imports: drop `TURTLE_NAMES` (currently imported on race.py line 9 area); add `SPECIES`.
(2) Replace `create_turtles(color_list)` with `create_racers(species: str)`. Implementation: reads `SPECIES[species]["names"]` and `["colors"]`; iterates `zip(names, colors)`; appends `{'name': name, 'color': color, 'o': Turtle(shape="turtle")}` to the racers list; returns the list. Add an inline comment: `# Shape dispatch (shape_drawer sentinel) is Phase 4's concern.`
(3) Rename `place_turtles_on_track(turtles_list, track_name)` → `place_racers_on_track(racers, track_name)`. Inside the function: rename loop variable `tortuga` → `racer`; compute `n = len(racers)` at the top; pass `n` to the `tracks.lane_start_pose(track_name, i, n)` call on line 145.
(4) In `run_race(turtles_list, track_name, user_bet)`, rename parameter to `racers`. Compute `n = len(racers)` once at the top. Update the `tracks.build_lane_paths(track_name)` call on line 169 to `tracks.build_lane_paths(track_name, n)`. The `shared_distance` formula is N-safe per RESEARCH.md Section 2 (`avg_lane_length = sum / len(lane_paths)`) — no formula change needed. Update all 14 `turtles_list` sites in race.py to `racers` per RESEARCH.md Section 2 table.
(5) Replace `TURTLE_NAMES[i] if i < len(TURTLE_NAMES) else f"#{i}"` (race.py lines 181 + 228) with `racers[i]['name']`. The fallback conditional disappears because every racer now has a 'name' field.
(6) Rename remaining `tortuga` occurrences (race.py:247, 248 — inside `show_podium`'s loop) to `racer`.
(7) Add `n` parameter to `draw_start_line(track_name, n)`, `draw_boundary_stones(track_name, n)`, `draw_finish_line(track_name, n)` (race.py lines ~77–132). Forward `n` to the inner `tracks.start_line_segments(track_name, n)` / `tracks.boundary_stones(track_name, n)` / `tracks.finish_line_segments(track_name, n)` calls.
(8) Verify no remaining `turtles_list` or `tortuga` identifiers in race.py.
Note: main.py is NOT touched in this task — it will be temporarily broken (calls `create_turtles` which no longer exists). That is intentional and resolved in Plan 3.1. The pytest suite does not exercise main.py and will stay green.</action>
  <verify>pytest ; python -c "import race; assert hasattr(race, 'create_racers'); assert hasattr(race, 'place_racers_on_track'); assert not hasattr(race, 'create_turtles'); assert not hasattr(race, 'place_turtles_on_track'); print('race.py renames complete')"</verify>
  <done>(1) `pytest` (full) is green — tests pass because they don't exercise main.py. (2) `grep -n "turtles_list\|create_turtles\|place_turtles_on_track\|tortuga" race.py` returns zero matches. (3) race.create_racers, race.place_racers_on_track, race.draw_start_line (with 2 params), race.draw_boundary_stones (with 2 params), race.draw_finish_line (with 2 params) all exist. (4) `TURTLE_NAMES` not imported anywhere in race.py: `grep -n "TURTLE_NAMES" race.py` returns zero matches. (5) SPECIES imported. (6) SUMMARY-2.1.md written to .shipyard/phases/2/results/SUMMARY-2.1.md. (7) Commit made with `git add tests/test_tracks.py race.py .shipyard/phases/2/results/SUMMARY-2.1.md` (file-specific).</done>
</task>

## Verification

Run all of these at the close of the plan:

```powershell
pytest
pytest tests/test_tracks.py -v
```

Repo-wide grep:

```powershell
# pattern="turtles_list|create_turtles|place_turtles_on_track|tortuga", glob="*.py", excluding main.py
# Expect: zero matches in race.py and tests/. main.py still has them (Plan 3.1 fixes).
```

**Note:** `python main.py` is **expected to be broken** at the end of this plan — main.py still calls `create_turtles`. Smoke test is in Plan 3.1.

**Builder reminders (from Phase 1 retrospective):**

1. **Write `.shipyard/phases/2/results/SUMMARY-2.1.md` before returning.** Acceptance criterion in Task 2.
2. **Use file-specific `git add`** — do not `git add .`. Task 2's done criterion specifies the exact files.
