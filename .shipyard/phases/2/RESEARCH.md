# Research: Phase 2 — Generalize `race.py` and `tracks.py` to N racers (turtle-only parity)

## Context

Phase 1 landed the `SPECIES` config dict in `constants.py` (Shadow/Ralph/Anaconda snake constants, SPECIES dispatch dict with `"shape_drawer"` as a string sentinel). Phase 2 generalizes the race and track code from a hardcoded N=4 to a parameterized N = `len(racers)`. End state: 4-turtle race still runs indistinguishably from pre-Phase-2; no snake wiring yet.

Locked decisions per `CONTEXT-2.md`:
- Decision 1: every `tracks.py` function that reads `N_LANES` takes an explicit `n` parameter — no default.
- Decision 2: `N_LANES` removed from `constants.py` entirely.
- Decision 3: `test_tracks.py` extended in-place; parametrize for N=3 and N=4.
- Decision 4: `tortuga` → `racer` rename in `race.py`.
- Decision 5: `turtles_list` → `racers`, `create_turtles(color_list)` → `create_racers(species)`, `place_turtles_on_track` → `place_racers_on_track`.
- Decision 6: turtle race still works with zero visual regression.
- Decision 7: `create_racers` returns `[{'o': ..., 'color': ..., 'name': ...}]`.

---

## 1. `tracks.py` Complete N Usage Map

`tracks.py` is 396 lines. The import at line 20 brings in `N_LANES` from constants. All 14 usage sites (from CONTEXT-2.md grep) are confirmed by re-reading the file:

### Import line

- **Line 20**: `from constants import (N_LANES, TRACK_PADDING, LANE_SPACING, SPIRAL_STEP, ...)`
  - Action: Remove `N_LANES` from this import list. All other imported names stay.

### Per-function breakdown

**`_lane_coefficient(lane_idx: int)` — lines 55–57**
- Line 57: `return (N_LANES - 1) / 2.0 - lane_idx`
- Role: signed offset multiplier for positioning a lane relative to the centerline. Lane 0 is outermost (`+(N-1)/2`), lane N-1 is innermost (`-(N-1)/2`).
- Fix: Add `n` parameter: `def _lane_coefficient(lane_idx: int, n: int) -> float`. Use `n` in place of `N_LANES`. This is a private helper; callers are `_straight_lane`, `_rectangular_lane`, `_spiral_lane`, `_boundary_paths` — they must all pass `n` through.

**`_rectangular_finish_y()` — lines 109–115**
- Line 115: `return -((N_LANES - 1) / 2.0 + 1) * LANE_SPACING`
- Role: Y-coordinate of the rectangular finish bar. Placed one `LANE_SPACING` below the lowest start tick (lane N-1, at `y = -(N-1)/2 * LANE_SPACING`).
- Fix: Add `n` parameter: `def _rectangular_finish_y(n: int) -> float`. **Important downstream effect:** `_rectangular_lane` calls this function at line 95. `finish_line_segments` calls it at line 374 (inside the `RECTANGULAR` branch). Both call sites must pass `n`.

**`_spiral_lane(lane_idx: int)` — lines 118–169**
- Line 165: `pre_distance = (N_LANES - 1 - lane_idx) * (LANE_SPACING * 2)`
- Role: staggered-start head-start. Outer lane (index 0) gets `(N-1)*2*LANE_SPACING` of advance; innermost lane (index N-1) gets 0. This is the mechanism for the diagonal start staircase on spiral.
- Fix: Add `n` parameter. Use `n` in the formula: `(n - 1 - lane_idx) * (LANE_SPACING * 2)`.

**`_spiral_pair_cap()` — lines 172–183**
- Line 181: `inner_o = -((N_LANES - 1) / 2.0) * LANE_SPACING`
- Role: computes the innermost lane's offset to determine the lane's shortest dimension, then caps how many spiral pairs all lanes share. This ensures all lanes run the same number of spiral legs.
- Fix: Add `n` parameter. Called only by `_spiral_lane` (line 141) — pass `n` through.

**`build_lane_paths(track_name: str)` — lines 214–217**
- Line 215 (docstring): `"""Return one path dict per lane, indexed 0..N_LANES-1."""`
- Line 217: `return [builder(i) for i in range(N_LANES)]`
- Role: public API — calls each lane builder for every lane index from 0 to N-1. This is the primary entry point called from `race.py`.
- Fix: Add `n` parameter: `def build_lane_paths(track_name: str, n: int) -> list[dict]`. Update the range call and docstring. Pass `n` into each builder call (requires `_LANE_BUILDERS` dispatch to forward `n`). The builder signature `(lane_idx, n)` must be established.

**`start_line_segments(track_name: str)` — lines 253–278**
- Line 268: `for lane_idx in range(N_LANES):`  — SPIRAL/RECTANGULAR branch, iterates to draw one tick per lane.
- Line 274: `x1, y1, _ = lane_start_pose(track_name, N_LANES - 1)` — STRAIGHT branch, references last lane by index.
- Role: generates start-line bar endpoints. For SPIRAL/RECTANGULAR, creates one tick per lane. For STRAIGHT, creates one connecting bar from lane 0 to lane N-1.
- Fix: Add `n` parameter. Update `range(N_LANES)` → `range(n)` and `N_LANES - 1` → `n - 1`. `lane_start_pose` is a thin wrapper that does not use `N_LANES` directly (it calls the builder function for a single lane); no change needed to `lane_start_pose` itself if the lane builder is updated.

**`_boundary_paths(track_name: str)` — lines 281–336**
- Line 294: `y_top = (N_LANES / 2.0) * LANE_SPACING` — STRAIGHT top boundary.
- Line 295: `y_bot = -(N_LANES / 2.0) * LANE_SPACING` — STRAIGHT bottom boundary.
- Line 302: `o = (N_LANES / 2.0) * LANE_SPACING` — RECTANGULAR/SPIRAL outer boundary offset.
- Line 315: `o_in = -(N_LANES / 2.0) * LANE_SPACING` — RECTANGULAR inner boundary offset.
- Role: generates outer (and for rectangular, inner) boundary paths used for placing boundary stones. Offset is `N/2 * LANE_SPACING` outside the outermost lane.
- Fix: Add `n` parameter. Replace all 4 usages with `n`. Called only from `boundary_stones()` (which calls `_boundary_paths`) — `boundary_stones` must also accept and forward `n`.

