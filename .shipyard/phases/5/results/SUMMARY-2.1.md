# Build Summary: Plan 2.1

## Status: complete

## Tasks Completed
- Task 1: Add automated smoke + manual packaged-exe checklist — complete — commit `298fce8` — files: `tools/smoke_phase_5.py` (NEW, 191 lines), `tools/smoke_packaged.md` (NEW, 140 lines)

## Files Modified
- `tools/smoke_phase_5.py` (NEW): Automated source-mode smoke for Phase 5. Tk-free (imports only `json`, `os`, `sys`, `tempfile`, `paths`, `leaderboard`). Entry point `main()` runs 6 steps in order:
  1. Env redirect: `os.environ["APPDATA"] = tmpdir` BEFORE any `paths`/`leaderboard` import.
  2. Path assertion: `paths.user_data_path("leaderboard.json")` resolves under tmpdir; parent dir auto-created; file not yet present.
  3. 2-race fixture: turtles/straight (4 racers) → snakes/spiral (3 racers) via `leaderboard.record_race(...)`. Verifies `schema_version == 1`, `len(races) == 2`, and the species/track fields in each race entry.
  4. `reset_session()` byte-equality check: capture file bytes before, call `leaderboard.reset_session()`, re-read bytes, assert byte-identical.
  5. `reset_all()` canonical-shape check: call `leaderboard.reset_all()`, re-read JSON, assert exact equality to `{"schema_version": 1, "races": []}`.
  6. Final PASS banner: `[smoke] phase 5 smoke PASS — path resolution + file lifecycle verified`.

  Uses inline `sys.exit(1)` early-exit pattern with `[smoke] FAIL — <reason>` diagnostic on any assertion failure. Mirrors the `[smoke]` log prefix and tempdir-via-`tempfile.mkdtemp` from `smoke_phase_3.py` / `smoke_phase_4.py`.
- `tools/smoke_packaged.md` (NEW): Human-runnable checklist for the packaged exe. 3-checkbox pre-flight section + 10-step manual sequence (`pyinstaller turtle_race.spec` → run `dist/TurtleRace.exe` → race once → quit → grep JSON → re-launch → All-Time view shows race → Reset Session unchanged → Reset All wipes → final exit), each with `- [ ] PASS  - [ ] FAIL` boxes. References `tools/smoke_phase_5.py` three times. Top-of-file note positions this as the manual release gate that complements the automated smoke.

## Decisions Made
- **Docstring phrasing to satisfy the Tk-free grep check.** The plan's `<done>` criterion runs `grep -cE "import dialogs|import main|import audio|..."` and expects 0 hits. A first draft of the smoke included a module-docstring sentence like "this smoke does not `import dialogs / main / ...`" — but the grep's lack of `^` anchor meant the word `import` immediately preceding any of those names would match. Rephrased the docstring to use slash-separated bare module names (`dialogs / main / audio / ...`) so no `import <module>` substring is ever present. Final grep count: 0.
- **`leaderboard.record_race` docstring reference removed.** A first draft mentioned `leaderboard.record_race()` in a docstring bullet, which would have pushed the `grep -cE "leaderboard\.record_race|..."` count to 3 instead of the required exactly-2 (one per fixture race). Rephrased the docstring bullet to `record_race()` (without the `leaderboard.` prefix). Final grep count: 2 (one per fixture race call).
- **Checklist has 13 boxes, not 10.** The plan required ≥10. Final structure: 3 pre-flight items + 10 step items × 2 boxes per step (PASS, FAIL) means 13 distinct `- [ ]` lines if you count each bullet line, OR 23 if you count individual `[ ]` markers. The grep counts lines containing `- [ ]`, so the requirement is comfortably met.

## Issues Encountered
- **`paths.user_data_path()` creates the parent directory eagerly.** It calls `os.makedirs(root, exist_ok=True)` before returning — so the `TurtleRace/` subdirectory exists immediately after the call, before any `record_race()` invocation. The smoke's Step 2 assertion `os.path.isdir(os.path.dirname(data_path))` passes by virtue of this eager creation, NOT lazy-after-record creation. Documented this behavior in the smoke's inline comments so a future reader doesn't misread the test as "directory created lazily by record_race."
- **`paths.user_data_path()` does NOT create the file.** Only `leaderboard.record_race()` creates the file (via `_save()` calling `_atomic_write_json`). The directory is pre-created (above), the file is lazy. Step 2's `not os.path.exists(data_path)` assertion verifies the file is absent immediately after path resolution but before any record.
- **`reset_session()` is purely in-memory.** It only calls `_SESSION_RACES.clear()` — zero disk I/O. The byte-equality check passes trivially because the OS never touches the file during this operation. Captured the file's mtime defensively for diagnostics only (not part of the assertion), in case a future `reset_session()` implementation ever touches disk.
- **`reset_all()` rewrites via the atomic-write path.** The JSON serialization may differ in indentation/whitespace from a hand-written empty store, but `json.load()` round-trips both forms back to the same Python dict, so `data == {"schema_version": 1, "races": []}` passes regardless of formatting.
- **Em-dash terminal rendering.** The `—` in the final PASS line renders as `�` in some Windows PowerShell terminal sessions (UTF-8 output encoding issue), but the string IS correctly encoded in the file. The smoke's grep verification check matches on the ASCII prefix `phase 5 smoke PASS` and does NOT depend on the em-dash. Confirmed: `[smoke] phase 5 smoke PASS � path resolution + file lifecycle verified` in the terminal is the SAME string `[smoke] phase 5 smoke PASS — path resolution + file lifecycle verified` in the file.

## Verification Results
- `python tools/smoke_phase_5.py` → exit 0. Final line: `[smoke] phase 5 smoke PASS — path resolution + file lifecycle verified`.
- `pytest -q` → **135 passed in 0.34s** at commit `298fce8` (unchanged — tools/ is not in pytest collection).
- All 15 plan verification checks pass per the plan's Verification section (grep counts on Tk-free invariant, exact-2 `record_race` calls, etc.).
- The CLAUDE.md addendum's forward reference to `tools/smoke_phase_5.py` (flagged as a minor finding in REVIEW-1.1.md) is now resolved — the referenced file exists.
- `tools/smoke_phase_3.py` and `tools/smoke_phase_4.py` untouched (carryover preserved).
- No production code modified (`dialogs.py`, `main.py`, `leaderboard.py`, `race.py`, `audio.py`, `paths.py`, `constants.py`, `tracks.py` all unchanged this commit).
- `tools/_smoke_common.py` was NOT created (CONTEXT-5 Decision 6 honored).

Phase 5 is functionally complete. The only remaining ship-time gate is a human running `tools/smoke_packaged.md` against a fresh `pyinstaller turtle_race.spec` build.
