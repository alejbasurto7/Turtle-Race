# Simplification Report — Phase 2

## Verdict: LOW_PRIORITY

Phase 2 is a focused refactor — its job is to *introduce* parameterization, not simplify it further. A few small items found; nothing blocking.

## High Priority

None.

## Medium Priority

None.

## Low Priority

### S2.1 — Carried-over: `_build_spiral_legs` loop variable `n` shadows the lane-count parameter

- **Type:** Rename (shadow disambiguation)
- **Effort:** Trivial
- **Location:** `tracks.py:195` (or thereabouts) — `for n in range(max_legs):`
- **Description:** Pre-existing from before Phase 2. After Phase 2, `n` is the universal lane-count parameter across `tracks.py`. The reuse of `n` as a local loop counter in `_build_spiral_legs` is now confusing; reading the function, `n` toggles between meanings line by line.
- **Suggestion:** Rename to `leg_i` or `leg_num` (`for leg_i in range(max_legs): pair_idx = leg_i // 2 ...`).
- **Why deferred:** Flagged in REVIEW-1.1 (M2) and REVIEW-2.1 (S2). Genuinely out of scope for Phase 2's "introduce `n`" mandate; a dedicated cleanup pass before or during Phase 4 makes sense.

### S2.2 — `main.py` recomputes `len(racers)` three times in adjacent lines

- **Type:** Hoist
- **Effort:** Trivial
- **Location:** `main.py:29-32` — `draw_boundary_stones(track_name, len(racers))`, `draw_start_line(track_name, len(racers))`, `draw_finish_line(track_name, len(racers))`
- **Description:** Three back-to-back calls compute `len(racers)` independently. Each is O(1) so performance is irrelevant; readability is the issue.
- **Suggestion:** `n = len(racers)` after `create_racers`, then pass `n` into each call. Mirrors the established pattern inside `race.py` (`n = len(racers)` is computed once per function).
- **Why low:** Cosmetic. Either form is fine. Apply during Phase 3 if you're already in `main.py` adding the species dialog wiring.

## Notes

- **`n`-parameter threading is exhaustive but warranted.** Every public `tracks.py` function genuinely needs `n` — there's no spot where the parameter is dead weight or where N=4 logic is tied so tightly to other constants that the threading is excessive. CONTEXT-2.md Decision 1's "hard refactor, no defaults" was the right call.
- **No AI bloat detected** — assertion messages concise, no verbose try/except, no premature helper classes, no decorator misuse.
- **Test parametrize introduction is lean** — 5 functions × 22 invocations, no over-engineering. The module docstring documenting the parametrize style break is appropriate.

## Summary

- Cross-task duplication: 1 cosmetic (S2.2)
- Pre-existing shadowing: 1 (S2.1, carried over from prior phases)
- Dead code: 0
- Unnecessary abstractions: 0
- AI bloat: 0
- Cleanup impact if both addressed: ~4 lines net

## Recommendation

Non-blocking. Address S2.1 in a future cleanup pass (Phase 4 candidate). Address S2.2 opportunistically during Phase 3's `main.py` work.