**`finish_line_segments(track_name: str)` — lines 359–395**
- Line 377: `half_len = (N_LANES * LANE_SPACING) / 2 + LANE_SPACING` — RECTANGULAR finish bar half-width.
- Line 383: `half_len = N_LANES * LANE_SPACING` — SPIRAL finish bar half-height.
- Role: RECTANGULAR finish bar spans the full lane ladder width plus extensions; SPIRAL bar spans the full lane stack height (since all lanes end at origin). STRAIGHT finish uses `build_lane_paths` (which already uses N) — indirect dependency.
- Fix: Add `n` parameter. The `build_lane_paths(track_name)` call at line 386 (STRAIGHT branch) becomes `build_lane_paths(track_name, n)`. Replace the two `N_LANES` literals.

### Summary: functions requiring an `n` parameter

| Function | Current signature | New signature |
|---|---|---|
| `_lane_coefficient` (private) | `(lane_idx)` | `(lane_idx, n)` |
| `_rectangular_finish_y` (private) | `()` | `(n)` |
| `_spiral_pair_cap` (private) | `()` | `(n)` |
| `build_lane_paths` (public) | `(track_name)` | `(track_name, n)` |
| `start_line_segments` (public) | `(track_name)` | `(track_name, n)` |
| `_boundary_paths` (private) | `(track_name)` | `(track_name, n)` |
| `boundary_stones` (public) | `(track_name, spacing)` | `(track_name, n, spacing)` |
| `finish_line_segments` (public) | `(track_name)` | `(track_name, n)` |

Functions NOT needing `n`:
- `set_window_size`, `_window`, `_move`, `_straight_lane`, `_rectangular_lane`, `_spiral_lane` — these already receive `lane_idx` from the builder loop and can receive `n` via their caller; they call `_lane_coefficient(lane_idx, n)` after the refactor.
- `_build_spiral_legs` — pure geometry, no N dependency.
- `path_length`, `position_at_arc` — operate on a single pre-built path dict, no N needed.
- `lane_start_pose` — delegates to a lane builder for a single lane; the builder must accept `n`. If the builder signature becomes `(lane_idx, n)`, then `lane_start_pose` must pass `n` too, making its signature `(track_name, lane_idx, n)`.

**Note on `lane_start_pose`**: currently at lines 245–250, it calls `_LANE_BUILDERS[track_name](lane_idx)`. After the refactor, builders take `(lane_idx, n)`, so `lane_start_pose` must become `lane_start_pose(track_name, lane_idx, n)`. This is an additional public API change not listed in CONTEXT-2.md's 14-line count but required by the cascade. All call sites in `race.py` (`place_racers_on_track` at line 145 calls `tracks.lane_start_pose`) and `test_tracks.py` must pass `n`.

**Note on `_LANE_BUILDERS` dict**: currently at lines 207–211, maps `track_name → builder_fn`. The builder functions must be called with `(lane_idx, n)`. The builder functions `_straight_lane`, `_rectangular_lane`, `_spiral_lane` currently take only `(lane_idx)`. They must become `(lane_idx, n)` and call `_lane_coefficient(lane_idx, n)` and other private helpers with `n`.

---

## 2. `race.py` Complete N Usage and Rename Map

### `turtles_list` occurrences

| Line | Context | New identifier |
|---|---|---|
| 142 | `def place_turtles_on_track(turtles_list, track_name):` | `racers` |
| 144 | `for i, tortuga in enumerate(turtles_list):` | `racers` |
| 156 | `def run_race(turtles_list, track_name, user_bet):` | `racers` |
| 174 | `progress = [0.0] * len(turtles_list)` | `racers` |
| 179 | `for i, turtle in enumerate(turtles_list):` | `racers` |
| 189 | `finish_ticks = [None] * len(turtles_list)` | `racers` |
| 190 | `coast_remaining = [None] * len(turtles_list)` | `racers` |
| 191 | `done = [False] * len(turtles_list)` | `racers` |
| 194 | `for i, turtle in enumerate(turtles_list):` | `racers` |
| 236 | `def show_podium(turtles_list, finish_order):` | `racers` |
| 247 | `for tortuga in turtles_list:` | `racers` |
| 298 | `turtle = turtles_list[lane_idx]['o']` | `racers` |
| 350 | `def announce_result(winner, user_bet, turtles_list):` | `racers` |
| 352 | `if winner.pencolor() == turtles_list[user_bet - 1]['o'].pencolor():` | `racers` |

### `create_turtles` occurrences

| Line | Context |
|---|---|
| 135 | `def create_turtles(color_list):` — function definition |

No other references to `create_turtles` inside `race.py` itself. Only `main.py:30` is the external call site.

### `place_turtles_on_track` occurrences

| Line | Context |
|---|---|
| 142 | `def place_turtles_on_track(turtles_list, track_name):` — function definition |

External call site: `main.py:31`. New name: `place_racers_on_track(racers, track_name)`.

### `tortuga` (loop variable) occurrences

| Line | Context | New identifier |
|---|---|---|
| 144 | `for i, tortuga in enumerate(turtles_list):` in `place_turtles_on_track` | `racer` |
| 146–151 | body: `tortuga['o'].hideturtle()` etc. | `racer` |
| 247 | `for tortuga in turtles_list:` in `show_podium` | `racer` |
| 248 | `tortuga['o'].hideturtle()` | `racer` |

### N=4-specific assumptions

**`TURTLE_NAMES` lookup in `run_race`** (lines 181, 228):
```python
name = TURTLE_NAMES[i] if i < len(TURTLE_NAMES) else f"#{i}"
```
These lines use `TURTLE_NAMES` from constants to log lane names. After Phase 2, `create_racers(species)` stores the racer name in each dict (`racer['name']`). The print-logging block should use `racer['name']` from the racers list instead of the `TURTLE_NAMES` constant. This removes the hardcoded turtle-species dependency from the race loop's logging. The import of `TURTLE_NAMES` at `race.py:9` can be dropped.

