# Phase 5 Verification (Post-Build)

## Overall status: complete

## Requirements coverage

| Success criterion (from ROADMAP) | Status | Evidence |
| --- | --- | --- |
| `CLAUDE.md` gains a short addendum (10–20 lines) covering the main-menu entry point, `%APPDATA%\TurtleRace\leaderboard.json` data path, `leaderboard.py` Tk-free invariant, and the schema_version field | ✅ met | `2a8dffa` adds `### Leaderboard (Phase 1 module, Phase 4 view)` after `### Round loop shape` — 11-line section covering all four facts. The Tk-free invariant is explicit ("Do not add `import tkinter` to `leaderboard.py`"). |
| `turtle_race.spec` reviewed; no new `datas=` entries; confirmation in spec comment or commit message | ✅ met | `20a9eb7` prepends 2 `#` comment lines confirming `leaderboard.json` runtime-generated semantic. `datas=` and all functional spec content byte-identical (`git diff 762630a 20a9eb7 -- turtle_race.spec` shows only the 3-line additive change). |
| README — skipped per CONTEXT-5 Decision 1 (no README.md exists; not creating one this phase) | ✅ met (skipped) | No `README.md` in repo root before or after Phase 5. ROADMAP explicitly allows "if no README, this bullet is skipped without ceremony." |
| Build `dist/TurtleRace.exe` via `pyinstaller turtle_race.spec`; race once; quit; confirm leaderboard.json contains the race; re-launch and verify All-Time view shows it | ⚠️ deferred to manual gate | Per CONTEXT-5 Decision 4, the packaged-exe smoke is split. Source-mode invariants (path resolution + file lifecycle) are covered by automated `tools/smoke_phase_5.py` (exits 0 with PASS banner). The actual frozen-exe behaviors are documented in `tools/smoke_packaged.md` as a human-run checklist required before any ship. **Not blocking this phase's completion** — it's the explicit pre-ship gate. |
| Smoke-test all reset paths from the packaged exe: Reset Session leaves file present and unchanged; Reset All wipes to `{schema_version: 1, races: []}` | ⚠️ deferred to manual gate (source-mode invariant proven) | `tools/smoke_phase_5.py` Step 4 verifies `reset_session()` byte-equality; Step 5 verifies `reset_all()` produces exact `{"schema_version": 1, "races": []}` shape. Frozen-exe equivalent is steps 8 & 9 of `tools/smoke_packaged.md`. |
| All previous-phase success criteria still hold | ✅ met | `pytest -q` reports 135 passed at HEAD. `python -c "import dialogs; import main; import leaderboard"` exits 0. `python tools/smoke_phase_4.py` continues to exit 0 with its PASS banner. No production code modified this phase. |
| `pytest` remains green | ✅ met | 135 passed in 0.34s at HEAD `298fce8`. |

## Test/build results
- **pytest -q** → `135 passed in 0.34s`. Identical to Phase 4's final state — no test changes, no regressions.
- **`python -c "import dialogs; import main; import leaderboard"`** → exit 0.
- **`python tools/smoke_phase_5.py`** → exit 0. Final line: `[smoke] phase 5 smoke PASS — path resolution + file lifecycle verified`.
- **`python tools/smoke_phase_4.py`** → exit 0 (Phase 4's smoke still green; not regressed by Phase 5).
- **`python -c "import ast; ast.parse(open('turtle_race.spec').read())"`** → exit 0 (spec is still valid Python after the comment prepend).

## Phase status by plan
- **Plan 1.1** — PASS (REVIEW-1.1.md). 2 atomic commits (`2a8dffa`, `20a9eb7`). One minor flagged (forward reference to `smoke_phase_5.py` in the addendum) was self-resolving once Wave 2 landed.
- **Plan 2.1** — PASS (REVIEW-2.1.md). 1 atomic commit (`298fce8`). Three cosmetic minors (em-dash terminal rendering, eager-parent-dir-creation nuance, checklist could spell out prerequisite ordering) — none blocking.

## Gaps identified
- **None blocking.** The "deferred to manual gate" items in the table above are NOT gaps — they are the explicit Phase 5 design from CONTEXT-5 Decision 4. The automated smoke proves the source-mode invariants; the manual checklist is the documented gate before any actual release.

## Infrastructure validation
- **Not applicable.** No Terraform, Ansible, Docker, Kubernetes, or CloudFormation files were touched. `turtle_race.spec` is PyInstaller config and was modified ONLY to add comments (no `datas=` or other functional change). `iac_validation: auto` in config detected zero relevant changes — skipped.

## Cross-phase regression check
- All Phase 1–4 invariants hold. `leaderboard.py` is unchanged this phase (read-only access via the public API was already established in Phase 4). `dialogs.show_leaderboard()` is unchanged. The CLAUDE.md addendum DOCUMENTS rather than CHANGES the existing behavior.
- `tools/smoke_phase_3.py` and `tools/smoke_phase_4.py` are unchanged this phase. The new `tools/smoke_phase_5.py` is scope-limited to path resolution + file lifecycle (NOT the menu/UI contract that smoke_phase_4 covers).

## Recommendations
- **Before any actual release:** run `tools/smoke_packaged.md` against a fresh `pyinstaller turtle_race.spec` build. The frozen-exe `_MEIPASS` risk on `paths.user_data_path` is the one regression vector that this manual gate is specifically designed to catch.
- **Optional polish (Phase 6 or post-ship):** replace the em-dash in the smoke's PASS banner with `--` for cross-terminal cleanliness. Cosmetic only; not worth its own commit.
- **All gates clear.** Phase 5 is the final ROADMAP phase. `/shipyard:ship` is the next step.
