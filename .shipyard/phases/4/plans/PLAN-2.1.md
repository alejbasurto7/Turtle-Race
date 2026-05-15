---
phase: snakes-racer-mode
plan: 2.1
wave: 2
dependencies: [1.1, 1.2]
must_haves:
  - Extract draw_turtle_shape(t) and draw_snake_shape(t, length_units) in race.py
  - Define module-level _SHAPE_DRAWERS dispatch in race.py
  - Refactor create_racers(species) to use the dispatch and pass SNAKE_LENGTHS[i] for snakes
  - Fix announce_result + celebrate to identify the winning racer by dict-identity (`is`) on the turtle object, not by pencolor() comparison
  - Fix main.py:40 user_won check from pencolor() == pencolor() to `is` identity
  - Display the configured color STRING (not the pencolor() tuple) in the win message — fixes Ralph's "(0.91, 0.62, 0.31) racer" bug
  - Zero behavior regression in turtle mode; snakes still look like classic turtles after this plan (head-offset wiring comes in PLAN-3.1)
  - pytest stays green
files_touched:
  - race.py
  - main.py
tdd: false
risk: medium
---

# PLAN-2.1 — Shape-drawer dispatch + win-message identity refactor

## Context

This is the structural heart of Phase 4. Per CONTEXT-4 Decisions 1, 4, and 5, plus RESEARCH.md §1, §4, §5, §6:

1. **Shape dispatch (Decision 4):** `SPECIES[species]["shape_drawer"]` is currently a string sentinel (`"turtle"` / `"snake"`). Resolve it to a callable inside race.py via a module-level `_SHAPE_DRAWERS` dict. Extract the existing inline `Turtle(shape="turtle")` setup into a `draw_turtle_shape(t)` function for symmetry.

2. **Snake shape (Decision 1):** `draw_snake_shape(t, length_units)` uses stretched `classic` per CONTEXT-4 Decision 1. No polygon-fallback escalation yet — that's a smoke-driven decision in PLAN-3.1.

