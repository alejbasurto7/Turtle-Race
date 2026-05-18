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
pyinstaller reptile_race.spec
```

Output lands in `dist/ReptileRace.exe`. Build intermediates in `build/` and `dist/` are disposable.

## Architecture

Single-process Tk app. Three runtimes share the same Tk root and must coexist:

- **`turtle` module** drives the race animation. `Screen()` is created once via `race.make_screen()` and reused across rounds via `screen.clear()` + re-`set_background()` rather than recreated.
- **`tkinter`** owns the six modal dialogs in [dialogs.py](dialogs.py) — `get_user_track`, `get_user_species`, `get_user_bet`, `ask_play_again_choice`, `get_main_menu_choice`, and `show_leaderboard`. Each dialog uses `Toplevel` + `grab_set()` + `wait_window()` to block until the user chooses, with `WM_DELETE_WINDOW` redirected (no-op or routed to a Close handler) so the user must pick a button.
- **`pygame.mixer`** plays the looped MIDI soundtrack as background music (initialized and stopped via [audio.py](audio.py)). It is started once at the top of `main()` and stopped on exit.

### Resource loading (PyInstaller-aware)

All asset paths must be resolved through `resource_path()` (defined in [paths.py](paths.py)), which honors `sys._MEIPASS` so the frozen build can find bundled files. When you add a new asset, also add it to the `datas=` list in [reptile_race.spec](reptile_race.spec) — otherwise it works from source but breaks in the packaged exe. Note: glob patterns in `datas=` do **not** recurse, so subdirectories like `assets/snakes/*.png`, `assets/tracks/*.png`, and `assets/turtles/*.jpg` each need their own entries.

### Racer identity is positional, and species-dispatched

[constants.py](constants.py) defines per-species identity lists and a `SPECIES` config dict that downstream code dispatches on. Code relies on these invariants:

- **Per-species positional lists:** `TURTLE_NAMES[i] ↔ TURTLE_COLORS[i]`; `SNAKE_NAMES[i] ↔ SNAKE_COLORS[i] ↔ SNAKE_LENGTHS[i]`. Image dicts (`TURTLE_IMAGES`, `SNAKE_IMAGES`) are keyed by name, and `tests/test_constants.py` enforces key/name parity.
- **`SPECIES`** is the dispatch surface — `SPECIES["turtles"]` and `SPECIES["snakes"]` each carry `names`, `colors`, `images`, `bet_layout`, and `shape_drawer`. `shape_drawer` is a **string sentinel** (`"turtle"` / `"snake"`) — never a callable — to keep `constants.py` import-clean (no `race.py` circular import).
- **Bet indexing:** `user_bet` is 1-based; `racers[user_bet - 1]` is the user's pick. The bet dialog computes this as `SPECIES[species]["names"].index(name) + 1`.
- **Bet-grid layouts** are module-level constants in [dialogs.py](dialogs.py): `_TURTLE_GRID_LAYOUT` (2×2, matches the position hints in turtle JPG filenames) and `_SNAKE_ROW_LAYOUT` (1×3, in `SNAKE_NAMES` order).
- **Snake length ratio** is by name, not list position: `SNAKE_LENGTHS = [6, 2, 5]` (positional with `SNAKE_NAMES = ["Shadow", "Ralph", "Anaconda"]`); the 6:5:2 visual ratio is Shadow:Anaconda:Ralph **by value**, which is locked by `test_snake_lengths_positional_values`.
- **Hex pencolor caveat:** `turtle.color("#RRGGBB")` round-trips through `pencolor()` as an `(r, g, b)` tuple, not the original string. When logging/displaying a racer's color, read it from the racer dict (`racer['color']`), not via `pencolor()`. For win detection use racer-dict identity (`winner_racer['o'] is racers[user_bet - 1]['o']`), not pencolor equality, since two racers could theoretically share a color.

### Shape dispatch and finish detection

`race._SHAPE_DRAWERS` maps each `shape_drawer` sentinel to its drawer callable (`draw_turtle_shape` for `"turtle"`, `draw_snake_shape` for `"snake"`). To add a third species, register its drawer there — do not branch in `create_racers`. The snake shape itself is a custom polygon registered lazily on first `draw_snake_shape` call via `screen.register_shape("snake", _SNAKE_POLYGON)`; `register_shape` persists across `screen.clear()`, so the lazy guard prevents re-registration across rounds.

Head-position finish detection in `run_race` is universal: it reads each racer's `shapesize()[1]` (stretch_len) once at race start, computes a per-racer `head_offset_progress[]` parallel array, and checks `progress[i] >= shared_distance - head_offset_progress[i]`. `_SHAPE_UNIT_SIZE` maps shape names to their natural length along the heading axis: `9` for `"classic"` and `"turtle"` shapes, `20` for the custom `"snake"` polygon (`_SNAKE_POLYGON_LENGTH = 20`). The helpers `_head_offset_arc_for(t)` and `_back_pos(...)` in `race.py` back each racer's center behind its lane-start point so the racer's HEAD sits precisely at the lane start position.

Podium scaling in `show_podium` is species-aware: turtles get a uniform `(3.0, 3.0)` enlargement; snakes preserve their race-time `stretch_len` (so the 6:5:2 length ratio survives) and just bump width to `3.0` for visibility.

### N-parameterized track geometry

[tracks.py](tracks.py) is fully generalized over the number of racers. Every public function takes `n: int` explicitly — there is no `N_LANES` constant and no default. `race.create_racers(species)` and `race.place_racers_on_track(racers, track_name)` derive `n = len(racers)` and thread it through.

### Tk image references

`PhotoImage` objects must be retained or Tk garbage-collects them and the buttons go blank. Each dialog stashes them on its own list:

- `dialog._track_images` (in `get_user_track`)
- `dialog._species_images` (in `get_user_species`)
- `dialog._bet_images` (in `get_user_bet`, both turtle and snake branches share the same list)

The background image is stashed on `canvas._bg_photo`. Preserve this pattern when adding images.

### Round loop shape

`main()` uses a **two-level loop**. The **outer loop** iterates the main menu (`dialogs.get_main_menu_choice()` returns `"race" | "leaderboard" | "quit"`); the **inner loop** iterates race rounds when `"race"` is chosen.

`running` (outer) and `in_round_loop` (inner) are the sentinel booleans. **Quit** from the post-race prompt (`dialogs.ask_play_again_choice()` → `"quit"`) sets BOTH False so the outer loop exits cleanly without re-entering the menu — this is intentional; `audio.stop_background_music()` and `screen.bye()` must run exactly once on the way out.

Each race round flows: `screen.clear()` → `set_background()` → `get_user_track()` → `get_user_species()` → `create_racers(species)` → place/draw → `get_user_bet(species)` → `run_race(racers, ...)` → `leaderboard.record_race(species, track_name, finish_order_names)` → `show_podium` → `celebrate` → `announce_result` → `ask_play_again_choice()`.

The race loop itself lives in `race.run_race(...)`. It advances every racer along its lane path by a fraction of `shared_distance` per tick (so longer lanes like the spiral don't auto-lose), detects finishers, and runs a fixed `COAST_TICKS` post-finish coast for visual polish. No `is_race_on` boolean, no `cheat_mode` branch — those were removed during the Phase 2 generalization.

### Leaderboard (Phase 1 module, Phase 4 view)

[leaderboard.py](leaderboard.py) is the persistence and scoring core. It is **Tk-free** — `import leaderboard` succeeds in a headless Python with no `DISPLAY` and no Tk root. The three no-GUI smoke scripts (`tools/smoke_phase_3.py`, `tools/smoke_phase_4.py`, `tools/smoke_phase_5.py`) depend on this invariant: they import `leaderboard` directly and never instantiate a `Tk()` root. Do not add `import tkinter` (or any Tk-touching helper) to `leaderboard.py`.

The on-disk store lives at `%APPDATA%\ReptileRace\leaderboard.json` on Windows (`~/.local/share/ReptileRace/leaderboard.json` on Linux, `~/Library/Application Support/ReptileRace/leaderboard.json` on macOS), resolved via `paths.user_data_path("leaderboard.json")`. `user_data_path()` is the writable-per-user-data sibling of `resource_path()` — it **never** returns a path inside `sys._MEIPASS`. The JSON file is **generated at runtime** by `leaderboard._save()`; it is NOT a [reptile_race.spec](reptile_race.spec) `datas=` entry.

The schema is `{"schema_version": 1, "races": [...]}` (constant `leaderboard.SCHEMA_VERSION`). Future migrations dispatch on `schema_version`; only v1 ships today. Writes are atomic (tempfile + `os.replace`) and unparseable input is quarantined to `<path>.corrupt-<ts>` and replaced with a fresh empty store.

[dialogs.py](dialogs.py)'s `show_leaderboard()` reads data **only** through the public `leaderboard` API — `query`, `query_per_track`, `known_tracks`, `reset_session`, `reset_all` — never via direct file I/O. This direction (`dialogs` imports `leaderboard`, never the reverse) keeps the Tk-free invariant intact.
