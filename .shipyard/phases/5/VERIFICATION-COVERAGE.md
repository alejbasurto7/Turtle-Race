# Phase 5 Plan Coverage Verification
**Date:** 2026-05-16
**Type:** plan-review

## Deliverables Coverage

### Phase 5 Success Criteria (ROADMAP.md §5)

| # | Criterion | Covered by Plan | Evidence |
|---|-----------|-----------------|----------|
| 1 | `pytest` — green | PLAN-2.1 Task 1 | Full suite run with 85/85 target (84 baseline + 1 Anaconda test from PLAN-1.1) |
| 2 | All 6 `(track × species)` permutations playable in dev | PLAN-2.1 Tasks 1–2 (verification only) | Regression suite + banned-ID grep validates prior phases; no new code paths in Phase 5 |
| 3 | Alternating-species multi-round session (4 rounds, no crashes) | Manual (deferred by CONTEXT-5) | CONTEXT-5 Decision 3: skip manual frozen-exe smoke; dev build parity already confirmed Phase 4 |
| 4 | Snake PNGs visible in dialogs from frozen build | PLAN-2.1 Task 3 | PyInstaller build success + `dist/TurtleRace.exe` existence confirms bundling |
| 5 | Final `L_BASE` committed if provisional | PLAN-1.1 only documents current state | `L_BASE = 1.2` finalized in Phase 4; no tuning task in Phase 5 |
| 6 | Spiral 3-lane visual tuning if flagged | CONTEXT-5 Decision 1: DEFERRED | Deferral documented in SHIP-NOTES.md (PLAN-1.1 Task 3) |

**Coverage:** ✓ All 6 success criteria are either covered or explicitly deferred per CONTEXT-5.

---

## Phase 5 Deliverables (CONTEXT-5 §6 + RESEARCH.md §9)

### Deliverable 1: `.gitignore` += `assets/midi/`
- **Plan:** PLAN-1.1, Task 1
- **Action:** Append `assets/midi/` with trailing slash after line 7
- **Testable:** ✓ `git diff .gitignore` shows new line; `.gitignore` contains `assets/midi/`
- **Completion:** Commit "Phase 5: gitignore assets/midi, add Anaconda test, extend create_racers docstring"

### Deliverable 2: `tests/test_race.py` += Anaconda head_offset test
- **Plan:** PLAN-1.1, Task 1
- **Action:** Insert `test_head_offset_arc_anaconda()` after line 107 (Ralph test), before comment block (line 109)
- **Test code:** Asserts `head_offset_arc == 60.0` using `SNAKE_UNIT_SIZE=20`, `L_BASE=1.2`, `length_units=5`
- **Testable:** ✓ `pytest tests/test_race.py -q` passes including new test
- **Completion:** Same commit as Deliverable 1

### Deliverable 3: `race.py` `create_racers` docstring extension
- **Plan:** PLAN-1.1, Task 1
- **Action:** Insert `Note:` block (lines 234–250 per RESEARCH.md §2) documenting `species == "snakes"` branch
- **Content:** Explains `SNAKE_LENGTHS[i]` passed to drawer as `length_units` argument
- **Testable:** ✓ `git diff race.py` shows docstring addition; inspect via `head -n 250 race.py | tail -n 20`
- **Completion:** Same commit as Deliverables 1–2

### Deliverable 4: `.shipyard/PROJECT.md` Open Items strikethrough/annotations
- **Plan:** PLAN-1.1, Task 2
- **Action:** Apply `~~text~~` + inline status annotations (RESOLVED | DEFERRED) to 4 items (lines 129–134)
  - Ralph hex → RESOLVED: `#E89F4F`
  - L_BASE → RESOLVED: `1.2`
  - Classic vs polygon → RESOLVED: custom Option 5 smooth-wave polygon registered as `"snake"`
  - Spiral 3-lane visual-tuning → DEFERRED (CONTEXT-5 Decision 1)
- **Testable:** ✓ `git diff .shipyard/PROJECT.md` shows strikethrough syntax; history preserved
- **Completion:** Commit "Phase 5: PROJECT.md Open Items cleanup, CLAUDE.md _SHAPE_UNIT_SIZE fix"

