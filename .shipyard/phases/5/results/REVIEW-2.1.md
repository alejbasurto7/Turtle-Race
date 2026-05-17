# Review: Plan 2.1

## Verdict: PASS

## Findings

### Critical
- None.

### Minor
- **Em-dash terminal rendering on Windows.** The smoke's final PASS banner contains an em-dash (`—`, U+2014) which renders as `�` in PowerShell's default code page (cp1252). The string IS correctly encoded in the source file (UTF-8) and the regression-grep check matches on the ASCII prefix `phase 5 smoke PASS` (not the em-dash), so this is purely a terminal-cosmetic issue. Documented in the builder's SUMMARY under "Issues Encountered." Could be replaced with `--` for cross-terminal consistency, but matches Phase 4's smoke style which uses an em-dash too. **Not blocking.**
- **Eager parent-dir creation in `paths.user_data_path()` is asserted but not deeply explained.** The smoke's Step 2 assertion `os.path.isdir(os.path.dirname(data_path))` passes because `paths.user_data_path` calls `os.makedirs(root, exist_ok=True)` BEFORE returning. The smoke comments capture this but a future reader of the plan + smoke pair might misread the test as proving "directory created lazily by record_race" when in fact it's eager-on-path-resolution. The smoke is correct; just a documentation nuance worth surfacing if anyone refactors `paths.user_data_path` to be lazy. Not actionable in Phase 5.
- **`smoke_packaged.md` could note the source-mode smoke is a hard prerequisite, not just a parallel artifact.** The checklist mentions `tools/smoke_phase_5.py` three times but stops short of saying "if `smoke_phase_5.py` fails on source, do NOT proceed to the packaged-exe smoke — the bug is upstream." Minor doc polish; the human running the checklist would likely infer this anyway.

### Positive
- **All six smoke steps land correctly and the assertions match the plan exactly:**
  1. Env redirect before any `paths`/`leaderboard` import: confirmed by reading source — `os.environ["APPDATA"] = tmpdir` is at the top of `main()`, before the `import paths` and `import leaderboard` lines.
  2. Path resolution under tmpdir: `paths.user_data_path("leaderboard.json")` returns a path with `tmpdir/TurtleRace/leaderboard.json`.
  3. 2-race fixture: turtle race on "straight" with 4 racer names, then snake race on "spiral" with 3 racer names. `len(races) == 2` after both records.
  4. `reset_session()` byte-equality: `before_bytes == after_bytes` (purely in-memory operation, no disk write).
  5. `reset_all()` canonical-shape: `data == {"schema_version": 1, "races": []}` exact equality after JSON re-read.
  6. PASS banner with the exact-prefix grep-match.
- **Tk-free invariant verified by grep:** `grep -cE "import tkinter|import dialogs|import main|import audio" tools/smoke_phase_5.py` → 0. No Tk imports anywhere, neither at module level nor inside the test functions. This is the load-bearing invariant the CLAUDE.md addendum specifically calls out, and the smoke proves it by example.
- **Plan's exact-2 invariant on `record_race`:** `grep -cE "leaderboard\.record_race" tools/smoke_phase_5.py` → 2. One call per fixture race. The builder's docstring rewording (avoiding `leaderboard.record_race` in prose to keep the count at exactly 2) is the right level of attention to grep-determinism.
- **Checklist has 13 `- [ ]` items**, comfortably above the plan's ≥10 floor. Covers the full sequence: pyinstaller build → first launch → race → quit → grep JSON → re-launch → All-Time view shows race → Reset Session (file present, unchanged) → Reset All (file wiped to canonical shape) → final exit. The PASS/FAIL bracketing pattern is unambiguous for a human to fill in.
- **Atomic single commit (`298fce8`)** containing both new files. Diff is purely additive — no modification to existing files. `git diff 20a9eb7 298fce8 --stat` shows exactly the two new files at +191 / +140 lines.
- **No production code touched.** Confirmed by `git diff 20a9eb7 298fce8` showing only `tools/smoke_phase_5.py` and `tools/smoke_packaged.md`. `dialogs.py`, `main.py`, `leaderboard.py`, `paths.py`, `audio.py`, `race.py`, `constants.py`, `tracks.py`, `tests/`, and the existing smokes `tools/smoke_phase_3.py` / `tools/smoke_phase_4.py` all unchanged.
- **No `_smoke_common.py` extraction**, per CONTEXT-5 Decision 6. Inline boilerplate duplication accepted as the explicit trade-off for keeping Phase 5's scope minimal.
- **No `pyinstaller` invocation** as part of the build pipeline, per CONTEXT-5 Decision 4. The manual checklist is the gate for the packaged exe; the build commit itself ships only the checklist + source-mode smoke.
- **Wave 1's open minor finding (forward reference to `tools/smoke_phase_5.py` in the CLAUDE.md addendum) is now resolved.** The referenced file exists at `298fce8`.
- **No regressions:** `pytest -q` reports 135 passed at HEAD. `python tools/smoke_phase_5.py` exits 0 with the expected PASS banner on every run tested. `python -c "import dialogs; import main; import leaderboard"` exits 0.

Plan 2.1 is complete and clean. Phase 5 is functionally done modulo the human-run packaged-exe checklist gate before any actual release. Proceed to phase verification.
