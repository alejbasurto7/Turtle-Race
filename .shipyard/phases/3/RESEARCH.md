# Research: Phase 3 — Species + snake-aware bet dialogs

All claims below are directly observed from the codebase unless marked `[Inferred]`.
File paths are absolute-style project-relative; line numbers are as of the master branch
at the time of this research.

---

## 1. `dialogs.py` current state — full read

**File:** `dialogs.py` (136 lines total as of Phase 2 completion)

### Function inventory

#### `get_user_bet()` — lines 11–74
- **Signature:** `def get_user_bet()` — zero arguments. This is the call site that Phase 3
  must change to `get_user_bet(species)`.
- **Label text:** `"Which turtle do you think will win the race?"` — hardcoded at line 20.
- **Layout constant:** `grid_layout` — local variable defined at lines 29–34 inside the
  function body. Phase 3 must promote this to module-level `_TURTLE_GRID_LAYOUT`.
- **Image source:** `TURTLE_IMAGES[name]` via `resource_path()` at line 42. Resized to
  `BET_IMAGE_SIZE` × `BET_IMAGE_SIZE` at line 43.
- **Image-ref retention:** `dialog._bet_images = []` at line 37; `.append(photo)` at line 45.
- **Bet-index computation:** `idx = TURTLE_NAMES.index(name)` at line 40, returned as
  `idx + 1` (1-based) via `make_cb(idx + 1)` at line 61.
- **Modal pattern:** `grab_set()` line 71 → `wait_window()` line 72.
- **Window-close no-op:** `protocol("WM_DELETE_WINDOW", lambda: None)` at line 17.

#### `get_user_track()` — lines 77–131
- **Signature:** `def get_user_track()` — zero arguments. Unchanged by Phase 3.
- **Label text:** `"Pick a race track"` at line 86.
- **Layout:** local `layout` list at lines 94–98 — 3 `(track_name, label, image_path, col)`
  tuples. Buttons placed in a single row (`row=1`) at line 120.
- **Image source:** arbitrary path from the layout tuple — no constants import for the track
  preview images themselves.
- **Image-ref retention:** `dialog._track_images = []` at line 92.
- **Modal pattern:** `grab_set()` line 128 → `wait_window()` line 129. Same structure as
  `get_user_bet`.
- **Window-close no-op:** line 83.
- **Centering:** `update_idletasks()` + `winfo_width/height/screenwidth/screenheight` +
  `dialog.geometry(f"+{x}+{y}")` at lines 122–126. Same block exists in `get_user_bet` at
  lines 65–69.

#### `ask_play_again()` — line 134–135
- One-liner: `return tkinter.messagebox.askyesno(...)`. Unchanged by Phase 3.

### Current imports — lines 1–8
```python
import tkinter
import tkinter.messagebox

from PIL import Image, ImageTk

import tracks
from constants import TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE
from paths import resource_path
```

### New imports required by Phase 3
The following must be added to the `from constants import ...` line:
- `SNAKE_IMAGES` — needed by the `"row_3"` branch of `get_user_bet`
- `SPECIES` — needed so `get_user_bet(species)` can resolve `SPECIES[species]["bet_layout"]`,
  `SPECIES[species]["names"]`, and `SPECIES[species]["images"]`
- `SPECIES_DIALOG_IMAGE_SIZE` — needed by `get_user_species` (new constant; see Q6)

`SNAKE_NAMES` does not need to be imported directly: `SPECIES["snakes"]["names"]` carries
the same list. `TURTLE_NAMES` similarly becomes redundant but can be kept or replaced —
cleaner to go through `SPECIES` uniformly in the refactored function.

Updated import line:
```python
from constants import (
    TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE,
    SNAKE_IMAGES, SPECIES, SPECIES_DIALOG_IMAGE_SIZE,
)
```

`TURTLE_NAMES` is currently used only in `get_user_bet` for `TURTLE_NAMES.index(name)`.
After the refactor, that becomes `SPECIES[species]["names"].index(name)`, so `TURTLE_NAMES`
can be dropped from the import. Architect to decide whether to clean this up or leave it
as an alias for clarity.

