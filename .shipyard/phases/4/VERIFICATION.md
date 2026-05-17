# Plan Verification — Phase 4

## Verdict: PASS

## Coverage of Phase 4 success criteria (from ROADMAP.md, post-CONTEXT-4 revision)

| Criterion | Plan/Task | Status |
|---|---|---|
| `dialogs.show_leaderboard()` opens Toplevel with 4 combos + Treeview + empty-state label + 3 buttons | PLAN-1.1 Task 1 (scaffolding) + Task 2 (wiring) + Task 3 (resets + rename) | covered |
| All 4 combos `state="readonly"`; values match spec; defaults `All Time` / `All` / `All Tracks` / `None` | PLAN-1.1 Task 1 | covered |
| `Group by = None` → Rank/Racer/Points/Races/Wins/Podiums columns; rows from `leaderboard.query(...)` | PLAN-1.1 Task 2 (`_rebuild_columns("none")` + `_repopulate` calling `query`) | covered |
| `Group by = Track` → Track/Rank-in-track/Racer/... columns; rows from `query_per_track(...)` | PLAN-1.1 Task 2 (`_rebuild_columns("track")` + `_repopulate` calling `query_per_track`) | covered |
| Track combobox auto-disables when `Group by = Track`; re-enables on `None`; selected value preserved | PLAN-1.1 Task 2 `_on_group_by_change` — toggles `state="disabled"`/`state="readonly"`, does NOT clear Track value | covered |
| Filter changes immediately re-query + repopulate without flicker | PLAN-1.1 Task 2 `_on_filter_change` → `_repopulate` (`delete(*get_children())` + batch `insert`) | covered |
| Empty-state label `"No races recorded"` shown when result empty, hidden otherwise | PLAN-1.1 Task 1 (label scaffolding) + Task 2 (`grid()` / `grid_remove()` toggle) | covered |
| Reset Session: `messagebox.askyesno("Reset Session", "Clear current session stats?", default=NO)` + `reset_session()` + `_refresh_track_combo` + re-query | PLAN-1.1 Task 3 | covered (exact copy) |
| Reset All: `messagebox.askyesno("Reset All", "Delete all race history? This cannot be undone.", default=NO)` + `reset_all()` + reset Track combo to `["All Tracks"]` + re-query | PLAN-1.1 Task 3 | covered |
| Close button dismisses; WM_DELETE → Close | PLAN-1.1 Task 1 (`dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)`) | covered |
| Track combobox values refreshed from `known_tracks()` at window open AND after each reset | PLAN-1.1 Task 2 (`_refresh_track_combo` called at open) + Task 3 (called from both reset handlers) | covered |
| Current Session filter shows only races since latest start (Phase 1 invariant); restart preserves historic | inherited from Phase 1 `query("session", ...)` reading `_SESSION_RACES`; Phase 4 just calls the API | covered |
| `pytest` stays green (135) | both plans require it at every commit boundary | covered |
| Phase 1–3 success criteria still hold | no changes to `leaderboard.py`, `race.py`, `audio.py`, `paths.py`, `constants.py`, `tracks.py` | covered |

## Structural Checks

| Check | Result |
|---|---|
| Task count per plan | PLAN-1.1: 3, PLAN-2.1: 1 — both ≤ 3 |
| Wave / dependency ordering | 1.1 (no deps) → 2.1 (deps on 1.1) — strictly sequential |
| Same-file parallel conflicts | None. PLAN-1.1 touches `dialogs.py` + `main.py`. PLAN-2.1 creates `tools/smoke_phase_4.py` (new file). Disjoint surface. |
| Acceptance-criteria testability | Objective: grep counts, function rename verification, pytest count, smoke exit code |
| Verification commands | Concrete: `python -c "import dialogs; import main"`, `pytest -q`, grep checks, `python tools/smoke_phase_4.py` |

## CONTEXT-4 Decision Coverage

| Decision | Implementation | Verdict |
|---|---|---|
| 1. Single-view layout, no Notebook | PLAN-1.1 Task 1 creates ONE Toplevel with grid-laid widgets; no `ttk.Notebook` reference anywhere | covered |
| 2. Track filter disabled when Group by = Track | PLAN-1.1 Task 2 `_on_group_by_change` step 2 toggles `state`; value preserved | covered |
| 3. Reset confirmations via `messagebox.askyesno` with `default=NO` and exact copy | PLAN-1.1 Task 3 quotes both messages verbatim | covered |
| 4. Empty-state label `"No races recorded"` | PLAN-1.1 Task 1 (scaffolding) + Task 2 (toggle in `_repopulate`) | covered |

## Scope Creep

None. The plans:
- DO NOT touch `leaderboard.py` (Phase 1 module unchanged — all queries through public API).
- DO NOT add sortable column headers (out of scope per CONTEXT-4 Open Questions).
- DO NOT add row striping or other polish (deferred to Phase 5).
- DO NOT add new third-party deps (`ttk` is stdlib).
- DO NOT add new automated GUI tests (verification via smoke).
- DO NOT touch `tools/smoke_phase_2.py` or `tools/smoke_phase_3.py` (both broken-by-design after their respective phases; CONTEXT-4 carryover note).

---

