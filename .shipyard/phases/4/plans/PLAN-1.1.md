---
phase: leaderboard-view
plan: 1.1
wave: 1
dependencies: []
must_haves:
  - Replace dialogs.show_leaderboard_placeholder body with real Treeview-based leaderboard view (single Toplevel, no Notebook)
  - Four ttk.Combobox filters (Time / Species / Track / Group by), all state="readonly"
  - Track combobox toggles between "readonly" and "disabled" based on Group by value
  - Inline "No races recorded" label shown/hidden based on result emptiness
  - Group by reshape via _rebuild_columns(group_by) helper; flicker-free repop via delete + batch insert
  - _FILTER_LABEL_TO_KEY dict translates user-facing strings to leaderboard API enum values
  - Track combobox value list refreshed from leaderboard.known_tracks() at window open AND after both resets
  - Selected Track value preserved across the disable/enable toggle; falls back to "All Tracks" if no longer in the refreshed list
  - Reset Session / Reset All buttons gated by tkinter.messagebox.askyesno with default=tkinter.messagebox.NO and exact CONTEXT-4 copy
  - Atomic rename show_leaderboard_placeholder -> show_leaderboard with the main.py:32 call-site update in the same commit
  - No changes to leaderboard.py (Phase 1 APIs only)
  - No new third-party deps; ttk is stdlib
  - pytest stays green (135 passed)
files_touched:
  - dialogs.py
  - main.py
tdd: false
risk: medium
---

# PLAN 1.1 — Implement `dialogs.show_leaderboard()` (real Treeview view)

## Context

Phase 4 replaces the Phase 3 placeholder body in `dialogs.show_leaderboard_placeholder()` (currently at [dialogs.py:369](../../../../dialogs.py)) with the real leaderboard window described in `.shipyard/PROJECT.md` and `.shipyard/ROADMAP.md` Phase 4, per the binding decisions in [.shipyard/phases/4/CONTEXT-4.md](../CONTEXT-4.md).

Key shape (CONTEXT-4 Decision 1): a single `Toplevel` window with four `ttk.Combobox` filters (Time / Species / Track / Group by) above a single `ttk.Treeview` whose columns reshape based on Group by, an inline `tkinter.Label` that toggles on empty result, and three bottom buttons (Reset Session / Reset All / Close). All needed leaderboard APIs (`query`, `query_per_track`, `known_tracks`, `reset_session`, `reset_all`) already exist from Phase 1.

The function is also renamed `show_leaderboard_placeholder` -> `show_leaderboard` in this plan. The Phase 3 atomic-deletion pattern applies: the rename and the `main.py:32` call-site update happen in the same commit (Task 3) — no intermediate broken state.

## Dependencies

None. Phase 1 / 2 / 3 are complete. This plan touches `dialogs.py` and `main.py` only; `leaderboard.py` is read-only here.

## Tasks

<task id="1" files="dialogs.py" tdd="false">
  <action>
Replace the body of `dialogs.show_leaderboard_placeholder()` in `dialogs.py` with the **window scaffolding** (no data plumbing yet — filter callbacks are temporary no-op stubs). At the top of `dialogs.py` add `from tkinter import ttk` to the existing tkinter imports (keep `import tkinter.messagebox` already imported). Build the widget tree using `.grid()` layout:

- `dialog = tkinter.Toplevel()`; `dialog.title("Leaderboard")`; `dialog.resizable(True, True)`; window default size ~520x420 (use `dialog.geometry("520x420")`).
- **Filter row** (row=0) — a `tkinter.Frame` containing four labeled `ttk.Combobox` widgets, all `state="readonly"`:
  - Time: values `["All Time", "Current Session", "Today", "This Week", "This Month", "This Year"]`, default `"All Time"`.
  - Species: values `["All", "Turtles", "Snakes"]`, default `"All"`.
  - Track: values `["All Tracks"]` only for now (populated for real in Task 2); default `"All Tracks"`.
  - Group by: values `["None", "Track"]`, default `"None"`.
  - Each combobox stored on `dialog` as `dialog._time_combo`, `dialog._species_combo`, `dialog._track_combo`, `dialog._group_combo` so Task 2's callbacks can reach them.
