# Phase 1 Research — Snake constants & `SPECIES` config foundation

## 1. `constants.py` shape (current state)

**Path:** `constants.py` — 34 lines, no imports, pure data module.

Current ordering:
- Line 8: `TURTLE_COLORS = ["red4", "DarkOrange", "blue", "DarkMagenta"]`
- Line 9: `TURTLE_NAMES = ["Raphael", "Michaelangelo", "Leonardo", "Donatello"]`
- Lines 11-17: `WINDOW_WIDTH=500`, `WINDOW_HEIGHT=400`, `SPACING=30`, `TURTLE_LENGTH=40`, `TURTLE_HEIGHT=10`, `MAX_PACE=10`, `TICK_DELAY=0.01`
- Lines 19-24: `TURTLE_IMAGES` dict
- Line 25: `BET_IMAGE_SIZE = 140`
- Lines 27-33: track layout constants (`N_LANES=4`, `TRACK_PADDING`, `LANE_SPACING`, `SPIRAL_STEP`, `TRACK_PREVIEW_W/H`)

**Insertion point for snake constants:** after `BET_IMAGE_SIZE` (line 25), before `# Track layout` (line 27).

**Important finding:** `N_LANES = 4` already exists. Phase 2's "parameterize on N" work will need to either remove this constant or treat it as a default/fallback. Out of scope for Phase 1 but worth flagging.

Proposed Phase 1 block:
```python
# --- Snake racer identity ---
SNAKE_NAMES   = ["Shadow", "Ralph", "Anaconda"]
SNAKE_COLORS  = ["black", "#E89F4F", "green"]    # positional with SNAKE_NAMES; Ralph hex per CONTEXT-1.md
SNAKE_LENGTHS = [6, 2, 5]                         # positional with SNAKE_NAMES; 6:5:2 ratio is Shadow:Anaconda:Ralph by value
SNAKE_IMAGES  = {
    "Shadow":   "assets/snakes/Shadow.png",
    "Ralph":    "assets/snakes/Ralph.png",
    "Anaconda": "assets/snakes/Anaconda.png",
}
L_BASE = 1.0   # placeholder — tuned visually in Phase 4

# --- Species config ---
SPECIES = {
    "turtles": {
        "names":        TURTLE_NAMES,
        "colors":       TURTLE_COLORS,
        "images":       TURTLE_IMAGES,
        "bet_layout":   "grid_2x2",
        "shape_drawer": "turtle",
    },
    "snakes": {
        "names":        SNAKE_NAMES,
        "colors":       SNAKE_COLORS,
        "images":       SNAKE_IMAGES,
        "bet_layout":   "row_3",
        "shape_drawer": "snake",
    },
}
```

`SNAKE_LENGTHS` is **not** inside `SPECIES` — the turtles entry has no `lengths` analog, and embedding it would create schema asymmetry. Phase 4's `create_racers` reads `SNAKE_LENGTHS[i]` directly by index.

## 2. `turtle_race.spec` — existing `datas=` syntax

**Path:** `turtle_race.spec` — line 7.

Current:
```python
datas=[('lawn.jpg', '.'), ('assets/*.jpg', 'assets'), ('assets/*.mid', 'assets'), ('assets/*.png', 'assets')],
```

Pattern: `(source_glob, destination_folder)`, all on one line.

**Critical finding:** `('assets/*.png', 'assets')` does NOT recurse into subdirectories. The new entry is genuinely additive:

```python
datas=[..., ('assets/snakes/*.png', 'assets/snakes')],
```

Destination `'assets/snakes'` → files land at `<_MEIPASS>/assets/snakes/`, matching `SNAKE_IMAGES` path prefix exactly. No path-resolution mismatch.

## 3. `tests/test_constants.py` — current patterns

**Path:** `tests/test_constants.py` — 26 lines, 3 tests.

Existing patterns:
- Module-level `sys.path.insert` makes project root importable
- Plain `def test_*` functions, no fixtures, no parametrize
- Imports specific names (`from constants import TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE`)
- Disk-exists test (line 16-20) uses manual `project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` — **does NOT use `paths.resource_path()`**. Mirror this. The new snake test must use the same manual project_root pattern, not import `paths`.

