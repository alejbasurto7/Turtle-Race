# CONCERNS.md

## Overview

Turtle Race is a small, single-process desktop game with a low security surface area. The concerns that matter here are maintainability traps and brittleness in the invariants that hold the game together — things that would silently break under routine changes. There are no critical issues; the most actionable items are medium-severity debt around dead code, verbose debug output, and a positional-identity coupling that is easy to violate.

## Metrics

| Metric | Value |
|--------|-------|
| Source files (project, excluding .venv) | 7 (main.py, race.py, dialogs.py, tracks.py, audio.py, paths.py, constants.py) |
| Test files | 2 (test_constants.py, test_tracks.py) |
| TODO / FIXME / HACK in project source | 0 |
| Commented-out dead constants | 1 (WINDOW_WIDTH = 2550 in constants.py) |
| Debug `print()` calls left in production path | 9 (race.py lines 176-231, 353-356) |
| Assets listed in datas= (spec) | 4 glob patterns covering all current asset types |
| Hardcoded secrets | 0 |

---

## Findings

### Dead Code

- **Vestigial `cheat_mode` branch**: CLAUDE.md explicitly flags that `get_user_input()` "always returns `cheat_mode=False`" and describes a `cheat_mode` branch as vestigial. However, `get_user_input()` is **not present anywhere in the current source** — it was already removed. The `cheat_mode` variable is not referenced anywhere. The concern in CLAUDE.md predates the cleanup; the dead code is already gone. The only surviving artefact is the CLAUDE.md documentation itself, which is now stale on this point.
  - Evidence: `main.py` (lines 1-51) — no `cheat_mode` or `get_user_input` call; `grep` across all project `.py` files returns zero matches.
  - Severity: **low** (already cleaned up; CLAUDE.md is just stale)

- **Commented-out wide-screen constant**: `WINDOW_WIDTH = 2550` is commented out directly above the live `WINDOW_WIDTH = 500`.
  - Evidence: `constants.py` lines 10-11
  - Severity: **low** — no runtime impact, but signals unfinished wide-screen work or an abandoned experiment.

### Debt

- **Debug `print()` logging throughout `run_race`**: Nine `print()` calls emit detailed race telemetry to stdout on every race — lane positions, path lengths, finish order, and result. These are useful during development but are never suppressed in production, including the packaged `.exe` (which sets `console=False` in the spec, so stdout is silently discarded anyway, making the prints pointless overhead in the frozen build).
  - Evidence: `race.py` lines 176-183 (race start table), 224-231 (race end table), 353-356 (win/loss message)
  - Evidence: `turtle_race.spec` line 29 (`console=False`)
  - Severity: **medium** — cosmetic in the packaged exe, but confusing for anyone running from source expecting a clean terminal.

- **Positional identity across three parallel lists**: `TURTLE_NAMES[i]`, `TURTLE_COLORS[i]`, and `TURTLE_IMAGES[name]` must stay in sync. The win-check in `main.py` uses `turtles_list[user_bet - 1]` (1-based index from the bet dialog) and `winning_turtle.pencolor()` to compare colors. A reorder of `TURTLE_NAMES` without a matching reorder of `TURTLE_COLORS` silently corrupts which turtle the user bet on.
  - Evidence: `constants.py` lines 8-24 (three separate data structures)
  - Evidence: `main.py` line 39 (`turtles_list[user_bet - 1]`)
  - Evidence: `dialogs.py` line 40 (`idx = TURTLE_NAMES.index(name)`)
  - Mitigation present: `tests/test_constants.py` lines 10-13 enforce that `TURTLE_IMAGES.keys() == set(TURTLE_NAMES)`, but this does not catch a `TURTLE_COLORS` reorder.
  - Severity: **medium** — silent wrong behavior, not a crash; only triggered by editing `constants.py`.

- **Bet dialog grid layout is decoupled from `TURTLE_NAMES` order**: The 2×2 grid in `get_user_bet()` is hard-coded with position-based tuples (`("Leonardo", 1, 0)`, etc.) matching the `top_left`/`top_right`/etc. hints in asset filenames. Adding a fifth turtle or renaming a turtle requires edits in three places: `TURTLE_NAMES`, `TURTLE_IMAGES`, and the `grid_layout` list in `dialogs.py`.
  - Evidence: `dialogs.py` lines 29-34 (`grid_layout` hard-coded)
  - Evidence: `constants.py` lines 9, 19-24
  - Severity: **medium** — maintenance overhead when the turtle roster changes.

- **`SPEED_FACTOR` and `COAST_TICKS` are in-function magic numbers**: Both constants are defined inside `run_race()` with comments saying "tweak to taste" / "extra ticks". They affect race feel significantly but are invisible from `constants.py` where all other tuning knobs live.
  - Evidence: `race.py` lines 168 (`SPEED_FACTOR = 0.3`), 185 (`COAST_TICKS = 30`)
  - Severity: **low** — easy to find with comments, but inconsistent with the `constants.py` tuning convention.

- **Podium layout has its own embedded magic numbers**: `PODIUM_W`, `PODIUM_HEIGHTS`, `PODIUM_X`, `PODIUM_BASE_Y`, and `MEDAL_COLORS` are all defined inside `show_podium()` with no corresponding constants file entries.
  - Evidence: `race.py` lines 250-258
  - Severity: **low** — self-contained and unlikely to need tuning, but adds local noise to an already long function.

### Maintainability

