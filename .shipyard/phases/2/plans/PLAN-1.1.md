---
phase: 2-snakes-racer-mode
plan: 1.1
wave: 1
dependencies: []
must_haves:
  - Every public + private function in tracks.py that previously read N_LANES takes an explicit `n` parameter (no default)
  - `from constants import N_LANES` removed from tracks.py
  - `N_LANES = 4` deleted from constants.py
  - tests/test_tracks.py updated so every tracks.* call passes `n=4` explicitly; N_LANES import removed; all assertions referencing N_LANES rewritten with the literal `n` value
  - Full pytest suite green at end of plan (still N=4 only — no new N=3 tests yet)
  - Atomic refactor: cannot be split. Test suite must stay green throughout.
files_touched:
  - tracks.py
  - constants.py
  - tests/test_tracks.py
tdd: false
risk: medium
---

# Plan 1.1 — Hard-refactor tracks.py to take `n` explicitly; delete N_LANES

## Context

Per CONTEXT-2.md Decision 1 (hard refactor, no default arg) and Decision 2 (delete `N_LANES` from constants).

RESEARCH.md Section 1 enumerates all 14 N_LANES usage sites in tracks.py plus one cascade site (`lane_start_pose`) not in the original 14-line count. RESEARCH.md Section 4 enumerates every test_tracks.py site that uses N_LANES (15+ sites) and every tracks.* call that needs an `n` argument appended.

This plan is intentionally atomic: tracks.py changes are useless without the test-suite updates, and deleting N_LANES from constants.py must coincide with removing the last import (`tests/test_tracks.py` line 10 and `tracks.py` line 20). Doing these in separate plans would leave the test suite red between commits.

**No new tests added in this plan.** Geometry coverage stays at N=4 — Wave 2 (Plan 2.1) adds N=3 parametrized cases. End of Wave 1 means: same test surface, refactored internals, N_LANES gone.

## Dependencies

None. This is Wave 1.

## Tasks

