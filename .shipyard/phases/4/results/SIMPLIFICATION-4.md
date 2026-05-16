# Simplification Report — Phase 4

## Verdict: LOW_PRIORITY

Phase 4 is the centerpiece refactor — its job is to *introduce* shape dispatch, length scaling, and head-offset math. A few small items found; nothing blocking. Two are corrections to earlier reviews.

## High Priority

None.

## Medium Priority

### S4.1 — `constants.py:31` `SNAKE_LENGTHS` ratio comment is misleading (pre-existing)

- **Location:** `constants.py:31` (approximate)
- **Description:** Comment reads `# 6:5:2 ratio is Shadow:Anaconda:Ralph by value` — describing the descending-magnitude ordering. But `SNAKE_LENGTHS = [6, 2, 5]` and `SNAKE_NAMES = ["Shadow", "Ralph", "Anaconda"]`, so by-position the array reads Shadow=6, **Ralph=2**, Anaconda=5. The comment risks misleading a fresh reader into assuming the by-name positional order is Shadow:Anaconda:Ralph (which it isn't).
- **Suggestion:** Replace with explicit per-name annotation: `# Shadow=6, Ralph=2, Anaconda=5 (positional with SNAKE_NAMES; the visual 6:5:2 ratio is by-magnitude)`. Or just: `# By position: Shadow=6, Ralph=2, Anaconda=5`.
- **Carried-forward from:** REVIEW-3.1 flagged this. Pre-existing from Phase 1; never addressed. `tests/test_constants.py:test_snake_lengths_positional_values` enforces the correct mapping in code, so the bug is comment-only. Trivial fix.

## Low Priority

### S4.2 — `_SHAPE_UNIT_SIZE` is function-local in `run_race`

- **Location:** `race.py` (inside `run_race`, around line 264)
- **Description:** `_SHAPE_UNIT_SIZE = 9` is defined inside `run_race`. If another function later needs this constant (e.g., a future polygon-fallback drawer that uses the same unit basis), it'll be duplicated.
- **Suggestion:** Lift to module-level alongside `STONE_COLOR`, `FINISH_CHECKER_SIZE`, etc. Doesn't change behavior; improves discoverability.
- **Effort:** Trivial.
- **Carried-forward from:** REVIEW-3.1 suggested this.

### S4.3 — `next(r for r in racers if r['o'] is winner)` duplicated across `announce_result` and `celebrate`

- **Locations:** `race.py` `announce_result` and `celebrate` bodies
- **Description:** Both functions resolve the winner_racer the same way. Just-above Rule-of-Two threshold.
- **Suggestion:** Extract a small helper `_find_racer_by_turtle(racers, t)`. Trade-off: 2 callers, the helper would be a one-liner. Could go either way.
- **Effort:** Trivial.
- **Recommendation:** Defer unless a third caller emerges (Phase 5 polish or a documenter pass that adds another consumer of winner_racer).

### S4.4 — Missing Anaconda concrete plug-in test in `tests/test_race.py`

- **Location:** `tests/test_race.py`
- **Description:** Shadow (stretch_len=3.6 → arc=16.2) and Ralph (stretch_len=1.2 → arc=5.4) have explicit plug-in tests. Anaconda (stretch_len=3.0 → arc=13.5) is missing. Symmetric coverage is nicer but not required.
- **Suggestion:** Add `test_head_offset_arc_anaconda` to complete the species triple. Three lines of test code.
- **Carried-forward from:** REVIEW-3.1 suggested.

## Notes / corrections

- **REVIEW-2.1 flagged `won` in `celebrate` as unused — that finding was incorrect.** REVIEW-3.1 corrected it: `won` controls smile/frown mouth at `race.py:517-524`. The signature `(winner, won, racers)` is the right shape; no parameter to drop.

## AI bloat / dead code / complexity hotspots

- **AI bloat:** None detected.
- **Dead code:** None.
- **Complexity:** `run_race` body grew with the head-offset block (~14 lines including comment). Still readable; no extraction needed yet.
- **Inline comment density in race.py is high** but appropriate — the head-offset math is non-obvious and the calibration caveat needs documentation.

## Already-flagged carry-overs (NOT re-flagged)

- `assets/midi/` untracked (user added; possibly future feature)
- Spiral 3-lane visual tuning (deferred to Phase 5)

## Summary

- Cross-task duplication: 1 low (S4.3 — winner_racer lookup, just above Rule-of-Two)
- Pre-existing comment hazard: 1 medium (S4.1 — easy fix)
- Coverage gap: 1 low (S4.4 — Anaconda test for symmetry)
- Module-vs-local refactor opportunity: 1 low (S4.2 — _SHAPE_UNIT_SIZE)
- AI bloat: 0
- Dead code: 0

## Recommendation

Non-blocking. **Address S4.1 (comment fix) opportunistically** — 30 seconds. Defer S4.2-S4.4 to a Phase 5 polish pass or skip entirely.