- **PyInstaller `datas=` requires manual sync when adding assets**: Every new asset type (e.g., `.ogg`, `.gif`) must be added to the glob patterns in `turtle_race.spec` line 7. The current spec covers `*.jpg`, `*.mid`, `*.png`, and the root `lawn.jpg`. Nothing enforces this; the build silently succeeds but the frozen exe crashes at runtime for missing assets.
  - Evidence: `turtle_race.spec` line 7 (`datas=[('lawn.jpg', '.'), ('assets/*.jpg', 'assets'), ('assets/*.mid', 'assets'), ('assets/*.png', 'assets')]`)
  - Evidence: `paths.py` lines 5-7 (`resource_path()` pattern)
  - Severity: **medium** — silent failure mode that only surfaces in the packaged exe, not during source runs.

- **`PhotoImage` GC protection is a manual convention with no enforcement**: The pattern of stashing `PhotoImage` objects on the widget (`dialog._bet_images`, `canvas._bg_photo`) is correct but purely by convention. Forgetting it when adding a new image causes silent blank image bugs that are hard to diagnose.
  - Evidence: `dialogs.py` lines 37, 45 (`dialog._bet_images`)
  - Evidence: `race.py` line 62 (`canvas._bg_photo = bg`)
  - Evidence: `dialogs.py` lines 92 (`dialog._track_images`)
  - Severity: **low** — pattern is documented in CLAUDE.md; risk is only when adding new images.

- **`tracks.py` module-level mutable state (`_window_w`, `_window_h`)**: Window dimensions are set once via `set_window_size()` (called from `race.make_screen()`) and fall back to `constants.py` defaults for tests. This is functional but makes `tracks` an implicitly stateful module — tests that forget to call `set_window_size()` use the constants fallback silently, which may mask issues on non-standard screen sizes.
  - Evidence: `tracks.py` lines 41-42 (`_window_w`, `_window_h` module globals)
  - Evidence: `tracks.py` lines 45-48 (`set_window_size()`)
  - Severity: **low** — tests currently pass because the fallback values match the expected defaults.

### Performance

- **`time.sleep(TICK_DELAY)` blocks the main thread on every tick**: The race loop calls `time.sleep(0.01)` inside the Tk/turtle event thread. This prevents any Tk event processing (resize, close button) during the race. For a fullscreen game with a fixed race duration, this is acceptable, but it means the window is unresponsive to OS-level close events mid-race.
  - Evidence: `race.py` line 220 (`time.sleep(TICK_DELAY)`)
  - Evidence: `constants.py` line 17 (`TICK_DELAY = 0.01`)
  - Severity: **low** — expected trade-off for this game loop pattern; documented behavior.

- **New `Turtle()` objects accumulate across rounds**: `create_turtles()`, `draw_start_line()`, `draw_boundary_stones()`, `show_podium()`, `celebrate()`, and `announce_result()` all create new `Turtle` instances. On `screen.clear()` between rounds these are wiped, but within a single long session they all live until `clear()`. Not a leak per se (clear() does dispose them), but it means the turtle object count grows monotonically within a round.
  - Evidence: `race.py` lines 65-74 (`_draw_segment` creates a new `Turtle()`), 86-93, 135-139, 358-362
  - Severity: **low** — `screen.clear()` between rounds resets state; no cross-round accumulation.

### Security

This is a local desktop game with no network access, no user-generated data stored to disk, and no authentication. The security surface is effectively zero. No hardcoded secrets, credentials, or insecure defaults were found. The audio failure in `audio.py` is swallowed silently (acceptable for optional music). No security concerns warranting action.

---

## Summary Table

| Item | Category | Severity | Confidence |
|------|----------|----------|------------|
| CLAUDE.md stale on `cheat_mode` (code already removed) | dead-code | low | Observed |
| Commented-out `WINDOW_WIDTH = 2550` | dead-code | low | Observed |
| 9 debug `print()` calls in `run_race` / `announce_result` | debt | medium | Observed |
| Positional coupling: TURTLE_NAMES / TURTLE_COLORS / TURTLE_IMAGES | maintainability | medium | Observed |
| `TURTLE_COLORS` reorder not caught by existing test | maintainability | medium | Observed |
| Hard-coded bet dialog grid layout decoupled from TURTLE_NAMES | maintainability | medium | Observed |
| `SPEED_FACTOR` / `COAST_TICKS` defined inside function, not in constants.py | debt | low | Observed |
| Podium magic numbers embedded in `show_podium()` | debt | low | Observed |
| PyInstaller datas= requires manual sync for new asset types | maintainability | medium | Observed |
| PhotoImage GC protection is convention-only | maintainability | low | Observed |
| `tracks.py` module-level mutable window state | maintainability | low | Observed |
| `time.sleep()` blocks Tk event thread during race | performance | low | Observed |
| New Turtle() objects per drawing call accumulate within a round | performance | low | Observed |
| No hardcoded secrets or network exposure | security | n/a | Observed |

## Open Questions

- The commented-out `WINDOW_WIDTH = 2550` suggests wide-screen / multi-monitor support was explored. Is that work still planned? If not, the comment should be removed.
- `SPEED_FACTOR = 0.3` ("tweak to taste") — is there an intended target race duration? Moving this to `constants.py` with a clear docstring would help future tuning.
- Tests cover geometry (`test_tracks.py`) and constants (`test_constants.py`) but nothing in `dialogs.py`, `race.py`, or `audio.py`. This is expected for a UI-heavy game, but worth noting for anyone planning to extend the game loop.
