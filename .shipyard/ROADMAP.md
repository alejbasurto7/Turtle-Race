# ROADMAP — Snakes Racer Mode

Milestone goal: add a per-round species selector (Turtles | Snakes) that drops a 3-snake field onto the existing tracks via a single parameterized code path keyed by a `SPECIES` config, with zero regression in the 4-turtle experience. Authoritative spec: `.shipyard/PROJECT.md`. Module map: `.shipyard/codebase/STRUCTURE.md`. Behavioral baseline: `.shipyard/codebase/ARCHITECTURE.md`.

Phases are ordered by dependency. Each phase ends with a verifiable checkpoint so regressions surface immediately. Risk-tagged; highest-risk visual work (spiral 3-lane, `L_BASE`) is isolated to Phase 4 and revisited in Phase 5.

---

## Phase 1 — Snake constants & `SPECIES` config foundation  ✅ COMPLETE (2026-05-15)

**Goal:** Land all snake identity data + the `SPECIES` config dict in `constants.py`, register snake PNGs in the PyInstaller spec, and lock invariants with tests. Pure data — no behavior changes yet.

**Risk: low** — additive, fully unit-testable, no race-loop touch.

**Deliverables**
- `constants.py`: add `SNAKE_NAMES = ["Shadow", "Ralph", "Anaconda"]`, `SNAKE_COLORS` (Shadow=black, Ralph=concrete orange-tan hex e.g. `"#D2A679"`, Anaconda=green), `SNAKE_LENGTHS = [6, 2, 5]` (positional with `SNAKE_NAMES`), `SNAKE_IMAGES = {"Shadow": "assets/snakes/Shadow.png", "Ralph": "assets/snakes/Ralph.png", "Anaconda": "assets/snakes/Anaconda.png"}`, `L_BASE` placeholder constant (tuned later), and a `SPECIES` dict with `"turtles"` and `"snakes"` entries. **Note:** the `SPECIES` dict cannot reference `draw_turtle_shape` / `draw_snake_shape` yet (those live in `race.py`); use a string key `"shape_drawer": "turtle"` / `"snake"` or defer the `shape_drawer` field to Phase 4 and document the omission inline. Pick one approach in Task 1.1 and stick with it.
- `turtle_race.spec`: add `('assets/snakes/*.png', 'assets/snakes')` to `datas=`.
- `tests/test_constants.py`: new snake invariant tests.

**Tasks**

1. **(TDD)** Add snake invariant tests to `tests/test_constants.py` first: `SNAKE_NAMES`, `SNAKE_COLORS`, `SNAKE_LENGTHS` all length 3; `SNAKE_IMAGES.keys() == set(SNAKE_NAMES)`; lengths positional-map to `{Shadow: 6, Ralph: 2, Anaconda: 5}`; each PNG file exists on disk via `paths.resource_path()`.
2. Implement the constants in `constants.py` to make the new tests pass. Pick Ralph's concrete hex now; comment the choice.
3. **(TDD)** Add `SPECIES` config shape test to `tests/test_constants.py`: keys `{"turtles", "snakes"}` present; each has required sub-keys `{"names", "colors", "images", "bet_layout"}`; `bet_layout` ∈ `{"grid_2x2", "row_3"}`; `len(SPECIES["turtles"]["names"]) == 4`; `len(SPECIES["snakes"]["names"]) == 3`.
4. Implement `SPECIES` dict in `constants.py` to satisfy the test. Decide and document the `shape_drawer` strategy (string key vs. deferred wiring).
5. Update `turtle_race.spec` `datas=` to include `('assets/snakes/*.png', 'assets/snakes')`.

**Success criteria**
- `pytest tests/test_constants.py` — green, including all new snake + SPECIES tests.
- `pytest` (full) — still green.
- `python -c "import constants; print(constants.SPECIES['snakes']['names'])"` prints `['Shadow', 'Ralph', 'Anaconda']`.

**Risks / gotchas**
- Positional ordering of `SNAKE_LENGTHS` is `[Shadow=6, Ralph=2, Anaconda=5]` to mirror `SNAKE_NAMES`. The 6:5:2 visual ratio in PROJECT.md is Shadow:Anaconda:Ralph by *value*, not by list position — easy to get wrong. Lock this with a name-keyed test.
- If `shape_drawer` is set to a callable in this phase, it pulls a circular import (`constants` ↔ `race`). Keep it a string sentinel or defer.

---

## Phase 2 — Generalize `race.py` to N racers (turtle-only parity)

