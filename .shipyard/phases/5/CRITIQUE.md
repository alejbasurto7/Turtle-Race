# Plan Critique — Phase 5: Polish and Ship

**Date:** 2026-05-17  
**Reviewer:** Verification Engineer  
**Phase:** 5 (LOW risk, 2 plans, 2 waves)

---

## Verdict: **READY**

Both Phase 5 plans are well-scoped, complete, and ready for builder execution. They adhere to CONTEXT-5 decisions, cover all ROADMAP success criteria, and follow established patterns from Phases 1–4.

---

## Per-Plan Feasibility

### PLAN 1.1 — Docs (CLAUDE.md addendum + turtle_race.spec comment)

#### ✅ YAML Frontmatter (8 required fields)
- `phase: polish-and-ship` — correct
- `plan: 1.1` — correct
- `wave: 1` — correct
- `dependencies: []` — correct (Wave 1, no upstream)
- `must_haves:` — 6 bullets, all present, objective and specific
- `files_touched:` — correct list (`CLAUDE.md`, `turtle_race.spec`)
- `tdd: false` — correct (docs-only, no TDD cycle)
- `risk: low` — appropriate for documentation change

#### ✅ File-path Accuracy
- **CLAUDE.md:** Current state verified (lines 1–89 read). Line 40 contains the stale "three modal dialogs" bullet — exact match against Plan 1.1's quoted text (`"owns the three modal dialogs in [dialogs.py](dialogs.py) — track selection, species selection, bet — and the "play again?" messagebox."`). ✓
- **CLAUDE.md target location:** Plan 1.1 specifies the addendum goes after `### Round loop shape` (which ends at line 88 per inspection). Correct. ✓
- **turtle_race.spec:** Current state verified (lines 1–15 read). Line 1 currently reads `block_cipher = None`. Plan 1.1 correctly specifies prepending a 2-line comment ABOVE this line. The `datas=` tuple at line 7 is correctly flagged as "must remain untouched." ✓
- **No other files touched.** Both plan files explicitly state not to create README.md. ✓

#### ✅ Decision Coverage
- **Decision 1 (no README):** Plan explicitly lists "Do NOT create README.md (CONTEXT-5 Decision 1 explicitly skips this)" in the must_haves. ✓
- **Decision 2 (CLAUDE.md shape + stale correction):** Tasks 1A and 1B address both items (line correction + new subsection). Subsection content matches Decision 2's four bullets (Tk-free, data path, schema_version, dialogs API direction). The suggested text includes platform paths (`%APPDATA%\TurtleRace\` Windows, `~/.local/share/TurtleRace/` Linux, `~/Library/Application Support/TurtleRace/` macOS), schema_version mention, and API contract. ✓
- **Decision 3 (turtle_race.spec comment):** Task 2 prepends the exact 2-line comment specified in Decision 3. Plan explicitly forbids touching `Analysis()`, `datas=`, `hiddenimports`, `PYZ`, `EXE`. ✓

#### ✅ Acceptance Criteria (Objective)
All criteria are objective and measurable:
- `grep -nE "^### Leaderboard \(Phase 1 module, Phase 4 view\)" CLAUDE.md` — exactly 1 hit
- `grep -cE "owns the six modal dialogs" CLAUDE.md` — 1
- `grep -cE "owns the three modal dialogs" CLAUDE.md` — 0 (stale removed)
- `grep -cE "schema_version" CLAUDE.md` — >= 1
- `grep -cE "user_data_path" CLAUDE.md` — >= 1
- `grep -cE "Tk-free" CLAUDE.md` — >= 1
- `python -c "import ast; ast.parse(...)"` — exits 0
- `test ! -f README.md` — README not created
- `pytest -q` — 135 passed

#### ✅ Verification Commands Syntax
Both `<verify>` blocks are syntactically valid PowerShell/Python:
- Task 1: `python -c "import dialogs; import main; import leaderboard" ; pytest -q`
- Task 2: `python -c "import ast; ast.parse(open('turtle_race.spec', encoding='utf-8').read())" ; pytest -q`

Commands use valid Python and pytest syntax. Cross-reference to `grep` is fine; the plan uses PowerShell format which supports `grep` (via alias to `findstr` or direct POSIX via Bash tool).

