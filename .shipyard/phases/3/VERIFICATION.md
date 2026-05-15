# Phase 3 Verification Report
**Phase:** 3 — Species + Snake-Aware Bet Dialogs  
**Date:** 2026-05-15  
**Type:** build-verify  
**Verifier:** claude-haiku-4-5-20251001

---

## Results

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `get_user_species()` exists and is callable | PASS | `dialogs.py:194` defines `def get_user_species():` with no parameters. Verified: `callable(dialogs.get_user_species) == True`. |
| 2 | `get_user_species()` returns "turtles" or "snakes" | PASS | Lines 217-221: `make_cb` closure sets `selected[0]` to `"turtles"` or `"snakes"` (exact strings matching `SPECIES` keys). Line 284 returns `selected[0]`. Spec compliance verified. |
| 3 | Species dialog has composite button images | PASS | Lines 223-245 (turtle composite): `Image.new("RGBA")`, cell-based pasting with alpha mask. Lines 247-261 (snake composite): same pattern, resized to 200×200. Both converted to `RGBA` before paste (lines 228, 253). Dialog retains `PhotoImage` refs on `dialog._species_images = []` (line 215). |
| 4 | `SPECIES_DIALOG_IMAGE_SIZE = 200` in constants | PASS | `constants.py:26` declares `SPECIES_DIALOG_IMAGE_SIZE = 200`. Test `tests/test_constants.py:31-34` validates: positive int and >= BET_IMAGE_SIZE. Verified: `SPECIES_DIALOG_IMAGE_SIZE == 200` (type int). |
| 5 | `_TURTLE_GRID_LAYOUT` hoisted to module-level | PASS | `dialogs.py:16-21` defines `_TURTLE_GRID_LAYOUT = [("Leonardo", 1, 0), ("Donatello", 1, 1), ("Raphael", 2, 0), ("Michaelangelo", 2, 1)]` after imports. Verified: exact values match spec. |
| 6 | `_SNAKE_ROW_LAYOUT` hoisted to module-level | PASS | `dialogs.py:24-28` defines `_SNAKE_ROW_LAYOUT = [("Shadow", 1, 0), ("Ralph", 1, 1), ("Anaconda", 1, 2)]`. Verified: matches `SNAKE_NAMES` order, exact layout. |
| 7 | `get_user_bet(species)` signature accepts species | PASS | `dialogs.py:31` signature `def get_user_bet(species):`. Verified via inspect: `list(signature.parameters.keys()) == ['species']`. |
| 8 | `get_user_bet` dispatches on bet_layout | PASS | Lines 43-45: reads `bet_layout`, `species_names`, `species_images` from `SPECIES[species]`. Lines 63-122: if/elif/else on `bet_layout` with three branches: `"grid_2x2"` (turtles, lines 63-90), `"row_3"` (snakes, lines 92-119), else raise ValueError. Verified: both branches share `dialog._bet_images` initialization (line 55) and `make_cb` (lines 57-61), avoiding duplication. |
| 9 | Turtle bet dialog unchanged (regression check) | PASS | Lines 63-90: turtle branch uses `_TURTLE_GRID_LAYOUT`, title "Turtle Racing", label matches spec, `columnspan=2`, image source from `species_images[name]` (PILresized to `BET_IMAGE_SIZE`), 1-based index via `species_names.index(name) + 1`. Semantically identical to pre-refactor version. |
| 10 | Snake bet dialog layout is 1×3 row | PASS | Lines 92-119: snake branch uses `_SNAKE_ROW_LAYOUT`, title "Snake Racing", label "Which snake do you think will win the race?", `columnspan=3`, same PIL pipeline, 1-based index convention preserved. Verified: 3 columns, 1 row. |
| 11 | `SPECIES` dict has required keys | PASS | `constants.py:40-55` defines `SPECIES` with keys `"turtles"` and `"snakes"`. Each has subkeys: `"names"` (list), `"colors"` (list), `"images"` (dict), `"bet_layout"` (str), `"shape_drawer"` (str). Verified: `SPECIES["turtles"]["names"] == ['Raphael', 'Michaelangelo', 'Leonardo', 'Donatello']` (len 4); `SPECIES["snakes"]["names"] == ['Shadow', 'Ralph', 'Anaconda']` (len 3). `bet_layout` values: `"grid_2x2"` for turtles, `"row_3"` for snakes. |
| 12 | `main.py` calls `get_user_species()` between track and racer-creation | PASS | `main.py:27-29`: `track_name = dialogs.get_user_track()` (line 27), `species = dialogs.get_user_species()` (line 28), `racers = race.create_racers(species)` (line 29). Insertion position and order match spec exactly. |
| 13 | `main.py` passes `species` to `create_racers` | PASS | `main.py:29`: `racers = race.create_racers(species)`. Hardcoded `"turtles"` literal is gone. Verified: AST walk confirms `race.create_racers` is called with `species` variable, not a string literal. |
| 14 | `main.py` passes `species` to `get_user_bet` | PASS | `main.py:36`: `user_bet = dialogs.get_user_bet(species)`. Phase 2 Wave 1 left this as `dialogs.get_user_bet()` with no args (intentional breakage); Wave 2 fixes it. Verified: call site updated. |
| 15 | `create_racers` docstring documents `species` param | PASS | `race.py:135-151` includes docstring: "Args: species — A key in constants.SPECIES — either \"turtles\" or \"snakes\". ... Raises: KeyError: If species is not in SPECIES." Verified: 'species' and 'KeyError' both in `__doc__`. |
| 16 | `create_racers` docstring documents returned dict keys | PASS | `race.py:135-151` Returns section: "... dicts with keys 'name', 'color', 'o'. ..." Verified: 'name' in `__doc__`. Fulfills DOCUMENTATION-2 actionable from Phase 2 VERIFICATION. |
| 17 | Modal pattern: WM_DELETE_WINDOW no-op in species dialog | PASS | `dialogs.py:205`: `dialog.protocol("WM_DELETE_WINDOW", lambda: None)`. Matches existing pattern in `get_user_track` and `get_user_bet`. |
| 18 | Modal pattern: grab_set + wait_window in species dialog | PASS | `dialogs.py:281-282`: `dialog.grab_set()` then `dialog.wait_window()`. Correct order and method names. |
| 19 | `n = len(racers)` hoisted in main.py | PASS | `main.py:30`: `n = len(racers)` defined once. Lines 31, 33, 34 use `n` for `draw_boundary_stones`, `draw_start_line`, `draw_finish_line`. No residual `len(racers)` calls in the loop body. Fulfills SIMPLIFICATION-2 S2.2 carry-over. |
| 20 | `draw_boundary_stones` call moved after `create_racers` | PASS | `main.py:31`: `race.draw_boundary_stones(track_name, n)` is now called AFTER `n = len(racers)` is available. Phase 2 VERIFICATION noted "moved AFTER create_racers (G7 already addressed in Phase 2)" — this is the realized state. |
| 21 | pytest all 77 tests pass | PASS | `pytest -q` output: `77 passed in 0.10s`. Baseline Phase 2: 76. Phase 3 adds 1 new test (`test_species_dialog_image_size_is_positive_int`). No regressions. All Phase 1/2 tests still passing. |
| 22 | No hardcoded `"turtles"` remains in race-creation block | PASS | Grep for hardcoded species literal in `main.py:28-36` region: zero matches. Variable `species` is used throughout. |
| 23 | Phase 2 carry-over: `create_racers` docstring | PASS | See criterion 15-16. Fulfilled. |
| 24 | Phase 2 carry-over: `n = len(racers)` hoist | PASS | See criterion 19. Fulfilled. |
| 25 | Review verdict REVIEW-1.1: PASS | PASS | REVIEW-1.1.md line 6: `verdict: PASS`. All three Wave 1 tasks (SPECIES_DIALOG_IMAGE_SIZE, layout hoists, get_user_bet refactor) pass spec compliance. Minor finding (missing SNAKE_NAMES import) recorded but non-blocking. |
| 26 | Review verdict REVIEW-2.1: PASS | PASS | REVIEW-2.1.md line 6: `verdict: PASS`. All three Wave 2 tasks (get_user_species, main.py wire-up, docstring) pass spec compliance. Smoke gate PENDING_HUMAN_VERIFICATION as expected (no display available to autonomous verifier). |
| 27 | SUMMARY-2.1.md exists and is complete | PASS | File exists at `.shipyard/phases/3/results/SUMMARY-2.1.md`. Contains: task table, commit SHAs, pytest results (77/77), manual smoke checklist (4 rows PENDING), phase close-out statement ("Snakes mode reaches podium..."), deferred actionables (5 items including "Real snake shapes" and "L_BASE tuning" for Phase 4). |
| 28 | No stale imports in dialogs.py (carry-over) | PARTIAL | REVIEW-2.1 lines 98-102 note: `TURTLE_NAMES` and `TURTLE_IMAGES` are imported (`dialogs.py:8`) but no longer used in the refactored `get_user_bet`. After refactor, all turtle lookups go through `SPECIES[species]["names"]` and `SPECIES[species]["images"]`. This is a stale-import issue flagged as "Important" in REVIEW-2.1 with remediation: remove on next touch of `dialogs.py` in Phase 4. Non-blocking for Phase 3 acceptance but documented for Phase 4. |
| 29 | Missing SNAKE_NAMES import (carry-over) | PARTIAL | REVIEW-1.1 lines 87-90 and REVIEW-2.1 lines 93-96 both note: `SNAKE_NAMES` not imported despite plan spec. Comment at `dialogs.py:23` references `SNAKE_NAMES` by name, but actual hardcodes names in `_SNAKE_ROW_LAYOUT`. Zero runtime impact. Flagged as "Important" in REVIEW-2.1 with remediation: add import in Phase 4. Non-blocking for Phase 3 but documented for Phase 4. |
| 30 | Image assets exist on disk (all species) | PASS | Verified: `assets/turtle_*.jpg` (4 files) and `assets/snakes/*.png` (3 files) all exist and are readable via `resource_path()`. Tested: `os.path.exists()` for each image path returned True. |
| 31 | Spec deviation: RGBA vs. RGB in composites | PASS | Plan specified `Image.new("RGB", ...)` but code uses `"RGBA"` (lines 225, 250). CRITIQUE.md explicitly recommended RGBA to handle JPG/PNG mode mismatch without alpha-channel corruption. Code also calls `.convert("RGBA")` on all sources before paste (lines 228, 253), confirming intentional upgrade. REVIEW-2.1 line 44 approves: "This is the correct choice." No issue. |

