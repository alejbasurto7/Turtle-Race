# Build Summary: Plan 2.1

## Status: complete

## Tasks Completed
- Task 1: create `leaderboard.py` persistence layer + `record_race` — complete — files: `leaderboard.py` (commit `3814dd5`)
- Task 2: add `tests/test_leaderboard.py` with 9 persistence tests — complete — files: `tests/test_leaderboard.py` (commit `abc013e`)

## Files Modified
- **`leaderboard.py`** (new, ~113 lines): Tk-free, stdlib-only. Module-level constants (`POINTS = (6, 3, 1, 0)`, `SCHEMA_VERSION = 1`, `_FILENAME = "leaderboard.json"`) and `_SESSION_RACES: list[dict] = []`. Private helpers `_path()`, `_empty_store()`, `_atomic_write_json()`, `_quarantine_and_reset()`, `_load()`, `_save()`. Public `record_race(species, track, finish_order_names)`. Atomic write via `tempfile.mkstemp` + `os.replace`. Corrupt-file recovery renames to `.corrupt-{YYYYMMDDTHHMMSS}` sidecar, writes a fresh empty store, prints a one-line stderr warning, never raises.
- **`tests/test_leaderboard.py`** (new, ~163 lines): 9 tests under a `# --- Persistence + record_race ---` banner. Shared `lb` pytest fixture (`monkeypatch` + `tmp_path`) reusable by Plan 2.2.

## Decisions Made
- **Import style: `import paths`, NOT `from paths import user_data_path`.** Plan listed both as valid (noting `audio.py` uses the `from` form), but the `from`-import breaks the `lb` fixture — `monkeypatch.setattr("paths.user_data_path", ...)` only patches the attribute on the live `paths` module object; a `from`-import binds a local name that's never updated. With `import paths`, the helper `_path()` calls `paths.user_data_path(_FILENAME)` through the live module reference and the monkeypatch is observed on every call. This is the single most load-bearing implementation choice in this plan — the alternative produced 7 of 9 test failures.
- **Atomic-write crash test pattern.** Used `monkeypatch.setattr(os, "replace", boom_raiser)` AFTER the baseline `record_race` succeeds, so every subsequent `os.replace` raises. Originally tried a call-count gate, which was wrong because by the time the patch is applied the first write has already completed — the second `record_race`'s `_load()` reads a valid file without touching `os.replace`, so the first patched call is the actual `_save()` atomic swap.

## Issues Encountered
- **`from`-import / monkeypatch interaction** (described above). This is now solved in `leaderboard.py`, but the same trap will hit any future module that wants to be monkeypatch-able through a `paths.*` symbol. Worth a brief note in CLAUDE.md at Phase 5 ship time so the next contributor doesn't lose an hour to it.
- **`datetime.fromisoformat` on local-time strings:** confirmed working as expected on Python 3.10+ — accepts the no-suffix ISO format from `datetime.now().isoformat(timespec="seconds")` and round-trips correctly. No quirks.
- **`tempfile.mkstemp` + `os.replace` on Windows:** works without elevated permissions, atomicity guaranteed on the same filesystem (which is naturally satisfied because the temp file is created in the same dir as the target). No surprises.
- **Did NOT import `tracks` / `constants`:** confirmed by `grep -E "import tracks|import constants" leaderboard.py` returning nothing. The temptation was real (e.g., a thought of validating `track` against `TRACK_NAMES`), but per CONTEXT-1 Decision 5 the module stays history-only.

## Verification Results
- `pytest tests/test_leaderboard.py -q`: **9 passed** in ~0.05s.
- `pytest` (full suite): **103 passed** (94 baseline + 9 new).
- `python -c "import sys; sys.modules['tkinter'] = None; import leaderboard"` exits 0 — Tk-free import confirmed.
- `grep -n "tkinter\|turtle\|pygame\|PIL\|^import tracks\|^import constants\|from tracks\|from constants" leaderboard.py` returns no matches.
- Two atomic commits, one per task, both prefixed `shipyard(phase-1): ...`.
