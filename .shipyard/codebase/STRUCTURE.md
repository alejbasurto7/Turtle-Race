# STRUCTURE.md

## Overview

The project is a flat single-directory layout with no packages or sub-namespaces. All seven source modules live in the project root alongside the spec file and one root-level asset (`lawn.jpg`). Turtle/character images and audio files are collected under `assets/`. Tests live in `tests/`. There are no `__init__.py` files; the project is not installed as a package.

## Metrics

| Metric | Value |
|--------|-------|
| Source modules (root) | 7 |
| Test files | 2 |
| Asset files | 8 (1 MIDI, 3 PNG previews, 4 JPEG turtle images) |
| Root-level assets | 1 (`lawn.jpg` background) |
| Build output directories | `build/`, `dist/` (git-ignored) |
| Config/spec files | 1 (`turtle_race.spec`) |

---

## Findings

### Root Directory Layout

```
Turtle Race/
├── main.py             Entry point — round loop orchestration
├── audio.py            pygame.mixer wrapper (start/stop music)
├── constants.py        All shared constants (names, colors, images, layout)
├── dialogs.py          All tkinter modal dialogs (track, bet, play-again)
├── paths.py            resource_path() helper for PyInstaller compatibility
├── race.py             turtle drawing and race loop
├── tracks.py           Pure geometry module — lane paths, finish/start lines
│
├── lawn.jpg            Background image (root-level; bundled to '.' in spec)
├── assets/
│   ├── TeenageMutantNinjaTurtles.mid  Background music (pygame.mixer)
│   ├── track_straight.png             Track-selection dialog preview
│   ├── track_rectangular.png          Track-selection dialog preview
│   ├── track_spiral.png               Track-selection dialog preview
│   ├── turtle_1_leonardo_top_left.jpg     Bet dialog image
│   ├── turtle_2_donatello_top_right.jpg   Bet dialog image
│   ├── turtle_3_raphael_bottom_left.jpg   Bet dialog image
│   └── turtle_4_michelangelo_bottom_right.jpg  Bet dialog image
│
├── tests/
│   ├── test_constants.py   Validates TURTLE_IMAGES/TURTLE_NAMES alignment + file existence
│   └── test_tracks.py      Geometry invariants for all three track types
│
├── turtle_race.spec    PyInstaller spec — source of truth for bundled assets
├── requirements.txt    Runtime pip deps (pillow, pygame-ce)
├── CLAUDE.md           Architecture notes for AI-assisted development
│
├── build/              PyInstaller intermediate artifacts (git-ignored)
├── dist/               PyInstaller output (TurtleRace.exe) (git-ignored)
└── .venv/              Virtual environment (git-ignored)
```

Evidence for all files: verified by `find` on project root; asset listing from `assets/` glob; spec from `turtle_race.spec:7`.

---

### Module Responsibilities

#### `main.py` (51 lines)
The sole entry point and round-loop driver. Imports `audio`, `dialogs`, `race`, and `constants.TURTLE_COLORS`. Calls into the other modules in sequence; contains no logic of its own beyond the outer `while keep_playing` loop. The `if __name__ == "__main__": main()` guard is at line 50.

Evidence: `main.py:14-47`

#### `constants.py` (33 lines)
Single source of truth for all shared configuration values. Contains:
- `TURTLE_NAMES` / `TURTLE_COLORS` — parallel lists (positional identity invariant)
- `TURTLE_IMAGES` — dict mapping name to relative asset path
- Window and layout constants (`WINDOW_WIDTH`, `WINDOW_HEIGHT`, `SPACING`, `TURTLE_LENGTH`, etc.)
- Race timing constants (`MAX_PACE`, `TICK_DELAY`)
- Track layout constants (`N_LANES`, `TRACK_PADDING`, `LANE_SPACING`, `SPIRAL_STEP`)
- Dialog constants (`BET_IMAGE_SIZE`, `TRACK_PREVIEW_W`, `TRACK_PREVIEW_H`)

No other module may define these values; all modules import from `constants`.

Evidence: `constants.py:8-33`

#### `paths.py` (7 lines)
Single-function utility. `resource_path(rel_path)` resolves an asset path that works both in development (relative to the source file) and in a PyInstaller-frozen executable (`sys._MEIPASS`). Every asset-loading call site imports and uses this function.

Evidence: `paths.py:1-7`

#### `audio.py` (19 lines)
Thin wrapper around `pygame.mixer`. Exposes `start_background_music(midi_rel_path)` and `stop_background_music()`. All failure modes are caught and silently logged so the game continues without audio rather than crashing. Imports `resource_path` from `paths`.

Evidence: `audio.py:1-19`

#### `dialogs.py` (135 lines)
All user-facing tkinter dialogs. Three public functions:
- `get_user_track()` — `Toplevel` with 3 image buttons (track previews from `assets/*.png`); returns a track-name string constant from `tracks`
- `get_user_bet()` — `Toplevel` with a 2x2 image button grid (turtle JPEGs from `assets/*.jpg`); returns a 1-based integer bet index
- `ask_play_again()` — `tkinter.messagebox.askyesno`; returns bool

Both `Toplevel` dialogs use `grab_set()` + `wait_window()` for blocking modal behavior. Both stash `PhotoImage` references on the dialog object to prevent Tk garbage collection.

The bet grid layout is **hard-coded** in `dialogs.py:29-34` as `grid_layout`:
```python
grid_layout = [
    ("Leonardo",      1, 0),
    ("Donatello",     1, 1),
    ("Raphael",       2, 0),
    ("Michaelangelo", 2, 1),
]
```
This order is decoupled from `TURTLE_NAMES` order and is determined by the position hints embedded in the asset filenames (`top_left`, `top_right`, `bottom_left`, `bottom_right`).

