# Phase 4 Verification (Post-Build)

## Overall status: complete

## Requirements coverage

| Success criterion (from ROADMAP / CONTEXT-4) | Status | Evidence |
| --- | --- | --- |
| `dialogs.show_leaderboard()` opens a single `Toplevel` with 4 `ttk.Combobox` filters + empty-state label + `ttk.Treeview` + 3 buttons | ✅ met | `dialogs.py:391` `def show_leaderboard()`; widget tree built in commit `663faac`, wired in `24b9345`, finalized in `79b082e` |
| All four comboboxes `state="readonly"`; defaults: Time="All Time", Species="All", Track="All Tracks", Group by="None" | ✅ met | Inspected `dialogs.py` filter-frame block; `set()` defaults present |
| `Group by = None` → 6-col Treeview populated via `leaderboard.query(time, species, track)` | ✅ met | `_repopulate` branch in `dialogs.py`; smoke Steps 1–2 + 4 verify rows shape |
| `Group by = Track` → 7-col Treeview populated via `leaderboard.query_per_track(time, species)` (Track combobox ignored) | ✅ met | `_repopulate` track branch; smoke Step 3 verifies `min(rank)==1` per track + all-3-tracks-present |
| Track combobox auto-disables when `Group by = Track`; re-enables on `None`; selected value preserved | ✅ met | `_on_group_by_change` toggles `state="disabled"`/`"readonly"` without clearing value |
| Filter changes immediately re-query and repopulate (single `delete()` + batch `insert`, flicker-free) | ✅ met | `_repopulate` clears once then inserts in a loop |
| Empty-state label `"No races recorded"` shown when result empty, hidden otherwise | ✅ met | `_repopulate` toggles `_empty_label.grid()`/`grid_remove()` |
| Reset Session: `messagebox.askyesno("Reset Session", "Clear current session stats?", default=NO, parent=dialog)` → `reset_session()` + refresh + repop | ✅ met | Exact copy verified in `dialogs.py` `_on_reset_session` |
| Reset All: `messagebox.askyesno("Reset All", "Delete all race history? This cannot be undone.", default=NO, parent=dialog)` → `reset_all()` + refresh + repop | ✅ met | Exact copy verified in `dialogs.py` `_on_reset_all` |
| Track combobox values refreshed from `leaderboard.known_tracks()` at window open AND after both resets | ✅ met | `_refresh_track_combo` invoked at init and from both reset handlers |
| Close button + WM_DELETE_WINDOW both dismiss the dialog | ✅ met | `dialog.destroy` wired for both |
| `show_leaderboard_placeholder` renamed → `show_leaderboard`; `main.py` call site updated atomically | ✅ met | Single commit `79b082e`; zero remaining `show_leaderboard_placeholder` references in `dialogs.py`/`main.py` |
| `leaderboard.py` UNCHANGED (Phase 1 read-only) | ✅ met | `git diff 4505aad HEAD -- leaderboard.py` empty |
| `tools/smoke_phase_4.py` exists, exercises all Phase 1 API contract surfaces, exits 0 | ✅ met | Smoke produced by commit `62e821d`; 7-step driver covers query / query_per_track / known_tracks / reset_session / reset_all |
| `tools/smoke_phase_3.py` UNCHANGED (Carryover) | ✅ met | `git diff 4505aad HEAD -- tools/smoke_phase_3.py` empty |
| No new third-party deps | ✅ met | `requirements.txt` unchanged; `ttk` is stdlib |
| `pytest -q` reports 135 passed at HEAD | ✅ met | See test/build results below |

## Test/build results
- **pytest -q** → `135 passed in 0.38s`. No regressions vs Phase 3 baseline (also 135). No new automated tests added (Phase 4 verification is via the no-GUI smoke per CONTEXT-4).
- **`python -c "import dialogs; import main"`** → exit 0. No import-time side effects.
- **`python tools/smoke_phase_4.py`** → exit 0. Prints `[smoke] leaderboard driver PASS` followed by `[smoke] PASS — 3 races recorded, all Phase 1 API contract surfaces verified (Group-by, Track-filter, reset_session, reset_all, known_tracks)`.
- **Smoke flake (informational, non-blocking):** one run mid-verification failed with `PermissionError: [WinError 5]` during `leaderboard.py`'s `os.replace(tmp, target)`. This is a known Windows file-replace race (antivirus / indexer interference, not a code defect) — it self-cleared on retry. Same intermittent failure mode exists for any code path that does atomic JSON writes via temp file + rename on Windows. Not specific to Phase 4 changes. If it recurs systematically, consider tracking in ISSUES.md as a Phase 5 hardening task (retry-with-backoff in `_write_json_atomically`).

## Phase status by plan
- **Plan 1.1** — PASS (REVIEW-1.1.md). 3 atomic commits.
- **Plan 2.1** — MINOR_ISSUES, no criticals (REVIEW-2.1.md). 1 commit. Findings are coverage enhancements, not blockers.

## Gaps identified
- None blocking. Two cosmetic findings carried over from REVIEW-2.1.md:
  - `_FILTER_LABEL_TO_KEY` value-level drift is unchecked (only key presence is asserted).
  - `_repopulate`'s `rows` initialization is `if/else`-bound (defensible but fragile to future refactor).

Both are minor and can be addressed at any time (or never) without affecting Phase 4's completeness.

## Infrastructure validation
- **Not applicable.** No Terraform, Ansible, Docker, Kubernetes, or other IaC files touched. `iac_validation: auto` in config.json detected zero relevant changes — skipped.

## Phase 3 regression check
- All Phase 3 invariants hold: menu-loop / round-loop two-level shape preserved in `main.py`; `dialogs.get_main_menu_choice` and `dialogs.ask_play_again_choice` unchanged; `audio.start_background_music`/`stop_background_music` lifecycle unchanged.
- `tools/smoke_phase_3.py` is broken-by-design after Plan 1.1's rename (it patches the no-longer-existing `dialogs.show_leaderboard_placeholder`). This is the documented Carryover state, exactly mirroring how `tools/smoke_phase_2.py` was left after Phase 3.

## Recommendations
- Proceed to security audit (Step 5a) and simplification review (Step 5b).
- Defer the two REVIEW-2.1 minor findings to Phase 5 unless the simplifier flags them as worth addressing immediately.
- Note in HISTORY.md / lesson capture: the smoke-write Windows race is a recurring annoyance — tracking it explicitly will save future debugging time.
