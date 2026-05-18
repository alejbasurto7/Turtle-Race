# Milestone Report: Turtle Race Leaderboard

**Completed:** 2026-05-17
**Phases:** 5 / 5 complete (Phases 1–5 all marked COMPLETE in ROADMAP.md and STATE.json)
**Total commits in scope:** 32 (`eb006fb..HEAD`, from `shipyard: capture project definition` through `shipyard: complete phase 5 build`)

## Phase Summaries

### Phase 1 — Persistence + Scoring Core (HIGH risk)
Stood up `leaderboard.py` as a Tk-free module owning the JSON schema, `record_race` / `query` / `query_per_track` / `known_tracks` / `reset_session` / `reset_all`, plus `paths.user_data_path()` parallel to `paths.resource_path()`. Comprehensive test suite at `tests/test_leaderboard.py` and `tests/test_paths.py`. Verified: 105 → 135 pytest tests pass at phase end; `import leaderboard` succeeds in a headless Python with no `DISPLAY` or Tk root.

### Phase 2 — Wire Recording into the Round Loop (LOW risk)
Added `leaderboard.record_race(species, track, finish_order_names)` call to `main.py` immediately after `race.run_race(...)` returns. Added basename guard to `paths.user_data_path()` per documenter feedback. Created `tools/smoke_phase_2.py` no-GUI smoke for end-to-end record verification (now broken-by-design after Phase 3's `ask_play_again` rename — preserved as historical artifact).

### Phase 3 — Main Menu and Post-Race Prompt Restructure (MEDIUM risk)
Restructured `main.py` from a single round-loop into a two-level menu+rounds loop. Added three new dialogs: `get_main_menu_choice` (Race / View Leaderboard / Quit), `ask_play_again_choice` (Play Again / Main Menu / Quit), and `show_leaderboard_placeholder` (Phase 4 stub). Deleted dead `ask_play_again`. Created `tools/smoke_phase_3.py` covering the new menu lifecycle (becomes broken-by-design after Phase 4's rename — preserved as historical artifact, matching the Phase 2 → 3 pattern).

### Phase 4 — Leaderboard View (MEDIUM risk)
Implemented `dialogs.show_leaderboard()` (renamed from `_placeholder` atomically with the `main.py` call-site update). Single Toplevel modal with four `ttk.Combobox` filters (Time, Species, Track, Group by), one `ttk.Treeview` reshaping columns by Group by, an inline empty-state label, and three bottom buttons (Reset Session / Reset All / Close). Reset operations gated by `tkinter.messagebox.askyesno` with `default=NO` and exact CONTEXT-4 copy. Track filter auto-disables when Group by = Track. Created `tools/smoke_phase_4.py` covering the menu+leaderboard contract end-to-end without opening a real Toplevel.

### Phase 5 — Polish and Ship (LOW risk)
Added `### Leaderboard (Phase 1 module, Phase 4 view)` subsection to CLAUDE.md (11 lines documenting the Tk-free invariant, `%APPDATA%` data path, `schema_version: 1` field, and the `dialogs → leaderboard` import direction). Corrected the stale "three modal dialogs" bullet to six dialogs by name. Prepended a 2-line `#` comment to `turtle_race.spec` confirming `leaderboard.json` is runtime-generated and NOT a `datas=` entry. Created `tools/smoke_phase_5.py` (automated source-mode smoke for path resolution + file lifecycle) and `tools/smoke_packaged.md` (13-checkbox human-runnable checklist for the frozen exe).

## Key Decisions

### Design
- **Single-view leaderboard window, not Notebook+tabs** (CONTEXT-4 Decision 1). Group-by filter reshapes the same Treeview rather than switching between tabbed views. Decided in Phase 4 planning over the earlier ROADMAP-proposed tabbed shape.
- **Atomic rename + call-site update pattern** (Phase 3 precedent, Phase 4 reuse). Function renames and their single call-site update land in the same commit — no intermediate broken state. Applied to both `ask_play_again` deletion and `show_leaderboard_placeholder` → `show_leaderboard` rename.
- **Smoke scripts are broken-by-design after subsequent phases.** Each phase ships its own `smoke_phase_N.py`; the prior phase's smoke remains in the repo as a historical artifact but is not maintained. By Phase 5 this is the rule-of-four — `tools/_smoke_common.py` extraction was deliberately deferred per CONTEXT-5 Decision 6.
- **Split packaged-exe smoke** (CONTEXT-5 Decision 4). Source-mode invariants (path resolution + file lifecycle) covered by automated `smoke_phase_5.py`; frozen-exe invariants covered by manual `smoke_packaged.md` checklist. Avoids the over-investment of fully automated frozen-exe smoke for a hobby-project budget.

### Architecture
- **`leaderboard.py` is Tk-free by invariant.** Load-bearing for all no-GUI smokes; documented in CLAUDE.md's new addendum with the explicit instruction "Do not add `import tkinter` to `leaderboard.py`."
- **`dialogs.py` imports `leaderboard`, never the reverse.** Direction documented in CLAUDE.md.
- **`paths.user_data_path()` writes to `%APPDATA%\TurtleRace\` on Windows (POSIX fallbacks elsewhere) and never returns a path inside `sys._MEIPASS`.** The `_MEIPASS`-regression risk is the one real ship blocker, caught explicitly by the manual `smoke_packaged.md` checklist.
- **`turtle_race.spec` `datas=` list is unchanged this milestone.** The `leaderboard.json` file is runtime-generated, not a bundled resource. Confirmed by comment in the spec.

## Documentation Status

- **API documentation:** Public surface of `leaderboard.py` (record/query/reset functions, `Row` and `PerTrackRow` dataclasses, `SCHEMA_VERSION` constant) is documented via docstrings. No separate `docs/api/` tree.
- **Architecture documentation:** `CLAUDE.md` is comprehensive. New `### Leaderboard (Phase 1 module, Phase 4 view)` subsection (Phase 5) covers the four load-bearing invariants. Existing sections on resource loading, racer identity, shape dispatch, track geometry, Tk image references, and round loop shape are all current and accurate.
- **User guides:** None. This is a single-developer hobby game; CLAUDE.md serves as the developer-facing guide. No `docs/guides/` tree.
- **README updated:** N/A. No README.md exists in the repo and none was created (CONTEXT-5 Decision 1).

## Known Issues

- **`_FILTER_LABEL_TO_KEY` value-level drift is unchecked in `tools/smoke_phase_4.py`** (REVIEW-2.1 minor finding for Phase 4). Only key-presence is asserted; mapped values are not spot-checked. Coverage enhancement, not a defect.
- **`_repopulate`'s `rows` variable is `if/else`-bound in `dialogs.show_leaderboard`** (REVIEW-2.1 minor finding for Phase 4). Defensible today (combobox is `state="readonly"` with only two values), but fragile to future refactoring. Initializing `rows = []` would future-proof it.
- **`tools/_smoke_common.py` extraction is deferred** (CONTEXT-5 Decision 6, SIMPLIFICATION-5 medium finding). Rule-of-three threshold tipped into rule-of-four with `smoke_phase_5.py`. Should be revisited in any post-ship maintenance pass.
- **Smoke scripts intermittently raise a Tk shutdown traceback** on Windows after the PASS banner (during interpreter teardown of the Tk canvas). Exit code is still 0; cosmetic, pre-existing artifact.
- **Em-dash in `[smoke] phase 5 smoke PASS — ...` banner** renders garbled on default Windows PowerShell code page. Cosmetic.

## Metrics
- **Files created (production):** `leaderboard.py`, `paths.user_data_path` (added to existing `paths.py`).
- **Files created (tests):** `tests/test_leaderboard.py`, `tests/test_paths.py`.
- **Files created (tools):** `tools/smoke_phase_2.py`, `tools/smoke_phase_3.py`, `tools/smoke_phase_4.py`, `tools/smoke_phase_5.py`, `tools/smoke_packaged.md`.
- **Files modified (production):** `main.py` (round loop restructure + `record_race` wiring + call-site rename), `dialogs.py` (3 new dialogs + leaderboard window).
- **Files modified (docs/build):** `CLAUDE.md` (Phase 5 addendum + six-dialog correction), `turtle_race.spec` (2-line comment), `.shipyard/ROADMAP.md`, `.shipyard/PROJECT.md`, `.shipyard/STATE.json`, `.shipyard/HISTORY.md`.
- **Test count:** baseline ~100 → final **135 passed** (delta from leaderboard + paths test files in Phase 1).
- **Total commits in shipping scope:** 32, of which 25 are `shipyard(phase-N): ...` per-task atomic commits and 7 are `shipyard: plan phase N` or `shipyard: complete phase N build` artifact commits.

## Pre-Ship Gates
- **All five phase VERIFICATION.md files show `complete` status.**
- **AUDIT-1 through AUDIT-5:** all PASS verdict. Cumulative: no critical security findings across the entire milestone. The project has zero network surface, zero credentials, zero deserialization of untrusted data; all changes are local desktop Tk game scope.
- **DOCUMENTATION-1 through DOCUMENTATION-5:** all `adequate` verdict. No critical doc gaps.
- **SIMPLIFICATION-1 through SIMPLIFICATION-5:** all `clean` or `minor_findings` verdict. Single deferred item is the `tools/_smoke_common.py` extraction.
- **pytest -q:** 135 passed (clean).
- **`python tools/smoke_phase_4.py`:** exit 0 with PASS banner.
- **`python tools/smoke_phase_5.py`:** exit 0 with PASS banner.
- **Manual `tools/smoke_packaged.md` against a fresh `pyinstaller turtle_race.spec` build is the documented gate before any actual release** — not run as part of `/shipyard:ship` (per CONTEXT-5 Decision 4).