### Insertion point for `get_user_species`
Insert the new function **between `get_user_track` and `ask_play_again`** (i.e., after line
131, before line 134). Rationale: the round-flow order in `main.py` is
`get_user_track` → `get_user_species` → `get_user_bet`, so matching that order in
`dialogs.py` is the most readable arrangement. `ask_play_again` stays last because it is
not part of the setup sequence.

---

## 2. `get_user_bet` refactor map

### Module-level layout constants
Move the existing `grid_layout` local variable (currently `dialogs.py:29–34`) to
module-level as `_TURTLE_GRID_LAYOUT`. Place `_SNAKE_ROW_LAYOUT` immediately below it.
Both names follow the existing convention of leading-underscore for module-private symbols
(see `CONVENTIONS.md`: `_screen`, `_window_w`, `_window_h` in `race.py`/`tracks.py`).

Suggested placement: after the import block, before `get_user_bet` (around line 10).

```python
# 2×2 grid: positional order matches asset filename position hints.
_TURTLE_GRID_LAYOUT = [
    ("Leonardo",      1, 0),
    ("Donatello",     1, 1),
    ("Raphael",       2, 0),
    ("Michaelangelo", 2, 1),
]

# 1×3 row: SNAKE_NAMES order (Shadow | Ralph | Anaconda).
_SNAKE_ROW_LAYOUT = [
    ("Shadow",    1, 0),
    ("Ralph",     1, 1),
    ("Anaconda",  1, 2),
]
```

The tuple shape `(name, row, col)` is identical between the two layouts, so the loop
body inside `get_user_bet` can be written once and shared across branches (or kept
parallel for clarity — Decision 2 accepts either).

### Label text per species
- Turtles: `"Which turtle do you think will win the race?"` (unchanged from current)
- Snakes: `"Which snake do you think will win the race?"`

These are the smallest correct changes; they differ only in the species word.

### Image source
- Turtles branch: `SPECIES[species]["images"][name]` — resolves to `TURTLE_IMAGES[name]`
  at runtime. Consistent with using `SPECIES` as the single dispatch table.
- Snakes branch: `SPECIES[species]["images"][name]` — resolves to `SNAKE_IMAGES[name]` at
  runtime. Same expression; no special-casing needed.

Both require `resource_path()` wrapping, then PIL `Image.open(...).resize(...)`. Snakes are
1024×1024 RGBA PNGs; turtles are square JPGs (dimensions not directly verified in pixels,
but they are resized to `BET_IMAGE_SIZE` × `BET_IMAGE_SIZE` via `Image.LANCZOS` today
without issue, so the turtle JPGs are at least `BET_IMAGE_SIZE` in both dimensions).

### Bet-index computation
Replace the current `TURTLE_NAMES.index(name)` with:
```python
species_names = SPECIES[species]["names"]
idx = species_names.index(name)   # 0-based
# ...
make_cb(idx + 1)                  # 1-based, same as current convention
```

This produces:
- Turtles: same 1-based indices as today (Raphael=1, Michaelangelo=2, Leonardo=3,
  Donatello=4 — i.e., positional in `TURTLE_NAMES`).
- Snakes: Shadow=1, Ralph=2, Anaconda=3 — positional in `SNAKE_NAMES`.

The `make_cb` closure pattern at lines 47–51 is unchanged.

### `_bet_images` retention
`dialog._bet_images = []` at line 37 continues to work for both branches. No change needed.

### Function-length estimate
The refactored `get_user_bet(species)` will be approximately 65–75 lines: ~10 for the
shared setup (Toplevel, label, image list), ~25 per branch (layout iteration), ~10 for
centering + modal boilerplate. Well within CONTEXT-3's ~100-line budget.

---

## 3. `get_user_species` new function — design

### Outer state pattern
`selected = [None]` mutable list — identical to both `get_user_bet` (line 12) and
`get_user_track` (line 78). The closure mutation pattern (`selected[0] = value`) is
established and must be preserved.

### Button layout
Two buttons in **one row**: `column=0` for Turtles, `column=1` for Snakes.
`columnspan=2` on the label at `row=0`. Buttons at `row=1`. This matches
`get_user_track`'s structure (label row 0, buttons row 1, three columns there).

