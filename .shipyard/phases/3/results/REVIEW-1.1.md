---
phase: 3-snake-species
plan: 1.1
wave: 1
reviewer: claude-sonnet-4-6
verdict: PASS
---

# REVIEW-1.1 — Phase 3 Wave 1

## Stage 1: Spec Compliance

**Verdict: PASS**

All three tasks are correctly implemented. One minor spec deviation noted (import omission) that has no runtime consequence, recorded below.

---

### Task 1: Add `SPECIES_DIALOG_IMAGE_SIZE` constant + TDD test
- **Status: PASS**
- **Evidence:**
  - `constants.py:25-26` — `BET_IMAGE_SIZE = 140` on line 25, `SPECIES_DIALOG_IMAGE_SIZE = 200  # px, square — used by the species-selection dialog (composite images)` on line 26, directly below as required.
  - `tests/test_constants.py:31-34` — `test_species_dialog_image_size_is_positive_int` present, mirrors `test_bet_image_size_is_positive_int` in style, and correctly adds the `>= BET_IMAGE_SIZE` assertion specified in the task action.
  - `tests/test_constants.py:7-10` — import line updated to include `SPECIES_DIALOG_IMAGE_SIZE`.
- **Notes:** TDD discipline confirmed by SUMMARY (failing import error first, constant added second). Test is strictly stronger than the baseline `test_bet_image_size_is_positive_int` by adding the `>= BET_IMAGE_SIZE` relational assertion — matches spec. No issues.

---

