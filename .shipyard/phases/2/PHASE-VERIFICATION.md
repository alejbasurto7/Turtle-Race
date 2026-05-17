# Phase 2 Verification

## Overall Status: COMPLETE

(Phase 2 is small — 1 plan, 3 tasks, ~25 production lines + 1 smoke utility. The orchestrator performed phase verification inline rather than dispatching a verifier agent. This is the post-build phase-completion artifact; the plan-level verification document is `.shipyard/phases/2/VERIFICATION.md`.)

## Coverage of Phase 2 Success Criteria (from ROADMAP.md)

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Single `record_race(...)` call inserted in `main.py` between `run_race(...)` and `show_podium(...)` | MET | `main.py:42` calls `leaderboard.record_race(...)`; `main.py:43` is the blank line; `main.py:44` is `user_won = ...`; `main.py:45` is `race.show_podium(...)`. The call is correctly placed before the podium. |
| 2 | Inline adapter `[racers[i]['name'] for i in finish_order]` | MET | `main.py:41` literally is this comprehension. |
| 3 | After 1 race, `%APPDATA%\TurtleRace\leaderboard.json` contains 1 record with `schema_version:1` | MET | Smoke run output (after race 1 of 3): one record at `2026-05-16T22:30:22`, `species:"turtles"`, `track:"straight"`, 4-entry finish_order. |
| 4 | After 3 races, file contains 3 records in chronological order | MET | Smoke output: 3 records with ts `22:30:22 → 22:31:25 → 22:31:54`. |
| 5 | At least one turtle and one snake race | MET | Smoke covered turtles (races 1 and 3) and snakes (race 2). Snake race has a 3-entry finish_order; turtle races have 4-entry. |
| 6 | Existing `ask_play_again` messagebox unchanged | MET | `git diff main.py` shows only the wiring lines added; `dialogs.ask_play_again` is unchanged. |
| 7 | `pytest` remains green | MET | 135 passed (133 baseline + 2 new guard tests). |
| 8 | Path-traversal basename guard added to `paths.user_data_path` (auditor L1 deferred from Phase 1) | MET | `paths.py:11-23` adds the 4-condition guard; 2 new pytest assertions cover both `"../evil"` and embedded separators. `"leaderboard.json"` (the production caller) passes the guard, so Phase 1's 39 leaderboard tests still pass. |

## Test Suite
- Full `pytest -q` result: **135 passed**.
- Test growth: Phase 1 final 133 → Phase 2 final 135 (+2 basename guard tests).

## Integration Sanity
- `python main.py` runs unchanged end-to-end (smoke verified the wiring in the real GUI loop with monkeypatched dialogs).
- `record_race` writes to disk on every completed race; `%APPDATA%\TurtleRace\leaderboard.json` accumulates as expected.
- `paths.user_data_path` continues to accept bare filenames; rejects path traversal and separators with `ValueError`.
- No regressions in Phase 1's 133 tests.

## Gaps Identified
- None.

## Carryover to Phase 3
- Smoke script `tools/smoke_phase_2.py` will break if Phase 3 reorders `main()`'s round-loop calls (the `round_idx` advancement is coupled to `ask_play_again` being last). Phase 3 should not rely on the script — it will need its own no-GUI verification path if needed. Documented in REVIEW-1.1.md as the deferred Important finding.
- `import leaderboard` style in main.py remains the canonical form for production-side callers (per CONTEXT-1 + CONTEXT-2 carryover).
- Phase 3's planned restructure (main-menu-driven outer loop, three-button post-race prompt) will reshape the same `main()` block this phase modified. The current 2-line wiring will need to move into the new "race round" inner loop's body but stays in the same position relative to `run_race` and `show_podium`.