# Plan Critique — Feasibility Stress Test

## Verdict: READY

## Per-plan feasibility

### PLAN-1.1 — `dialogs.show_leaderboard()` implementation

- **File paths:** `dialogs.py` exists (~430 lines after Phase 3). `main.py` exists. Both are real.
- **API surface:** All `leaderboard.py` symbols referenced exist after Phase 1:
  - `leaderboard.query(time_window, species_filter="all", track_filter="all", *, now=None)` ✓
  - `leaderboard.query_per_track(time_window, species_filter="all", *, now=None)` ✓
  - `leaderboard.known_tracks()` ✓
  - `leaderboard.reset_session()` ✓
  - `leaderboard.reset_all()` ✓
- **`ttk` import:** `from tkinter import ttk` is stdlib in Python 3.10+. No risk.
- **Function rename atomicity:** Task 3 explicitly does the rename + main.py:32 update in the SAME commit. Same pattern as Phase 3's `ask_play_again` deletion. Correct sequencing prevents intermediate broken state.
- **Existing Phase 3 placeholder body** at `dialogs.py:369` is fully replaced by Task 1 (scaffolding) — the "Coming in Phase 4" Toplevel is wiped, and Task 1 ends with a structurally complete window. Tasks 2 and 3 build on Task 1's widget tree.
- **`_FILTER_LABEL_TO_KEY` at module scope:** allows the Phase 4 smoke (Plan 2.1) to introspect it without instantiating the GUI. Small visibility cost; meaningful regression-detection win.

### PLAN-2.1 — `tools/smoke_phase_4.py`

- **File path:** new file, no conflict.
- **Approach:** the architect's chosen strategy of replacing `dialogs.show_leaderboard` in the smoke with a Phase-1-API driver (rather than trying to programmatically click a live Toplevel) is the right call. The Plan 3 smoke established this pattern (canned-iterators + monkeypatched dialogs); Plan 4 extends it to additionally verify the leaderboard-view contract by calling `query`/`query_per_track`/`known_tracks`/`reset_session`/`reset_all` in the user-equivalent sequence and asserting observable behavior.
- **Smoke runs the actual `main()`** through the menu loop (3 rounds → leaderboard → quit), which exercises Phase 2's `record_race` wiring + Phase 3's menu loop end-to-end. The `fake_show_leaderboard` driver is invoked by the same `dialogs.show_leaderboard` callsite at `main.py:32` (renamed by Plan 1.1).

## Cross-plan findings

- **No forward references** beyond the declared dependency.
- **No same-wave file conflicts** (only one plan per wave).
- **`tools/smoke_phase_3.py` will break further** after Plan 1.1's rename (it monkeypatches `dialogs.show_leaderboard_placeholder`). PLAN-2.1 leaves it untouched — broken-by-design per CONTEXT-4 carryover, matching the Phase 2 → Phase 3 pattern.

## Risk register

- **`ttk.Treeview` column reshape on `Group by` change.** Reconfiguring `columns`, `heading`, `column` while the widget already has rows can leave stale state. PLAN-1.1 Task 2's `_rebuild_columns` is called BEFORE `_repopulate`, so the column set is reconfigured on an empty tree (the `_repopulate` call earlier in `_on_group_by_change` does the `delete(*get_children())` first — actually re-read: `_on_group_by_change` calls `_rebuild_columns` THEN `_repopulate`. The `_repopulate` clears children. So the column reconfigure happens BEFORE `delete()`. This works because `tree.configure(columns=...)` doesn't depend on row content — but worth verifying during build that no visual artifact remains).
- **`messagebox.askyesno`'s `parent=dialog` argument.** Some old Tk builds ignore the parent and center on the screen instead of the dialog. Modern Python (3.10+) on Windows respects it. PLAN-1.1 Task 3 includes `parent=dialog` correctly.
- **Track combobox state toggle while open.** `combobox.configure(state="disabled")` works but the widget may briefly show a stale rendering. Tk usually repaints immediately; if not, a manual `dialog.update_idletasks()` would force it. Non-blocking; spot-check during build.
- **`_FILTER_LABEL_TO_KEY` collisions.** The dict reuses `"all"` as the enum value for Time, Species, AND Track filters. Each filter calls into different leaderboard parameters (`time_window`, `species_filter`, `track_filter`) so the same string can legitimately mean different things in different parameter slots — there's no actual collision. The plan's dict structure is correct.

## Complexity flags

- 2 files modified (`dialogs.py`, `main.py`) + 1 new file (`tools/smoke_phase_4.py`). Well under thresholds.
- `dialogs.py` grows by ~150-200 lines (the `show_leaderboard` function body replacement). Below the 10-file / 3-dir thresholds.
- `dialogs.py` total length after Phase 4 will be roughly ~580 lines — still manageable in one file. No need to split.

## Headline

Plans are feasible and ready to build. The architect made three good design calls: (1) atomic rename of `show_leaderboard_placeholder` → `show_leaderboard` together with the `main.py:32` call-site update, (2) `_FILTER_LABEL_TO_KEY` at module scope so the smoke can introspect it, (3) splitting the smoke into Wave 2 so its dependency on the renamed function is explicit. Proceed with `/shipyard:build 4`.
