# ARCHITECTURE.md

## Overview

Turtle Race is a single-process Windows desktop game built as a thin orchestration layer over three coexisting UI/audio runtimes: the standard-library `turtle` module (race animation), `tkinter` (modal dialogs), and `pygame.mixer` (MIDI background music). All three share the same OS process and the same underlying Tk root window. The outer `main()` function drives a round loop; inside each round a race loop advances turtles tick-by-tick until one crosses the finish line.

## Metrics

| Metric | Value |
|--------|-------|
| Source modules | 7 (`main`, `audio`, `constants`, `dialogs`, `paths`, `race`, `tracks`) |
| Total source lines | 1,063 |
| Largest module | `race.py` (423 lines) |
| Second largest | `tracks.py` (395 lines) |
| Entry point | `main.py` (51 lines) |
| Distinct runtimes coexisting in one process | 3 (`turtle`, `tkinter`, `pygame.mixer`) |
| Track types | 3 (straight, rectangular, spiral) |
| Turtle racers | 4 (Raphael, Michaelangelo, Leonardo, Donatello) |

---

## Findings

### Three Coexisting Runtimes

The application never creates separate threads or processes. All three runtimes must remain compatible on the single OS main thread:

- **`turtle` (stdlib)** — owns the race canvas. `Screen()` is created once via `race.make_screen()` (`race.py:30-39`) and is reused across rounds by calling `screen.clear()` at the top of each round loop iteration (`main.py:24`) followed by `race.set_background()` (`main.py:27`). The screen is never destroyed and recreated.
  - Evidence: `race.py:13` — module-level singleton `_screen = None`; `race.py:30-39` — `make_screen()` guards against double-init with `if _screen is not None: return _screen`

- **`tkinter`** — owns the bet dialog, track-selection dialog, and "play again?" message box. `Toplevel` windows are used (not new `Tk()` roots), because `turtle.Screen()` implicitly creates the Tk root; all dialogs must be children of that root.
  - Evidence: `dialogs.py:14` — `dialog = tkinter.Toplevel()` for the bet dialog
  - Evidence: `dialogs.py:71-72` — `dialog.grab_set()` + `dialog.wait_window()` blocks `main()` until the user picks a turtle, producing modal behavior without a separate thread
  - Evidence: `dialogs.py:134` — `tkinter.messagebox.askyesno(...)` for the play-again prompt

- **`pygame.mixer`** — plays a looped MIDI soundtrack. Initialized once at program start (`main.py:16`, `audio.py:7-11`); stopped on clean exit (`main.py:46`, `audio.py:14-18`). Failures are caught and silently logged so a missing audio driver does not crash the game.
  - Evidence: `audio.py:6-12` — `start_background_music()` wraps `pygame.mixer.init()` + `.music.load()` + `.music.play(loops=-1)` in a `try/except`

### Main Loop Structure

```
main()                          [main.py:14-47]
  race.make_screen()            -- creates turtle Screen singleton
  audio.start_background_music()-- starts MIDI loop
  while keep_playing:           [main.py:22]
    screen.clear()              -- resets canvas for the new round (skipped on first run)
    race.set_background()       -- repaints lawn.jpg background
    track_name = dialogs.get_user_track()   -- Toplevel modal dialog
    race.draw_boundary_stones(track_name)
    turtles_list = race.create_turtles(TURTLE_COLORS)
    race.place_turtles_on_track(turtles_list, track_name)
    race.draw_start_line(track_name)
    race.draw_finish_line(track_name)
    user_bet = dialogs.get_user_bet()       -- Toplevel modal dialog
    winning_turtle, finish_order = race.run_race(turtles_list, track_name, user_bet)
    race.show_podium(turtles_list, finish_order)
    race.celebrate(winning_turtle, user_won)
    race.announce_result(winning_turtle, user_bet, turtles_list)
    keep_playing = dialogs.ask_play_again() -- tkinter.messagebox
  audio.stop_background_music()
  screen.bye()
```

Evidence: `main.py:14-47` (full `main()` function).

### Race Loop (Inner Loop)

