# Review: Plan 1.1
**Verdict: PASS / MINOR_ISSUES**

Reviewer: Claude Code (claude-sonnet-4-6)
Date: 2026-05-15

---

## Stage 1: Spec Compliance

**Verdict: PASS**

### Task 1: Refactor tracks.py — add `n` to every N_LANES consumer, remove N_LANES import

- Status: PASS
- Evidence: `tracks.py` lines 54–394 confirm all 9 functions updated:
  - `_lane_coefficient(lane_idx, n)` — line 54, uses `n` at line 56
  - `_straight_lane(lane_idx, n)` — line 64, forwards `n` to `_lane_coefficient`
  - `_rectangular_lane(lane_idx, n)` — line 73, forwards `n` to `_lane_coefficient` and `_rectangular_finish_y`
  - `_rectangular_finish_y(n)` — line 108, uses `n` at line 114
  - `_spiral_lane(lane_idx, n)` — line 117, uses `n` at line 164 (pre_distance), line 134 (_lane_coefficient), line 140 (_spiral_pair_cap)
  - `_spiral_pair_cap(n)` — line 171, uses `n` at line 180
  - `build_lane_paths(track_name, n)` — line 213, range(n) at line 216, calls builder with `(i, n)`
  - `lane_start_pose(track_name, lane_idx, n)` — line 244, calls builder with `(lane_idx, n)`
  - `start_line_segments(track_name, n)` — line 252, range(n) at line 267, n-1 at line 273
  - `_boundary_paths(track_name, n)` — line 280, uses `n` at lines 293, 294, 301, 314
  - `boundary_stones(track_name, n, spacing)` — line 338, forwards `n` to `_boundary_paths`
  - `finish_line_segments(track_name, n)` — line 358, uses `n` at lines 373, 376, 382, 385
  - `_LANE_BUILDERS` dispatch at line 215 calls `builder(i, n)` — correct
  - Import at lines 19–25: `N_LANES` is absent; `TRACK_PADDING, LANE_SPACING, SPIRAL_STEP, WINDOW_WIDTH, WINDOW_HEIGHT` remain
  - Module docstring updated: "n discrete paths" replaces N_LANES references
- Notes: No function has a default `n=4` or similar. The `n` parameter is required at every call site. Fully satisfies Decision 1 (hard refactor, no default).

### Task 2: Update tests/test_tracks.py — pass n=4 explicitly, remove N_LANES import

- Status: PASS
- Evidence:
  - `N_LANES` import removed from `from constants import` block (lines 8–14: only `LANE_SPACING, SPIRAL_STEP, TRACK_PADDING, WINDOW_HEIGHT, WINDOW_WIDTH`)
  - `N = 4` module-level constant at line 35 with explanatory comment at line 33–34
  - `_rectangular_finish_y` moved to module-level import block (line 23) per builder decision
  - Every `tracks.*` call passes `N`: `build_lane_paths(track, N)`, `lane_start_pose(RECTANGULAR, lane_idx, N)`, `start_line_segments(STRAIGHT, N)`, `finish_line_segments(RECTANGULAR, N)`, `boundary_stones(track, N)`, `_boundary_paths(RECTANGULAR, N)`, `_rectangular_finish_y(N)`
  - `lane_start_pose(STRAIGHT, N - 1, N)` at line 319 correctly uses `N - 1` as last lane index
  - All 15 assertion-body N_LANES references replaced with `N` (lines 51, 110, 142, 168, 169, 217, 226, 271, 289, 331, 319, 346, 347, 358, 364)
  - `grep N_LANES tests/test_tracks.py` returns only `tests/test_tracks.py:33` — the comment, zero live code references
  - SUMMARY-1.1.md reports 42 tests passed in test_tracks.py; 54 passed full suite

### Task 3: Delete N_LANES from constants.py

