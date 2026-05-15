# Plan Critique — Turtle Race Phase 2
**Date:** 2025-02-15
**Mode:** Pre-execution feasibility stress test
**Result:** **READY** with one critical clarification needed

---

## Executive Summary

All three Phase 2 plans are **feasible and well-researched** against the actual codebase. Plan 1.1 and 2.1 are tight and correct; Plan 3.1 is clean and low-risk. However, one inferred cascade from RESEARCH.md (the `lane_start_pose` signature change) is **NOT explicitly surfaced in Plan 1.1's task description**, and one critical gotcha from RESEARCH.md Gotcha G7 is implied but not explicit in Plan 3.1's reordering step.

**Verdict:** The plans are ready for execution, but the builder should flag these two points proactively:
1. **PLAN-1.1 Task 1**: `lane_start_pose(track_name, lane_idx)` must become `lane_start_pose(track_name, lane_idx, n)` — this is a consequence of the `_LANE_BUILDERS` dispatch change.
2. **PLAN-3.1 Task 1**: The call order in main.py's round loop must place `create_racers` **before** `draw_boundary_stones` because `draw_boundary_stones` will need `n` after Plan 1.1 refactors it.

---

## Per-Plan Findings

### PLAN 1.1 — Hard-refactor tracks.py to take `n` explicitly

**Status: FEASIBLE** — all line references verified against codebase.

#### File Existence & Line Numbers ✓

| File | Must-Haves | Verified | Evidence |
|---|---|---|---|
| `tracks.py` | Remove N_LANES import at line 20 | ✓ PASS | Line 20 imports N_LANES: `from constants import (N_LANES, TRACK_PADDING, ...)` |
| `tracks.py` | 14 N_LANES usage sites | ✓ PASS | `grep -c "N_LANES" tracks.py` returns 17 (includes module docstring lines) |
| `constants.py` | Delete `N_LANES = 4` at line 57 | ✓ PASS | Line 57: `N_LANES = 4` confirmed present |
| `tests/test_tracks.py` | N_LANES import at line 10 | ✓ PASS | Line 10 imports N_LANES from constants |

#### Line-Level Spot Checks ✓

All 14 N_LANES references cited in CONTEXT-2.md verified:
- Line 57 (`_lane_coefficient`): `return (N_LANES - 1) / 2.0 - lane_idx` ✓
- Line 115 (`_rectangular_finish_y`): `return -((N_LANES - 1) / 2.0 + 1) * LANE_SPACING` ✓
- Line 165 (`_spiral_lane`): `pre_distance = (N_LANES - 1 - lane_idx) * (LANE_SPACING * 2)` ✓
- Line 181 (`_spiral_pair_cap`): `inner_o = -((N_LANES - 1) / 2.0) * LANE_SPACING` ✓
- Lines 217, 268, 274, 294, 295, 302, 315, 377, 383: All confirmed as cited in RESEARCH.md.

#### API Surface ✓

All public and private functions referenced in Task 1 exist with the correct names:
- `_lane_coefficient` (private, takes lane_idx)
- `_rectangular_finish_y` (private, no params)
- `_spiral_pair_cap` (private, no params)
- `_spiral_lane` (private, takes lane_idx)
- `_boundary_paths` (private, takes track_name)
- `build_lane_paths` (public, takes track_name; returns list of lane path dicts)
- `boundary_stones` (public, takes track_name and spacing with default)
- `start_line_segments` (public, takes track_name)
- `finish_line_segments` (public, takes track_name)
- `lane_start_pose` (public, takes track_name, lane_idx)

#### INFERRED CHANGE — lane_start_pose signature ⚠️

**Finding:** RESEARCH.md Section 1 ("Note on `lane_start_pose`") explicitly flags that `lane_start_pose` must become `(track_name, lane_idx, n)` after the builder functions become `(lane_idx, n)`. However, **PLAN-1.1 Task 1 does not mention this signature change**. It mentions updating the "builder signatures" and the `_LANE_BUILDERS` dispatch but does not call out the consequence: `lane_start_pose` must also accept `n`.

