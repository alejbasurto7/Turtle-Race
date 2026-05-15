# Phase 4 — Discussion Capture

Decisions locked before research/architect/builder dispatch. The downstream agents must respect these.

## Decision 1 — Snake shape: stretched `classic` first, polygon fallback

`draw_snake_shape(t, length_units)` configures a `turtle.Turtle` to read as a snake:

```python
def draw_snake_shape(t, length_units):
    t.shape("classic")
    t.shapesize(stretch_wid=SNAKE_STRETCH_WID, stretch_len=L_BASE * length_units)
```

**Rationale:** quickest to implement, arrow-pointing-forward reads as a snake head, no asset registration needed.

**Fallback decision deferred to Phase 4 smoke:** if the stretched-classic shape doesn't read as a snake at race scale, escalate by registering a 2-segment polygon silhouette via `screen.register_shape("snake_<name>", polygon)`. Decide visually during the build's manual-smoke step; document the call in `race.py` as a comment.

**Polygon-fallback gotcha if escalation needed:** `register_shape` persists across `screen.clear()`, so register ONCE at startup or guard against re-registration in the round loop.

## Decision 2 — L_BASE = 0.6 (starting value)

```python
L_BASE = 0.6   # in constants.py — already exists as 1.0 placeholder from Phase 1; tune to 0.6 in Phase 4
SNAKE_STRETCH_WID = 0.5   # NEW in constants.py — controls snake body thickness
```

**Math (rationale):**
- `turtle.classic` default body length ≈ 10 units at `stretch_len = 1.0`
- Shadow: `6 * 0.6 * 10 ≈ 36 units` long. Reasonable size on a 300-unit-wide straight track.
- Anaconda: `5 * 0.6 * 10 = 30 units`
- Ralph: `2 * 0.6 * 10 = 12 units`
- `LANE_SPACING = 24` → at `stretch_wid = 0.5`, snake width ≈ 5 units. Comfortably fits vertically; visually thinner than the turtle classic (which is ~10 units wide at default `stretch_wid = 1.0`).
- 6:5:2 ratio preserved; visually distinct from turtles.

**Tune during smoke** — if Shadow looks too short or Ralph looks invisible, adjust `L_BASE`. If snakes look too thick or too thin, adjust `SNAKE_STRETCH_WID`. Smoke-driven empirical decision.

## Decision 3 — Head-position finish detection: universal

Both turtles and snakes use head-position for finish detection. Turtle module shapes are symmetric, so applying head-offset to turtles doesn't change behavior. Cleaner code: one finish-detection path, no species branching in `run_race`.

**Implementation:** the head offset is the current `stretch_len * shape_unit_size / 2` along the current `heading()` direction. Compute and add to the racer's position before the finish-line check.

**Edge case to verify in smoke:** for rectangular and spiral tracks where racers turn corners, `heading()` changes during the race. The head offset must use the *current* heading, not the lane's nominal direction.

## Decision 4 — `SHAPE_DRAWERS` dispatch in `race.py`

Resolves the string sentinel (`"turtle"` / `"snake"`) from `SPECIES[species]["shape_drawer"]` to a callable inside `race.py`:

```python
# In race.py, after draw_turtle_shape and draw_snake_shape are defined:
_SHAPE_DRAWERS = {
    "turtle": draw_turtle_shape,
    "snake":  draw_snake_shape,
}
```

`create_racers(species)` reads `SPECIES[species]["shape_drawer"]`, looks up the callable, and calls it on each racer's `turtle.Turtle`. For snakes, also passes `SNAKE_LENGTHS[i]` as the length parameter.

**`draw_turtle_shape`** is a thin wrapper that does what `create_racers` currently does (sets `shape("turtle")` and color). Extract the existing logic into this function for symmetry.

## Decision 5 — Phase 4 cleanup scope (all 4 items in)

Bundle these carry-forward items into Phase 4 commits where the file is already being touched:

1. **`dialogs.py` stale imports** — remove unused `TURTLE_NAMES`, `TURTLE_IMAGES`; add `SNAKE_NAMES` for symmetry. Fold into the Phase 4 dialogs touches (the docstring add below).
2. **`get_user_species()` docstring** — add per DOCUMENTATION-3 actionable: mention modal/blocking behavior (`grab_set()` + `wait_window()`), return value (`"turtles"` or `"snakes"`).
3. **`race.py:373/376` win-message tuple display** — current code: `print(f"You won! The {winner.pencolor()} racer is the winner!")` prints `"The (0.91, 0.62, 0.31) racer is the winner!"` for Ralph. Fix by using the winner's name from the racer dict instead — needs plumbing the racer (not just the turtle) into `announce_result`. Or pull color from `racers[lane_idx]['color']` where `lane_idx` is the winner's index. Architect to decide cleanest fix.
4. **`tracks.py:_build_spiral_legs` `n` shadow** — rename `for n in range(max_legs):` → `for leg_i in range(max_legs):`. Trivial. Flagged in REVIEW-1.1 (Phase 2) and REVIEW-2.1 (Phase 2) and never addressed.

## Decision 6 — Phase 4 end-state: snakes mode races and looks like snakes

End of Phase 4, picking **Snakes** must:
1. Show the snake bet dialog (Phase 3 wired this)
2. Run a 3-racer race with **3 visually-snake-shaped racers** (not turtle-shaped) in correct 6:5:2 length ratio
3. Reach the podium correctly with 3 finishers
4. Race fairness: head-position finish detection means longer snakes aren't unfairly advantaged or disadvantaged

Picking **Turtles** must remain visually indistinguishable from Phase 3 (zero regression on turtle mode).

This is the manual-smoke gate for Phase 4.

## Decision 7 — Spiral 3-lane visual tuning: still deferred to Phase 5

ROADMAP put spiral 3-lane visual tuning in Phase 5. Keep that deferral. If Phase 4's smoke reveals snake racers on spiral look weird *due to the snake shape itself* (not due to lane geometry), fix the shape. If the spiral geometry is the issue, capture observations and let Phase 5 handle them.

## Builder/agent reminders (still relevant)

1. **Write SUMMARY-W.P.md to disk before returning.** Hard acceptance criterion.
2. **Reviewers MUST write REVIEW-W.P.md to disk.** Phase 3's reviewer-disk-write pattern worked — keep it.
3. **File-specific `git add`.** Never `git add .`.
4. **Per-task atomic commits.** Discipline was good in Phase 3.
5. **Manual smoke is the gate** for the final wave — Phase 4 specifically needs visual confirmation of: snake-shape legibility, length ratio, head-position fairness across multiple races.
