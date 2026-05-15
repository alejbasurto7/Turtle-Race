# SUMMARY-1.1.md — Phase 3 Wave 1

## Status

COMPLETE. All three tasks executed, verified, and committed. pytest 76 → 77 tests green.

---

## Tasks Completed

### Task 1 — Add SPECIES_DIALOG_IMAGE_SIZE constant + TDD test
**Commit:** ded3720
**Message:** shipyard(phase-3): add SPECIES_DIALOG_IMAGE_SIZE constant and test

- Wrote failing test test_species_dialog_image_size_is_positive_int in
  tests/test_constants.py first (TDD). Test failed with ImportError as expected.
- Added SPECIES_DIALOG_IMAGE_SIZE = 200 to constants.py directly below BET_IMAGE_SIZE.
- Updated tests/test_constants.py import line to include SPECIES_DIALOG_IMAGE_SIZE.
- Verify command: pytest tests/test_constants.py -k species_dialog_image_size -q: 1 passed.
- Full suite: 77 passed (baseline 76 + 1 new test).

### Task 2 — Hoist layout to _TURTLE_GRID_LAYOUT, add _SNAKE_ROW_LAYOUT
**Commit:** b65bbc2
**Message:** shipyard(phase-3): hoist grid_layout to _TURTLE_GRID_LAYOUT, add _SNAKE_ROW_LAYOUT

- Promoted the local grid_layout variable inside get_user_bet() to module-level
  constant _TURTLE_GRID_LAYOUT in dialogs.py.
- Added sibling _SNAKE_ROW_LAYOUT = [("Shadow",1,0),("Ralph",1,1),("Anaconda",1,2)].
- Both placed directly after the import block, before get_user_bet.
- Extended from constants import to also import SNAKE_IMAGES, SPECIES, SPECIES_DIALOG_IMAGE_SIZE.
- Updated get_user_bet() body to iterate _TURTLE_GRID_LAYOUT instead of the removed local variable.
- Verify command passed: _TURTLE_GRID_LAYOUT[0][0] == Leonardo,
  _SNAKE_ROW_LAYOUT[0][0] == Shadow, len(_SNAKE_ROW_LAYOUT) == 3.
- Pure rename/extract — get_user_bet() behaviour unchanged. 77 tests green.

### Task 3 — Refactor get_user_bet() to get_user_bet(species) with if/elif dispatch
**Commit:** 07e4183
**Message:** shipyard(phase-3): refactor get_user_bet() -> get_user_bet(species) with if/elif dispatch

- Changed signature to get_user_bet(species).
- Reads bet_layout from SPECIES[species]["bet_layout"], species_names, species_images
  from the SPECIES dispatch table at the top of the function.
- dialog._bet_images = [] and make_cb closure defined before the if/elif so both
  branches share them (CONTEXT-3 G3 mitigation).
- if bet_layout == "grid_2x2": title "Turtle Racing", label "Which turtle do you think
  will win the race?", columnspan=2, uses _TURTLE_GRID_LAYOUT.
- elif bet_layout == "row_3": title "Snake Racing", label "Which snake do you think
  will win the race?", columnspan=3, uses _SNAKE_ROW_LAYOUT.
- else: raise ValueError(f"Unknown bet_layout: {bet_layout!r}").
- Image source is species_images[name] uniformly across both branches.
- Bet index: species_names.index(name) + 1 (1-based), same convention as before.
- Verify command: inspect.signature(dialogs.get_user_bet) parameters == ['species'] — passed.
- Full suite: 77 tests green.

---

## Files Modified

| File | Change |
|------|--------|
| constants.py | Added SPECIES_DIALOG_IMAGE_SIZE = 200 after BET_IMAGE_SIZE |
| tests/test_constants.py | Updated import line; added test_species_dialog_image_size_is_positive_int |
| dialogs.py | Extended imports; added _TURTLE_GRID_LAYOUT and _SNAKE_ROW_LAYOUT module-level; refactored get_user_bet to accept species parameter with internal if/elif dispatch |

main.py — NOT touched (intentional, see Issues Encountered below).

---

## Decisions Made

- TURTLE_NAMES retained in the dialogs.py import line even though the refactored
  get_user_bet no longer references it directly (uses SPECIES[species]["names"] instead).
  Left for now; PLAN-2.1 can remove it when touching the file again.
- make_cb closure hoisted before the if/elif (both branches use the same closure
  factory) — cleaner than duplicating it per branch.
- Function docstring added to get_user_bet(species) documenting the species arg,
  return value, and ValueError — not required by the plan but zero-cost and aids reviewer.

---

## Issues Encountered

None blocking.

### Intentional main.py runtime breakage (expected Wave-1 end state)

main.py line 34 still calls dialogs.get_user_bet() with no arguments. After the
Task 3 refactor this produces a TypeError at runtime:

  TypeError: get_user_bet() missing 1 required positional argument: 'species'

This is INTENTIONAL AND EXPECTED — the same mid-phase pattern used in Phase 2 Wave 1.
pytest stays green because no test exercises the dialog directly (Tk modal, not
unit-testable without a display). PLAN-2.1 (Wave 2) repairs the call site by wiring
species = dialogs.get_user_species() and passing it to get_user_bet(species).

---

## Verification Results

| Step | Command | Result |
|------|---------|--------|
| Baseline | pytest -q | 76 passed |
| Task 1 verify | pytest tests/test_constants.py -k species_dialog_image_size -q | 1 passed |
| Task 1 full | pytest -q | 77 passed |
| Task 2 verify | python -c "import dialogs; assert dialogs._TURTLE_GRID_LAYOUT[0][0] == 'Leonardo'; ..." | ok |
| Task 2 full | pytest -q | 77 passed |
| Task 3 verify | python -c "import dialogs, inspect; sig = ...; assert list(sig.parameters) == ['species']" | ok |
| Task 3 full | pytest -q | 77 passed |

pytest count delta: +1 (baseline 76 -> final 77).
