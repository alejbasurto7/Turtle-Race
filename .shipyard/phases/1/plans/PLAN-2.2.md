---
phase: snake-constants-species-config
plan: 2.2
wave: 2
dependencies: [1.1]
must_haves:
  - turtle_race.spec datas= includes ('assets/snakes/*.png', 'assets/snakes')
  - assets/snakes/Shadow.png, Ralph.png, Anaconda.png tracked by git
  - The on-disk snake PNG existence test survives a fresh clone after this phase ships
files_touched:
  - turtle_race.spec
  - assets/snakes/Shadow.png
  - assets/snakes/Ralph.png
  - assets/snakes/Anaconda.png
tdd: false
risk: low
---

# Plan 2.2: TDD green — register snake PNGs in PyInstaller spec and commit assets

## Context

Two atomic operations both required so the snake assets survive a fresh clone *and* land in the frozen `dist/TurtleRace.exe`:

1. Add `('assets/snakes/*.png', 'assets/snakes')` to `turtle_race.spec` `datas=` so PyInstaller bundles the snake PNGs at `<_MEIPASS>/assets/snakes/` (matching the path prefix in `SNAKE_IMAGES` from Plan 2.1).
2. `git add` the three currently-untracked snake PNGs so `test_snake_image_files_exist_on_disk` (from Plan 1.1) passes on a fresh clone.

Locked decision from `.shipyard/phases/1/CONTEXT-1.md` Decision 3: snake PNGs are committed in Phase 1 (not deferred). Size budget: 3 × 1024×1024 RGBA PNGs is acceptable for this repo; no LFS.

Critical finding from `RESEARCH.md` section 2: the existing `('assets/*.png', 'assets')` glob does **NOT** recurse into subdirectories. The new tuple for `assets/snakes/` is genuinely additive, not redundant. Without it, the frozen exe crashes at the snake bet dialog with a missing-file error in Phase 3+.

This plan can run **in parallel with Plan 2.1** — they touch different files. The joint GREEN state of the test suite is gated on both.

## Dependencies

- **Plan 1.1** must be complete (the failing `test_snake_image_files_exist_on_disk` test exists and is observing the on-disk state).

## Tasks

### Task 1 — Extend turtle_race.spec datas= with the snake PNG glob

**Files:**
- `turtle_race.spec`

**Action:**
Edit line 7 of `turtle_race.spec`. The current line is:

```python
    datas=[('lawn.jpg', '.'), ('assets/*.jpg', 'assets'), ('assets/*.mid', 'assets'), ('assets/*.png', 'assets')],
```

Append one tuple `('assets/snakes/*.png', 'assets/snakes')` so the line becomes:

```python
    datas=[('lawn.jpg', '.'), ('assets/*.jpg', 'assets'), ('assets/*.mid', 'assets'), ('assets/*.png', 'assets'), ('assets/snakes/*.png', 'assets/snakes')],
```

Keep the single-line format that the existing file uses — do not reflow the list onto multiple lines.

**Description:**
The destination string `'assets/snakes'` makes PyInstaller place the files at `<_MEIPASS>/assets/snakes/Shadow.png` (etc.), which is exactly the path stored in `SNAKE_IMAGES["Shadow"]` from Plan 2.1. `paths.resource_path("assets/snakes/Shadow.png")` resolves to that location in the frozen build.

**Acceptance criteria:**
- `turtle_race.spec` line 7 contains the literal substring `('assets/snakes/*.png', 'assets/snakes')`.
- The full line still uses single-line list formatting (no newline injected into the `datas=` list).
- The existing four tuples (`lawn.jpg`, `assets/*.jpg`, `assets/*.mid`, `assets/*.png`) are still present, in the same order, unchanged.
- Verification command:
  ```powershell
  python -c "import re; line = [l for l in open('turtle_race.spec') if 'datas=' in l][0]; print('assets/snakes/*.png' in line and 'assets/snakes' in line)"
  ```
  prints `True`.

### Task 2 — Add the three snake PNGs to git

**Files:**
- `assets/snakes/Shadow.png`
- `assets/snakes/Ralph.png`
- `assets/snakes/Anaconda.png`

**Action:**
Run `git add assets/snakes/Shadow.png assets/snakes/Ralph.png assets/snakes/Anaconda.png`. Verify the files are now staged (or already tracked) via `git ls-files assets/snakes/`. Do **not** create a commit — per `.shipyard/config.json`, the executing builder agent handles per-task commits.

If any of the three files is missing from the working tree, stop and escalate — the milestone's PNG assets were assumed present per `RESEARCH.md` section 6. Do **not** generate placeholder PNGs.

**Description:**
Currently the three PNGs sit untracked in the working tree, so a fresh clone has no `assets/snakes/` directory and `test_snake_image_files_exist_on_disk` fails. After this task, the files are part of the repository.

**Acceptance criteria:**
- `git ls-files assets/snakes/` lists exactly three lines: `assets/snakes/Anaconda.png`, `assets/snakes/Ralph.png`, `assets/snakes/Shadow.png` (alphabetical order — git's default).
- Each file is non-empty: `git cat-file -s :assets/snakes/Shadow.png` (and the other two) prints a positive integer.
- No other files were added in this step.

### Task 3 — Joint-green confirmation with Plan 2.1

**Files:**
- (read-only verification)

**Action:**
Run `pytest tests/test_constants.py` and then `pytest` (full). All 12 tests in `test_constants.py` must pass. This is the milestone-level GREEN gate — at this point a fresh clone of the repo, with `pytest` installed, will pass the full suite.

If `test_snake_image_files_exist_on_disk` is the only failure, re-verify Task 2 succeeded (`git ls-files assets/snakes/`). If `test_snake_*` or `test_species_*` tests fail at import time, Plan 2.1 has not landed yet — coordinate with that plan's completion before re-running.

**Description:**
This is the cross-plan acknowledgment that Plans 2.1 and 2.2 together close Phase 1. Either plan alone leaves the suite partially red.

**Acceptance criteria:**
- `pytest tests/test_constants.py` exits zero with 12 passed.
- `pytest` (full suite) exits zero.
- `git ls-files assets/snakes/` lists all three PNGs.

## Verification

```powershell
# Spec edit is in place:
python -c "import re; line = [l for l in open('turtle_race.spec') if 'datas=' in l][0]; print('assets/snakes/*.png' in line and 'assets/snakes' in line)"
# Expected: True

# Snake PNGs are tracked:
git ls-files assets/snakes/
# Expected (three lines, alphabetical):
# assets/snakes/Anaconda.png
# assets/snakes/Ralph.png
# assets/snakes/Shadow.png

# Joint suite green (requires Plan 2.1 also complete):
pytest tests/test_constants.py
pytest
```

**Cross-plan ordering note:** Plans 2.1 and 2.2 can be executed in either order or in parallel — they touch disjoint files (`constants.py` vs. `turtle_race.spec` + `assets/snakes/*.png`). The 12-pass `pytest tests/test_constants.py` result requires **both** plans complete. If running them sequentially, re-run the full test suite after the second plan lands to capture the joint GREEN state. A `pyinstaller turtle_race.spec` build is **not** part of Phase 1 verification — that gate lives in Phase 5.
