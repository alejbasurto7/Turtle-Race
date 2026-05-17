# Phase 3 Verification

## Overall Status: COMPLETE

## Coverage of Phase 3 Success Criteria (from ROADMAP.md)

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | `dialogs.get_main_menu_choice()` returns `"race" \| "leaderboard" \| "quit"`; Toplevel + grab_set + wait_window pattern; drawn over lawn background | MET | `dialogs.py:31` (Plan 1.1 commit `de38596`); WM_DELETE_WINDOW → `"quit"` per CONTEXT-3 Decision 3 |
| 2 | `dialogs.ask_play_again_choice()` returns `"again" \| "menu" \| "quit"`; replaces old `ask_play_again` callsite | MET | `dialogs.py:327` (Plan 1.1 commit `514093e`); `main.py:56` call site (Plan 2.1 commit `ba4e24b`); old `ask_play_again` deleted in same atomic commit |
| 3 | `main()` reshaped into two-level structure (outer menu, inner race rounds) | MET | `main.py:21-65` per RESEARCH-3 §1 target shape verbatim |
| 4 | Choosing **View Leaderboard** opens placeholder Toplevel ("Coming in Phase 4"); returns to menu | MET | `dialogs.show_leaderboard_placeholder` at `dialogs.py:369` (Plan 1.1 commit `2c18f10`); `main.py:28` call site; smoke verifies the menu→leaderboard→menu transition with a placeholder-call counter (must be exactly 1) |
| 5 | Tk `Screen()` and `pygame.mixer` initialized once at app start, torn down once at exit | MET | `main.py:15-17` (init prologue), `main.py:67-68` (cleanup epilogue) — both fire once per app lifetime; no recreation between menu/race transitions |
| 6 | `screen.clear()` + `set_background()` called at top of each race round, not on menu entry | MET | `main.py:33-34` (top of inner loop); outer menu loop body does NOT call clear+background; `set_background()` called once at `main.py:19` before first menu open |
| 7 | `pytest` remains green | MET | **135 passed** before and after Phase 3 |
| 8 | All race-loop invariants from CLAUDE.md preserved | MET | No changes to `race.py`, `audio.py`, `constants.py`, `tracks.py`, `paths.py`, `leaderboard.py`; `record_race` call site stays between `run_race` and `show_podium` (Phase 2 invariant); MIDI shuffle untouched |

## Test Suite
- Full `pytest -q` result: **135 passed**.
- Test growth this phase: **0 new tests** (Phase 3 is mostly Tk/GUI code; verification is via the no-GUI smoke + the existing 135-test suite covering Phase 1/2 surface).

## Smoke Verification (Plan 2.1 Task 2 substitute)

`tools/smoke_phase_3.py` executed cleanly on 2026-05-17 (run 1 at ~08:00; re-run at ~08:08 after REVIEW-2.1 caught and fixed the unreachable-leaderboard-branch bug). Output confirms:
- 3 races recorded (1 turtle/straight, 1 snake/spiral, 1 turtle/rectangular).
- 1 leaderboard placeholder call (the menu→leaderboard→menu branch is genuinely exercised, not just superficially printed).
- Chronological timestamps.
- Per-race species/track/finish_order length all match planned values.
- Each on-screen podium output (from `race.run_race`) matches the recorded `finish_order` exactly.
- `audio.stop_background_music()` and `screen.bye()` both run on Quit (clean exit).

## Integration Sanity
- `python main.py` runs end-to-end (verified via smoke).
- New control flow: menu-driven outer loop + race-rounds inner loop. Quit propagates cleanly through both loops.
- `tools/smoke_phase_2.py` is broken-by-design (monkeypatches the deleted `dialogs.ask_play_again`). Documented in CONTEXT-3 Carryover and Plan 2.1; not a regression.
- The 3-key control flow primitives (`get_main_menu_choice` for outer, `ask_play_again_choice` for post-race, `show_leaderboard_placeholder` for the leaderboard branch) are all called from `main.py`. Grep confirms one call site each.

## Gaps Identified
- None.

## Findings in ISSUES.md from this phase (non-blocking)
1. **`dialog.transient()` inconsistency** — new Phase 3 dialogs call `transient()` with no argument (no-op); legacy dialogs (`get_user_bet`, `get_user_track`, `get_user_species`) don't call it at all. Either remove from the new dialogs (uniformity), backfill into the legacy ones, or pass a real parent (best UX). Deferred to Phase 5 polish.
2. **`show_leaderboard_placeholder` lacks a comment about the missing sentinel pattern** — the other dialogs use `selected = [None]; make_cb(value)`; the placeholder uses a plain `def close(): dialog.destroy()` since there's no value to capture. A one-line comment would clarify intent for the Phase 4 maintainer replacing the body. Deferred.

## Carryover to Phase 4

- `show_leaderboard_placeholder` function name is locked. Phase 4 replaces the function BODY in-place with the real Treeview/filter/reset implementation. The function signature stays `() -> None`. The call site in `main.py:28` does not need to change.
- `dialogs.ask_play_again_choice` is the canonical post-race prompt. Phase 4 doesn't touch it.
- `tools/smoke_phase_3.py` may be adapted by Phase 4 to verify the leaderboard view rendering (or Phase 4 can write its own smoke).
- `tools/smoke_phase_2.py` continues to be broken; Phase 4 may either delete it or leave it as a historical reference (no impact either way).
- The `running` / `in_round_loop` two-loop control structure in `main.py` is stable; Phase 4 doesn't restructure further. Phase 4 only modifies `dialogs.py` (the placeholder body) and adds the leaderboard view + its tests.

## Lessons Captured for Ship-Time

1. **Atomic deletion of dead helpers.** Plan 2.1's pattern of folding the `dialogs.ask_play_again` deletion into the same commit as the `main.py` restructure prevented any intermediate broken state. Worth re-applying when retiring future helpers.
2. **Smoke scripts can lie if iterators are mis-ordered.** REVIEW-2.1 caught a real bug: the smoke claimed to exercise the leaderboard branch but the canned `menu_choices` ordering made that branch unreachable. Mitigation pattern: add a per-branch invocation counter on each monkeypatched function and assert the counter post-flow.
3. **`first_run` flags become noise in two-loop structures.** Replacing them with always-clear-at-top-of-iteration (relying on idempotency of `screen.clear()` on a clean canvas) simplifies the code.
