# Build Summary: Plan 1.1 (Phase 3)

## Status: complete

## Tasks Completed
- **Task 1:** add `dialogs.get_main_menu_choice()` — complete — files: `dialogs.py` (commit `de38596`, +36 lines).
- **Task 2:** add `dialogs.ask_play_again_choice()` — complete — files: `dialogs.py` (commit `514093e`, +42 lines).
- **Task 3:** add `dialogs.show_leaderboard_placeholder()` — complete — files: `dialogs.py` (commit `2c18f10`, +33 lines).

## Files Modified
- **`dialogs.py`** (+~111 lines across 3 commits): three new public functions appended/inserted:
  - `get_main_menu_choice() -> str` at [dialogs.py:31](dialogs.py#L31) — Toplevel modal, three stacked buttons (Race / View Leaderboard / Quit), Race gets focus, X-button returns `"quit"`.
  - `ask_play_again_choice() -> str` at [dialogs.py:327](dialogs.py#L327) — Toplevel modal, three buttons (Play Again / Main Menu / Quit), Play Again gets focus, X-button returns `"menu"`.
  - `show_leaderboard_placeholder() -> None` at [dialogs.py:369](dialogs.py#L369) — real Toplevel with body text "Leaderboard view coming in Phase 4" and a single Close button, X-button equivalent to Close.
- Old `ask_play_again()` at [dialogs.py:402](dialogs.py#L402) **left untouched** (deletion is Plan 2.1's atomic concern).

## Decisions Made
- **Function placement.** `get_main_menu_choice` placed early in the module (line 31) — before the existing `get_user_bet` — because it's logically the new entry point. The two post-race functions (`ask_play_again_choice` and `show_leaderboard_placeholder`) grouped immediately above the legacy `ask_play_again` so that Plan 2.1's deletion is atomic and visually obvious (the old function sits right next to its replacement).
- All three new dialogs use `dialog.title("Turtle Race")` to match the existing dialog convention.
- No `PhotoImage` references — text buttons only per CONTEXT-3 Decision 1.

## Issues Encountered
- None material. The existing modal pattern (`selected = [None]; def make_cb(value); transient + grab_set + wait_window`) was clean to mirror across all three functions.

## Verification Results
- `pytest -q` after each commit: **135 passed** (unchanged from baseline; no regressions).
- `python -c "import dialogs"` exits 0 after each commit.
- `grep -nE "^def (get_main_menu_choice|ask_play_again_choice|show_leaderboard_placeholder|ask_play_again)\b" dialogs.py` returns 4 hits — the 3 new functions plus the legacy `ask_play_again` (still present, awaiting Plan 2.1 deletion).
- Three atomic commits, one per task, all prefixed `shipyard(phase-3): add dialogs.*`.
