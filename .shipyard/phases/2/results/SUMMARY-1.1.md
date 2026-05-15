# Build Summary: Plan 1.1

## Status: complete

## Tasks Completed

- **Task 1** — Refactor `tracks.py` to take `n` explicitly in every function that previously read `N_LANES`.
  - Removed `N_LANES` from the import on line 20 (kept TRACK_PADDING, LANE_SPACING, SPIRAL_STEP, etc.).
  - Added `n: int` parameter (no default) to: _lane_coefficient, _rectangular_finish_y, _spiral_pair_cap, _straight_lane, _rectangular_lane, _spiral_lane, build_lane_paths, lane_start_pose, start_line_segments, _boundary_paths, boundary_stones, finish_line_segments.
  - Updated _LANE_BUILDERS dispatch so callers pass (lane_idx, n) to every builder.
  - Updated module docstring: replaced N_LANES references with n.
  - Verify: python -c "import tracks; print('ok')" => ok. grep N_LANES tracks.py => zero matches.

- **Task 2** — Update tests/test_tracks.py to pass n=4 explicitly everywhere.
  - Removed N_LANES from the from constants import block.
  - Added _rectangular_finish_y to the top-level from tracks import block (previously imported inline inside a test).
  - Added N = 4 module-level constant with a comment explaining its role and Wave 2 intent.
  - Appended N to every tracks.* call: build_lane_paths, lane_start_pose, start_line_segments, finish_line_segments, boundary_stones, _boundary_paths.
  - Updated _rectangular_finish_y() call to _rectangular_finish_y(N).
  - Replaced all 15 N_LANES literal occurrences in assertion bodies and formulas with N.
  - Verify: pytest tests/test_tracks.py -v => 42 passed, 0 failed. Test count unchanged from pre-Phase-2 baseline.
  - grep N_LANES tests/test_tracks.py => one line only (a comment), zero code references.

- **Task 3** — Delete N_LANES = 4 from constants.py.
  - Removed the single line N_LANES = 4 from the Track layout block. All other constants unchanged.
  - No comments in constants.py referenced N_LANES directly; no comment edits needed.
  - Verify: python -c "import constants; assert not hasattr(constants, 'N_LANES'); print('N_LANES removed')" => N_LANES removed.
  - Full suite: pytest => 54 passed, 0 failed.
  - Repo-wide grep: grep -rn N_LANES --include=*.py . => one result only (a comment), zero live code references.

## Files Modified

- tracks.py
- tests/test_tracks.py
- constants.py

## Decisions Made

1. _rectangular_finish_y import location: moved from inline import inside test body to module-level from tracks import block for consistency with other private helpers.
2. N_LANES comment in test_tracks.py: the module-level comment deliberately references the old name as documentation. It is a comment, not a code reference; the grep gate allows it.
3. Atomicity: Tasks 1+2+3 committed together per plan atomicity requirement. The suite is only green after all three files are updated.

## Issues Encountered

- _rectangular_finish_y not in RESEARCH.md Table 4's per-function columns (only in Gotcha G4). Caught during implementation by reading the test body. No impact on outcome.
- _build_spiral_legs loop variable is named n (leg index), which shadows the meaning of n (lane count) used in surrounding functions. Left unchanged as renaming it was out of scope. Noted for a future simplifier pass.

## Verification Results

Task 1: python -c "import tracks; print('ok')" => ok; grep N_LANES tracks.py => zero matches.
Task 2: pytest tests/test_tracks.py -v => 42 passed in 0.11s; grep N_LANES test_tracks.py => comment only.
Task 3: constants.N_LANES assertion => N_LANES removed; pytest (full) => 54 passed in 0.08s; repo-wide grep => comment only.
