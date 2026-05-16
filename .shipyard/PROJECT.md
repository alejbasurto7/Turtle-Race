# Turtle Race — Project Definition

## Project Name

Turtle Race — Snakes Racer Mode

## Description

Turtle Race is a Python desktop game built on the `turtle` module, `tkinter`, and `pygame.mixer`. The player picks a track, picks a racer to bet on, and watches the field race to a finish line with a podium celebration.

This milestone adds a **racer-species selector**. After the existing track-selection dialog, the player chooses between **Turtles** (existing 4-racer experience) and **Snakes** (new 3-racer experience). The Snakes mode introduces three new characters — **Shadow** (black), **Ralph** (orange-tan), and **Anaconda** (green) — and runs a 3-lane race that reuses the same tracks, race loop, and podium machinery.

The race code is **fully generalized**: race loop, placement, lane geometry, podium, finish-line, and bet-dialog all become parameterized by a `species` config in `constants.py`. The existing turtle path is preserved end-to-end through this generalization — no regressions in the 4-turtle experience.

## Goals

1. Add a species-selection dialog between track selection and bet selection.
2. Introduce three snake racers with distinct identities (name, color, image asset).
3. Support a 3-lane race that **redistributes lanes evenly** across the same race area on all three existing tracks.
4. Reuse the existing finish line, podium, celebration, and play-again flow so snakes behave like turtles end-to-end.
5. Refactor race/dialog code to one parameterized path keyed by species — no parallel code duplication.
6. Keep the existing 4-turtle experience unchanged when the player picks Turtles.

## Non-Goals

- New tracks, new music, or new background art for Snakes mode.
- Multiplayer, online, or persistent stats.
- Changes to race physics, betting payout, or `MAX_PACE` tuning.
- A mixed-species race (snakes vs. turtles in the same race).
- Mid-race species switching.
- Using the snake PNGs as the in-race graphic — they look poor at race-track scale. PNGs are for the bet dialog only.

## Requirements

### Functional — Selection flow (per round)

Round order: `set_background` → **track** → **species (NEW)** → **bet** → race → podium → play-again.

- New `get_user_species()` dialog in `dialogs.py`:
  - Tk `Toplevel`, modal (`grab_set` + `wait_window`), `WM_DELETE_WINDOW` no-op (forces a choice — matches existing dialogs).
  - Two large side-by-side buttons: **Turtles** | **Snakes**, each with a representative image (one turtle JPG; one snake PNG, e.g. `Shadow.png`).
  - Returns `"turtles"` or `"snakes"`.
- Species is re-asked every round (consistent with how track is re-asked).
- `get_user_bet(species)` becomes species-aware:
  - Turtles: existing 2×2 grid, unchanged.
  - Snakes: row of 3 buttons (Shadow | Ralph | Anaconda).
  - 1-based return value indexing into the chosen species' racer list (`racers[user_bet - 1]`) — matches existing turtle convention.

### Functional — Snake racers & data model

- Three snakes with fixed identity:
  - **Shadow** — black, length **6** units
  - **Ralph** — orange-tan (concrete hex TBD during build — e.g., `#D2A679`), length **2** units
  - **Anaconda** — green, length **5** units
- Snake lengths must visibly differ on screen and respect the **6 : 5 : 2** ratio (Shadow : Anaconda : Ralph). Absolute size of "1 unit" is a build-time tuning decision — pick a base that makes Shadow clearly the longest, Anaconda noticeably shorter than Shadow, and Ralph clearly the shortest, while still fitting comfortably in its lane.
- Snake PNG assets already exist at `assets/snakes/{Shadow,Ralph,Anaconda}.png` (1024×1024 RGBA). Used only in the bet dialog.
- Snake identity is positional in `constants.py`: `SNAKE_NAMES[i] ↔ SNAKE_COLORS[i] ↔ SNAKE_LENGTHS[i]`; `SNAKE_IMAGES` keyed by name. Same invariant as the existing turtle constants.
- `constants.py` introduces a `SPECIES` config dict:
  ```python
  SPECIES = {
      "turtles": {
          "names": TURTLE_NAMES, "colors": TURTLE_COLORS, "images": TURTLE_IMAGES,
          "bet_layout": "grid_2x2", "shape_drawer": draw_turtle_shape,
      },
      "snakes": {
          "names": SNAKE_NAMES, "colors": SNAKE_COLORS, "images": SNAKE_IMAGES,
          "bet_layout": "row_3", "shape_drawer": draw_snake_shape,
      },
  }
  ```
- `assets/snakes/*.png` is added to `turtle_race.spec` `datas=` so the frozen build bundles them.

### Functional — Snake in-race shape (custom-drawn)

- `draw_snake_shape(t, length_units)` configures a `turtle.Turtle` to read as a snake:
  - Start with `t.shape("classic")` (arrow shape — head-pointing-forward read).
  - `t.shapesize(stretch_wid=W, stretch_len=L_BASE * length_units)` — `L_BASE` is a build-time constant so Shadow (6), Anaconda (5), Ralph (2) end up in the 6:5:2 ratio at a visible-but-fits-in-lane scale.
  - Fallback if the stretched classic reads weak: register a custom polygon via `screen.register_shape("snake_<name>", (...))` sized per length unit, for a 2-segment silhouette.
