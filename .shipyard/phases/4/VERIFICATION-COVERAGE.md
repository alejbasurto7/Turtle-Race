# Phase 4 Plan Coverage Verification
**Date:** 2026-05-15  
**Type:** plan-review  
**Plans Reviewed:** PLAN-1.1, PLAN-1.2, PLAN-2.1, PLAN-3.1

---

## Deliverable Coverage Matrix

| # | Phase 4 Deliverable (from ROADMAP) | Plan | Task | Coverage | Status |
|---|-------------------------------------|------|------|----------|--------|
| 1 | `draw_turtle_shape(t)` defined in `race.py` | PLAN-2.1 | 1 | Explicit: extract existing `Turtle(shape="turtle")` into function | ✓ |
| 2 | `draw_snake_shape(t, length_units)` defined in `race.py` | PLAN-2.1 | 1 | Explicit: `t.shape("classic")` + `t.shapesize(stretch_wid=SNAKE_STRETCH_WID, stretch_len=L_BASE * length_units)` | ✓ |
| 3 | `_SHAPE_DRAWERS` dispatch table in `race.py` | PLAN-2.1 | 1 | Explicit: `{"turtle": draw_turtle_shape, "snake": draw_snake_shape}` module-level dict | ✓ |
| 4 | `create_racers(species)` refactored to use dispatch | PLAN-2.1 | 1 | Explicit: reads `_SHAPE_DRAWERS[SPECIES[species]["shape_drawer"]]`, calls drawer on fresh `Turtle()` per racer | ✓ |
| 5 | `L_BASE = 0.6` tuned from `1.0` placeholder | PLAN-1.1 | 2 | Explicit: change constant in `constants.py` + verify in tests | ✓ |
| 6 | `SNAKE_STRETCH_WID = 0.5` added to `constants.py` | PLAN-1.1 | 2 | Explicit: new constant with comment; TDD tests in Task 1 | ✓ |
| 7 | Unit tests lock `L_BASE` and `SNAKE_STRETCH_WID` | PLAN-1.1 | 1 | Explicit: `test_l_base_is_positive_float` (assert == 0.6), `test_snake_stretch_wid_is_positive_float` (assert == 0.5) | ✓ |
| 8 | Head-position finish detection — UNIVERSAL (both species) | PLAN-3.1 | 2 | Explicit: `head_offset_progress[]` parallel array; finish check becomes `progress[i] >= shared_distance - head_offset_progress[i]` | ✓ |
| 9 | Head-offset computed ONCE at race start (per-racer) | PLAN-3.1 | 2 | Explicit: compute array before race loop; RESEARCH.md §10 gotcha 5 cited | ✓ |
| 10 | Unit tests for head-offset math (trig conversion) | PLAN-3.1 | 1 | Explicit: new `tests/test_race.py`; pure-math tests on formula; Shadow/Ralph concrete assertions | ✓ |
| 11 | `announce_result` uses racer-dict identity (`is`), not `pencolor()` | PLAN-2.1 | 2 | Explicit: `winner_racer = next(r for r in racers if r['o'] is winner)`; replace ALL `pencolor()` refs | ✓ |
| 12 | `celebrate` uses racer-dict identity for `face_color` | PLAN-2.1 | 2 | Explicit: same `is`-based lookup pattern; use `winner_racer['color']` string (not tuple) | ✓ |
| 13 | `main.py:40` `user_won` uses `is` identity (not `pencolor() ==`) | PLAN-2.1 | 3 | Explicit: replace `pencolor() == pencolor()` with `is` comparison | ✓ |
| 14 | Win-message displays winner name/color from racer dict (fixes Ralph tuple bug) | PLAN-2.1 | 2 | Explicit: use `winner_racer['name']` + `winner_racer['color']` string in format; reject tuple display | ✓ |
| 15 | Cleanup: `dialogs.py` remove stale `TURTLE_NAMES`, `TURTLE_IMAGES` imports | PLAN-1.2 | 1 | Explicit: edit import line; confirm via Grep not referenced | ✓ |
| 16 | Cleanup: `get_user_species()` docstring locked (modal/blocking behavior) | PLAN-1.2 | 1 | Explicit: add triple-quoted docstring per RESEARCH.md §7b; mention `grab_set()`, `wait_window()`, return values | ✓ |
| 17 | Cleanup: `tracks.py:_build_spiral_legs` rename `n` → `leg_i` (eliminate shadow) | PLAN-1.2 | 2 | Explicit: identify loop var shadowing outer N parameter; rename + update loop body refs | ✓ |
| 18 | Manual smoke gate explicit in final wave | PLAN-3.1 | 3 | Explicit: Task 3 is the manual-smoke gate (6 track×species permutations + alternating round test) | ✓ |

