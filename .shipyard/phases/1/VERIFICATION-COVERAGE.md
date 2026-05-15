# Plan Coverage Verification — Phase 1
**Date:** 2026-05-15
**Type:** pre-execution coverage review

## Executive Summary

All three Phase 1 plans are present and properly structured. Collectively they comprehensively address every Phase 1 requirement from ROADMAP.md and PROJECT.md. Task counts, dependencies, file conflicts, and acceptance criteria are sound. **VERDICT: PASS** — plans are ready for execution.

---

## Per-Plan Analysis

### Plan 1.1: TDD Red — Snake & SPECIES Invariant Tests

**Wave:** 1 (no dependencies)

**Files touched:** `tests/test_constants.py` only

**Task count:** 3 tasks ✓ (within limit of 3)

**Coverage of requirements:**
1. Snake identity invariant tests: 4 tests specified (test_snake_lists_are_length_3, test_snake_image_map_has_entry_for_every_snake_name, test_snake_lengths_positional_values, test_snake_image_files_exist_on_disk) — **covers SNAKE_NAMES, SNAKE_COLORS, SNAKE_LENGTHS, SNAKE_IMAGES validation from ROADMAP Phase 1 deliverables**
2. SPECIES schema tests: 5 tests specified (test_species_has_required_top_level_keys, test_species_entries_have_required_sub_keys, test_species_bet_layout_values_are_valid, test_species_racer_counts, test_species_shape_drawer_is_string_sentinel) — **covers SPECIES dict shape, string sentinel decision from CONTEXT-1.md, and required sub-keys**
3. RED-state verification: Task 3 explicitly verifies expected ImportError failure mode

**Must-haves check:**
- ✓ "All 9 new snake/SPECIES invariant tests added to tests/test_constants.py" — Tasks 1 and 2 list all 9
- ✓ "Tests mirror existing file style exactly (no PIL, no parametrize, no fixtures, manual project_root)" — Plan explicitly calls out manual project_root pattern from RESEARCH.md section 3 and prohibits parametrize/fixtures
- ✓ "Tests fail when run (RED) because constants do not yet exist" — Task 3 verifies ImportError at collection time
- ✓ "Imports extend the existing import line, not replace it" — Task 1 explicitly extends line 7, Task 2 extends again to add SPECIES

**Acceptance criteria specificity:**
- Task 1: Concrete assertion of import line extension + 4 new test functions in order ✓
- Task 2: 5 new test functions specified with exact test names and test logic descriptions ✓
- Task 3: Concrete pytest command + AST verification command with expected output ✓

**Risk assessment:** LOW — pure test additions, no code changes, no asset dependencies, no imports

---

### Plan 2.1: TDD Green — Implement Snake Constants and SPECIES Config

**Wave:** 2 (depends on 1.1)

**Files touched:** `constants.py` only

**Task count:** 3 tasks ✓ (within limit of 3)

**Coverage of requirements:**
1. Snake identity constants block: SNAKE_NAMES, SNAKE_COLORS, SNAKE_LENGTHS, SNAKE_IMAGES, L_BASE — **directly addresses all snake identity deliverables from ROADMAP Phase 1**
   - Ralph's hex `#E89F4F` from CONTEXT-1.md Decision 2 ✓
   - SNAKE_LENGTHS positional values [6, 2, 5] for [Shadow, Ralph, Anaconda] per CONTEXT-1.md Decision 2 ✓
   - L_BASE as placeholder (1.0) with comment noting Phase 4 tuning ✓
2. SPECIES config dict: turtles and snakes entries with required sub-keys (names, colors, images, bet_layout, shape_drawer) — **addresses SPECIES config from ROADMAP Phase 1 deliverables and CONTEXT-1.md Decision 1**
   - shape_drawer as string sentinel ("turtle"/"snake") per CONTEXT-1.md Decision 1 ✓
   - No imports from race.py (circular import prevention) ✓

**Must-haves check:**
- ✓ "SNAKE_NAMES, SNAKE_COLORS, SNAKE_LENGTHS, SNAKE_IMAGES, L_BASE defined in constants.py" — Task 1 defines all five with exact expected values and formats
- ✓ "SPECIES dict with 'turtles' and 'snakes' entries; shape_drawer is a STRING sentinel ('turtle'/'snake')" — Task 2 specifies exact SPECIES structure with string sentinels
- ✓ "constants.py imports nothing from race.py (no circular import)" — Plan explicitly prohibits this; acceptance criterion Task 1 verifies zero imports
- ✓ "All 9 new tests from Plan 1.1 turn green (assuming PNGs are present on disk; Plan 2.2 covers committing them)" — Task 3 runs pytest tests/test_constants.py and full pytest suite

