# Build Summary: Plan 2.1

## Status: complete

## Tasks Completed
- Task 1: Add `tools/smoke_phase_4.py` (no-GUI end-to-end smoke for the Phase 4 leaderboard view) — complete — commit `62e821d` — files: tools/smoke_phase_4.py

## Files Modified
- `tools/smoke_phase_4.py` (NEW, 331 lines). Mirrors `smoke_phase_3.py`'s structural pattern:
  - Sets `os.environ["APPDATA"]` to a fresh `tempfile.mkdtemp(prefix="turtlerace_phase4_smoke_")` directory BEFORE any `paths` or `leaderboard` import.
  - Imports `dialogs` and `audio` immediately after; monkeypatches all six dialog callables (`get_main_menu_choice`, `show_leaderboard`, `get_user_track`, `get_user_species`, `get_user_bet`, `ask_play_again_choice`) plus both `audio` functions (`start_background_music`, `stop_background_music`) and `tkinter.messagebox.askyesno`.
  - Drives 3 rounds via iterators: `menu_choices = iter(["race", "leaderboard", "quit"])`, `post_race_choices = iter(["again", "again", "menu"])`, and a `rounds` list with `(turtles/straight/bet=1)`, `(snakes/spiral/bet=2)`, `(turtles/rectangular/bet=3)`.
  - `fake_show_leaderboard()` exercises all seven plan steps against the live `leaderboard` module without opening a Toplevel:
    - Steps 1–2: `query("all"/"session", "all", "all")` → asserts `len(rows) >= 6`.
    - Step 3: `query_per_track("all", "all")` → asserts the three planned tracks all appear and `min(rank) == 1` per track.
    - Step 4: `query("all", "all", "straight")` → asserts exactly 4 rows (the turtle round's 4 racers).
    - Step 5: `known_tracks()` → asserts `{"straight", "spiral", "rectangular"}`.
    - Step 6: `reset_session()` → asserts `query("session", "all", "all") == []` and `len(query("all", "all", "all")) >= 6` (historic survives).
    - Step 7: `reset_all()` → asserts `query("all", ...) == []`, `known_tracks() == []`, and the on-disk JSON equals `{"schema_version": 1, "races": []}`.
  - After `main.main()` returns, re-reads the on-disk JSON and asserts the empty-store shape; asserts `show_leaderboard_calls == 1`.
- `tools/smoke_phase_3.py`: **unchanged** (CONTEXT-4 Carryover).
- `dialogs.py`, `main.py`, `leaderboard.py`: **unchanged**.

## Decisions Made
- **Patched `dialogs.show_leaderboard` as a module attribute**, not a local alias. `main.main()` calls `dialogs.show_leaderboard()`, which resolves via attribute lookup on the `dialogs` module — so a local-name patch would leave the real function in place and the test would hang on `wait_window()`. This is the non-obvious gotcha PLAN-2.1's monkeypatch surface specifically called out.
- **Driver calls `leaderboard.*` directly** (not through GUI widget callbacks). PLAN-2.1 §Context settled this: replacing `show_leaderboard` with an API driver is more reliable than trying to thread the real Toplevel from a headless context.
- **`dialogs._FILTER_LABEL_TO_KEY` is read and logged** (printing all 11 entries) and validated for expected keys at the start of the driver. This provides a regression signal if Plan 1.1's translation dict drifts, without forcing the driver to use it for translation (the driver calls `leaderboard.query` with the enum values directly).
- **`tkinter.messagebox.askyesno` monkeypatched globally** before `main.main()` as a defensive net. The driver bypasses the GUI buttons and calls `reset_session()`/`reset_all()` directly, so `askyesno` never actually fires — but the global patch prevents any unforeseen code path from blocking on a native dialog.

## Issues Encountered
- **None blocking.** Smoke passed on first attempt with no source file changes.
- **Informational — query aggregation behavior:** `query("all", "all", "all")` returns 7 rows (not 11) because the API aggregates by racer name across all rounds — 4 turtles across 2 turtle races + 3 snakes across 1 snake race = 7 distinct racer entries. The plan's `>= 6` lower bound is correct and satisfied.
- **Informational — session vs all parity:** `query("session", ...)` returns the same 7 rows as `query("all", ...)` for a fresh smoke run. Correct: `record_race` writes to both `_SESSION_RACES` and disk atomically, so both views reflect the same 3 races with no double-counting.

## Verification Results
- `python tools/smoke_phase_4.py` → exit 0. Prints `[smoke] leaderboard driver PASS` and final `[smoke] PASS — 3 races recorded, all Phase 1 API contract surfaces verified (Group-by, Track-filter, reset_session, reset_all, known_tracks)`.
- `pytest -q` → **135 passed** (unchanged — smoke lives in `tools/`, not collected by pytest).
- `grep -nE "fake_show_leaderboard|_FILTER_LABEL_TO_KEY|reset_session|reset_all|query_per_track|known_tracks" tools/smoke_phase_4.py` → 37 hits (well above the `>= 6` plan lower bound).
- `grep -cE "^def show_leaderboard\b" dialogs.py` → 1 (Plan 1.1 invariant preserved).
- `dialogs.py`, `main.py`, `leaderboard.py` — confirmed unchanged via `git diff 79b082e HEAD -- dialogs.py main.py leaderboard.py` (empty).

All Plan 2.1 acceptance criteria met.
