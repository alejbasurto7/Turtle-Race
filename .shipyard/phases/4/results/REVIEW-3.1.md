---
plan: PLAN-3.1
wave: 3
phase: snakes-racer-mode
reviewer: claude-sonnet-4-6
date: 2026-05-15
verdict: APPROVE
stage1: PASS
stage2: PASS
---

# REVIEW-3.1 — Head-position finish detection + manual smoke gate

## Pre-Check: Prior Findings

- REVIEW-1.1, REVIEW-1.2, REVIEW-2.1 all returned PASS verdicts with zero Critical findings.
- REVIEW-2.1 flagged one Minor: unused `won` parameter in `celebrate`. That parameter is still present (`race.py:478`) and `main.py:42` still passes it. No regression — the carry-over is cosmetic and was explicitly flagged as non-blocking.
- No `.shipyard/ISSUES.md` file exists — no prior ISSUES carry-over required.
- No recurring Critical pattern across waves.

---

## Stage 1: Spec Compliance

**Verdict: PASS**

### Task 1: tests/test_race.py — pure-math unit tests

- Status: PASS
- Evidence: `tests/test_race.py` exists. File contains zero imports from `race.py`, `turtle`, `tkinter`, or any Tk-dependent module. A standalone `_head_offset_progress(stretch_len, shared_distance, lane_length)` helper reproduces the formula verbatim at lines 23-32.
- Five test functions confirmed at lines 39, 53, 67, 85, 96:
  - `test_head_offset_progress_ratio_equal` — lane_length == shared_distance (ratio 1.0), asserts `result == head_offset_arc` exactly.
  - `test_head_offset_progress_ratio_less_than_one` — lane_length = 2x shared_distance (ratio 0.5), asserts `result == 8.1` with float epsilon.
  - `test_head_offset_progress_ratio_greater_than_one` — lane_length = 0.5x shared_distance (ratio 2.0), asserts `result == 32.4` with float epsilon.
  - `test_head_offset_arc_shadow` — `stretch_len = 0.6 * 6 = 3.6`, `arc = 9 * 3.6 / 2 = 16.2`. Asserts `abs(arc - 16.2) < 1e-9`.
  - `test_head_offset_arc_ralph` — `stretch_len = 0.6 * 2 = 1.2`, `arc = 9 * 1.2 / 2 = 5.4`. Asserts `abs(arc - 5.4) < 1e-9`.
- Turtle-species note is a comment (line 107-109), not an assertion — matches plan spec ("no assertion required; smoke handles it").
- SUMMARY claims 84/84 pass (79 prior + 5 new). The prior 79 total includes parametrize-expanded cases in `test_tracks.py` (39 function defs there expand to ~64 test cases). Arithmetic is consistent.
- Notes: All three lane-length ratio scenarios covered. Shadow and Ralph concrete plug-ins match `constants.SNAKE_LENGTHS = [6, 2, 5]` and `L_BASE = 0.6` exactly. No Tk dependency introduced.

### Task 2: race.py — head_offset_progress wired into run_race