### Task 2: Hoist layout constants to module-level `_TURTLE_GRID_LAYOUT` / `_SNAKE_ROW_LAYOUT`
- **Status: PASS**
- **Evidence:**
  - `dialogs.py:16-21` — `_TURTLE_GRID_LAYOUT` is module-level, four entries: Leonardo (1,0), Donatello (1,1), Raphael (2,0), Michaelangelo (2,1). Placed directly after the import block.
  - `dialogs.py:24-28` — `_SNAKE_ROW_LAYOUT` is module-level beside it: Shadow (1,0), Ralph (1,1), Anaconda (1,2). Order matches `SNAKE_NAMES` exactly.
  - `dialogs.py:73` — `get_user_bet` body references `_TURTLE_GRID_LAYOUT` (used in Task 3's refactored form; the pure-extract pre-Task-3 state would have also referenced it).
  - Spelling: "Michaelangelo" in `_TURTLE_GRID_LAYOUT:20` matches the intentional codebase spelling in `constants.py:9` (`TURTLE_NAMES`) and `constants.py:22` (`TURTLE_IMAGES` key). No drift.
- **Minor deviation:** The plan's Task 2 action states: "the existing `from constants import ...` block **which must be extended to also import `SPECIES`, `SNAKE_NAMES`, `SNAKE_IMAGES`**." The import at `dialogs.py:7-10` imports `SNAKE_IMAGES`, `SPECIES`, and `SPECIES_DIALOG_IMAGE_SIZE` but does **not** import `SNAKE_NAMES`. `SNAKE_NAMES` is referenced only in a comment (`dialogs.py:23`). Since `_SNAKE_ROW_LAYOUT` hardcodes names as string literals, `SNAKE_NAMES` is not needed at runtime and the omission has zero functional impact. Recorded as a minor spec deviation, not blocking.

---

### Task 3: Refactor `get_user_bet()` → `get_user_bet(species)` with if/elif dispatch
- **Status: PASS**
- **Evidence:**
  - `dialogs.py:31` — signature is `def get_user_bet(species):`. Positional arg, not kwarg-only. Wave 2 readiness confirmed.
  - `dialogs.py:43-45` — reads `bet_layout`, `species_names`, `species_images` from `SPECIES[species]`.
  - `dialogs.py:55` — `dialog._bet_images = []` initialized before the if/elif. Both branches append to the same list. No typo or drift.
  - `dialogs.py:57-61` — `make_cb` closure defined once before the if/elif (shared by both branches — CONTEXT-3 G3 mitigation noted in SUMMARY).
  - `dialogs.py:63-90` — `"grid_2x2"` branch: title "Turtle Racing", label "Which turtle do you think will win the race?", `columnspan=2`, iterates `_TURTLE_GRID_LAYOUT`, image source `species_images[name]`, resize to `BET_IMAGE_SIZE`, bet index `species_names.index(name) + 1`. Matches spec.
  - `dialogs.py:92-119` — `"row_3"` branch: title "Snake Racing", label "Which snake do you think will win the race?", `columnspan=3`, iterates `_SNAKE_ROW_LAYOUT`, same PIL pipeline and `BET_IMAGE_SIZE`. Bet index same convention. Matches spec.
  - `dialogs.py:121-122` — `else: raise ValueError(f"Unknown bet_layout: {bet_layout!r}")`. Present.
  - `dialogs.py:124-132` — centering block shared after both branches (not duplicated). Correct.
  - `dialogs.py:131-132` — `grab_set()` then `wait_window()` after both branches. Tk modal correctness preserved.
  - `dialogs.py:49-51` — `Toplevel()`, `resizable(False, False)`, `WM_DELETE_WINDOW` no-op all present before the if/elif. Correct.
  - `dialogs.py:134` — returns `selected[0]`. Correct.
  - Total function length: lines 31-134 = ~104 lines including docstring. Within ~110 line target.
  - CONTEXT-3 Decision 2 honored: no helper extracted; single function with internal branching.
- **Notes:** Docstring added voluntarily at lines 32-42 (not required by plan). This is a net positive — documents the `species` arg, return value, and `ValueError`. The `SPECIES_DIALOG_IMAGE_SIZE` is imported at `dialogs.py:9` even though it is not yet used in this plan's scope — this is forward-looking and harmless; Wave 2 will use it for `get_user_species`.

---

## Stage 2: Integration Review

### Intentional `main.py` runtime breakage
- **Confirmed.** `main.py:34` reads `user_bet = dialogs.get_user_bet()` — zero arguments. After the Task 3 refactor this produces `TypeError: get_user_bet() missing 1 required positional argument: 'species'` at runtime, exactly as specified. PLAN-2.1 fixes this. No surprise.

### pytest green
- SUMMARY confirms 76 → 77 tests green across all three commits. The new test `test_species_dialog_image_size_is_positive_int` is the only addition. Consistent with the plan's done criteria.

### No regression in turtle bet dialog logic
- The `"grid_2x2"` branch is semantically equivalent to the pre-refactor `get_user_bet()`: same layout constant (now named `_TURTLE_GRID_LAYOUT`), same image source, same resize, same Tk modal pattern, same 1-based index. No regression risk.

### Wave 2 readiness
- `dialogs.get_user_bet` accepts exactly one positional parameter `species`. PLAN-2.1 can call `dialogs.get_user_bet(species)` without any further signature change.

### Conventions
- 4-space indentation throughout. Blank lines between functions. Comment style matches existing `get_user_track`. No style regressions observed.

### `dialog._bet_images` integrity
- Initialized as `[]` at `dialogs.py:55`, before the if/elif. Both branches call `.append(photo)` in their loop. The reference list is on the `dialog` object, consistent with the existing `dialog._track_images` pattern in `get_user_track`. No garbage-collection risk.

---

## Findings

### Critical
None.

### Minor
- **`SNAKE_NAMES` not imported in `dialogs.py`** (`dialogs.py:7-10`)
  - The plan's Task 2 action explicitly required extending the import to include `SNAKE_NAMES` alongside `SPECIES` and `SNAKE_IMAGES`. It is absent. The comment on line 23 references `SNAKE_NAMES` by name, which creates a minor documentation/intent mismatch. The omission has zero runtime impact because the names are hardcoded as string literals in `_SNAKE_ROW_LAYOUT`.
  - Remediation: Add `SNAKE_NAMES` to the import on line 7-10. This satisfies the spec and makes the layout's ordering intent verifiable at import time (e.g., future test could assert `[t[0] for t in _SNAKE_ROW_LAYOUT] == SNAKE_NAMES`).

### Positive Observations
- `make_cb` closure hoisted before if/elif is a clean G3 mitigation — avoids late-binding issues without duplicating the closure in each branch.
- Voluntary docstring on `get_user_bet(species)` is immediately useful to Wave 2's builder.
- `SPECIES_DIALOG_IMAGE_SIZE` imported in `dialogs.py` even though unused in Wave 1 — reduces the diff size for Wave 2's `get_user_species` addition.
- Centering block and modal setup (`grab_set` + `wait_window`) correctly placed after the if/elif rather than duplicated inside each branch — reduces risk of future divergence.
- "Michaelangelo" spelling faithfully preserved, with no drift to the common "Michelangelo" spelling.

---

## Summary

**Verdict: PASS — APPROVE**

All three tasks are correctly implemented and match the spec. The sole deviation (missing `SNAKE_NAMES` import) is a Minor finding with zero functional impact; it can be added opportunistically in PLAN-2.1 when `dialogs.py` is touched again. The intentional `main.py` runtime breakage is confirmed and expected. The implementation is Wave 2 ready.

Critical: 0 | Minor: 1 | Positive: 5
