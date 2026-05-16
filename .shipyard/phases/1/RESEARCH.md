# RESEARCH — Phase 1: Persistence + Scoring Core

Findings gathered during `/shipyard:plan 1` to inform the architect. The original researcher agent dispatch terminated before writing this file; findings below were gathered via direct Read/Grep against the source.

## 1. `paths.py` current shape

Full current contents (7 lines):

```python
import os
import sys


def resource_path(rel_path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)
```

**How `resource_path()` works:**
- In **source mode** (`python main.py`): `sys._MEIPASS` is unset → uses the directory of `paths.py` (= project root) as the base.
- In **frozen mode** (`dist/TurtleRace.exe`): `sys._MEIPASS` is set by the PyInstaller bootloader to the temporary unpack directory → returns paths under that temp dir.

**Where to add `user_data_path(filename)`:** below `resource_path()` is fine — order doesn't matter for the existing single user (`paths` is imported as a flat module). No existing convention to follow.

**Imports available without changes:** `os` and `sys` are already imported. `pathlib` would need to be added (recommended — `pathlib.Path` makes the `mkdir(parents=True, exist_ok=True)` ergonomic).

## 2. `race.run_race(...)` return signature

[race.py:357](race.py#L357):
```python
finish_order = []                            # lane indices in order of crossing the line
```

[race.py:386](race.py#L386):
```python
finish_order.append(i)   # i is a lane index (int)
```

[race.py:413](race.py#L413):
```python
return winning_turtle, finish_order
```

So `run_race` returns `(winning_turtle: Turtle, finish_order: list[int])`. `finish_order` is **a list of `int` lane indices** in the order the racers crossed the line. Length equals the number of racers (3 for snakes, 4 for turtles).

**Racer dict shape** ([race.py:266](race.py#L266)):
```python
racers.append({'name': name, 'color': color, 'o': t})
```

Per the function docstring ([race.py:241-249](race.py#L241-L249)):
- `'name'` — `str`, matches `SPECIES[species]["names"][i]`
- `'color'` — `str`, matches `SPECIES[species]["colors"][i]`
- `'o'` — `turtle.Turtle`

**Adapter from `finish_order` to name list** (for [main.py](main.py) in Phase 2):
```python
finish_order_names = [racers[i]['name'] for i in finish_order]
leaderboard.record_race(species, track_name, finish_order_names)
```

`species` is already a local variable in `main()` ([main.py:25-26](main.py#L25-L26) approx — see `dialogs.get_user_species()` callsite). `track_name` is in scope from [main.py:27](main.py#L27).

The architect should design `record_race(species: str, track: str, finish_order_names: list[str])` — taking names, not indices, so `leaderboard.py` never needs to know about racer dicts or `SPECIES`.

## 3. `tracks.py` track names

Canonical names ([tracks.py:27-31](tracks.py#L27-L31)):

```python
STRAIGHT = "straight"
RECTANGULAR = "rectangular"
SPIRAL = "spiral"

TRACK_NAMES = (STRAIGHT, RECTANGULAR, SPIRAL)
```

`track_name` originates at [main.py:27](main.py#L27): `track_name = dialogs.get_user_track()`. This returns one of `"straight" | "rectangular" | "spiral"` (lowercase string literals).

**Per CONTEXT-1.md Decision 5**, `leaderboard.py` MUST NOT import `tracks.TRACK_NAMES`. `known_tracks()` is derived from race history only.

## 4. Existing test conventions

Directory listing:

```
tests/
  __pycache__
  test_constants.py
  test_race.py
  test_tracks.py
```

No `conftest.py` exists. No shared fixtures defined.

**Style: pytest, not unittest.** [test_race.py](tests/test_race.py) uses module-level test functions (`def test_...`) and bare `assert`. No `unittest.TestCase` usage anywhere.

**`tmp_path` / `monkeypatch` usage:** none currently. This phase will be the first user of either. Both are pytest built-ins — no fixture import needed; just declare them as test-function parameters.

**Convention to follow** (per [test_race.py:1-18](tests/test_race.py#L1-L18)): tests reproduce formulas/logic inline rather than importing modules that would trigger Tk/`Screen()` setup. For `leaderboard.py` this is non-binding — the module is Tk-free by design, so direct import is fine.

**Confirm:** pytest is the test runner (per CLAUDE.md "Commands" section). It is not in `requirements.txt`; the user installs it separately.

## 5. Imports already in use — Tk poisoning check

Top-of-file imports from project-root modules (excluding the new `leaderboard.py`):

| File | Imports Tk transitively? | Top-level imports |
|---|---|---|
| `main.py` | **yes** (via `dialogs`) | `sys`, `audio`, `dialogs`, `race` |
| `race.py` | **yes** (`from turtle import ...`) | `math`, `random`, `time`, `turtle`, `PIL`, `tracks`, `constants`, `paths` |
| `dialogs.py` | **yes** (`import tkinter`) | `tkinter`, `tkinter.messagebox`, `PIL`, `tracks`, `constants` |
| `paths.py` | **no** | `os`, `sys` |
| `audio.py` | no | `glob`, `os`, `random`, `threading`, `time`, `pygame`, `paths` |
| `constants.py` | no | (none — pure data) |
| `tracks.py` | no | (verified — module is geometry math only) |

**Therefore `leaderboard.py` may safely import:** `paths` (for `user_data_path`). Anything else from this project would either be irrelevant or pull in Tk.

**Tk-free invariant verification recipe** (for the builder to use):
```bash
python -c "import sys; sys.modules['tkinter'] = None; import leaderboard"
```
If this command runs without error, no transitive Tk import exists.

## 6. `%APPDATA%` resolution

**No existing references** to `%APPDATA%`, `os.environ.get('APPDATA')`, `pathlib.Path.home()`, or `tempfile` in the project source. This is greenfield.

**Recommended approach for `user_data_path(filename)`:**

```python
def user_data_path(filename: str) -> str:
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

**Conventions chosen** (justify these in the plan/code comments):
- Windows: `%APPDATA%\TurtleRace\` (matches PROJECT.md success criterion 8).
- macOS: `~/Library/Application Support/TurtleRace/` (platform-idiomatic for app data).
- Linux/other: `$XDG_DATA_HOME/TurtleRace/`, falling back to `~/.local/share/TurtleRace/` (XDG Base Directory spec).

**Critical:** `sys._MEIPASS` must not appear in this function. Unlike `resource_path()`, `user_data_path()` is for *writable user state*, never for bundled resources. The architect's plan and builder's code must both make this explicit.

## 7. PyInstaller spec — current `datas=`

[turtle_race.spec:7](turtle_race.spec#L7):
```python
datas=[('lawn.jpg', '.'), ('assets/*.jpg', 'assets'), ('assets/*.mid', 'assets'),
       ('assets/midi/*.mid', 'assets/midi'), ('assets/*.png', 'assets'),
       ('assets/snakes/*.png', 'assets/snakes')]
```

All currently-bundled files are static assets under `lawn.jpg` or `assets/`. None of them are user-writable, none would collide with `leaderboard.json`. **No spec change is required for Phase 1.** Phase 5 (Polish) will revisit this.

## 8. Atomic write on Windows

Confirmed: `os.replace(src, dst)` is documented to be atomic on Windows (Python 3.3+) — it wraps `MoveFileEx` with `MOVEFILE_REPLACE_EXISTING`. Same-filesystem requirement holds, which is naturally satisfied if the temp file is created in the same directory as the target.

**Pattern for the architect to specify:**

```python
import tempfile, os, json

def _save(data: dict, target_path: str) -> None:
    target_dir = os.path.dirname(target_path) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".leaderboard.", suffix=".tmp", dir=target_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, target_path)   # atomic on Windows + POSIX
    except Exception:
        try: os.unlink(tmp_path)
        except OSError: pass
        raise
```

The temp file is created in the same directory as the target (mandatory for `os.replace` atomicity on Windows) and the dot-prefix hides it from casual `ls`.

## Summary

- `paths.py` is 7 lines; adding `user_data_path()` below `resource_path()` is straightforward, no Tk risk.
- `run_race` returns `finish_order: list[int]` (lane indices); name-string conversion is `[racers[i]['name'] for i in finish_order]`. `record_race` should accept names, not indices.
- Canonical track names are `"straight"`, `"rectangular"`, `"spiral"` (lowercase strings); `leaderboard.py` does not import them per CONTEXT-1.md Decision 5.
- Tests are pytest-style with `assert`; no `conftest.py` exists yet; `tmp_path` and `monkeypatch` are first-time uses.
- `paths.py` is Tk-clean and is the only project module `leaderboard.py` should import.
- No existing `%APPDATA%` or `tempfile` precedent — full pattern recommended above; macOS and Linux fallback paths chosen to be idiomatic.
- No `turtle_race.spec` change required in Phase 1.
- `os.replace` is the right primitive for atomic writes on both Windows and POSIX; temp file must live in the same directory as the target.