### Button labels
- `"Turtles"` (`compound="top"`, image above label)
- `"Snakes"` (`compound="top"`, image above label)

Consistent with existing convention in `get_user_bet` (character name below image) and
`get_user_track` (track name below image).

### Dialog title
`"Turtle Race"` — same as `get_user_bet`. Alternatively `"Choose Species"` for
clarity. Either is acceptable; the architect decides.

### Composite image construction
Per CONTEXT-3 Decision 1, the images are composites built at dialog-open time via Pillow.
CONTEXT-3 says a helper `_compose_grid(image_paths, rows, cols, cell_size)` is optional —
the architect decides inline vs. helper.

The function must:
1. Compose the turtle 2×2 composite (cell size = `SPECIES_DIALOG_IMAGE_SIZE // 2 = 100`).
2. Compose the snake 1×3 composite (cell size = `SPECIES_DIALOG_IMAGE_SIZE // 3 ≈ 66`).
3. Resize each composite to `SPECIES_DIALOG_IMAGE_SIZE` × `SPECIES_DIALOG_IMAGE_SIZE`.
4. Convert to `ImageTk.PhotoImage`.
5. Store both refs on `dialog._species_images = []` (append both).

### Modal/centering boilerplate
Copy verbatim from `get_user_track` (lines 122–129):
```python
dialog.update_idletasks()
w, h = dialog.winfo_width(), dialog.winfo_height()
x = (dialog.winfo_screenwidth() - w) // 2
y = (dialog.winfo_screenheight() - h) // 2
dialog.geometry(f"+{x}+{y}")

dialog.grab_set()
dialog.wait_window()
```

### Return values
`"turtles"` or `"snakes"` — must match `SPECIES` keys exactly (confirmed: `constants.py:39-54`
shows keys are `"turtles"` and `"snakes"`).

---

## 4. Image composition strategy

### Turtle JPG dimensions
Not directly read in pixels, but `dialogs.py:42-43` currently opens and resizes them to
`140 × 140` via `Image.LANCZOS` without error — confirming they are at least 140 px in
both dimensions. [Inferred] They are likely 500–1000 px square based on typical asset
conventions; exact dimensions do not matter because PIL handles arbitrary source sizes.

### Snake PNG dimensions
Confirmed 1024×1024 RGBA from ROADMAP.md Phase 3 Risks section ("PNGs are 1024×1024").

### Mode mismatch: RGB vs RGBA
Turtle JPGs are RGB. Snake PNGs are RGBA. The blank canvas for composition should be
`Image.new("RGBA", ...)` to support RGBA snake paste correctly. Before pasting turtle
images onto an RGBA canvas, convert them: `img.convert("RGBA")`. Alternatively, create
a separate canvas mode per composite. The `Image.paste` call with an RGBA source uses the
alpha channel as a mask automatically if the destination is also RGBA.

**Concrete recommendation:**
- Turtle 2×2 composite canvas: `Image.new("RGBA", (200, 200), (0, 0, 0, 0))`
- For each turtle cell: `img.convert("RGBA")` before `paste()`.
- Snake 1×3 composite canvas: `Image.new("RGBA", (198, 66), (0, 0, 0, 0))` (3×66 wide,
  66 tall — then resize to 200×200).
- Final step for both: `composite.resize((SPECIES_DIALOG_IMAGE_SIZE, SPECIES_DIALOG_IMAGE_SIZE), Image.LANCZOS)` — this produces a square 200×200 regardless of source aspect ratio. The snake composite starts as 3:1 wide so squashing it to 200×200 compresses it — this is acceptable (species buttons convey the group, not individual portraits) and is symmetric with how the 2×2 turtle composite works.

### Cell sizes
- Turtle 2×2: cell = `SPECIES_DIALOG_IMAGE_SIZE // 2 = 100` px per cell; canvas = 200×200.
- Snake 1×3: cell = `SPECIES_DIALOG_IMAGE_SIZE // 3 = 66` px wide × 66 px tall; raw canvas
  = 198×66; resize to 200×200. (Using 66 rather than 67 to avoid fractional math; the
  2-px shortfall disappears in the LANCZOS resize.)

