---
phase: snakes-racer-mode
plan: 1.2
wave: 1
dependencies: []
must_haves:
  - Remove unused TURTLE_NAMES and TURTLE_IMAGES imports from dialogs.py
  - Add the locked docstring to get_user_species() per CONTEXT-4 Decision 5 / RESEARCH.md §7b
  - Rename the inner `n` loop variable in tracks.py:_build_spiral_legs to `leg_i` (eliminates shadow of the outer N-lane parameter)
  - pytest stays green; manual import smoke of dialogs.py succeeds
files_touched:
  - dialogs.py
  - tracks.py
tdd: false
risk: low
---

# PLAN-1.2 — Cleanups: dialogs.py imports + docstring, tracks.py loop rename

## Context

Three small, fully-independent cleanups carried over from Phase 2/3 reviews. CONTEXT-4 Decision 5 bundles them into Phase 4 commits where the file is already in scope. None of them touch race.py, so this plan runs in Wave 1 in parallel with PLAN-1.1 (disjoint files: constants.py + tests/test_constants.py for 1.1; dialogs.py + tracks.py for 1.2).

Per RESEARCH.md §7a recommendation: drop `TURTLE_NAMES` and `TURTLE_IMAGES` from the dialogs.py import line. Do NOT add `SNAKE_NAMES` (it isn't referenced; importing creates a flake8 hit).

## Tasks

<task id="1" files="dialogs.py" tdd="false">
  <action>In dialogs.py: (a) Edit the import line `from constants import TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE, SPECIES, SPECIES_DIALOG_IMAGE_SIZE` to drop the unused `TURTLE_NAMES` and `TURTLE_IMAGES` names, leaving `from constants import BET_IMAGE_SIZE, SPECIES, SPECIES_DIALOG_IMAGE_SIZE`. Confirm via Grep that neither name is referenced anywhere else in dialogs.py. (b) Add the docstring to `get_user_species()` per RESEARCH.md §7b verbatim: triple-quoted block explaining modal/blocking behavior (`grab_set()` + `wait_window()`), the no-op WM_DELETE_WINDOW handler, and the return values (`"turtles"` or `"snakes"` as keys into `constants.SPECIES`).</action>
  <verify>python -c "import dialogs; help(dialogs.get_user_species)" && pytest</verify>
  <done>`python -c` import of dialogs succeeds with no NameError. `help(dialogs.get_user_species)` prints a docstring containing the words "Modal", "grab_set", and "turtles" / "snakes". Full pytest stays green.</done>
</task>

<task id="2" files="tracks.py" tdd="false">
  <action>In tracks.py: locate `_build_spiral_legs` (Grep for "def _build_spiral_legs"). Inside, find the inner loop `for n in range(max_legs):` (shadows the function's outer `n` lane-count parameter). Rename the loop variable to `leg_i` and update every reference inside the loop body (e.g., `pair_idx = n // 2` → `pair_idx = leg_i // 2`). Before committing, Grep inside the loop body to confirm no remaining reference to a bare `n` was supposed to refer to the OUTER `n` — if it does, leave it as `n` (the outer one); only the loop-counter references switch. After the rename, run the tracks geometry tests.</action>
  <verify>pytest tests/ -k "track or spiral or geometry" && pytest</verify>
  <done>The targeted pytest subset is green (no spiral geometry regressed). Full pytest is green. Grep for `\bn\b` inside `_build_spiral_legs` shows the only remaining `n` references are the outer-parameter (lane-count) usages.</done>
</task>

## Notes for the builder

- Tasks 1 and 2 touch DIFFERENT files (dialogs.py vs. tracks.py). Commit each task separately, each with file-specific `git add`.
- This plan is fully parallel with PLAN-1.1 (no shared files).
- Write SUMMARY-1.2.md to disk before returning.
