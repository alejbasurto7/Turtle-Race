# RESEARCH — Phase 2: Wire `record_race` into the round loop

This phase is small enough that the bulk of relevant findings already live in `.shipyard/phases/1/RESEARCH.md`. This file captures the few new specifics needed for the wiring change and the basename guard.

## 1. Current `main.py` shape and exact insertion point

Full file is 53 lines. The round loop body is `main.py:21-45`. Relevant subset around the insertion point:

```python
# main.py:36-45
user_bet = dialogs.get_user_bet(species)

winning_turtle, finish_order = race.run_race(racers, track_name, user_bet)

user_won = winning_turtle is racers[user_bet - 1]['o']
race.show_podium(racers, finish_order)
race.celebrate(winning_turtle, user_won, racers)
race.announce_result(winning_turtle, user_bet, racers)

keep_playing = dialogs.ask_play_again()
```

**Insertion point per CONTEXT-2 Decision 1:** between `main.py:38` (the `run_race` call) and `main.py:41` (the `show_podium` call). Specifically, insert two lines after line 38 and before line 40 (the `user_won` assignment is fine to stay where it is — it doesn't touch persistence). Resulting shape:

```python
winning_turtle, finish_order = race.run_race(racers, track_name, user_bet)

finish_order_names = [racers[i]['name'] for i in finish_order]
leaderboard.record_race(species, track_name, finish_order_names)

user_won = winning_turtle is racers[user_bet - 1]['o']
race.show_podium(racers, finish_order)
```

**Variables already in scope at the insertion point:**
- `racers` (list of `{'name', 'color', 'o'}` dicts) — assigned at `main.py:29`
- `track_name` (`"straight" | "rectangular" | "spiral"`) — assigned at `main.py:27`
- `species` (`"turtles" | "snakes"`) — assigned at `main.py:28`
- `finish_order` (`list[int]` of lane indices) — assigned at `main.py:38`

No new local variables required beyond `finish_order_names`.

## 2. Import block placement

Current `main.py:1-10`:

```python
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import audio
import dialogs
import race
```

The project-internal imports (`audio`, `dialogs`, `race`) are alphabetical. Per CONTEXT-2.md "Open Questions" recommendation, add `import leaderboard` between `import dialogs` and `import race`:

```python
import audio
import dialogs
import leaderboard
import race
```

## 3. `paths.user_data_path` current shape (for the basename guard)

Current implementation at `paths.py:10-27` (from Phase 1):

```python
def user_data_path(filename: str) -> str:
    # ... comment about _MEIPASS ...
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
        root = os.path.join(base, "TurtleRace")
    elif sys.platform == "darwin":
        root = os.path.expanduser("~/Library/Application Support/TurtleRace")
    else:
        root = os.path.join(
            os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share"),
            "TurtleRace",
        )
    os.makedirs(root, exist_ok=True)
    return os.path.join(root, filename)
```

**Guard insertion point:** the very top of the function body — before `os.makedirs` and before any path resolution. Reject inputs with separators or `..` outright; do not sanitize.

**Recommended implementation:**

```python
def user_data_path(filename: str) -> str:
    # Reject any filename that contains a directory separator or path traversal —
    # callers should pass a bare basename (e.g. "leaderboard.json"). Sanitization
    # is harder to reason about than rejection; reject and let the caller fix the call.
    if os.path.basename(filename) != filename or os.sep in filename or (os.altsep and os.altsep in filename):
        raise ValueError(f"user_data_path requires a bare filename (no path separators), got: {filename!r}")
    # ... rest unchanged ...
```

On Windows, `os.sep` is `"\\"` and `os.altsep` is `"/"` — checking both catches `"a/b"` and `"a\\b"`. On POSIX, `os.altsep` is `None` so the third clause short-circuits. The `os.path.basename(filename) != filename` check also catches embedded separators on the active platform but the explicit sep checks make the intent visible to readers.

**Note on the `..` case:** `os.path.basename("..")` returns `".."`, which IS equal to `".."`, so the basename comparison alone does NOT catch `".."`. The explicit `os.sep` checks don't catch it either (no separator in just `".."`). Add an explicit `..` rejection:

```python
if filename in ("", ".", "..") or os.path.basename(filename) != filename or ...
```

Or more thoroughly:

```python
if os.path.basename(filename) != filename:
    raise ValueError(...)
if filename in (".", "..") or filename.startswith(("..", ".\\", "./")):
    raise ValueError(...)
```

The architect should pick one shape. Recommendation: keep it simple — reject the two common attack patterns (`"../X"` and `"subdir/X"`) plus the literal `".."`. Over-validation creates its own readability burden.

## 4. Tests already touching `paths.user_data_path`

`tests/test_paths.py` (9 tests after Plan 1.1 + the hygiene fix). The new guard tests should append to this file under a banner like `# --- Filename validation (Phase 2 basename guard) ---` and follow the existing convention (per-file `sys.path.insert`, plain `def test_*`, no `conftest.py`).

**Required additions per CONTEXT-2 Decision 4:**
- `test_user_data_path_rejects_path_separator` — assert `pytest.raises(ValueError)` on input `"subdir/x.txt"` (and `"subdir\\x.txt"` on Windows via `os.sep`).
- `test_user_data_path_rejects_parent_traversal` — assert `pytest.raises(ValueError)` on input `"../evil"` and on bare `".."`.

Two test functions are sufficient. Existing 9 tests stay green.

## 5. Manual verification protocol for the wiring change

Per CONTEXT-2 Decision 3, the builder must run `python main.py` three times — at least one turtle race and one snake race. For each run:

1. Note the species selected, track selected, and the actual finishing order shown in the on-screen podium and announced winner.
2. After each run completes (i.e., after clicking "No" on `ask_play_again`), inspect `%APPDATA%\TurtleRace\leaderboard.json` and confirm:
   - Schema version is `1`.
   - The race count matches the number of runs so far.
   - The newest record's `species`, `track`, and `finish_order` match the run's observed ground truth.
   - Timestamps are in monotonically non-decreasing order.

The builder includes this evidence (file contents excerpt + ground-truth notes) in `SUMMARY-2.1.md` "Verification Results".

**Cleanup note:** After verification, the `%APPDATA%\TurtleRace\leaderboard.json` file remains on the dev machine. The builder may delete it before subsequent test runs to start fresh, but this is optional — Phase 4's reset functionality can also wipe it. Document if not deleted.

## 6. PyInstaller spec — confirmed no changes required

`turtle_race.spec` was last touched before Phase 1. The leaderboard file is generated at runtime, not bundled. No spec change in Phase 2.

## Summary

Phase 2 is mechanically the smallest phase in the roadmap:
- 2 lines added to `main.py` plus 1 new import.
- ~3 lines added to `paths.user_data_path` (the basename guard).
- 2 new tests in `tests/test_paths.py`.
- Manual race-run verification (3 runs).
- No new dependencies, no spec change, no UI change, no test infrastructure change.

The dependency from Phase 1 is direct: Phase 2 imports `leaderboard.record_race` (provided by Phase 1) and calls `paths.user_data_path` indirectly through it.