### Helper vs. inline
CONTEXT-3 Decision 1 explicitly says architect decides. Research recommendation: expose
`_compose_grid(image_paths, rows, cols, cell_size)` as a module-private helper. It is
~10 lines, called twice with different arguments, and its logic (nested paste loop) is
non-obvious enough to warrant a name. Two call sites is enough to justify extraction.
Inline would also work given Decision 2 (parallel implementations).

---

## 5. `main.py` changes

### Current round-loop lines (main.py:27–34)
```python
track_name = dialogs.get_user_track()                     # line 27
racers = race.create_racers("turtles")                    # line 28  ← "turtles" hardcoded
race.draw_boundary_stones(track_name, len(racers))        # line 29  ← len(racers) #1
race.place_racers_on_track(racers, track_name)            # line 30
race.draw_start_line(track_name, len(racers))             # line 31  ← len(racers) #2
race.draw_finish_line(track_name, len(racers))            # line 32  ← len(racers) #3

user_bet = dialogs.get_user_bet()                         # line 34  ← no arg
```

### Required changes per CONTEXT-3 Decision 5
```python
track_name = dialogs.get_user_track()
species    = dialogs.get_user_species()                   # NEW — between track and create_racers
racers     = race.create_racers(species)                  # "turtles" literal → species variable
n          = len(racers)                                  # S2.2 hoist (SIMPLIFICATION-2)
race.draw_boundary_stones(track_name, n)
race.place_racers_on_track(racers, track_name)
race.draw_start_line(track_name, n)
race.draw_finish_line(track_name, n)

user_bet   = dialogs.get_user_bet(species)                # species arg added
```

### `n = len(racers)` hoist
Straightforward. Three consecutive `len(racers)` calls at lines 29, 31, 32 (all pass `n`
to `race.*` functions). Adding `n = len(racers)` on line 29.5 and replacing all three is a
3-line edit. CONTEXT-3 Decision 5 explicitly endorses this as "opportunistic S2.2 fix."

### `create_racers` docstring
DOCUMENTATION-2 flags the docstring at `race.py:136-138` as incomplete. Phase 3 is the
right time to update it (the docstring currently says `"turtles"` only; after Phase 3,
`species` is a runtime-dynamic argument). Architect to include this as a sub-task.
Suggested text is already drafted in `DOCUMENTATION-2.md` lines 49–61.

### No import changes needed in `main.py`
`dialogs.get_user_species()` is already accessible via the existing `import dialogs` at
line 9. No new imports required.

---

## 6. `constants.py` change

### Current `BET_IMAGE_SIZE` location
`constants.py:25` — `BET_IMAGE_SIZE = 140  # px, square — used by the bet dialog`

### Insertion point for `SPECIES_DIALOG_IMAGE_SIZE`
Insert immediately after `BET_IMAGE_SIZE` on line 25, making it line 26:
```python
BET_IMAGE_SIZE = 140             # px, square — used by the bet dialog
SPECIES_DIALOG_IMAGE_SIZE = 200  # px, square — used by the species-selection dialog
```

Placing it adjacent groups all dialog-image-size constants together, consistent with the
existing organization (window constants together, track layout constants together). No
other constant needs to move.

---

## 7. `tests/test_constants.py` impact

### Current test for `BET_IMAGE_SIZE` — line 23
```python
def test_bet_image_size_is_positive_int():
    assert isinstance(BET_IMAGE_SIZE, int)
    assert BET_IMAGE_SIZE > 0
```

### Recommendation: ADD the mirror test
Add `test_species_dialog_image_size_is_positive_int`. Reasons:

1. Mirrors an existing pattern exactly — trivial to add (3 lines).
2. `SPECIES_DIALOG_IMAGE_SIZE` is used in `_compose_grid` as a divisor (`// 2`, `// 3`);
   a non-integer or zero would cause a runtime error or silent misbehavior.
3. The test file already imports a growing list of constants; the new constant should be
   added to the import line anyway to signal it is covered.