**Impact:** Medium. `lane_start_pose` is called from `race.py:145` (inside `place_racers_on_track`) and from `tests/test_tracks.py` (3 call sites at lines approx. 81, 107, 316 area). If the builder refactor is done but `lane_start_pose` is not updated, Task 2 (`tests/test_tracks.py` updates) will hit a `TypeError` when tests try to call `lane_start_pose(track, lane_idx, n)` against the old signature.

**Recommendation:** Explicitly add to PLAN-1.1 Task 1's action text: "(15) Change `lane_start_pose(track_name, lane_idx)` → `lane_start_pose(track_name, lane_idx, n)` and forward `n` to the builder call."

---

### PLAN 2.1 — Add N=3 geometry tests + generalize race.py (TDD)

**Status: FEASIBLE** — well-scoped and cleanly separated from Plan 1.1.

#### Dependencies ✓

- Depends on Plan 1.1 (marked in YAML). Correct — Plan 1.1 must deliver the N-parameterized tracks.py before Plan 2.1 can add N=3 tests that call it.

#### Task 1 (Geometry tests) ✓

- Recommends Approach A (parametrize) — justified by RESEARCH.md Section 7 findings (precedent in the file at lines 44, 333, 400, 409).
- Test structure references match RESEARCH.md Section 7 Test 1–5 exactly.
- Parametrization over `(track, n)` tuples is sound.
- Expected count of new test invocations (18–22) is reasonable for N ∈ {3, 4} over 3 tracks.

**One note:** The task description says "place at the bottom of the file, after the existing tests" — this is a minor style comment and is appropriate. The tests themselves are straightforward assertions on geometry invariants.

#### Task 2 (race.py refactor) ✓

All refactors align with CONTEXT-2.md Decisions 4, 5, 7:

| Change | CONTEXT Decision | Location(s) | Verified |
|---|---|---|---|
| `turtles_list` → `racers` | Decision 5 | 14 sites in race.py per RESEARCH.md table | ✓ All named |
| `tortuga` → `racer` | Decision 4 | 4 sites (lines ~144, 146–151, 247, 248) | ✓ Confirmed in sed output |
| `create_turtles` → `create_racers(species)` | Decision 5 | Line 135 (function def) | ✓ Exists, takes color_list |
| `place_turtles_on_track` → `place_racers_on_track` | Decision 5 | Line 142 (function def) | ✓ Exists |
| Logging: `TURTLE_NAMES[i]` → `racers[i]['name']` | Decision 7 | Lines 181, 228 | ✓ Both lines confirmed, use TURTLE_NAMES now |
| Add `n` to draw_* functions | Derived from Decision 1 | race.py lines 77, 85, 127 | ✓ Functions exist, currently take only track_name |

**create_racers implementation:** Task 2 specifies the shape:
```python
def create_racers(species: str):
    data = SPECIES[species]
    racers = []
    for name, color in zip(data["names"], data["colors"]):
        racers.append({'name': name, 'color': color, 'o': Turtle(shape="turtle")})
    return racers
```

This is verified correct — `SPECIES["turtles"]["names"]` and `["colors"]` both exist and are 4-element lists matching `TURTLE_NAMES` and `TURTLE_COLORS`.

#### Verification commands ✓

Task 2's done criterion is tight:
- `pytest` — will pass if race.py refactors are correct.
- `grep -n "turtles_list\|create_turtles\|place_turtles_on_track\|tortuga" race.py` returns zero — will verify rename completeness.
- `race.create_racers` and `place_racers_on_track` exist — can be checked with `hasattr`.

All commands are runnable and verifiable.

#### Note on main.py ✓

Task 2 explicitly states: "main.py is NOT touched in this task — it will be temporarily broken (calls `create_turtles` which no longer exists). That is intentional and resolved in Plan 3.1."

This is correct and transparent. Tests do not import main.py, so `pytest` will pass even though main.py is broken. This is a safe intermediate state.

---

### PLAN 3.1 — Wire main.py to the new race.py API; turtle parity smoke

**Status: FEASIBLE** — small, low-risk wire-up plan with critical manual gate.

#### Scope ✓

Single file (main.py), 7 refactoring steps per RESEARCH.md Section 3 table. All call sites verified:

| Line | Call | Change | Verified |
|---|---|---|---|
| 11 | `from constants import TURTLE_COLORS` | Remove import | ✓ Line 11 confirmed |
| 30 | `race.create_turtles(TURTLE_COLORS)` | → `race.create_racers("turtles")` | ✓ Line 30 confirmed |
| 31 | `race.place_turtles_on_track(turtles_list, track_name)` | → `race.place_racers_on_track(racers, track_name)` | ✓ Line 31 confirmed |
| 32 | `race.draw_start_line(track_name)` | → `race.draw_start_line(track_name, len(racers))` | ✓ Line 32 confirmed |
| 33 | `race.draw_finish_line(track_name)` | → `race.draw_finish_line(track_name, len(racers))` | ✓ Line 33 confirmed |
| 29 | `race.draw_boundary_stones(track_name)` | → `race.draw_boundary_stones(track_name, len(racers))` | ✓ Line 29 confirmed |
| 37 | `race.run_race(turtles_list, track_name, user_bet)` | → `race.run_race(racers, track_name, user_bet)` | ✓ Line 37 confirmed |
| 39–42 | Remaining `turtles_list` refs | → `racers` | ✓ Lines 39, 40, 42 confirmed |

#### CALL ORDER ISSUE — Gotcha G7 ⚠️

**Finding:** RESEARCH.md Gotcha G7 states:
> Currently `main.py` calls `draw_boundary_stones(track_name)` on line 29, **before** `create_turtles` on line 30. After the refactor, `draw_boundary_stones` needs `n`.

**Current main.py order (lines 28–33):**
```python
28: race.set_background()
29: track_name = dialogs.get_user_track()
29: race.draw_boundary_stones(track_name)
30: turtles_list = race.create_turtles(TURTLE_COLORS)
31: race.place_turtles_on_track(turtles_list, track_name)
32: race.draw_start_line(track_name)
33: race.draw_finish_line(track_name)
```

**After Plan 1.1**, `draw_boundary_stones` must accept `n`:
```python
def draw_boundary_stones(track_name, n):
    ...
    for x, y in tracks.boundary_stones(track_name, n):
        ...
```

**Required fix:** Move line 30 (`create_racers`) **before** line 29 (`draw_boundary_stones`):
```python
28: race.set_background()
29: track_name = dialogs.get_user_track()
30: racers = race.create_racers("turtles")
29: race.draw_boundary_stones(track_name, len(racers))
31: race.place_racers_on_track(racers, track_name)
32: race.draw_start_line(track_name, len(racers))
33: race.draw_finish_line(track_name, len(racers))
```

**Status in Plan 3.1:** Task 1's action text mentions:
> "(2) Reorder the round-loop setup so create_racers runs before any of the draw_* calls that now need `n`."

And:
> "Exact line positions per RESEARCH.md Section 3 table — move what was line 30 (the racers-creation) above what was line 29 (draw_boundary_stones)."

**This is correct and explicit.** ✓ No gap here.

#### Verification Commands ✓

- `python -c "import ast; ast.parse(open('main.py').read()); print('main.py parses')"` — simple syntax check.
- `grep -n "turtles_list|create_turtles|..." main.py` — verifies renames.
- `grep "N_LANES|turtles_list|..." *.py` — repo-wide verification (uses Grep tool, pattern is regex).
- `python main.py` — **manual smoke test** on all 3 tracks.

**Manual smoke is the critical gate** per CONTEXT-2.md Decision 6: "zero visual regression vs. pre-Phase-2 baseline". RESEARCH.md Gotcha G9 notes: "No automated visual diff exists". Task 2 of Plan 3.1 acknowledges this:
> "If the builder cannot run `python main.py` (headless environment), the SUMMARY must explicitly flag the smoke as pending human verification — do not declare Phase 2 complete on automated tests alone."

**This is appropriate and transparent.** ✓

---

## Cross-Plan Dependency Verification

| Dependency | Stated | Verified |
|---|---|---|
| PLAN-1.1 has no dependencies (Wave 1) | ✓ Correct | No prior plans in scope; standalone. |
| PLAN-2.1 depends on PLAN-1.1 | ✓ Correct | Task 1 adds N=3 tests against refactored tracks.py from 1.1; Task 2 assumes N_LANES is gone. |
| PLAN-3.1 depends on PLAN-1.1 and PLAN-2.1 | ✓ Correct | Task 1 calls the new race.py API (from 2.1); assume tracks.py is refactored (from 1.1). |
| Wave 1 → Wave 2 → Wave 3 is sequential | ✓ Correct | No cross-wave forward references; each wave is independent given prior dependencies. |

