# Review: Plan 1.1

## Verdict: PASS

## Findings

### Critical
- None.

### Minor
- **Forward reference to `tools/smoke_phase_5.py` in the CLAUDE.md addendum.** The new `### Leaderboard (Phase 1 module, Phase 4 view)` subsection lists `tools/smoke_phase_5.py` alongside the two existing smokes as evidence of the Tk-free invariant. That file does not exist yet at the tip of commit `20a9eb7` — it lands in Wave 2 (Plan 2.1). This creates a one-commit window where the docs reference a file that hasn't been created. Two reasonable views:
  - **Tolerable:** the gap closes within the same phase (next commit in Wave 2), and the addendum reads correctly once Phase 5 is complete. Documentation is allowed to anticipate the same-phase artifact landing.
  - **Strict:** the build is supposed to leave the codebase in a runnable state at every commit. `python tools/smoke_phase_5.py` at tip `20a9eb7` fails with `FileNotFoundError`, so the doc claim is temporarily false.
  - **Verdict on this point:** Tolerable — the file claim is a referential note (it doesn't break import or test), and Phase 5 is the polish-and-ship phase where the docs SHOULD describe the end-state. The next plan in the same phase closes the gap. Not worth a CRITICAL or a retry.
- **Slight scope expansion in Task 1.** The plan explicitly required correcting the dialog count from three to six. The builder also tightened the `WM_DELETE_WINDOW` description from "no-op to force a choice" to "redirected (no-op or routed to a Close handler) so the user must pick a button." The expansion is technically correct (Phase 4's `show_leaderboard` routes WM_DELETE to `dialog.destroy`, which is a Close handler, not a no-op). The builder documented this in SUMMARY-1.1.md under "Decisions Made," and the rationale (leaving a different stale statement in the file would be worse) is sound. Non-blocking. If the project enforces strict-plan-faithfulness, log a note for next time. Otherwise accept.

### Positive
- **CLAUDE.md addendum lands at exactly the right place** — immediately after the existing `### Round loop shape` subsection, under `## Architecture`. Style and tone match the surrounding sections: terse imperative, `[file.py](path)` markdown links to source files, no fluff.
- **All four CONTEXT-5 Decision 2 facts are present and accurate:**
  - **Tk-free invariant:** Explicitly stated, with the smoke scripts called out as dependents. "Do not add `import tkinter` (or any Tk-touching helper) to `leaderboard.py`." — load-bearing instruction for future maintainers.
  - **`%APPDATA%` data path:** Covers Windows AND POSIX fallbacks (a small but accurate expansion — `paths.user_data_path` actually handles multiple OSes). Explicit warning that it never returns under `_MEIPASS`.
  - **`schema_version` field:** Names the module constant `leaderboard.SCHEMA_VERSION` and mentions the atomic-write + corrupt-file-quarantine semantics.
  - **API direction:** "`dialogs.py` imports `leaderboard`, never the reverse." — explicit dependency-direction note that justifies the Tk-free invariant.
- **The stale "three modal dialogs" bullet was corrected by name**, not just by count. All six dialogs (`get_user_track`, `get_user_species`, `get_user_bet`, `ask_play_again_choice`, `get_main_menu_choice`, `show_leaderboard`) are listed, grep-friendly. Future readers can ctrl-F any dialog name and find it here.
- **`turtle_race.spec` change is exactly 3 lines** — two `#` comments plus one blank line. Diff is byte-clean: no whitespace creep, no `datas=` modification, no Analysis()/PYZ()/EXE() touch. `ast.parse(open('turtle_race.spec').read())` continues to exit 0 (the spec is still valid Python).
- **Em-dash in the spec comment** (`—`) handled correctly. Python 3 source files default to UTF-8, so the non-ASCII character is harmless and the builder explicitly verified with `ast.parse()`.
- **No regressions:** `pytest -q` reports 135 passed at both commit tips. `python -c "import dialogs; import main; import leaderboard"` exits 0.
- **Two atomic commits** with descriptive `shipyard(phase-5): ...` messages — matches the per-task git strategy from prior phases.

Plan 1.1 is complete and clean. Proceed to Wave 2 (Plan 2.1 — `tools/smoke_phase_5.py` + `tools/smoke_packaged.md`). When Wave 2 commits land, the one outstanding minor (forward reference to `tools/smoke_phase_5.py` in the CLAUDE.md addendum) is automatically resolved.