4. CONTEXT-3 Decision 7 calls it "non-blocking either way" — but given the near-zero cost,
   include it.

New test:
```python
def test_species_dialog_image_size_is_positive_int():
    assert isinstance(SPECIES_DIALOG_IMAGE_SIZE, int)
    assert SPECIES_DIALOG_IMAGE_SIZE > 0
```

The import line at `test_constants.py:7` must also add `SPECIES_DIALOG_IMAGE_SIZE`:
```python
from constants import (
    TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE, SPECIES_DIALOG_IMAGE_SIZE,
    SNAKE_NAMES, SNAKE_COLORS, SNAKE_LENGTHS, SNAKE_IMAGES, SPECIES,
)
```

---

## 8. Phase 3 end-state runtime smoke checklist

Minimal manual verification after Phase 3 lands. All 6 `(track × species)` permutations
are the full gate (ROADMAP Phase 3 success criteria), but the *minimal* checklist for a
first pass:

### Turtles mode (regression check)
1. Launch `python main.py`.
2. Track dialog opens. Pick **Straight**.
3. Species dialog opens. Pick **Turtles**.
4. Bet dialog opens — 2×2 grid of 4 turtle buttons, images visible (not blank). Pick any.
5. Race runs. 4 turtle-shaped racers cross finish. Podium appears.
6. "Play again?" → Yes. Confirm no crash, no blank images on repeat.

### Snakes mode (new path)
1. Launch `python main.py`.
2. Track dialog. Pick **Straight**.
3. Species dialog. Pick **Snakes**.
4. Bet dialog opens — **1×3 row** of 3 snake buttons, snake PNG images visible (not blank).
   Pick any.
5. Race runs. **3** turtle-shaped racers (snake colors: black, `#E89F4F`, green) cross
   finish. Podium appears with 3 entries.
6. "Play again?" → Yes. Round 2: pick Snakes again. Confirm no image-GC blanking on
   second open.

### Cross-species switching (state-leak check)
1. Round 1: Turtles → Straight → any bet → complete race.
2. Round 2: Snakes → Rectangular → any bet → complete race.
3. Round 3: Turtles → Spiral → any bet → complete race.
4. Confirm: no crashes, no image blanking, no stale turtle shapes in snake round, no
   wrong racer count.

---

## 9. Tk image-reference retention discipline

### Existing pattern (MUST mirror exactly)
- `get_user_bet`: `dialog._bet_images = []` at line 37 → `.append(photo)` at line 45.
- `get_user_track`: `dialog._track_images = []` at line 92 → `.append(photo)` at line 103.

### Phase 3 additions
**`get_user_species`:**
```python
dialog._species_images = []
# ... after creating each PhotoImage:
dialog._species_images.append(photo)
```
Two images are stored (one turtle composite + one snake composite), both appended before
`grab_set()`.

**`get_user_bet` snake branch:**
`dialog._bet_images = []` is set once at the top of the function (before the if/elif), so
both branches append to the same list. No change to the retention mechanism — the
if/elif only changes which images are loaded, not the retention pattern.

### Why this matters — concrete failure mode
`PhotoImage` objects are reference-counted by Python + Tk. If `dialog` is destroyed
(`dialog.destroy()` inside a button callback) while the only reference is a local
variable, the image becomes a blank (gray) square or disappears entirely before it is
rendered, depending on GC timing. Stashing on the dialog object keeps the reference alive
until `wait_window()` returns. After that, `dialog` goes out of scope but the images have
already been rendered and the dialog is closed, so GC is safe. Do not use a module-level
list — that would leak across rounds.

---

## 10. Files-affected list for Phase 3

