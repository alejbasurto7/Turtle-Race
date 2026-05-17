---
phase: polish-and-ship
plan: 2.1
wave: 2
dependencies: [1.1]
must_haves:
  - New tools/smoke_phase_5.py — automated source-mode smoke for path-resolution + leaderboard file-lifecycle invariants
  - Sets os.environ["APPDATA"] to a tempfile.mkdtemp(prefix="turtlerace_phase5_smoke_") BEFORE any paths or leaderboard import (Phase 3/4 pattern)
  - Asserts paths.user_data_path("leaderboard.json") resolves to a path under the tempdir AND that the parent directory exists on demand
  - Drives a 2-race fixture (mixed species, different tracks) via leaderboard.record_race; verifies file appears on disk after the first record; JSON has schema_version=1 and a races list of length 2
  - Verifies leaderboard.reset_session() leaves the on-disk file present and byte-unchanged (only in-memory session clears)
  - Verifies leaderboard.reset_all() rewrites the file to exactly {"schema_version": 1, "races": []} (re-read the JSON to confirm)
  - Final PASS line — exactly "[smoke] phase 5 smoke PASS — path resolution + file lifecycle verified"
  - Exit non-zero with "[smoke] FAIL — <reason>" on any assertion failure
  - Mirrors the [smoke] log-prefix style and tmpdir-via-tempfile-mkdtemp pattern from smoke_phase_3 / smoke_phase_4
  - Does NOT call main.main(), does NOT monkeypatch dialogs — scope-limited to path/lifecycle invariants (smoke_phase_4 already covers the menu/round/leaderboard contract)
  - Per CONTEXT-5 Decision 6 — smoke_phase_5.py duplicates env-setup boilerplate from smoke_phase_4. NO tools/_smoke_common.py extraction
  - New tools/smoke_packaged.md — human-runnable checklist for the actual frozen exe, with PASS/FAIL boxes per step
  - Checklist sequence — pyinstaller build → first launch → race once → quit → grep JSON for race → re-launch → All-Time view shows race → Reset Session (file unchanged) → Reset All (file wiped to canonical shape)
  - Top-of-file note that this is the manual gate before any actual release; source-mode equivalents are in tools/smoke_phase_5.py; running both is the full Phase 5 smoke
  - Does NOT actually run pyinstaller from the builder — the checklist is a human gate
  - Does NOT touch dialogs.py, main.py, leaderboard.py, race.py, audio.py, paths.py, constants.py, tracks.py, tests/, or any other production code
  - pytest stays green (135 passed)
files_touched:
  - tools/smoke_phase_5.py
  - tools/smoke_packaged.md
tdd: false
risk: low
---

# PLAN 2.1 — Phase 5 smoke artifacts (automated source-mode + manual packaged-exe checklist)

## Context

Per [.shipyard/phases/5/CONTEXT-5.md](../CONTEXT-5.md) Decision 4, the Phase 5 packaged-exe smoke is split into TWO complementary artifacts:

- **`tools/smoke_phase_5.py`** — an **automated source-mode smoke** that verifies the path-resolution + file-lifecycle invariants. Specifically: `paths.user_data_path("leaderboard.json")` returns a path under the redirected `%APPDATA%` and creates the parent directory on demand; `leaderboard.record_race(...)` writes a JSON file with `schema_version: 1`; `reset_session()` leaves the file present and unchanged on disk; `reset_all()` rewrites the file to `{"schema_version": 1, "races": []}`. This is the automated half of the Phase 5 success criteria — it catches the `_MEIPASS`-style regression risk that the ROADMAP calls out without requiring a frozen build.

- **`tools/smoke_packaged.md`** — a **human-runnable checklist** for the actual `dist/TurtleRace.exe` produced by `pyinstaller turtle_race.spec`. This is the manual gate before any release. It includes PASS/FAIL boxes per step and references `tools/smoke_phase_5.py` as the automated complement.

