# Build Summary: Plan 2.2

## Status: complete (with cross-plan adaptation)

## Tasks Completed

- **Task 1** (commit `825a044` `shipyard(phase-1): register snake PNGs in PyInstaller spec`):
  Appended `('assets/snakes/*.png', 'assets/snakes')` to `turtle_race.spec` `datas=` at line 7. Single-line format preserved. All 4 existing tuples preserved in original order.
  Verification: `python -c "..."` reading the line printed `True`. Spec line now contains both `assets/snakes/*.png` and `assets/snakes`.
- **Task 2** — Adapted: PNGs were already committed by Plan 2.1's commit `2681e4b` (Plan 2.1 builder used a broad `git add` that pulled in the untracked PNGs alongside `constants.py`). No separate commit needed.
  Acceptance criteria still satisfied:
  - `git ls-files assets/snakes/` lists `Anaconda.png`, `Ralph.png`, `Shadow.png` (alphabetical)
  - `git cat-file -s` confirms non-empty: Shadow=2,335,735 B, Ralph=2,375,089 B, Anaconda=2,562,838 B
  - No placeholder PNGs were generated; real art files are committed
- **Task 3** — Joint-green verification:
  - `pytest tests/test_constants.py` — 12/12 pass
  - `pytest` (full) — 54/54 pass

## Files Modified

- `turtle_race.spec` — line 7 extended with `('assets/snakes/*.png', 'assets/snakes')` tuple

## Decisions Made

- When Task 2's `git add` showed nothing staged, the builder investigated rather than fabricated PNGs. Found Plan 2.1's commit had already captured them. Reported Task 2 as already-satisfied rather than re-committing or rolling back.

## Issues Encountered

- **Cross-plan PNG capture:** Plan 2.1's `2681e4b` commit included the three PNGs alongside `constants.py`. By the time Plan 2.2 ran its `git add`, the files were already tracked. End state is correct; commit boundaries are not as planned. See Plan 2.1's SUMMARY for the same note from the other side.
- **Baseline `ImportError` (expected):** If Task 3 had run before Plan 2.1 completed, `pytest tests/test_constants.py` would have shown `ImportError`. In practice both plans landed before this Task 3 ran, so the test suite was green.

## Verification Results

- `python -c "import re; line = [l for l in open('turtle_race.spec') if 'datas=' in l][0]; print('assets/snakes/*.png' in line and 'assets/snakes' in line)"` → `True`
- `git ls-files assets/snakes/` → 3 lines (Anaconda, Ralph, Shadow)
- `pytest tests/test_constants.py` → 12 passed
- `pytest` (full) → 54 passed