---

## Plan Structure Verification

### Wave 1 Parallelism
- **PLAN-1.1** touches: `constants.py`, `tests/test_constants.py`
- **PLAN-1.2** touches: `dialogs.py`, `tracks.py`
- **Verdict:** Disjoint files → **PARALLEL OK**

### Wave 2 Dependencies
- **PLAN-2.1** depends on: [1.1, 1.2]
- **Requires:** `L_BASE`, `SNAKE_STRETCH_WID` from PLAN-1.1 (for `draw_snake_shape`)
- **Requires:** `dialogs.py` + `tracks.py` clean from PLAN-1.2
- **Verdict:** Dependency order correct → **PASS**

### Wave 3 Dependencies
- **PLAN-3.1** depends on: [2.1]
- **Requires:** `create_racers`, `run_race` refactored and dispatch wired (PLAN-2.1)
- **Verdict:** Dependency order correct → **PASS**

### Task Count per Plan
| Plan | Task Count | Limit |
|------|-----------|-------|
| PLAN-1.1 | 3 | ≤3 | ✓ |
| PLAN-1.2 | 2 | ≤3 | ✓ |
| PLAN-2.1 | 3 | ≤3 | ✓ |
| PLAN-3.1 | 3 | ≤3 | ✓ |

---

## Acceptance Criteria — Testability & Objectivity

| Plan | Acceptance Criteria | Testable? | Objective? |
|------|-------------------|-----------|-----------|
| PLAN-1.1 | `pytest tests/test_constants.py` green; `pytest` full green; python -c assertions | ✓ Automated | ✓ Pass/Fail |
| PLAN-1.2 | `python -c "import dialogs; help(...)"` docstring present; `pytest` green | ✓ Automated | ✓ Pass/Fail |
| PLAN-2.1 | `pytest` green; Grep `pencolor()` in race.py/main.py returns 0; function callables verified | ✓ Automated | ✓ Pass/Fail |
| PLAN-3.1 Task 1-2 | `pytest tests/test_race.py` green; `head_offset_progress` array in run_race verified | ✓ Automated | ✓ Pass/Fail |
| PLAN-3.1 Task 3 | Manual smoke 6 permutations + alternating round; snakes visibly snake-shaped 6:5:2 ratio; turtle mode unchanged | ⚠ Manual/visual | ✓ Pass/Fail (structured checklist) |

---

## File Conflict Analysis

| File | Plans | Conflict Risk |
|------|-------|----------------|
| `constants.py` | PLAN-1.1 | Single plan, sequential edits (L_BASE line + SNAKE_STRETCH_WID line) → ✓ **No conflict** |
| `tests/test_constants.py` | PLAN-1.1 | Single plan, tests added in Task 1, implementation in Task 2 → ✓ **No conflict** |
| `dialogs.py` | PLAN-1.2 | Single plan, import edit + docstring add (separate lines) → ✓ **No conflict** |
| `tracks.py` | PLAN-1.2 | Single plan, loop var rename (local scope) → ✓ **No conflict** |
| `race.py` | PLAN-2.1, PLAN-3.1 | **Potential concern**: PLAN-2.1 Task 1 adds shape functions + dispatch; PLAN-2.1 Task 2 modifies `announce_result`/`celebrate`; PLAN-3.1 Task 2 modifies `run_race` finish check. Order: 2.1 completes → 3.1 executes → **Different functions touched in sequence, mergeable** → ✓ **No conflict if commits are ordered** |
| `tests/test_race.py` | PLAN-3.1 | New file, single plan → ✓ **No conflict** |
| `main.py` | PLAN-2.1 | Single plan, line 40 edited → ✓ **No conflict** |

**Overall:** ✓ **No file conflicts detected.** PLAN-2.1 and PLAN-3.1 both modify `race.py` but in different functions and at different phases; sequential execution is safe.

---

## Verification Commands — Feasibility

