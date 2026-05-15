---
phase: 2-snakes-racer-mode
plan: 3.1
wave: 3
dependencies: [1.1, 2.1]
must_haves:
  - main.py call sites updated to use create_racers("turtles"), racers, place_racers_on_track, etc. per RESEARCH.md Section 3 table
  - draw_boundary_stones (and draw_start_line / draw_finish_line) calls reordered so create_racers runs first (so len(racers) is available)
  - TURTLE_COLORS import dropped from main.py (no replacement needed — create_racers reads SPECIES internally)
  - Final pytest green
  - Manual smoke: python main.py runs on all 3 tracks (straight, rectangular, spiral) with 4 turtles — zero visual regression vs. master baseline
  - Repo-wide grep for turtles_list / create_turtles / place_turtles_on_track / tortuga / N_LANES returns zero results across all *.py files
files_touched:
  - main.py
tdd: false
risk: low
---

# Plan 3.1 — Wire main.py to the new race.py API; turtle parity smoke

## Context

Plans 1.1 + 2.1 left the codebase in this state:
- tracks.py: fully N-parameterized; no N_LANES references.
- constants.py: N_LANES deleted.
- race.py: renamed (turtles_list → racers, etc.); `create_racers(species)` reads SPECIES.
- tests/test_tracks.py: extended with N=3 + N=4 parametrized geometry tests; all green.
- main.py: **broken** — still calls `race.create_turtles(TURTLE_COLORS)`, `race.place_turtles_on_track(...)`, etc., which no longer exist.

This plan is the closing wire-up. It is small (one file) but blocked on both prior waves. The big risk is **the manual visual smoke** — Phase 2's primary acceptance gate per CONTEXT-2.md Decision 6 ("zero visual regression vs. pre-Phase-2 baseline"). No automated visual diff exists per RESEARCH.md Gotcha G9.

**Call-order subtlety per RESEARCH.md G7:** Currently main.py calls `draw_boundary_stones(track_name)` on line 29, **before** `create_turtles` on line 30. After this plan, `draw_boundary_stones` needs `n`, so `create_racers` must move above `draw_boundary_stones`. The reorder is mechanical but must be explicit.

## Dependencies

- **Plan 1.1** — tracks.py and constants.py refactor.
- **Plan 2.1** — race.py refactor and rename. `create_racers` must exist before main.py can call it.

## Tasks

<task id="1" files="main.py" tdd="false">
  <action>Update main.py call sites per RESEARCH.md Section 3 table. Specifically:
(1) Remove `from constants import TURTLE_COLORS` on line 11 (RESEARCH.md Section 3, line 11). No replacement import needed in main.py — `create_racers("turtles")` reads SPECIES internally.
(2) Reorder the round-loop setup so create_racers runs before any of the draw_* calls that now need `n`. New order: `create_racers("turtles")` → `draw_boundary_stones(track_name, len(racers))` → `place_racers_on_track(racers, track_name)` → `draw_start_line(track_name, len(racers))` → `draw_finish_line(track_name, len(racers))`. Exact line positions per RESEARCH.md Section 3 table — move what was line 30 (the racers-creation) above what was line 29 (draw_boundary_stones).
(3) Replace `race.create_turtles(TURTLE_COLORS)` → `race.create_racers("turtles")`.
(4) Replace `race.place_turtles_on_track(turtles_list, track_name)` → `race.place_racers_on_track(racers, track_name)`.
(5) Replace `race.draw_start_line(track_name)` → `race.draw_start_line(track_name, len(racers))`.
(6) Replace `race.draw_finish_line(track_name)` → `race.draw_finish_line(track_name, len(racers))`.
(7) Replace `race.draw_boundary_stones(track_name)` → `race.draw_boundary_stones(track_name, len(racers))`.
(8) Replace `race.run_race(turtles_list, track_name, user_bet)` → `race.run_race(racers, track_name, user_bet)`.
(9) Replace any remaining `turtles_list` identifier with `racers` (RESEARCH.md table lists lines 37, 39, 40, 42 area).
(10) Leave `dialogs.get_user_bet()` call untouched — Phase 3 wires species into that dialog; Phase 2 keeps the existing signature. The bet is still a 1-based index into the (still 4-element) turtle name list.</action>
  <verify>python -c "import ast; ast.parse(open('main.py').read()); print('main.py parses')"</verify>
  <done>(1) main.py parses without SyntaxError. (2) `grep -n "turtles_list\|create_turtles\|place_turtles_on_track\|TURTLE_COLORS" main.py` returns zero matches. (3) `create_racers("turtles")` appears in main.py. (4) The setup-order in the round loop has `create_racers` before any `draw_*` or `place_*` call that needs `len(racers)`.</done>
</task>

<task id="2" files="main.py" tdd="false">
  <action>Run the final automated verification suite, then the manual turtle-parity smoke. (a) Run `pytest` — must be fully green. (b) Run `python -c "import constants; assert not hasattr(constants, 'N_LANES'); print('ok')"` — must print "ok". (c) Use the Grep tool with pattern `N_LANES|turtles_list|create_turtles|place_turtles_on_track|tortuga` and glob `*.py` — must return zero results across the entire repo. (d) Manual smoke: launch `python main.py`, pick the **straight** track, run a race to completion. Confirm 4 turtles, podium shows 3 winners, play-again works. Repeat for **rectangular** and **spiral** tracks. Compare each visually against pre-Phase-2 `master` baseline (or against the developer's memory — there is no automated visual diff per RESEARCH.md G9). Any visual difference is a regression and must be investigated before declaring Phase 2 complete. Note that `python main.py` requires a display — if running in a headless CI/agent environment, instruct the user to run this step locally and confirm before merging.</action>
  <verify>pytest</verify>
  <done>(1) `pytest` (full) green. (2) constants.N_LANES does not exist. (3) Repo-wide grep for the legacy identifiers returns zero results in all *.py files. (4) Manual smoke on all 3 tracks (straight, rectangular, spiral) completed by the human operator with zero visual regression confirmed. If the builder is non-interactive, this step is delegated to the human reviewer and explicitly called out in SUMMARY-3.1.md as "MANUAL SMOKE PENDING — human must verify on all 3 tracks before Phase 2 close". (5) SUMMARY-3.1.md written to .shipyard/phases/2/results/SUMMARY-3.1.md describing the wire-up and listing the smoke-test outcome (or pending status). (6) Commit made with `git add main.py .shipyard/phases/2/results/SUMMARY-3.1.md` (file-specific).</done>
</task>

## Verification

Run all of these at the close of the plan:

```powershell
pytest
pytest tests/test_tracks.py -v
python -c "import constants; print(hasattr(constants, 'N_LANES'))"   # expect False
python main.py   # MANUAL: race on each of straight, rectangular, spiral; confirm no visual regression
```

Repo-wide grep (use Grep tool, pattern is regex):

```
pattern="N_LANES|turtles_list|create_turtles|place_turtles_on_track|tortuga"
glob="*.py"
# Expect: zero matches across all *.py files in the repo
```

**Builder reminders (from Phase 1 retrospective):**

1. **Write `.shipyard/phases/2/results/SUMMARY-3.1.md` before returning.** Acceptance criterion in Task 2.
2. **Use file-specific `git add`** — do not `git add .`. Task 2's done criterion specifies the exact files.
3. **The manual smoke is the primary acceptance gate** for Phase 2 per CONTEXT-2.md Decision 6. If the builder cannot run `python main.py` (headless environment), the SUMMARY must explicitly flag the smoke as pending human verification — do not declare Phase 2 complete on automated tests alone.
