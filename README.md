# Turtle Race

A small Python turtle-racing game. Pick the turtle you think will win, watch four colored turtles race across a lawn, and find out if your bet was right.

This is the **original** branch — the earliest version of the project, kept around as a reference snapshot. The active, expanded version lives on `master` (multi-species racers, multiple tracks, leaderboard, audio, podium, etc.).

## Requirements

- Python 3 (any modern 3.x)
- Standard library only — `turtle` and `tkinter`, both shipped with Python on Windows/macOS/Linux

`requirements.txt` is intentionally empty; nothing extra to `pip install` to run the game.

## Run from source

```powershell
python main.py
```

A 500x400 window opens with a lawn background. A text prompt asks which turtle (1–4) you think will win:

1. red4
2. DarkOrange
3. blue
4. DarkMagenta

Type a number, press OK, and the race begins. The winning turtle then does a celebratory spiral. Click the window to exit.

## Files

- `main.py` — game loop, turtle creation, race logic, win detection, celebration
- `constants.py` — turtle colors, window size, spacing, max per-tick pace
- `lawn.gif` — background image, loaded by `main.py` via `s.bgpic("lawn.gif")` (relative path — must sit next to the running script or exe)

## Pre-built executable

A pre-built Windows exe is committed at:

```
dist_original/ReptileRace_original.exe
dist_original/lawn.gif
```

Run `ReptileRace_original.exe` directly. **Keep `lawn.gif` in the same folder** — the exe loads it via a relative path, and the window will fail to open the background if it's missing.

## Build your own exe

The committed exe was built with [PyInstaller](https://pyinstaller.org/) from a Windows machine. To rebuild it yourself:

### 1. Install PyInstaller

```powershell
pip install pyinstaller
```

(PyInstaller is a build-time-only dependency, so it isn't in `requirements.txt`.)

### 2. Build with the spec file (recommended)

The repo ships `ReptileRace_original.spec`, which is the source of truth for the build configuration:

```powershell
pyinstaller ReptileRace_original.spec
```

Output goes to `dist_original/ReptileRace_original.exe`. Build intermediates land in `build_original/` (both are git-ignored except for the final exe).

### 3. Or build from scratch with CLI flags

If you don't have the spec file, this is equivalent:

```powershell
pyinstaller --onefile --name ReptileRace_original --distpath dist_original --workpath build_original main.py
```

### 4. Place `lawn.gif` next to the exe

Because `main.py` uses a plain relative path (`s.bgpic("lawn.gif")`) rather than a PyInstaller-aware resource loader, the bundled exe cannot find `lawn.gif` on its own. After building, copy it next to the exe:

```powershell
copy lawn.gif dist_original\
```

Now `dist_original\ReptileRace_original.exe` will run standalone — distribute the whole `dist_original\` folder (or just those two files) together.

### Notes

- `--onefile` produces a single ~11 MB exe that self-extracts to a temp dir on each launch.
- For a faster-launching but multi-file build, swap `--onefile` for `--onedir`.
- Add `--windowed` if you want to suppress the console window, but be aware `main.py` calls `print()` for win/lose announcements — without a console those messages disappear.
