# Review: Phase 3 Plan 1.1

## Verdict: MINOR_ISSUES (approved)

(Authored by the shipyard:reviewer agent; the agent persisted the Important + Suggestion findings to `.shipyard/ISSUES.md` but did not separately write REVIEW-1.1.md. Captured here by the orchestrator from the agent's structured output.)

## Findings

### Critical
- None.

### Important (logged to ISSUES.md; non-blocking)
- **`transient()` called with no argument in the 3 new functions but absent from the 3 legacy functions.** `dialogs.py:60, 362, 397` call `dialog.transient()` with no argument in the new dialogs; the legacy `get_user_bet`, `get_user_track`, `get_user_species` don't call `transient()` at all. The no-arg form is a no-op (needs a parent reference to have effect), so there's no behavior difference — but it's a within-file inconsistency. Options for cleanup: (a) remove the no-op calls from the new functions; (b) backfill into the legacy functions; (c) pass a real parent (most correct UX-wise — dialogs would minimize/restore with the parent). Deferred to Phase 5 polish.

### Minor / Suggestions
- **`show_leaderboard_placeholder` does not use the `selected = [None]` sentinel pattern.** Correct as written (the function returns `None`, no capture needed), but a Phase 4 maintainer replacing the body may wonder why the pattern is absent. A one-line comment near the `def close():` would clarify the intent. Deferred.

### Positive
- All three functions match the existing modal pattern (Toplevel + grab_set + wait_window + transient).
- `WM_DELETE_WINDOW` policies are correct per CONTEXT-3: menu → `"quit"`, post-race → `"menu"`, placeholder → equivalent to Close.
- Text buttons only — no `PhotoImage` machinery introduced (matches CONTEXT-3 Decision 1).
- `dialog.title("Turtle Race")` set consistently across all three.
- Race button gets `focus_set()` in the menu; Play Again button gets `focus_set()` in the post-race prompt.
- Legacy `dialogs.ask_play_again()` (the bool-returning helper) is **untouched** — Plan 2.1's responsibility to delete.
- Placeholder body text exactly matches "Leaderboard view coming in Phase 4" (Phase 4 will replace the function body in-place).
- `pytest` stays at 135 passed; `python -c "import dialogs"` exits 0; no regression to any of the 4 existing top-level functions in `dialogs.py`.

## Verification Results
- `pytest -q`: **135 passed** (no regression).
- `python -c "import dialogs"`: exits 0.
- `grep -nE "^def (get_main_menu_choice|ask_play_again_choice|show_leaderboard_placeholder|ask_play_again)\b" dialogs.py`: 4 hits (3 new + 1 legacy).
- `WM_DELETE_WINDOW` per dialog: confirmed correct per CONTEXT-3.
- Existing functions unchanged: confirmed via diff inspection on the three commits (`de38596`, `514093e`, `2c18f10`) — each commit adds one new function and modifies nothing else.
