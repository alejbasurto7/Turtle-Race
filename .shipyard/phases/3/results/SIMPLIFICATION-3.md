# Simplification Report — Phase 3

## Verdict: LOW_PRIORITY

Phase 3 added one new dialog + refactored another; the diff is mostly additive UI plumbing. CONTEXT-3 Decision 2 explicitly forbids extracting a shared dialog helper. A handful of small items found; nothing blocking.

## High Priority

None.

## Medium Priority

### S3.1 — Stale imports in `dialogs.py` after refactor

- **Locations:** `dialogs.py:8` — `from constants import TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE, SPECIES, SPECIES_DIALOG_IMAGE_SIZE`
- **Description:** After the Wave 1 refactor, `TURTLE_NAMES` and `TURTLE_IMAGES` are no longer used directly in `dialogs.py` — `_TURTLE_GRID_LAYOUT` hardcodes names as literals, and `SPECIES["turtles"]["images"]` is accessed via the dict. `flake8 F401` would flag these.
- **Suggestion:** Drop both from the import line. While editing, **add** `SNAKE_NAMES` for symmetry (currently the layout literals work because `_SNAKE_ROW_LAYOUT` hardcodes them, but importing makes the relationship explicit).
- **Effort:** Trivial (one line). Pair with Phase 4's `dialogs.py` touches for snake-shape work.

## Low Priority

### S3.2 — Composite-image generation has minor inline duplication

- **Location:** inside `get_user_species()` in `dialogs.py`
- **Description:** The turtle 2×2 composite and snake 1×3 composite share the inner pattern of (open, convert RGBA, resize cell, paste with alpha mask). Both could be a small private helper `_compose_grid(image_paths, rows, cols, total_size)` returning a PIL.Image.
- **Trade-off:** CONTEXT-3 Decision 2 forbids the larger dialog-helper extraction but doesn't speak to a small private helper *within* `get_user_species`. The user's call was about helper-vs-parallel **between dialogs**, not within. A `_compose_grid` helper inside the module is consistent with the intent.
- **Suggestion:** Optional. If `get_user_species()` is ever touched again (e.g., to swap composite images or tune sizes), fold this in. Don't pre-emptively refactor for two call sites.
- **Effort:** Low-medium (~20 lines, one new helper).

### S3.3 — `get_user_bet(species)` if/elif branches share Tk setup

- **Location:** `dialogs.py:31`+ (the refactored `get_user_bet`)
- **Description:** Both `"grid_2x2"` and `"row_3"` branches construct the dialog, the title label, the image-ref list, and the centering boilerplate. Only the button placement loop differs.
- **Trade-off:** Could be restructured as "common pre-setup → per-layout button loop → common post-setup" to remove the duplication. This was CONTEXT-3 Decision 3's "internal branching" approach taken to its logical conclusion.
- **Suggestion:** Optional. The current branching is fine and readable. If Phase 4 adds anything mode-specific to the bet dialog (it shouldn't), revisit.
- **Effort:** Low.

## Notes on already-flagged items (NOT re-flagged as new)

- `_build_spiral_legs` loop variable `n` shadow in `tracks.py` (pre-Phase 1 carry; still unaddressed; queue for Phase 4 cleanup)
- `main.py:38` `pencolor()` win-check fragility (pre-Phase 2 carry; queue for Phase 4 cleanup)

Neither got worse this phase.

## AI bloat / dead code / complexity hotspots

- **AI bloat:** None detected. Docstrings are concise and accurate; assertions/exceptions don't over-explain.
- **Dead code:** Stale imports flagged as S3.1. Otherwise none — `_TURTLE_GRID_LAYOUT` and `_SNAKE_ROW_LAYOUT` are both read by `get_user_bet`.
- **Complexity:** None. `get_user_species` is ~80 lines including composite generation — appropriate for what it does. `get_user_bet(species)` is ~100 lines and was at ~80 before, growth proportional to the new species path.

## Summary

- Cross-task duplication: 1 medium (stale imports — already flagged in REVIEW-2.1)
- Inline duplication: 2 low (composite generation S3.2, bet dialog setup S3.3) — both deferrable
- Dead code: covered by S3.1
- AI bloat: 0
- Pre-existing carries: 2 (no worsening)

## Recommendation

Non-blocking. **Fold S3.1 into the first Phase 4 commit that touches `dialogs.py`** (likely the imports diff anyway). Skip S3.2 and S3.3 unless Phase 4 has a reason to revisit those functions.
