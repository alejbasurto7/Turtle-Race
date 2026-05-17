# Review: Plan 1.1

## Verdict: PASS

## Findings

### Critical
- None.

### Minor
- **Forward-reference style inside `show_leaderboard`.** `_on_reset_session` and `_on_reset_all` are defined before `_refresh_track_combo` and `_repopulate`, yet reference them in their bodies. This works correctly because Python resolves free variables in nested functions at call time (LEGB lookup), and all helpers are bound to the enclosing scope before any callback can fire (`wait_window()` is the last line). Functionally fine; style-wise the reverse order (define helpers first, then button handlers) would have read more naturally. Not worth a follow-up — leave as is.
- **`_repopulate` binds `rows` inside a 2-branch `if/else` and reads it after.** This is structurally fragile to refactoring (e.g., adding a third group-by value would risk `UnboundLocalError`), but currently safe because `dialog._group_combo` is `state="readonly"` with values `["None", "Track"]` only, and `_FILTER_LABEL_TO_KEY` maps both to defined keys. Defensible as-is; an explicit `rows = []` initializer would future-proof it. Not blocking.
- **Two `else:` branches contain shape-redundant heading/width/anchor dicts.** `_rebuild_columns` could share the six common-column entries between the "none" and "track" branches (only the leading `track` column differs), but the explicit-pair form is more readable than a dict-merge. Acceptable trade-off; AI bloat watch flag for the simplifier, not for the builder.

### Positive
- **All three tasks landed as separate atomic commits** with descriptive `shipyard(phase-4): ...` messages, exactly per Plan 1.1's task boundaries. The Task 3 commit `79b082e` correctly bundles the rename + main.py call-site update + reset-button wiring as a single atomic change — no broken intermediate state, matching the Phase 3 atomic-deletion precedent.
- **Hard CONTEXT-4 constraints are all honored:**
  - Decision 1 (single Toplevel, no Notebook, four ttk.Comboboxes, single Treeview): present.
  - Decision 2 (Track combobox disable when Group by = Track; value preserved): `_on_group_by_change` configures `state="disabled"|"readonly"` and never clears the value; `_refresh_track_combo` only resets to `"All Tracks"` if the current value is no longer in the refreshed track list.
  - Decision 3 (messagebox.askyesno with exact copy and `default=tkinter.messagebox.NO`): both call sites use the exact strings `"Clear current session stats?"` and `"Delete all race history? This cannot be undone."`, both with `default=tkinter.messagebox.NO` and `parent=dialog`.
  - Decision 4 (empty-state label): `dialog._empty_label` created up front, `.grid_remove()`-ed immediately, toggled by `_repopulate` based on `len(rows) == 0`.
- **`_FILTER_LABEL_TO_KEY` placement** correctly mirrors the existing module-level `_TURTLE_GRID_LAYOUT` / `_SNAKE_ROW_LAYOUT` constants pattern (single-underscore-prefixed, just below the existing layout constants).
- **Tk pitfalls avoided:**
  - `ttk.Scrollbar` correctly wired bidirectionally (`command=tree.yview` + `tree.configure(yscrollcommand=scrollbar.set)`).
  - Treeview lives in a `tree_frame` sub-Frame with its own row/column weights so the scrollbar can sit beside it without colliding with the dialog's `columnconfigure(0, weight=1)` weight propagation.
  - `dialog._tree.delete(*dialog._tree.get_children())` is called once before the batch insert — exactly the flicker-free pattern the plan called for.
- **`leaderboard.py` is unchanged** (`git diff 4505aad HEAD -- leaderboard.py` is empty), honoring the read-only constraint.
- **Verification clean:** `pytest -q` reports 135 passed at HEAD; `python -c "import dialogs; import main"` exits 0; all plan-specified `grep` invariants hold (single `^def show_leaderboard\b`, zero `show_leaderboard_placeholder` references anywhere, 5 leaderboard API call sites, two `askyesno` calls with `default=tkinter.messagebox.NO`).
- **Builder's SUMMARY-1.1.md "Decisions Made" section is rich** — the `tree_frame`/`filter_frame` sub-Frame rationale and the `configure(columns=...)` reset-to-defaults note are exactly the kind of non-obvious implementation detail that helps future readers.

Plan 1.1 is complete and clean. Proceed to Wave 2 (Plan 2.1 — smoke_phase_4).