---

## File Conflict Audit

**Files touched by each plan:**

| File | Plan 1.1 | Plan 2.1 | Plan 3.1 | Conflict? |
|---|---|---|---|---|
| `tracks.py` | ✓ (refactor) | — | — | No |
| `constants.py` | ✓ (delete N_LANES) | — | — | No |
| `tests/test_tracks.py` | ✓ (update N calls) | ✓ (add new tests) | — | No — sequential; 1.1 updates existing, 2.1 adds new. |
| `race.py` | — | ✓ (rename + refactor) | — | No |
| `main.py` | — | — | ✓ (wire-up) | No |

**Verdict: Zero file conflicts.** ✓

---

## Verification Command Quality

| Plan | Command | Quality |
|---|---|---|
| 1.1 | `pytest` | ✓ Concrete, runnable. |
| 1.1 | `pytest tests/test_tracks.py -v` | ✓ Concrete, runnable. |
| 1.1 | `python -c "import constants; print(hasattr(constants, 'N_LANES'))"` | ✓ Concrete, checks expected False. |
| 1.1 | Grep `N_LANES` with glob `*.py` → zero results | ✓ Concrete, runnable with Grep tool. |
| 2.1 | `pytest` | ✓ Concrete. |
| 2.1 | `pytest tests/test_tracks.py -v` | ✓ Concrete. |
| 2.1 | `grep ... "turtles_list\|..." race.py` (excluding main.py) | ✓ Concrete; clarifies scope (main.py still broken). |
| 3.1 | `python -c "import ast; ast.parse(...)` | ✓ Concrete syntax check. |
| 3.1 | `grep ... N_LANES\|turtles_list\|...` all `*.py` | ✓ Concrete. |
| 3.1 | `python main.py` (manual) on 3 tracks | ✓ Concrete but requires interactive testing; contingency noted if headless. |

**All verification commands are concrete and runnable.** ✓

---

## Risk Assessment

| Risk | PLAN Exposure | Mitigation in Plan |
|---|---|---|
| Cascade: `lane_start_pose` signature change not called out in Task 1 | PLAN 1.1 | ⚠️ **See Inferred Change section above** — not mentioned, but RESEARCH.md flags it. Builder must consciously include it. |
| Test suite breaks if `lane_start_pose` signature not updated | PLAN 1.1 → 2.1 | Moderate — Task 2 (`test_tracks.py` updates) will fail with `TypeError` if Task 1 missed `lane_start_pose`. |
| `draw_boundary_stones` call before `create_racers` in main.py | PLAN 3.1 | ✓ Explicitly handled in Task 1 step (2); reorder is clear. |
| Manual smoke test cannot run in headless CI | PLAN 3.1 | ✓ Task 2 acknowledges and provides fallback (SUMMARY must flag if pending). |
| Spiral N=3 visual quality (stagger cramped) | Phase 2+ | Low risk — RESEARCH.md notes this is deferred to Phase 5 visual polish; Phase 2 does not run N=3 races at runtime. |
| `_rectangular_finish_y` direct import in tests | PLAN 1.1 | ⚠️ RESEARCH.md Gotcha G4 mentions `test_tracks.py:81` imports `_rectangular_finish_y` directly. When signature changes to `(n)`, the test call must update too. PLAN 1.1 Task 2 does address this (lines 81, 87 per action text step (3)). ✓ |

---

## Builder Reminders (from CONTEXT-2.md)

Both explicitly called out in the plans:

1. **Write SUMMARY file to disk before returning** — explicitly stated in Task 3 (Plan 1.1), Task 2 (Plan 2.1), Task 2 (Plan 3.1). ✓

2. **Use file-specific `git add`** — explicitly stated in all three plans' done criteria. ✓

---

## Hidden Dependencies & Gotchas

### Gotcha G1: `_lane_coefficient` cascade ✓
PLAN 1.1 Task 1 handles it by updating `_LANE_BUILDERS` dispatch and all 4 callers.

### Gotcha G2: Spiral staggered start (N=3 geometry) ✓
PLAN 2.1 Task 1 adds test coverage for N=3 spiral paths. Test will catch any breakage.

