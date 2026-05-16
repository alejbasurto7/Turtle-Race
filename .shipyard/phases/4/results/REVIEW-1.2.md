---
plan: 1.2
phase: snakes-racer-mode
wave: 1
reviewer: claude-sonnet-4-6
verdict: APPROVE
---

# REVIEW-1.2 — Cleanups: dialogs.py imports + docstring, tracks.py loop rename

## Pre-Check: Prior Findings

No `.shipyard/ISSUES.md` exists. No prior REVIEW files for Phase 4. No recurring
patterns to escalate.

---

## Stage 1: Spec Compliance

**Verdict:** PASS

### Task 1: dialogs.py — drop stale imports + add get_user_species() docstring

- Status: PASS
- Evidence:
  - `dialogs.py` lines 7-10: import block reads
    `from constants import (BET_IMAGE_SIZE, SNAKE_IMAGES, SPECIES, SPECIES_DIALOG_IMAGE_SIZE,)`.
    `TURTLE_NAMES` and `TURTLE_IMAGES` are absent.
  - Grep for `TURTLE_NAMES|TURTLE_IMAGES` in `dialogs.py`: zero matches.
  - `BET_IMAGE_SIZE`, `SNAKE_IMAGES`, `SPECIES`, `SPECIES_DIALOG_IMAGE_SIZE` are
    all present in the import block and used in the function bodies — no orphaned
    imports introduced.
  - `get_user_species()` docstring (lines 195-203) contains: "Modal dialog",
    "grab_set()", "wait_window()", "WM_DELETE_WINDOW", `"turtles"`, `"snakes"`,
    and a Returns annotation mapping to `constants.SPECIES`. Matches the plan's
    done criteria verbatim.
- Notes: Commit is clean; no body code changed — only the import line and the
  docstring were touched. The no-op WM_DELETE_WINDOW handler at line 209
  (body) correctly documents the guard already in place.

### Task 2: tracks.py — rename loop variable n → leg_i in _build_spiral_legs

- Status: PASS
- Evidence:
  - `tracks.py` lines 195-202: `for leg_i in range(max_legs):`, `pair_idx = leg_i // 2`,
    `leg_i % 2 == 0`, `headings[leg_i % 4]` — all four in-loop references
    converted.
  - Grep for `for n in range` in `tracks.py`: zero matches.
  - Grep for bare `\bn\b` inside `_build_spiral_legs` (lines 185-203): zero
    matches inside the function body; all remaining `n` tokens in the file are
    on other public functions that use `n` as the lane-count parameter — no
    cross-contamination.
  - SUMMARY confirms `_build_spiral_legs` has no `n` parameter in its signature
    (`w, h, step, max_pairs, max_legs`) — rename was safe and behaviorally inert.
- Notes: Exactly four lines changed as reported. The outer-scope lane-count `n`
  in callers (`_spiral_lane`, `_spiral_pair_cap`, etc.) is untouched and correct.

### Integration checks (Stage 2 spec items)

- `constants.py` and `tests/test_constants.py` — neither file was touched by
  commits 612faf5 or ea47c30. PLAN-1.1 parallelism constraint satisfied.
- pytest reported 79/79 at the end of both tasks.

---

## Stage 2: Code Quality

### Critical

None.

### Important

None.

### Suggestions

None.

---

## Summary

**Verdict:** APPROVE

Both commits implement exactly what the plan specified. The stale imports are
gone, the docstring matches the locked spec text, and the loop-variable rename
is complete with zero residual `n` references inside `_build_spiral_legs`. No
regressions were introduced and no PLAN-1.1 files were touched.

Critical: 0 | Important: 0 | Suggestions: 0
