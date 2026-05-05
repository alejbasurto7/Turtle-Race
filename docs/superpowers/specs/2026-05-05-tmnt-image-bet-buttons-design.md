# TMNT Image Bet Buttons — Design

## Goal

Replace the four colored name buttons in the bet dialog with the actual TMNT turtle images stored in `assets/`, arranged as a 2x2 character-select grid with the turtle's name shown as a caption under each image.

## Context

`get_user_input()` in `main.py` (lines 16–60) currently builds a vertical stack of `tkinter.Button` widgets — one per name in `TURTLE_NAMES`, each colored with the matching entry from `TURTLE_COLORS`. Clicking a button records the user's bet (1-indexed) and closes the dialog.

The race itself identifies turtles by `pencolor()`, not by name. The bet selection translates the chosen index into a color via `turtles[user_bet - 1]['o'].pencolor()`. This contract must not change.

Available assets (in `assets/`):

- `turtle_1_leonardo_top_left.jpg` — Leonardo (blue)
- `turtle_2_donatello_top_right.jpg` — Donatello (purple / DarkMagenta)
- `turtle_3_raphael_bottom_left.jpg` — Raphael (red)
- `turtle_4_michelangelo_bottom_right.jpg` — Michelangelo (orange)

Note that the asset numbering does not match the order in `constants.py`:

```python
TURTLE_NAMES  = ["Raphael", "Michaelangelo", "Leonardo", "Donatello"]
TURTLE_COLORS = ["red4",    "DarkOrange",    "blue",     "DarkMagenta"]
```

The bet index returned by `get_user_input()` indexes into these arrays, so each image must be associated with the correct turtle by **name**, not by file number.

## Design

### 1. Constants

Add to `constants.py` a mapping from each turtle name to its asset filename:

```python
TURTLE_IMAGES = {
    "Raphael":      "assets/turtle_3_raphael_bottom_left.jpg",
    "Michaelangelo":"assets/turtle_4_michelangelo_bottom_right.jpg",
    "Leonardo":     "assets/turtle_1_leonardo_top_left.jpg",
    "Donatello":    "assets/turtle_2_donatello_top_right.jpg",
}
BET_IMAGE_SIZE = 140  # px, square
```

Using a dict keyed by name avoids any chance of mis-ordering.

### 2. Dialog layout

Rewrite the body of `get_user_input()` to build a 2x2 grid using `tkinter.grid()`:

- Row 0: title label (`columnspan=2`).
- Rows 1 and 2: two cells each. Each cell is a single `tkinter.Button` with `compound="top"`, an `image=` of the resized turtle, and `text=` set to the turtle's name. Using one widget per cell (instead of separate Label + Button) keeps the entire image+name area clickable and removes alignment work.

Grid order matches the position hints encoded in the filenames:

```
(row 1, col 0) Leonardo      (row 1, col 1) Donatello
(row 2, col 0) Raphael       (row 2, col 1) Michelangelo
```

Bet index returned to the caller is still the 1-based index of the clicked turtle in `TURTLE_NAMES` — unchanged contract.

### 3. Image loading

- Use `PIL.Image.open(resource_path(path))` → `.resize((BET_IMAGE_SIZE, BET_IMAGE_SIZE), Image.LANCZOS)` → `ImageTk.PhotoImage(...)`.
- Store the `PhotoImage` references on the dialog (e.g., `dialog._bet_images = [...]`) to prevent Tk garbage-collecting them while the dialog is open. The existing background-image code in `set_background()` uses the same pattern.
- `resource_path()` already handles PyInstaller's `_MEIPASS` so no new path logic is needed.

### 4. PyInstaller bundling

Update `turtle_race.spec`:

```python
datas=[('lawn.jpg', '.'), ('assets/*.jpg', 'assets')],
```

This ships the four turtle images alongside `lawn.jpg` inside the frozen executable.

### 5. Out of scope

- No hover / selected-state styling. Single click still locks in the bet, same as today.
- No changes to the race loop, the on-track turtles, or the win/lose UI.
- No changes to `TURTLE_NAMES` or `TURTLE_COLORS` ordering — the race and bet-index logic continue to depend on them.
- No "play again" dialog changes.

## Risk and verification

- **Image-to-name mismatch** is the main risk (which image gets which name). Mitigated by using a name-keyed dict in `constants.py` and by visual verification: launch the app, confirm each image's caption matches the character shown.
- **PyInstaller miss**: verify the bundled `dist/TurtleRace.exe` shows the images, not a missing-file error.
- **Tk image GC**: if images don't render but no error is raised, that's almost always lost references — confirm `dialog._bet_images` is held for the dialog's lifetime.
