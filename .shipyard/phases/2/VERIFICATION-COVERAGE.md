# Plan Coverage Verification — Phase 2
**Phase:** 2 - Generalize race.py to N racers (turtle-only parity)
**Date:** 2026-05-15
**Mode:** Plan review (pre-execution)
**Verdict:** PASS — all three plans collectively cover Phase 2 requirements and success criteria.

---

## Phase 2 Roadmap Requirements

From `.shipyard/ROADMAP.md` lines 39-66, Phase 2 must deliver:

| Requirement | Coverage | Evidence |
|---|---|---|
| `tracks.py` hard refactor: every function takes `n` explicitly, no default | COVERED | PLAN-1.1 Task 1 refactors all 9 functions per RESEARCH.md Section 1 summary table. Task specifies removal of `N_LANES` import, `(lane_idx, n)` signatures for builders, and N-parameterization of all 14 line-number references. RESEARCH.md Section 1 is comprehensive (lines 18-96). |
| `N_LANES = 4` removed entirely from `constants.py` | COVERED | PLAN-1.1 Task 3 explicitly "Delete `N_LANES = 4` from constants.py (currently around line 57)" with verification command `python -c "import constants; assert not hasattr(constants, 'N_LANES')"`. Done criterion includes "constants.N_LANES does not exist." Grep verification for zero `N_LANES` matches in repo. |
| `tests/test_tracks.py` extended to cover both N=3 and N=4 | COVERED | PLAN-2.1 Task 1 adds parametrized geometry tests per RESEARCH.md Section 7. Specifically: 5 new test functions (`test_n_start_positions_are_distinct`, `test_n_start_positions_within_canvas_bounds`, `test_straight_lanes_n_spaced_by_lane_spacing`, `test_spiral_n_lanes_all_end_at_origin`, `test_finish_line_segment_count`) covering 6 `(track, N)` pairs (straight/rectangular/spiral × 3/4). Parametrize approach chosen (Approach A) per RESEARCH.md Section 7 recommendation. |
| `tortuga` → `racer` rename in `race.py` | COVERED | PLAN-2.1 Task 2 (action, point 6) "Rename remaining `tortuga` occurrences (race.py:247, 248 — inside `show_podium`'s loop) to `racer`" plus point 3 in the loop-variable rename within `place_racers_on_track`. CONTEXT-2.md Decision 4 explicitly calls this out. |
| `turtles_list` → `racers` everywhere | COVERED | PLAN-2.1 Task 2 (action, point 4) renames all 14 sites per RESEARCH.md Section 2 table (lines 103-119). Done criterion includes `grep -n "turtles_list\|..."` returns zero matches in race.py. |
| `create_turtles(color_list)` → `create_racers(species)` reading SPECIES dict | COVERED | PLAN-2.1 Task 2 (action, point 2) fully specifies: "reads `SPECIES[species]["names"]` and `["colors"]`; iterates `zip(names, colors)`; appends `{'name': name, 'color': color, 'o': Turtle(shape="turtle")}`" — exact implementation from CONTEXT-2.md Decision 7. |
| `place_turtles_on_track` → `place_racers_on_track` | COVERED | PLAN-2.1 Task 2 (action, point 3) renames function and derives `n = len(racers)` internally. |
| Racer dicts include `name` field | COVERED | PLAN-2.1 Task 2 (action, point 2) explicitly appends `'name': name` to each racer dict. CONTEXT-2.md Decision 7 mandates this: "extend dict with `'name'`... Phase 4 will use it". |
| `main.py` call-site updates with hardcoded `species="turtles"` | COVERED | PLAN-3.1 Task 1 (action, points 1-10) updates all 7 call sites per RESEARCH.md Section 3 table. Specifically: `create_racers("turtles")`, `place_racers_on_track(racers, track_name)`, `draw_start_line/finish_line/boundary_stones` with `len(racers)` parameter, `run_race(racers, ...)`, and remaining `turtles_list` → `racers`. |
| `run_race`'s `shared_distance` N-safety | COVERED | PLAN-2.1 Task 2 (action, point 4) includes: "`shared_distance` formula is N-safe per RESEARCH.md Section 2 (`avg_lane_length = sum / len(lane_paths)`) — no formula change needed." RESEARCH.md Section 2 (lines 160-173) provides full analysis: "SAFE. `avg_lane_length` is dynamically computed from actual lane set — no hardcoded 4 appears here." Formula is algebraically N-safe. |
| End-state: turtle race still works with zero visual regression | COVERED | PLAN-3.1 Task 2 (action, point d) "Manual smoke: launch `python main.py`, pick the **straight** track, run a race to completion... Repeat for **rectangular** and **spiral** tracks. Compare each visually against pre-Phase-2 `master` baseline... Any visual difference is a regression and must be investigated before declaring Phase 2 complete." Done criterion: "Manual smoke on all 3 tracks (straight, rectangular, spiral) completed by the human operator with zero visual regression confirmed." This is the primary acceptance gate per CONTEXT-2.md Decision 6. |