### Gotcha G3: `_spiral_pair_cap` innermost lane computation ✓
PLAN 1.1 Task 1 updates it to take `n`; PLAN 2.1 test `test_spiral_n_lanes_all_end_at_origin` verifies correctness.

### Gotcha G4: `_rectangular_finish_y` direct import in tests ✓
PLAN 1.1 Task 2 explicitly updates the test import and call site.

### Gotcha G5: `show_podium` hardcoded top-3 ✓
RESEARCH.md verified it is N-safe; no changes needed. Plans do not touch it — correct.

### Gotcha G6: `run_race` logging uses `TURTLE_NAMES` ✓
PLAN 2.1 Task 2 replaces with `racers[i]['name']`. Correct.

### Gotcha G7: `draw_boundary_stones` call order ✓
PLAN 3.1 Task 1 explicitly reorders. Correct.

### Gotcha G8: `place_labels` hardcoded to 4 entries ✓
RESEARCH.md verified it is N-safe with fallback; no changes needed. Plans do not touch it — correct.

### Gotcha G9: Manual smoke as primary acceptance gate ✓
PLAN 3.1 Task 2 makes this the final gate. Correct.

---

## Inferred Changes Not Yet Explicit

### 1. `lane_start_pose` signature change

**Where:** PLAN 1.1 Task 1, step 10 area.

**Current text:** "(10) Change `lane_start_pose(track_name, lane_idx)` → `lane_start_pose(track_name, lane_idx, n)` and forward `n` to the builder."

**Status:** Actually, re-reading Task 1, it DOES mention this at step 10! Let me re-verify...

**Verified:** PLAN 1.1 Task 1 action text includes: "(10) Change `lane_start_pose(track_name, lane_idx)` → `lane_start_pose(track_name, lane_idx, n)` and forward `n` to the builder."

✓ **Already covered.** No gap here after all.

### 2. Call order in main.py

**Where:** PLAN 3.1 Task 1, step (2).

**Status:** Explicitly stated. ✓

---

## Completeness vs. ROADMAP

| ROADMAP Requirement | Addressed by Plan(s) | Verified |
|---|---|---|
| Phase 2 success: turtles-only race with N parameterized to tracks/race | Plans 1.1, 2.1, 3.1 | ✓ |
| Zero visual regression for N=4 vs. master | Plan 3.1 Task 2 manual smoke | ✓ |
| TURTLE_NAMES removed from module-level scope | Plan 1.1, Plan 2.1 | ✓ Plan 1.1 removes import; Plan 2.1 replaces logging usage. |
| N_LANES removed from constants.py | Plan 1.1 Task 3 | ✓ |
| Test coverage for N=3 + N=4 geometry | Plan 2.1 Task 1 | ✓ |
| No back-compat aliases (Decision 5) | All plans | ✓ Plans do direct renames; no aliases. |

---

## Final Verdict

**READY** — All three plans are feasible, well-researched, and verified against the actual codebase. Line numbers match, API surfaces are correct, dependencies flow correctly, and verification commands are concrete and runnable.

**One small thing to flag:** The `lane_start_pose` signature change is **already explicitly mentioned** in PLAN 1.1 Task 1 step (10), so there is no gap after all. 

**Execution can proceed.**

---

## Recommendations for Builders

1. **Before starting Plan 1.1**, read RESEARCH.md Section 1 fully — it maps all 15 function changes (14 + `lane_start_pose`), and PLAN-1.1 Task 1 covers all 15.

2. **After completing PLAN-1.1 Task 1**, run `pytest tests/test_tracks.py -v` to confirm the refactored tracks.py functions are callable with the new signatures before moving to Task 2.

3. **Before Plan 3.1 Task 1**, ensure the order change in main.py is done first (move `create_racers` before `draw_boundary_stones`); this unblocks the rest of the main.py wire-up.

4. **Plan 3.1 Task 2 (manual smoke)** is non-negotiable. If the builder is in a headless environment, flag this explicitly in SUMMARY-3.1.md as "PENDING HUMAN SMOKE TEST" and do not mark Phase 2 complete until human verification is done.

5. **Use the Grep tool** for repo-wide verification instead of shell grep — the plans reference this tool, and it handles regex patterns correctly.

