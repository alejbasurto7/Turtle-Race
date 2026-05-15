# STACK.md

## Overview

Turtle Race is a single-file-entry Python desktop game targeting Windows. It combines three coexisting runtimes — the standard-library `turtle`/`tkinter` GUI stack, Pillow for image processing, and `pygame-ce` for audio — all packaged into a standalone Windows executable via PyInstaller. There is no web server, no database, and no network layer.

## Metrics

| Metric | Value |
|--------|-------|
| Language | Python 3 |
| Python version (dev environment) | 3.14.4 |
| Total source lines (project root .py files) | 1,063 |
| Source modules | 7 (`main`, `audio`, `constants`, `dialogs`, `paths`, `race`, `tracks`) |
| Third-party runtime dependencies | 2 (`pillow`, `pygame-ce`) |
| Standard-library frameworks used | `turtle`, `tkinter`, `tkinter.messagebox` |
| Build tool | PyInstaller (spec-driven, single-file exe) |
| Package manager | pip + `.venv` virtualenv |
| Target platform | Windows (exe output; `winsound`/`winmm` referenced in dev tooling) |

## Findings

### Language

- **Python 3** — sole language. No type annotations in source modules; dev tooling (`tools/generate_track_previews.py`) uses the `X | Y` union syntax (`Image.Image | None`) which requires Python 3.10+.
  - Evidence: `tools/generate_track_previews.py` line 32

### Runtime Frameworks

- **`turtle` (stdlib)** — drives all race animation. `Screen()` singleton is created in `race.make_screen()` and reused across rounds via `screen.clear()` rather than being recreated.
  - Evidence: `race.py` lines 4, 30–39
- **`tkinter` (stdlib)** — owns all modal dialogs (bet selection, track selection, play-again prompt). Dialogs use `Toplevel` + `grab_set()` + `wait_window()` to block the main loop.
  - Evidence: `dialogs.py` lines 1–2, 14, 71–73
- **`tkinter.messagebox` (stdlib)** — used for the "play again?" yes/no prompt.
  - Evidence: `dialogs.py` lines 2, 135

### Third-Party Libraries

- **Pillow 12.2.0** (`pillow` on PyPI) — used for background image loading and scaling (`Image.open`, `Image.LANCZOS`, `ImageTk.PhotoImage`), bet-dialog turtle images, and track-preview generation.
  - Evidence: `race.py` line 5; `dialogs.py` line 4; `tools/generate_track_previews.py` line 12
- **pygame-ce 2.5.7** (`pygame-ce` on PyPI) — community edition fork of pygame. Used exclusively for `pygame.mixer` to load and loop the MIDI soundtrack. No display or event features from pygame are used.
  - Evidence: `audio.py` lines 1, 8–11; `requirements.txt` line 2

### Build Tools and Packaging

- **PyInstaller** — bundles the app into a single `dist/TurtleRace.exe`. The spec file is the source of truth for bundled assets. Version not pinned in `requirements.txt` (not listed there at all).
  - Evidence: `turtle_race.spec`; `CLAUDE.md` build instructions
- **`turtle_race.spec`** — spec mode: `onefile` (single EXE), `console=False` (windowed), UPX compression enabled, no icon set.
  - Evidence: `turtle_race.spec` lines 17–31
- **Bundled asset globs** in spec: `lawn.jpg` (root), `assets/*.jpg`, `assets/*.mid`, `assets/*.png`.
  - Evidence: `turtle_race.spec` line 7
- **`hiddenimports=['turtle']`** — `turtle` must be explicitly declared because PyInstaller's static analysis misses it.
  - Evidence: `turtle_race.spec` line 8

### Package Manager and Environment

- **pip** with a `.venv` local virtualenv. No `pyproject.toml`, no `setup.py`, no lock file (`requirements.txt` lists only two packages with no pinned versions).
  - Evidence: `requirements.txt` (2 lines); `.venv/` directory present in repo root
- **pytest** is the test runner but is intentionally excluded from `requirements.txt`; must be installed separately.
  - Evidence: `CLAUDE.md` — "pytest is not in requirements.txt — install it separately"

### Environment Configuration

- No `.env` file, no environment variable reads in application code. All configuration is compile-time constants in `constants.py`.
  - Evidence: `constants.py` — only literal assignments, no `os.environ` calls
- [Inferred] Target runtime is Windows only. `tools/diagnose_audio.py` uses `winsound` and `ctypes.windll.winmm` (Windows MIDI API). The `pygame.mixer` MIDI path may or may not work on other platforms depending on system MIDI synthesizer availability.
  - Evidence: `tools/diagnose_audio.py` lines 11, 56–67

## Summary Table

| Item | Detail | Confidence |
|------|--------|------------|
| Language | Python 3 | Observed |
| Min Python version | 3.10 (union syntax used in tools) | Observed |
| Dev Python version | 3.14.4 | Observed |
| GUI framework | `tkinter` + `turtle` (stdlib) | Observed |
| Image processing | Pillow 12.2.0 | Observed |
| Audio | pygame-ce 2.5.7, `pygame.mixer` only | Observed |
| Build / packaging | PyInstaller (spec-driven) | Observed |
| Package manager | pip + venv | Observed |
| Lock file | None | Observed |
| Platform target | Windows (exe) | Observed |
| Config mechanism | Compile-time constants in `constants.py` | Observed |

## Open Questions

- What is the minimum supported Python version for the game itself? The `|` union syntax in `tools/generate_track_previews.py` requires 3.10+, but that file is a dev tool not bundled into the exe. The main source files do not use 3.10+ features visibly, so 3.8+ may work for the game — but this has not been verified.
- PyInstaller version is not pinned anywhere. If the build is reproduced on a fresh machine, a mismatched PyInstaller version could silently produce a broken exe.
- `pygame-ce` vs `pygame`: the community edition is a drop-in replacement, but the `requirements.txt` pin to `pygame-ce` (not `pygame`) means contributors must know to install it specifically. No comment explains the fork choice.