---

## Plan-by-Plan Must-Have Coverage

### PLAN-1.1 — Hard-refactor tracks.py to take `n` explicitly; delete N_LANES

| Must-Have | Satisfied | Evidence |
|---|---|---|
| Every public + private function in tracks.py that previously read N_LANES takes an explicit `n` parameter (no default) | YES | Task 1 action enumerates all 9 functions (lines 39-55 of plan). Task specifies: change `_lane_coefficient(lane_idx)` → `_lane_coefficient(lane_idx, n)`, same for `_rectangular_finish_y`, `_spiral_pair_cap`, all 3 lane builders, `build_lane_paths`, `lane_start_pose`, `start_line_segments`, `_boundary_paths`, `boundary_stones`, `finish_line_segments`. No defaults mentioned. |
| `from constants import N_LANES` removed from tracks.py | YES | Task 1 action point (1): "Remove `N_LANES` from the import on line 20 (keep TRACK_PADDING, LANE_SPACING, SPIRAL_STEP, etc.)". Task verify: `` grep -n "N_LANES" tracks.py` returns zero matches". |
| `N_LANES = 4` deleted from constants.py | YES | Task 3 action: "Delete `N_LANES = 4` from constants.py (currently around line 57 per CONTEXT-2.md)". Task 3 verify: `python -c "import constants; assert not hasattr(constants, 'N_LANES')"` must pass. |
| tests/test_tracks.py updated so every tracks.* call passes `n=4` explicitly; N_LANES import removed; all assertions referencing N_LANES rewritten | YES | Task 2 action points (1)-(4) fully specify: remove N_LANES import, add local `N = 4` constant, append `n=N` to every tracks.* call, update `_rectangular_finish_y` call signature. Task specifies 15+ sites in RESEARCH.md Section 4. Task 2 verify: `pytest tests/test_tracks.py -v` passes, `grep -n "N_LANES" tests/test_tracks.py` returns zero matches. |
| Full pytest suite green at end of plan (still N=4 only — no new N=3 tests yet) | YES | Task 3 verify includes `pytest` command — "Full pytest green at end of plan... All green." Done criterion: "(2) `pytest` (full suite) green." |
| Atomic refactor: cannot be split. Test suite must stay green throughout. | IMPLICIT | Plan context states "This plan is intentionally atomic: tracks.py changes are useless without the test-suite updates, and deleting N_LANES from constants.py must coincide with removing the last import... Doing these in separate plans would leave the test suite red between commits." All 3 tasks are merged in one commit per Task 3 done criterion: "`git add tracks.py constants.py tests/test_tracks.py .shipyard/phases/2/results/SUMMARY-1.1.md`". |

---

### PLAN-2.1 — Add N=3 geometry tests + generalize race.py (TDD)

| Must-Have | Satisfied | Evidence |
|---|---|---|
| Parametrized N=3 + N=4 geometry tests added to tests/test_tracks.py (Approach A — pytest.mark.parametrize, per RESEARCH.md Section 7 recommendation) | YES | Task 1 action specifies 5 parametrized test functions with 6 (track, n) pairs: `test_n_start_positions_are_distinct`, `test_n_start_positions_within_canvas_bounds`, `test_straight_lanes_n_spaced_by_lane_spacing`, `test_spiral_n_lanes_all_end_at_origin`, `test_finish_line_segment_count`. Task includes module-level comment: "Note: parametrize is used below for N=3/N=4 coverage; the existing single-track parametrize precedent is at lines 44, 333, 400, 409." Approach A rationale provided in plan context. |
| race.py refactored: turtles_list → racers (14 sites), tortuga → racer (4 sites) | YES | Task 2 action points (4), (6), and context reference RESEARCH.md Section 2 table (lines 103-119) which lists all 14 `turtles_list` sites and their replacements. Point 6: "Rename remaining `tortuga` occurrences (race.py:247, 248)" plus the loop variable in point 3. Done criterion: `` grep -n "turtles_list\|...\|tortuga" race.py` returns zero matches". |
| create_turtles(color_list) → create_racers(species: str) — reads SPECIES[species]["names"] and ["colors"]; returns [{'o': ..., 'color': ..., 'name': ...}] | YES | Task 2 action point (2) specifies full implementation: "reads `SPECIES[species]["names"]` and `["colors"]`; iterates `zip(names, colors)`; appends `{'name': name, 'color': color, 'o': Turtle(shape="turtle")}`". Matches CONTEXT-2.md Decision 7 requirement exactly. |
| place_turtles_on_track → place_racers_on_track(racers, track_name) — derives n = len(racers) internally | YES | Task 2 action point (3): "Rename `place_turtles_on_track(turtles_list, track_name)` → `place_racers_on_track(racers, track_name)`. Inside the function: rename loop variable `tortuga` → `racer`; compute `n = len(racers)` at the top; pass `n` to the `tracks.lane_start_pose(track_name, i, n)` call". |
| draw_start_line / draw_boundary_stones / draw_finish_line take an explicit `n` parameter | YES | Task 2 action point (7): "Add `n` parameter to `draw_start_line(track_name, n)`, `draw_boundary_stones(track_name, n)`, `draw_finish_line(track_name, n)` (race.py lines ~77–132). Forward `n` to the inner `tracks.start_line_segments(track_name, n)` / `tracks.boundary_stones(track_name, n)` / `tracks.finish_line_segments(track_name, n)` calls." |
| Every tracks.* call from race.py passes n | YES | Task 2 action point (4) includes: "Update the `tracks.build_lane_paths(track_name)` call on line 169 to `tracks.build_lane_paths(track_name, n)`" and the context states "Compute `n = len(racers)` once at the top" of `run_race`. Point (7) specifies forwarding `n` to all draw_* helpers. |
| TURTLE_NAMES import dropped from race.py; logging uses racer['name'] instead | YES | Task 2 action point (5): "Replace `TURTLE_NAMES[i] if i < len(TURTLE_NAMES) else f"#{i}"` (race.py lines 181 + 228) with `racers[i]['name']`. The fallback conditional disappears because every racer now has a 'name' field." Point (1): "Update imports: drop `TURTLE_NAMES` (currently imported on race.py line 9 area)". |
| SPECIES imported in race.py | YES | Task 2 action point (1): "add `SPECIES`" to imports. Point (2) implementation reads SPECIES. Done criterion: "(5) SPECIES imported." |
| Full pytest green at end of plan, including new N=3 + N=4 parametrized cases | YES | Task 2 verify: `pytest ; python -c "import race; assert hasattr(race, 'create_racers')..."`. Done criterion: "(1) `pytest` (full) is green — tests pass because they don't exercise main.py." Context notes: "The pytest suite does not exercise main.py and will stay green." |