**Acceptance criteria specificity:**
- Task 1: Concrete Python commands to verify each constant (SNAKE_NAMES, SNAKE_COLORS, SNAKE_LENGTHS, SNAKE_IMAGES, L_BASE types) + verification that constants.py has zero imports ✓
- Task 2: Concrete Python commands to verify SPECIES["snakes"]["names"], shape_drawer values, bet_layout values, and that SPECIES reference the original list objects ✓
- Task 3: pytest commands with explicit expected results (12 passed) ✓

**Wave 2 parallel execution:** Can run in parallel with Plan 2.2 because they modify disjoint files (constants.py vs. turtle_race.spec + assets/) — **no file conflicts** ✓

**Risk assessment:** LOW — pure data, additive to constants.py, no new imports, locked hex and values from CONTEXT-1.md

---

### Plan 2.2: TDD Green — Register Snake PNGs in PyInstaller Spec and Commit Assets

**Wave:** 2 (depends on 1.1)

**Files touched:**
- `turtle_race.spec` (modification)
- `assets/snakes/Shadow.png` (git add)
- `assets/snakes/Ralph.png` (git add)
- `assets/snakes/Anaconda.png` (git add)

**Task count:** 3 tasks ✓ (within limit of 3)

**Coverage of requirements:**
1. PyInstaller spec update: Add `('assets/snakes/*.png', 'assets/snakes')` to datas tuple — **addresses turtle_race.spec extension from ROADMAP Phase 1 deliverables**
   - Exact tuple and destination path matching SNAKE_IMAGES paths per RESEARCH.md section 2 ✓
   - Critical note on glob non-recursion and why the new tuple is genuinely additive ✓
2. Git add snake PNGs: Track `assets/snakes/{Shadow,Ralph,Anaconda}.png` — **addresses CONTEXT-1.md Decision 3 (PNGs committed in Phase 1)**
   - Ensures on-disk test survives fresh clone ✓
3. Joint-green verification: Confirms tests/test_constants.py passes with both plans complete

**Must-haves check:**
- ✓ "turtle_race.spec datas= includes ('assets/snakes/*.png', 'assets/snakes')" — Task 1 specifies exact edit with single-line format preservation
- ✓ "assets/snakes/Shadow.png, Ralph.png, Anaconda.png tracked by git" — Task 2 explicitly runs git add for all three, verifies via git ls-files
- ✓ "The on-disk snake PNG existence test survives a fresh clone after this phase ships" — Task 2 explains the current untracked state and Plan 2.2's role in fixing it; Task 3 verifies joint-green state

**Acceptance criteria specificity:**
- Task 1: Concrete Python command to verify spec edit (checks for substring `'assets/snakes/*.png'` and `'assets/snakes'` in the datas line) ✓
- Task 2: git commands (git ls-files, git cat-file -s) with expected output (three files alphabetical, non-empty) ✓
- Task 3: pytest commands with expected results (12 passed) + git ls-files verification ✓

**Wave 2 parallel execution:** Can run in parallel with Plan 2.1 because they modify disjoint files — **no file conflicts** ✓

**Risk assessment:** LOW — mechanical spec edit, git tracking of existing assets, no code changes

---

## Cross-Plan Dependency and Ordering Analysis

```
Plan 1.1 (Wave 1, TDD RED)
  └── tests/test_constants.py: 9 new test functions (import time failures)

Plan 2.1 (Wave 2, TDD GREEN)
  └── depends on 1.1 ✓
  └── constants.py: snake identity + SPECIES block
  └── Can run in parallel with Plan 2.2 ✓ (different files)

Plan 2.2 (Wave 2, TDD GREEN)
  └── depends on 1.1 ✓
  └── turtle_race.spec: datas edit
  └── assets/snakes/: git add
  └── Can run in parallel with Plan 2.1 ✓ (different files)

JOINT GATE:
  └── Plans 2.1 and 2.2 both complete
  └── pytest tests/test_constants.py → 12 passed
  └── pytest (full) → all green
```

**Dependency chain:** Sound. Plan 1.1 establishes the RED state. Plans 2.1 and 2.2 independently turn it GREEN. No circular dependencies, no missing dependencies, no micro-dependencies that force sequential execution within Wave 2.

**Ordering:** Wave 1 → Wave 2 is correct. Within Wave 2, 2.1 and 2.2 can execute in either order or in parallel. The plan explicitly documents the cross-plan gate: "re-run pytest once both Plan 2.1 and Plan 2.2 are merged."

---

## Phase 1 Requirements Coverage Matrix