**Goal:** Refactor every N=4-hardcoded code path in `race.py` to a parameterized `N = len(racers)`, including renames `turtles_list` → `racers` and `create_turtles` → `create_racers(species)`. The end state at the close of this phase still runs **only turtles**; verifying parity here de-risks Phase 3/4.

**Risk: medium** — touches the largest module (`race.py`, 423 lines) and rewires `main.py`. Race-loop math (`run_race`) iterates the field already so the loop body is safe, but `place_racers_on_track` / `draw_start_line` need per-track N-aware geometry.

**Deliverables**
- `race.py`: `create_racers(species)` replaces `create_turtles`; `place_racers_on_track(racers, track_name)` and `draw_start_line(track_name, n)` parameterized by N; identifier rename `turtles_list` → `racers` everywhere in the module (`race.py:135-138`, `race.py:156-233`, podium/celebrate/announce). No back-compat aliases.
- `main.py`: call-site rename to match (`main.py:14-47` block — `create_turtles` → `create_racers("turtles")`, `turtles_list` → `racers`, etc.). Species value hard-coded to `"turtles"` in this phase; Phase 3 wires the dialog.
- `tests/test_tracks.py` (or new `tests/test_race_geometry.py`): geometry tests covering 6 `(track, N)` pairs.

**Tasks**