---

### PLAN-3.1 — Wire main.py to the new race.py API; turtle parity smoke

| Must-Have | Satisfied | Evidence |
|---|---|---|
| main.py call sites updated to use create_racers("turtles"), racers, place_racers_on_track, etc. per RESEARCH.md Section 3 table | YES | Task 1 action points (1)-(9) map exactly to RESEARCH.md Section 3 table (lines 197-209): replace `create_turtles(TURTLE_COLORS)` → `create_racers("turtles")`, `place_turtles_on_track(turtles_list, ...)` → `place_racers_on_track(racers, ...)`, `draw_start_line(track_name)` → `draw_start_line(track_name, len(racers))`, similar for `draw_finish_line`, `draw_boundary_stones`, `run_race`, and remaining `turtles_list` → `racers`. |
| draw_boundary_stones (and draw_start_line / draw_finish_line) calls reordered so create_racers runs first | YES | Task 1 action point (2): "Reorder the round-loop setup so create_racers runs before any of the draw_* calls that now need `n`. New order: `create_racers("turtles")` → `draw_boundary_stones(track_name, len(racers))` → ...". Task context (lines 31-32) cites "RESEARCH.md G7: Currently main.py calls `draw_boundary_stones(track_name)` on line 29, **before** `create_turtles` on line 30... the reorder is mechanical but must be explicit." |
| TURTLE_COLORS import dropped from main.py (no replacement needed — create_racers reads SPECIES internally) | YES | Task 1 action point (1): "Remove `from constants import TURTLE_COLORS` on line 11 (RESEARCH.md Section 3, line 11). No replacement import needed in main.py — `create_racers("turtles")` reads SPECIES internally." |
| Final pytest green | YES | Task 2 action includes `pytest` verification and done criterion: "(1) `pytest` (full) green." |
| Manual smoke: python main.py runs on all 3 tracks (straight, rectangular, spiral) with 4 turtles — zero visual regression vs. master baseline | YES | Task 2 action point (d) specifies: "Manual smoke: launch `python main.py`, pick the **straight** track, run a race to completion. Confirm 4 turtles, podium shows 3 winners, play-again works. Repeat for **rectangular** and **spiral** tracks. Compare each visually against pre-Phase-2 `master` baseline... Any visual difference is a regression and must be investigated before declaring Phase 2 complete." Done criterion: "(4) Manual smoke on all 3 tracks (straight, rectangular, spiral) completed by the human operator with zero visual regression confirmed." This is explicitly the "primary acceptance gate" per plan context. |
| Repo-wide grep for turtles_list / create_turtles / place_turtles_on_track / tortuga / N_LANES returns zero results across all *.py files | YES | Task 2 verification includes grep command: pattern=`N_LANES\|turtles_list\|create_turtles\|place_turtles_on_track\|tortuga`, glob=`*.py` — "must return zero results across the entire repo". Done criterion: "(3) Repo-wide grep for the legacy identifiers returns zero results in all *.py files." |