| Requirement (from ROADMAP § Phase 1) | Addressed by | Evidence |
|---|---|---|
| `SNAKE_NAMES = ["Shadow", "Ralph", "Anaconda"]` | Plan 2.1 Task 1 | Exact constant block specified; test in Plan 1.1 Task 2 |
| `SNAKE_COLORS` with Shadow=black, Ralph=#E89F4F, Anaconda=green | Plan 2.1 Task 1 | Exact values from CONTEXT-1.md; test in Plan 1.1 Task 2 |
| `SNAKE_LENGTHS = [6, 2, 5]` positional | Plan 2.1 Task 1 | Exact list specified; name-keyed test in Plan 1.1 Task 2 prevents by-value confusion |
| `SNAKE_IMAGES` dict keyed by name with PNG paths | Plan 2.1 Task 1 | Exact dict specified; test in Plan 1.1 Task 2 checks key=names match and disk existence |
| `L_BASE` placeholder constant | Plan 2.1 Task 1 | Specified as 1.0 with comment noting Phase 4 tuning |
| `SPECIES` dict with "turtles" and "snakes" entries | Plan 2.1 Task 2 | Exact structure specified; 5 tests in Plan 1.1 Task 2 cover schema |
| `SPECIES[species]` required sub-keys: names, colors, images, bet_layout, shape_drawer | Plan 2.1 Task 2 + Plan 1.1 Task 2 (test_species_entries_have_required_sub_keys) | ✓ |
| `bet_layout` ∈ {"grid_2x2", "row_3"} | Plan 2.1 Task 2 + Plan 1.1 Task 2 (test_species_bet_layout_values_are_valid) | turtles="grid_2x2", snakes="row_3" ✓ |
| `shape_drawer` as STRING sentinel ("turtle"/"snake") per CONTEXT-1.md | Plan 2.1 Task 2 + Plan 1.1 Task 2 (test_species_shape_drawer_is_string_sentinel) | CONTEXT-1.md Decision 1 enforced by test ✓ |
| Racer counts: turtles=4, snakes=3 | Plan 2.1 Task 2 + Plan 1.1 Task 2 (test_species_racer_counts) | SPECIES references TURTLE_NAMES (4) and SNAKE_NAMES (3) ✓ |
| `turtle_race.spec` `datas=` includes `('assets/snakes/*.png', 'assets/snakes')` | Plan 2.2 Task 1 | Exact edit specified; Python verification command provided |
| Snake PNGs committed to git | Plan 2.2 Task 2 | git add for all three; git ls-files verification command provided |
| Tests covering all above invariants | Plan 1.1 Tasks 1–2 | 9 tests specified, matching ROADMAP § Phase 1 Task 1 and Task 3 requirements |
| `pytest tests/test_constants.py` green | Plan 2.1 Task 3 + Plan 2.2 Task 3 | Joint-green gate documented; expects 12 passed |
| `pytest` (full) green | Plan 2.1 Task 3 + Plan 2.2 Task 3 | Full suite verification included |
| `python -c "import constants; print(constants.SPECIES['snakes']['names'])"` → `['Shadow', 'Ralph', 'Anaconda']` | Plan 2.1 Task 2 | Concrete smoke test in acceptance criteria |

**Coverage verdict:** COMPLETE ✓

---

## Task Count and Scope

| Plan | Task Count | Limit | Status |
|---|---|---|---|
| Plan 1.1 | 3 (Extend imports & tests, Add SPECIES tests, Verify RED) | 3 | ✓ |
| Plan 2.1 | 3 (Snake identity block, SPECIES dict, Run tests) | 3 | ✓ |
| Plan 2.2 | 3 (Spec datas edit, git add, Joint-green verification) | 3 | ✓ |

All plans stay within the 3-task limit.

---

## Test Quality and Specificity

**Plan 1.1 test specifications:**
- Snake lists length test: exact assertion `len(SNAKE_NAMES) == len(SNAKE_COLORS) == len(SNAKE_LENGTHS) == 3` ✓
- Snake image map test: exact assertion `set(SNAKE_IMAGES.keys()) == set(SNAKE_NAMES)` ✓
- Snake lengths positional test: name-keyed assertion against `{"Shadow": 6, "Ralph": 2, "Anaconda": 5}` — defends against by-position vs. by-ratio confusion ✓
- Snake image files test: disk-check with manual project_root, mirrors existing turtle test ✓
- SPECIES shape tests (5 total): top-level keys, required sub-keys, bet_layout values, racer counts, shape_drawer string sentinel ✓

**Acceptance criteria:** Concrete and verifiable. Every task specifies commands that can be run and expected output/behavior.

---

## File Conflict Analysis

| File | Plan 1.1 | Plan 2.1 | Plan 2.2 | Conflict? |
|---|---|---|---|---|
| `tests/test_constants.py` | Modify | — | — | No |
| `constants.py` | — | Modify | — | No |
| `turtle_race.spec` | — | — | Modify | No |
| `assets/snakes/Shadow.png` | — | — | git add | No |
| `assets/snakes/Ralph.png` | — | — | git add | No |
| `assets/snakes/Anaconda.png` | — | — | git add | No |

**No conflicts between plans.** Plans 2.1 and 2.2 are safe to run in parallel.

