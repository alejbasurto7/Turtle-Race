---
phase: 5
plan: 2.1
wave: 2
type: verification-only
date: 2026-05-16
author: builder-agent
commits_made: 0
---

# SUMMARY-2.1 - Phase 5 Verification Gate

Pure verification pass - no source edits, no commits. Covers pytest regression sweep,
banned-identifier grep, and PyInstaller build.

---

## Task 1 - pytest 85/85

### Command

    pytest -q

### Output (full - suite is fast)

    ........................................................................ [ 84%]
    .............                                                            [100%]
    85 passed in 0.08s

### Result: PASS

- Exit code: 0
- Total passed: 85 (matches CONTEXT-5 target: 84 baseline + 1 Anaconda test from PLAN-1.1)
- test_head_offset_arc_anaconda confirmed present (committed in PLAN-1.1)
- No failures, no errors, no skips

---

## Task 2 - Banned-identifier grep

### Pattern searched

    N_LANES|turtles_list|create_turtles|place_turtles_on_track|tortuga

### Output

    tests/test_tracks.py:38:# Local constant replaces the deleted N_LANES from constants.py.

### Result: PASS

Exactly one match at the intentional historical-comment location (tests/test_tracks.py:38).
No regressions anywhere else in the Python source tree.

---

## Task 3 - PyInstaller build

### Environment

- PyInstaller version: 6.20.0 (already installed - no install step needed)
- Python: 3.14.4
- Platform: Windows-11-10.0.26100-SP0
- UPX: not present on PATH (benign)

### Exit code: 0

### Last 20 lines of build output

    46215 INFO: Building PYZ (ZlibArchive) PYZ-00.pyz
    46561 INFO: Building PYZ (ZlibArchive) PYZ-00.pyz completed successfully.
    46614 INFO: Building PKG (CArchive) TurtleRace.pkg
    51546 INFO: Building PKG (CArchive) TurtleRace.pkg completed successfully.
    51562 INFO: Bootloader Windows-64bit-intel/runw.exe
    51589 INFO: Building EXE from EXE-00.toc
    51594 INFO: Copying bootloader EXE to dist/TurtleRace.exe
    51708 INFO: Copying icon to EXE
    51803 INFO: Copying 0 resources to EXE
    51804 INFO: Embedding manifest in EXE
    51896 INFO: Appending PKG archive to EXE
    52012 INFO: Fixing EXE headers
    54218 INFO: Building EXE from EXE-00.toc completed successfully.
    54233 INFO: Build complete! The results are available in: dist

### dist/TurtleRace.exe

- Exists: yes
- Size: 44,870,165 bytes (~42.8 MB)

### Warning-file review

All warnings in warn-turtle_race.txt are standard POSIX-module stubs (pwd, grp, posix,
fcntl, termios, etc.) expected on every Windows PyInstaller build with pygame/PIL/numpy.
No warnings about missing project assets. All spec datas= entries resolved correctly.

### Result: PASS

- Exit code 0; dist/TurtleRace.exe exists (42.8 MB)
- No missing-asset errors or warnings
- No frozen-exe smoke per CONTEXT-5 Decision 3 (BUILD-ONLY)

---

## Task 4 - Lightweight final smoke note

Status: PENDING_HUMAN_VERIFICATION

Cannot run autonomously (requires display). Not a critical gate - the user has
iteratively smoke-tested the full race loop through Phase 4 (turtle + snake, 3 tracks
each, bet dialog, win/loss dialogs, play-again loop, audio). This is a final sanity
checkpoint only.

To complete: run python main.py, play one round each species on any track, confirm
race, win/loss dialog, and play-again prompt all work.

---

## Overall Phase 5 PLAN-2.1 Verdict

| Task                   | Expected                  | Actual                    | Status   |
|------------------------|---------------------------|---------------------------|----------|
| pytest count           | 85 passed                 | 85 passed                 | PASS     |
| pytest exit code       | 0                         | 0                         | PASS     |
| banned-identifier grep | 1 hit (test_tracks.py:38) | 1 hit (test_tracks.py:38) | PASS     |
| dist/TurtleRace.exe    | exists                    | exists (42.8 MB)          | PASS     |
| PyInstaller exit code  | 0                         | 0                         | PASS     |
| Missing-asset warnings | none                      | none                      | PASS     |
| Manual smoke           | human-required            | PENDING_HUMAN_VERIFICATION| DEFERRED |

Phase 5 is CLOSED. All hard gates passed.