---

## Task Count & Complexity

| Plan | Task Count | Risk | Complexity | Status |
|---|---|---|---|---|
| PLAN-1.1 | 3 tasks | MEDIUM | High (tracks.py is 396 lines; 14 sites + cascade site; atomic constraint) | All tasks explicit and actionable |
| PLAN-2.1 | 2 tasks | MEDIUM | High (race.py is 424 lines; 14 identifier sites + function refactor + TDD step) | Both tasks explicit; TDD order clear (tests first) |
| PLAN-3.1 | 2 tasks | LOW | Low (main.py is 51 lines; 10 call-site renames; reorder is mechanical) | Both tasks explicit; small surface area |
| **Total** | **7 tasks** | — | — | All pass task-count limit (≤3 per plan). |

---

## Wave Dependency & Ordering

```
Wave 1 (Plan 1.1):   tracks.py refactor + constants.py delete + test updates
          ↓ (blocks Wave 2: need N-parameterized tracks.py)
Wave 2 (Plan 2.1):   N=3/N=4 geometry tests + race.py refactor
          ↓ (blocks Wave 3: race.py must have create_racers before main.py can use it)
Wave 3 (Plan 3.1):   main.py wire-up + turtle parity smoke
```

**Verdict:** Dependency ordering is correct. PLAN-1.1 must precede PLAN-2.1 (tracks.py must accept `n` before tests can pass `n`). PLAN-2.1 must precede PLAN-3.1 (`create_racers` must exist before main.py calls it). No circular dependencies. No cross-wave conflicts.

---

## File Conflicts & Sequencing