| File | Change type | Summary |
|------|-------------|---------|
| `dialogs.py` | Modify | Add `get_user_species()`; refactor `get_user_bet()` → `get_user_bet(species)`; promote `grid_layout` → `_TURTLE_GRID_LAYOUT`; add `_SNAKE_ROW_LAYOUT`; update imports |
| `main.py` | Modify | Insert `species = dialogs.get_user_species()`; replace `"turtles"` literal with `species`; add `n = len(racers)` hoist; add `species` arg to `get_user_bet(species)` |
| `constants.py` | Modify | Add `SPECIES_DIALOG_IMAGE_SIZE = 200` after `BET_IMAGE_SIZE` |
| `tests/test_constants.py` | Modify (recommended) | Add `test_species_dialog_image_size_is_positive_int`; update import line |
| `race.py` | Modify (optional) | Update `create_racers` docstring per DOCUMENTATION-2 recommendation |
| `turtle_race.spec` | No change | Snake PNGs already registered: `('assets/snakes/*.png', 'assets/snakes')` confirmed at spec line 7 |

**Create:** none. **Delete:** none.

---

## 11. Phase 3 gotchas — architect risk notes

### G1: Tk modal correctness — third dialog with the same pattern
**Risk:** A subtle mistake in `grab_set` / `wait_window` / `WM_DELETE_WINDOW` no-op
ordering can produce a dialog that: (a) does not block the round loop, (b) can be
closed via the window manager returning `None`, or (c) steals focus incorrectly.
**Mitigation:** Copy the boilerplate block verbatim from `get_user_track` (lines 83,
122–129) — do not rewrite from memory. The three-statement modal sequence
(`protocol` → `grab_set` → `wait_window`) must appear in that order after all widgets
are created and the window is positioned.

### G2: Image-ref retention on `get_user_species`
**Risk:** Forgetting `dialog._species_images = []` causes blank species buttons, which
is visually broken but does not crash — making it easy to miss in a smoke test.
**Mitigation:** Add `dialog._species_images = []` as the first statement after
`dialog = tkinter.Toplevel()`, mirroring the pattern at `dialogs.py:37`.

### G3: Image-ref retention on the snake branch of `get_user_bet`
**Risk:** Same as G2, but for the snake bet buttons. Since `_bet_images = []` is set
before the if/elif branch, both branches use the same list — this is safe. Risk is
only present if the architect mistakenly moves the `_bet_images` initialization inside
one branch.
**Mitigation:** Initialize `dialog._bet_images = []` before the `if bet_layout ==`
block, not inside either branch.

### G4: 1×3 snake bet row width
**Risk:** 3 buttons × (`BET_IMAGE_SIZE` + 2×`padx`) = 3 × (140 + 24) = 492 px. On a
standard 1920-wide screen this is fine. On a low-res display (≤800 px wide) the dialog
could clip. `dialog.resizable(False, False)` means it won't adapt.
**Mitigation:** Keep `padx=12` (matching the turtle bet dialog) — total = 3×164 = 492 px,
well within any modern display. No action needed unless targeting sub-HD screens.

### G5: PIL `paste` mode mismatch (RGB turtle JPG onto RGBA canvas)
**Risk:** `Image.paste(rgb_img, pos)` onto an `RGBA` canvas silently ignores the alpha
channel of the canvas at the paste position, replacing it with fully opaque. This is
actually the desired behavior (turtle images have no transparency). The actual risk is
the reverse: pasting an RGBA source onto an RGB canvas raises a `ValueError` in some
Pillow versions.
**Mitigation:** Create both composite canvases as `"RGBA"`. Convert turtle images with
`img.convert("RGBA")` before pasting. Snake PNGs are already RGBA and paste correctly.

### G6: `get_user_species` returning unexpected values → `KeyError` in `create_racers`
**Risk:** If `get_user_species` has a bug where `selected[0]` is never set (e.g., the
modal closes without a click — impossible with the no-op `WM_DELETE_WINDOW`, but worth
noting), `species` would be `None`, and `race.create_racers(None)` would raise
`KeyError: None` with no helpful message.
**Mitigation:** `get_user_species` uses `protocol("WM_DELETE_WINDOW", lambda: None)` so
the window cannot be closed without a button click. However, the architect should confirm
the function never returns `None` — either by assertion (`assert selected[0] is not None`)
or by structuring the button callbacks so `selected[0]` is always set before
`dialog.destroy()`. The latter is already guaranteed by the `make_cb` pattern.

