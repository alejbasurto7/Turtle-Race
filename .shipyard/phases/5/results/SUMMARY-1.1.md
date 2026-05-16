---
phase: 5
plan: 1.1
wave: 1
status: COMPLETE
baseline_tests: 84
final_tests: 85
commits: 3
---

# SUMMARY-1.1 — Phase 5 file edits execution summary

## Baseline

- pytest --collect-only -q before any changes: 84 tests collected
- Git status: clean (master branch)

## Task 1 — .gitignore, Anaconda test, create_racers docstring

Files: .gitignore, tests/test_race.py, race.py

1. Appended assets/midi/ after .vscode/launch.json in .gitignore.
2. Inserted test_head_offset_arc_anaconda in tests/test_race.py after Ralph test.
   stretch_len = 1.2 * 5 = 6.0, head_offset_arc = 20 * 6.0 / 2 = 60.0.
3. Extended create_racers docstring in race.py with Note block (SNAKE_LENGTHS[i] branch).

Verification: 85/85 passed.
Commit: 207f0e3 — shipyard(phase-5): gitignore assets/midi, add Anaconda test, extend create_racers docstring

## Task 2 — PROJECT.md strikethrough + CLAUDE.md 3 fixes

Files: .shipyard/PROJECT.md, CLAUDE.md

1. Strikethrough + RESOLVED annotations on 3 Open Items; DEFERRED on spiral.
2. CLAUDE.md fix 1: _SHAPE_UNIT_SIZE is a dict (9 for classic/turtle, 20 for snake).
3. CLAUDE.md fix 2: podium bump width corrected 2.0 -> 3.0 (Phase 4 commit 4fb207e).
4. CLAUDE.md fix 3: HEAD-at-start placement via _head_offset_arc_for/_back_pos noted.

Commit: 96c9ed3 — shipyard(phase-5): PROJECT.md Open Items cleanup, CLAUDE.md _SHAPE_UNIT_SIZE fix

## Task 3 — SHIP-NOTES.md creation

File: SHIP-NOTES.md (new, project root)

Created with all 6 sections: What Shipped, Architecture Pointers, Run/Test/Build,
Known Deferrals, Snake Assets, Future Work Suggestions.

Commit: dae6b79 — shipyard(phase-5): add SHIP-NOTES.md milestone summary

## Final state

| Check                              | Result        |
|------------------------------------|---------------|
| Baseline tests                     | 84            |
| Final tests                        | 85/85 passed  |
| New test                           | test_head_offset_arc_anaconda (60.0) |
| .gitignore contains assets/midi/   | Yes           |
| race.py docstring has Note block   | Yes           |
| PROJECT.md Open Items annotated    | Yes           |
| CLAUDE.md 3 fixes applied          | Yes           |
| SHIP-NOTES.md exists and tracked   | Yes           |
| Atomic commits per task            | 3             |

## Deviations

CLAUDE.md scope expansion per CRITIQUE.md: Task 2 applied 3 fixes instead of 1.
This was explicitly required by the CRITIQUE and prompt instructions. No other deviations.
