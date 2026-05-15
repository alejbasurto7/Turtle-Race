# Phase 4 Research — Snake shape, length, head-finish detection

## 1. Current `create_racers(species)` body

**File:** `race.py:135-157`

```python
def create_racers(species: str):
    """..."""
    # Shape dispatch (shape_drawer sentinel) is Phase 4's concern.
    data = SPECIES[species]
    racers = []
    for name, color in zip(data["names"], data["colors"]):
        racers.append({'name': name, 'color': color, 'o': Turtle(shape="turtle")})
    return racers
```

Shape setup is inline — `Turtle(shape="turtle")`. Color is assigned later in `place_racers_on_track` (line 166: `racer['o'].color(racer['color'])`).

**Phase 4 refactor:** extract the shape setup into a per-species drawer. Read `SPECIES[species]["shape_drawer"]` (string sentinel — `"turtle"` or `"snake"`), look up the callable from a module-level `_SHAPE_DRAWERS` dict, call it on a freshly-constructed `Turtle()`. For snakes, pass `SNAKE_LENGTHS[i]` too.

## 2. `run_race` finish-detection mechanism

**File:** `race.py:175-256` (full function). Key lines:

- **Line 188:** `n = len(racers)`
- **Line 189-193:** lane paths and shared_distance setup
- **Line 194:** `progress = [0.0] * len(racers)` — per-racer progress along their lane (in shared_distance units)
- **Line 217-233:** the race loop body. Per-tick advance:
  - Line 220: `step = random.randint(0, MAX_PACE)` — random per-tick advance
  - Line 222: `progress[i] = min(progress[i] + step, shared_distance)` — clamp at goal
  - Line 223: `fraction = progress[i] / shared_distance`
  - Line 224: `arc = fraction * lane_lengths[i]` — physical arc length along this racer's lane
  - Line 225: `x, y, heading = tracks.position_at_arc(lane_paths[i], arc)` — center position + heading
  - Line 227: `turtle['o'].goto(x, y)` — places the racer at the lane-center position
  - Line 228: **the finish check:** `if progress[i] >= shared_distance` — i.e., when `progress[i]` hits the cap (clamped to `shared_distance` on line 222)

**Critical insight:** the finish check is on `progress[i]`, NOT on screen position. So the "head vs. center" question is really about **when does `progress[i]` cap?** Currently it caps when `progress[i] + step ≥ shared_distance`. For head-position fairness, we want the snake's HEAD to reach the goal position, not its center.

**Head-position offset implementation:**

Two equivalent approaches:

- **(A) Position-based:** compute `head_x, head_y` from `x, y + (head_offset * cos/sin(heading))`. Check if head crosses the finish line geometry. **Doesn't work cleanly** because the finish detection is on `progress`, not screen position.

- **(B) Progress-based:** lengthen the effective lane by the head-offset. Equivalently, finish when `progress[i] >= shared_distance - head_offset_in_progress_units`. This is consistent with how `progress` is the proxy for "how far along the path."

Approach (B) is simpler and integrates with the existing loop structure. The conversion is:

```python
head_offset_arc = (stretch_len * shape_unit_size / 2)   # half the length, in arc/pixel units
head_offset_progress = head_offset_arc * (shared_distance / lane_lengths[i])
# Finish when progress[i] >= shared_distance - head_offset_progress
```

For turtles (where `stretch_len = 1`), `head_offset_arc ≈ 5px` (half of 10px classic length). For snakes (e.g., Shadow at stretch_len = 3.6), `head_offset_arc ≈ 18px`.

**Edge case:** at the moment of finish, the racer's center is at `(arc = lane_length - head_offset_arc)`. The head visually crosses the finish line. The `goto(x, y)` still places the CENTER at that position — the head is rendered ahead of center based on heading. ✓ Consistent.

**Simpler alternative (recommended for Phase 4):** sub-tract a single `head_offset_progress` per racer from `shared_distance` in the comparison, computed once per race-start from each racer's current stretch_len. Document the formula and tune if needed.

## 3. `turtle.shapesize` and the `classic` shape