| File | Plan 1.1 | Plan 2.1 | Plan 3.1 | Conflict? |
|---|---|---|---|---|
| `tracks.py` | Full refactor (signature changes + import removal) | — | — | NO (1.1 only) |
| `constants.py` | Delete `N_LANES` | — | — | NO (1.1 only) |
| `tests/test_tracks.py` | Update existing tests to pass `n=4` | Add N=3/N=4 parametrized tests | — | NO (sequential: 1.1 updates existing, 2.1 adds new; no overlap) |
| `race.py` | — | Full refactor (renames + generalization) | — | NO (2.1 only) |
| `main.py` | — | — | Update call sites | NO (3.1 only) |
| Dialogs, other modules | — | — | — | NO (untouched through Phase 2) |

**Verdict:** File sequencing is sequential by wave. No conflicts. Each plan touches a distinct set of files (except test_tracks.py, which 1.1 and 2.1 both touch but at different parts — existing test updates vs. new test additions).

---

## Acceptance Criteria — Testability

| Plan | Task | Acceptance Criterion | Testable? | Evidence |
|---|---|---|---|---|
| 1.1 | 1 | `grep -n "N_LANES" tracks.py` returns zero | YES (Bash command) | Explicit in task verify |
| 1.1 | 2 | `pytest tests/test_tracks.py -v` green | YES (test command) | Explicit in task verify |
| 1.1 | 3 | `python -c "import constants; assert not hasattr(constants, 'N_LANES')"` passes | YES (Python command) | Explicit in task verify |
| 2.1 | 1 | `pytest tests/test_tracks.py -v -k "n_start_positions or spiral_n_lanes..."` green | YES (test command) | Explicit in task verify |
| 2.1 | 2 | `python -c "import race; assert hasattr(race, 'create_racers')..."` passes | YES (Python command) | Explicit in task verify |
| 3.1 | 1 | `python -c "import ast; ast.parse(open('main.py').read())"` succeeds (syntax check) | YES (Python command) | Explicit in task verify |
| 3.1 | 2 | `pytest` green | YES (test command) | Explicit in task verify |
| 3.1 | 2 | Manual smoke: `python main.py` on all 3 tracks with zero visual regression | MANUAL (human) | Explicit in task action (point d) and done criterion |

**Verdict:** All acceptance criteria are concrete and objective. No vague phrases like "code is clean" or "check that it works". Manual smoke is explicitly flagged as **human-operator** task (not automated) — plan context clarifies "If the builder is non-interactive, this step is delegated to the human reviewer and explicitly called out in SUMMARY-3.1.md as 'MANUAL SMOKE PENDING'".

---

## CONTEXT-2.md Decision Fulfillment

| Decision | Required | Plans Addressing | Verification |
|---|---|---|---|
| Decision 1: Hard refactor tracks.py, no default `n` arg | Every function takes `n` explicitly | PLAN-1.1 Task 1 | Action enumerates all 9 functions; no defaults mentioned |
| Decision 2: Delete `N_LANES` from constants.py | `N_LANES` removed, verified by grep | PLAN-1.1 Task 3 | Done criterion: constant does not exist; repo-wide grep confirms zero matches |
| Decision 3: Extend test_tracks.py in-place, parametrize for N=3 and N=4 | Add parametrized tests (Approach A) | PLAN-2.1 Task 1 | Action specifies 5 test functions with parametrize decorator; module comment added per Decision 3 spec |
| Decision 4: `tortuga` → `racer` rename | Rename in race.py | PLAN-2.1 Task 2 (points 3, 6) | Action specifies all 4 sites; done criterion confirms zero matches |
| Decision 5: Identifier renames (`turtles_list`, `create_turtles`, `place_turtles_on_track`) | All renamed in race.py + main.py | PLAN-2.1 Task 2 + PLAN-3.1 Task 1 | race.py done criterion confirms zero matches; main.py action specifies all 7 call-site updates |
| Decision 6: Turtle race still works with zero visual regression | Manual smoke on all 3 tracks | PLAN-3.1 Task 2 | Action point (d) specifies manual verification; done criterion: "Human operator with zero visual regression confirmed" |
| Decision 7: `create_racers` returns `[{'o': ..., 'color': ..., 'name': ...}]` | Dict extended with 'name' field | PLAN-2.1 Task 2 point (2) | Action specifies: "appends `{'name': name, 'color': color, 'o': Turtle(...)}`" |