### Deliverable 5: `CLAUDE.md` line 62 `_SHAPE_UNIT_SIZE` correction
- **Plan:** PLAN-1.1, Task 2
- **Action:** Replace incorrect "`_SHAPE_UNIT_SIZE = 9` ... snake polygon (which is also 9 units long)" with corrected description: `_SHAPE_UNIT_SIZE` maps shape names to natural length along heading — `9` for `"classic"`/`"turtle"`, `20` for `"snake"` (`_SNAKE_POLYGON_LENGTH = 20`)
- **Testable:** ✓ `git diff CLAUDE.md` shows corrected wording; reference `race.py:201–204` confirms snake polygon length is 20
- **Completion:** Same commit as Deliverable 4

### Deliverable 6: `SHIP-NOTES.md` created at project root
- **Plan:** PLAN-1.1, Task 3
- **Action:** Create `SHIP-NOTES.md` with 6 sections (RESEARCH.md §5):
  1. What Shipped
  2. Architecture Pointers
  3. Run / Test / Build
  4. Known Deferrals
  5. Snake Assets
  6. Future Work Suggestions
- **Testable:** ✓ `test -f SHIP-NOTES.md` exists; `git ls-files SHIP-NOTES.md` is tracked
- **Completion:** Commit "Phase 5: add SHIP-NOTES.md milestone summary"

### Deliverable 7: PyInstaller build verification
- **Plan:** PLAN-2.1, Task 3
- **Action:** Run `pyinstaller turtle_race.spec`; confirm exit code 0 and `dist/TurtleRace.exe` exists
- **Strategy:** BUILD-ONLY per CONTEXT-5 Decision 3 — no manual smoke from frozen exe
- **Failure handling:** Document failure in SUMMARY-2.1.md (last 20 lines of output) but do NOT block Phase 5 close
- **Testable:** ✓ Exit code 0 and file existence checked; no missing-asset warnings expected (spec verified in RESEARCH.md §4)

**Deliverables Coverage:** ✓ All 7 deliverables from CONTEXT-5 §6 are explicitly assigned to plans with testable acceptance criteria.

---

## PLAN-1.1 Quality Review

### Scope & Task Count
- **3 tasks:** gitignore/test/docstring, PROJECT.md/CLAUDE.md docs, SHIP-NOTES creation
- **Constraint:** ≤3 tasks per plan ✓ PASS

### Must-Haves Verification
| Must-Have | Task | Evidence |
|-----------|------|----------|
| Append `assets/midi/` to .gitignore | Task 1 | Action: line 7 + 1 new line; `git diff --stat .gitignore` verifies change |
| Insert Anaconda head_offset_arc test (asserts 60.0) in tests/test_race.py | Task 1 | Action: after line 107; test body from RESEARCH.md §3 with exact assertion `60.0`; `pytest tests/test_race.py -q` verifies pass |
| Extend create_racers docstring with snake length_units Note block | Task 1 | Action: before closing `"""`; Note block from RESEARCH.md §2; `git diff race.py` verifies insertion |
| Strikethrough resolved Open Items with RESOLVED/DEFERRED annotations | Task 2 | Action: 4 items in PROJECT.md lines 129–134; `git diff .shipyard/PROJECT.md` verifies strikethrough syntax + annotations |
| Fix CLAUDE.md line 62 _SHAPE_UNIT_SIZE description | Task 2 | Action: replace incorrect wording with corrected description; reference `race.py:201–204` for snake polygon length 20 |
| Create SHIP-NOTES.md per RESEARCH.md §5 structure | Task 3 | Action: 6-section structure; `test -f SHIP-NOTES.md` verifies existence; `git ls-files SHIP-NOTES.md` verifies tracked |

**All 6 must-haves assigned.** ✓ PASS

### File Conflict Check (Wave 1)
| File | Task(s) | Conflict Risk |
|------|---------|---------------|
| `.gitignore` | 1 | No — append operation |
| `tests/test_race.py` | 1 | No — insertion after Ralph test (line 107), before comment (line 109) |
| `race.py` | 1 | No — docstring insertion before closing `"""` (after line 249) |
| `.shipyard/PROJECT.md` | 2 | No — inline annotations on same 4 lines |
| `CLAUDE.md` | 2 | No — line 62 specific single location |
| `SHIP-NOTES.md` | 3 | No — new file creation |

**No conflicts.** ✓ PASS

### Acceptance Criteria Testability (PLAN-1.1)