#### ✅ Scope Containment
Plan 1.1 declares `tdd: false` and specifies no new tests or pytest modifications — only documentation. The task bodies explicitly state "Do NOT modify any other section of CLAUDE.md" and "Do NOT modify ... Analysis, PYZ, EXE, ...". ✓

---

### PLAN 2.1 — Phase 5 smoke artifacts (automated source-mode + manual checklist)

#### ✅ YAML Frontmatter (8 required fields)
- `phase: polish-and-ship` — correct
- `plan: 2.1` — correct
- `wave: 2` — correct
- `dependencies: [1.1]` — correct (depends on Plan 1.1 for wave ordering; CLAUDE.md addendum documents the invariants this smoke verifies)
- `must_haves:` — 12 bullets, all present, specific and achievable
- `files_touched:` — correct list (`tools/smoke_phase_5.py`, `tools/smoke_packaged.md`)
- `tdd: false` — correct (smoke scripts are not pytest tests)
- `risk: low` — appropriate for a smoke test in the LOW-risk capstone phase

#### ✅ File-path Accuracy
- **tools/smoke_phase_5.py:** Does not exist yet; plan creates it as a new file. Plan specifies structure (module docstring, imports, main() function, `if __name__ == "__main__": main()`). ✓
- **tools/smoke_packaged.md:** Does not exist yet; plan creates it as a Markdown checklist artifact. Committed to repo (not under `.shipyard/`), per CONTEXT-5 Decision 4. ✓
- **No changes to production code.** Plan explicitly forbids touching `dialogs.py`, `main.py`, `leaderboard.py`, `race.py`, `audio.py`, `paths.py`, `constants.py`, `tracks.py`, `tests/`, or other smoke scripts. ✓

#### ✅ Decision Coverage
- **Decision 4 (split smoke into source-mode automated + packaged-exe manual checklist):** Plan creates BOTH files. Scope split verified: `smoke_phase_5.py` targets path-resolution + file-lifecycle (NOT menu/round/leaderboard UI contract — `smoke_phase_4.py` covers that). Checklist does NOT instruct builder to run PyInstaller (manual step). ✓
- **Decision 5 (wave structure):** Plan 2.1 declares `wave: 2, dependencies: [1.1]`. Correct. ✓
- **Decision 6 (smoke-script common helper — DEFER):** Plan explicitly lists "Per CONTEXT-5 Decision 6 — smoke_phase_5.py duplicates env-setup boilerplate from smoke_phase_4. NO tools/_smoke_common.py extraction". ✓

#### ✅ Acceptance Criteria (Objective)
All criteria are objective and measurable:
- **`tools/smoke_phase_5.py` exists and exits 0:** `python tools/smoke_phase_5.py` exits 0 and prints final PASS line
- **Path resolution verified:** `paths.user_data_path("leaderboard.json")` resolves under tempdir AND parent dir exists
- **2-race fixture:** `leaderboard.record_race` called exactly 2 times (verified by `grep -cE "leaderboard\.record_race" tools/smoke_phase_5.py` == 2)
- **JSON file lifecycle:** schema_version=1, races list grows, reset_session leaves file byte-identical, reset_all rewrites to canonical shape
- **Tk-free invariant:** `grep -cE "^import dialogs|^import main|^import tkinter|^import turtle|^import pygame|^import audio|^import race|^import constants|^import tracks"` == 0
- **Checklist present:** `tools/smoke_packaged.md` exists with 10-step PASS/FAIL boxes
- **pytest -q reports 135 passed**

All commands are grep/Python expressions (cross-platform via Bash tool, valid PowerShell syntax).

#### ✅ Verification Commands Syntax
- `<verify>`: `python tools/smoke_phase_5.py ; pytest -q` — valid
- Verification section: Multiple `grep -cE` patterns and file existence checks — all valid

#### ✅ Scope Containment
Plan declares `tdd: false` and lists 12 explicit `must_haves` that forbid touching any production code. Task 1 is atomic (both files created in same commit). ✓

