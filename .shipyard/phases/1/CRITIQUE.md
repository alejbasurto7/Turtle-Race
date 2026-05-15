# Phase 1 Plan Critique — Feasibility Stress Test

## Verdict: **READY**

All three plans are feasible against the current codebase state. No blocking issues. One minor cosmetic redundancy noted (informational only).

## Per-plan findings

### PLAN-1.1 — TDD red, test scaffolding

- **File paths:** `tests/test_constants.py` exists ✓
- **API surface:** existing imports (`TURTLE_NAMES`, `TURTLE_IMAGES`, `BET_IMAGE_SIZE`) verified present in `constants.py`. Import-extension approach is correct.
- **Verify commands:** `pytest tests/test_constants.py` is runnable; the `ast.parse` smoke test is syntactically valid Python.
- **Failure-mode prediction accuracy:** Task 1 / line 61 correctly notes that `test_snake_image_files_exist_on_disk` will pass as soon as constants are defined (the PNGs are physically present on disk regardless of git status). The "all tests fail at import time" framing is also correct because the new import line is shared across all 9 new tests — Python's import-error cascades collection failure. Both statements are consistent.
- **Complexity:** 1 file touched. Low.

### PLAN-2.1 — Implement constants and SPECIES

- **File paths:** `constants.py` exists ✓; line 25 (`BET_IMAGE_SIZE`) and line 27 (`# Track layout`) confirmed as the correct insertion bracket.
- **API surface:** the symbols `TURTLE_NAMES`, `TURTLE_COLORS`, `TURTLE_IMAGES` referenced by `SPECIES["turtles"]` all exist in `constants.py` above the proposed insertion point — `SPECIES`'s definition order is sound.
- **No circular import:** plan correctly forbids `from race import …` in `constants.py`. Task 1 acceptance criterion verifies via `ast.parse` that the import list stays empty.
- **Verify commands:** all `python -c …` commands and `pytest` invocations are runnable.
- **`L_BASE` placeholder:** correctly typed as `float` (`1.0`), not constrained by tests in Phase 1.
- **Complexity:** 1 file touched. Low.

### PLAN-2.2 — Register PNGs in spec + git-add assets

- **File paths:** `turtle_race.spec` exists, line 7 has the `datas=` list confirmed by `grep`. The three snake PNGs exist on disk.
- **API surface:** spec syntax pattern verified — existing tuples use `(source_glob, destination_folder)`; the new tuple matches.
- **Verify commands:** the `python -c` one-liner reading the `datas=` line is runnable. `git ls-files`, `git cat-file -s` are standard git commands.
- **No path-resolution mismatch:** destination `'assets/snakes'` matches the path prefix `"assets/snakes/"` in `SNAKE_IMAGES` from Plan 2.1.
- **Complexity:** 1 file edited + 3 files git-added. Low.

## Cross-plan analysis

### Forward references — none

- Wave 2 plans (2.1, 2.2) touch disjoint files: `constants.py` vs. `turtle_race.spec` + `assets/snakes/*.png`. No shared file edits.
- Neither plan depends on the other's output during its own task execution. The only shared artifact is the test suite — which depends on **both** for full GREEN.

### Hidden dependencies

- **Test-suite gating:** Both Plan 2.1's Task 3 and Plan 2.2's Task 3 run the full pytest suite. If they execute in parallel, both runs happen concurrently — that's fine (pytest doesn't share state), but it's redundant.
  - **Mitigation (informational, not blocking):** Acceptable as-is. The redundancy provides a sanity check at both completion points; cost is one extra pytest run.
- **`test_snake_image_files_exist_on_disk` interaction:** This test passes whenever the PNGs are physically on disk, regardless of git status. Since the PNGs are present locally now, both plans' test-suite gates will pass on the current developer machine before Plan 2.2 git-adds them. The git-add is for fresh-clone durability, not local test passage. Both plans correctly call this out in their cross-plan ordering notes.

### Complexity flags

- No plan touches >10 files or crosses >3 directories.
- Total files modified across Phase 1: 3 (`constants.py`, `tests/test_constants.py`, `turtle_race.spec`). Total files added: 3 (the PNGs).
- No I/O, no network, no external deps.

### Wave ordering

- Wave 1 (1.1) → Wave 2 (2.1, 2.2). Correct dependency chain. Plan 1.1 produces failing tests that Wave 2 turns green; Plan 1.1 is a hard prerequisite for Wave 2.

## Items to be aware of (not blocking)

1. **Redundant pytest invocation** between Plan 2.1 Task 3 and Plan 2.2 Task 3. Both running the full suite is harmless; could be consolidated into a single post-wave gate, but the current structure is defensible (each plan has a self-contained verification).
2. **Plan 2.1 Task 1 acceptance criterion** asserts `[]` for `constants.py` imports via `ast.parse`. The criterion is correct *as stated* but Phase 2's `race.py` refactor may someday introduce typing imports here — the test in `tests/test_constants.py` does not enforce this beyond Phase 1. The acceptance criterion is for the builder's sanity check during Phase 1 only.
3. **Phase 1 does not test `L_BASE`** beyond ensuring it exists with a numeric type. Per RESEARCH.md, this is correct — value tuning is Phase 4's job. Confirmed acceptable.

## Summary

Phase 1 plans are READY to execute. Risk level uniformly low across all three plans. Total work scope: 3 file edits + 3 file additions + ~9 new tests, executable in well under an hour. Recommend proceeding to `/shipyard:build 1`.
