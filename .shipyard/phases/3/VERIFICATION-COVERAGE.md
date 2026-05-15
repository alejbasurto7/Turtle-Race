# Coverage Verification Report — Phase 3 Plans
**Date:** 2026-05-15  
**Type:** plan-review  
**Scope:** PLAN-1.1, PLAN-2.1, PLAN-2.2

---

## Executive Summary

The three Phase 3 plans collectively cover all seven Phase 3 deliverables with no gaps or double coverage. Task count, wave ordering, and file conflicts are all within acceptable bounds. One design oddity (PLAN-2.2) has been assessed and a recommendation issued.

**Verdict:** **PASS** (with recommendation on PLAN-2.2 workflow integration)

---

## 1. Coverage Analysis

### Phase 3 Deliverables (ROADMAP §Phase 3)

| # | Deliverable | PLAN | Task | Status |
|---|-------------|------|------|--------|
| 1 | `dialogs.py`: new `get_user_species()` with composite images | 2.1 | 1 | ✓ Covered |
| 2 | `dialogs.py`: refactor `get_user_bet(species)` with if/elif on `SPECIES[species]["bet_layout"]` | 1.1 | 3 | ✓ Covered |
| 3 | `_TURTLE_GRID_LAYOUT` and `_SNAKE_ROW_LAYOUT` module-level constants | 1.1 | 2 | ✓ Covered |
| 4 | `main.py`: insert `species = dialogs.get_user_species()` between track and create_racers | 2.1 | 2 | ✓ Covered |
| 5 | `main.py`: pass `species` to `create_racers(species)` and `get_user_bet(species)` | 2.1 | 2 | ✓ Covered |
| 6 | `constants.py`: `SPECIES_DIALOG_IMAGE_SIZE = 200` constant | 1.1 | 1 | ✓ Covered |
| 7 | End-state: snakes mode reaches podium with turtle-shaped placeholders | 2.1 | 3 (manual smoke) | ✓ Covered |

**Coverage verdict:** All deliverables addressed; no orphans or double coverage.

---

## 2. Per-Plan Assessment

### PLAN-1.1 — `constants.py` constant + `get_user_bet(species)` refactor

**Wave:** 1 (no dependencies)  
**Task count:** 3 ✓

**Must-haves verification:**
- `SPECIES_DIALOG_IMAGE_SIZE = 200` in constants.py — Task 1
- Test for `SPECIES_DIALOG_IMAGE_SIZE` — Task 1
- `get_user_bet(species)` refactor — Task 3
- `_TURTLE_GRID_LAYOUT` and `_SNAKE_ROW_LAYOUT` module-level — Task 2
- `row_3` branch with Shadow | Ralph | Anaconda buttons at `BET_IMAGE_SIZE` — Task 3
- pytest GREEN — All tasks

**Deliberate mid-phase breakage:** PLAN-1.1 leaves `main.py` calling `get_user_bet()` with no args (post-refactor signature requires `species`). This will produce `TypeError` at runtime. This is intentional and mirrors Phase 2's pattern (refactor in Wave 1, repair in Wave 2). The pattern was successful then; no regression risk here.

**TDD compliance:** Task 1 is explicitly TDD (test-first). ✓

**Verdict:** PLAN-1.1 is well-formed.

---

### PLAN-2.1 — `get_user_species()` + `main.py` wire-up + manual smoke

**Wave:** 2  
**Depends on:** PLAN-1.1 ✓  
**Task count:** 3 ✓

**Must-haves verification:**
- `get_user_species()` returning "turtles" or "snakes" — Task 1
- Composite images (2x2 turtles, 1x3 snakes) at `SPECIES_DIALOG_IMAGE_SIZE` — Task 1
- `main.py` inserts `species = dialogs.get_user_species()` — Task 2
- `species` passed to `create_racers(species)` and `get_user_bet(species)` — Task 2
- Hoist `n = len(racers)` (SIMPLIFICATION-2 S2.2) — Task 2 (opportunistic)
- `create_racers` docstring updated (DOCUMENTATION-2) — Task 2 (opportunistic)
- Manual smoke: both species reach podium — Task 3
- pytest GREEN — All tasks

**Composite image strategy:** PLAN-2.1 Task 1 specifies:
- Turtle composite: 2×2 grid at 100 px per cell, composited at dialog-open time, resized to `SPECIES_DIALOG_IMAGE_SIZE`
- Snake composite: 1×3 row at ~66 px per cell, resized to `SPECIES_DIALOG_IMAGE_SIZE`
- Image-ref retention on `dialog._species_images = []` (critical for Tk GC prevention)
- Use inline composition (no helper extraction per CONTEXT-3 Decision 2)