---

## Gaps

### Closed Gaps (Phase 3 accomplished)
- **All Phase 3 success criteria from ROADMAP met:** species dialog exists, bet dialog dispatches on layout, main.py wires species end-to-end, all required constants defined, tests pass.
- **All Phase 2 carry-over items addressed:** `create_racers` docstring added, `n = len(racers)` hoisted.
- **Both review verdicts are PASS:** Wave 1 and Wave 2 reviews found no critical issues; minor findings are non-blocking and documented for Phase 4.

### Deferred (Not Gaps, Documented for Phase 4)
| Item | Location | Status | Next Phase |
|------|----------|--------|-----------|
| Real snake shapes (currently turtle-shaped) | `race.py:156` | Placeholder: `shape="turtle"` for all species | Phase 4: wire `SPECIES[species]["shape_drawer"]` to `draw_snake_shape()` |
| L_BASE placeholder (snake body-length scaling) | `constants.py:37` | Stub value: `L_BASE = 1.0` | Phase 4: tune visually on straight track; verify on rectangular/spiral |
| Head-position finish-line detection | `race.py` (run_race) | Not yet implemented; currently uses center position for all | Phase 4: add head-offset computation for snakes |
| `TURTLE_NAMES` stale import | `dialogs.py:8` | Imported but unused; flagged in REVIEW-2.1 Important | Phase 4: remove when next touching dialogs.py |
| `SNAKE_NAMES` missing import | `dialogs.py:7-10` | Not imported despite spec; flagged in REVIEW-2.1 Important | Phase 4: add alongside stale-import cleanup |
| CLAUDE.md "Turtle identity is positional" section | `CLAUDE.md` | Pre-existing; needs comprehensive rewrite for species-agnostic architecture | Phase 3+4 completion or Phase 5 polish |