**Tests to add (mirroring existing style):**
- `test_snake_lists_are_length_3` — `SNAKE_NAMES`, `SNAKE_COLORS`, `SNAKE_LENGTHS` all length 3
- `test_snake_image_map_has_entry_for_every_snake_name` — `set(SNAKE_IMAGES.keys()) == set(SNAKE_NAMES)`
- `test_snake_lengths_positional_values` — name-keyed: Shadow=6, Ralph=2, Anaconda=5
- `test_snake_image_files_exist_on_disk` — manual project_root pattern
- `test_species_has_required_top_level_keys` — `{"turtles", "snakes"}`
- `test_species_entries_have_required_sub_keys` — `{"names","colors","images","bet_layout","shape_drawer"}` ⊆ each entry's keys
- `test_species_bet_layout_values_are_valid` — ∈ `{"grid_2x2", "row_3"}`
- `test_species_racer_counts` — turtles=4, snakes=3
- `test_species_shape_drawer_is_string_sentinel` — `isinstance(str)` and ∈ `{"turtle", "snake"}`

Imports to add: `SNAKE_NAMES`, `SNAKE_COLORS`, `SNAKE_LENGTHS`, `SNAKE_IMAGES`, `SPECIES`.

## 4. `paths.py` (`resource_path`)

```python
def resource_path(rel_path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)
```

In dev (no `_MEIPASS`), `base` resolves to the project root (paths.py sits there). `resource_path("assets/snakes/Shadow.png")` resolves correctly.

**Not used in tests** — see Section 3. Test the file existence with manual project_root, not `resource_path()`.

## 5. Files-affected list

**Modify (3):**
- `constants.py` — add snake block + `SPECIES` between line 25 and line 27
- `turtle_race.spec` — extend `datas=` at line 7
- `tests/test_constants.py` — extend imports, add 9 test functions

**Create (0):** Phase 1 creates no new files.

**`git add` (3, currently untracked):**
- `assets/snakes/Shadow.png`
- `assets/snakes/Ralph.png`
- `assets/snakes/Anaconda.png`

## 6. Snake PNG verification

All three files present at `assets/snakes/{Shadow,Ralph,Anaconda}.png`. Dimensions previously confirmed as 1024×1024 RGBA. Visual content: square-format cartoon snakes — Shadow grey-blue, Ralph vivid orange, Anaconda green.

## 7. Gotchas for the architect

1. **`SNAKE_LENGTHS` order vs. ratio:** list is positional `[6, 2, 5]` (Shadow, Ralph, Anaconda) but the 6:5:2 ratio is by-name (Shadow:Anaconda:Ralph). Easy to reverse. Lock with name-keyed test.
2. **Shadow PNG vs. `SNAKE_COLORS[0]="black"`:** PNG art is grey-blue; constant is "black". Constant drives Phase 4's in-race `turtle.color()`, PNG drives bet-dialog only. Not a Phase 1 conflict — document for Phase 4.
3. **`SPECIES` reference order:** snake constants must be defined above `SPECIES` in the file. Insertion order above satisfies this.
4. **No `SNAKE_LENGTHS` in `SPECIES`:** keeps the schema symmetric between species; Phase 4 reads it by index directly.
5. **`assets/*.png` glob does not recurse:** the new `('assets/snakes/*.png', 'assets/snakes')` tuple is required, not redundant. Without it the frozen exe will crash at the snake bet dialog with a missing-file error.
6. **`test_constants.py` imports must extend, not replace** the existing import line.
7. **TDD order from ROADMAP:** tests first → constants → SPECIES test → SPECIES dict. Don't collapse into a single step.

## Uncertainty flags

- **`L_BASE` testing:** Phase 1 introduces the name but doesn't tune it. Recommend NO test on `L_BASE` value in Phase 1 (only Phase 4 should constrain it). Architect to confirm.
- **PNG dimension tests:** existing tests avoid Pillow imports. Adding a `(1024, 1024)` dimension assertion would force a `from PIL import Image` import. Recommend skipping dimension tests in Phase 1 — file-exists is sufficient invariant coverage.
