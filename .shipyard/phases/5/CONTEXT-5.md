# CONTEXT — Phase 5: Polish and Ship

Architectural decisions captured for `/shipyard:plan 5` (2026-05-17). The user invoked the build in no-clarifying-questions mode, so these decisions were made by the planner agent based on the ROADMAP, the existing codebase state, and the precedents set by Phases 1–4. Binding for all downstream agents.

## Decisions

### 1. README is out of scope (no file exists)
**Decision:** `README.md` does not exist in the project root. Per ROADMAP §"Phase 5 success criteria" bullet 3: "If no README, this bullet is skipped without ceremony." We will NOT create one in this phase.

**Rationale:** The project is a single-developer hobby game. CLAUDE.md serves as the developer-facing documentation. A user-facing README would be additive scope beyond what the ROADMAP requires, and creating documentation files without explicit user request conflicts with the default behavior in CLAUDE.md.

**Implications:**
- No `README.md` task in Phase 5.
- The CLAUDE.md addendum (success criterion 1) is the only documentation work this phase.

### 2. CLAUDE.md addendum — shape and placement
**Decision:** A new section is added to `CLAUDE.md` titled `### Leaderboard (Phase 1 module, Phase 4 view)`. It lives under the existing `## Architecture` heading, after the `### Round loop shape` section. The section is 10–20 lines and covers:
- The `leaderboard.py` module is Tk-free; `import leaderboard` succeeds without a display. This is a load-bearing invariant for the no-GUI smoke scripts.
- The on-disk store is `%APPDATA%\TurtleRace\leaderboard.json` (Windows) or `~/.turtle_race/leaderboard.json` (POSIX), resolved via `paths.user_data_path()` (parallel to `paths.resource_path()` but writable-user-data, NOT bundled-resource). The JSON file is generated at runtime — it is NOT a PyInstaller `datas=` entry in [turtle_race.spec](../../../../turtle_race.spec).
- The JSON schema includes a `schema_version: 1` field. Future migrations will dispatch on this field. There is no migrator today.
- `dialogs.show_leaderboard()` reaches the data via the public `leaderboard` API (`query`, `query_per_track`, `known_tracks`, `reset_session`, `reset_all`) — no direct file I/O from the dialog.
- The existing "tkinter owns three modal dialogs" bullet in CLAUDE.md is stale (Phase 3 added the menu + post-race choice dialogs; Phase 4 added the leaderboard window — that's 6 dialogs now). The addendum corrects this in passing.

**Rationale:** A short addendum is the right size — CLAUDE.md is already comprehensive and adding a full new top-level section would unbalance it. Updating the stale "three dialogs" line is a CLAUDE.md-hygiene tax that's been carried forward since Phase 3 and is cheap to pay now.

**Implications:**
- Plan 1.1 modifies `CLAUDE.md` only.
- No code changes in Plan 1.1.

### 3. `turtle_race.spec` review — explicit no-change confirmation
**Decision:** The spec is read and verified that NO new `datas=` entry is required for `leaderboard.json` (which is a runtime-generated user-data file, not a bundled resource). The confirmation is recorded as a comment in the spec file itself OR in the Plan 1.1 commit message — Plan 1.1's task description picks one.

**Rationale:** The ROADMAP success criterion explicitly calls for this confirmation. Inlining it in the spec keeps the rationale grep-findable in the long term; the commit message alone risks the rationale being lost to git-archaeology.

**Recommendation for the architect:** Put a 2-line comment block at the top of `turtle_race.spec` reading something like:
```
# Note: %APPDATA%/TurtleRace/leaderboard.json is generated at runtime by
# leaderboard.py — it is NOT a bundled resource and does NOT belong in datas=.
```

**Implications:**
- Plan 1.1 also touches `turtle_race.spec` (a 2-line comment add). It does NOT change any `datas=` list or any other Analysis() / EXE() argument.

### 4. Packaged-exe smoke test — semi-automated checklist + automated source-mode equivalent
**Decision:** Phase 5's packaged-exe smoke is split into TWO artifacts:

- **`tools/smoke_phase_5.py`** — runs the source-mode equivalent of the packaged-exe smoke described in the ROADMAP. Exit code 0 on success. Verifies the same end-to-end flow (`paths.user_data_path` lands at `%APPDATA%\TurtleRace\` on Windows when `APPDATA` is set; `leaderboard.json` is written on race; `reset_session` leaves the file present; `reset_all` wipes to `{schema_version: 1, races: []}`). This is NOT a re-run of `smoke_phase_4.py` — it specifically targets path resolution and the file lifecycle, not the leaderboard UI contract.

- **`tools/smoke_packaged.md`** — a human-runnable checklist for the actual packaged exe. Lists the exact steps: `pyinstaller turtle_race.spec` → run `dist/TurtleRace.exe` → race once → quit → grep `%APPDATA%\TurtleRace\leaderboard.json` for the race entry → re-launch → confirm All-Time view shows the race → Reset Session (confirm file present, schema_version unchanged) → Reset All (confirm file wiped to `{schema_version: 1, races: []}`). Each step has a PASS/FAIL line for the human to fill in. The commit message for Plan 2.1 references this checklist.

**Rationale:** A fully automated packaged-exe smoke would require headless GUI driving in a frozen executable — that's higher complexity than Phase 5's LOW-risk budget allows. Splitting the smoke into "automated for the source-mode invariants" + "manual checklist for the packaged-exe invariants" keeps the automated CI surface clean while ensuring the `_MEIPASS` regression risk (the one real risk per ROADMAP risk notes) is caught by an explicit human checklist run before any release.

**Implications:**
- Plan 2.1 creates BOTH `tools/smoke_phase_5.py` AND `tools/smoke_packaged.md`. They are independent files but logically coupled (the checklist references the automated smoke as a prerequisite step).
- Plan 2.1 does NOT actually run `pyinstaller turtle_race.spec` as part of the build pipeline — the architect's instructions to the builder make the manual step explicit and require the builder to either run it (if practical in the build environment) or document that it was deferred to a human-run final step before ship.
- The `tools/smoke_packaged.md` checklist is committed to the repo (NOT under `.shipyard/`) so future shipping cycles can rerun it.

### 5. Wave structure — two waves, one plan per wave
**Decision:**
- **Wave 1:** Plan 1.1 — Docs (`CLAUDE.md` addendum + `turtle_race.spec` comment).
- **Wave 2:** Plan 2.1 — Packaged-exe smoke (automated `tools/smoke_phase_5.py` + manual `tools/smoke_packaged.md` checklist).

**Rationale:** Plans 1.1 and 2.1 touch disjoint files (`CLAUDE.md` + `turtle_race.spec` vs `tools/smoke_phase_5.py` + `tools/smoke_packaged.md`), so they COULD parallelize in a single wave. They're split into separate waves anyway because:
- The CLAUDE.md addendum references the data-path invariant that the smoke verifies — having the addendum land first means the smoke's commit message can cross-reference the documented invariant.
- Phase 5 is the LOW-risk capstone phase; sequential commits are easier to debug if the packaged-exe smoke surfaces an unexpected `_MEIPASS` issue.
- The total work is small (2 plans, ~2 commits each) so the sequential cost is negligible.

**Implications:**
- The architect produces `.shipyard/phases/5/plans/PLAN-1.1.md` (wave: 1, deps: []) and `.shipyard/phases/5/plans/PLAN-2.1.md` (wave: 2, deps: [1.1]).

## Out-of-Scope Reminders (from ROADMAP / PROJECT.md)
- **No new functionality.** Phase 5 is polish + ship only.
- **No changes to scoring, filters, or UI** beyond what Phase 4 already shipped.
- **No performance optimization** beyond confirming no regression.
- **No README creation** (Decision 1).
- **No actual PyInstaller invocation** as part of the automated build pipeline (Decision 4) — the packaged-exe smoke is a human-run checklist artifact.

## Carryover from Phase 4 (informational)
- `dialogs.show_leaderboard()` shipped (renamed from `_placeholder`). `main.py:37` calls it.
- `tools/smoke_phase_2.py` and `tools/smoke_phase_3.py` are broken-by-design after subsequent phases' renames. `tools/smoke_phase_4.py` is the canonical Phase 4 smoke. Phase 5 adds `tools/smoke_phase_5.py` (different scope: path resolution + file lifecycle, NOT leaderboard UI contract).
- REVIEW-2.1 noted two minor findings (`_FILTER_LABEL_TO_KEY` value-level drift unchecked; `_repopulate`'s `rows` if/else binding fragile to refactor). These are NOT addressed in Phase 5 — they remain logged in the REVIEW file and can be picked up opportunistically if needed.
- SIMPLIFICATION-4 recommended deferring the `tools/_smoke_common.py` extraction decision to Phase 5 ("if Phase 5 adds a fourth smoke, extract then"). **Phase 5 IS adding a fourth smoke** (`smoke_phase_5.py`), which makes the rule-of-three threshold tip into rule-of-four territory.

### 6. Smoke-script common helper — DEFER
**Decision:** Despite Phase 5 introducing the fourth smoke script, the `tools/_smoke_common.py` extraction is **deferred** (NOT done in Phase 5). The new `smoke_phase_5.py` is allowed to duplicate the env-setup + monkeypatch boilerplate from `smoke_phase_4.py`.

**Rationale:**
- `smoke_phase_5.py` exercises a DIFFERENT scope from the other smokes (path resolution + file lifecycle, not the menu/round/leaderboard contract). Its monkeypatch surface and assertion shape will be only ~50% overlapping with `smoke_phase_4.py`.
- Phase 5 is LOW-risk and polish-focused. Adding a new shared module would extend Phase 5's scope (and reviewer/auditor/simplifier surface) for a refactor that's not strictly necessary.
- The decision to extract `tools/_smoke_common.py` can be made cleanly in a future maintenance pass — possibly as a follow-up issue logged in `.shipyard/ISSUES.md`. The duplication is currently visible and well-known, not hidden tech debt.

**Implications:**
- Plan 2.1 introduces `smoke_phase_5.py` as a standalone file mirroring `smoke_phase_3.py` / `smoke_phase_4.py`'s preamble pattern.
- After Phase 5 ships, an ISSUES.md entry recording the deferred extraction may be added during lesson capture.