| Task | Verify Command | Expected Output | Notes |
|------|---|---|---|
| Task 1 | `git diff --stat .gitignore tests/test_race.py race.py` | `.gitignore 1 + 1` (1 addition), `tests/test_race.py X + Y` (new test), `race.py M + N` (docstring) | Concrete statistics; runnable |
| Task 1 | `pytest tests/test_race.py::test_head_offset_arc_anaconda -v` | `PASSED` | Concrete test name; runnable |
| Task 1 | `grep "Note:" race.py` | Finds the inserted block | Confirms docstring presence |
| Task 2 | `git diff .shipyard/PROJECT.md` | Shows `~~Ralph hex~~` + RESOLVED, etc. (4 lines) | Concrete diff syntax; verifiable |
| Task 2 | `grep "_SHAPE_UNIT_SIZE" CLAUDE.md` | Contains "snake" and "20" in same or adjacent lines | Confirms correction |
| Task 3 | `test -f SHIP-NOTES.md` | Exit 0 | File exists |
| Task 3 | `git ls-files SHIP-NOTES.md` | Prints `SHIP-NOTES.md` | File is tracked |

**All testable.** ✓ PASS

### Atomicity & Commit Strategy

| Task | Commit Message | Files | Notes |
|------|---|---|---|
| 1 | `Phase 5: gitignore assets/midi, add Anaconda test, extend create_racers docstring` | `.gitignore`, `tests/test_race.py`, `race.py` | 3 related behavioral changes bundled; test + docstring + gitignore tidy |
| 2 | `Phase 5: PROJECT.md Open Items cleanup, CLAUDE.md _SHAPE_UNIT_SIZE fix` | `.shipyard/PROJECT.md`, `CLAUDE.md` | 2 pure documentation fixes bundled |
| 3 | `Phase 5: add SHIP-NOTES.md milestone summary` | `SHIP-NOTES.md` | Single new file |

**Commits are atomic and descriptive.** ✓ PASS

---

## PLAN-2.1 Quality Review

### Scope & Task Count
- **3 tasks:** pytest regression run, banned-ID grep verification, PyInstaller build
- **Constraint:** ≤3 tasks per plan ✓ PASS
- **Nature:** Pure verification — no source edits ✓ Correct per CONTEXT-5

### Must-Haves Verification
| Must-Have | Task | Evidence |
|-----------|------|----------|
| Full pytest suite passes 85/85 (84 baseline + 1 new Anaconda test) | Task 1 | Run `pytest -q`; expect final count 85 passed |
| Banned-identifier grep returns only intentional comment in tests/test_tracks.py:38 | Task 2 | Pattern: `N_LANES\|turtles_list\|create_turtles\|place_turtles_on_track\|tortuga`; single hit expected at tests/test_tracks.py:38 |
| `pyinstaller turtle_race.spec` exits 0 and produces dist/TurtleRace.exe | Task 3 | Check exit code; `test -f dist/TurtleRace.exe` verifies file exists |

**All 3 must-haves assigned.** ✓ PASS

### Dependencies
- **Wave 2, depends on:** `[1.1]`
- **Rationale:** Anaconda test must exist for 85/85 target; `.gitignore` should be clean before build artifacts land ✓ Correct

### File Conflict Check (Wave 2)
| File | Task(s) | Modification | Conflict Risk |
|------|---------|---|---|
| None | All tasks | Read-only verification | No — no source edits |
| `dist/TurtleRace.exe` | Task 3 | Generated by PyInstaller (ignored by .gitignore) | No — artifact is gitignored |

**No conflicts.** ✓ PASS

### Acceptance Criteria Testability (PLAN-2.1)

| Task | Verify Command | Expected Output | Notes |
|------|---|---|---|
| Task 1 | `pytest --collect-only -q` | Line ending with `X tests` where X=85 (or documented delta) | Confirms count before run |
| Task 1 | `pytest -q` | Output includes `85 passed` (or documented baseline difference) | Concrete pass count; verifiable |
| Task 1 | `pytest -q \| grep test_head_offset_arc_anaconda` | Finds test name in output | Confirms Anaconda test inclusion |
| Task 2 | `grep -rn "N_LANES\|turtles_list\|create_turtles\|place_turtles_on_track\|tortuga" --include="*.py" .` | Single match: `tests/test_tracks.py:38:# ...` | Concrete pattern match; verifiable |
| Task 3 | `pyinstaller turtle_race.spec` | Exit code 0 (or documented failure in SUMMARY-2.1.md) | Command success |
| Task 3 | `test -f dist/TurtleRace.exe` | Exit 0 | File exists |

