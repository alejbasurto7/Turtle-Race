# Build Summary: Plan 3.1

## Status: complete (manual smoke pending)

## Tasks Completed

### Task 1 -- Wire main.py to the new race.py API; fold in REVIEW-2.1 I2 fix

**I2 fix (race.py):** Moved the comment
`# Shape dispatch (shape_drawer sentinel) is Phase 4's concern.`
out of the `create_racers` docstring body (where it was a string literal)
and into the function body as a real `#` code comment. Zero semantic change;
fixes the docstring formatting issue flagged in REVIEW-2.1.

**main.py call-site updates (10 changes):**

1. Removed `from constants import TURTLE_COLORS` -- no replacement; `create_racers`
   reads SPECIES internally.
2. Reordered round-loop so `create_racers("turtles")` runs first (before any
   `draw_*` or `place_*` call that needs `len(racers)`). Resolves RESEARCH.md G7
   call-order gotcha.
3. `race.create_turtles(TURTLE_COLORS)` -> `race.create_racers("turtles")`
4. `race.place_turtles_on_track(turtles_list, track_name)` ->
   `race.place_racers_on_track(racers, track_name)`
5. `race.draw_start_line(track_name)` -> `race.draw_start_line(track_name, len(racers))`
6. `race.draw_finish_line(track_name)` -> `race.draw_finish_line(track_name, len(racers))`
7. `race.draw_boundary_stones(track_name)` ->
   `race.draw_boundary_stones(track_name, len(racers))`
8. `race.run_race(turtles_list, track_name, user_bet)` ->
   `race.run_race(racers, track_name, user_bet)`
9. `turtles_list[user_bet - 1]` -> `racers[user_bet - 1]`
10. `race.show_podium(turtles_list, ...)` / `race.announce_result(..., turtles_list)` ->
    `racers` throughout

`dialogs.get_user_bet()` call left untouched per plan constraint (Phase 3 scope).
`"turtles"` hardcoded per plan constraint (Phase 3 will replace with dialogs.get_user_species()).

### Task 2 -- Final automated verification suite

All automated checks ran and passed. Manual turtle-parity smoke is
PENDING_HUMAN_VERIFICATION (see Verification Results below).

## Files Modified

- `race.py` -- I2 fix: comment moved outside docstring
- `main.py` -- 10 call-site updates, import removal, call reorder
- `.shipyard/phases/2/results/SUMMARY-3.1.md` -- this file

## Commits

- `e036be0` -- `shipyard(phase-2): wire main.py to race.py API; fix I2 docstring comment`
  (staged: `main.py`, `race.py`)
- Task 2 commit: `main.py` + `SUMMARY-3.1.md` (staged file-specific)

## Decisions Made

1. I2 fix folded into Task 1's commit (same atomic commit as main.py wire-up) since
   REVIEW-2.1 explicitly said "fold into Wave 3's first commit."
2. The single N_LANES grep hit (`tests/test_tracks.py:38`) is a prose `#` comment
   documenting the constant's deletion -- not a live identifier usage. Pattern
   `N_LANES|turtles_list|create_turtles|place_turtles_on_track|tortuga` yields
   zero actual code usages across all `*.py` files.

## Issues Encountered

None. Changes were mechanical. main.py had exactly 10 stale call sites matching
RESEARCH.md Section 3 table.

## Verification Results

### Autonomously verified

| Check | Command | Result |
|-------|---------|--------|
| main.py parses | `python -c "import ast; ast.parse(open('main.py').read()); print('main.py parses')"` | PASS |
| No stale identifiers in main.py | grep turtles_list/create_turtles/place_turtles_on_track/TURTLE_COLORS main.py | 0 matches |
| create_racers("turtles") present | grep main.py | line 28 confirmed |
| Call order correct | read main.py | create_racers line 28, draw_boundary_stones line 29 |
| constants.N_LANES absent | `python -c "import constants; assert not hasattr(constants, 'N_LANES'); print('ok')"` | ok |
| Repo-wide legacy identifier grep | pattern across *.py | 0 code usages (1 prose comment, not code) |
| pytest (full suite) | `pytest` | 76/76 passed |
| pytest tests/test_tracks.py -v | all 64 tests | 64/64 passed |
| Baseline delta | 76 pre-task, 76 post-task | 0 regressions |

### PENDING_HUMAN_VERIFICATION -- Manual smoke

`python main.py` requires a display. This environment is non-interactive and cannot
launch the Turtle/Tk GUI. Alejandro must run the following manual smoke before
declaring Phase 2 complete:

**What to run:**
```powershell
python main.py
```

**What to verify on each of the 3 tracks (straight, rectangular, spiral):**

1. **Straight track**
   - Race launches with 4 turtles (Raphael=red4, Michaelangelo=DarkOrange,
     Leonardo=blue, Donatello=DarkMagenta)
   - Boundary stones visible as two parallel horizontal rows flanking the lanes
   - White start-line bar visible at left
   - Checkered finish bar visible at right
   - All 4 turtles race left-to-right; one crosses first
   - Podium appears with gold/silver/bronze medals on top-3 turtles
   - Win/loss announcement and smiley face appear
   - "Play again?" dialog works; selecting Yes loops back to track selection

2. **Rectangular track**
   - 4 turtles, staggered start positions (diagonal ladder)
   - Boundary stones form a rectangular border
   - Checkered finish bar at bottom
   - Race runs; all 4 turtles finish

3. **Spiral track**
   - 4 turtles with staggered spiral starts (outer lane has longest head-start)
   - Boundary stones follow spiral shape
   - Finish bar at center/origin
   - All 4 turtles spiral inward and finish

**Zero visual regression criterion:** Every visual element (colors, positions,
boundary stone layout, start/finish bars, podium, medals) must be indistinguishable
from the pre-Phase-2 master baseline on all 3 tracks.

**If any regression is observed:** Do NOT merge Phase 2 to master; open an issue.

## End State

- `pytest`: 76 passed, 0 failed (unchanged from Wave 2 baseline)
- `python main.py`: parseable; runtime requires manual smoke (PENDING_HUMAN_VERIFICATION)
- Repo-wide grep for legacy identifiers: 0 code usages
- `constants.N_LANES`: does not exist
- `race.create_racers`: exists, reads SPECIES, returns [{'name', 'color', 'o'}]
- `main.py`: calls `race.create_racers("turtles")` with hardcoded species (Phase 3 will replace)
- Phase 2 automated gate: CLOSED (all automated checks green)
- Phase 2 manual gate (CONTEXT-2.md Decision 6): PENDING human smoke on all 3 tracks
