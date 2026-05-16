---
phase: 5
plan: 1.1
wave: 1
dependencies: []
must_haves:
  - Append `assets/midi/` to .gitignore
  - Insert Anaconda head_offset_arc test (asserts 60.0) in tests/test_race.py
  - Extend create_racers docstring in race.py with snake length_units Note block
  - Strikethrough resolved Open Items in .shipyard/PROJECT.md with RESOLVED/DEFERRED annotations
  - Fix CLAUDE.md line 62 _SHAPE_UNIT_SIZE description (snake is 20, not 9)
  - Create SHIP-NOTES.md at project root per RESEARCH.md §5 structure
files_touched:
  - .gitignore
  - tests/test_race.py
  - race.py
  - .shipyard/PROJECT.md
  - CLAUDE.md
  - SHIP-NOTES.md
tdd: false
risk: low
---

# PLAN-1.1 — Phase 5 file edits (gitignore, test, docs)

Six small file changes grouped into 3 atomic-commit-sized tasks. All paths are disjoint within a task, but Task 1 covers the only test addition (Anaconda) and the only behavioral docstring touch; Tasks 2 and 3 are pure documentation polish.

Reference: `.shipyard/phases/5/RESEARCH.md` for exact insertion points, line numbers, and verbatim content.

<task id="1" files=".gitignore, tests/test_race.py, race.py" tdd="false">
  <action>
    1. Append `assets/midi/` (with trailing slash) as a new line after line 7 of `.gitignore`.
    2. In `tests/test_race.py`, insert the `test_head_offset_arc_anaconda` function after the Ralph test (after line 107, before the comment block at line 109). Use the exact body from RESEARCH.md §3 — asserts `head_offset_arc == 60.0` using `SNAKE_UNIT_SIZE` (already imported at module top).
    3. In `race.py`, extend the `create_racers` docstring (currently ends at line 249) by inserting the `Note:` block from RESEARCH.md §2 immediately before the closing `"""`. The Note documents the `species == "snakes"` branch passing `SNAKE_LENGTHS[i]` to the drawer.
    Commit with message `Phase 5: gitignore assets/midi, add Anaconda test, extend create_racers docstring`.
  </action>
  <verify>git diff --stat .gitignore tests/test_race.py race.py; pytest tests/test_race.py -q</verify>
  <done>`.gitignore` contains `assets/midi/`. `pytest tests/test_race.py` passes including `test_head_offset_arc_anaconda`. `race.py` docstring contains the `Note:` block referencing `SNAKE_LENGTHS[i]`.</done>
</task>

<task id="2" files=".shipyard/PROJECT.md, CLAUDE.md" tdd="false">
  <action>
    1. In `.shipyard/PROJECT.md` Open Items section (lines 129-134 per RESEARCH.md §6), apply strikethrough (`~~text~~`) plus inline status annotations:
       - Ralph hex → RESOLVED: `#E89F4F`
       - L_BASE concrete value → RESOLVED: `1.2`
       - Classic vs polygon → RESOLVED: custom Option 5 smooth-wave polygon registered as `"snake"`
       - Spiral 3-lane visual-tuning → DEFERRED per CONTEXT-5 Decision 1
       Preserve original line history; do not delete the items.
    2. Fix `CLAUDE.md` line 62: replace the incorrect "`_SHAPE_UNIT_SIZE = 9` ... snake polygon (which is also 9 units long)" wording with the corrected description from RESEARCH.md §7: `_SHAPE_UNIT_SIZE` maps shape names to natural length along heading — `9` for `"classic"`/`"turtle"`, `20` for `"snake"` (`_SNAKE_POLYGON_LENGTH = 20`).
    Commit with message `Phase 5: PROJECT.md Open Items cleanup, CLAUDE.md _SHAPE_UNIT_SIZE fix`.
  </action>
  <verify>git diff --stat .shipyard/PROJECT.md CLAUDE.md</verify>
  <done>PROJECT.md Open Items show strikethrough + RESOLVED/DEFERRED annotations for all 4 items. CLAUDE.md line 62 (or near it) describes snake polygon length as 20, not 9.</done>
</task>

<task id="3" files="SHIP-NOTES.md" tdd="false">
  <action>Create `SHIP-NOTES.md` at the project root using the structure from RESEARCH.md §5 verbatim (sections: What Shipped, Architecture Pointers, Run / Test / Build, Known Deferrals, Snake Assets, Future Work Suggestions). Cross-reference CLAUDE.md for commands rather than duplicating. Commit with message `Phase 5: add SHIP-NOTES.md milestone summary`.</action>
  <verify>test -f SHIP-NOTES.md; git ls-files SHIP-NOTES.md</verify>
  <done>`SHIP-NOTES.md` exists at project root, is tracked by git, and contains all 6 sections from RESEARCH.md §5.</done>
</task>