**Verdict:** All 7 context decisions are addressed by at least one plan task. No decisions are unaddressed.

---

## ROADMAP Deliverable Fulfillment

| Deliverable | Addressed by | Task | Details |
|---|---|---|---|
| `race.py` refactor: `create_racers(species)` | PLAN-2.1 | Task 2 | Point (2): full implementation specified; reads SPECIES[species]["names"] and ["colors"] |
| `race.py` refactor: `place_racers_on_track(racers, track_name)` parameterized by N | PLAN-2.1 | Task 2 | Point (3): derives n = len(racers); passes to tracks.lane_start_pose |
| `race.py` refactor: `draw_start_line(track_name, n)` + `draw_boundary_stones(track_name, n)` + `draw_finish_line(track_name, n)` parameterized by N | PLAN-2.1 | Task 2 | Point (7): all 3 functions get `n` parameter; forward to tracks.* calls |
| `race.py` refactor: identifier rename `turtles_list` → `racers` everywhere | PLAN-2.1 | Task 2 | Point (4): 14 sites per RESEARCH.md table; done criterion confirms zero matches |
| `main.py` call-site renames | PLAN-3.1 | Task 1 | Points (1)-(9): all 7 call sites updated per RESEARCH.md Section 3 table |
| `main.py`: species hardcoded to `"turtles"` for Phase 2 | PLAN-3.1 | Task 1 | Point (3): `race.create_racers("turtles")` is literal call; Phase 3 will generalize |
| `tests/test_tracks.py`: geometry tests covering 6 (track, N) pairs | PLAN-2.1 | Task 1 | 5 parametrized test functions with @pytest.mark.parametrize("track,n", [...]) covering straight/rectangular/spiral × 3/4 |

**Verdict:** All ROADMAP deliverables are addressed. No deliverable is missing or partially addressed.

---

## RESEARCH.md Coverage

RESEARCH.md provides foundational analysis for Phase 2. The plans must operationalize the recommendations:

| Section | Recommendation | Plan Adoption | Evidence |
|---|---|---|---|
| Section 1 (tracks.py usage map) | 9 functions need `n` parameter (table) | PLAN-1.1 Task 1 | Action enumerates each function exactly as table specifies |
| Section 2 (race.py map) | 14 `turtles_list` sites, 4 `tortuga` sites, 1 `create_turtles`, etc. | PLAN-2.1 Task 2 | References RESEARCH.md Section 2 table explicitly; points (4), (6) match table rows |
| Section 3 (main.py map) | 7 call-site changes per table | PLAN-3.1 Task 1 | References RESEARCH.md Section 3 table; points (1)-(9) map exactly |
| Section 4 (test_tracks.py map) | 15+ test sites that use N_LANES; both N-specific and structural invariant patterns | PLAN-1.1 Task 2 + PLAN-2.1 Task 1 | Task 2 point (4) lists affected lines per RESEARCH.md Section 4; Task 1 adds new parametrized tests per Section 7 (structural invariants pattern) |
| Section 5 (test_constants.py) | Zero N_LANES references; no test modifications needed | PLAN-2.1 Task 2 context | Acknowledged implicitly (no test_constants.py changes listed); done criterion does not include regressions |
| Section 7 (geometry tests) | 5 test functions recommended (test_n_start_positions_are_distinct, etc.) | PLAN-2.1 Task 1 | Action point (1) specifies all 5 test functions with exact names and signatures from Section 7 |
| Section 9 (Gotchas) | G1–G9 risks (lane_coefficient cascade, spiral stagger, _rectangular_finish_y, boundary_stones, podium, logging, call order, place_labels, visual regression) | Various | G2 spiral stagger: no visual tuning in Phase 2 (deferred to Phase 5) ✓; G4 _rectangular_finish_y: test import updated in PLAN-1.1 Task 2 ✓; G7 call order: reorder explicitly in PLAN-3.1 Task 1 point (2) ✓; G9 visual regression: manual smoke in PLAN-3.1 Task 2 point (d) ✓ |

