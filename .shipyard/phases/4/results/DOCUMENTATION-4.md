# Documentation Report
**Phase:** snakes-racer-mode / Phase 4
**Verdict:** MINOR_GAPS

---

## Summary

- API/Code docs: 2 new public functions documented inline (draw_turtle_shape, draw_snake_shape); 1 private dispatch table commented; head_offset_progress block documented inline. All inline coverage is good.
- Architecture updates: CLAUDE.md needs one targeted addition (see below). No new file required.
- User-facing docs: no user-facing changes in this phase.

---

## API Documentation

### `draw_turtle_shape(t)` — `race.py:135`
- **Type:** Reference
- **Status:** Complete. Docstring present, explains the color-deferral contract correctly. No gaps.

### `draw_snake_shape(t, length_units)` — `race.py:144`
- **Type:** Reference
- **Status:** Complete. Docstring documents both shapesize parameters, the 6:5:2 visual ratio, the ~32 px Shadow estimate, and the PHASE-4-PLACEHOLDER escalation path. No gaps.

### `_SHAPE_DRAWERS` dispatch table — `race.py:168`
- **Type:** Reference (internal)
- **Status:** Complete. The one-line comment above the dict ("Resolves the string sentinel in SPECIES[species]['shape_drawer'] to a callable. Keyed by the same string values used in constants.SPECIES.") is exactly sufficient. No gaps.

### `head_offset_progress` block — `run_race()`, `race.py:240–269`
- **Type:** Explanation (inline)
- **Status:** Complete. The 14-line comment block covers: the fairness rationale, the formula from RESEARCH.md §2 Approach B, the shape_unit_size=9 calibration and its turtle-approximation caveat, the clamp/guard interaction, and a reference to CRITIQUE.md. Commit f810a69 asked whether this was sufficient — it is. No additional prose needed.

### `create_racers` species-branch — `race.py:191–200`
- **Type:** Reference
- **Status:** Minor gap (see CLAUDE.md section below). The function-level docstring was not updated to mention the `length_units` branching. Because the function is internal-ish and the docstring already describes the racer dict contract accurately, this is low priority. However CLAUDE.md is the right place to capture the dispatch invariant for future contributors.

### `announce_result` / `celebrate` identity refactor — `race.py:455, 478`
- **Type:** Reference
- **Status:** Complete. Inline comments explain the hex-pencolor round-trip caveat where color strings are read from the racer dict. This is consistent with the existing CLAUDE.md "Hex pencolor caveat" note.

---

## Architecture Updates

### CLAUDE.md — "Racer identity is positional, and species-dispatched"

- **Type:** Explanation
- **Current state:** The section documents SPECIES, shape_drawer as a string sentinel, bet indexing, SNAKE_LENGTHS positional invariant, and the hex pencolor caveat. It does NOT mention shape dispatch or head-offset finish detection.
- **Gap:** Phase 4 made shape dispatch and universal head-position finish detection the permanent design. A future contributor adding a third species or tuning snake lengths needs to know: (a) `_SHAPE_DRAWERS` is the extension point, not `create_racers`; (b) head-offset is derived from `shapesize()[1]` at race start, so it is automatically correct for any shape configured via the dispatch table.
- **Recommendation:** Add a short paragraph to the existing section. Proposed text (append after the `shape_drawer` bullet):

  > **Shape dispatch and finish detection:** `race._SHAPE_DRAWERS` maps each `shape_drawer` sentinel to its callable. To add a third species, register its drawer there — do not branch in `create_racers`. Head-position finish detection reads each racer's `shapesize()[1]` (stretch_len) after placement, so it adapts automatically to any shape registered through the dispatch table; no separate constant is needed.

- **File to edit:** `C:\Users\T0226129\PyCharmProjects\Turtle Race\CLAUDE.md`
- **Target location:** After the `shape_drawer` bullet on line 52, before the `Bet indexing` bullet on line 53.

---

## User Documentation

No user-facing changes in Phase 4 (no new dialogs, no tutorial impact). No updates required.

---

## Gaps

### Gap 1 (MINOR) — CLAUDE.md missing shape-dispatch extension point
**Severity:** Minor. Existing docs are not wrong; they just don't describe the dispatch table or the automatic head-offset adaptation.
**Action:** Apply the paragraph above to CLAUDE.md, "Racer identity" section.

### Gap 2 (INFORMATIONAL) — `create_racers` docstring silent on length_units branch
**Severity:** Informational. The `species == "snakes"` branch that passes `SNAKE_LENGTHS[i]` to the drawer is not reflected in the docstring. This is acceptable because the docstring correctly describes the return contract, and the branching logic is a one-liner readable in-context. Worth noting if the function ever grows a third species branch.
**Action:** No immediate action required.

---

## Notes on Verified Coverage

Code examples in this phase are all internal race-loop logic with Tk/turtle dependencies; they cannot be run in isolation. All docstring examples and formula references have been checked against the diff and SUMMARY files for accuracy rather than execution.