**Opportunistic cleanups:** The hoist and docstring updates are explicitly authorized by CONTEXT-3 Decision 5. These are non-blocking but valuable (reduce boilerplate, improve maintainability).

**Manual smoke gate:** Task 3 is the critical acceptance criterion. It verifies:
1. Round 1: Turtles flow unchanged (regression check)
2. Round 2: Snakes flow reaches podium (new path)
3. Round 3: Cross-species switching (state leak check)

The artifact required (`SUMMARY-2.1.md`) must record pass/fail with enough detail for Phase 4 to act on any blockers.

**Verdict:** PLAN-2.1 is well-formed; manual smoke is the hard gate.

---

### PLAN-2.2 — Reviewer pass for Wave 1 + Wave 2

**Wave:** 2  
**Depends on:** PLAN-1.1 ✓ (reads post-PLAN-2.1-task-2 tree)  
**Task count:** 2 ✓

**Must-haves verification:**
- `REVIEW-1.1.md` on disk covering PLAN-1.1 changes — Task 1
- `REVIEW-2.1.md` on disk covering PLAN-2.1 changes — Task 2
- Reviews include: signature compat, image-ref retention, modal pattern, regression, docstring — Both tasks
- "Carry-over to Phase 4" section in REVIEW-2.1.md — Task 2
- Blocking findings escalated (not acted on in this plan) — Both tasks

**Checklist detail:** The reviews must cite file:line for every finding (blocking or not). Vague reviews are unactionable. PLAN-2.2 Task 1 and 2 have explicit verification steps that check for the disk artifacts.

---

## 3. PLAN-2.2 Oddity Assessment

### Problem Statement

PLAN-2.2 formalizes the code review as a **builder task** that produces `REVIEW-*.md` files on disk. This overlaps with the standard Shipyard workflow's Step 4c (reviewer dispatcher), which normally invokes separate reviewer agents. The question: is PLAN-2.2 redundant with the standard workflow, or does it serve a distinct purpose?

### Analysis

**Why PLAN-2.2 exists:**
- Phase 2 reviewers "consistently failed to write `REVIEW-W.P.md` to disk" (cited in PLAN-2.2 context)
- Making it an explicit plan with `must_haves` forces the artifact to surface
- The "Carry-over to Phase 4" section ensures blocking findings aren't lost between phases

**Why it could be considered redundant:**
- Standard Shipyard workflow already dispatches reviewers (Step 4c)
- The reviewer agent (if called) would produce similar `REVIEW-*.md` files
- Having PLAN-2.2 AND a standard reviewer step = two parallel review passes (wasteful)
- PLAN-2.2 cannot act on findings; it only documents them (a reviewer agent should escalate to a new plan if blocking)

**Execution model:**
- PLAN-2.2 runs in parallel with PLAN-2.1 (reviewer reads post-PLAN-2.1-task-2 commit)
- PLAN-2.2 is non-blocking (findings are recorded but not acted on immediately)
- Phase 4 input will reference the `REVIEW-*.md` carry-overs

### Recommendation: Option A (KEEP PLAN-2.2 as-is)

**Rationale:**
1. **Explicit enforcement:** Phase 2 already proved that implicit reviewer expectations failed. Making review an explicit plan with disk deliverables is more reliable than hoping a separate workflow step happens.
2. **Parallel cost:** Running PLAN-2.2 in parallel with PLAN-2.1 adds one task; it doesn't serialize the critical path (both are Wave 2).
3. **Handoff clarity:** The "Carry-over to Phase 4" section ensures Phase 4 inherits findings without them getting lost in chat history.
4. **Unconventional but proven:** This pattern (builder performs review) is not standard, but it worked for Phase 2 (once the artifact was written).

**Critical caveat:**
The parent workflow that dispatches these Phase 3 plans must **not also** dispatch a separate standard Reviewer step. PLAN-2.2 IS the reviewer step for Phase 3. If the workflow invokes both, you'll get duplicate reviews and wasted effort.

**If PLAN-2.2 fails (findings not written to disk):**
The build-verify step should flag this as a phase-completion blocker (no release until `REVIEW-*.md` files exist). This makes the artifact requirement just as enforceable as pytest passing.

---

## 4. Task Count & Wave Ordering

