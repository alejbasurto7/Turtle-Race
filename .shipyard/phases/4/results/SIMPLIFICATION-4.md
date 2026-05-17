# Simplification Review — Phase 4

## Verdict: minor_findings

## Findings

### High priority (fix now or plan for Phase 5)
- None.

### Medium (consider)
- **Smoke-script duplication has crossed the rule-of-three boundary.** `tools/smoke_phase_2.py` (broken-by-design), `tools/smoke_phase_3.py`, and now `tools/smoke_phase_4.py` all share the same ~30-line preamble: tempdir creation, `os.environ["APPDATA"]` redirect BEFORE imports, `dialogs.*` + `audio.*` + `tkinter.messagebox` monkeypatch surface, `[smoke] ...` log prefix, iterator-pattern for canned `dialogs.get_*` answers, and the post-`main()` JSON re-inspection. Phase 4's simplifier note in PROJECT.md flagged this back in Phase 3 ("rule of three threshold met"). Two reasonable shapes for Phase 5:
  - **Helper module `tools/_smoke_common.py`** exposing `setup_tmp_appdata()`, `patch_dialogs(menu_iter, post_race_iter, rounds, leaderboard_override=None)`, `patch_audio()`, `read_final_json()`. Each phase smoke shrinks to ~50 lines of phase-specific assertions.
  - **Keep the duplication.** Three smoke scripts is not yet painful enough to justify the indirection, and CLAUDE.md's "three similar lines is better than a premature abstraction" rule applies. Smokes ARE supposed to read like standalone scripts — flattening makes failures easy to localize.
  - **Recommendation:** Defer the decision to Phase 5. If Phase 5 adds a fourth smoke (e.g., `smoke_phase_5.py` for whatever Phase 5 introduces), extract then. If Phase 5 doesn't add one, the rule-of-three pressure stays at exactly three and the duplication is tolerable.

### Low / aesthetic
- **The two reset handlers (`_on_reset_session`, `_on_reset_all`) share structure but differ in three concrete ways:** title string, body string, and which `leaderboard.reset_*()` they call. A factored helper would look like:
  ```python
  def _confirm_and_reset(title, body, reset_fn):
      if tkinter.messagebox.askyesno(title, body, default=tkinter.messagebox.NO, parent=dialog):
          reset_fn()
          _refresh_track_combo()
          _repopulate()
  ```
  This collapses 16 lines into ~6 lines + 2 wrappers. However, CLAUDE.md explicitly says "three similar lines is better than a premature abstraction" — two callers is below the threshold. Current form is more readable for someone scanning the dialog body to find what "Reset All" does. **Leave as is.**
- **`_rebuild_columns` parallel dicts (lines ~545–567).** Two branches build three dicts each (`headings`, `widths`, `anchors`) and then iterate `for col in cols`. The "none" branch and the "track" branch share six column definitions; only the leading "track" column differs. Possible refactor: define a base column-spec list at module scope, then prepend the `track` spec for the track branch. This would save ~20 lines but obscure the per-mode column geometry that's currently grep-friendly. **Leave as is** — the explicit form documents the design and matches existing `dialogs.py` style (the bet-grid layouts `_TURTLE_GRID_LAYOUT` and `_SNAKE_ROW_LAYOUT` are also exhaustively positional rather than abstracted).
- **`_FILTER_LABEL_TO_KEY` collisions on `"all"`** as the enum value for both Time and Species filters is harmless because each filter calls into a different `leaderboard.query()` parameter slot — there's no actual ambiguity. A split into three smaller dicts (`_TIME_LABEL_TO_KEY`, `_SPECIES_LABEL_TO_KEY`, `_GROUP_BY_LABEL_TO_KEY`) would be slightly cleaner but adds three names where one suffices. **Leave as is.**
- **`_on_filter_change` is a single-line wrapper around `_repopulate`.** It exists to give the `<<ComboboxSelected>>` binding a callable that accepts the event arg. Could inline as `lambda event=None: _repopulate()` at the bind site. Cosmetic; current form is more grep-friendly than a lambda. **Leave as is.**

## Positive observations
- **The Plan 1.1 builder resisted abstraction-for-its-own-sake.** With four similar callbacks (filter-change, group-by-change, reset-session, reset-all) it would have been easy to invent a generic dispatch table. Builder kept them as named functions inside the dialog body. Matches CLAUDE.md style.
- **No dead code introduced.** The renamed function has no remaining `_placeholder` traces; `main.py:32` (now `main.py:37`) is the only call site and was updated atomically. No unreferenced imports.
- **No defensive try/except blocks around impossible failures.** The builder used assertion-by-shape (e.g., `_FILTER_LABEL_TO_KEY[combo.get()]` will KeyError loudly if the combo somehow holds an unexpected value) rather than `try: ... except KeyError: fallback`. This matches CLAUDE.md "Don't add error handling, fallbacks, or validation for scenarios that can't happen."
- **No verbose internal-only error messages.** The smoke uses concise `[smoke] FAIL — <reason>` strings; the dialog code uses no error strings at all.
- **`_FILTER_LABEL_TO_KEY` lives at module scope** rather than nested inside `show_leaderboard`. This makes it introspectable by `tools/smoke_phase_4.py` for regression detection — a small structural choice that pays off in test coverage.
- **Treeview column reshape via `configure(columns=...)` + re-application loop in `_rebuild_columns`** is the minimal correct pattern. Tk's `configure(columns=...)` resets heading text and column geometry to defaults; the loop re-applies them. No premature abstraction (e.g., a column-spec dataclass).

## Recommendations
- **Now:** None blocking. Ship Phase 4 as-is.
- **Phase 5:** Re-evaluate the smoke-script duplication if a fourth smoke is needed. If not, accept the duplication permanently.
- **Phase 5:** If the documenter's recommendation to add a one-liner WHY-comment on the `_rebuild_columns` `configure(columns=...)` call is acted on, that's a 1-line edit — cheaper than refactoring.
- **Never (or only on direct user request):** Inline the reset-button helpers into a `_confirm_and_reset` shared function. The two-caller threshold doesn't justify it and the named handlers grep more obviously than a generic helper.