**Scope split** (CONTEXT-5 Decision 4): `smoke_phase_5.py` is intentionally **narrower** than `smoke_phase_4.py`. It does NOT drive `main.main()`, does NOT monkeypatch dialogs, and does NOT exercise the menu/round/leaderboard UI contract — `tools/smoke_phase_4.py` already covers all of that. Phase 5's automated smoke targets specifically the writable-user-data path resolution and the leaderboard-file lifecycle.

**Duplication is allowed** (CONTEXT-5 Decision 6): the env-setup boilerplate (`tempfile.mkdtemp` + `os.environ["APPDATA"]` + `sys.path.insert`) is duplicated verbatim from `smoke_phase_4.py`. A `tools/_smoke_common.py` extraction was considered and deferred — the Phase 5 smoke's assertion shape is only ~50% overlapping with `smoke_phase_4.py` and Phase 5 is the LOW-risk capstone; the extraction can be done in a future maintenance pass.

This plan depends on Plan 1.1 only for ordering reasons (the CLAUDE.md addendum documents the invariants this smoke verifies, so the addendum lands first for commit-message clarity). The smoke itself reads only `paths` and `leaderboard` — both stable since Phase 1 — so there is no functional dependency on Plan 1.1's edits.

## Dependencies

- Plan 1.1 must be complete (CLAUDE.md addendum + turtle_race.spec comment are merged). This is a wave-ordering dependency, not a code dependency.

## Tasks

<task id="1" files="tools/smoke_phase_5.py, tools/smoke_packaged.md" tdd="false">
  <action>
Create BOTH files in the same atomic commit.

---

### A. `tools/smoke_phase_5.py`

A standalone Python script — no `pytest` collection (lives under `tools/`, not `tests/`). Structure mirrors `tools/smoke_phase_3.py` and `tools/smoke_phase_4.py`:

1. **Module docstring** (top of file) — describes the scope: path-resolution + leaderboard file-lifecycle invariants, NOT the menu/round/leaderboard UI contract (which `smoke_phase_4.py` already covers). Reference CONTEXT-5 Decision 4. Note that this is the automated half of the Phase 5 smoke; the manual half is `tools/smoke_packaged.md` and runs against `dist/TurtleRace.exe`.

2. **Imports** — `json`, `os`, `sys`, `tempfile` only (no third-party). Do NOT import `paths` or `leaderboard` at module scope.