**`place_labels = ["1st", "2nd", "3rd", "4th"]`** (line 223):
This list has exactly 4 entries. The code already has a fallback: `place_labels[place] if place < len(place_labels) else f"{place+1}th"`. For N=3, indices 0–2 map to "1st"/"2nd"/"3rd" — safe. For N>4, falls back to the `f-string`. No change required, but the architect should verify the intent: if N=3 is ever run, `"4th"` is never accessed and `place_labels` can stay as-is. [Inferred: safe to leave unchanged in Phase 2]

**`show_podium` — hardcoded top-3 assumption** (lines 236–347):
`show_podium` explicitly iterates `for place in (1, 2, 3)` and `for place in (2, 1, 3)`. It accesses `finish_order[place - 1]` for place in 1, 2, 3. The guard at line 243 (`if len(finish_order) < 3: return`) handles N<3. For N=3 (snake mode — Phase 3+), all 3 finishers fill the podium exactly. For N=4, `finish_order[3]` is never referenced — safe. No change required for Phase 2.

### `run_race` `shared_distance` computation — N safety analysis

Lines 169–173:
```python
lane_paths = tracks.build_lane_paths(track_name)        # line 169 — after refactor: pass n
lane_lengths = [tracks.path_length(p) for p in lane_paths]
straight_length = _screen.window_width() - 2 * TRACK_PADDING
avg_lane_length = sum(lane_lengths) / len(lane_lengths)  # line 172
shared_distance = ((straight_length + avg_lane_length) / 2) / SPEED_FACTOR  # line 173
```

**N-safety verdict: SAFE.** `avg_lane_length` at line 172 is `sum / len(lane_lengths)`. `len(lane_lengths)` equals `len(lane_paths)` equals `n` (the number of racers, after the refactor). For N=3, `sum` covers 3 lane lengths and divides by 3. The formula is dynamically computed from the actual lane set — no hardcoded 4 appears here. The `progress`, `done`, `finish_ticks`, `coast_remaining` arrays at lines 174–191 are all sized `len(turtles_list)` (i.e., `len(racers)` after rename) — all N-safe.

**One required change at line 169:** after `build_lane_paths` gains its `n` parameter, this call must become `tracks.build_lane_paths(track_name, n)` where `n = len(racers)`. The builder must be called with `n` before the loop.

### Call sites to `tracks.py` inside `race.py`

| Line | Current call | Required change |
|---|---|---|
| 79 | `tracks.start_line_segments(track_name)` | `tracks.start_line_segments(track_name, n)` |
| 91 | `tracks.boundary_stones(track_name)` | `tracks.boundary_stones(track_name, n)` |
| 129 | `tracks.finish_line_segments(track_name)` | `tracks.finish_line_segments(track_name, n)` |
| 145 | `tracks.lane_start_pose(track_name, i)` | `tracks.lane_start_pose(track_name, i, n)` |
| 169 | `tracks.build_lane_paths(track_name)` | `tracks.build_lane_paths(track_name, n)` |
| 202 | `tracks.position_at_arc(lane_paths[i], arc)` | No change — `position_at_arc` does not use N |

**Problem:** `draw_start_line(track_name)`, `draw_boundary_stones(track_name)`, `draw_finish_line(track_name)` (lines 77–132) are called from `main.py` with only `track_name`. They internally call the `tracks.*` functions. After the refactor, these `race.py` wrapper functions must also accept `n` (or derive it from a `racers` argument). Since `main.py` calls them after `create_racers()`, the cleanest approach is:
- `draw_start_line(track_name, n)` — passes `n` into `tracks.start_line_segments`.
- `draw_boundary_stones(track_name, n)` — passes `n` into `tracks.boundary_stones`.
- `draw_finish_line(track_name, n)` — passes `n` into `tracks.finish_line_segments`.
- `place_racers_on_track(racers, track_name)` — derives `n = len(racers)` internally, passes to `tracks.lane_start_pose`.

---

## 3. `main.py` Call-Site Changes

Full `main.py` is 51 lines. Changes required by CONTEXT-2.md Decision 5:

| Line | Current | New |
|---|---|---|
| 11 | `from constants import TURTLE_COLORS` | `from constants import SPECIES` (or remove entirely — `create_racers` reads SPECIES internally) |
| 30 | `turtles_list = race.create_turtles(TURTLE_COLORS)` | `racers = race.create_racers("turtles")` |
| 31 | `race.place_turtles_on_track(turtles_list, track_name)` | `race.place_racers_on_track(racers, track_name)` |
| 32 | `race.draw_start_line(track_name)` | `race.draw_start_line(track_name, len(racers))` |
| 33 | `race.draw_finish_line(track_name)` | `race.draw_finish_line(track_name, len(racers))` |
| 29 | `race.draw_boundary_stones(track_name)` | `race.draw_boundary_stones(track_name, len(racers))` |
| 37 | `race.run_race(turtles_list, track_name, user_bet)` | `race.run_race(racers, track_name, user_bet)` |
| 39 | `turtles_list[user_bet - 1]` | `racers[user_bet - 1]` |
| 40 | `race.show_podium(turtles_list, finish_order)` | `race.show_podium(racers, finish_order)` |
| 42 | `race.announce_result(winning_turtle, user_bet, turtles_list)` | `race.announce_result(winning_turtle, user_bet, racers)` |

**Note — line 35:** `user_bet = dialogs.get_user_bet()` — Phase 2 does NOT change this call. `get_user_bet()` retains its current signature (no `species` argument) until Phase 3. The bet still returns a 1-based index. No change at this line.

**Note — `draw_boundary_stones` call order:** Currently at `main.py:29`, before `create_racers` is called at line 30. After the refactor, `len(racers)` is needed. Either (a) move `create_racers` above `draw_boundary_stones`, or (b) use a literal `n=4` for Phase 2 (acceptable since Phase 2 hardcodes turtles). Option (a) is cleaner because the round-loop structure becomes: create racers → setup canvas → race. The architect should choose the ordering explicitly.

