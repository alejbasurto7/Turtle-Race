# Documentation Report
**Phase:** 5 — Documentation closure (CLAUDE.md fixes, PROJECT.md cleanup, SHIP-NOTES.md, create_racers docstring)

## Summary
- API/Code docs: 1 function docstring extended (`create_racers`)
- Architecture updates: 3 corrections applied to CLAUDE.md
- User-facing docs: 1 milestone summary created (SHIP-NOTES.md), 1 open-items list updated (PROJECT.md)

---

## API Documentation

### `create_racers` (`race.py`)
- **File:** race.py, line 234
- **Type:** Reference
- **Public interfaces:** 1
- **Status:** Extended

The docstring now covers the species branch. The Note block accurately describes the
`SNAKE_LENGTHS[i]` dispatch (`Shadow=6, Ralph=2, Anaconda=5`) and the absence of an
extra argument for the turtle branch. Verified against the actual dispatch at lines
262–264:

```python
if species == "snakes":
    drawer(t, SNAKE_LENGTHS[i])
else:
    drawer(t)
```

No drift detected between docstring and implementation.

---

## Architecture Updates

### CLAUDE.md — Three corrections applied
- **File:** CLAUDE.md
- **Type:** Explanation
- **Status:** Updated

**Fix 1 — `_SHAPE_UNIT_SIZE` is a dict, not a scalar.**
CLAUDE.md now reads: "`_SHAPE_UNIT_SIZE` maps shape names to their natural length along
the heading axis: `9` for `"classic"` and `"turtle"` shapes, `20` for the custom
`"snake"` polygon (`_SNAKE_POLYGON_LENGTH = 20`)."
Verified: `race.py` line 201–204 defines the dict with exactly these keys and values.

**Fix 2 — Podium snake width corrected from `2.0` to `3.0`.**
CLAUDE.md now reads: "snakes preserve their race-time `stretch_len` … and just bump
width to `3.0` for visibility."
Verified: `race.py` line 488 calls `shapesize(stretch_wid=3.0, ...)`.

**Fix 3 — HEAD-at-start placement helpers noted.**
CLAUDE.md now names `_head_offset_arc_for(t)` and `_back_pos(...)` and their role.
Verified: both helpers exist at `race.py` lines 209–225.

**Minor stale comment in source (out of scope):**
`race.py` line 200 has an inline comment "the custom snake polygon is 18 units long"
but `_SNAKE_POLYGON_LENGTH = 20`. This is a source-code comment — not editable by the
documentation agent — and does not affect any documentation file. Flagged for the next
code review pass.

---

## User Documentation

### PROJECT.md Open Items
- **File:** .shipyard/PROJECT.md, lines 131–134
- **Type:** How-to (reference for contributors)
- **Status:** Updated

All four open items are annotated:
- Three resolved with strikethrough + **RESOLVED:** and concrete values (`#E89F4F`,
  `1.2`, custom `"snake"` polygon).
- Spiral geometry item marked **DEFERRED** per CONTEXT-5 Decision 1.

### SHIP-NOTES.md
- **File:** SHIP-NOTES.md (project root)
- **Type:** Explanation (milestone summary)
- **Status:** Created

Six sections present: What Shipped, Architecture Pointers, Run/Test/Build, Known
Deferrals, Snake Assets, Future Work Suggestions. Content is accurate and consistent
with CLAUDE.md. The test count (`85/85`) matches the verified pytest output in
SUMMARY-2.1.md.

---

## Gaps

**NO_GAPS.** All documentation targets from CONTEXT-5 were delivered:

| Target                                      | Delivered |
|---------------------------------------------|-----------|
| CLAUDE.md `_SHAPE_UNIT_SIZE` dict fix        | Yes       |
| CLAUDE.md podium width `2.0 → 3.0` fix      | Yes       |
| CLAUDE.md `_head_offset_arc_for/_back_pos`  | Yes       |
| PROJECT.md Open Items annotated             | Yes       |
| SHIP-NOTES.md created                       | Yes       |
| `create_racers` docstring Note block        | Yes       |
| Anaconda test added (`test_head_offset_arc_anaconda`) | Yes (85/85) |

One non-blocking code comment drift exists in `race.py` line 200 ("18 units" vs
actual 20). Not a documentation file issue; no documentation remediation required.