3. **`main()` function** — entry point. The body:

   **Step 1 — env redirect BEFORE any paths/leaderboard import.**
   ```python
   tmpdir = tempfile.mkdtemp(prefix="turtlerace_phase5_smoke_")
   os.environ["APPDATA"] = tmpdir
   print(f"[smoke] redirected %APPDATA% to {tmpdir}")
   sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
   ```

   **Step 2 — import `paths` and `leaderboard` and assert path resolution.**
   - `data_path = paths.user_data_path("leaderboard.json")`
   - Assert `os.path.normpath(data_path).startswith(os.path.normpath(tmpdir))` — the resolved path lives under the redirected tempdir.
   - Assert `os.path.basename(data_path) == "leaderboard.json"`.
   - Assert `os.path.isdir(os.path.dirname(data_path))` — the parent directory was created on demand by `user_data_path()` (this is a hard invariant from Phase 1).
   - Assert NOT `os.path.exists(data_path)` yet — `user_data_path()` creates the parent dir but NOT the file; the file is only created by the first `record_race`.
   - Print `[smoke] path resolution OK: {data_path}`.

   **Step 3 — drive a 2-race fixture (mixed species, different tracks) via `leaderboard.record_race`.**
   - `leaderboard.record_race("turtles", "straight", ["Phil", "Bert", "Speedy", "Slowpoke"])` — finish order is illustrative; use names that match `constants.TURTLE_NAMES` if possible but the smoke does not import constants (Tk-free invariant) — any 4-string list works at the leaderboard layer. Use the canonical names: `["Phil", "Bert", "Speedy", "Slowpoke"]` or read them with a small local import inside the function if the architect prefers — see note below.
   - Assert `os.path.exists(data_path)` — the file appears on disk after the first record.
   - Re-read JSON: `with open(data_path, "r", encoding="utf-8") as f: data = json.load(f)`.
   - Assert `data["schema_version"] == 1` and `len(data["races"]) == 1`.
   - Print `[smoke] first record OK: 1 race, schema_version=1`.
   - `leaderboard.record_race("snakes", "spiral", ["Shadow", "Anaconda", "Ralph"])`.
   - Re-read JSON. Assert `len(data["races"]) == 2`. Assert the two records have the correct `species` and `track` fields in chronological insert order: races[0].species=="turtles" and races[0].track=="straight"; races[1].species=="snakes" and races[1].track=="spiral".
   - Print `[smoke] second record OK: 2 races on disk`.

   Architect note on racer names: the smoke can use ANY string list — `record_race` does not validate names against the constants module. Using the canonical names is informational only. If the builder prefers, the names can be `["A", "B", "C", "D"]` and `["X", "Y", "Z"]`; the invariants asserted by the smoke do not depend on name content.

   **Step 4 — `leaderboard.reset_session()` leaves the file present and unchanged.**
   - Capture pre-reset bytes: `before = open(data_path, "rb").read()`.
   - Capture pre-reset mtime: `mtime_before = os.path.getmtime(data_path)` (defensive — used only in the diagnostic message if the assertion fails).
   - Call `leaderboard.reset_session()`.
   - Assert `os.path.exists(data_path)` — file still there.
   - Capture post-reset bytes: `after = open(data_path, "rb").read()`.
   - Assert `before == after` — file is byte-identical (reset_session is in-memory-only per Phase 1 docs).
   - Re-read JSON and assert `len(data["races"]) == 2` (disk still has both races).
   - Also assert `leaderboard.query("session", "all", "all") == []` — in-memory session cleared as expected.
   - Print `[smoke] reset_session OK: file unchanged on disk ({len(before)} bytes), session emptied`.

   **Step 5 — `leaderboard.reset_all()` rewrites the file to the canonical empty store.**
   - Call `leaderboard.reset_all()`.
   - Assert `os.path.exists(data_path)` — file still there (reset_all rewrites, does not delete).
   - Re-read JSON: assert `data == {"schema_version": 1, "races": []}` — exact equality, not just structural.
   - Print `[smoke] reset_all OK: file rewritten to canonical empty store`.

   **Step 6 — final PASS line.**
   - Print exactly: `[smoke] phase 5 smoke PASS — path resolution + file lifecycle verified`.
   - Also print `[smoke] (tmpdir was {tmpdir}; leaderboard.json remains there for inspection)` for parity with smoke_phase_3/4.
   - `return` (don't `sys.exit(0)` — the implicit return is exit 0).

4. **Failure handling** — wrap each assertion in an explicit `if not <condition>:` block that prints `[smoke] FAIL — <reason>` to stdout and calls `sys.exit(1)`. Do NOT use `assert` statements (they're stripped by `python -O` and produce cryptic tracebacks). Use the same diagnostic style as `smoke_phase_4.py`'s `errors.append(...)` pattern, or — simpler given the smaller number of assertions — inline early `sys.exit(1)` per check. The architect's recommendation is the inline early-exit style:
   ```python
   if not os.path.normpath(data_path).startswith(os.path.normpath(tmpdir)):
       print(f"[smoke] FAIL — user_data_path {data_path!r} not under tempdir {tmpdir!r}")
       sys.exit(1)
   ```

5. **`if __name__ == "__main__": main()`** at the bottom.

6. **Do NOT** import `dialogs`, `main`, `audio`, `tkinter`, `turtle`, `pygame`, `race`, `constants`, or `tracks`. The Tk-free invariant from CLAUDE.md (preserved by Plan 1.1's addendum) means `import leaderboard` succeeds without any of those — and the Phase 5 smoke MUST exercise that invariant.

7. **Do NOT** call `leaderboard.record_race` more than twice — the fixture is intentionally minimal. The goal is path-resolution + file-lifecycle correctness, not stress testing.

---

### B. `tools/smoke_packaged.md`

A Markdown checklist for the actual frozen-exe smoke run. Top-of-file note + step-by-step PASS/FAIL gates. Structure:

1. **Top-of-file callout** — a short paragraph stating: "This is the manual gate before any actual release. The automated source-mode equivalents are in `tools/smoke_phase_5.py` — running both is the full Phase 5 smoke. This checklist requires a Windows host with PyInstaller installed and write access to `%APPDATA%\\TurtleRace\\`."

2. **Pre-flight checklist** — confirm `pyinstaller` is installed, confirm `python tools/smoke_phase_5.py` passes BEFORE building the exe (catches source-mode regressions before wasting a build cycle), confirm `pytest -q` reports 135 passed.

3. **Step-by-step checklist** with PASS/FAIL boxes (use `- [ ]` markdown checkboxes). Each step is one user action + one verification line. Sequence:

   - **Step 1 — Clean previous build.**
     Action: Delete `build/` and `dist/` directories (PowerShell: `Remove-Item -Recurse -Force build, dist` — ignore-missing).
     Verify: `dist/` does not exist; `build/` does not exist.
     `- [ ] PASS  - [ ] FAIL`

   - **Step 2 — Build the exe.**
     Action: Run `pyinstaller turtle_race.spec` from the project root.
     Verify: command exits 0; `dist/TurtleRace.exe` exists and is executable.
     `- [ ] PASS  - [ ] FAIL`

   - **Step 3 — Optional but recommended — wipe stale leaderboard state.**
     Action: `Remove-Item "$env:APPDATA\TurtleRace\leaderboard.json"` (ignore-missing, to make later assertions deterministic).
     Verify: `Test-Path "$env:APPDATA\TurtleRace\leaderboard.json"` returns `False`.
     `- [ ] PASS  - [ ] FAIL`

   - **Step 4 — First launch.**
     Action: Double-click `dist/TurtleRace.exe` (or run from PowerShell: `.\dist\TurtleRace.exe`).
     Verify: Main menu opens (Race / View Leaderboard / Quit); background music plays.
     `- [ ] PASS  - [ ] FAIL`

   - **Step 5 — Race once.**
     Action: From the menu choose Race → pick any track → pick any species → pick any bet → wait for the race to complete → on the post-race prompt choose Quit.
     Verify: The app exits cleanly (window closes, no error dialog).
     `- [ ] PASS  - [ ] FAIL`

   - **Step 6 — Verify the JSON file appeared with the race.**
     Action: In PowerShell, open `"$env:APPDATA\TurtleRace\leaderboard.json"` in a text editor (or `Get-Content`).
     Verify: File exists; contains `"schema_version": 1`; `"races"` is a list with exactly 1 entry whose `species`, `track`, and `finish_order` match the race you just ran.
     `- [ ] PASS  - [ ] FAIL`

   - **Step 7 — Re-launch and confirm All-Time view shows the race.**
     Action: Run `.\dist\TurtleRace.exe` again. From the menu choose View Leaderboard.
     Verify: With filters at their defaults (Time=All Time, Species=All, Track=All Tracks, Group by=None), the Treeview shows at least one row corresponding to the racer that won Step 5. The "Current Session" filter would be empty (because this is a fresh launch — that's the `_MEIPASS` regression canary).
     `- [ ] PASS  - [ ] FAIL`

   - **Step 8 — Reset Session leaves the file unchanged on disk.**
     Action: Click Reset Session → click Yes on the confirmation dialog.
     Verify: The Treeview empties for Time=Current Session (already empty since fresh launch — confirm it stays empty). Switch Time to All Time: the historic row from Step 6 IS STILL PRESENT. Open the JSON file again in a text editor: it is unchanged (still 1 race, same content).
     `- [ ] PASS  - [ ] FAIL`

   - **Step 9 — Reset All wipes the file to canonical empty.**
     Action: Click Reset All → click Yes on the confirmation dialog.
     Verify: The Treeview is empty for every Time filter (including All Time). Open the JSON file: it now reads exactly `{"schema_version": 1, "races": []}` (or the equivalent pretty-printed form — verify by content, not byte equality).
     `- [ ] PASS  - [ ] FAIL`

   - **Step 10 — Final exit.**
     Action: Close the leaderboard → choose Quit from the main menu.
     Verify: App exits cleanly.
     `- [ ] PASS  - [ ] FAIL`

4. **Sign-off line** at the bottom: "Tested by: ________   Date: ________   Build: dist/TurtleRace.exe sha256: ________"

Format the file as standard GitHub-flavored Markdown. The PASS/FAIL boxes use `- [ ]` syntax so the checklist can be checked off in a Markdown viewer or filled in via text edit.

Do NOT actually run `pyinstaller turtle_race.spec` from the builder. This checklist is a human-run artifact — the builder commits the file but does not execute any step beyond Step 1.5 of the pre-flight (`python tools/smoke_phase_5.py` IS run by the builder per the verify command below).

Do NOT modify any other file — no edits to `dialogs.py`, `main.py`, `leaderboard.py`, `paths.py`, `race.py`, `audio.py`, `constants.py`, `tracks.py`, `tests/`, `tools/smoke_phase_3.py`, or `tools/smoke_phase_4.py`. Phase 5 is docs + smoke only.
  </action>
  <verify>python tools/smoke_phase_5.py ; pytest -q</verify>
  <done>`python tools/smoke_phase_5.py` exits 0 and prints `[smoke] phase 5 smoke PASS — path resolution + file lifecycle verified` as its final substantive line. `pytest -q` reports `135 passed` (the smoke is not part of pytest collection — it lives under `tools/`, not `tests/`). `tools/smoke_packaged.md` exists and contains the full 10-step checklist. `grep -cE "phase 5 smoke PASS" tools/smoke_phase_5.py` returns >= 1. `grep -cE "tempfile\.mkdtemp\(prefix=\"turtlerace_phase5_smoke_\"\)" tools/smoke_phase_5.py` returns 1. `grep -cE "os\.environ\[\"APPDATA\"\]" tools/smoke_phase_5.py` returns >= 1 (env redirect present). `grep -cE "leaderboard\.record_race" tools/smoke_phase_5.py` returns 2 (exactly two record_race calls — the two-race fixture). `grep -cE "leaderboard\.reset_session" tools/smoke_phase_5.py` returns >= 1. `grep -cE "leaderboard\.reset_all" tools/smoke_phase_5.py` returns >= 1. `grep -cE "import dialogs|import main|import tkinter|import turtle|import pygame|import audio|import race|import constants|import tracks" tools/smoke_phase_5.py` returns 0 (Tk-free invariant preserved — the smoke must NOT import any Tk-touching module). `test -f tools/smoke_packaged.md` succeeds. `grep -cE "pyinstaller turtle_race.spec" tools/smoke_packaged.md` returns >= 1. `grep -cE "Reset Session|Reset All" tools/smoke_packaged.md` returns >= 2. `grep -cE "\- \[ \]" tools/smoke_packaged.md` returns >= 10 (PASS/FAIL boxes present for each step). `grep -cE "smoke_phase_5\.py" tools/smoke_packaged.md` returns >= 1 (cross-reference present).</done>
</task>

## Acceptance Criteria

- `tools/smoke_phase_5.py` exists, follows the `[smoke]` log-prefix style and `tempfile.mkdtemp` env-redirect pattern from `tools/smoke_phase_3.py` and `tools/smoke_phase_4.py`, and exits 0 when run from the project root.
- The smoke verifies all four invariants from CONTEXT-5 Decision 4: (1) `user_data_path` resolves under the redirected `%APPDATA%` tempdir AND creates the parent directory on demand; (2) `record_race` produces a JSON file with `schema_version: 1` and the correct race count; (3) `reset_session` leaves the file byte-identical on disk; (4) `reset_all` rewrites the file to exactly `{"schema_version": 1, "races": []}`.
- The smoke does NOT import any Tk-touching module (`dialogs`, `main`, `audio`, `tkinter`, `turtle`, `pygame`, `race`, `constants`, `tracks`) — preserving the Tk-free invariant documented in Plan 1.1's CLAUDE.md addendum.
- The smoke does NOT call `main.main()` and does NOT monkeypatch dialogs — scope-limited to path/lifecycle invariants per CONTEXT-5 Decision 4.
- `tools/smoke_packaged.md` exists, contains the 10-step manual checklist with PASS/FAIL boxes, references `tools/smoke_phase_5.py` as the automated complement, and includes a top-of-file note that this is the manual gate before any actual release.
- The checklist does NOT instruct the builder to run `pyinstaller turtle_race.spec` — that step is for the human running the release gate.
- No production code is modified — `dialogs.py`, `main.py`, `leaderboard.py`, `paths.py`, `race.py`, `audio.py`, `constants.py`, `tracks.py`, and all of `tests/` are untouched.
- `tools/smoke_phase_3.py` and `tools/smoke_phase_4.py` are not modified.
- `pytest -q` reports 135 passed.

## Verification

```powershell
python tools/smoke_phase_5.py     # exits 0, prints "[smoke] phase 5 smoke PASS — path resolution + file lifecycle verified"
pytest -q                         # 135 passed

# Source-mode smoke shape and contract surfaces
grep -cE "phase 5 smoke PASS" tools/smoke_phase_5.py                  # >= 1
grep -cE "tempfile\.mkdtemp" tools/smoke_phase_5.py                   # >= 1
grep -cE "os\.environ\[.APPDATA.\]" tools/smoke_phase_5.py            # >= 1
grep -cE "paths\.user_data_path" tools/smoke_phase_5.py               # >= 1
grep -cE "leaderboard\.record_race" tools/smoke_phase_5.py            # exactly 2 (two-race fixture)
grep -cE "leaderboard\.reset_session" tools/smoke_phase_5.py          # >= 1
grep -cE "leaderboard\.reset_all" tools/smoke_phase_5.py              # >= 1
grep -cE "schema_version" tools/smoke_phase_5.py                      # >= 1

# Tk-free invariant — the smoke must NOT import any Tk-touching module
grep -cE "^import dialogs|^import main|^import tkinter|^import turtle|^import pygame|^import audio|^import race|^import constants|^import tracks" tools/smoke_phase_5.py
                                                                       # 0

# Manual checklist
Test-Path tools/smoke_packaged.md                                      # True
grep -cE "pyinstaller turtle_race.spec" tools/smoke_packaged.md        # >= 1
grep -cE "Reset Session" tools/smoke_packaged.md                       # >= 1
grep -cE "Reset All" tools/smoke_packaged.md                           # >= 1
grep -cE "smoke_phase_5\.py" tools/smoke_packaged.md                   # >= 1 (cross-reference)
grep -cE "\- \[ \]" tools/smoke_packaged.md                            # >= 10 (PASS/FAIL boxes)
```

The orchestrator runs `python tools/smoke_phase_5.py` after the builder finishes; the builder's environment runs it directly (no display required — the smoke is fully headless). `tools/smoke_packaged.md` is committed for the human to run before any actual release.
