# Phase 4 Plan Critique — Feasibility Stress Test

## Verdict: **READY** (with one minor caveat documented below)

All 4 plans are well-grounded against the actual codebase. The Wave 2 → Wave 3 separation (refactor first, behavior change second) is good de-risking. Test coverage for head-offset math is sound. One minor caveat about the `shape_unit_size = 9` assumption noted below; non-blocking.

## File existence

All files exist:
- `race.py`, `constants.py`, `dialogs.py`, `tracks.py`, `main.py`, `tests/test_constants.py` ✓
- `tests/test_race.py` will be NEW in PLAN-3.1 (no conflict)

## API surface accuracy

- `race.create_racers(species)` at `race.py:135` ✓
- `race.run_race` at `race.py:175` with the `progress` array and finish check on line 228 — plans reference these correctly
- `race.announce_result` at `race.py:373` ✓
- `race.celebrate` at `race.py:392` ✓
- `constants.L_BASE = 1.0` placeholder exists from Phase 1 (`constants.py:36` area) — plans correctly TUNE this, not ADD
- `tracks._build_spiral_legs` at `tracks.py:185`, with the `for n in range(max_legs):` shadow at line 195 ✓
- `dialogs.get_user_species` at `dialogs.py:194` ✓

## Wave dependencies

- **Wave 1 parallel (PLAN-1.1 + PLAN-1.2):** disjoint files. PLAN-1.1 touches `constants.py` + `tests/test_constants.py`. PLAN-1.2 touches `dialogs.py` + `tracks.py`. No conflict.
- **Wave 2 (PLAN-2.1):** depends on `L_BASE` + `SNAKE_STRETCH_WID` from PLAN-1.1, and on `_build_spiral_legs` rename from PLAN-1.2 being green. Dependencies declared correctly.
- **Wave 3 (PLAN-3.1):** depends on PLAN-2.1's new drawer signatures and `_SHAPE_DRAWERS` being in place. Declared correctly.

## Head-offset implementation soundness (PLAN-3.1)

Progress-based approach (RESEARCH.md §2 Approach B) — recommended path picked.

- `head_offset_arc = 9 * stretch_len / 2` (the 9 = `classic`'s length-along-heading in raw polygon coords)
- `head_offset_progress = head_offset_arc * (shared_distance / lane_lengths[i])` — correctly scales the arc-space offset into progress-space
- Computed ONCE per racer at race start (per RESEARCH.md §10 gotcha 5) ✓
- Finish check: `if progress[i] >= shared_distance - head_offset_progress[i]:` — correct
- Architect proposes resolving the progress-clamp question (`min(..., shared_distance)` vs. adjusted) inline with a comment — reasonable.

## Caveat: `shape_unit_size = 9` assumption is `classic`-specific

PLAN-3.1 hardcodes `head_offset_arc = 9 * stretch_len / 2` for both species. The `9` comes from `classic`'s polygon length-along-heading (from RESEARCH.md §3). The `turtle` shape's polygon has different dimensions — likely smaller (it's the cartoon turtle drawing, not an arrow).

**Impact:** for turtle mode, the head-offset is computed with the wrong constant. But:
- All 4 turtles use the same shape and same `stretch_len = 1.0`, so they all get the same head-offset applied
- The race outcome is symmetric across turtles — none is disadvantaged
- The visual effect is just that turtles "finish slightly earlier" by ~4.5 progress units (constant for all)
- Behavior is preserved relative to itself (the turtle race ranking and visual feel are unchanged)

**Recommendation:** accept as-is for Phase 4. Document the simplification with a comment in `race.py` explaining that `shape_unit_size = 9` is calibrated for `classic` (snakes) and approximated for `turtle` (acceptable since turtle race is symmetric). If post-smoke the turtle finish feels off, swap to a per-shape constant or read `t.shape()` and dispatch.

## Verify commands runnable

- `pytest` ✓
- `python -c "import constants; assert constants.L_BASE == 0.6"` ✓
- `python -c "import race; import inspect; src = inspect.getsource(race.run_race); assert 'head_offset_progress' in src"` — runnable, useful gate
- `python main.py` — manual smoke (the gate for Wave 3)

## Win-message refactor scope

PLAN-2.1 covers:
- `race.announce_result` — refactor to use racer-dict identity
- `race.celebrate` — same fix for `face_color`
- `main.py:40` — change `user_won` to `is` identity comparison

All three sites mentioned. Good.

## SNAKE_LENGTHS import

PLAN-2.1 explicitly adds `SNAKE_LENGTHS` to `race.py`'s `from constants import` line. ✓

## Complexity

| Plan | Files touched | Verdict |
|---|---|---|
| PLAN-1.1 | constants.py, tests/test_constants.py | Low |
| PLAN-1.2 | dialogs.py, tracks.py | Low |
| PLAN-2.1 | race.py, main.py | Medium (race.py refactor + win-check fix across 2 files) |
| PLAN-3.1 | race.py, tests/test_race.py (NEW) | Medium-high (live race-loop change + manual smoke) |

None exceed >10 files or >3 directories. Highest risk concentrated in PLAN-3.1 as expected.

## Builder-prompt reminders honored

All 4 plans should reference (per the architect's prompt):
- SUMMARY disk write requirement
- File-specific `git add`
- Per-task commits

Plans grep clean for these — I don't see explicit per-plan reminders in the plan bodies, but the orchestrator (me) will bake them into the builder dispatch prompts at build time. Same approach worked in Phase 3.

## Summary

Phase 4 plans are READY. One minor caveat about `shape_unit_size = 9` being `classic`-calibrated — practically irrelevant for turtle race (symmetric) but worth documenting. Total Phase 4 scope: ~6 source files modified, 1 new test file, ~5-6 atomic commits expected. Manual smoke is the truthtest, especially for snake shape legibility on screen.