### G7: `main.py` call-site signature mismatch on `get_user_bet`
**Risk:** `get_user_bet()` is called at `main.py:34` with no arguments today. Changing
the signature to `get_user_bet(species)` without updating the call site produces
`TypeError: get_user_bet() missing 1 required positional argument: 'species'` on the
first run. This is an easy break that shows up immediately.
**Mitigation:** Update `main.py:34` to `dialogs.get_user_bet(species)` atomically with
the `dialogs.py` signature change in the same commit. The AUDIT-2.md already flags this
exact call site (`main.py:28` in Phase 2 numbering, now line 34).

### G8: `n = len(racers)` hoist ordering — `draw_boundary_stones` must follow `create_racers`
**Risk:** In the current `main.py`, `draw_boundary_stones` is at line 29 — immediately
after `create_racers` (line 28). The CONTEXT-3 decision-5 call order places
`get_user_species()` between `get_user_track()` and `create_racers()`. The boundary
stones call already comes after `create_racers`, so the hoist is clean. But if the
architect reorders to place boundary stones before `create_racers`, `n` would be
undefined at that point.
**Mitigation:** Keep the order: `create_racers` → `n = len(racers)` → all `race.*`
track-drawing calls. This is the order shown in CONTEXT-3 Decision 5's pseudocode.

---

## Sources

All findings are from direct codebase reads — no web sources consulted. Files read:

1. `dialogs.py` (lines 1–136)
2. `main.py` (lines 1–51)
3. `constants.py` (lines 1–62)
4. `race.py` (lines 1–239, read in two passes)
5. `tests/test_constants.py` (lines 1–84)
6. `turtle_race.spec` (lines 1–32)
7. `.shipyard/phases/3/CONTEXT-3.md` (lines 1–102)
8. `.shipyard/ROADMAP.md` (lines 1–165)
9. `.shipyard/codebase/STRUCTURE.md` (lines 1–209)
10. `.shipyard/codebase/CONVENTIONS.md` (lines 1–106)
11. `.shipyard/phases/2/results/AUDIT-2.md` (lines 1–86)
12. `.shipyard/phases/2/results/SIMPLIFICATION-2.md` (lines 1–53)
13. `.shipyard/phases/2/results/DOCUMENTATION-2.md` (lines 1–144)
14. `assets/` glob — confirmed snake PNGs at `assets/snakes/{Shadow,Ralph,Anaconda}.png`

---

## Uncertainty Flags

### U1: Turtle JPG exact pixel dimensions
The turtle JPG dimensions were not directly measured (Pillow `Image.open().size` not
called). The only confirmed fact is they are square enough to be resized to 140×140
without error. For the species composite, the architect should verify that
`img.convert("RGBA")` works on these JPGs (it does for all standard JPEGs — [Inferred]).
If the architect wants exact dimensions for documentation, run:
```python
from PIL import Image
print(Image.open("assets/turtle_1_leonardo_top_left.jpg").size)
```

### U2: Snake PNG alpha compositing on the species button background
The species dialog uses a `Toplevel` with the OS default background color. Snake PNGs
are 1024×1024 RGBA — if a snake PNG has transparent regions, the transparent areas will
show the dialog background color (typically gray) after `ImageTk.PhotoImage` conversion.
This may look acceptable or may look odd depending on the PNG content. No visual
inspection was performed. If the result is unacceptable, the fix is to pre-fill the
composite canvas with the dialog's background color instead of transparent black
(`(0,0,0,0)` → e.g., `(240,240,240,255)` for typical Windows Tk gray).

**Decision Required:** Architect should note this as a visual QA point during smoke
testing and decide whether to handle it pre-emptively or reactively.

### U3: `SPECIES_DIALOG_IMAGE_SIZE` divisor correctness for snake composite
`200 // 3 = 66` (not 67). The snake composite canvas would be 198 wide × 66 tall, then
resized to 200×200. The 2-px shortfall is absorbed by LANCZOS resize and is visually
imperceptible. However, if the architect prefers exact math, `cell_width = 67` makes the
canvas 201 wide, and the resize still produces 200×200. Either is correct; the 2-px
difference disappears in the resize step.