#### ✅ Smoke Structuring
Inspection of `tools/smoke_phase_4.py` (Phase 4 precedent) shows:
- Monkeypatch-based architecture (replaces dialogs callables)
- Tempfile env redirect BEFORE import
- `[smoke]` log-prefix style
- Exit 0 on success, sys.exit(1) on failure

Plan 2.1's spec for `smoke_phase_5.py` mirrors this pattern exactly (per must_haves: "Mirrors the [smoke] log-prefix style and tmpdir-via-tempfile-mkdtemp pattern from smoke_phase_3 / smoke_phase_4"). The architect's recommended code blocks (Step 1–6 in Action section) follow the same style. ✓

---

## Cross-Plan Findings

### ✅ Dependency Ordering
- Plan 1.1 (Wave 1) has `dependencies: []` — no upstream.
- Plan 2.1 (Wave 2) has `dependencies: [1.1]` — correctly declares Wave 1 dependency.
- Both are sequential, which is correct: Wave 1 must complete before Wave 2 starts (CONTEXT-5 Decision 5).

### ✅ Same-File Conflicts
- Plan 1.1 touches: `CLAUDE.md`, `turtle_race.spec`
- Plan 2.1 touches: `tools/smoke_phase_5.py`, `tools/smoke_packaged.md`
- **No overlap.** ✓

### ✅ Cross-Plan Reference Integrity
- Plan 1.1's CLAUDE.md addendum documents the leaderboard module's Tk-free invariant and file-path resolution.
- Plan 2.1's `smoke_phase_5.py` exercises exactly those invariants (path resolution, file lifecycle).
- Plan 2.1's `smoke_packaged.md` references `tools/smoke_phase_5.py` as the automated complement.
- All references are consistent. ✓

---

## Risk Register

| Risk | Likelihood | Plan Impact | Mitigation |
|------|------------|-------------|-----------|
| CLAUDE.md edit lands in wrong location (not after Round loop shape) | Very Low | Plan 1.1 Task 1 | Verification command `grep -nE "^### Leaderboard"` + `<done>` assert "sits AFTER `### Round loop shape`" |
| turtle_race.spec comment breaks Python syntax | Very Low | Plan 1.1 Task 2 | `python -c "import ast; ast.parse(...)"` in `<verify>` catches this |
| smoke_phase_5.py imports Tk-touching module | Low | Plan 2.1 | `grep` verification explicitly checks for forbidden imports returning 0 |
| leaderboard API contract changes post-Plan 1.1 | N/A | N/A | Phase 1 is complete; leaderboard.py is stable |
| Manual checklist incomplete (missing steps) | Very Low | Plan 2.1 | Verification requires `>= 10` PASS/FAIL boxes |

**Overall:** Phase 5 is LOW-risk by design. No breaking changes. Documentation-only + smoke-only. Phase 1–4 are already shipped and stable.

---

## Complexity Flags

| Flag | Status |
|------|--------|
| **Circular dependencies** | None — Wave 1 → Wave 2 is clean |
| **Ambiguous acceptance criteria** | None — all measurable via grep/Python/pytest |
| **Vague verification commands** | None — all explicit and runnable |
| **Out-of-scope scope creep** | None — both plans explicitly forbid changes outside declared files_touched |
| **Task atomicity** | Good — Plan 1.1 has 2 tasks; Plan 2.1 has 1 task (both files in one commit). Each is atomic. |
| **Duplication across plans** | Acceptable — Plan 2.1 duplicates boilerplate from smoke_phase_4.py per CONTEXT-5 Decision 6 (deferred common extraction). Documented explicitly in Plan 2.1 Context. |
| **PyInstaller interaction** | Correct — Plan 2.1's `smoke_packaged.md` is a human-run checklist; builder does NOT run PyInstaller. Proper separation per Decision 4. |

---

## Decision Traceability

