---
phase: 5
plan: 1.1
wave: 1
reviewer: claude-sonnet-4-6
verdict: APPROVE
---

# REVIEW-1.1 — Phase 5 file edits (gitignore, test, docs)

## Pre-Check: Prior Findings

No `.shipyard/ISSUES.md` exists. No prior `REVIEW-*.md` files from this phase. No recurring patterns to escalate.

CRITIQUE.md flagged a scope expansion for CLAUDE.md: 3 fixes (snake polygon length, podium width, HEAD-at-start placement) rather than the 1 originally planned. SUMMARY-1.1 explicitly acknowledges this and claims all 3 were applied. Verified below.

---

## Stage 1: Spec Compliance

**Verdict: PASS**

### Task 1: .gitignore + Anaconda test + create_racers docstring

- Status: PASS
- Evidence:
  - `.gitignore` line 8: `assets/midi/` — trailing slash present, appended as the final line after `.vscode/launch.json` (line 7). Confirmed.
  - `tests/test_race.py` lines 110-119: `test_head_offset_arc_anaconda` is present, placed after the Ralph test (line 107 ends the Ralph block; Anaconda begins at line 110 after a blank line). The comment block (`# Note (no assertion):`) follows at line 122 — insertion order is correct.
  - Test body: `stretch_len = 1.2 * 5` (6.0), `head_offset_arc = SNAKE_UNIT_SIZE * stretch_len / 2`, asserts `abs(head_offset_arc - 60.0) < 1e-9`. Uses `SNAKE_UNIT_SIZE` which is module-level at line 21. Math is correct: 20 * 6.0 / 2 = 60.0. No new import required.
  - `race.py` lines 251-255: `Note:` block inserted immediately before closing `"""` at line 256. References `SNAKE_LENGTHS[i]`, `length_units`, Shadow=6, Ralph=2, Anaconda=5. Matches RESEARCH.md §2 verbatim structure.
- Notes: All three sub-tasks correct. Commit message matches plan.

### Task 2: PROJECT.md strikethrough + CLAUDE.md 3 fixes

- Status: PASS
- Evidence:
  - `.shipyard/PROJECT.md` lines 131-134: all four Open Items annotated. Ralph hex: `~~...~~ **RESOLVED:** \`#E89F4F\``. L_BASE: `~~...~~ **RESOLVED:** \`1.2\``. Classic vs polygon: `~~...~~ **RESOLVED:** custom Option 5 smooth-wave polygon registered as \`"snake"\``. Spiral: `**DEFERRED** per CONTEXT-5 Decision 1` (no strikethrough on the spiral item, which is correct — it was not resolved, only deferred).
  - CLAUDE.md line 62 (fix 1 — snake polygon length): "`_SHAPE_UNIT_SIZE` maps shape names to their natural length along the heading axis: `9` for `"classic"` and `"turtle"` shapes, `20` for the custom `"snake"` polygon (`_SNAKE_POLYGON_LENGTH = 20`)." Old "9 units long" claim gone.
  - CLAUDE.md line 64 (fix 2 — podium width): "just bump width to `3.0` for visibility." Old `2.0` claim gone.
  - CLAUDE.md line 62 (fix 3 — HEAD-at-start placement): "The helpers `_head_offset_arc_for(t)` and `_back_pos(...)` in `race.py` back each racer's center behind its lane-start point so the racer's HEAD sits precisely at the lane start position." All three CRITIQUE.md fixes confirmed in a single coherent paragraph.
- Notes: Scope expansion from CRITIQUE.md (3 fixes vs. 1) correctly applied. All 4 Open Items present with appropriate markup.

### Task 3: SHIP-NOTES.md creation

- Status: PASS
- Evidence:
  - `SHIP-NOTES.md` exists at project root.
  - All 6 required sections present: `## What Shipped` (line 3), `## Architecture Pointers` (line 14), `## Run / Test / Build` (line 24), `## Known Deferrals` (line 32), `## Snake Assets` (line 37), `## Future Work Suggestions` (line 41).
  - Cross-references CLAUDE.md rather than duplicating commands ("See CLAUDE.md for full command reference").
  - Length is approximately 1 page (49 lines total) — within scope.
- Notes: Section titles differ slightly from RESEARCH.md §5 (`Run / Test / Build` vs `Run/Test/Build`, `Future Work Suggestions` vs `Future Work`) but the semantic content matches exactly and the difference is cosmetic.

---

## Stage 2: Code Quality

### Critical

None.

### Important

None.

### Suggestions

- `tests/test_race.py` line 110: The Anaconda test is separated from the Ralph test block by a single blank line only, where the Shadow-to-Ralph transition uses two blank lines (between lines 95 and 98). This is a minor PEP 8 style inconsistency — top-level function definitions conventionally use two blank lines. The test runs correctly; this is cosmetic only.
  - Remediation: Add a second blank line before `def test_head_offset_arc_anaconda()` so the spacing matches the Shadow-to-Ralph gap above it.

---

## Summary

**Verdict: APPROVE**

All three tasks are correctly implemented: the `.gitignore` directory pattern is present, the Anaconda test is correctly inserted with right math and placement, the `create_racers` Note block matches the spec, PROJECT.md shows all four items with proper strikethrough/RESOLVED/DEFERRED annotations, all three CRITIQUE.md CLAUDE.md fixes landed in a single coherent paragraph (snake polygon size = 20, podium width = 3.0, HEAD-at-start helpers named), and SHIP-NOTES.md has all six required sections and defers to CLAUDE.md for commands.

Critical: 0 | Important: 0 | Suggestions: 1