- Color applied per-snake from `SNAKE_COLORS`; length applied per-snake from `SNAKE_LENGTHS`.
- **Race-position convention:** finish-line detection uses the snake's **head** position (not center) so longer snakes don't get a "head start" or "head deficit" relative to shorter ones. This is a behavioral requirement, not just visual.
- The snake PNGs are explicitly NOT used as the in-race graphic — they don't scale down well to racer size.

### Functional — 3-lane race plumbing

- Lane placement helpers in `race.py` parameterized by N (= `len(racers)`):
  - `create_racers(species)` replaces `create_turtles(TURTLE_COLORS)`.
  - `place_racers_on_track(racers, track_name)` produces N evenly-spaced start positions, **redistributed to fill the same race area** (not 3-of-4 with a gap).
  - `draw_start_line(track_name, n)` spans the new N-lane geometry.
  - `draw_finish_line(track_name)` is N-independent — unchanged.
- Per-track geometry recompute:
  - **Straight:** vertical spacing `track_height / (N+1)`.
  - **Rectangular:** stagger offsets along the start edge recomputed for N.
  - **Spiral:** staggered spiral entry points recomputed for N. Highest visual-tuning risk.
- `run_race(racers, track_name, user_bet)` already iterates over the field — drops in unchanged for N=3.

### Functional — Podium, celebration, announce

- `show_podium(racers, finish_order)` already iterates `finish_order` — generalizes to 3 or 4 finishers. For Snakes mode (N=3), all racers go on the podium; no off-podium 4th.
- `celebrate(winning_racer, user_won)` and `announce_result(winning_racer, user_bet, racers)` are name/color-agnostic — unchanged beyond identifier renames.

### Non-Functional Requirements

- **Asset handling:** All snake images load through `paths.resource_path()` so the frozen PyInstaller build works.
- **Tk image references:** Snake `PhotoImage` objects must be retained on the dialog (mirroring `dialog._bet_images`, `dialog._track_images`) to avoid Tk GC blanking. New: `dialog._species_images`.
- **No turtle-mode regression:** The existing turtle race must remain visually and behaviorally identical when Turtles is selected.
- **Generalization discipline:** Single parameterized code path — no `create_snakes()` alongside `create_turtles()`, no `get_user_snake_bet()` alongside `get_user_bet()`. Species choice flows through one config object.
- **Cross-round cleanup:** Switching species across "play again" rounds must not leak Tk state, registered shapes, or image refs.

## Success Criteria

1. Picking **Turtles** at the species dialog launches the unchanged 4-turtle bet flow on the chosen track and races to a turtle podium.
2. Picking **Snakes** launches a 3-snake bet flow on the chosen track and races to a 3-snake podium with celebration.
3. The frozen `dist/TurtleRace.exe` build runs both modes correctly (snake assets bundled via `turtle_race.spec`).
4. `pytest` passes, including new tests:
   - Snake constant invariants (names/colors/lengths/images line up; PNG files exist on disk; `SNAKE_LENGTHS` values are `{Shadow: 6, Anaconda: 5, Ralph: 2}`).
   - `SPECIES` config shape (required keys present per species; `bet_layout` valid).
   - Geometry: `place_racers_on_track` produces N distinct positions within bounds for each `(track, N)` pair in `{(straight,3), (straight,4), (rect,3), (rect,4), (spiral,3), (spiral,4)}`.
5. Manual smoke across all 6 (track × species) permutations: race runs to a winner, podium displays correctly, "play again" works.
6. Alternating species across rounds in a single session works with no visual artifacts or crashes.

## Constraints

- **Stack-locked:** Python + `turtle` + `tkinter` + `pygame.mixer` + `Pillow` + PyInstaller. No new heavyweight dependencies.
- **Single-screen Tk root:** `Screen()` is created once and reused via `clear()` + `set_background()`. Snake mode must respect this — no second screen, no destroying the root.
- **Asset budget:** Snake PNGs already provided (`assets/snakes/{Shadow,Ralph,Anaconda}.png`, 1024×1024 RGBA). Bet-dialog resize handled via existing `BET_IMAGE_SIZE` resize pipeline.
- **Bet indexing:** 1-based, `racers[user_bet - 1]` — matches existing turtle convention.
- **Backward compatibility within the session:** Identifier renames are allowed (`turtles_list` → `racers`, `create_turtles` → `create_racers`, etc.) — no `turtles_list` alias needs to be kept.

## Open Items (resolve during planning/build)

- ~~Concrete hex for **Ralph**'s orange-tan color — decide during constants task.~~ **RESOLVED:** `#E89F4F`
- ~~Concrete value for the `L_BASE` length multiplier so Shadow (length 6) is visibly snake-ish but fits in its lane — tune visually during build verification.~~ **RESOLVED:** `1.2`
- ~~Whether the stretched "classic" shape is sufficient for the snake silhouette, or whether to escalate to a registered custom polygon — decide visually during build verification, not up-front.~~ **RESOLVED:** custom Option 5 smooth-wave polygon registered as `"snake"`
- Spiral 3-lane geometry will likely need a manual visual-tuning pass on the running app, not just unit-test coverage. **DEFERRED** per CONTEXT-5 Decision 1
