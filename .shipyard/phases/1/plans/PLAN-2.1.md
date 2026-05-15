---
phase: snake-constants-species-config
plan: 2.1
wave: 2
dependencies: [1.1]
must_haves:
  - SNAKE_NAMES, SNAKE_COLORS, SNAKE_LENGTHS, SNAKE_IMAGES, L_BASE defined in constants.py
  - SPECIES dict with "turtles" and "snakes" entries; shape_drawer is a STRING sentinel ("turtle"/"snake")
  - constants.py imports nothing from race.py (no circular import)
  - All 9 new tests from Plan 1.1 turn green (assuming PNGs are present on disk; Plan 2.2 covers committing them)
files_touched:
  - constants.py
tdd: false
risk: low
---

# Plan 2.1: TDD green — implement snake constants and SPECIES config

## Context

Implements the snake identity block + `SPECIES` config dict in `constants.py` to turn the failing tests from Plan 1.1 green.

Locked decisions from `.shipyard/phases/1/CONTEXT-1.md`:
- **`shape_drawer` is a STRING sentinel** (`"turtle"` / `"snake"`). Resolving it to a callable happens in `race.py` in Phase 4. Do **NOT** import from `race.py` in `constants.py` — that re-introduces the circular import this decision exists to avoid.
- **Ralph's color hex is `"#E89F4F"`** — warm orange-tan. Use exactly this string in `SNAKE_COLORS[1]`.
- **`SNAKE_LENGTHS = [6, 2, 5]`** — positional with `SNAKE_NAMES` (Shadow=6, Ralph=2, Anaconda=5). The 6:5:2 visual ratio is Shadow:Anaconda:Ralph by *value*, not by list position.
- **`SNAKE_LENGTHS` is NOT inside `SPECIES`** — keeps the schema symmetric with turtles (which has no `lengths` analog). Phase 4's `create_racers` will read `SNAKE_LENGTHS[i]` by index directly.

Insertion point (per `RESEARCH.md` section 1): after `BET_IMAGE_SIZE` on line 25 of `constants.py`, before the `# Track layout` comment on line 27.

This plan can run **in parallel with Plan 2.2** — they touch different files. The full test suite goes green only after both 2.1 and 2.2 land; the cross-plan gate is documented in Verification below.

## Dependencies

- **Plan 1.1** must be complete (failing tests in place so we can observe the RED → GREEN transition).

## Tasks

### Task 1 — Add the snake identity block to constants.py

**Files:**
- `constants.py`

**Action:**
Insert the following block between `constants.py:25` (`BET_IMAGE_SIZE = 140 ...`) and `constants.py:27` (`# Track layout`). Preserve the blank line on each side so the file's visual sectioning stays consistent:

```python
# --- Snake racer identity ---
SNAKE_NAMES   = ["Shadow", "Ralph", "Anaconda"]
SNAKE_COLORS  = ["black", "#E89F4F", "green"]      # positional with SNAKE_NAMES; Ralph hex per CONTEXT-1.md
SNAKE_LENGTHS = [6, 2, 5]                           # positional with SNAKE_NAMES; 6:5:2 ratio is Shadow:Anaconda:Ralph by value
SNAKE_IMAGES  = {
    "Shadow":   "assets/snakes/Shadow.png",
    "Ralph":    "assets/snakes/Ralph.png",
    "Anaconda": "assets/snakes/Anaconda.png",
}
L_BASE = 1.0   # placeholder — tuned visually in Phase 4
```

**Description:**
Pure additive data block. Mirrors the positional invariant pattern already used by `TURTLE_NAMES` / `TURTLE_COLORS`. The `L_BASE` placeholder is named here so Phase 4 has a single edit-site; no test in Phase 1 constrains its value.

**Acceptance criteria:**
- `python -c "import constants; print(constants.SNAKE_NAMES, constants.SNAKE_COLORS, constants.SNAKE_LENGTHS)"` prints `['Shadow', 'Ralph', 'Anaconda'] ['black', '#E89F4F', 'green'] [6, 2, 5]`.
- `python -c "import constants; print(constants.SNAKE_IMAGES['Shadow'])"` prints `assets/snakes/Shadow.png`.
- `python -c "import constants; print(type(constants.L_BASE).__name__, constants.L_BASE)"` prints a numeric type and `1.0`.
- The four `test_snake_*` tests from Plan 1.1 pass (assuming PNGs exist on disk — they are physically present in the working tree; Plan 2.2 makes that survive a fresh clone).
- `constants.py` still contains no `import` statements (verify: `python -c "import ast; print([n for n in ast.parse(open('constants.py').read()).body if isinstance(n, (ast.Import, ast.ImportFrom))])"` prints `[]`).

