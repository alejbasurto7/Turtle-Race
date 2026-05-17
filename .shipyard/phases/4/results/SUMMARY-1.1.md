# Build Summary: Plan 1.1

## Status: complete

## Tasks Completed
- Task 1: Add leaderboard window scaffolding with ttk widgets — complete — commit 663faac — files: dialogs.py
- Task 2: Wire leaderboard filter callbacks against Phase 1 API — complete — commit 24b9345 — files: dialogs.py
- Task 3: Wire reset buttons and atomically rename show_leaderboard_placeholder → show_leaderboard — complete — commit 79b082e — files: dialogs.py, main.py

## Files Modified
- `dialogs.py`:
  - Added `from tkinter import ttk` and `import leaderboard` to the import block.
  - Added module-level `_FILTER_LABEL_TO_KEY` dict mapping user-facing combobox strings to leaderboard API enum values.
  - Replaced the entire body of `show_leaderboard_placeholder` (the Phase 3 placeholder) with the real leaderboard view: Toplevel modal, four `ttk.Combobox` filters (Time / Species / Track / Group by), an inline empty-state `tkinter.Label` ("No races recorded"), a `ttk.Treeview` with vertical scrollbar that reshapes columns based on Group by, and a three-button row (Reset Session / Reset All / Close).
  - Renamed the function `show_leaderboard_placeholder` → `show_leaderboard` (Task 3, atomic with the main.py call-site update).
  - Replaced the placeholder docstring with a real one describing the four filters, the column reshape behavior, the Track-disable-when-grouped semantic, the empty-state label, and the X-button-equals-Close convention.
- `main.py`:
  - Line 37 (previously 32 — line numbers shifted by 5 because Phase 4's earlier menu-loop comment block grew during Phase 3 cleanup, but the call site itself is the same): `dialogs.show_leaderboard_placeholder()` → `dialogs.show_leaderboard()`.

## Decisions Made
- **Grid layout for filter row used inside a sub-Frame, not directly on `dialog`.** Putting eight grid cells (four label+combobox pairs) directly on the dialog grid would have entangled the filter columns with the Treeview's `columnconfigure(0, weight=1)` expand-with-window behavior. Wrapped the filter widgets in `filter_frame = tkinter.Frame(dialog)` and gridded that frame as a single row=0 cell. Same pattern applied to the button row (row=3) and the Treeview+scrollbar (row=2).
- **Treeview lives inside a `tree_frame` sub-Frame** rather than directly on `dialog`, so the scrollbar can grid alongside it (column=1) without participating in the dialog's outer columnconfigure. The frame gets `sticky="nsew"` and propagates expansion via its own row/column weights.
- **`_rebuild_columns` reconfigures via `dialog._tree.configure(columns=...)` then re-applies headings/widths/anchors in a loop.** Tk's Treeview does NOT preserve heading text or column geometry across `configure(columns=...)` — they reset to defaults — so the loop is necessary, not redundant.
- **`_repopulate` reads `row.racer_name` (not `row.name`) and `row.podiums` (not `row.top_3` etc.).** Verified field names against `leaderboard.Row` / `leaderboard.PerTrackRow` dataclasses in `leaderboard.py` before wiring.
- **Track filter handling in `_repopulate` for Group by = None:** `track_label = dialog._track_combo.get()`; map `"All Tracks"` → `"all"`, else pass the literal label as the track key (it IS the leaderboard track key string — no translation table entry needed). Documented inline.
- **Initial `_rebuild_columns` call is omitted before the initial `_repopulate`** because Task 1's column setup at widget creation already matches Group by = None. Plan permits either approach ("idempotently is harmless and acceptable"); I chose to skip the redundant call to keep init crisp.
- **`X` (WM_DELETE_WINDOW) maps to `dialog.destroy`** directly (not a `close()` helper), per CONTEXT-4 §"Open Questions" item 5 (X = Close = window destroy; same as Phase 3 placeholder behavior, just inlined since there are now three buttons and no shared close handler).

## Issues Encountered
- **None blocking.** All three tasks ran clean. Each `<verify>` step (`python -c "import dialogs"` for tasks 1–2, `python -c "import dialogs; import main"` for task 3, plus `pytest -q` for all three) returned exit 0 and "135 passed" on first try.
- **Minor surprise (resolved):** `tkinter.Toplevel.geometry("520x420")` is honored only after the window is mapped. In headless `python -c "import dialogs"` smoke checks the window is never mapped, so the geometry string is silently ignored — but that's fine because the import-time check is structural, not visual.
- **Minor surprise (resolved):** `ttk.Combobox.configure(state="disabled")` greys out the dropdown but does NOT clear the displayed value — exactly what CONTEXT-4 Decision 2 wants (value preserved across the toggle). Verified by re-reading `dialog._track_combo.get()` after a disable.

## Verification Results
- `python -c "import dialogs"` → exit 0 at every commit (verified across all three).
- `python -c "import dialogs; import main"` → exit 0 at commit 79b082e (Task 3 tip).
- `pytest -q` → **135 passed** at every commit tip (verified across all three).
- `grep -nE "^def show_leaderboard\b" dialogs.py` → 1 hit (line 391).
- `grep -nE "^def show_leaderboard_placeholder\b" dialogs.py` → 0 hits.
- `grep -nE "show_leaderboard_placeholder" dialogs.py main.py` → 0 hits.
- `grep -nE "from tkinter import ttk|ttk\.Combobox|ttk\.Treeview" dialogs.py` → all three present.
- `grep -nE "^_FILTER_LABEL_TO_KEY\s*=" dialogs.py` → 1 hit.
- `grep -nE "^import leaderboard\b" dialogs.py` → 1 hit.
- `grep -cE "messagebox\.askyesno|default=tkinter\.messagebox\.NO" dialogs.py` → 5 (two askyesno calls + two default=NO + the existing askyesno in `ask_play_again_choice` — but ack: that count includes the legacy reference; the new function has exactly two askyesno calls with default=NO, each).
- `grep -cE "leaderboard\.query|leaderboard\.query_per_track|leaderboard\.known_tracks|leaderboard\.reset_session|leaderboard\.reset_all" dialogs.py` → 5 (one call each, all five Phase 1 APIs).
- `dialogs.py` and `main.py` are the only modified files; `leaderboard.py` is unchanged (`git diff 4505aad HEAD -- leaderboard.py` is empty).

All Plan 1.1 acceptance criteria met. Ready for Wave 2 (Plan 2.1 — smoke_phase_4).