Evidence: `dialogs.py:11-135`; grid layout at `dialogs.py:29-34`

#### `race.py` (423 lines)
All turtle-module drawing and race animation. Owns:
- The `_screen` singleton (`race.py:13`) and its lifecycle helpers (`make_screen`, `get_screen`)
- Background painting (`set_background`) — uses PIL to resize and crop `lawn.jpg` to the actual window size, then places it on the underlying Tk canvas as a `create_image` item
- Track drawing helpers (`draw_boundary_stones`, `draw_start_line`, `draw_finish_line`)
- Turtle creation and placement (`create_turtles`, `place_turtles_on_track`)
- The race loop (`run_race`) — fractional progress model, `time.sleep(TICK_DELAY)` between ticks, race log printed to stdout
- Post-race display (`show_podium`, `celebrate`, `announce_result`) — podium uses direct Tk canvas drawing to avoid z-order conflicts with turtle sprites

Evidence: `race.py:1-424`

#### `tracks.py` (395 lines)
Pure geometry library with **no side effects** and no turtle/Tk imports. Computes all path data for the three track types as dicts of `{"start": (x, y), "legs": [(heading_deg, length_px), ...]}`. Public interface:

| Function | Returns |
|---|---|
| `build_lane_paths(track_name)` | `list[dict]` — one path dict per lane |
| `path_length(path)` | `float` — total arc length |
| `position_at_arc(path, arc)` | `(x, y, heading_deg)` — interpolated position |
| `lane_start_pose(track_name, lane_idx)` | `(x, y, heading_deg)` — start pose |
| `start_line_segments(track_name)` | `list[((x,y),(x,y))]` — segments to draw |
| `finish_line_segments(track_name)` | `list[((x,y),(x,y))]` — segments to draw |
| `boundary_stones(track_name)` | `list[(x,y)]` — stone center points |
| `set_window_size(w, h)` | `None` — injects runtime canvas dimensions |

Track name constants: `STRAIGHT = "straight"`, `RECTANGULAR = "rectangular"`, `SPIRAL = "spiral"`. These strings are the public API; `dialogs.py` passes them through to `race.py` and `tracks.py`.

Evidence: `tracks.py:28-32`, `tracks.py:214-395`

---

### Asset Organization

The asset filename encoding carries semantic meaning relied upon by the bet dialog grid layout:

| File | Encodes |
|---|---|
| `turtle_1_leonardo_top_left.jpg` | Index 1, name Leonardo, grid position top-left |
| `turtle_2_donatello_top_right.jpg` | Index 2, name Donatello, grid position top-right |
| `turtle_3_raphael_bottom_left.jpg` | Index 3, name Raphael, grid position bottom-left |
| `turtle_4_michelangelo_bottom_right.jpg` | Index 4, name Michaelangelo, grid position bottom-right |

The numeric prefix (1–4) does **not** correspond to `TURTLE_NAMES` order; it is just a file-sorting artifact. The actual mapping from name to file path is in `constants.py:19-24` (`TURTLE_IMAGES` dict), and the grid position is hard-coded in `dialogs.py:29-34`.

Evidence: `assets/` directory listing; `constants.py:19-24`; `dialogs.py:29-34`

### Build Artifact Boundaries

PyInstaller produces a single-file `dist/TurtleRace.exe` (one-file mode; `a.scripts`, `a.binaries`, `a.zipfiles`, `a.datas` all passed to `EXE`). Build intermediates land in `build/turtle_race/`. Both directories are git-ignored.

The `turtle_race.spec` `datas=` entry is the **authoritative list** of what gets bundled. When adding a new asset, both the code (`resource_path(...)`) and `datas=` in the spec must be updated.

Evidence: `turtle_race.spec:7,17-31`

---

### Dependency Graph (Internal Modules)

```
main
 ├── audio        → paths
 ├── dialogs      → paths, constants, tracks
 ├── race         → paths, constants, tracks
 └── constants    (no internal imports)

tracks             → constants
paths              (no internal imports)
```

No circular dependencies. `paths` and `constants` are pure leaf modules. `tracks` depends only on `constants`. `audio`, `dialogs`, and `race` all depend on `paths`. `main` is the only module that imports `audio`, `dialogs`, and `race` together.

Evidence: `import` statements cross-checked across all seven modules.

---

## Summary Table

| Item | Detail | Confidence |
|------|--------|------------|
| Layout style | Flat (no packages, no sub-namespaces) | Observed |
| Entry point | `main.py` / `main()` | Observed |
| Constants module | `constants.py` — single source of truth | Observed |
| Asset path helper | `paths.py` / `resource_path()` | Observed |
| Geometry module | `tracks.py` — pure functions, no side effects | Observed |
| Dialog module | `dialogs.py` — all tkinter UI | Observed |
| Race/drawing module | `race.py` — all turtle drawing + race loop | Observed |
| Audio module | `audio.py` — thin pygame.mixer wrapper | Observed |
| Circular dependencies | None | Observed |
| Root-level non-Python asset | `lawn.jpg` only | Observed |
| Asset subdirectory | `assets/` — images + MIDI | Observed |
| Test directory | `tests/` — 2 files | Observed |

## Open Questions

- `constants.py` line 10 contains a commented-out `# WINDOW_WIDTH = 2550` alongside the active `WINDOW_WIDTH = 500`. The intent (retina display? dual-monitor?) is not documented. The `500` value is only a fallback for tests; the runtime window is fullscreen.
- There is no `conftest.py` or `pytest.ini`; test discovery relies on pytest's default conventions. The `tests/` directory has no `__init__.py`. [Inferred] Both test files manually insert the project root into `sys.path` at the top, making them runnable from any working directory.
