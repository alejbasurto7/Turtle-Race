# Review: Plan 3.1

## Verdict: PASS (pending human manual smoke)

All 10 `main.py` call-site substitutions correct. I2 docstring fix landed. Banned-identifier sweep clean. Manual `python main.py` smoke on all 3 tracks is the only remaining gate — that's a human action.

## Findings

### Critical

None.

### Important

- **Manual smoke gate remains open.** SUMMARY-3.1 declares the `python main.py` parity smoke on straight/rectangular/spiral as `PENDING_HUMAN_VERIFICATION`. Required by CONTEXT-2.md Decision 6 ("zero visual regression"). No code change needed — this is Alejandro's manual gate.
- **Pre-existing `pencolor()` fragility (`main.py:38`):** `user_won = winning_turtle.pencolor() == racers[user_bet - 1]['o'].pencolor()`. If two racers ever share a color, the comparison can mis-attribute a win. Pre-existing (predates Phase 2), not introduced by this plan. Future cleanup: `user_won = winning_turtle is racers[user_bet - 1]['o']`. Out of scope for Phase 2.

### Suggestions

- **`TURTLE_COLORS` constant remains** in `constants.py:8` and is referenced inside `SPECIES["turtles"]["colors"]`. The plan's "remove from `main.py`" was scoped to the import line, not the constant itself. Correct as-is.
- **Pre-existing `_build_spiral_legs` loop-variable shadow** (`tracks.py:195`, `for n in range(max_legs):`) — flagged in REVIEW-1.1 and REVIEW-2.1, still unaddressed. Out of scope for Phase 2; queue for a future cleanup pass.

### Positive

- **All 10 main.py substitutions exact:**
  - `from constants import TURTLE_COLORS` removed
  - `create_racers("turtles")` at line 28 (BEFORE `draw_boundary_stones` — G7 fix)
  - `place_racers_on_track(racers, track_name)` at line 30
  - `draw_start_line(track_name, len(racers))`, `draw_finish_line(track_name, len(racers))`, `draw_boundary_stones(track_name, len(racers))`
  - `run_race(racers, track_name, user_bet)`, `show_podium(racers, finish_order)`, `announce_result(winning_turtle, user_bet, racers)`
  - `dialogs.get_user_bet()` left untouched (Phase 3 scope)
- **I2 fix landed:** `# Shape dispatch (shape_drawer sentinel) is Phase 4's concern.` now lives at `race.py:140` as a real `#` code comment, OUT of the docstring.
- **Banned-identifier sweep:** repo-wide grep returns only `tests/test_tracks.py:38` (prose comment about the deleted `N_LANES` — intentional, harmless). Zero live code references to old names.
- **Test suite green:** 76/76 pass. Same count as Wave 2 — no regression introduced by Wave 3.
- **Per-task commits maintained:** 2 commits (`e036be0` wire-up + I2 fix, `a9cc82e` SUMMARY).

## Wave 3 Gate: OPEN (pending human smoke) — Phase 2 cleared for verification/audit/simplification/documentation passes.

Critical: 0 | Important: 2 | Suggestions: 2