### Task 2 — Add the SPECIES config dict to constants.py

**Files:**
- `constants.py`

**Action:**
Append the following block directly after the snake identity block from Task 1 (still above the `# Track layout` section):

```python
# --- Species config ---
SPECIES = {
    "turtles": {
        "names":        TURTLE_NAMES,
        "colors":       TURTLE_COLORS,
        "images":       TURTLE_IMAGES,
        "bet_layout":   "grid_2x2",
        "shape_drawer": "turtle",
    },
    "snakes": {
        "names":        SNAKE_NAMES,
        "colors":       SNAKE_COLORS,
        "images":       SNAKE_IMAGES,
        "bet_layout":   "row_3",
        "shape_drawer": "snake",
    },
}
```

**Description:**
The `SPECIES` config is the single dispatch surface that downstream phases (2 — race generalization, 3 — dialogs, 4 — shape drawer wiring) will read. `shape_drawer` values are deliberately strings — `race.py` will dispatch them to callables via its own table in Phase 4.

**Acceptance criteria:**
- `python -c "import constants; print(constants.SPECIES['snakes']['names'])"` prints `['Shadow', 'Ralph', 'Anaconda']`.
- `python -c "import constants; print(constants.SPECIES['turtles']['shape_drawer'], constants.SPECIES['snakes']['shape_drawer'])"` prints `turtle snake`.
- `python -c "import constants; print(constants.SPECIES['turtles']['bet_layout'], constants.SPECIES['snakes']['bet_layout'])"` prints `grid_2x2 row_3`.
- The five `test_species_*` tests from Plan 1.1 pass.
- The reference list (`SPECIES["turtles"]["names"]`) is the same object as `TURTLE_NAMES`: `python -c "import constants; print(constants.SPECIES['turtles']['names'] is constants.TURTLE_NAMES)"` prints `True`.

### Task 3 — Run the test suite and confirm GREEN (modulo PNGs)

**Files:**
- (read-only verification)

**Action:**
Run `pytest tests/test_constants.py`. All 12 tests must pass **if the snake PNGs are physically present on disk** (which they are in the working tree — Plan 2.2 handles tracking them in git). If `test_snake_image_files_exist_on_disk` fails, verify the three files exist at `assets/snakes/{Shadow,Ralph,Anaconda}.png` on the local working tree; if they do, the failure is a path-construction bug in the test (escalate); if they don't, this plan ran in a fresh-clone context and Plan 2.2 must run first.

Then run the full suite (`pytest`) to confirm no regression in the other test files.

**Description:**
Final RED→GREEN gate for this plan. Co-located with Plan 2.2's `git add` step; the two together produce a fully-green suite that survives a fresh clone.

**Acceptance criteria:**
- `pytest tests/test_constants.py` exits zero with 12 passed.
- `pytest` (full suite) exits zero — no regression in `test_constants.py`, `test_tracks.py`, or any other test module.

## Verification

```powershell
# All snake/SPECIES tests green:
pytest tests/test_constants.py

# Full suite — no collateral regressions:
pytest

# Quick SPECIES smoke (matches the success criterion in ROADMAP.md):
python -c "import constants; print(constants.SPECIES['snakes']['names'])"
# Expected: ['Shadow', 'Ralph', 'Anaconda']

# Confirm no circular-import risk was introduced:
python -c "import ast; print([n for n in ast.parse(open('constants.py').read()).body if isinstance(n, (ast.Import, ast.ImportFrom))])"
# Expected: []
```

**Cross-plan ordering note:** The 12-pass result depends on the snake PNGs being on disk. They are present in the local working tree today, so this plan can pass `pytest tests/test_constants.py` on its own. For the milestone-level "fresh clone passes pytest" guarantee, Plan 2.2 must also land — re-run `pytest tests/test_constants.py` once both Plan 2.1 and Plan 2.2 are merged to confirm the joint GREEN state.