**Import cleanup:** `TURTLE_COLORS` import on line 11 must be replaced or removed. `SPECIES` is consumed internally by `create_racers`; `main.py` does not need to import it directly if `create_racers("turtles")` is the call form.

---

## 4. `tests/test_tracks.py` Map

The file is 418 lines. All `N_LANES` imports and usages:

### N_LANES usage in tests

| Line | Test function | How N_LANES is used | N-sensitive? |
|---|---|---|---|
| 10 | (import) | `from constants import N_LANES` | Must be removed |
| 47 | `test_build_lane_paths_returns_one_per_lane` | `assert len(paths) == N_LANES` | Yes — asserts count equals N |
| 107 | `test_rectangular_lane_first_heading_is_north` | `for lane_idx in range(N_LANES):` | Yes — loops over all lanes |
| 139 | `test_rectangular_lane_start_points_staggered_diagonally` | `assert len(set(ys)) == N_LANES` | Yes — asserts N distinct Ys |
| 165 | `test_spiral_lane_start_points_staggered` | `assert len(set(xs)) == N_LANES` | Yes |
| 166 | `test_spiral_lane_start_points_staggered` | `assert len(set(ys)) == N_LANES` | Yes |
| 214 | `test_spiral_first_heading_is_north` | `for lane_idx in range(N_LANES):` | Yes |
| 223 | `test_position_at_arc_zero_returns_start` | `for lane_idx in range(N_LANES):` | Yes — loops all lanes |
| 268 | `test_spiral_start_returns_one_tick_per_lane` | `assert len(bars) == N_LANES` | Yes |
| 287 | `test_straight_finish_segments_share_x_and_span_lanes` | `assert len(bars) == N_LANES` | Yes |
| 316 | `test_straight_start_returns_one_connecting_bar` | `lane_start_pose(STRAIGHT, N_LANES - 1)` | Yes — references last lane |
| 328 | `test_rectangular_start_returns_one_tick_per_lane` | `assert len(bars) == N_LANES` | Yes |
| 343–344 | `test_straight_boundary_stones_form_two_parallel_rows` | `(N_LANES / 2.0) * LANE_SPACING` (twice) | Yes — boundary Y depends on N |
| 355 | `test_rectangular_boundary_stones_bracket_the_racing_band` | `o_outer = (N_LANES - 1) / 2.0 * LANE_SPACING` | Yes |
| 361 | `test_rectangular_boundary_stones_bracket_the_racing_band` | `o_inner = -(N_LANES - 1) / 2.0 * LANE_SPACING` | Yes |

After removing the `N_LANES` import, every test that uses it must be rewritten to pass `n` explicitly into the `tracks.*` call and then assert against the passed `n` value.

### Tests that call `tracks.*` and need `n` added

Every call to a public `tracks.*` function in the test file needs `n` appended after the refactor:

| Function called | Affected test functions |
|---|---|
| `build_lane_paths(track)` | `test_build_lane_paths_returns_one_per_lane`, `test_straight_lane_length_matches_window_minus_padding`, `test_straight_lanes_share_x_differ_in_y`, `test_rectangular_average_lane_length_close_to_centerline_perimeter`, `test_rectangular_lane_ends_at_finish_bar`, `test_rectangular_corner_headings_are_right_turns`, `test_rectangular_outer_lane_is_longer_than_inner`, `test_rectangular_lane_start_points_staggered_diagonally`, `test_rectangular_lane_fits_inside_screen`, `test_spiral_lane_start_points_staggered`, `test_spiral_lanes_all_end_at_origin`, `test_spiral_legs_decreasing`, `test_spiral_terminates_near_center`, `test_position_at_arc_zero_returns_start`, `test_position_at_arc_clamps_past_end`, `test_position_at_arc_walks_correctly_through_corners`, `test_straight_finish_segments_share_x_and_span_lanes` |
| `lane_start_pose(track, lane_idx)` | `test_rectangular_lane_first_heading_is_north`, `test_spiral_first_heading_is_north`, `test_straight_start_line_is_perpendicular_to_heading`, `test_straight_start_returns_one_connecting_bar` |
| `start_line_segments(track)` | `test_straight_start_line_is_perpendicular_to_heading`, `test_spiral_start_returns_one_tick_per_lane`, `test_straight_start_returns_one_connecting_bar`, `test_rectangular_start_returns_one_tick_per_lane` |
| `finish_line_segments(track)` | `test_rectangular_finish_is_single_horizontal_bar_below_starts`, `test_straight_finish_segments_share_x_and_span_lanes`, `test_spiral_finish_is_single_bar_centered_on_origin`, `test_rectangular_lane_ends_at_finish_bar` |
| `boundary_stones(track)` | `test_boundary_stones_nonempty_for_each_track`, `test_straight_boundary_stones_form_two_parallel_rows`, `test_rectangular_boundary_stones_bracket_the_racing_band`, `test_boundary_stones_fit_inside_screen`, `test_boundary_stones_count_matches_path_length` |
| `_boundary_paths(track)` | `test_rectangular_returns_outer_and_inner_boundary_paths`, `test_spiral_boundary_first_stone_near_outer_bl_corner` |

### Tests asserting N=4-specific values vs. structural invariants

**Genuinely N=4-specific (value depends on N=4 specifically):**
- `test_straight_boundary_stones_form_two_parallel_rows` (lines 339–345): asserts `ys == {N_LANES/2 * LANE_SPACING, -N_LANES/2 * LANE_SPACING}`. For N=4 this is `{2*LANE_SPACING, -2*LANE_SPACING}`; for N=3 it's `{1.5*LANE_SPACING, -1.5*LANE_SPACING}`. Must be parameterized.
- `test_rectangular_boundary_stones_bracket_the_racing_band` (lines 349–378): hardcodes `o_outer = (N_LANES-1)/2 * LANE_SPACING`. Must pass `n` and compute `o_outer = (n-1)/2 * LANE_SPACING`.