3. **Win-message identity fix (Decision 5 item 3 + RESEARCH.md §6):** the current `announce_result` uses `winner.pencolor()` three times and `winner.pencolor() == racers[user_bet-1]['o'].pencolor()` to detect the user win. This is fragile (Ralph's hex round-trips to a float tuple → ugly display) and uses non-identity comparison (two racers sharing a color would mis-attribute). Switch to dict-identity using `is` on the turtle object, and pull `name` + `color` from the matched racer dict for display.

4. **main.py:40 (Gotcha §10.8):** same root cause one level up. Switch from `pencolor()`-equality to `is` identity comparison.

**Crucially:** this plan does NOT yet add head-position finish detection. That's PLAN-3.1. After this plan, turtle mode is byte-identical to Phase 3; snake mode races with stretched-classic snake-shaped racers but uses the legacy center-position finish check (still functional, fairness fix lands in 3.1).

Wave 2 because both files touched here depend on Wave 1's `L_BASE`/`SNAKE_STRETCH_WID` constants (PLAN-1.1) for `draw_snake_shape`. PLAN-1.2's tracks.py/dialogs.py touches are disjoint but also Wave 1, so Wave 2 starts cleanly after both 1.x plans finish.

## Tasks

<task id="1" files="race.py" tdd="false">
  <action>In race.py: (a) Add `from constants import ..., L_BASE, SNAKE_STRETCH_WID, SNAKE_LENGTHS` to the existing constants import line (Grep `from constants import` to find it; add the three names if not already imported). (b) Above `create_racers`, define two module-level functions: `draw_turtle_shape(t)` that calls `t.shape("turtle")` (matches the existing inline `Turtle(shape="turtle")` behavior — color is still applied later in `place_racers_on_track`); and `draw_snake_shape(t, length_units)` that calls `t.shape("classic")` followed by `t.shapesize(stretch_wid=SNAKE_STRETCH_WID, stretch_len=L_BASE * length_units)`. (c) Immediately below them, define `_SHAPE_DRAWERS = {"turtle": draw_turtle_shape, "snake": draw_snake_shape}` (per CONTEXT-4 Decision 4). (d) Refactor `create_racers(species)` per RESEARCH.md §5: read `drawer = _SHAPE_DRAWERS[SPECIES[species]["shape_drawer"]]`; iterate with `enumerate(zip(data["names"], data["colors"]))`; create a bare `Turtle()` (no shape kwarg); if `species == "snakes"` call `drawer(t, SNAKE_LENGTHS[i])` else call `drawer(t)`; build the racer dict as before (`name`, `color`, `o`). Add a short comment near `draw_snake_shape` reserving space for the polygon-fallback escalation per CONTEXT-4 Decision 1.</action>
  <verify>pytest && python -c "import race; assert callable(race.draw_turtle_shape); assert callable(race.draw_snake_shape); assert race._SHAPE_DRAWERS['turtle'] is race.draw_turtle_shape; assert race._SHAPE_DRAWERS['snake'] is race.draw_snake_shape; print('OK')"</verify>
  <done>pytest is fully green. The `python -c` smoke prints `OK`. Grep `Turtle(shape=` in race.py returns zero matches inside `create_racers` (the inline shape kwarg has been replaced by the drawer dispatch).</done>
</task>

<task id="2" files="race.py" tdd="false">
  <action>In race.py: refactor `announce_result` and `celebrate` (lines ~373-394) per RESEARCH.md §6. (a) `announce_result(winner, user_bet, racers)`: at the top, resolve `winner_racer = next(r for r in racers if r['o'] is winner)`; then compute `won = winner_racer['o'] is racers[user_bet - 1]['o']`; build the win/lose message strings using `winner_racer['name']` (existing 'name' key, populated by `create_racers` since Phase 2) and `winner_racer['color']` (the configured string — for Ralph this is the `"#D2A679"` hex, NOT the float tuple). Replace ALL `winner.pencolor()` references in the function body. (b) `celebrate(winner, racers)`: change `face_color = winner.pencolor()` to resolve the same `winner_racer` via the `is`-identity lookup and use `face_color = winner_racer['color']`. The `pen.color(face_color)` call works equally well with a hex string. (c) If `celebrate`'s signature currently doesn't accept `racers`, widen it and update the call site at the bottom of `run_race`. Grep `celebrate(` to find both call sites.</action>
  <verify>pytest && python -c "import race; import inspect; src = inspect.getsource(race.announce_result) + inspect.getsource(race.celebrate); assert 'pencolor()' not in src, 'pencolor() still present in announce_result/celebrate'; print('OK')"</verify>
  <done>pytest is fully green. The smoke `python -c` prints `OK` (no `pencolor()` calls remain in either function body). The win-message format string now interpolates a name + color-string, never a tuple.</done>
</task>

<task id="3" files="main.py" tdd="false">
  <action>In main.py: change the user-win check on line 40 (Grep "pencolor" in main.py to confirm the exact line). The current pattern is `winner.pencolor() == racers[user_bet - 1]['o'].pencolor()` (or similar). Replace with the dict-identity form: `winner is racers[user_bet - 1]['o']`. This is the same root-cause fix as Task 2 one level up: identity over color-equality. Confirm via Grep that `pencolor()` no longer appears in main.py at all.</action>
  <verify>pytest && python -c "import ast, pathlib; src = pathlib.Path('main.py').read_text(); assert 'pencolor()' not in src, 'pencolor() still in main.py'; print('OK')"</verify>
  <done>pytest is fully green. The smoke `python -c` prints `OK`. Grep `pencolor` in main.py returns zero hits.</done>
</task>

## Notes for the builder

- Per-task atomic commits. Task 1 touches race.py only (shape extraction + dispatch + create_racers refactor — a single coherent commit). Task 2 touches race.py only (win-message refactor — second coherent commit). Task 3 touches main.py only.
- Do NOT add head-offset progress adjustment in this plan. That is intentionally deferred to PLAN-3.1 so this plan stays a pure refactor with a verifiable "no behavior regression" gate.
- A full manual `python main.py` smoke is OPTIONAL here (the gate is in PLAN-3.1) but recommended after Task 3 to confirm turtle mode is still indistinguishable from Phase 3.
- Write SUMMARY-2.1.md to disk before returning.
