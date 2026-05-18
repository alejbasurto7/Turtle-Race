# Turtle Race

A whimsical Python racing game where you bet on Teenage Mutant Ninja Turtles or snakes scrambling across one of three tracks, set to a looping rock/MIDI soundtrack.

Built on the standard-library `turtle` module, `tkinter` dialogs, and `pygame.mixer` for audio. Runs from source on any platform with Python 3.10+ and ships as a single-file Windows executable via PyInstaller.

## Features

- **Two species to race:** four turtles (Raphael, Michelangelo, Leonardo, Donatello) or three snakes (Shadow, Ralph, Anaconda) — each rendered with photo cards in the bet dialog and animated as scaled shapes on the track.
- **Three track shapes:** straight, rectangular, and spiral — each with its own lane geometry, start/finish lines, and boundary stones.
- **Place a bet** on a racer before the round starts and find out at the finish line whether you picked the winner.
- **Snake size variety:** Shadow, Ralph, and Anaconda race at a locked 6 : 2 : 5 length ratio, so the visual reads like real snakes rather than identical sprites.
- **Podium ceremony** after every race showing the top three in scaled-up form, plus a celebration animation if your bet won.
- **Persistent leaderboard** stored under `%APPDATA%\TurtleRace\leaderboard.json` (Windows) — tracks wins per racer overall and per-track, survives across sessions, and is viewable from the main menu.
- **Looping rock/MIDI soundtrack** (TMNT theme, Back in Black, Thunderstruck, Highway to Hell, Danger Zone, and more) playing in the background while you race.
- **Main menu loop:** race round after round, browse the leaderboard, or quit cleanly — no need to restart the app.
- **PyInstaller-friendly:** all asset paths resolve through a single helper so the frozen exe finds everything bundled inside it.

## Run from source

Requires Python 3.10+ with the standard-library `tkinter` and `turtle` modules (shipped with the official python.org installer on Windows).

```powershell
pip install -r requirements.txt
python main.py
```

Run the tests (pytest is not in `requirements.txt`, install it separately):

```powershell
pip install pytest
pytest
```

## Build your own Windows executable

The project ships a PyInstaller spec file ([turtle_race.spec](turtle_race.spec)) that is the source of truth for which assets get bundled into the exe.

```powershell
pip install pyinstaller
pyinstaller turtle_race.spec
```

The build produces `dist/TurtleRace.exe` — a single windowed executable with no console. The `build/` and `dist/` directories are disposable; delete them to do a clean rebuild.

### Adding new assets

If you add an image or MIDI file, you must also add it to the `datas=` list in [turtle_race.spec](turtle_race.spec) — otherwise the asset works when running from source but is missing in the packaged exe. Note that the glob patterns in `datas=` do **not** recurse, so each asset subdirectory (`assets/turtles/*.jpg`, `assets/snakes/*.png`, `assets/tracks/*.png`, `assets/midi/*.mid`) needs its own entry.

## Project layout

| File | Role |
| --- | --- |
| [main.py](main.py) | Entry point and main-menu / race-round loop |
| [race.py](race.py) | Race animation, shape dispatch, podium, finish detection |
| [tracks.py](tracks.py) | N-parameterized track geometry (straight, rectangular, spiral) |
| [dialogs.py](dialogs.py) | All Tk modal dialogs (track, species, bet, play-again, menu, leaderboard) |
| [leaderboard.py](leaderboard.py) | Tk-free persistence and scoring; JSON store under `%APPDATA%` |
| [audio.py](audio.py) | `pygame.mixer` MIDI playback wrapper |
| [constants.py](constants.py) | Per-species identity, `SPECIES` dispatch config, layout sizes |
| [paths.py](paths.py) | `resource_path()` (PyInstaller-aware) and `user_data_path()` |
| [turtle_race.spec](turtle_race.spec) | PyInstaller build config — source of truth for bundled assets |
| [tests/](tests/) | pytest suite covering constants invariants and asset wiring |
| [assets/](assets/) | Turtle JPGs, snake PNGs, track previews, lawn background, MIDI tracks |

## License

No license file is provided. Treat the source as "all rights reserved" by default — open an issue if you want to discuss reuse.