`race.run_race()` (`race.py:156-233`) uses a **fractional progress model** to keep a multi-lane race fair when lanes have different perimeters (rectangular and spiral tracks):

1. A single `shared_distance` is computed once per race. It is the midpoint of the straight-track length and the current track's average lane length, scaled by `1/SPEED_FACTOR` (0.3). All turtles race toward the same `shared_distance` target.
2. Each tick: every turtle advances by `random.randint(0, MAX_PACE)` (`constants.py:16` — `MAX_PACE = 10`).
3. A turtle's visual position is computed as `fraction = progress/shared_distance`, then `arc = fraction * lane_lengths[i]`. The geometry function `tracks.position_at_arc(path, arc)` returns the `(x, y, heading)` at that arc distance along the lane path.
4. After crossing the finish (reaching `shared_distance`), a turtle enters a 30-tick coasting phase (`race.py:185` — `COAST_TICKS = 30`) where it continues moving forward visually.
5. The loop terminates when all turtles have completed their coast.

Evidence: `race.py:156-233`; `constants.py:16-17` for `MAX_PACE` and `TICK_DELAY`.

### Turtle Identity is Positional

Turtle identity is maintained through parallel positional arrays, not objects with names attached:

- `TURTLE_NAMES[i]` and `TURTLE_COLORS[i]` describe the **same** turtle at index `i`.
  - Evidence: `constants.py:8-9`
- `turtles_list[i]['o']` is the live `Turtle` object for lane `i`.
  - Evidence: `race.py:135-138` — `create_turtles()` produces `[{'color': c, 'o': Turtle(...)} for c in color_list]`
- `user_bet` is **1-based**. The winner check is `turtles_list[user_bet - 1]`.
  - Evidence: `main.py:39` — `user_won = winning_turtle.pencolor() == turtles_list[user_bet - 1]['o'].pencolor()`
- The bet dialog converts name to 1-based index via `TURTLE_NAMES.index(name) + 1`.
  - Evidence: `dialogs.py:40` — `idx = TURTLE_NAMES.index(name)` and `make_cb(idx + 1)` at line 61

**Invariant enforced by tests**: `TURTLE_IMAGES.keys()` must exactly equal `set(TURTLE_NAMES)`.
  - Evidence: `tests/test_constants.py:10-13`

### Tk Image Reference Retention

`PhotoImage` objects must be kept alive by Python or Tk silently drops them (garbage collection kills the image). The codebase uses two explicit retention patterns:

1. **Bet dialog images** — stored on `dialog._bet_images` (a list assigned directly to the `Toplevel` instance).
   - Evidence: `dialogs.py:37` — `dialog._bet_images = []`; `dialogs.py:45` — `dialog._bet_images.append(photo)`
2. **Track-selection images** — stored on `dialog._track_images` by the same pattern.
   - Evidence: `dialogs.py:92` — `dialog._track_images = []`
3. **Background image** — stored on `canvas._bg_photo` (the underlying Tk `Canvas` widget).
   - Evidence: `race.py:60` — `canvas._bg_photo = bg`

### PyInstaller-Aware Resource Loading

All asset paths are resolved through `paths.resource_path()`, which checks `sys._MEIPASS` (the PyInstaller extraction directory in a frozen build) and falls back to the source file's directory for development runs.

- Evidence: `paths.py:5-7`
  ```python
  def resource_path(rel_path):
      base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
      return os.path.join(base, rel_path)
  ```
- All asset-loading call sites use this helper: `audio.py:9`, `dialogs.py:42`, `dialogs.py:101`, `race.py:52`.
- The `turtle_race.spec` `datas=` list declares all bundled asset globs:
  ```python
  datas=[('lawn.jpg', '.'), ('assets/*.jpg', 'assets'), ('assets/*.mid', 'assets'), ('assets/*.png', 'assets')]
  ```
  Evidence: `turtle_race.spec:7`
- `turtle` is declared as a `hiddenimport` because PyInstaller's static analysis misses it.
  - Evidence: `turtle_race.spec:8`

### Track Geometry Architecture

