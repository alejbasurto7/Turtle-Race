# Phase 5 Plan Critique — Feasibility Stress Test

## Verdict: **READY** (with one expanded scope note for CLAUDE.md)

Plans are feasible against the actual codebase. Pytest baseline confirmed at 84 (CONTEXT-5's assumption holds; Anaconda test brings it to 85). One small expansion noted: CLAUDE.md has **two** drifts, not one — the plan should fix both.

## File existence

All referenced files exist:
- `.gitignore`, `tests/test_race.py`, `race.py`, `CLAUDE.md`, `.shipyard/PROJECT.md`, `turtle_race.spec` ✓
- `SHIP-NOTES.md` correctly does NOT exist (Phase 5 creates it)

## API surface accuracy

- `race.py:215` is `def create_racers(species: str):` ✓
- `tests/test_race.py:21` has `SNAKE_UNIT_SIZE = 20` ✓
- `tests/test_race.py:86-107` has Shadow + Ralph tests ✓
- `.shipyard/PROJECT.md:129` is `## Open Items` ✓
- `pytest --collect-only` shows 84 tests collected → Anaconda makes 85 (CONTEXT-5 target matches)

## CLAUDE.md drift — TWO issues, not one

RESEARCH §7 flagged 1 issue (the "9 units long" claim). Closer reading reveals **a second drift** also dating from Phase 4 commit `4fb207e`:

Current CLAUDE.md (the multi-paragraph section under "Shape dispatch and finish detection"):

> 1. "The `_SHAPE_UNIT_SIZE = 9` constant is calibrated for the classic shape and reused for the snake polygon (which is also 9 units long)"

→ **Wrong:** snake polygon is 20 units long now (Option 5 smooth-wave). The dict has `{"turtle": 9, "classic": 9, "snake": 20}`.

> 2. "snakes preserve their race-time `stretch_len` (so the 6:5:2 length ratio survives) and just bump width to `2.0` for visibility"

→ **Wrong:** the podium width was bumped from 2.0 → 3.0 in Phase 4 commit `4fb207e` ("Nokia-snake polygon, 2x bigger, podium snakes stand on platform"). Current code in `race.py` `show_podium`: `turtle.shapesize(stretch_wid=3.0, stretch_len=current_stretch_len, outline=2)`.

**Additionally NOT documented in CLAUDE.md** (introduced in Phase 4 commit `b54c8d2`):

> 3. HEAD-at-start placement: `place_racers_on_track` and `run_race` now back the visual position up by `head_offset_arc` along heading so the racer's HEAD sits at the lane arc position. Helpers `_head_offset_arc_for(t)` and `_back_pos(...)` in `race.py`.

**Recommendation:** PLAN-1.1 Task 2 (CLAUDE.md fix) should address all THREE points — the two drifts (snake polygon length, podium width) AND add a brief note about HEAD-at-start placement. Roughly 2-3 sentences total.

This is a slight expansion of the original "fix line 62" scope but still trivial (paragraph-scale edit, not architectural).

## Verify commands runnable

- `pytest` ✓
- `git ls-files .gitignore` ✓
- `grep -rn "N_LANES\|turtles_list\|create_turtles\|place_turtles_on_track\|tortuga" --include="*.py" .` — current state returns only `tests/test_tracks.py:38` ✓
- `pyinstaller turtle_race.spec` — should work; `requirements.txt` doesn't list pyinstaller but it's a build-only tool typically installed separately. Builder should check `pyinstaller --version` first; if not available, document in SUMMARY.

## Wave ordering

- PLAN-1.1 (file edits) → PLAN-2.1 (verification) sequential. Correct — PLAN-2.1 needs Anaconda test in place to hit 85/85.
- Within PLAN-1.1's 3 tasks, files are disjoint:
  - Task 1: `.gitignore` + `tests/test_race.py` + `race.py` (docstring only)
  - Task 2: `.shipyard/PROJECT.md` + `CLAUDE.md`
  - Task 3: `SHIP-NOTES.md` (new file)
  - No conflicts.

## Hidden dependencies

None. PLAN-2.1's PyInstaller build depends on no Phase 5 file edits (turtle_race.spec is unchanged); it could technically run before PLAN-1.1. But sequential ordering keeps the test count target accurate.

## Complexity

- PLAN-1.1: 3 files modified + 1 created across 3 tasks. Low.
- PLAN-2.1: pure verification (no source modification). Low.

## PyInstaller environment

- `pyinstaller` is NOT in `requirements.txt`. Build-only tool, typically installed separately or via PyInstaller installer.
- If not installed in the user's venv, build fails immediately with "pyinstaller: command not found" or "ModuleNotFoundError: No module named PyInstaller". Per CONTEXT-5 Decision 3, builder should document the failure but not block Phase 5 close.
- If installed: UPX may or may not be on PATH. UPX-missing is a benign warning.

## Items to be aware of (not blocking)

1. **CLAUDE.md scope expansion** — addressed above; fold into PLAN-1.1 Task 2.
2. **`pyinstaller` not in requirements** — builder may need to install it (`pip install pyinstaller`) or note that it's not available. Either way, document.
3. **Pytest baseline 84 confirmed** — Anaconda test brings it to 85, matches CONTEXT-5 target.

## Summary

Phase 5 plans are READY. CLAUDE.md fix scope is slightly larger than the plan describes (2 drifts + 1 missing note vs. just 1 fix), but it's still a tiny paragraph-scale edit. Builder should fold the expanded scope into the existing Task 2 of PLAN-1.1. No structural changes needed to the plans themselves.