1. **(TDD)** Add geometry tests for `place_racers_on_track` (or the underlying lane-start logic in `tracks.py` if N is plumbed there): for each `(track, N) ∈ {(straight,3), (straight,4), (rect,3), (rect,4), (spiral,3), (spiral,4)}`, assert N distinct start positions, all within canvas bounds, and (for straight) symmetric vertical spacing of `track_height / (N+1)`.
2. Refactor `race.py:create_turtles` → `create_racers(species)` that reads `SPECIES[species]["names"]` + `["colors"]` and returns the same `[{'color': c, 'o': Turtle(...)}, ...]` shape (extend dict with `'name'` while we're here — Phase 4 will use it). Rename `turtles_list` → `racers` throughout `race.py`.
3. Parameterize `place_racers_on_track` and `draw_start_line` on N. For straight: vertical spacing `H/(N+1)`. For rectangular: recompute stagger offsets for N. For spiral: recompute staggered spiral entry points for N (cosmetic visual tuning deferred to Phase 5).
4. Update `main.py` call sites to the new names; pass `species="turtles"` literally for now.
5. Smoke-run `python main.py` on all 3 tracks with N=4 turtles. Confirm zero visual regression vs. master.

**Success criteria**
- `pytest` — green, including new `(track, N)` geometry tests for both N=3 and N=4.
- Manual: `python main.py` runs straight + rectangular + spiral with 4 turtles; visual output indistinguishable from `master`.
- `grep` confirms no remaining references to `create_turtles` or `turtles_list` (`Grep` over `*.py`).

**Risks / gotchas**
- `race.py:run_race` (`race.py:156-233`) computes `shared_distance` using *average* lane length — verify it still behaves with N=3 lane sets even though we don't *run* N=3 races until Phase 4.
- Podium layout (`show_podium`) is N-sensitive in spacing even though it iterates `finish_order` already. Sanity-check 4-finisher layout pixel-for-pixel.
- `draw_finish_line` is documented N-independent — confirm by reading and don't touch.

---

## Phase 3 — Species + snake-aware bet dialogs

**Goal:** Insert the species dialog into the round flow and make `get_user_bet` species-aware. End of phase: picking "Turtles" runs the existing flow; picking "Snakes" reaches the bet step and returns a valid bet (race still uses turtle drawing — wired in Phase 4).

**Risk: medium** — Tk modal correctness (`grab_set`, `wait_window`, `WM_DELETE_WINDOW` no-op, image-ref retention via `dialog._species_images`) is easy to get subtly wrong and only manifests at runtime.

**Deliverables**
- `dialogs.py`: new `get_user_species()` (`Toplevel`, 2 side-by-side image buttons, modal, returns `"turtles"` | `"snakes"`); refactor `get_user_bet()` to `get_user_bet(species)` dispatching on `SPECIES[species]["bet_layout"]` (`"grid_2x2"` keeps the existing hard-coded turtle layout; `"row_3"` builds a Shadow | Ralph | Anaconda row).
- `main.py`: insert `species = dialogs.get_user_species()` between `get_user_track()` and the racer-creation block; pass `species` to `create_racers` and `get_user_bet`.
- New constants if needed (e.g., `SPECIES_DIALOG_IMAGE_SIZE`) added to `constants.py`.

**Tasks**

1. Implement `get_user_species()` in `dialogs.py` mirroring `get_user_track()`'s structure (`dialogs.py:81-` area as the pattern): `Toplevel`, two buttons each with a `PhotoImage`; one turtle JPG and `assets/snakes/Shadow.png` as the reps; retain refs on `dialog._species_images`; `protocol("WM_DELETE_WINDOW", lambda: None)`; `grab_set()` + `wait_window()`.
2. Refactor `get_user_bet()` signature to `get_user_bet(species)`. Branch on `SPECIES[species]["bet_layout"]`. Move the existing `grid_layout` to a `_TURTLE_GRID_LAYOUT` constant inside `dialogs.py`; add a `_SNAKE_ROW_LAYOUT` for snakes. Both branches return 1-based index into the species' name list, computed as `species_names.index(name) + 1`.
3. Update `main.py` round loop: call `get_user_species()` after `get_user_track()`; pass `species` into `create_racers(species)` and `get_user_bet(species)`. **Note:** snake-mode race still uses `draw_turtle_shape` placeholder until Phase 4 — that's fine for this checkpoint; it should *run*, even if snakes look like turtles on-canvas.
4. Manual smoke: launch app, pick Turtles → confirm existing flow unchanged end-to-end. Launch again, pick Snakes → confirm species dialog → snake bet row of 3 → race runs (turtle-shaped) → podium shows 3 racers → play-again works.
5. Verify cross-round species switching: round 1 Turtles, round 2 Snakes, round 3 Turtles. No crashes, no image-GC blanking, no stale shapes.

**Success criteria**
- `python main.py` — manual smoke of all 6 `(track × species)` permutations reaches at least the podium step without crash (snakes will look like turtles — acceptable for this checkpoint).
- `pytest` — green.
- Species dialog cannot be dismissed via the window close button (matches existing `WM_DELETE_WINDOW` no-op pattern from track/bet dialogs).

**Risks / gotchas**
- `dialog._species_images` retention — forgetting this blanks the buttons. Mirror `dialogs.py:37` (`dialog._bet_images = []`) exactly.
- The existing `get_user_bet` is called from `main.py` with no args today. Changing the signature without updating the call site is the easy break — verify Phase 2 left the call site touched so a missing-arg `TypeError` shows up immediately on first run.
- Snake bet dialog must size to the same `BET_IMAGE_SIZE` so dialog dimensions feel consistent; PNGs are 1024×1024 and need to be resized via the existing PIL pipeline.

---

## Phase 4 — Snake in-race shape, length, head-finish detection

**Goal:** Replace the placeholder turtle-shaped snake with a custom-drawn stretched-classic (or registered polygon fallback), per-snake `length_units` scaling, and head-position finish-line detection. End of phase: Snakes mode is feature-complete and visually correct on at least the straight and rectangular tracks.

**Risk: high** — `L_BASE` tuning, head-vs-center finish geometry, and the stretched-`classic` legibility decision all live here. Spiral visual tuning is acknowledged but deferred to Phase 5.

**Deliverables**
- `race.py`: new `draw_snake_shape(t, length_units)` (configures `t.shape("classic")` + `t.shapesize(stretch_wid=W, stretch_len=L_BASE * length_units)`; optional fallback that registers a 2-segment polygon via `screen.register_shape("snake_<name>", ...)`); `create_racers(species)` extended to call the appropriate `shape_drawer` from `SPECIES`; `run_race` finish detection changed to use head position when `species == "snakes"` (or, cleaner: always use head position — turtles are symmetric so behavior is unchanged).
- `constants.py`: `L_BASE` tuned to a concrete value (e.g., 0.4–1.0 range; tuned empirically) such that Shadow's length-6 racer fits in its lane on the straight track while clearly reading as longer than Anaconda (5) and Ralph (2).
- `SPECIES` config: wire `shape_drawer` to the actual callables (resolve the Phase 1 deferred decision — likely a name-keyed dispatch inside `create_racers` to keep `constants.py` free of `race` imports).

**Tasks**

1. Implement `draw_snake_shape(t, length_units)` in `race.py`. Start with the stretched-`classic` approach. Apply color from `racer['color']`; apply `shapesize(stretch_wid=W, stretch_len=L_BASE * length_units)` with `W` and `L_BASE` chosen so length-6 fits the straight-track lane height with margin.
2. Wire `shape_drawer` dispatch in `create_racers(species)`: for `"turtles"`, current shape setup (extract existing logic into `draw_turtle_shape(t)` if needed for symmetry); for `"snakes"`, call `draw_snake_shape(t, SNAKE_LENGTHS[i])`. Resolve the constants-vs-race import question now.
3. Change finish-line detection in `run_race` to head position. For `turtle.Turtle` the position is already the center; head offset = `current_stretch_len * shape_pixel_unit / 2` along the heading vector. Compute and add to the position used in the finish check. Add a brief comment explaining why this is uniform for both species.
4. Manual smoke and `L_BASE` tuning: run snakes on straight track. Confirm visually that Shadow (6) > Anaconda (5) > Ralph (2), all fit in their lanes, none clip the boundary stones. Adjust `L_BASE` and commit the tuned value.
5. Manual smoke on rectangular track with snakes. Confirm head-position finish detection means longer snakes are not disadvantaged (no obvious unfairness across repeated runs).
6. Manual smoke on spiral track with snakes. Note any visual issues for Phase 5 polish.
7. **Decision gate:** if stretched `classic` reads as a snake at race scale, ship it. Otherwise, register a 2-segment custom polygon via `screen.register_shape("snake_<name>", ...)` and switch the shape source. Decide visually; document the decision in `race.py` as a comment.

**Success criteria**
- Snakes mode runs end-to-end on straight and rectangular tracks: snake bet → race → podium → play-again, with visibly different-length snakes.
- Head-position finish: after >5 races, the win distribution does not visibly favor Shadow (longest) or penalize Ralph (shortest) due to geometry. Eyeballed, not statistical.
- `pytest` — green.
- Turtle-mode regression check: pick Turtles, race all 3 tracks, confirm unchanged vs. Phase 2 baseline.

**Risks / gotchas**
- `turtle.shapesize` `stretch_len` units are turtle-shape units (1 unit = 20 px for `"classic"`), not arbitrary px. `L_BASE` must account for this.
- Head-offset computation needs to use the *current* heading, not the lane's nominal direction (rectangular and spiral lanes turn). Use `t.heading()` (or the heading returned by `tracks.position_at_arc`).
- If `register_shape` is used, the screen-reuse pattern means shapes persist across `screen.clear()` — registering once at startup is safer than per-round. Watch for "shape already registered" or per-round leakage.
- `racer['o'].pencolor()` vs `racer['color']` — the existing user-bet match in `main.py:39` compares `pencolor()`. Snakes will have distinct colors so this still works, but verify Ralph's hex round-trips through `pencolor()` cleanly.

---

## Phase 5 — Regression sweep, frozen build, visual polish

**Goal:** Full test run, full manual smoke matrix, frozen-exe verification, and visual cleanup of any spiral-3-lane or `L_BASE` issues flagged in Phase 4.

**Risk: low–medium** — risk is PyInstaller-specific (asset path resolution in frozen build) and visual taste calls. No structural code changes expected.

**Deliverables**
- Final `L_BASE` value committed if Phase 4's tuning was provisional.
- Spiral 3-lane entry geometry tuned in `race.py` / `tracks.py` if Phase 4 flagged it.
- `dist/TurtleRace.exe` verified to run both species modes correctly.

**Tasks**

1. Full `pytest` run; address any regressions.
2. Manual smoke matrix: all 6 `(track × species)` permutations, each ending in podium + play-again. Then a 4-round session alternating species (T, S, T, S) on rotating tracks — confirm no Tk state leak, image-GC blanking, or stale registered-shape artifacts.
3. Spiral 3-lane visual pass: if entry points feel cramped or asymmetric, adjust the per-N stagger formula in the spiral lane builder. This is the highest-risk visual area called out in PROJECT.md.
4. Run `pyinstaller turtle_race.spec`. Verify `dist/TurtleRace.exe` launches; smoke both species modes from the frozen build; confirm snake PNGs render in the species + bet dialogs (proves the spec `datas=` glob worked).
5. If `L_BASE` or shape strategy was provisional in Phase 4, finalize it now based on accumulated playtesting.

**Success criteria**
- `pytest` — green.
- All 6 `(track × species)` permutations playable in dev (`python main.py`) and in the frozen build (`dist/TurtleRace.exe`).
- Alternating-species multi-round session: 4 rounds, no crashes, no visual artifacts.
- Snake PNGs visible in the species dialog and snake bet dialog from the frozen `dist/TurtleRace.exe` — proves PyInstaller bundling.

**Risks / gotchas**
- PyInstaller's `datas=` glob `('assets/snakes/*.png', 'assets/snakes')` places files at `<_MEIPASS>/assets/snakes/`. Confirm `SNAKE_IMAGES` paths in `constants.py` match this destination (`"assets/snakes/Shadow.png"`, not `"assets/Shadow.png"`).
- Spiral 3-lane: redistributing 3 lanes evenly across the spiral's nested-rectangle entry zone may require widening the stagger step beyond `SPIRAL_STEP`. Tune by eye.
- The frozen build's first launch can be slow — don't mistake startup latency for a hang.
