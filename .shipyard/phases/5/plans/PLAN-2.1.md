---
phase: 5
plan: 2.1
wave: 2
dependencies: [1.1]
must_haves:
  - Full pytest suite passes 85/85 (84 baseline + 1 new Anaconda test)
  - Banned-identifier grep returns only the intentional comment in tests/test_tracks.py:38
  - `pyinstaller turtle_race.spec` exits 0 and produces dist/TurtleRace.exe (or failure is documented per CONTEXT-5)
files_touched: []
tdd: false
risk: medium
---

# PLAN-2.1 — Phase 5 verification gate (tests, grep, build)

Pure verification — no source edits. Runs the final regression sweep and the PyInstaller build pass. Depends on PLAN-1.1 because the Anaconda test must exist for the 85/85 target and `.gitignore` should be clean before build artifacts land.

Per CONTEXT-5 Decision 3, this is BUILD-ONLY — no frozen-exe runtime smoke. Per CONTEXT-5 builder reminder, if PyInstaller fails, document the failure in SUMMARY-2.1.md with the last 20 lines of build output but do NOT block Phase 5 close.

<task id="1" files="" tdd="false">
  <action>Run `pytest --collect-only -q` first to confirm collection count, then `pytest -q` to run the full suite. Expected: 85 passed (84 baseline + 1 new Anaconda test from PLAN-1.1). If count differs from 85, record the actual baseline-vs-final delta in SUMMARY-2.1.md but proceed (CONTEXT-5 §10 acknowledges the 84 baseline is assumed). No commit — verification only.</action>
  <verify>pytest -q</verify>
  <done>pytest exits 0. Total passed count is 85 (or documented delta if baseline was not exactly 84). `test_head_offset_arc_anaconda` appears in the output.</done>
</task>

<task id="2" files="" tdd="false">
  <action>Run the banned-identifier grep over Python files: `grep -rn "N_LANES\|turtles_list\|create_turtles\|place_turtles_on_track\|tortuga" --include="*.py" .` (use the Grep tool with pattern `N_LANES|turtles_list|create_turtles|place_turtles_on_track|tortuga`, type `py`, output_mode `content`). Expected: a single hit at `tests/test_tracks.py:38` (the intentional historical-comment from Phase 2). Any other hit is a regression and must be investigated before closing the phase. No commit — verification only.</action>
  <verify>grep -rn "N_LANES\|turtles_list\|create_turtles\|place_turtles_on_track\|tortuga" --include="*.py" .</verify>
  <done>Exactly one match returned: `tests/test_tracks.py:38`. No other matches anywhere in the tree.</done>
</task>

<task id="3" files="" tdd="false">
  <action>Run `pyinstaller turtle_race.spec` from the project root. Capture the exit code and the last ~20 lines of stdout/stderr. On success, confirm `dist/TurtleRace.exe` exists. On failure (or asset-missing warnings), record the tail of output in SUMMARY-2.1.md per CONTEXT-5 failure-handling guidance — do NOT block Phase 5 close. UPX-missing warnings are benign and may be ignored. No commit — `build/` and `dist/` are gitignored.</action>
  <verify>pyinstaller turtle_race.spec; test -f dist/TurtleRace.exe</verify>
  <done>PyInstaller exits 0 AND `dist/TurtleRace.exe` exists with no missing-asset warnings — OR — failure is documented in SUMMARY-2.1.md with the last 20 lines of build output and a note that spec/datas correctness was validated by inspection.</done>
</task>