**Structural invariants (pass any N, just assert length/count = n):**
- `test_build_lane_paths_returns_one_per_lane`: `len(paths) == n` — works for any n.
- `test_rectangular_lane_start_points_staggered_diagonally`: `len(set(ys)) == n` — works for any n.
- `test_spiral_lane_start_points_staggered`: `len(set(xs)) == n` and `len(set(ys)) == n` — works for any n.
- `test_spiral_start_returns_one_tick_per_lane`: `len(bars) == n` — works for any n.
- `test_rectangular_start_returns_one_tick_per_lane`: `len(bars) == n` — works for any n.
- `test_straight_finish_segments_share_x_and_span_lanes`: `len(bars) == n` — works for any n.

### Recommendation: Approach A (parametrize) over Approach B (duplicate)

CONTEXT-2.md Decision 3 explicitly states both approaches are acceptable and defers to the architect. My recommendation is **Approach A** (pytest.mark.parametrize) for Phase 2, with the following rationale:

1. The existing test file already uses `@pytest.mark.parametrize("track", TRACK_NAMES)` at 4 locations (lines 44, 333, 400, 409). Precedent already exists for parametrize in this file; claiming it "breaks convention" is inaccurate for this specific file.
2. Duplicating every affected test into `_n3` / `_n4` variants would add approximately 60+ lines for a minimal new coverage surface. This substantially inflates the test file's line count for structural reasons, not semantic ones.
3. Parametrize pattern `@pytest.mark.parametrize("n", [3, 4])` or `@pytest.mark.parametrize("track,n", [(STRAIGHT, 3), (STRAIGHT, 4), (RECTANGULAR, 3), ...])`is readable, matches the cross-track parametrize already in the file, and keeps assertions in one place.
4. Per CONTEXT-2.md: "If approach A is used, document the style break in `tests/test_tracks.py` with a short module-level comment." The file already has no module-level docstring, so adding one is additive.

**Recommended form for the new geometry tests:**
```python
@pytest.mark.parametrize("track,n", [
    (STRAIGHT, 3), (STRAIGHT, 4),
    (RECTANGULAR, 3), (RECTANGULAR, 4),
    (SPIRAL, 3), (SPIRAL, 4),
])
def test_n_lane_start_positions_distinct_and_in_bounds(track, n): ...
```

---

## 5. `tests/test_constants.py` Impact

Current file: 12 tests (TESTING.md reported 3 originally, but Phase 1 added 9 more; actual count is 12 as seen in the file). None of the 12 tests reference `N_LANES`.

```python
grep -n "N_LANES" tests/test_constants.py  # returns zero results (confirmed)
```

**Impact: zero.** All 12 existing tests remain valid after `N_LANES` is removed from `constants.py`. The tests cover `TURTLE_NAMES`, `TURTLE_IMAGES`, `BET_IMAGE_SIZE`, `SNAKE_NAMES`, `SNAKE_COLORS`, `SNAKE_LENGTHS`, `SNAKE_IMAGES`, `SPECIES` sub-keys, `bet_layout` values, racer counts, and `shape_drawer` sentinel. None of these touch `N_LANES`. No test modifications needed.

---

## 6. SPECIES Dispatch Table — Shape Logic in `create_racers`

### What `create_turtles(color_list)` does today (lines 135–139)

```python
def create_turtles(color_list):
    t = []
    for turtle_color in color_list:
        t.append({'color': turtle_color, 'o': Turtle(shape="turtle")})
    return t
```

Shape setup: `Turtle(shape="turtle")` — the shape is set at construction time via the `shape` keyword argument. No separate `draw_turtle_shape()` call exists. Color is stored in the dict but NOT applied to the Turtle object here — it is applied later in `place_racers_on_track` at line 147: `tortuga['o'].color(tortuga['color'])`.

### What `create_racers(species)` needs to do in Phase 2

Per Decision 7, returns `[{'o': Turtle(...), 'color': c, 'name': name}, ...]`.

For Phase 2 (turtles-only), the implementation reads from `SPECIES["turtles"]`:
- `names = SPECIES[species]["names"]` → `["Raphael", "Michaelangelo", "Leonardo", "Donatello"]`
- `colors = SPECIES[species]["colors"]` → `["red4", "DarkOrange", "blue", "DarkMagenta"]`
- `shape_drawer = SPECIES[species]["shape_drawer"]` → `"turtle"` string sentinel

**In Phase 2, does `create_racers` need any species-specific shape logic?**

No complex dispatch needed in Phase 2. The `shape_drawer` string sentinel (`"turtle"`) is present in `SPECIES` but Phase 2 can simply hardcode `Turtle(shape="turtle")` without branching on the sentinel — this is identical to current behavior. The shape sentinel dispatch (calling `draw_turtle_shape` vs `draw_snake_shape`) is Phase 4's job.

Simplest correct Phase 2 implementation:
```python
def create_racers(species: str):
    data = SPECIES[species]
    racers = []
    for name, color in zip(data["names"], data["colors"]):
        racers.append({'name': name, 'color': color, 'o': Turtle(shape="turtle")})
    return racers
```

This adds `'name'` to the dict (Decision 7) and reads from `SPECIES` (Decision 5) without requiring shape dispatch. The `shape_drawer` field is consulted but the only valid value in Phase 2 is `"turtle"`, so no branch is needed. If the architect wants forward-compatibility, a simple guard can be added:
```python
assert data["shape_drawer"] == "turtle", "snake shape wiring is Phase 4"
```

**Import needed:** `from constants import SPECIES` (plus removing the `TURTLE_NAMES` import from `race.py:9`; `SPECIES["turtles"]["names"]` replaces it).

---

## 7. Geometry Tests for New (track, N) Pairs

Recommended test structure for the 6 pairs mandated by ROADMAP:

### Test 1: N distinct start positions

```python
@pytest.mark.parametrize("track,n", [
    (STRAIGHT, 3), (STRAIGHT, 4),
    (RECTANGULAR, 3), (RECTANGULAR, 4),
    (SPIRAL, 3), (SPIRAL, 4),
])
def test_n_start_positions_are_distinct(track, n):
    """N lanes produce N distinct (x, y) start positions."""
    paths = build_lane_paths(track, n)
    assert len(paths) == n
    starts = [p["start"] for p in paths]
    # All starts should be at distinct positions
    assert len(set(starts)) == n
```

### Test 2: All start positions within canvas bounds