<task id="1" files="tracks.py" tdd="false">
  <action>Refactor tracks.py to take `n` explicitly in every function that previously read N_LANES. Specifically: (1) Remove `N_LANES` from the import on line 20 (keep TRACK_PADDING, LANE_SPACING, SPIRAL_STEP, etc.). (2) Change `_lane_coefficient(lane_idx)` → `_lane_coefficient(lane_idx, n)`, replace `N_LANES` on line 57 with `n`. (3) Change `_rectangular_finish_y()` → `_rectangular_finish_y(n)`, replace `N_LANES` on line 115 with `n`. (4) Change `_spiral_pair_cap()` → `_spiral_pair_cap(n)`, replace `N_LANES` on line 181 with `n`. (5) Change `_straight_lane(lane_idx)` → `_straight_lane(lane_idx, n)`, forward `n` to `_lane_coefficient`. (6) Change `_rectangular_lane(lane_idx)` → `_rectangular_lane(lane_idx, n)`, forward `n` to `_lane_coefficient` and `_rectangular_finish_y`. (7) Change `_spiral_lane(lane_idx)` → `_spiral_lane(lane_idx, n)`, replace `N_LANES` on line 165 with `n`, forward `n` to `_lane_coefficient` and `_spiral_pair_cap`. (8) Update `_LANE_BUILDERS` dispatch so callers pass `(lane_idx, n)` to the builder. (9) Change `build_lane_paths(track_name)` → `build_lane_paths(track_name, n)`, update `range(N_LANES)` on line 217 to `range(n)`, update docstring. (10) Change `lane_start_pose(track_name, lane_idx)` → `lane_start_pose(track_name, lane_idx, n)` and forward `n` to the builder. (11) Change `start_line_segments(track_name)` → `start_line_segments(track_name, n)`, update line 268 `range(N_LANES)` → `range(n)`, line 274 `N_LANES - 1` → `n - 1`, forward `n` to `lane_start_pose` calls. (12) Change `_boundary_paths(track_name)` → `_boundary_paths(track_name, n)`, replace `N_LANES` on lines 294, 295, 302, 315 with `n`. (13) Change `boundary_stones(track_name, spacing)` → `boundary_stones(track_name, n, spacing)`, forward `n` to `_boundary_paths`. (14) Change `finish_line_segments(track_name)` → `finish_line_segments(track_name, n)`, replace `N_LANES` on lines 377, 383 with `n`, forward `n` to `build_lane_paths` call on line 386 and `_rectangular_finish_y` call on line 374. Do NOT modify race.py or main.py in this task (they'll break temporarily; fixed in Task 2-style scope below — but per atomicity, do tasks 1+2+3 in one commit).</action>
  <verify>python -c "import tracks; print('ok')"</verify>
  <done>tracks.py imports without error. `grep -n "N_LANES" tracks.py` returns zero matches. All 9 functions listed in RESEARCH.md Section 1 summary table have the new signatures. Module-level imports list no longer contains `N_LANES`.</done>
</task>

<task id="2" files="tests/test_tracks.py" tdd="false">
  <action>Update tests/test_tracks.py to pass `n=4` explicitly to every tracks.* call and remove the N_LANES import. Specifically: (1) Remove `N_LANES` from the import on line 10. Add a local module constant `N = 4` near the top of the file (after imports) to keep the existing assertions readable — assertions like `assert len(paths) == N_LANES` become `assert len(paths) == N`. (2) Append `n=N` (or positional `N`) to every tracks.* call: `build_lane_paths(track, N)`, `lane_start_pose(track, lane_idx, N)`, `start_line_segments(track, N)`, `finish_line_segments(track, N)`, `boundary_stones(track, N)` (signature became `(track, n, spacing)` — pass spacing if test used it; default-arg behavior preserved if test omitted it before), `_boundary_paths(track, N)`. (3) Update the direct `_rectangular_finish_y` import and call (RESEARCH.md G4, test line 81/87 area): `_rectangular_finish_y()` → `_rectangular_finish_y(N)`. (4) Replace every `N_LANES` literal in assertion bodies and formulas with `N` (the new local). Affected test lines per RESEARCH.md Section 4: 47, 107, 139, 165, 166, 214, 223, 268, 287, 316, 328, 343, 344, 355, 361. No new tests added — Wave 2 adds N=3 parametrized cases.</action>
  <verify>pytest tests/test_tracks.py -v</verify>
  <done>All existing test_tracks.py tests pass. `grep -n "N_LANES" tests/test_tracks.py` returns zero matches. Test count is unchanged from pre-Phase-2 baseline.</done>
</task>

<task id="3" files="constants.py, tests/test_tracks.py" tdd="false">
  <action>Delete `N_LANES = 4` from constants.py (currently around line 57 per CONTEXT-2.md). Keep TRACK_PADDING, LANE_SPACING, SPIRAL_STEP, TRACK_PREVIEW_W/H unchanged. If a code comment in constants.py refers to N_LANES, update or remove that comment. Then run the verification commands to confirm zero stale references anywhere. After verification, write the SUMMARY file to disk and commit with a file-specific git add (no broad `git add .`).</action>
  <verify>python -c "import constants; assert not hasattr(constants, 'N_LANES'); print('N_LANES removed')" ; pytest</verify>
  <done>(1) constants.N_LANES does not exist (assertion above passes). (2) `pytest` (full suite) green. (3) `grep -rn "N_LANES" --include="*.py" .` returns zero results across the repo. (4) SUMMARY-1.1.md written to .shipyard/phases/2/results/SUMMARY-1.1.md describing the refactor scope, files touched, and verification output. (5) Commit made with `git add tracks.py constants.py tests/test_tracks.py .shipyard/phases/2/results/SUMMARY-1.1.md` (file-specific, NOT `git add .`).</done>
</task>

## Verification

Run all of these at the close of the plan:

```powershell
pytest
pytest tests/test_tracks.py -v
python -c "import constants; print(hasattr(constants, 'N_LANES'))"   # expect False
```

Then a repo-wide grep:

```powershell
# In Grep tool: pattern="N_LANES", glob="*.py" — expect zero results
```

**Builder reminders (from Phase 1 retrospective):**

1. **Write `.shipyard/phases/2/results/SUMMARY-1.1.md` before returning.** Phase 1 builders skipped this disk write. Acceptance criterion is explicit in Task 3.
2. **Use file-specific `git add`** — do not `git add .`. Task 3's done criterion specifies the exact files.