| Task | Verification Command | Feasibility |
|------|---------------------|-------------|
| PLAN-1.1 Task 1 | `pytest tests/test_constants.py::test_l_base_is_positive_float tests/test_constants.py::test_snake_stretch_wid_is_positive_float` | ✓ Runnable |
| PLAN-1.1 Task 2 | `pytest tests/test_constants.py && python -c "import constants; assert constants.L_BASE == 0.6; assert constants.SNAKE_STRETCH_WID == 0.5; print('OK')"` | ✓ Runnable |
| PLAN-1.1 Task 3 | `pytest` | ✓ Runnable |
| PLAN-1.2 Task 1 | `python -c "import dialogs; help(dialogs.get_user_species)" && pytest` | ✓ Runnable |
| PLAN-1.2 Task 2 | `pytest tests/ -k "track or spiral or geometry" && pytest` | ✓ Runnable |
| PLAN-2.1 Task 1 | `pytest && python -c "import race; assert callable(race.draw_turtle_shape); assert callable(race.draw_snake_shape); assert race._SHAPE_DRAWERS['turtle'] is race.draw_turtle_shape; assert race._SHAPE_DRAWERS['snake'] is race.draw_snake_shape; print('OK')"` | ✓ Runnable |
| PLAN-2.1 Task 2 | `pytest && python -c "import race; import inspect; src = inspect.getsource(race.announce_result) + inspect.getsource(race.celebrate); assert 'pencolor()' not in src, 'pencolor() still present in announce_result/celebrate'; print('OK')"` | ✓ Runnable |
| PLAN-2.1 Task 3 | `pytest && python -c "import ast, pathlib; src = pathlib.Path('main.py').read_text(); assert 'pencolor()' not in src, 'pencolor() still in main.py'; print('OK')"` | ✓ Runnable |
| PLAN-3.1 Task 1 | `pytest tests/test_race.py -v` | ✓ Runnable |
| PLAN-3.1 Task 2 | `pytest && python -c "import race; import inspect; src = inspect.getsource(race.run_race); assert 'head_offset_progress' in src, 'head_offset_progress not wired'; print('OK')"` | ✓ Runnable |
| PLAN-3.1 Task 3 | `python main.py` (6 permutations + alternating round) | ✓ Runnable (manual gate) |

**Overall:** ✓ **All verification commands are concrete and runnable.** No vague criteria like "check that it works."

---

## Must-Haves Traceability

### PLAN-1.1 must_haves
- ✓ Tune existing L_BASE placeholder from 1.0 to 0.6 → Task 2
- ✓ Add new SNAKE_STRETCH_WID = 0.5 constant → Task 2
- ✓ Add unit tests that lock both values as positive floats with expected magnitudes → Task 1
- ✓ pytest stays green → Task 3

### PLAN-1.2 must_haves
- ✓ Remove unused TURTLE_NAMES and TURTLE_IMAGES imports from dialogs.py → Task 1
- ✓ Add locked docstring to get_user_species() → Task 1
- ✓ Rename inner `n` loop variable in tracks.py:_build_spiral_legs to `leg_i` → Task 2
- ✓ pytest stays green; manual import smoke of dialogs.py succeeds → Task 1

### PLAN-2.1 must_haves
- ✓ Extract draw_turtle_shape(t) and draw_snake_shape(t, length_units) → Task 1
- ✓ Define module-level _SHAPE_DRAWERS dispatch → Task 1
- ✓ Refactor create_racers(species) to use dispatch + pass SNAKE_LENGTHS[i] → Task 1
- ✓ Fix announce_result + celebrate to use dict-identity (`is`) → Task 2
- ✓ Fix main.py:40 user_won from pencolor() == pencolor() to `is` → Task 3
- ✓ Display configured color STRING (not pencolor tuple) in win message → Task 2
- ✓ Zero behavior regression in turtle mode; snakes still look like classic turtles → Task 2 (no-op for snakes until 3.1)
- ✓ pytest stays green → All tasks

### PLAN-3.1 must_haves
- ✓ Universal head-position finish detection in run_race (Approach B) → Task 2
- ✓ head_offset_progress computed ONCE at race start (per racer) → Task 2
- ✓ Pure-trig unit tests for head-offset math → Task 1
- ✓ Manual smoke gate: both species run end-to-end on all 3 tracks → Task 3
- ✓ Snakes look snake-shaped with 6:5:2 length ratio → Task 3
- ✓ Turtle mode visually indistinguishable from Phase 3 baseline → Task 3
- ✓ pytest stays green → Task 1, Task 2

---

## Cross-Plan Consistency

