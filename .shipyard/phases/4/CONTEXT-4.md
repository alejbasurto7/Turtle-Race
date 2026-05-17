# CONTEXT — Phase 4: Leaderboard View

User decisions captured during `/shipyard:plan 4` Discussion Capture (2026-05-17). Binding for all downstream agents. **Note:** Decision 1 deviates from earlier PROJECT.md / ROADMAP.md revisions that prescribed a Notebook + Per-Track tab layout. PROJECT.md and ROADMAP.md were updated in the same planning session to match the decision below.

## Decisions

### 1. Window layout — single view with "Group by" filter, no Notebook
**Decision:** A single `Toplevel` window. Four `ttk.Combobox` filters at the top (Time, Species, Track, Group by). One `ttk.Treeview` below. Three buttons at the bottom (Reset Session, Reset All, Close). No Notebook, no Per-Track tab.

**Rationale:** Simpler UI with fewer widgets and no tab-switching complexity. The "Group by: Track" filter reshapes the same Treeview into the per-track breakdown view, so both visualizations live in one widget. User explicitly chose this over the Notebook+tabs approach.

**Implications:**
- `dialogs.show_leaderboard()` (renamed from `show_leaderboard_placeholder`) is a single function — no separate "Overall tab" / "Per Track tab" helpers.
- Phase 1's `leaderboard.query(...)` and `leaderboard.query_per_track(...)` BOTH get called from this view, depending on `Group by`. Both functions are already in place from Phase 1; no leaderboard.py changes required.
- PROJECT.md and ROADMAP.md were updated in this planning session to remove the Notebook/Per-Track tab requirements and replace with the single-view + Group-by spec.

### 2. Track filter behavior when "Group by: Track" is selected
**Decision:** Track filter combobox is **automatically disabled** (`state="disabled"`, greyed out) when `Group by = Track`. Re-enabled (`state="readonly"`) when `Group by` returns to `None`. The Track filter's previously-selected value is **preserved** across the disable/enable toggle.

**Rationale:** Grouping by track already organizes results by every track present in the data, so the Track-name filter would be redundant (selecting a specific track would just collapse the grouped view to a single group). Disabling the filter visually communicates this rather than allowing nonsensical filter combinations.

**Implications:**
- A `_on_group_by_change()` callback toggles the Track combobox's `state` between `"readonly"` and `"disabled"`.
- Toggling does NOT clear the user's previously-selected Track value (so switching back to `Group by = None` restores their context).
- When `Group by = Track` is active, the `query_per_track(time, species)` call ignores the (disabled but still-set) Track filter value entirely.

### 3. Reset confirmation dialogs — native messagebox
**Decision:** `tkinter.messagebox.askyesno(...)` for both Reset Session and Reset All. Default focus on **No** (safer default). Exact copy:
- Reset Session: title `"Reset Session"`, body `"Clear current session stats?"`
- Reset All: title `"Reset All"`, body `"Delete all race history? This cannot be undone."`

**Rationale:** Native messagebox is faster to implement, smaller, and familiar to users (matches the bool-returning style the legacy `ask_play_again` once used). Custom Toplevel modals are unnecessary for a binary Yes/No confirmation.

**Implications:**
- Two short helper functions or inline calls; no new `dialogs.py` machinery for confirmation modals.
- The `default=tkinter.messagebox.NO` argument biases the dialog toward the safe choice.

### 4. Empty-state handling
**Decision:** When the filtered query returns zero rows, show an inline `tkinter.Label` reading `No races recorded` below the filter row (and above/beside the empty Treeview). Hide the label automatically when the next query returns ≥ 1 row.

**Rationale:** A bare empty Treeview is ambiguous (broken? loading? wrong filter?). The explicit label makes the empty state diagnosable on fresh installs and after Reset All.

**Implications:**
- A `tkinter.Label` widget is created up front and `.grid_remove()` / `.grid()` toggled by the query callback based on result length.
- The Treeview's empty state is just zero rows — no placeholder "loading" item.

## Open Questions Left for the Architect

- **Rename `show_leaderboard_placeholder` → `show_leaderboard`?** The Phase 3 placeholder used the explicit `_placeholder` suffix to signal Phase 4 would replace it. Now that Phase 4 ships the real view, the function should logically be `show_leaderboard()`. **Recommendation:** rename, and update the call site in `main.py:32` in the same atomic commit that adds the real body. The architect should specify whether this is a separate task or folded into the main implementation task.

- **Window size.** Reasonable default: ~520x420 px (enough for the 6-column Treeview + filter row + button row). `dialog.resizable(True, True)` so users can grow it for more rows. Architect specifies exact values.

- **Treeview row striping (alternating row colors).** Nice-to-have polish; defer to Phase 5 unless trivial to add now. Recommendation: skip in Phase 4 to keep the diff focused.

- **Sort by column header click.** Out of scope for Phase 4 (PROJECT.md doesn't require sortable headers; the default sort is the Phase 1 tiebreaker order). Don't add sort handlers.

- **Window-close (X) policy on the leaderboard window.** Phase 3's `show_leaderboard_placeholder` mapped X to Close. Phase 4 should preserve this — X = close window, return to menu. No surprises.

## Out-of-Scope Reminders (from PROJECT.md / ROADMAP.md)

- **No new leaderboard data fields.** Phase 1 already shipped the public `Row` and `PerTrackRow` dataclasses; Phase 4 just renders them.
- **No new `leaderboard.py` functions.** All needed APIs (`query`, `query_per_track`, `known_tracks`, `reset_session`, `reset_all`) exist from Phase 1.
- **No editing/undo of records, no per-racer drilldown, no CSV export, no charts.**
- **No changes to `main.py`** except the single call-site rename (if the architect chooses to rename the function — see Open Questions).
- **No new tests for the GUI itself.** The existing 135 pytest tests must stay green. End-to-end verification will use a no-GUI smoke script analogous to `tools/smoke_phase_3.py`.

## Carryover from Phase 3 (informational)

- `dialogs.show_leaderboard_placeholder()` exists with the "Coming in Phase 4" body. Phase 4 replaces this body with the real view.
- `main.py:32` calls `dialogs.show_leaderboard_placeholder()`. If the function is renamed in Phase 4, this call site must update atomically.
- The deferred `transient()` no-arg inconsistency in ISSUES.md still applies but is for Phase 5 polish.
- `tools/smoke_phase_2.py` is broken-by-design. `tools/smoke_phase_3.py` is the current canonical smoke — Phase 4 will likely write `tools/smoke_phase_4.py` (rule of three threshold met; the simplifier flagged the boilerplate extraction opportunity at this point).