**Verdict:** All major research recommendations are operationalized in plan tasks. Gotchas are either explicitly addressed or correctly deferred (e.g., spiral visual tuning to Phase 5).

---

## Summary: Coverage by Requirement Type

### Structural Requirements (Code Organization)
- ✅ tracks.py N-parameterization (PLAN-1.1)
- ✅ N_LANES removal (PLAN-1.1, PLAN-3.1 verification)
- ✅ Identifier renames (PLAN-2.1, PLAN-3.1)
- ✅ Function signature updates (PLAN-1.1 tracks.py, PLAN-2.1 race.py, PLAN-3.1 main.py)

### Behavioral Requirements
- ✅ `create_racers(species)` reads SPECIES dict (PLAN-2.1)
- ✅ Racer dicts include 'name' field (PLAN-2.1)
- ✅ Turtle race parity (PLAN-3.1 manual smoke)
- ✅ N-safe shared_distance computation (PLAN-2.1 context notes RESEARCH.md analysis)

### Testing Requirements
- ✅ N=3 and N=4 geometry tests (PLAN-2.1)
- ✅ All existing tests updated and passing (PLAN-1.1)
- ✅ Full pytest green (all 3 plans)
- ✅ Manual smoke on all 3 tracks (PLAN-3.1)

### Documentation Requirements
- ✅ SUMMARY files per Phase 1 retrospective (all 3 plans, Task 3/Task 2/Task 2)
- ✅ File-specific git add (all 3 plans)
- ✅ Module-level comment in test_tracks.py (PLAN-2.1 Task 1)

---

## Gaps Identified

**None.** All Phase 2 requirements and must_haves are explicitly addressed by the three plans. No requirement is missing, deferred, or underspecified.

Minor clarifications that are already handled:
- **Straight-track spacing formula ambiguity (RESEARCH.md "Uncertainty Flags")**: ROADMAP mentions `track_height/(N+1)` but current code uses fixed `LANE_SPACING`. RESEARCH.md flags this as "Decision Required." Neither plan claims to change the formula, so the architectural decision to keep the current layout is implicitly accepted. This is not a coverage gap — it is a *correct* non-change.
- **lane_start_pose signature change (inferred but not in CONTEXT-2.md's 14-line list)**: PLAN-1.1 Task 1 explicitly adds `(track_name, lane_idx, n)` signature, so the inferred change is addressed.
- **Manual smoke delegation (headless environment)**: PLAN-3.1 Task 2 context acknowledges "If the builder is non-interactive, this step is delegated to the human reviewer and explicitly called out in SUMMARY-3.1.md as 'MANUAL SMOKE PENDING'." No coverage gap — the plan has a contingency.

---

## Recommendations

**None.** All plans are well-scoped, have concrete acceptance criteria, and collectively cover Phase 2 fully. The plans can proceed to execution.

**Note on Phase 1 retrospective reminders:** Both PLAN-2.1 and PLAN-3.1 explicitly call out the two Phase 1 lessons:
1. Write SUMMARY files before returning (done criterion in all 3 plans)
2. Use file-specific `git add` (done criterion in all 3 plans)

These are embedded in the acceptance criteria, not left to chance.

---

## Verdict

**PASS**

**Summary:** The three Phase 2 plans (PLAN-1.1, PLAN-2.1, PLAN-3.1) collectively satisfy all Phase 2 success criteria from ROADMAP.md and all must_haves from CONTEXT-2.md. Coverage is complete:

- **Structural:** tracks.py N-parameterized; N_LANES deleted; race.py refactored with new API; main.py wired to new API.
- **Behavioral:** `create_racers(species)` reads SPECIES; racer dicts include 'name'; N-safe geometry and race loop; turtle parity maintained.
- **Testing:** N=3 and N=4 geometry tests added; all existing tests updated; full test suite green; manual smoke on all 3 tracks.
- **Documentation:** SUMMARY files and file-specific commits per Phase 1 lessons.

**No gaps. No conflicts. All dependencies and wave ordering correct. All acceptance criteria are concrete and testable (automated or manual with clear success conditions).**

The plans can proceed to execution.

---

**Report generated:** 2026-05-15  
**Verifier:** Verification Engineer (Claude Code)
