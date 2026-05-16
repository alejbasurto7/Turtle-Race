# Phase 4 Verification

## Overall phase status: **COMPLETE (pending manual smoke)**

All automated gates pass. Manual smoke is the only remaining gate before Phase 4 closes.

## Per-deliverable coverage

| CONTEXT-4.md / ROADMAP deliverable | Status | Evidence |
|---|---|---|
| `draw_turtle_shape(t)` in `race.py` | ✓ | commit `8670e6c`, REVIEW-2.1 PASS |
| `draw_snake_shape(t, length_units)` in `race.py` | ✓ | same commit; uses `t.shape("classic")` + `t.shapesize(stretch_wid=SNAKE_STRETCH_WID, stretch_len=L_BASE * length_units)` |
| `_SHAPE_DRAWERS = {"turtle": ..., "snake": ...}` dispatch | ✓ | same commit |
| `create_racers(species)` uses dispatch | ✓ | same commit; bare `Turtle()` + drawer dispatch + species-aware length pass |
| `L_BASE = 0.6` (tuned from 1.0) | ✓ | commit `5c30980`; REVIEW-1.1 PASS |
| `SNAKE_STRETCH_WID = 0.5` | ✓ | same commit |
| Universal head-position finish detection | ✓ | commit `f810a69`; REVIEW-3.1 PASS; `head_offset_progress[]` parallel array, computed once per race, applied universally |
| `announce_result` uses racer-dict identity (no pencolor()) | ✓ | commit `d4c1a1a` |
| `celebrate` uses racer-dict identity | ✓ | same commit; signature widened to `(winner, won, racers)`; `won` IS used (mouth selection) |
| `main.py:40` `user_won` uses `is` identity | ✓ | commit `0704f03` |
| Win-message displays winner name/color from racer dict (Ralph tuple bug fixed) | ✓ | commit `d4c1a1a` |
| `dialogs.py` stale imports removed | ✓ | commit `612faf5`; REVIEW-1.2 PASS |
| `get_user_species()` docstring added | ✓ | same commit |
| `tracks.py:_build_spiral_legs` `n` → `leg_i` | ✓ | commit `ea47c30` |
| 5 new head-offset math tests | ✓ | commit `95f42d8`; tests/test_race.py |
| End-state turtle race works | ⏳ | **PENDING_HUMAN_VERIFICATION** |
| End-state snakes look snake-like with 6:5:2 length ratio | ⏳ | **PENDING_HUMAN_VERIFICATION** |
| Head-position fairness (Ralph not advantaged/disadvantaged) | ⏳ | **PENDING_HUMAN_VERIFICATION** |

## Review verdicts

| Plan | Verdict | Notes |
|---|---|---|
| 1.1 | PASS | Constants tune clean; commit `c1a38f2` was a near-no-op (tests pre-existed) — minor |
| 1.2 | PASS | Cleanups clean, no findings |
| 2.1 | PASS | Shape dispatch + win-check identity refactor; minor noted `won` param later corrected to "actually used" by REVIEW-3.1 |
| 3.1 | PASS | Head-offset math + tests; surfaced pre-existing SNAKE_LENGTHS comment hazard (now in SIMPLIFICATION-4 S4.1) |

No CRITICAL review findings unresolved.

## Quality-gate results

- **Test suite:** `pytest` → **84/84 passed** (was 79 + 5 new head-offset math tests). No regressions.
- **Security audit:** AUDIT-4.md → **CLEAN**. No findings.
- **Simplification:** SIMPLIFICATION-4.md → **LOW_PRIORITY**. One opportunistic fix recommended (S4.1 comment hazard); rest defer to Phase 5.
- **Documentation:** DOCUMENTATION-4.md → **MINOR_GAPS**. CLAUDE.md should mention shape-dispatch extension point + finish-detection auto-adapt. Recommend folding into Phase 4 wrap-up.

## IaC

No IaC files touched. N/A.

## Gaps identified

**One open gate: manual `python main.py` smoke.** Required for Phase 4 to be declared closed. Smoke checklist:

1. **Turtle mode regression:** pick Turtles, race on each of 3 tracks. Confirm 4 turtles race fairly to podium, no visual regression vs. Phase 3 baseline.
2. **Snake mode visual:** pick Snakes, race on each of 3 tracks. Confirm:
   - Snakes render as visibly snake-like stretched arrows (NOT turtle shapes)
   - Length ratio Shadow > Anaconda > Ralph reads on screen
   - Stretched-classic shape decision (CONTEXT-4 Decision 1) — does it look snake-y enough? If NO, escalate to polygon fallback in a Phase 4 follow-up.
3. **Head-position fairness:** run Snakes mode multiple times. Across enough races, Ralph (shortest, would be disadvantaged with center-position) should win sometimes. Eyeball, not statistical.
4. **Win-message correctness:** when Ralph wins, the message should display his color as a string (e.g., "#E89F4F"), NOT a tuple `(0.91, 0.62, 0.31)`.
5. **Cross-round species switching:** alternate Turtles → Snakes → Turtles → Snakes. No Tk state leak, no shape persistence bugs.

## Recommendations for Phase 5

1. **Address SIMPLIFICATION-4 S4.1** (`SNAKE_LENGTHS` comment) — opportunistic, 30 seconds.
2. **Address DOCUMENTATION-4 actionable** — append shape-dispatch + finish-detection paragraph to CLAUDE.md. Could fold into Phase 4 wrap-up commit (the same pattern Phase 3 used) OR defer to Phase 5's documentation pass.
3. **Spiral 3-lane visual tuning** (deferred since Phase 2). Now is the time, especially since snakes-on-spiral is a new visual surface.
4. **`L_BASE` re-tuning** if smoke shows snakes look too short or too long. Empirical adjustment.
5. **Polygon fallback escalation** if stretched-classic doesn't read as a snake during smoke.
6. **Frozen-build test** — `pyinstaller turtle_race.spec` must succeed and the exe must run both modes correctly. This is the Phase 5 gate.
7. **Optional:** SIMPLIFICATION-4 S4.2-S4.4 (lift `_SHAPE_UNIT_SIZE` to module-level, extract winner_racer helper, add Anaconda concrete test). Defer.

## Conclusion

Phase 4 is **COMPLETE** as far as automated verification can prove. The manual smoke remains the gating action — it's the truthtest for the visual snake shape, length ratio, and head-position fairness that pytest can't measure.