| Plan | Wave | Tasks | Limit | Status |
|------|------|-------|-------|--------|
| 1.1 | 1 | 3 | ≤3 | ✓ OK |
| 2.1 | 2 | 3 | ≤3 | ✓ OK |
| 2.2 | 2 | 2 | ≤3 | ✓ OK |

**Dependency chain:**
- PLAN-1.1 (Wave 1) has no dependencies ✓
- PLAN-2.1 (Wave 2) depends on PLAN-1.1 ✓
- PLAN-2.2 (Wave 2) depends on PLAN-1.1 ✓

**Wave 2 parallelization:**
- PLAN-2.1 and PLAN-2.2 can run in parallel (no shared file modifications during execution)
- PLAN-2.2 reads the post-PLAN-2.1-task-2 commit, so there's a logical dependency on PLAN-2.1 task 2, but PLAN-2.2 doesn't block PLAN-2.1
- Net effect: PLAN-2.1 completes first (manual smoke is the longest task), then PLAN-2.2 reviews the results

---

## 5. File Conflict Assessment

### PLAN-2.1 vs. PLAN-2.2 (parallel Wave 2 plans)

| File | PLAN-2.1 | PLAN-2.2 |
|------|----------|----------|
| `dialogs.py` | Modify (tasks 1–2) | Review only |
| `main.py` | Modify (task 2) | Review only |
| `race.py` | Modify (task 2, docstring) | Review only |
| `.shipyard/phases/3/reviews/*` | — | Create (tasks 1–2) |

**Conflict verdict:** None. PLAN-2.2 only reads and reviews; it does not modify production code. Safe to run in parallel. ✓

---

## 6. Verification Commands

The plans provide concrete verification commands for each task:

- **PLAN-1.1 Task 1:** `pytest tests/test_constants.py -k species_dialog_image_size -q`
- **PLAN-1.1 Task 2:** `python -c "import dialogs; assert dialogs._TURTLE_GRID_LAYOUT[0][0] == 'Leonardo'; assert dialogs._SNAKE_ROW_LAYOUT[0][0] == 'Shadow'; assert len(dialogs._SNAKE_ROW_LAYOUT) == 3; print('ok')"`
- **PLAN-1.1 Task 3:** `python -c "import dialogs, inspect; sig = inspect.signature(dialogs.get_user_bet); assert list(sig.parameters) == ['species'], sig; print('ok')"` && `pytest -q`
- **PLAN-2.1 Task 1:** `python -c "import dialogs, inspect; assert callable(dialogs.get_user_species); sig = inspect.signature(dialogs.get_user_species); assert len(sig.parameters) == 0; print('ok')"` && `pytest -q`
- **PLAN-2.1 Task 2:** Signature check + AST parse of `main.py` for `species` variable + `pytest -q`
- **PLAN-2.1 Task 3:** Manual smoke + SUMMARY file exists with size > 500 chars
- **PLAN-2.2 Task 1:** File-exists check for `REVIEW-1.1.md` with blocking/non-blocking sections
- **PLAN-2.2 Task 2:** File-exists check for `REVIEW-2.1.md` with carry-over section

All verification commands are concrete and runnable. ✓

---

## 7. Risks & Gotchas

### High-confidence (from ROADMAP gotchas & RESEARCH gotchas)

1. **Image-ref retention** (CRITICAL): Both `get_user_bet(species)` (snake branch) and `get_user_species()` must retain refs on dialog attributes (`dialog._bet_images`, `dialog._species_images`). Forgetting this causes blank buttons. PLAN-2.1 Task 1 explicitly includes `dialog._species_images = []` at line 45.

2. **Modal correctness**: The three-statement sequence (`protocol("WM_DELETE_WINDOW", ...) → grab_set() → wait_window()`) must appear in that order. PLAN-2.1 Task 1 and PLAN-1.1 Task 3 both specify this.

3. **Signature mismatch**: PLAN-1.1 intentionally breaks `main.py` (calling 0-arg `get_user_bet()` post-refactor). PLAN-2.1 Task 2 must fix this. If not fixed, the runtime error is immediate and obvious (good for catching in smoke test).

4. **Composite image sizing**: PLAN-2.1 Task 1 specifies cell sizes (100 px for 2×2 turtle grid, 66 px for 1×3 snake row). The research document confirms these are correct for `SPECIES_DIALOG_IMAGE_SIZE = 200`. ✓

### Medium-confidence (from CONTEXT-3 gotchas G1–G8)

