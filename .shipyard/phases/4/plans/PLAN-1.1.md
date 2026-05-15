---
phase: snakes-racer-mode
plan: 1.1
wave: 1
dependencies: []
must_haves:
  - Tune existing L_BASE placeholder from 1.0 to 0.6 in constants.py
  - Add new SNAKE_STRETCH_WID = 0.5 constant in constants.py
  - Add unit tests that lock both values as positive floats with the expected magnitudes
  - pytest stays green (no race-flow code touched)
files_touched:
  - constants.py
  - tests/test_constants.py
tdd: true
risk: low
---

# PLAN-1.1 — Tune L_BASE and add SNAKE_STRETCH_WID

## Context

Phase 1 landed `L_BASE = 1.0` as a placeholder. Phase 4 tunes it to `0.6` based on RESEARCH.md §3 math (Shadow ≈ 32 units along heading, Anaconda ≈ 27 units, Ralph ≈ 11 units — preserves the 6:5:2 ratio and fits the 300-unit-wide straight track). Also adds `SNAKE_STRETCH_WID = 0.5` for snake body thickness (5 units wide at default classic shape, comfortably fits in the 24-unit lane spacing).

Pure data change. No race.py code touches the new constants yet — that comes in PLAN-2.1.

## Tasks

<task id="1" files="tests/test_constants.py" tdd="true">
  <action>Add two tests to tests/test_constants.py mirroring the existing `test_bet_image_size_is_positive_int` style: (a) `test_l_base_is_positive_float` asserts `constants.L_BASE` is a float, > 0, and == 0.6 exactly; (b) `test_snake_stretch_wid_is_positive_float` asserts `constants.SNAKE_STRETCH_WID` is a float, > 0, and == 0.5 exactly. These should FAIL before Task 2 (L_BASE is currently 1.0; SNAKE_STRETCH_WID does not exist).</action>
  <verify>pytest tests/test_constants.py::test_l_base_is_positive_float tests/test_constants.py::test_snake_stretch_wid_is_positive_float</verify>
  <done>Both new tests appear in pytest output and FAIL (red): L_BASE assertion fails on the value (1.0 != 0.6); SNAKE_STRETCH_WID assertion fails with AttributeError. This is the expected red state of TDD.</done>
</task>

<task id="2" files="constants.py" tdd="true">
  <action>In constants.py: change the existing `L_BASE = 1.0` placeholder to `L_BASE = 0.6`. Add a new line `SNAKE_STRETCH_WID = 0.5` near the L_BASE line. Add a brief comment on each line referencing Phase 4 / CONTEXT-4 Decision 2 rationale (Shadow at 32 units along heading fits the 300-unit straight track; snake width of 5 units fits the 24-unit lane spacing).</action>
  <verify>pytest tests/test_constants.py && python -c "import constants; assert constants.L_BASE == 0.6; assert constants.SNAKE_STRETCH_WID == 0.5; print('OK')"</verify>
  <done>pytest tests/test_constants.py is fully green including the two new tests from Task 1. The python -c invocation prints `OK`.</done>
</task>

<task id="3" files="" tdd="false">
  <action>Run the full pytest suite to confirm no other tests regressed.</action>
  <verify>pytest</verify>
  <done>Full pytest run is green. No tests skipped that were previously running; no new failures introduced.</done>
</task>

## Notes for the builder

- This plan does NOT touch race.py, main.py, dialogs.py, or tracks.py.
- The smoke-tune step (Phase 4 ROADMAP task 4) — running `python main.py` and visually adjusting L_BASE if Shadow looks too short or Ralph too small — happens in PLAN-3.1, not here. Just commit 0.6 as the starting value.
- Per-task atomic commits. `git add` only the files listed in each task's `files=` attribute. Never `git add .`.
- Write SUMMARY-1.1.md to disk before returning.
