# Simplification Report — Phase 1

## Verdict: LOW_PRIORITY

One trivial finding, non-blocking. No action required before shipping Phase 1.

## High Priority

None.

## Medium Priority

None.

## Low Priority

### Duplicated `project_root` derivation in two test functions

- **Type:** Consolidate
- **Effort:** Trivial
- **Locations:** `tests/test_constants.py:17`, `tests/test_constants.py:44`
- **Description:** `project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` is copied verbatim in `test_image_files_exist_on_disk` (line 17) and `test_snake_image_files_exist_on_disk` (line 44). Two occurrences sits just below the Rule-of-Three threshold for extraction.
- **Suggestion:** Lift to a module-level `PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` after the `sys.path.insert` block; reference in both tests. If Phase 2 adds a third disk-existence test (e.g., track-preview images), this becomes necessary — doing it now is zero-risk.

## Summary

- Duplication: 1 instance (2 occurrences)
- Dead code: 0 — `L_BASE = 1.0` is a documented Phase 4 placeholder, not dead
- Complexity hotspots: 0
- AI bloat: 0 — concise assertion messages, no redundant type checks, no over-engineering
- Spec glob check: the new `('assets/snakes/*.png', 'assets/snakes')` is correct and necessary; `*.png` does not recurse into subdirectories
- Cleanup impact: 1 line refactor (net zero, removes duplication)

## Recommendation

Non-blocking. Either consolidate now (~30s of work) or defer until Phase 2 adds a third asset-existence test. Shipyard's TDD gate is green either way.
