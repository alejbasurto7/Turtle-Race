# Build Summary: Plan 1.1 (Phase 2)

## Status: complete

(Task 3 — manual race-run verification — was substituted by a no-GUI automated smoke test executed by the orchestrator. The plan's intent — three end-to-end race runs across both species producing the expected JSON state — is preserved; only the keyboard-driven part of the verification is replaced by canned dialog responses.)

## Tasks Completed

- **Task 1** — wire `leaderboard.record_race` into the round loop. Status: complete. Files: `main.py`. Commit: `86a0830`.
- **Task 2** — basename guard on `paths.user_data_path` + 2 tests (TDD). Status: complete. Files: `paths.py`, `tests/test_paths.py`. Commit: `afc3a89`.
- **Task 3** — manual race-run verification. **Substituted** by `tools/smoke_phase_2.py`, executed by the orchestrator. Result: PASS (3 races recorded with correct schema, species, track, and finish_order lengths).

## Files Modified

- **`main.py`** (+4 lines): added `import leaderboard` between `import dialogs` and `import race` (preserves alphabetical order in the project-internal import block); added 3 lines in the round body between `race.run_race(...)` and `user_won = ...` — the list-comprehension adapter `finish_order_names = [racers[i]['name'] for i in finish_order]`, the `leaderboard.record_race(species, track_name, finish_order_names)` call, and one blank separator. Zero deletions, zero modifications to existing lines.
- **`paths.py`** (+13 lines): added a 4-condition basename guard at the very top of `user_data_path()` body. Rejects (raises `ValueError`) any filename where `os.path.basename(filename) != filename`, OR filename is `"."` / `".."`, OR `os.sep in filename`, OR `os.altsep is not None and os.altsep in filename`. Error message uses `repr(filename)` so the offending input is visible. No other lines touched; `resource_path()` unchanged.
- **`tests/test_paths.py`** (+16 lines including the post-build linter touch-up to spacing): two new test functions under a `# --- Filename validation (Phase 2 basename guard) ---` banner. `test_user_data_path_rejects_path_separator` covers `"subdir/x.txt"` and `f"subdir{os.sep}x.txt"`. `test_user_data_path_rejects_parent_traversal` covers `"../evil"` and bare `".."`.
- **`tools/smoke_phase_2.py`** (new, ~110 lines): orchestrator-authored no-GUI smoke script (see "Decisions Made" below).

## Decisions Made

- **Task 3 substitution:** the plan's "manual verification" protocol required `python main.py` × 3 with keyboard interaction. The builder agent has no display and can't drive a Tk GUI. The orchestrator built a no-GUI substitute (`tools/smoke_phase_2.py`) that monkeypatches `dialogs.get_user_track`, `dialogs.get_user_species`, `dialogs.get_user_bet`, and `dialogs.ask_play_again` to return canned answers, silences `audio.start_background_music`, redirects `%APPDATA%` to a tempdir via `os.environ["APPDATA"]`, then calls `main.main()`. The Tk window opens and animates three races without user input. After the loop completes, the script reads the on-disk JSON and asserts schema_version, race count, species/track per round, and finish_order length per species. **End-to-end coverage equivalent to the manual protocol** — the wiring is exercised through the real `main()` round loop, the actual `race.run_race` returns the actual `finish_order`, and the real `record_race` writes to the real `paths.user_data_path`. The only thing skipped is the human looking at the screen.
- **Smoke script committed under `tools/`** (with `diagnose_audio.py` and the other one-off utilities). Not part of `pytest` because it requires a display, and the unit-test surface is already comprehensive (135 tests after Task 2). Available for re-use by Phase 3 if a similar no-GUI integration check is needed.
- **TDD discipline followed for Task 2:** tests appended first, confirmed red (2 failed, 9 passed), then guard added, tests passed. Documented in the Task 2 commit.

## Issues Encountered

- **Tk + display dependency** forced the Task 3 substitution. Not a true issue with the build — the constraint was anticipated upfront by the orchestrator (see the AskUserQuestion exchange at the start of this build). The chosen substitute exercises the same code path the manual protocol would have.
- **Linter touch-up to `tests/test_paths.py` after builder commit `afc3a89`.** A post-build linter normalized spacing/blank-line conventions in the new guard tests (lines 83–106). Intentional, non-substantive, no test behavior change. Already in the working tree.
- **No other surprises.** `import leaderboard` slotted alphabetically without issue. `paths.user_data_path("leaderboard.json")` continued to work after the guard was added (`basename` of a bare filename equals the filename; the guard short-circuits to the platform branching). Phase 1's 39 leaderboard tests stayed green.

## Verification Results

### Static checks
- `python -c "import main"` exits 0.
- `grep -c "record_race\|import leaderboard" main.py` → 2.
- `git diff cd2870f..afc3a89 -- main.py paths.py tests/test_paths.py` shows: `main.py` +4 / -0; `paths.py` +13 / -0; `tests/test_paths.py` +16 / -0 (16 including the linter touch-up). No other code files in this diff.

### Test suite
- `pytest tests/test_paths.py -q`: **11 passed** (9 existing + 2 new guard tests).
- `pytest -q` (full): **135 passed** (133 baseline after Phase 1 cleanup + 2 new).

### End-to-end smoke (Task 3 substitute)
Smoke script output (excerpt from `tools/smoke_phase_2.py` run on 2026-05-16):
```
[smoke] redirected %APPDATA% to C:\Users\T0226129\AppData\Local\Temp\1\turtlerace_smoke_0qnqumxf
[smoke] running main() for 3 rounds...
[smoke] main() returned
[smoke] inspecting C:\Users\T0226129\AppData\Local\Temp\1\turtlerace_smoke_0qnqumxf\TurtleRace\leaderboard.json
[smoke] schema_version = 1
[smoke] races count    = 3
[smoke]   race 1: ts='2026-05-16T22:30:22' species='turtles' track='straight'     finish_order=['Leonardo', 'Raphael', 'Michaelangelo', 'Donatello']
[smoke]   race 2: ts='2026-05-16T22:31:25' species='snakes'  track='spiral'       finish_order=['Ralph', 'Shadow', 'Anaconda']
[smoke]   race 3: ts='2026-05-16T22:31:54' species='turtles' track='rectangular'  finish_order=['Donatello', 'Michaelangelo', 'Raphael', 'Leonardo']
[smoke] PASS — all 3 races recorded with expected schema, species, track, and finish_order length
```

Cross-check vs. on-screen podium output (printed by `race.run_race`):
- Race 1 (turtles / straight): podium 1st Leonardo / 2nd Raphael / 3rd Michaelangelo / 4th Donatello — **matches `finish_order`**.
- Race 2 (snakes / spiral): podium 1st Ralph / 2nd Shadow / 3rd Anaconda — **matches `finish_order`**.
- Race 3 (turtles / rectangular): podium 1st Donatello / 2nd Michaelangelo / 3rd Raphael / 4th Leonardo — **matches `finish_order`**.

### Manual guard check
- `python -c "import paths; print(paths.user_data_path('leaderboard.json'))"` → prints a valid path under `TurtleRace`, exits 0.
- `python -c "import paths; paths.user_data_path('../evil')"` → exits non-zero with `ValueError: user_data_path requires a bare filename (no path separators or traversal), got: '../evil'`.

### Coverage of ROADMAP Phase 2 success criteria
All 8 criteria satisfied. The "single `record_race` call inserted in `main.py` between `run_race(...)` and `show_podium(...)`" check is verified by both static grep AND the smoke run (the smoke run's JSON is empty before main.main() and non-empty after — only the inserted `record_race` call could have produced that). The "after three races, the file lists exactly three races in chronological order" check is verified by the smoke output (race counts, ascending timestamps, species/track diversity).
