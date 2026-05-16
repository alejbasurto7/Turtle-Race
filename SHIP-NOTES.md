# Turtle Race — Snakes Racer Mode: Ship Notes

## What Shipped

- Species selector dialog (Turtles | Snakes) per round
- Three snake racers: Shadow (black, length 6), Ralph (#E89F4F, length 2), Anaconda (green, length 5)
- Custom smooth-wave snake polygon; 6:5:2 length ratio at L_BASE=1.2
- Head-position finish detection (universal — turtles and snakes)
- Snake bet dialog (1x3 row); composite turtles/snakes species dialog images
- N-parameterized lane geometry on all 3 tracks (oval, rectangular, spiral)
- Podium supports 3 or 4 finishers; snake lengths preserved in podium display
- Snake PNGs bundled in PyInstaller spec under `assets/snakes/`
- **Shuffled MIDI playlist soundtrack** (post-milestone scope creep via quick-task 001): `audio.py` builds a randomized playlist from `assets/midi/*.mid` at startup; tracks rotate sequentially in a background thread, reshuffle when exhausted. 9 MIDI files bundled.

## Architecture Pointers

Cross-reference CLAUDE.md for the full picture. Key entry points:

- `constants.py` — `SPECIES`, `SNAKE_NAMES/COLORS/LENGTHS/IMAGES`, `L_BASE`
- `race.py` — `draw_snake_shape`, `create_racers`, `place_racers_on_track`, `run_race`, `show_podium`
- `dialogs.py` — `get_user_species`, `get_user_bet`
- `paths.py` — `resource_path()`, all asset loads go through here
- `tracks.py` — N-parameterized geometry, no N_LANES constant

## Run / Test / Build

See CLAUDE.md for full command reference. Quick reference:

- Dev run: `python main.py`
- Tests: `pytest` (expect 85/85)
- Build: `pyinstaller turtle_race.spec` → `dist/TurtleRace.exe`

## Known Deferrals

- **Spiral 3-lane visual tuning:** Snake mode on the spiral track ships as-is. Open a follow-up plan if the geometry looks off in production use.

## Snake & Audio Assets

Snake PNGs (`assets/snakes/Shadow.png`, `Ralph.png`, `Anaconda.png`) are user-provided 1024x1024 RGBA images. They are bundled in the PyInstaller spec via the `assets/snakes/*.png` glob entry.

The shuffled MIDI playlist lives in `assets/midi/` (9 `.mid` files). All are tracked and bundled via the `assets/midi/*.mid` glob entry. The original single-track soundtrack (`assets/TeenageMutantNinjaTurtles.mid`) is still at the `assets/` root and tracked, but `audio.py` no longer loads it directly — the playlist builder picks it up alongside the others if it lives in `assets/midi/`.

## Future Work Suggestions

- 4th species (lizards, frogs) via the `SPECIES` config pattern — no core changes required
- Per-round statistics or win-streak tracking
- Difficulty slider (MAX_PACE tuning) exposed via a dialog
- macOS/Linux packaging (PyInstaller spec is Windows-targeted)
- Spiral 3-lane geometry tuning if visual issues arise in practice