```python
@pytest.mark.parametrize("track,n", [
    (STRAIGHT, 3), (STRAIGHT, 4),
    (RECTANGULAR, 3), (RECTANGULAR, 4),
    (SPIRAL, 3), (SPIRAL, 4),
])
def test_n_start_positions_within_canvas_bounds(track, n):
    half_w, half_h = WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2
    paths = build_lane_paths(track, n)
    for p in paths:
        x, y = p["start"]
        assert -half_w <= x <= half_w, f"{track} n={n}: start x={x} out of bounds"
        assert -half_h <= y <= half_h, f"{track} n={n}: start y={y} out of bounds"
```

### Test 3: Straight track — symmetric vertical spacing

Per ROADMAP: `track_height / (N+1)` symmetric vertical spacing. Existing `_straight_lane` uses `LANE_SPACING` as the fixed spacing between lanes, not `H/(N+1)`. The ROADMAP's formula description may be aspirational (Phase 3/4 behavior when snake lanes need spacing calibrated to the window height) rather than a requirement for Phase 2. **For Phase 2, the straight track formula remains `coeff * LANE_SPACING`, where `coeff = (n-1)/2 - lane_idx`.** The structural invariant that must hold: N distinct Y values, equally spaced by `LANE_SPACING`.

```python
@pytest.mark.parametrize("n", [3, 4])
def test_straight_lanes_n_spaced_by_lane_spacing(n):
    paths = build_lane_paths(STRAIGHT, n)
    ys = sorted(p["start"][1] for p in paths)
    assert len(ys) == n
    diffs = [ys[i+1] - ys[i] for i in range(n-1)]
    for d in diffs:
        assert _approx(d, LANE_SPACING)
```

**Uncertainty flag:** The ROADMAP says "symmetric vertical spacing `track_height / (N+1)`". The current formula is `(n-1)/2 - lane_idx` multiplied by `LANE_SPACING`, which produces N equally-spaced lanes centered at y=0. This is geometrically symmetric but the spacing is `LANE_SPACING` (fixed constant), not `H/(N+1)` (dynamic based on window height). If the ROADMAP intends to change the spacing formula, that is a behavioral change — not just a parameterization — and should be flagged as a **Decision Required** for the architect.

### Test 4: Spiral lanes end at origin for N=3

```python
@pytest.mark.parametrize("n", [3, 4])
def test_spiral_n_lanes_all_end_at_origin(n):
    paths = build_lane_paths(SPIRAL, n)
    for lane_idx, p in enumerate(paths):
        x, y, _ = position_at_arc(p, path_length(p))
        assert _approx(x, 0.0), f"spiral n={n} lane {lane_idx} x={x}"
        assert _approx(y, 0.0), f"spiral n={n} lane {lane_idx} y={y}"
```

### Test 5: Finish-line segment count

```python
@pytest.mark.parametrize("track,n,expected_count", [
    (STRAIGHT, 3, 3),
    (STRAIGHT, 4, 4),
    (RECTANGULAR, 3, 1),  # always 1 horizontal bar
    (RECTANGULAR, 4, 1),
    (SPIRAL, 3, 1),       # always 1 vertical bar at origin
    (SPIRAL, 4, 1),
])
def test_finish_line_segment_count(track, n, expected_count):
    bars = finish_line_segments(track, n)
    assert len(bars) == expected_count
```

---

## 8. Definitive Files-Affected List for Phase 2

### Modify

| File | Summary of changes |
|---|---|
| `constants.py` | Remove `N_LANES = 4` (line 57). Update the `# Track layout` comment block comment if needed. |
| `tracks.py` | (1) Remove `N_LANES` from import line 20. (2) Add `n` parameter to all 8 functions listed in Section 1. (3) Update `_lane_coefficient`, `_rectangular_finish_y`, `_spiral_pair_cap`, `_spiral_lane`, `_boundary_paths`, `build_lane_paths`, `start_line_segments`, `finish_line_segments`, `boundary_stones`. (4) Update `lane_start_pose` signature. (5) Update `_LANE_BUILDERS` dispatch to forward `n` to builder functions. (6) Update module docstring references to `N_LANES`. |
| `race.py` | (1) Rename `create_turtles` → `create_racers(species)` with SPECIES-based implementation + `'name'` in dict. (2) Rename `place_turtles_on_track` → `place_racers_on_track`. (3) Rename `turtles_list` → `racers` everywhere (14 sites). (4) Rename `tortuga` → `racer` (4 sites). (5) Add `n` parameter to `draw_start_line`, `draw_boundary_stones`, `draw_finish_line`. (6) Pass `n = len(racers)` to all `tracks.*` calls. (7) Replace `TURTLE_NAMES[i]` lookups in logging with `racers[i]['name']`. (8) Update import: drop `TURTLE_NAMES`, add `SPECIES`. |
| `main.py` | (1) Replace `from constants import TURTLE_COLORS` import. (2) Update 7 call sites per Section 3 table. (3) Harden call order (move `create_racers` before `draw_boundary_stones` if needed). |
| `tests/test_tracks.py` | (1) Remove `N_LANES` from imports. (2) Add `n` argument to every `tracks.*` call. (3) Replace `N_LANES` literal in assertions with the explicit `n` value. (4) Add new parametrized geometry tests for 6 `(track, n)` pairs (Section 7). (5) Add module-level comment noting parametrize usage. |

### Create

None expected. ROADMAP mentions "tests/test_race_geometry.py" as an alternative, but CONTEXT-2.md Decision 3 mandates extending `test_tracks.py` in-place.

### Delete

None.

### No change

| File | Reason |
|---|---|
| `turtle_race.spec` | No new assets in Phase 2. |
| `dialogs.py` | Bet dialog unchanged (Phase 3). Track dialog unchanged. |
| `audio.py` | No changes in scope. |
| `paths.py` | No changes in scope. |
| `tests/test_constants.py` | Zero `N_LANES` references; all 12 tests remain valid (Section 5). |

---

## 9. Phase 2 Gotchas

### G1: `_lane_coefficient` cascade — private function used by multiple lane builders

