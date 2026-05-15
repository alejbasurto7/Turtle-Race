# Build Summary: Plan 2.1

## Status: complete

## Tasks Completed

- **Task 1** (commit `2681e4b` `shipyard(phase-1): add snake identity constants`):
  Inserted snake identity block into `constants.py` between line 25 (`BET_IMAGE_SIZE`) and the `# Track layout` section. Added `SNAKE_NAMES = ["Shadow", "Ralph", "Anaconda"]`, `SNAKE_COLORS = ["black", "#E89F4F", "green"]`, `SNAKE_LENGTHS = [6, 2, 5]`, `SNAKE_IMAGES` dict, `L_BASE = 1.0`. Ralph hex is exact (`"#E89F4F"`). No imports introduced (AST check: `[]`).
  **Note:** this commit also accidentally bundled the three previously-untracked snake PNGs (`assets/snakes/Shadow.png`, `Ralph.png`, `Anaconda.png`) — these were supposed to be in Plan 2.2's commit. The end state is correct (PNGs are tracked) but the commit boundaries are not as planned. See "Issues encountered" below.
- **Task 2** (commit `c7e89ed` `shipyard(phase-1): add SPECIES config dict`):
  Appended `SPECIES` dict directly below the snake identity block. `shape_drawer` values are string sentinels (`"turtle"` / `"snake"`) — no `race.py` import, no circular-import risk. `SPECIES["turtles"]["names"] is TURTLE_NAMES` confirmed `True` (same-object identity).
- **Task 3** — verification (no commit):
  - `pytest tests/test_constants.py`: **12 passed**, exit 0
  - `pytest` (full suite): **54 passed**, exit 0 — no regressions in `test_tracks.py`
  - SPECIES smoke: `['Shadow', 'Ralph', 'Anaconda']`
  - Circular-import AST check: `[]`

## Files Modified

- `constants.py` — added snake identity block + `SPECIES` dict between line 25 and the track-layout section
- `assets/snakes/Shadow.png`, `Ralph.png`, `Anaconda.png` — captured into commit `2681e4b` (should have been Plan 2.2's responsibility)

## Decisions Made

- Used `git add` more broadly than planned, which pulled in the snake PNGs alongside `constants.py`. Recovered net state is correct; commit hygiene is slightly off (see issues).

## Issues Encountered

- **Cross-plan commit pollution:** Task 1's commit (`2681e4b`) includes both `constants.py` and the three snake PNGs. The PNGs were supposed to be committed by Plan 2.2 in a separate commit. This is the exact failure mode my dispatch prompt warned against ("Be careful about cross-plan file pollution"). Plan 2.2's builder detected this and adapted gracefully (it ran its spec-edit task and reported the PNG-add task as already-done).
  - **Impact:** None functional — all files are in git, all tests pass.
  - **Cleanup option:** None reasonable. Rewriting history with `git reset --soft` + restructuring the commits is more risk than the benefit warrants. Move on; document for future builds.

## Verification Results

- `pytest tests/test_constants.py` — 12/12 pass
- `pytest` — 54/54 pass (full suite green)
- `python -c "import constants; print(constants.SPECIES['snakes']['names'])"` → `['Shadow', 'Ralph', 'Anaconda']`
- `python -c "import ast; print([n for n in ast.parse(open('constants.py').read()).body if isinstance(n, (ast.Import, ast.ImportFrom))])"` → `[]`