- G1 (Tk modal): mitigated by copying boilerplate verbatim
- G2 (species image retention): mitigated by explicit must_have
- G3 (bet image retention): mitigated by initializing before if/elif
- G4 (snake row width): 492 px is acceptable on standard screens
- G5 (RGB/RGBA mismatch): mitigated by converting images to RGBA
- G6 (None return): mitigated by `WM_DELETE_WINDOW` no-op + modal pattern
- G7 (main.py signature mismatch): mitigated by PLAN-2.1 Task 2 fixing call site
- G8 (boundary stones ordering): already safe (PLAN-2.1 Task 2 places `create_racers` before `draw_boundary_stones`)

All documented gotchas have stated mitigations in the plans. ✓

---

## 8. Alignment with CONTEXT-3 Decisions

| Decision | PLAN Coverage | Status |
|----------|---------------|--------|
| D1 (Composite turtle/snake images) | PLAN-2.1 Task 1 | ✓ Covered |
| D2 (Keep 3 parallel implementations; no helper) | PLAN-2.1 Task 1 | ✓ Noted |
| D3 (Internal if/elif dispatch on bet_layout) | PLAN-1.1 Task 3 | ✓ Covered |
| D4 (Snake bet row layout) | PLAN-1.1 Task 3 | ✓ Covered |
| D5 (main.py insertion point & opportunistic cleanups) | PLAN-2.1 Task 2 | ✓ Covered |
| D6 (Snake mode reaches podium with turtle shapes) | PLAN-2.1 Task 3 (manual smoke) | ✓ Covered |
| D7 (Test for SPECIES_DIALOG_IMAGE_SIZE) | PLAN-1.1 Task 1 | ✓ Covered |

All decisions have explicit plan coverage. ✓

---

## 9. Quality Gates

All plans specify clear `pytest` green and manual acceptance gates:

- PLAN-1.1: `pytest -q` green at end of each task
- PLAN-2.1: `pytest -q` green + manual smoke matrix (6 permutations across tracks/species)
- PLAN-2.2: `REVIEW-*.md` artifacts on disk with no pytest obligation (review-only plan)

PLAN-2.1 Task 3's manual smoke is the hardest gate — it verifies end-to-end flow including image rendering, modal behavior, and podium reachability.

---

## 10. Recommendations

### For Execution

1. **Execute PLAN-1.1 first** (Wave 1). Confirm `pytest` green and that `main.py` fails with `TypeError` (intentional).
2. **Execute PLAN-2.1 and PLAN-2.2 in parallel** (Wave 2). PLAN-2.1 Task 3 (manual smoke) is the critical path; PLAN-2.2 can review simultaneously.
3. **If PLAN-2.1 Task 3 (smoke) fails**, mark the phase incomplete and do not proceed to Phase 4. Findings must be recorded in `SUMMARY-2.1.md`.
4. **If PLAN-2.2 does not produce `REVIEW-*.md` files**, treat it as a phase-completion blocker (same severity as pytest failure).

### For Workflow Integration

**Caveat on PLAN-2.2 (reviewer as builder):**
- The parent workflow dispatching these plans should **not also** invoke a standard Step 4c (reviewer dispatcher) for Phase 3.
- PLAN-2.2 IS the reviewer step. Invoking both will waste effort and create conflicting review documents.
- Document this in the workflow's Phase 3 section (e.g., "Reviewer step is PLAN-2.2; do not dispatch separate reviewer agent").

### For Future Phases

If Phase 4 execution shows PLAN-2.2's pattern working well (artifacts always on disk, no missed findings), consider codifying this as a standard Shipyard practice: explicit reviewer plans with must_haves instead of implicit workflow steps.

---

## 11. Conclusion

| Category | Result |
|----------|--------|
| **Coverage** | PASS — All 7 deliverables addressed; no gaps or double-coverage |
| **Task count** | PASS — All plans ≤ 3 tasks |
| **Wave ordering** | PASS — Sequential (1 → 2) with safe parallelization (2.1 ‖ 2.2) |
| **File conflicts** | PASS — No conflicts between parallel plans |
| **Verification commands** | PASS — All concrete and runnable |
| **PLAN-2.2 oddity** | PASS — Assessed; recommendation issued (Option A: keep, document caveat) |
| **Alignment with CONTEXT-3** | PASS — All 7 decisions have explicit plan coverage |
| **Quality gates** | PASS — pytest + manual smoke + review artifacts |

**VERDICT: PASS**

The Phase 3 plans are well-formed, comprehensive, and ready for execution. The PLAN-2.2 integration with the parent workflow requires a one-line clarification (do not dispatch separate reviewer step), but the plan itself is sound.