`_lane_coefficient` is called inside `_straight_lane`, `_rectangular_lane`, `_spiral_lane`, and `_boundary_paths`. Adding `n` to it requires passing `n` through all four callers. The `_LANE_BUILDERS` dict currently maps to `(lane_idx)` functions; it must map to `(lane_idx, n)` functions after the refactor. This is a clean change but touches every lane builder and the dispatch in `build_lane_paths`.

### G2: Spiral staggered start — the trickiest geometry

`_spiral_lane` at line 165:
```python
pre_distance = (N_LANES - 1 - lane_idx) * (LANE_SPACING * 2)
```
For N=4: outer lane (idx 0) gets `3 * 2 * LANE_SPACING = 6 * LANE_SPACING` of head-start. Innermost (idx 3) gets 0.
For N=3: outer lane (idx 0) gets `2 * 2 * LANE_SPACING = 4 * LANE_SPACING`. Innermost (idx 2) gets 0.

The stagger step `LANE_SPACING * 2` is fixed, so reducing N reduces total stagger. This is geometrically correct (fewer lanes need less spread), but the visual appearance of the N=3 staircase at runtime has not been validated. ROADMAP marks this as a risk for Phase 5 visual polish. For Phase 2, the formula change is mechanical; visual tuning deferred.

**Additional risk:** `pre_distance = min(pre_distance, max(first_length - 1, 0))` (line 167) clamps the head-start to ensure the first leg doesn't go negative. For N=3 with a smaller first leg dimension (if window height limits it), this clamp may activate differently. The test `test_spiral_n_lanes_all_end_at_origin` for N=3 will catch any geometric breakage.

### G3: `_spiral_pair_cap` — innermost lane computation

For N=4, innermost lane offset is `-(3/2) * LANE_SPACING = -1.5 * LANE_SPACING`.
For N=3, innermost lane offset is `-(2/2) * LANE_SPACING = -1.0 * LANE_SPACING`.

For N=3, the innermost lane's `inner_h = H - 2*TRACK_PADDING + 2*(-1.0*LANE_SPACING)`. For `WINDOW_HEIGHT=400, TRACK_PADDING=100, LANE_SPACING=24`: `inner_h = 400 - 200 + 2*(-24) = 152`. `max(1, int(152 // 96) - 1) = max(1, 1-1) = max(1, 0) = 1`. The cap returns 1, same as for N=4 (which also returns 1 on the test canvas). No regression expected at test dimensions.

### G4: `_rectangular_finish_y` cascade

`_rectangular_finish_y` is called in two places:
1. `_rectangular_lane` at line 95 (inline, to compute `closing_leg`)
2. `finish_line_segments` at line 374 (to position the cosmetic finish bar)
3. `test_tracks.py` at line 81 (imported directly: `from tracks import _rectangular_finish_y`)

After adding `n`, the test import and call at line 87 (`_rectangular_finish_y()`) must also pass `n`. Since it is a private function, the test direct-imports it — the test must be updated to call `_rectangular_finish_y(n)`.

### G5: `show_podium` N-flexibility — verified, no changes needed

`show_podium` iterates `for place in (1, 2, 3)` and accesses `finish_order[place - 1]`. The guard `if len(finish_order) < 3: return` handles N<3 (which never happens in current flows). For N=4, `finish_order[3]` is never accessed — the podium shows top 3 only. For N=3, all 3 are shown. No changes needed in Phase 2. ROADMAP says "sanity-check 4-finisher layout pixel-for-pixel" — this is a manual smoke task, not a code change.

### G6: `run_race` logging still references `TURTLE_NAMES` at lines 181 and 228