`tracks.py` is a pure-geometry module with no side effects. It exposes a strategy registry (`_LANE_BUILDERS`) keyed by track name string, mapping to three lane-builder functions:

- `_straight_lane` — single east-heading leg per lane, all equal length
- `_rectangular_lane` — five-leg clockwise rectangle (N, E, S, W, closing N up to finish bar)
- `_spiral_lane` — shrinking CW rectangular spiral with a two-leg orthogonal "homing" segment to bring all lanes to the canvas origin `(0, 0)`

Evidence: `tracks.py:207-211` — `_LANE_BUILDERS` dict; `tracks.py:214-217` — `build_lane_paths()`.

The actual window size is injected at runtime via `tracks.set_window_size()` (`tracks.py:45-48`), called once from `race.make_screen()` (`race.py:38`). Tests run against the fallback constants-file values (`WINDOW_WIDTH = 500`, `WINDOW_HEIGHT = 400`).

### Canvas Layering / Z-order Management

Tk canvas items are drawn in creation order (later items appear on top). The `turtle` module internally calls `tag_raise` on every turtle sprite during each `_screen.update()`, which pushes podium medals behind turtle shapes. The code works around this by explicitly calling `canvas.tag_raise(PODIUM_MEDAL_TAG)` after every `_screen.update()` in the post-race display sequence.

- Evidence: `race.py:26-27` — `PODIUM_MEDAL_TAG = "podium_medal"`
- Evidence: `race.py:345`, `race.py:365`, `race.py:422` — three `tag_raise` calls after `update()`
- Evidence: `race.py:306-308` — comment explaining why stamps are used instead of live turtles for podium figures

### Tracer Batching Pattern

All multi-step drawing operations disable the turtle tracer before drawing and re-enable it after, so the user sees one complete frame rather than a progressive draw:

```python
_screen.tracer(0)
# ... drawing operations ...
_screen.update()
_screen.tracer(1)
```

Evidence: `race.py:77-82` (`draw_start_line`), `race.py:85-95` (`draw_boundary_stones`), `race.py:127-132` (`draw_finish_line`), `race.py:193-221` (race loop inner block).

---

## Summary Table

| Item | Detail | Confidence |
|------|--------|------------|
| Architectural pattern | Single-process Tk desktop app | Observed |
| Runtime count | 3: `turtle`, `tkinter`, `pygame.mixer` | Observed |
| Screen lifecycle | Created once; reused via `screen.clear()` per round | Observed |
| Dialog blocking mechanism | `Toplevel` + `grab_set()` + `wait_window()` | Observed |
| Music failure handling | Silent catch + print, game continues | Observed |
| Turtle identity | 0-based positional index; `user_bet` is 1-based | Observed |
| Image GC prevention | Attributes stored on `dialog._bet_images`, `canvas._bg_photo` | Observed |
| Asset resolution | `paths.resource_path()` checks `sys._MEIPASS` | Observed |
| Track geometry | Pure-math module, no side effects, injected window size | Observed |
| Race fairness | Fractional progress normalizes lane-length differences | Observed |
| Z-order conflict | `turtle` re-raises sprites each `update()`; medals need explicit `tag_raise` | Observed |
| Cheat mode | Branch exists in CLAUDE.md but `get_user_input()` always returns `cheat_mode=False` | Observed (`dialogs.py` has no cheat-mode parameter; CLAUDE.md describes vestigial branch) |

## Open Questions

- The CLAUDE.md references a `cheat_mode` branch and `get_user_input()` returning `cheat_mode=False`, but the current `dialogs.py` has no `get_user_input()` function. This code may have been removed in a refactor and the CLAUDE.md note is stale.
- `tracks.set_window_size()` uses `_screen.window_width()` / `_screen.window_height()` after `_screen.setup(width=1.0, height=1.0)` (full-screen). The actual pixel dimensions are platform-dependent and not recorded anywhere; tests fall back to `WINDOW_WIDTH = 500`. It is unclear whether `WINDOW_WIDTH` in `constants.py` is still used for anything beyond tests, given the commented-out `# WINDOW_WIDTH = 2550` line suggests the constant was once the canonical size.