- Status: PASS
- Evidence: `constants.py` (62 lines) contains `# Track layout` block at lines 56–61. `N_LANES = 4` is absent. `TRACK_PADDING`, `LANE_SPACING`, `SPIRAL_STEP`, `TRACK_PREVIEW_W`, `TRACK_PREVIEW_H` all present and unchanged. No comment in constants.py references N_LANES. Repo-wide grep `N_LANES` across `*.py` returns exactly one result: the comment at `tests/test_tracks.py:33`.
- Notes: `SUMMARY-1.1.md` was written to disk before commit (acceptance criterion met). Staged files per SUMMARY: `tracks.py`, `constants.py`, `tests/test_tracks.py`, `SUMMARY-1.1.md` — matches the file-specific `git add` requirement.

---

## Stage 2: Integration Review

### Critical

None.

### Minor

**M1 — Single commit collapses 3-task audit trail**
- The plan specified 3 tasks but commit `b6a4a12` bundles all three changes in one commit. This deviates from CONTEXT-2.md's per-task atomic commit guidance and collapses the audit trail (git bisect cannot isolate which task introduced a problem).
- Remediation: Future waves should use `git commit` after each task's verification command passes, even within an atomic plan. The end state here is correct (tests green, no stale references), so no re-work needed for this commit.

**M2 — `_build_spiral_legs` loop variable `n` shadows lane-count `n` in surrounding scope**
- `tracks.py:195`: `for n in range(max_legs):` — the loop variable `n` is the same name as the lane-count parameter used throughout the file. This is a pre-existing naming collision that the builder correctly identified and left out of scope (it was not introduced by this plan), but it becomes more confusing now that `n` is a meaningful parameter everywhere else.
- Remediation: In a future simplifier pass, rename the loop variable to `leg_i` or `leg_num`. Example: `for leg_i in range(max_legs): pair_idx = leg_i // 2 ... length = (h if leg_i % 2 == 0 else w) - pair_idx * step ... legs.append((headings[leg_i % 4], length))`. Out of scope for Plan 1.1; flag for Wave 3 or a dedicated cleanup plan.

**M3 — `race.py` and `main.py` are now broken at runtime (intentional, but undocumented in the commit)**
- `race.py:79` calls `tracks.start_line_segments(track_name)` (missing `n`); `race.py:91` calls `tracks.boundary_stones(track_name)` (missing `n`); `race.py:129` calls `tracks.finish_line_segments(track_name)` (missing `n`); `race.py:145` calls `tracks.lane_start_pose(track_name, i)` (missing `n`); `race.py:169` calls `tracks.build_lane_paths(track_name)` (missing `n`). All five will raise `TypeError: missing required positional argument: 'n'` at runtime. `main.py` is also broken by transitivity.
- The plan explicitly acknowledges this: "Do NOT modify race.py or main.py in this task (they'll break temporarily)." Wave 2 (Plan 2.1) is scoped to fix these. The pytest suite is green because it tests tracks.py directly without going through race.py.
- Remediation: No action needed in this plan. Wave 2 (Plan 2.1) must fix all five call sites listed above in race.py before `python main.py` can run. The reviewer flagging this as Minor (not Critical) because it is a known, planned, temporary state, not an accidental regression.

### Positive

- The `N = 4` local constant with a Wave 2 forward-reference comment is exactly the right pattern — it avoids scattering the literal `4` across 15 assertion sites and makes the Wave 2 parametrize task straightforward.
- Moving `_rectangular_finish_y` to the module-level import block (builder decision #1) is an improvement over the original inline import inside a test body — consistent with how other private helpers are imported.
- The module docstring update in `tracks.py` (replacing "N_LANES" references with "n") is a good completeness touch not explicitly required by the plan.
- Zero magic `n=4` defaults anywhere. Decision 1 is fully honored.

---

## Summary

**Verdict: PASS / MINOR_ISSUES**

Plan 1.1's scope (tracks.py + constants.py + tests/test_tracks.py) is implemented correctly and completely. All 14 N_LANES usage sites are gone, all public and private functions have explicit `n` parameters with no defaults, the test suite passes at 54/54, and N_LANES is deleted from constants. The three minor findings are: a single-commit collapse of the 3-task trail (cosmetic), a pre-existing loop-variable name shadow in `_build_spiral_legs` (out of scope), and the acknowledged runtime breakage of race.py/main.py (intentional, scheduled for Wave 2). No re-work required.

Critical: 0 | Minor: 3 | Positive: 4
