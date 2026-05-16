# Review: Plan 2.1

## Verdict: PASS

All 3 commits implement the plan correctly. One minor signature deviation flagged (cosmetic). 79/79 pass throughout. Snake mode now renders as stretched-classic shapes — visible behavioral change, expected per CONTEXT-4.

## Findings

### Critical

None.

### Minor

- **`celebrate` signature: `(winner, won, racers)` keeps the unused `won` parameter.** Plan suggested simplifying to `celebrate(winner, racers)` since `won` was already unused inside the function (`face_color` derives from winner alone). Builder kept `won` to preserve the existing call-site shape. End state is functionally equivalent; `won` remains dead in the function body. Cosmetic — could drop in a future cleanup but not blocking.

### Positive

- **Shape dispatch is exact per CONTEXT-4 + RESEARCH:**
  - `from constants import L_BASE, SNAKE_STRETCH_WID, SNAKE_LENGTHS` added to imports
  - `draw_turtle_shape(t)` calls `t.shape("turtle")` (color applied later in place_racers_on_track — preserved Phase 3 behavior)
  - `draw_snake_shape(t, length_units)` calls `t.shape("classic")` + `t.shapesize(stretch_wid=SNAKE_STRETCH_WID, stretch_len=L_BASE * length_units)`
  - `_SHAPE_DRAWERS = {"turtle": draw_turtle_shape, "snake": draw_snake_shape}` defined AFTER both functions (no NameError risk)
  - `create_racers(species)` cleanly dispatches; bare `Turtle()` (no shape kwarg); snake branch passes `SNAKE_LENGTHS[i]` correctly
  - Polygon-fallback comment placeholder per CONTEXT-4 Decision 1 included

- **Win-check identity refactor exhaustive:**
  - `announce_result`: `winner_racer = next(r for r in racers if r['o'] is winner)`; uses `winner_racer['color']` (configured string) for display; uses `winner_racer['name']` for messaging — eliminates the Phase 3 hex-tuple ugly display for Ralph
  - `celebrate`: same `winner_racer` resolution via identity; `face_color = winner_racer['color']` (no more pencolor() round-trip)
  - `main.py:40`: `user_won = winning_turtle is racers[user_bet - 1]['o']` — identity, fixes pre-existing two-racers-same-color fragility
  - `main.py:42`: `race.celebrate(winning_turtle, user_won, racers)` — racers passed correctly

- **Three atomic commits**, file-specific git add maintained, per-task discipline excellent.

- **No head-offset code added** — correctly deferred to Wave 3 (PLAN-3.1).

- **No regression to turtle mode** — `Turtle()` then `t.shape("turtle")` is functionally identical to old `Turtle(shape="turtle")`.

- **Snake mode visual change is EXPECTED** per CONTEXT-4 Decision 1: snakes now render as stretched-classic arrows (Shadow ~32 units along heading, Anaconda ~27, Ralph ~11). This is the planned Phase 4 visual.

- **Test suite stays GREEN at 79/79** — no regression, no new tests in this plan (shape rendering is smoke-only territory).

### Carry-over to Wave 3 (PLAN-3.1)

- Universal head-offset progress adjustment in `run_race`
- New `tests/test_race.py` for head-offset math
- Manual smoke gate

### Open question for smoke

When you run the snake race in PLAN-3.1's smoke gate, observe whether stretched-classic at `L_BASE = 0.6` reads as "snake-like." If not, escalate to the polygon fallback per CONTEXT-4 Decision 1 (the placeholder comment is already in `draw_snake_shape`).

Critical: 0 | Minor: 1 (unused `won` param) | Positive: 7
