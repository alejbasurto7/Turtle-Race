# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Install deps (also need standard-lib `tkinter` and `turtle`, shipped with Python):

```powershell
pip install -r requirements.txt
```

Run the game:

```powershell
python main.py
```

Run tests (pytest is not in `requirements.txt` — install it separately):

```powershell
pytest                                  # all tests
pytest tests/test_constants.py          # single file
pytest tests/test_constants.py::test_image_files_exist_on_disk   # single test
```

Build the standalone Windows executable with PyInstaller (uses the spec, which is the source of truth for bundled data files):

```powershell
pyinstaller turtle_race.spec
```

Output lands in `dist/TurtleRace.exe`. Build intermediates in `build/` and `dist/` are disposable.

## Architecture

Single-process Tk app. Three runtimes share the same Tk root and must coexist:

- **`turtle` module** drives the race animation. `Screen()` is created once at module load (in [main.py](main.py)) and reused across rounds via `s.clear()` + re-`set_background()` rather than recreated.
- **`tkinter`** owns the bet dialog ([main.py:31](main.py#L31)) and the "play again?" `messagebox`. The bet dialog uses `Toplevel` + `grab_set()` + `wait_window()` to block until the user picks a turtle.
- **`pygame.mixer`** plays the looped MIDI soundtrack as background music ([main.py:22](main.py#L22)). It is initialized once and stopped on exit.

### Resource loading (PyInstaller-aware)

All asset paths must be resolved through `resource_path()` ([main.py:17](main.py#L17)), which honors `sys._MEIPASS` so the frozen build can find bundled files. When you add a new asset, also add it to the `datas=` list in [turtle_race.spec](turtle_race.spec) — otherwise it works from source but breaks in the packaged exe.

### Turtle identity is positional

[constants.py](constants.py) defines `TURTLE_NAMES`, `TURTLE_COLORS`, and `TURTLE_IMAGES`. Code relies on these invariants:

- `TURTLE_NAMES[i]` and `TURTLE_COLORS[i]` describe the **same** turtle.
- `TURTLE_IMAGES` is keyed by name, and `tests/test_constants.py` enforces that its keys match `TURTLE_NAMES` exactly.
- `user_bet` is 1-based; `turtles[user_bet - 1]` is the user's pick. The bet dialog computes this with `TURTLE_NAMES.index(name) + 1`.
- The 2x2 bet grid layout is decoupled from `TURTLE_NAMES` order — it's hard-coded in `grid_layout` ([main.py:49](main.py#L49)) to match the position hints in the asset filenames (`top_left`, `top_right`, etc.).

### Tk image references

`PhotoImage` objects must be retained or Tk garbage-collects them and the images vanish. The dialog stashes them on `dialog._bet_images`; the background image is stashed on `canvas._bg_photo`. Preserve this pattern when adding images.

### Main loop shape

The outer `while keep_playing` loop in [main.py](main.py) is the round loop. The inner `while is_race_on` advances every turtle by `random.randint(0, MAX_PACE)` per tick until one crosses the finish line at `x = (WINDOW_WIDTH - TURTLE_LENGTH) / 2`. There is a vestigial `cheat_mode` branch wired up but `get_user_input()` always returns `cheat_mode=False`.