- **Empty-state label** (row=1) — `dialog._empty_label = tkinter.Label(dialog, text="No races recorded")` created up front and immediately hidden via `dialog._empty_label.grid_remove()` (Tk remembers the grid coords, so re-`.grid()` later restores it without re-specifying row/col).
- **Treeview** (row=2) — `dialog._tree = ttk.Treeview(dialog, columns=("rank","racer","points","races","wins","podiums"), show="headings", height=12)` with explicit `heading()` and `column(..., width=N, anchor="center" or "w")` configured for the default Group by = None columns (Rank/Racer/Points/Races/Wins/Podiums). Use a vertical scrollbar (`ttk.Scrollbar` with `orient="vertical"`, `command=tree.yview`) on the right; set `tree.configure(yscrollcommand=scrollbar.set)`. The grid weights for row=2 and the tree's column must use `sticky="nsew"` and `dialog.rowconfigure(2, weight=1)` / `dialog.columnconfigure(0, weight=1)` so the tree expands with the window.
- **Button row** (row=3) — a `tkinter.Frame` containing three `tkinter.Button`s: **Reset Session**, **Reset All**, **Close**. Wire **Close** to `dialog.destroy`. Wire **Reset Session** and **Reset All** to two temporary stub functions (`def _on_reset_session(): pass`, `def _on_reset_all(): pass`) — Task 3 replaces these stubs with the real confirm+call logic.
- Bind the four comboboxes' `<<ComboboxSelected>>` event to a temporary no-op `def _on_filter_change(event=None): pass` and a separate no-op `def _on_group_by_change(event=None): _on_filter_change()` for the Group by combo. Task 2 fills these in.
- Modal lifecycle (mirror Phase 3 placeholder): `dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)`; `dialog.transient()`; `dialog.grab_set()`; `dialog.wait_window()`.

Do NOT yet rename the function — it must still be `show_leaderboard_placeholder` after this task. Do NOT yet call `leaderboard.query(...)` or `leaderboard.known_tracks()`. Do NOT yet add the messagebox confirmations. The result is a structurally complete but visually empty window that opens and closes correctly.
  </action>
  <verify>python -c "import dialogs" ; pytest -q</verify>
  <done>`python -c "import dialogs"` exits 0. `pytest -q` reports 135 passed (no regressions). `grep -nE "^def show_leaderboard_placeholder\b" dialogs.py` returns 1 hit. `grep -nE "_time_combo|_species_combo|_track_combo|_group_combo|_empty_label|_tree" dialogs.py` shows the new widget attributes. `grep -nE "from tkinter import ttk|ttk\.Combobox|ttk\.Treeview" dialogs.py` confirms ttk wired in. `grep -nE "show_leaderboard\b" main.py` still returns the existing `show_leaderboard_placeholder` call site at line 32 (NOT yet renamed).</done>
</task>

<task id="2" files="dialogs.py" tdd="false">
  <action>
Wire the filter callbacks against the real Phase 1 leaderboard API. All edits remain inside the renamed-in-Task-3 `show_leaderboard_placeholder` function body.

1. **Add a module-level `_FILTER_LABEL_TO_KEY` dict** near the top of `dialogs.py` (just below the existing `_SNAKE_ROW_LAYOUT`), mapping user-facing combobox strings to the enum values that `leaderboard.query` / `query_per_track` expect:

```python
_FILTER_LABEL_TO_KEY = {
    # Time window
    "All Time":        "all",
    "Current Session": "session",
    "Today":           "today",
    "This Week":       "week",
    "This Month":      "month",
    "This Year":       "year",
    # Species
    "All":             "all",
    "Turtles":         "turtles",
    "Snakes":          "snakes",
    # Group by
    "None":            "none",
    "Track":           "track",
}
```

The track-name combobox values are leaderboard track strings already (no translation needed) except for the sentinel `"All Tracks"` which maps to the `"all"` enum value used by `query(..., track_filter=...)`.

2. **Add `import leaderboard` to dialogs.py's local-imports block** (after `from paths import resource_path`).

3. **Replace the temporary no-op callbacks** with real implementations:

- `_refresh_track_combo()` — reads `leaderboard.known_tracks()`, sets `dialog._track_combo["values"] = ["All Tracks"] + known_tracks()`. Preserves the currently-selected value if still in the list; otherwise falls back to `"All Tracks"`. This helper is called once at window open AND from the reset callbacks (Task 3).
- `_rebuild_columns(group_by_key)` — reconfigures `dialog._tree` for the active column set. Branch on `group_by_key`:
  - `"none"`: columns `("rank","racer","points","races","wins","podiums")`; headings Rank/Racer/Points/Races/Wins/Podiums; widths (suggested) 50/120/70/70/70/70 with `anchor="center"` except Racer = `"w"`.
  - `"track"`: columns `("track","rank","racer","points","races","wins","podiums")`; headings Track/Rank/Racer/Points/Races/Wins/Podiums; widths (suggested) 110/50/110/70/70/70/70 with anchors per the same pattern (Track and Racer = `"w"`, others `"center"`).
  - Use `dialog._tree.configure(columns=cols)` then a loop that calls `heading(col, text=...)` and `column(col, width=..., anchor=...)` for each. The `show="headings"` mode is set at widget creation in Task 1 and need not change.
- `_repopulate()` — reads the current four combobox values, translates via `_FILTER_LABEL_TO_KEY`, calls `leaderboard.query(...)` OR `leaderboard.query_per_track(...)` based on group-by key, then:
  - Clears the tree with `dialog._tree.delete(*dialog._tree.get_children())` once before insertion (single delete, then batch insert — keeps flicker invisible).
  - For each row, calls `dialog._tree.insert("", "end", values=(...))` with the value tuple shaped to match the active columns.
  - Track-filter handling when `group_by_key == "none"`: read `track_label = dialog._track_combo.get()`; map `"All Tracks"` -> `"all"`, anything else -> the literal track-name string (it IS the leaderboard track key — no translation).
  - When `group_by_key == "track"`: call `query_per_track(time_key, species_key)` (ignore the disabled Track combo's value — CONTEXT-4 Decision 2).
  - Toggle the empty-state label: if `len(rows) == 0` then `dialog._empty_label.grid()` else `dialog._empty_label.grid_remove()`.
- `_on_filter_change(event=None)` — calls `_repopulate()`.
- `_on_group_by_change(event=None)` — does the following IN ORDER:
  1. Read new group_by_key from `dialog._group_combo.get()` via `_FILTER_LABEL_TO_KEY`.
  2. Toggle Track combobox state: `dialog._track_combo.configure(state="disabled" if group_by_key == "track" else "readonly")`. Do NOT clear the Track combobox's value.
  3. Call `_rebuild_columns(group_by_key)`.
  4. Call `_repopulate()`.

4. **Call `_refresh_track_combo()` and `_repopulate()` ONCE before `dialog.wait_window()`** so the initial state is populated. The initial group_by_key is `"none"` so the default-column setup from Task 1 already matches; no initial `_rebuild_columns` call is needed (but calling it idempotently is harmless and acceptable).

Do NOT touch the reset buttons yet — they remain stubbed `pass` from Task 1. Do NOT yet rename the function.
  </action>
  <verify>python -c "import dialogs" ; pytest -q</verify>
  <done>`python -c "import dialogs"` exits 0. `pytest -q` reports 135 passed. `grep -nE "^_FILTER_LABEL_TO_KEY\s*=" dialogs.py` returns 1 hit. `grep -nE "^import leaderboard\b" dialogs.py` returns 1 hit. `grep -cE "_refresh_track_combo|_rebuild_columns|_repopulate|_on_filter_change|_on_group_by_change" dialogs.py` returns >=5 (one definition each). `grep -nE "leaderboard\.query|leaderboard\.query_per_track|leaderboard\.known_tracks" dialogs.py` shows all three Phase 1 query APIs are invoked from within the function body. `grep -nE 'state="disabled"|state="readonly"' dialogs.py` confirms the Track combobox toggle pattern is present.</done>
</task>

<task id="3" files="dialogs.py, main.py" tdd="false">
  <action>
Atomically (single commit) do BOTH of the following:

**A. Wire the reset buttons inside `dialogs.show_leaderboard_placeholder`:**

Replace the two `pass` stubs from Task 1 with:

- `_on_reset_session()`:
  ```python
  if tkinter.messagebox.askyesno(
      "Reset Session",
      "Clear current session stats?",
      default=tkinter.messagebox.NO,
      parent=dialog,
  ):
      leaderboard.reset_session()
      _refresh_track_combo()
      _repopulate()
  ```
- `_on_reset_all()`:
  ```python
  if tkinter.messagebox.askyesno(
      "Reset All",
      "Delete all race history? This cannot be undone.",
      default=tkinter.messagebox.NO,
      parent=dialog,
  ):
      leaderboard.reset_all()
      _refresh_track_combo()
      _repopulate()
  ```

Wire these to the existing Task 1 Reset Session / Reset All buttons by replacing the temporary stub callbacks with these named functions (the buttons' `command=` argument).

**B. Rename `show_leaderboard_placeholder` -> `show_leaderboard` and update the single call site in `main.py` IN THE SAME COMMIT (no intermediate broken state, per CONTEXT-3 / Phase 3 atomic-deletion precedent):**

- In `dialogs.py`: rename `def show_leaderboard_placeholder() -> None:` to `def show_leaderboard() -> None:`. Update the docstring to drop the "placeholder" phrasing and describe the real behavior (single-view Toplevel with four filters, Treeview, three buttons, reset confirmations via messagebox).
- In `main.py`: change line 32 (currently `dialogs.show_leaderboard_placeholder()`) to `dialogs.show_leaderboard()`.

Verify no other file references `show_leaderboard_placeholder` before committing (`tools/smoke_phase_3.py` does — but it is "broken by design" per Plan 2.1 Phase 3 SUMMARY and remains untouched here; the new Phase 4 smoke in Plan 2.1 will call the renamed function).
  </action>
  <verify>python -c "import dialogs; import main" ; pytest -q</verify>
  <done>`python -c "import dialogs; import main"` exits 0. `pytest -q` reports 135 passed. `grep -nE "^def show_leaderboard\b" dialogs.py` returns 1 hit; `grep -nE "^def show_leaderboard_placeholder\b" dialogs.py` returns 0 hits. `grep -nE "dialogs\.show_leaderboard\b" main.py` returns 1 hit at line 32 (or wherever the call site landed — exact line allowed to shift if intermediate edits moved it); `grep -nE "dialogs\.show_leaderboard_placeholder\b" main.py` returns 0 hits. `grep -nE "messagebox\.askyesno" dialogs.py` shows at least two askyesno calls with the exact CONTEXT-4 copy ("Clear current session stats?" and "Delete all race history? This cannot be undone."). `grep -nE "default=tkinter\.messagebox\.NO" dialogs.py` returns 2 hits.</done>
</task>

## Acceptance Criteria

- `dialogs.show_leaderboard()` exists (renamed from `show_leaderboard_placeholder`) and opens a Toplevel with the four-filter + Treeview + empty-state-label + three-button layout described in CONTEXT-4 Decision 1.
- Track combobox auto-disables when Group by = Track and re-enables (with preserved value) when Group by = None.
- Filter changes immediately re-query and repopulate; the empty-state label toggles correctly.
- Reset Session and Reset All both gate behind `messagebox.askyesno` with `default=tkinter.messagebox.NO` and the exact CONTEXT-4 copy.
- The Track combobox value list is refreshed from `leaderboard.known_tracks()` at window open AND after both resets.
- `main.py:32` calls `dialogs.show_leaderboard()` (renamed in the same commit as the rename — no broken intermediate state).
- `leaderboard.py` is unchanged.
- `pytest -q` reports 135 passed at the tip of every commit in this plan.
- `python -c "import dialogs; import main"` exits 0 at the tip of every commit.

## Verification

After all three tasks:

```powershell
python -c "import dialogs; import main"      # exits 0
pytest -q                                    # 135 passed
grep -nE "^def show_leaderboard\b" dialogs.py                # 1 hit
grep -nE "show_leaderboard_placeholder" dialogs.py main.py    # 0 hits
grep -nE "messagebox\.askyesno" dialogs.py                   # >= 2 hits
grep -nE "leaderboard\.query|leaderboard\.query_per_track|leaderboard\.known_tracks|leaderboard\.reset_session|leaderboard\.reset_all" dialogs.py   # >= 5 hits
```

Live GUI verification (running `python main.py` and opening the leaderboard) is **not** part of the builder's verification — the no-GUI smoke in Plan 2.1 (Wave 2) covers the end-to-end behavior programmatically.
