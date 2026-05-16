---
plan: 2.1
wave: 2
status: COMPLETE
date: 2026-05-15
commits:
  - 8670e6c  shipyard(phase-4): extract shape-drawer dispatch and refactor create_racers
  - d4c1a1a  shipyard(phase-4): refactor announce_result and celebrate to use racer-dict identity
  - 0704f03  shipyard(phase-4): fix user_won and celebrate call site to use is-identity in main.py
tests: 79/79 pass (baseline was 79/79; no regressions)
---

# SUMMARY-2.1 -- Shape-drawer dispatch + win-message identity refactor

## Baseline

79/79 tests passing before any changes. No pre-existing failures.

## Task 1 -- Shape dispatch refactor (race.py)

### What was done

1. Extended `from constants import` to include L_BASE, SNAKE_STRETCH_WID, SNAKE_LENGTHS.

2. Added draw_turtle_shape(t) above create_racers: calls t.shape("turtle").
   Thin wrapper replicating prior inline Turtle(shape="turtle"). Color left
   for place_racers_on_track, same as before.

3. Added draw_snake_shape(t, length_units): calls t.shape("classic") then
   t.shapesize(stretch_wid=SNAKE_STRETCH_WID, stretch_len=L_BASE * length_units).
   Produces Shadow ~32px > Anaconda ~27px > Ralph ~11px at 6:5:2 ratio.
   PHASE-4-PLACEHOLDER comment marks polygon-fallback escalation point
   (CONTEXT-4 Decision 1).

4. Added _SHAPE_DRAWERS = {"turtle": draw_turtle_shape, "snake": draw_snake_shape}.

5. Refactored create_racers: drawer = _SHAPE_DRAWERS[data["shape_drawer"]];
   enumerate(zip(...)); bare Turtle(); branch on species=="snakes" to pass
   SNAKE_LENGTHS[i]. Racer dict structure unchanged.

### Verification: pytest 79/79, smoke OK, grep Turtle(shape= zero matches.

## Task 2 -- Win-message identity refactor (race.py)

### What was done

announce_result: added winner_racer = next(r for r in racers if r['o'] is winner).
Replaced pencolor() equality with is-identity. Replaced all pencolor() display
refs with winner_racer['color'] and winner_racer['name']. Fixes Ralph's
"(0.91, 0.62, 0.31) racer" tuple display bug.

celebrate: widened signature to (winner, won, racers). Replaced
face_color = winner.pencolor() with is-identity lookup + winner_racer['color'].

Note: the celebrate call-site in main.py was updated in Task 3 (main.py's
commit), consistent with the plan's "Task 2 touches race.py only" rule.

### Verification: pytest 79/79, smoke OK, no pencolor() in either function.

## Task 3 -- main.py identity fix

### What was done

1. user_won = winning_turtle is racers[user_bet - 1]['o']  (was pencolor()==)
2. race.celebrate(winning_turtle, user_won, racers)  (widened call site)

### Verification: pytest 79/79, smoke OK, grep pencolor in main.py zero hits.

## Behavioral notes

Turtle mode: no visible change. draw_turtle_shape replicates prior behavior
exactly. is-identity win check is logically equivalent for turtles (unique colors).

Snake mode (expected visible change): snakes now appear as stretched classic
arrow shapes instead of turtle shapes from Phase 3. This IS the intended
Phase 4 change. Race finish behavior unchanged (center-position progress check).
Head-position fairness fix deferred to PLAN-3.1 per explicit constraint.

## Deviations

None. celebrate call-site widening (main.py) grouped with Task 3's main.py
commit -- consistent with plan's file-per-task rule.

## Final state

race.py: draw_turtle_shape, draw_snake_shape, _SHAPE_DRAWERS, refactored
create_racers, announce_result and celebrate using is-identity. Zero pencolor()
calls in either function.

main.py: user_won uses is-identity. celebrate passes racers. Zero pencolor() calls.

Tests: 79/79 throughout. 3 atomic commits, one per task.