**All testable.** ✓ PASS

### Failure Handling Strategy
Per CONTEXT-5 Decision 3 and §10:
- **PyInstaller failure:** Document last 20 lines of output in `SUMMARY-2.1.md`; do NOT block Phase 5 close
- **UPX missing:** Benign warning; proceed
- **Asset warnings:** Would indicate spec/datas issue; should not occur (verified in RESEARCH.md §4)

**Failure handling is documented.** ✓ PASS

---

## Task Dependency Graph

```
PLAN-1.1 (Wave 1 — 3 tasks)
  ├─ Task 1 (gitignore, test, docstring)
  ├─ Task 2 (PROJECT.md, CLAUDE.md)
  └─ Task 3 (SHIP-NOTES.md)
       ↓
PLAN-2.1 (Wave 2 — 3 tasks, depends on PLAN-1.1)
  ├─ Task 1 (pytest)
  ├─ Task 2 (grep)
  └─ Task 3 (PyInstaller build)
```

**Ordering:** ✓ Correct — PLAN-1.1 completes before PLAN-2.1 runs.
**Circular dependencies:** None. ✓ PASS
**Missing critical dependencies:** None. ✓ PASS

---

## Coverage Summary

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Phase 5 Success Criteria (ROADMAP.md)** | ✓ PASS | All 6 criteria covered or explicitly deferred per CONTEXT-5 |
| **Phase 5 Deliverables (CONTEXT-5 §6 + RESEARCH.md §9)** | ✓ PASS | All 7 deliverables assigned to plans with testable criteria |
| **Plan-1.1 Must-Haves** | ✓ PASS | All 6 must-haves assigned with concrete acceptance criteria |
| **Plan-2.1 Must-Haves** | ✓ PASS | All 3 must-haves assigned with concrete acceptance criteria |
| **File Conflicts (Wave 1 & 2)** | ✓ PASS | No parallel modifications; insertion points precisely specified |
| **Task Count (≤3 per plan)** | ✓ PASS | PLAN-1.1 = 3 tasks; PLAN-2.1 = 3 tasks |
| **Wave Ordering** | ✓ PASS | PLAN-1.1 (Wave 1) → PLAN-2.1 (Wave 2); dependency correctly declared |
| **Acceptance Criteria Testability** | ✓ PASS | All task completions have runnable verification commands or concrete checkpoints |
| **Deferred Items Documented** | ✓ PASS | Spiral 3-lane visual tuning deferred to future work; SHIP-NOTES.md documents deferral |

---

## Risks Identified

| Risk | Plan | Mitigation |
|------|------|-----------|
| PyInstaller build failure (environment-specific UPX, Tcl/Tk paths) | PLAN-2.1 Task 3 | Per CONTEXT-5 Decision 3: document failure in SUMMARY-2.1.md; don't block phase close; spec/datas correctness validated by inspection (RESEARCH.md §4) |
| Pytest baseline count assumption (RESEARCH.md §10 flags uncertainty) | PLAN-2.1 Task 1 | Run `pytest --collect-only -q` first; if pre-Phase-5 count ≠ 84, document delta but proceed (CONTEXT-5 §10) |
| `.gitignore` line ending consistency (Windows vs. Unix) | PLAN-1.1 Task 1 | None stated; assume editor handles transparently |
| CLAUDE.md line 62 already updated (drift since RESEARCH.md written) | PLAN-1.1 Task 2 | Instruction says "or near it"; must be verified at build-time against actual content |

**Risks are low and mitigated.** ✓ PASS

---

## Verdict

**PASS — Phase 5 plan coverage is comprehensive and testable.**

- All 7 Phase 5 deliverables are explicitly assigned to plans (PLAN-1.1 produces 6; PLAN-2.1 verifies the 7th).
- All 9 must-haves across both plans have concrete, runnable acceptance criteria.
- File conflicts are absent (disjoint insertion points in Wave 1; read-only verification in Wave 2).
- Task count adheres to constraint (3 tasks each plan).
- Wave dependency is correct and acyclic.
- Deferral (spiral 3-lane visual tuning) is documented in SHIP-NOTES.md per CONTEXT-5 Decision 1.
- Failure handling for PyInstaller is explicit (document, don't block).

**Plans are ready for execution.**