- Status: PASS
- Evidence:
  - `_SHAPE_UNIT_SIZE = 9` defined at `race.py:264`.
  - `head_offset_progress = []` initialized at `race.py:265`.
  - Pre-loop computation at `race.py:266-269`: iterates `range(len(racers))`, reads `shapesize()[1]` (index 1 = stretch_len per turtle API), computes `head_offset_arc`, appends `head_offset_arc * (shared_distance / lane_lengths[i])`.
  - Array is fully built before `while not all(done):` at `race.py:291` — computed exactly once per race.
  - Finish check at `race.py:310`: `if progress[i] >= shared_distance - head_offset_progress[i]:` — correct adjusted threshold.
  - Loop guard at `race.py:296`: `if coast_remaining[i] is None:` — uses `coast_remaining` sentinel (not `progress < shared_distance`), preventing racing-branch re-entry after the new lower finish threshold fires.
  - Clamp at `race.py:300`: `min(progress[i] + step, shared_distance)` — stays at `shared_distance` (plan's simpler option).
  - Comment block at `race.py:240-263` explains universality per CONTEXT-4 Decision 3, documents the `shape_unit_size = 9` calibration caveat per CRITIQUE.md, and justifies the clamp/guard design choice.
- Notes: The inline comment block is thorough and directly addresses the CRITIQUE.md caveat about `_SHAPE_UNIT_SIZE = 9` being `classic`-calibrated. The loop-guard change from `progress < shared_distance` to `coast_remaining[i] is None` is the correct fix — without it a racer could re-enter the racing branch on the tick after finish fires (since `progress[i]` is clamped at `shared_distance`, not at the lower finish threshold, so the old guard would pass again). Using the `coast_remaining` sentinel is clean and correct.
- Verification command `python -c "import race; import inspect; src = inspect.getsource(race.run_race); assert 'head_offset_progress' in src, 'head_offset_progress not wired'; print('OK')"` will pass — `head_offset_progress` appears 6 times in `run_race` source.

### Task 3: Manual smoke gate

- Status: PENDING_HUMAN_VERIFICATION (expected)
- Evidence: SUMMARY-3.1 documents the full smoke matrix as a checklist with all 6 track/species combinations and the alternating-round test. The `PENDING_HUMAN_VERIFICATION` status matches the precedent set in Phase 2 and Phase 3, where live-window verification is deferred to the human owner. Decision 1 gate (stretched-classic vs. polygon fallback) is documented with clear escalation criteria if needed during smoke.
- Notes: No polygon-fallback escalation was triggered — SUMMARY indicates stretched-classic shipped as-is (no new `register_shape` call found in race.py). This is consistent with the "ship as-is if shape reads OK" path in the plan.

---

## Stage 2: Code Quality

### Critical

None.

### Important

- **`constants.py:31` — positional comment is wrong about the ratio ordering** (pre-existing, not introduced this wave). The comment reads `# 6:5:2 ratio is Shadow:Anaconda:Ralph by value` but `SNAKE_LENGTHS = [6, 2, 5]` maps to `SNAKE_NAMES = ["Shadow", "Ralph", "Anaconda"]`, making the actual values Shadow=6, Ralph=2, Anaconda=5. The comment implies the array order is `[Shadow, Anaconda, Ralph]` by name, but the array order is `[Shadow, Ralph, Anaconda]`. The value 5 belongs to Anaconda (index 2), not Ralph (index 1). A developer reading only the comment would expect `Ralph=5, Anaconda=2` — the reverse of reality.
  - Remediation: Change comment to `# 6:5:2 ratio: Shadow (index 0) = 6, Ralph (index 1) = 2, Anaconda (index 2) = 5` — or reorder to state `# Shadow:Ralph:Anaconda = 6:2:5` matching the actual array order.
  - Note: `test_constants.py:49-50` has `assert named == {"Shadow": 6, "Ralph": 2, "Anaconda": 5}` which is the ground truth and guards against regression. The comment is purely a readability hazard.

### Suggestions

- **Commit prefix style deviation:** Commits `95f42d8` and `f810a69` use `test(race):` and `feat(race):` prefixes. Earlier Phase 4 commits used `shipyard(phase-4):`. Cosmetic inconsistency — does not affect functionality but breaks the project's commit-log convention for Phase 4.
  - Remediation: Use `shipyard(phase-4):` prefix for all Phase 4 wave commits in future waves, or establish `feat(race):` as the new standard and apply consistently going forward.

- **`_SHAPE_UNIT_SIZE` is a function-local constant** at `race.py:264`, defined inside `run_race`. If a future phase adds another function that needs the same constant (e.g., a pre-race preview or a shape-calibration helper), it will be duplicated.
  - Remediation: Lift `_SHAPE_UNIT_SIZE = 9` to module level alongside the other module-level constants (`STONE_COLOR`, `FINISH_CHECKER_SIZE`, etc.). No behavior change; purely organizational.

- **`test_race.py` could document Anaconda** alongside Shadow and Ralph. The concrete plug-in tests cover Shadow (stretch_len=3.6) and Ralph (stretch_len=1.2) but not Anaconda (stretch_len=0.6*5=3.0, arc=13.5). Given that Anaconda is the middle snake and has a distinct length, a third assert would complete the trio and make the test file a full species reference.
  - Remediation: Add `test_head_offset_arc_anaconda` asserting `abs(9 * 3.0 / 2 - 13.5) < 1e-9`.

---

## Carry-over to Phase 5

The following items were observed but are explicitly out of Phase 4 scope:

1. **Spiral 3-lane entry geometry tuning** — Per CONTEXT-4 Decision 7, deferred to Phase 5. Smoke may surface visual overlap or racer crowding at the spiral start; document those observations in smoke notes for the Phase 5 architect.

2. **`L_BASE` / `SNAKE_STRETCH_WID` empirical re-tuning** — If smoke reveals snakes look too short (Shadow too stubby) or too thick for the 24-unit `LANE_SPACING`, the constants at `constants.py:37-40` are the tuning levers. CRITIQUE.md accepts the current values as starting points; smoke is the gate.

3. **Polygon-fallback escalation decision** — If stretched-classic does not read as snake-shaped at race scale during smoke, the `# PHASE-4-PLACEHOLDER` comment at `race.py:156-160` documents the escalation path (`register_shape` at startup, switch `t.shape("classic")` to `t.shape("snake_<name>")`). If triggered, this becomes a Phase 5 item to complete and test.

4. **`_SHAPE_UNIT_SIZE` per-shape dispatch** — The CRITIQUE.md caveat notes that `9` is calibrated for `classic` (snakes) and is approximate for the `turtle` shape. If post-smoke the turtle finish threshold feels visually wrong, the fix is to dispatch by `t.shape()` return value: `_SHAPE_UNIT_SIZE = {"classic": 9, "turtle": 6}.get(t.shape(), 9)`. Deferred because all 4 turtles are symmetric.

5. **Unused `won` parameter in `celebrate`** — Carry-over from REVIEW-2.1 Minor finding. `race.py:478` accepts `won` and uses it for the smile/frown branch, so it is not dead in the function body (reviewing again: `celebrate` does use `won` at `race.py:517-524` for the mouth drawing). REVIEW-2.1's finding that `won` was "dead" was partially incorrect — `won` IS used for the mouth shape. The parameter is correct to keep. This carry-over can be closed: REVIEW-2.1's finding is retracted on closer inspection of the Phase 4 implementation.

---

## Summary

**Verdict: APPROVE**

Both commits implement the plan correctly and completely. The `head_offset_progress` parallel array is computed once before the race loop using the correct `shapesize()[1]` API, the finish check subtracts the per-racer offset, and the loop-guard change to `coast_remaining[i] is None` is the correct fix for the re-entry hazard introduced by the lower finish threshold. The test file is clean, Tk-free, and covers all three ratio scenarios plus the two species-specific plug-in values. Task 3 is pending human verification, consistent with the Phase 2/3 smoke-gate pattern.

Critical: 0 | Important: 1 (pre-existing comment inconsistency in constants.py) | Suggestions: 3
