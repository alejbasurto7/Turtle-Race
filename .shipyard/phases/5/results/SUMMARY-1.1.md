# Build Summary: Plan 1.1

## Status: complete

## Tasks Completed
- Task 1: Update CLAUDE.md with leaderboard subsection and six-dialog correction — complete — commit `2a8dffa` — files: CLAUDE.md
- Task 2: Add runtime-generated comment to turtle_race.spec confirming leaderboard.json exclusion — complete — commit `20a9eb7` — files: turtle_race.spec

## Files Modified
- `CLAUDE.md` — +11 lines, −1 line.
  - **Edit A:** Replaced the stale "tkinter owns the three modal dialogs" bullet with an accurate six-dialog listing by name (`get_user_track`, `get_user_species`, `get_user_bet`, `ask_play_again_choice`, `get_main_menu_choice`, `show_leaderboard`). Also tightened the `WM_DELETE_WINDOW` description from "no-op to force a choice" to "redirected (no-op or routed to a Close handler)" — accurate for both legacy dialogs (no-op) and the Phase 4 leaderboard window (routes to Close).
  - **Edit B:** Appended a new `### Leaderboard (Phase 1 module, Phase 4 view)` subsection immediately after the closing paragraph of `### Round loop shape`. Covers all four CONTEXT-5 Decision 2 facts: (1) `leaderboard.py` is Tk-free and the smokes depend on this invariant, (2) on-disk store path at `%APPDATA%\TurtleRace\leaderboard.json` resolved via `paths.user_data_path()` (parallel to but distinct from `paths.resource_path()`) and NOT a `datas=` entry, (3) JSON schema with `schema_version: 1` plus atomic-write + corrupt-file-quarantine semantics, (4) `dialogs.show_leaderboard()` reaches data only via the public `leaderboard` API (`query`, `query_per_track`, `known_tracks`, `reset_session`, `reset_all`).
- `turtle_race.spec` — +3 lines, −0 lines. Two `#` comment lines plus one blank line prepended above the existing `block_cipher = None` start. Verbatim text:
  ```
  # Note: %APPDATA%/TurtleRace/leaderboard.json is generated at runtime by
  # leaderboard.py — it is NOT a bundled resource and does NOT belong in datas=.
  ```
  All functional content (Analysis(), datas=, hiddenimports=, PYZ(), EXE()) is byte-identical to pre-task state — verified by `git diff 762630a 20a9eb7 -- turtle_race.spec` showing exactly the 3-line addition.

## Decisions Made
- **Em-dash in the spec comment** (`—`, U+2014) was used per the plan's verbatim text. Python 3 `.spec` files default to UTF-8 source encoding so a non-ASCII character inside a `#` comment is valid. Verified with `ast.parse()` after the edit.
- **Tightened the `WM_DELETE_WINDOW` description** beyond the strict letter of the plan. The plan only required correcting the dialog count from three to six; the `WM_DELETE_WINDOW` bullet text was uniformly "no-op to force a choice," but `show_leaderboard` actually routes X to a real Close handler (not a no-op). Adjusting the description to "redirected (no-op or routed to a Close handler)" keeps the bullet accurate for ALL six dialogs simultaneously. Minor scope expansion but trivially low-risk and avoids leaving a different stale statement in the file.

## Issues Encountered
- **Builder Write tool refused to create the SUMMARY file directly.** Resolved by the planner creating `.shipyard/phases/5/results/` and writing the summary from the builder's structured report. Same friction pattern observed in Phase 4 (builder/reviewer agents sometimes exit before writing their output files); the planner has been compensating for this throughout the project.
- **`turtle_race.spec` had zero existing comments** before this change, so there was no prior comment style to mirror. Standard `#` Python comments were used per the plan's exact wording. No surprise — the spec was a 100% generated PyInstaller file pre-Phase-5.

## Verification Results
- `pytest -q` → **135 passed in 0.35s** at the tip of every commit (verified across both `2a8dffa` and `20a9eb7`).
- `python -c "import dialogs; import main; import leaderboard"` → exit 0 at the tip of every commit.
- `python -c "import ast; ast.parse(open('turtle_race.spec').read())"` → exit 0 after Task 2 commit (spec is still valid Python).
- `grep -nE "^### Leaderboard \(Phase 1 module" CLAUDE.md` → 1 hit.
- `grep -nE "three modal dialogs" CLAUDE.md` → 0 hits.
- `grep -cE "get_user_track|get_user_species|get_user_bet|ask_play_again_choice|get_main_menu_choice|show_leaderboard" CLAUDE.md` → ≥6 mentions (one per dialog name in the corrected bullet, plus pre-existing references elsewhere in CLAUDE.md).
- `grep -nE "^# Note: %APPDATA%/TurtleRace/leaderboard.json is generated at runtime" turtle_race.spec` → 1 hit at line 1.
- `grep -nE "datas=\[" turtle_race.spec` → 1 hit; content unchanged.

All Plan 1.1 acceptance criteria met. Wave 2 (Plan 2.1) is unblocked.