### Manual Smoke Gate (PENDING_HUMAN_VERIFICATION)
**Status:** PENDING — autonomous verifier cannot execute Tk dialogs or render graphics.

The SUMMARY-2.1.md specifies a 4-round manual smoke checklist (lines 83-88):
1. Straight track, Turtles species → species dialog renders composites, turtle bet dialog 2×2, 4 racers, 4-finisher podium
2. Rectangular track, Snakes species → snake bet dialog 1×3 row, 3 racers (turtle-shaped placeholders), 3-finisher podium
3. Spiral track, Turtles species → visually identical to pre-Phase-3 master (zero regression)
4. Any track, any species → "Play again? No" → clean exit, no Tk errors

**Acceptance:** Phase 3 is functionally complete pending human execution of `python main.py` and visual confirmation of the checklist. Code is ready; no blocking issues identified.

---

## Recommendations

1. **Execute manual smoke gate.** Human (Alejandro) should run `python main.py` and complete the 4-round checklist in SUMMARY-2.1.md lines 83-88. Expected outcome: all rows PASS (no crashes, images render, species switching works). Mark as PENDING_HUMAN_VERIFICATION until complete.

2. **Phase 4 carry-over items (non-blocking for Phase 3):**
   - Implement `draw_snake_shape(t, length_units)` in `race.py` (high-risk per ROADMAP).
   - Tune `L_BASE` constant empirically on straight track.
   - Implement head-position finish detection in `run_race()`.
   - Add `SNAKE_NAMES` import + remove `TURTLE_NAMES`/`TURTLE_IMAGES` stale imports in `dialogs.py`.
   - Wire `SPECIES[species]["shape_drawer"]` dispatch in `create_racers()`.

