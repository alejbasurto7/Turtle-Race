---
phase: 3-snake-species
plan: 1.1
wave: 1
dependencies: []
must_haves:
  - SPECIES_DIALOG_IMAGE_SIZE = 200 added to constants.py
  - tests/test_constants.py asserts SPECIES_DIALOG_IMAGE_SIZE is a positive int
  - get_user_bet refactored to get_user_bet(species) with internal dispatch on SPECIES[species]["bet_layout"]
  - _TURTLE_GRID_LAYOUT and _SNAKE_ROW_LAYOUT module-level constants in dialogs.py
  - row_3 branch builds Shadow | Ralph | Anaconda buttons at BET_IMAGE_SIZE
  - pytest stays GREEN end-to-end (Tk dialogs not exercised by tests)
files_touched:
  - constants.py
  - tests/test_constants.py
  - dialogs.py
tdd: true
risk: medium
---

# PLAN-1.1 — `constants.py` constant + `get_user_bet(species)` refactor

## Context

Phase 3 Wave 1. Lays the species-aware foundation in `constants.py` and `dialogs.py` **without** touching `main.py`. After this plan, `main.py` still calls `dialogs.get_user_bet()` with no args, so runtime is broken (TypeError) — but `pytest` stays green because no test exercises the dialog signature. Wave 2 (PLAN-2.1) repairs runtime by wiring `main.py`.

This pattern (ship a refactor that breaks runtime mid-phase, fix it in the next plan) was used successfully in Phase 2.

CONTEXT-3 decisions in scope: 3 (internal dispatch), 4 (snake row layout at `BET_IMAGE_SIZE`), 7 (small constant test).

## Tasks

<task id="1" files="constants.py, tests/test_constants.py" tdd="true">
  <action>Add a TDD test `test_species_dialog_image_size_is_positive_int` to `tests/test_constants.py` mirroring the existing `test_bet_image_size_is_positive_int` (asserting `SPECIES_DIALOG_IMAGE_SIZE` is `int`, `> 0`, and `>= BET_IMAGE_SIZE` since the species choice should not be smaller than a bet button). Then add `SPECIES_DIALOG_IMAGE_SIZE = 200  # px, square — used by the species-selection dialog (composite images)` to `constants.py` directly below the existing `BET_IMAGE_SIZE = 140` line.</action>
  <verify>pytest tests/test_constants.py -k species_dialog_image_size -q</verify>
  <done>The new test passes. `python -c "from constants import SPECIES_DIALOG_IMAGE_SIZE; print(SPECIES_DIALOG_IMAGE_SIZE)"` prints `200`. Full `pytest -q` remains green (baseline + 1 = 77 if Phase 2 ended at 76).</done>
</task>

<task id="2" files="dialogs.py" tdd="false">
  <action>In `dialogs.py`, hoist the existing in-function `grid_layout` to a module-level constant named `_TURTLE_GRID_LAYOUT` (same `[(name, row, col), ...]` tuples in the same order: Leonardo (1,0), Donatello (1,1), Raphael (2,0), Michaelangelo (2,1)). Add a sibling `_SNAKE_ROW_LAYOUT = [("Shadow", 1, 0), ("Ralph", 1, 1), ("Anaconda", 1, 2)]`. Place both directly under the existing `from constants import ...` block (which must be extended to also import `SPECIES`, `SNAKE_NAMES`, `SNAKE_IMAGES`). Do not change behavior yet — `get_user_bet()` must still reference `_TURTLE_GRID_LAYOUT` and continue to work as before with no `species` argument. Commit as a pure rename/extract.</action>
  <verify>python -c "import dialogs; assert dialogs._TURTLE_GRID_LAYOUT[0][0] == 'Leonardo'; assert dialogs._SNAKE_ROW_LAYOUT[0][0] == 'Shadow'; assert len(dialogs._SNAKE_ROW_LAYOUT) == 3; print('ok')"</verify>
  <done>Both module-level layout constants exist with the correct entries. `get_user_bet` (still 0-arg) imports cleanly. `pytest -q` green.</done>
</task>

<task id="3" files="dialogs.py" tdd="false">
  <action>Refactor `get_user_bet()` to `get_user_bet(species)`. Inside, read `bet_layout = SPECIES[species]["bet_layout"]`, `species_names = SPECIES[species]["names"]`, `species_images = SPECIES[species]["images"]`. Branch:
- `if bet_layout == "grid_2x2"`: use `_TURTLE_GRID_LAYOUT`, dialog title `"Turtle Racing"`, label `"Which turtle do you think will win the race?"`, columnspan 2 on the label, button image source `species_images[name]` resized to `BET_IMAGE_SIZE`. Bet index = `species_names.index(name) + 1`.
- `elif bet_layout == "row_3"`: use `_SNAKE_ROW_LAYOUT`, dialog title `"Snake Racing"`, label `"Which snake do you think will win the race?"`, columnspan 3 on the label, same `BET_IMAGE_SIZE` resize, same image-ref retention pattern (`dialog._bet_images = []`), same `WM_DELETE_WINDOW` no-op, same centering, same `grab_set()` + `wait_window()`. Bet index = `species_names.index(name) + 1`.
- `else`: `raise ValueError(f"Unknown bet_layout: {bet_layout}")`.
Both branches return `selected[0]`. Keep total function under ~110 lines. Do NOT extract a helper (CONTEXT-3 Decision 2). Do NOT touch `main.py` in this task — runtime will be broken until PLAN-2.1; this is intentional and matches Phase 2's mid-phase pattern.</action>
  <verify>python -c "import dialogs, inspect; sig = inspect.signature(dialogs.get_user_bet); assert list(sig.parameters) == ['species'], sig; print('ok')" && pytest -q</verify>
  <done>`get_user_bet` accepts exactly one parameter named `species`. Importing `dialogs` raises no error. `pytest -q` is green. `python main.py` is expected to fail with `TypeError: get_user_bet() missing 1 required positional argument: 'species'` — that is the intended Wave-1 end state, repaired by PLAN-2.1.</done>
</task>

## Out of scope

- `get_user_species()` — PLAN-2.1.
- `main.py` wiring — PLAN-2.1.
- Composite image helper — PLAN-2.1.
- Manual smoke — PLAN-2.1.

## Reminders for the builder

1. Per-task atomic commits. Three tasks → three commits.
2. **File-specific `git add`** only (e.g., `git add constants.py tests/test_constants.py`). Never `git add .` or `-A`.
3. Write `SUMMARY-1.1.md` to `.shipyard/phases/3/summaries/` before returning. Include: tasks done, commit SHAs, pytest count delta, the deliberate `main.py` runtime breakage flag for Wave 2.