After Phase 2, `TURTLE_NAMES` should not be imported in `race.py` (it's accessible via `SPECIES["turtles"]["names"]`, and `create_racers` stores names in each dict). The logging code guards with `if i < len(TURTLE_NAMES)` — a smell that signals species-awareness was not built in. After Phase 2, `racer['name']` should be used instead, eliminating the conditional fallback.

### G7: `draw_boundary_stones` call order in `main.py`

Currently `main.py` calls `draw_boundary_stones(track_name)` at line 29 — before `create_racers` at line 30. After the refactor, `draw_boundary_stones` needs `n`. If `n` is obtained from `len(racers)`, `create_racers` must be called first. This requires a reordering of 2 lines in the main loop. Low risk but must be explicit in the plan.

### G8: `place_labels` list hardcoded to 4 entries

`place_labels = ["1st", "2nd", "3rd", "4th"]` at `race.py:223`. The code already uses `place < len(place_labels)` as the guard. For N=3 (Phase 3+), only indices 0–2 are used — safe. Leave as-is for Phase 2.

### G9: No visual regression in N=4 is the primary acceptance gate

All geometry refactors that change function signatures but preserve N=4 behavior must leave the on-screen race visually identical. The only way to verify this is manual smoke (`python main.py`) on all 3 tracks, as ROADMAP specifies. No automated visual diff exists. The architect should plan an explicit "before" screenshot baseline or a manual-checklist smoke task.

---

## 10. Risks to Flag for the Architect

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `lane_start_pose` signature change not in CONTEXT-2.md's 14-line list; cascade missed during build | Medium | Medium | Architect to include `lane_start_pose(track_name, lane_idx, n)` explicitly in the plan. Grepping for `lane_start_pose` in the built output confirms all call sites updated. |
| `_rectangular_finish_y` direct-imported by `test_tracks.py:81` — test breaks silently if signature not updated | High | Low | Plan must include updating `test_tracks.py:81` and `test_tracks.py:87` for the new `(n)` signature. |
| Spiral N=3 visual quality — stagger step of `LANE_SPACING*2 = 48px` may read as cramped on 400px canvas | Low (Phase 2) / High (Phase 4) | Medium | Phase 2 does not run N=3 races; test verifies geometry correctness only. Flag for Phase 5 visual polish task. |
| Call order: `draw_boundary_stones` before `create_racers` in `main.py` | High | Low | Plan must reorder to: `create_racers` → `draw_boundary_stones` → `place_racers_on_track`. |
| `TURTLE_NAMES` import in `race.py` — removing it and replacing logging with `racer['name']` is a cleanup that could be missed | Medium | Low | Add explicit task: "remove `TURTLE_NAMES` import from `race.py`; replace lines 181, 228 with `racers[i]['name']`." |
| `shared_distance` N-safety: confirmed safe (Section 2), but only tested at N=4. N=3 `shared_distance` is untested at runtime | Low | Low | Geometry tests indirectly validate the path-length inputs; `shared_distance` formula is algebraically N-safe. |
| Spiral `_spiral_pair_cap` returns 1 for N=3 on test canvas — same as N=4 — but may differ on full-screen (1920×1080). No full-screen geometry tests. | Low | Low | Accept; geometry tests use constants fallback window. Full-screen is manual smoke only. |
| `test_constants.py` passing `SPECIES["turtles"]["names"]` already expects length 4 (line 71) — Phase 2 `create_racers("turtles")` must produce 4 racers | Low | Low | `SPECIES["turtles"]["names"]` has 4 entries (`TURTLE_NAMES`). `zip(names, colors)` with 4+4 produces 4 racers. Invariant maintained. |
| `build_lane_paths` after refactor: builder functions in `_LANE_BUILDERS` must accept `(lane_idx, n)` — currently `(lane_idx)` — and the dispatch in `build_lane_paths` must forward `n` | High | Medium | Plan must explicitly add `n` to `_straight_lane`, `_rectangular_lane`, `_spiral_lane` signatures and update `_LANE_BUILDERS` call in `build_lane_paths`. |
| Missing `n` at any single `tracks.*` call site causes `TypeError` at runtime; test suite may not exercise all paths if not all 3 tracks are smoke-tested | Medium | Medium | Architecture plan: smoke all 3 tracks manually before declaring Phase 2 complete. |

---

## Implementation Considerations

### Integration points with existing code

1. `tracks.py` is a pure-geometry module with no side effects. Adding `n` to function signatures does not change its testability or isolation. Tests continue to run against the constants-file fallback window size (`500×400`).
2. `race.py` functions `draw_start_line`, `draw_boundary_stones`, `draw_finish_line` currently take only `track_name`. They are thin wrappers that call `tracks.*`. Adding `n` to their signatures is the cleanest option (vs. computing `n` from a global or requiring callers to call `tracks.*` directly).
3. The `_LANE_BUILDERS` dict is an internal dispatch table. The refactor must update it so each builder is called as `builder(i, n)` — either by changing builder signatures or by using `functools.partial`. Direct signature change is simpler and consistent with the codebase's convention of no functional dependencies.

### Migration path

The refactor is strictly in-place. No compatibility shims needed (CONTEXT-2.md Decision 5: "No back-compat aliases"). Build sequence: (1) update `tracks.py`, (2) update `race.py`, (3) update `main.py`, (4) update `tests/test_tracks.py`. Each step in isolation may break the test suite; the builder should make all four changes in one atomic commit or plan step.

### Testing strategy

1. Update all existing `test_tracks.py` call sites to pass `n=4` explicitly. All existing tests should pass unchanged at N=4 behavior.
2. Add new parametrized tests for N=3 and N=4 (6 `(track, n)` pairs per Section 7). Run `pytest tests/test_tracks.py` to confirm green.
3. Run `pytest tests/test_constants.py` to confirm no regression.
4. Manual smoke: `python main.py` on all 3 tracks. Confirm 4-turtle race looks identical to pre-Phase-2 master.

### Performance implications

None. All changes are to function signatures and internal arithmetic. No algorithmic complexity changes. The geometry functions run O(N) in the number of lanes; N changes from 4 to 3 or 4 — negligible.

---

## Uncertainty Flags

**Decision Required — straight track spacing formula:**
ROADMAP mentions symmetric vertical spacing of `track_height / (N+1)` for the straight track. The current code uses fixed `LANE_SPACING` spacing regardless of N. For N=4: `H/(N+1) = 400/5 = 80px` vs `LANE_SPACING = 24px` — these are very different numbers. If the ROADMAP's formula is prescriptive, the lane geometry changes visually for N=4 (spacing widens significantly) and is **not** a no-op for turtles. If `track_height/(N+1)` is only intended as a description of the current symmetric layout (i.e., the current centering logic already produces symmetric results — which it does), no code change is needed. The architect must decide: is `track_height/(N+1)` a new formula to implement, or a description of the existing layout's symmetry property?

**Inferred — `lane_start_pose` signature:** The CONTEXT-2.md's list of 14 `N_LANES` references in `tracks.py` does not include `lane_start_pose` explicitly, because `lane_start_pose` itself does not use `N_LANES` directly — it delegates to a builder. However, the builder now requires `n`, making `lane_start_pose(track_name, lane_idx, n)` a necessary cascade change. This was confirmed by reading the function body at lines 245–250. Flagged as inferred to distinguish it from the explicitly listed 14 references.

**Inferred — `draw_boundary_stones` in `race.py`:** Currently takes `(track_name)` only. After refactor, must pass `n` to `tracks.boundary_stones`. No explicit mention of this function in CONTEXT-2.md's rename/change list. Flagged as inferred.

---

## Sources

All findings are based on direct reading of source files in `C:\Users\T0226129\PyCharmProjects\Turtle Race`. No external URLs consulted — all research is codebase-only per the research question specification.

1. `tracks.py` — full read, 396 lines
2. `race.py` — full read, 424 lines
3. `main.py` — full read, 51 lines
4. `tests/test_tracks.py` — full read, 418 lines
5. `tests/test_constants.py` — full read, 84 lines
6. `constants.py` — full read, 63 lines
7. `.shipyard/phases/2/CONTEXT-2.md` — full read
8. `.shipyard/ROADMAP.md` — full read
9. `.shipyard/codebase/ARCHITECTURE.md` — full read
10. `.shipyard/codebase/CONVENTIONS.md` — full read
11. `.shipyard/codebase/TESTING.md` — full read
12. `.shipyard/phases/1/results/AUDIT-1.md` — partial read (Phase 1 outcome context)
13. Grep results: `N_LANES` across all `.py` files; `turtles_list|create_turtles|tortuga|TURTLE_COLORS` across all `.py` files; `TURTLE_NAMES\[i\]` across all `.py` files