3. **Phase 5 carries over spiral 3-lane visual inspection** if Phase 4 flags cramped or asymmetric entry points.

---

## Verdict

**COMPLETE (pending manual smoke verification)**

All Phase 3 success criteria from ROADMAP are met:
- `get_user_species()` exists with composite images ✓
- `get_user_bet(species)` dispatches on bet_layout ✓
- `_TURTLE_GRID_LAYOUT` and `_SNAKE_ROW_LAYOUT` hoisted ✓
- `main.py` wires species end-to-end ✓
- `SPECIES_DIALOG_IMAGE_SIZE = 200` in constants ✓
- Both review verdicts are PASS ✓
- pytest 77/77 green (no regressions) ✓
- Phase 2 carry-overs addressed (docstring, n hoist) ✓
- Manual smoke gate is PENDING_HUMAN_VERIFICATION (expected state) ✓

The codebase is ready for Phase 4. No blocking issues. Minor deferred items (stale imports, real snake shapes, L_BASE tuning) are explicitly documented in REVIEW-2.1 carry-over table for Phase 4 pickup.

---

## Phase 4 Readiness

Phase 4 (Snake in-race shape, length, head-finish detection) may begin immediately upon human smoke clearance of Phase 3. The required API surfaces are stable:
- `SPECIES[species]["shape_drawer"]` field exists (values: "turtle" | "snake")
- `L_BASE` constant exists (placeholder value: 1.0)
- `create_racers(species)` reads from `SPECIES` and returns `'name'` field in racer dicts
- `main.py` passes `species` to all race-creation calls

All blockers for Phase 4 shape/length work are removed.