**Default `classic` polygon (from Python's turtle module source):**
```
((0,0), (-5,-9), (0,-7), (5,-9))
```

Bounding box at `shapesize(1, 1)`: 10 wide (x in [-5, 5]) × 9 tall (y in [-9, 0]). The arrow points UP at default heading.

When `setheading(0)` is set (heading = East = +x), the turtle module rotates this polygon 90° clockwise so the apex points right (East). Effective dimensions at `setheading(0)`:
- Along heading (length / forward direction): 9 units (the polygon's original y-extent)
- Perpendicular to heading (width): 10 units (the original x-extent)

**Wait** — `stretch_len` stretches along the polygon's length (its y-axis in raw coords, BEFORE heading rotation). `stretch_wid` stretches along x-axis (width axis). So:

- `shape("classic")` + `shapesize(stretch_wid=W, stretch_len=L)`: shape becomes `10*W` wide and `9*L` tall in raw polygon space, then rotated by heading.

For Phase 4:
- `stretch_wid = 0.5` → effective width = 5 units (half default, slimmer than turtle classic)
- `stretch_len = L_BASE * length_units` with `L_BASE = 0.6`:
  - Shadow (length=6): stretch_len = 3.6 → effective body-length = 9 * 3.6 = **32.4 units** along heading
  - Anaconda (5): stretch_len = 3.0 → **27 units**
  - Ralph (2): stretch_len = 1.2 → **10.8 units**

Body lengths in the order Shadow > Anaconda > Ralph, ratio preserved. Visible against the 300-unit straight-track width.

**Head offset for the finish check** = half the body length along heading = `(9 * stretch_len) / 2` units.

## 4. `draw_turtle_shape` and `draw_snake_shape`

Place both functions near the top of `race.py` (above `create_racers`). Below them, define `_SHAPE_DRAWERS`.

```python
def draw_turtle_shape(t):
    t.shape("turtle")
    # (Color is applied later in place_racers_on_track.)

def draw_snake_shape(t, length_units):
    t.shape("classic")
    t.shapesize(stretch_wid=SNAKE_STRETCH_WID, stretch_len=L_BASE * length_units)

_SHAPE_DRAWERS = {
    "turtle": draw_turtle_shape,
    "snake":  draw_snake_shape,
}
```

## 5. `SHAPE_DRAWERS` invocation in `create_racers`

**Recommended approach:** uniform signature with optional length.

```python
def create_racers(species: str):
    data = SPECIES[species]
    drawer = _SHAPE_DRAWERS[data["shape_drawer"]]
    racers = []
    for i, (name, color) in enumerate(zip(data["names"], data["colors"])):
        t = Turtle()
        if species == "snakes":
            drawer(t, SNAKE_LENGTHS[i])
        else:
            drawer(t)
        racers.append({'name': name, 'color': color, 'o': t})
    return racers
```

The species-name branch in `create_racers` is small and clear. Alternative (uniform `drawer(t, length=None)`) is also fine; either reads OK. Architect's choice.

**Note on import:** add `SNAKE_LENGTHS` to `race.py`'s imports from `constants`.

## 6. Win-message fix (carry-forward item 3)

**Files:** `race.py:373-389` (`announce_result`) and `race.py:392-394` (`celebrate`).

Lines 375-379 use `winner.pencolor()` three times — fragile for Ralph (returns tuple). Line 394 uses `face_color = winner.pencolor()`, passed to `pen.color(face_color)` — that's safe (turtle.color accepts tuples).

**Cleanest fix:** change `run_race` to return the winner's INDEX (or racer dict) in addition to the turtle. Then `announce_result(winner, user_bet, racers)` becomes `announce_result(winner_idx, user_bet, racers)` and reads `racers[winner_idx]['name']` and `racers[winner_idx]['color']` directly.

But that's a wide change. **Simpler fix:**

```python
def announce_result(winner, user_bet, racers):
    # Find the racer dict matching the winning turtle.
    winner_racer = next(r for r in racers if r['o'] is winner)
    won = winner_racer['o'] is racers[user_bet - 1]['o']    # identity, not pencolor()
    color_display = winner_racer['color']                    # original config string
    name = winner_racer['name']
    ...
```

This uses `is` for identity comparison (fixes pre-existing pencolor() fragility too — main.py:38 win-check), and the configured color string for display. Same fix pattern for `celebrate`'s `face_color`.

`main.py:40` also uses pencolor() == pencolor() for user_won — should switch to `is` identity. **In scope for Phase 4** since we're touching the win logic anyway.

## 7. Carry-forward cleanups — exact line edits

### 7a. `dialogs.py` stale imports — line 8

Current:
```python
from constants import TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE, SPECIES, SPECIES_DIALOG_IMAGE_SIZE
```

`TURTLE_NAMES` and `TURTLE_IMAGES` are not referenced anywhere in `dialogs.py` after the Phase 3 refactor (verified by grep). `_TURTLE_GRID_LAYOUT` hardcodes the names as literals; `SPECIES["turtles"]["images"]` is accessed via the dict.

`SNAKE_NAMES` — not currently imported and not currently used (`_SNAKE_ROW_LAYOUT` also hardcodes the names). Adding it for symmetry is optional; if `_SNAKE_ROW_LAYOUT` doesn't reference it, importing creates an unused-name flake8 hit. **Recommendation: drop `TURTLE_NAMES` and `TURTLE_IMAGES`, do NOT add `SNAKE_NAMES`.** Less symmetric but truly minimal imports.

### 7b. `get_user_species()` docstring — `dialogs.py:194`

Add:
```python
def get_user_species():
    """Modal dialog: ask the user to pick between Turtles and Snakes.

    Blocks (via grab_set() + wait_window()) until the user clicks one of the
    two species buttons. The WM_DELETE_WINDOW handler is a no-op, so the
    dialog cannot be dismissed without making a choice.

    Returns:
        str: ``"turtles"`` or ``"snakes"`` — keys into ``constants.SPECIES``.
    """
```

### 7c. `tracks.py:_build_spiral_legs` `n` shadow

**File:** `tracks.py` around line 195 (the exact line in current state — grep first to confirm).

Current:
```python
for n in range(max_legs):
    pair_idx = n // 2
    ...
```

This `n` shadows the function parameter `n` (the lane count) introduced in Phase 2. Body uses inner `n` for loop counting. Risk: if a future edit touches code inside the loop and accidentally reads outer `n` (the lane count), it'll get the loop counter instead.

**Rename:** `for leg_i in range(max_legs):` then update internal references (`pair_idx = leg_i // 2` etc.). Confirm by grep that no other code in the loop body references the OUTER `n`.

## 8. Tests for Phase 4

- **`draw_snake_shape`** — untestable without a turtle screen. Smoke-only.
- **Head-offset math** — pure trig, testable:
  - `head_x = pos_x + offset * cos(radians(heading))` (heading in degrees, turtle convention)
  - `head_y = pos_y + offset * sin(radians(heading))`
  - Test at heading = 0 → head is at `(pos_x + offset, pos_y)`
  - Test at heading = 90 → head is at `(pos_x, pos_y + offset)`
  - Test at heading = 180 → head is at `(pos_x - offset, pos_y)`
  - Test at heading = 270 → head is at `(pos_x, pos_y - offset)`
  - If head-offset is folded into `progress`-based comparison (approach B), test the conversion: `head_offset_progress = head_offset_arc * (shared_distance / lane_length)`.
- **`L_BASE`, `SNAKE_STRETCH_WID` constants** — add `test_l_base_is_positive_float`, `test_snake_stretch_wid_is_positive_float`. Mirror `test_bet_image_size_is_positive_int` style.

Probably 2-3 new tests total.

## 9. Files-affected list for Phase 4

**Modify:**
- `race.py` — major: extract `draw_turtle_shape` + `draw_snake_shape`, define `_SHAPE_DRAWERS`, refactor `create_racers`, add head-offset to finish check, fix `announce_result` + `celebrate` to use racer dict
- `constants.py` — tune `L_BASE = 0.6`, add `SNAKE_STRETCH_WID = 0.5`
- `dialogs.py` — drop stale imports + add `get_user_species()` docstring
- `tracks.py` — rename `n` → `leg_i` in `_build_spiral_legs`
- `main.py` — change `user_won` from pencolor() == pencolor() to `is` identity comparison (fixes the same fragility one level up)
- `tests/test_constants.py` — add 2 trivial tests for `L_BASE` + `SNAKE_STRETCH_WID`
- Maybe `tests/test_race.py` (NEW) — head-offset math tests, OR put them in an existing test file

**Create:** maybe `tests/test_race.py` for head-offset trig tests.

**Delete:** none.

**PyInstaller spec:** unchanged.

## 10. Phase 4 gotchas

1. **`heading()` returns degrees in default turtle mode** — must convert via `math.radians()` for trig.
2. **`_SHAPE_DRAWERS` defined AFTER its constituent functions** — Python module-load order. Place at the bottom of the function definitions, BEFORE `create_racers` uses it.
3. **`announce_result` widening** — if the function signature changes (winner_idx added), `main.py` caller needs updating. Plan accordingly.
4. **Head-offset must be re-computed per racer per tick** if the shape changes mid-race. We don't change shapes mid-race, so compute once at race start. But heading does change — re-read `t.heading()` if doing position-based head check.
5. **Recommended: compute head_offset_progress ONCE per racer at race start** (after `place_racers_on_track`), based on the racer's initial `stretch_len`, and store in an array parallel to `progress[]`. Simpler than re-computing per tick.
6. **Polygon fallback (Decision 1 in CONTEXT-4):** if escalation is needed, `register_shape` persists across `screen.clear()` — register once at module import or guard against re-registration in the round loop. Same name in `screen._shapes` is overwriteable but it's a subtle gotcha.
7. **Spiral 3-lane visual tuning** is OUT OF SCOPE (per CONTEXT-4 Decision 7) — but if snake-shape rendering on spiral looks bad due to *the shape*, the fix belongs here. Distinguish shape issues from geometry issues during smoke.
8. **`main.py:40` `pencolor() == pencolor()` win check** is a pre-existing fragility (two racers sharing a color would mis-attribute). Phase 4 should fix to identity check (`is`) since we're already in there. Bumps the scope slightly but is the same root cause as the win-message fix.