---

## Risk Assessment

**Plan 1.1 (Wave 1, TDD RED):**
- Risk: LOW
- Rationale: Pure test additions; no code changes; no external dependencies; no assets; failure is intentional (RED state)

**Plan 2.1 (Wave 2, constants implementation):**
- Risk: LOW
- Rationale: Additive pure data; no imports; no behavioral changes; locked values from CONTEXT-1.md; spec-compliant

**Plan 2.2 (Wave 2, spec + git tracking):**
- Risk: LOW
- Rationale: Mechanical spec edit (glob tuple addition); existing assets already on disk; no code changes

**Cross-plan risk:**
- Circular import risk from accidentally wiring `race.py` into `constants.py`: Mitigated by CONTEXT-1.md Decision 1 (string sentinel) and Plan 1.1 test_species_shape_drawer_is_string_sentinel test that enforces this invariant ✓

**External assumptions:**
- Snake PNGs exist on disk at `assets/snakes/{Shadow,Ralph,Anaconda}.png` — RESEARCH.md section 6 confirms all three present as 1024×1024 RGBA PNGs ✓

---

## Wave Ordering and Test Gates

**Wave 1:** Plan 1.1 establishes RED state (tests fail at import time because constants don't exist).

**Wave 2 entry gate:** Plan 1.1 complete; pytest on test_constants.py must show ImportError on SNAKE_NAMES, SNAKE_COLORS, SNAKE_LENGTHS, SNAKE_IMAGES, SPECIES.

**Wave 2 execution:** Plans 2.1 and 2.2 can run in parallel. Both must complete for joint-green.

**Wave 2 exit gate:** 
- `pytest tests/test_constants.py` must show 12 passed
- `pytest` (full suite) must show no regressions
- `git ls-files assets/snakes/` must list all three PNGs
- `python -c "import constants; print(constants.SPECIES['snakes']['names'])"` must print `['Shadow', 'Ralph', 'Anaconda']`

---

## Verification Command Coverage

All plans include concrete, runnable verification commands:

**Plan 1.1:**
- `pytest tests/test_constants.py` (expect non-zero exit, ImportError message)
- `python -c "import ast; tree = ast.parse(...)"` (AST parse to verify function order)

**Plan 2.1:**
- `python -c "import constants; print(constants.SNAKE_NAMES, ...)"` (smoke test all constants)
- `python -c "import constants; print(constants.SPECIES['snakes']['names'])"` (ROADMAP success criterion)
- `python -c "import ast; print([n for n in ast.parse(...)])"` (verify zero imports)
- `pytest tests/test_constants.py` and `pytest` (full suite)

**Plan 2.2:**
- `python -c "import re; line = [l for l in open('turtle_race.spec')...]; print('assets/snakes/*.png' in line ...)"` (spec edit verification)
- `git ls-files assets/snakes/` (PNG tracking verification)
- `git cat-file -s :assets/snakes/Shadow.png` (non-empty file check)
- `pytest tests/test_constants.py` and `pytest` (full suite)

---

## Gaps and Observations

### Minor observation (not a gap):
- **Plan 2.1 cross-plan ordering note:** Plan 2.1 Task 3 observes that the 12-pass result depends on snake PNGs being on disk (which they are), so Plan 2.1 can pass its tests standalone. However, Plan 2.1 explicitly documents: "For the milestone-level 'fresh clone passes pytest' guarantee, Plan 2.2 must also land — re-run pytest once both Plan 2.1 and Plan 2.2 are merged." This is correct and explicitly called out in the plan. The joint-green gate is properly documented in both Plan 2.1 Task 3 and Plan 2.2 Task 3.

### No functional gaps identified.

---

## Final Verdict

**PASS** — All Phase 1 plans comprehensively cover the ROADMAP and PROJECT.md Phase 1 requirements. Task counts are within limits. Dependencies are correctly ordered. File conflicts are absent. Acceptance criteria are measurable and specific. Verification commands are concrete and runnable. The plans are ready for execution.

**Key strengths:**
1. Requirement traceability: Every ROADMAP requirement is explicitly addressed.
2. Test-first discipline: Plan 1.1 establishes invariants before implementation.
3. Cross-plan coordination: Plans 2.1 and 2.2 are properly scoped to execute in parallel with an explicit joint-green gate.
4. Circular import prevention: CONTEXT-1.md Decision 1 (string sentinel) is locked by a dedicated test.
5. Locked values: Ralph's hex (#E89F4F) and SNAKE_LENGTHS [6, 2, 5] from CONTEXT-1.md are embedded in the plans.
6. PyInstaller awareness: Plan 2.2 correctly identifies the non-recursive nature of the existing glob and adds the additive tuple.
7. Git and file handling: Plan 2.2 explicitly handles asset tracking and verification.

---