### CONTEXT-4 Decision Alignment
| Decision | Plan Coverage | Status |
|----------|---------------|--------|
| Decision 1 (Stretched `classic` first; polygon fallback) | PLAN-2.1 Task 1 (add comment); PLAN-3.1 Task 3 (smoke gate decision) | ✓ Covered |
| Decision 2 (L_BASE = 0.6; SNAKE_STRETCH_WID = 0.5) | PLAN-1.1 Tasks 1-2 | ✓ Covered |
| Decision 3 (Universal head-position finish; symmetric turtles) | PLAN-3.1 Task 2 (add comment) | ✓ Covered |
| Decision 4 (_SHAPE_DRAWERS dispatch in race.py) | PLAN-2.1 Task 1 | ✓ Covered |
| Decision 5 (Cleanups: dialogs imports, docstring, tracks rename) | PLAN-1.2 Tasks 1-2 | ✓ Covered |
| Decision 6 (Phase 4 end-state: snakes race + look snake-shaped) | PLAN-3.1 Task 3 (manual smoke) | ✓ Covered |
| Decision 7 (Spiral 3-lane deferred to Phase 5) | PLAN-3.1 Task 3 (note observations only, no fixes) | ✓ Covered |

### RESEARCH.md Alignment
| Section | Plan Coverage | Status |
|---------|---------------|--------|
| §1 (current `create_racers` body) | PLAN-2.1 Task 1 (refactor with dispatch) | ✓ |
| §2 (run_race finish detection; Approach B) | PLAN-3.1 Task 2 (head_offset_progress array) | ✓ |
| §3 (turtle.shapesize math; shape_unit_size = 9) | PLAN-3.1 Tasks 1-2 (tests + implementation comment) | ✓ |
| §4 (draw_turtle_shape / draw_snake_shape) | PLAN-2.1 Task 1 | ✓ |
| §5 (SHAPE_DRAWERS invocation) | PLAN-2.1 Task 1 | ✓ |
| §6 (Win-message fix; identity + racer dict) | PLAN-2.1 Tasks 2-3 | ✓ |
| §7a (dialogs.py stale imports) | PLAN-1.2 Task 1 | ✓ |
| §7b (get_user_species() docstring) | PLAN-1.2 Task 1 | ✓ |
| §7c (tracks.py `n` shadow rename) | PLAN-1.2 Task 2 | ✓ |
| §10 (gotchas 1-8) | Scattered across plans with inline comments | ✓ |

---

## Gaps & Observations

### No Gaps Identified
All 18 deliverables from Phase 4 ROADMAP are addressed by the 4 plans. All CONTEXT-4 decisions are explicitly covered. All RESEARCH.md recommendations are mapped to tasks.

### Minor Observations (Non-Blocking)

1. **PLAN-3.1 Task 3 polygon-fallback escalation:** The task correctly defers the polygon-fallback decision to smoke-time (CONTEXT-4 Decision 1), but does NOT pre-define a polygon silhouette in the code. If escalation is needed during smoke, the builder must design and register the shape on-the-fly. This is intentional per the decision-gate pattern; acceptable.

2. **Head-offset math documentation:** PLAN-3.1 Task 2 asks for "inline comment citing RESEARCH.md §3" but does NOT ask the builder to show the full formula in the code. The implementation is straightforward, so this is acceptable, but a verbose comment (e.g., `# head_offset_arc = stretch_len * 9 / 2, where 9 is the classic shape unit-size along heading`) might improve maintainability. The task description allows this ("Add a 1-2 line comment block").

3. **Smoke-gate alternating-round test:** PLAN-3.1 Task 3 asks for "no crashes, no image-GC blanking, no leftover shapes" but does NOT define how to verify "image-GC blanking" (e.g., visible symptoms to watch for). The criteria is reasonable for a manual smoke test, but guidance in SUMMARY-3.1.md will be essential for reproducibility.

### No Regressions Expected
- Phase 3 code is not modified except for `main.py:40` identity fix (functionally equivalent, safer).
- Turtle-mode tests in `tests/test_*.py` should remain green (no logic changes to turtles).
- Snake-mode tests (new) are isolated and do not affect existing paths.

---

## Verdict

**✓ PASS** — All Phase 4 deliverables are covered by the 4 plans. Wave structure is sound (Wave 1 parallel, Wave 2 depends on 1, Wave 3 depends on 2). No file conflicts. All acceptance criteria are testable and objective. Task counts are within limits. CONTEXT-4 decisions and RESEARCH.md recommendations are faithfully mapped to plan tasks.

**Recommendation to Builder:** Execute plans in wave order (1.1 + 1.2 parallel, then 2.1, then 3.1). Each plan's SUMMARY file will be the artifact to verify completion. The manual smoke gate in PLAN-3.1 Task 3 is the final acceptance criterion for Phase 4.