| CONTEXT-5 Decision | Plan Coverage | Evidence |
|-------------------|----------------|----------|
| 1 — No README | Plan 1.1 must_haves | "Do NOT create README.md (CONTEXT-5 Decision 1 explicitly skips this)" |
| 2 — CLAUDE.md shape + stale correction | Plan 1.1 Tasks 1A & 1B | Addendum placement, four bullets, stale line replacement all specified |
| 3 — turtle_race.spec comment + no functional change | Plan 1.1 Task 2 | 2-line comment prepended; `datas=` / Analysis / EXE / etc. forbidden |
| 4 — Split smoke into automated + manual | Plan 2.1 files_touched | Creates both `smoke_phase_5.py` (automated) + `smoke_packaged.md` (checklist) |
| 5 — Wave structure (Wave 1 + Wave 2) | YAML frontmatter | Plan 1.1: `wave: 1, dependencies: []`; Plan 2.1: `wave: 2, dependencies: [1.1]` |
| 6 — Defer common helper extraction | Plan 2.1 must_haves | "Per CONTEXT-5 Decision 6 — ... NO tools/_smoke_common.py extraction" |

All decisions are honored. ✓

---

## ROADMAP Success Criteria Alignment

Phase 5 ROADMAP bullets (from `.shipyard/ROADMAP.md` Phase 5 section):

| Criterion | Plan | Coverage |
|-----------|------|----------|
| 1. CLAUDE.md gains a short addendum (10–20 lines) covering Tk-free invariant, %APPDATA% data path, schema_version field, and dialogs.show_leaderboard() API direction | Plan 1.1 Task 1B | ✓ Addendum has 4 mandatory bullets; estimated ~15 lines |
| 2. turtle_race.spec is reviewed — confirm no new datas= needed, comment or commit message | Plan 1.1 Task 2 | ✓ 2-line comment prepended; no datas= change |
| 3. README (if exists) — skip without ceremony (it doesn't exist) | Plan 1.1 must_haves | ✓ Explicitly forbids README creation |
| 4. Build exe, race once, quit, confirm %APPDATA%\TurtleRace\leaderboard.json contains the race | Plan 2.1 smoke_packaged.md Step 6 | ✓ Manual checklist Step 6: verify JSON file with race data |
| 5. Smoke-test all reset paths (Reset Session leaves file unchanged; Reset All wipes to canonical) | Plan 2.1 smoke_phase_5.py Steps 4–5 | ✓ Automated smoke verifies both reset paths |
| 6. All previous-phase success criteria still hold | Both plans | ✓ pytest -q reports 135 passed (Phase 1–4 test suite) |
| 7. pytest remains green | Both plans | ✓ Verification commands include `pytest -q` |

All ROADMAP criteria are addressed. ✓

---

## Recommendations

### Plan 1.1
- **No changes required.** The plan is complete and ready.
- **Minor note:** The suggested CLAUDE.md addendum text includes the phrase "do not add `import tkinter` ... to `leaderboard.py`" — this is prescriptive guidance for future maintainers, which is appropriate.

### Plan 2.1
- **No changes required.** The plan is complete and ready.
- **Minor note:** The plan allows the builder to use any racer names in the `record_race` fixture ("Use canonical names ... or ... any 4-string list works"). This is correct — `leaderboard.py` does not validate names against constants.

---

## Headline

**Phase 5 plans are ready for builder execution.** Both adhere to CONTEXT-5 binding decisions, cover all ROADMAP criteria, declare correct dependencies and wave order, and include objective, runnable verification commands. No scope creep, no ambiguities, no conflicts. Risk is appropriately LOW.

---

## Sign-off

| Aspect | Status | Evidence |
|--------|--------|----------|
| Plan completeness | ✅ PASS | All 8 YAML fields present; frontmatter, Context, Dependencies, Tasks, Acceptance, Verification sections all complete |
| Decision coverage | ✅ PASS | All 6 CONTEXT-5 decisions honored |
| Acceptance objectivity | ✅ PASS | All criteria measurable via grep / pytest / Python syntax check |
| Verification runnability | ✅ PASS | All `<verify>` and Verification-section commands are valid and can run in the builder environment |
| File-path accuracy | ✅ PASS | Current state verified; target locations confirmed; no cross-plan file conflicts |
| Dependency ordering | ✅ PASS | Wave 1 → Wave 2 is clean; no circular dependencies |
| Scope containment | ✅ PASS | No production code changes; files_touched lists are complete and accurate |
| Risk alignment | ✅ PASS | Marked `risk: low`; consistent with Phase 5's LOW-risk budget and documentation/smoke scope |

**VERDICT: READY — No revisions required. Proceed to builder.**
