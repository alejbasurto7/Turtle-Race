---
phase: snake-constants-species-config
plan: 1.1
wave: 1
dependencies: []
must_haves:
  - All 9 new snake/SPECIES invariant tests added to tests/test_constants.py
  - Tests mirror existing file style exactly (no PIL, no parametrize, no fixtures, manual project_root)
  - Tests fail when run (RED) because constants do not yet exist
  - Imports extend the existing import line, not replace it
files_touched:
  - tests/test_constants.py
tdd: true
risk: low
---

# Plan 1.1: TDD red — snake & SPECIES invariant tests

## Context

Phase 1 of the Snakes Racer Mode milestone. Pure data work. Lock the invariants of the new snake identity constants and `SPECIES` config dict via failing tests before any implementation lands.

Authoritative inputs:
- `.shipyard/PROJECT.md` — Functional / Snake racers & data model section
- `.shipyard/ROADMAP.md` — Phase 1, Tasks 1 and 3
- `.shipyard/phases/1/CONTEXT-1.md` — locked decisions: string sentinel `shape_drawer` (∈ `{"turtle", "snake"}`); Ralph hex `#E89F4F`; snake PNGs are committed in Phase 1
- `.shipyard/phases/1/RESEARCH.md` — sections 3 and 7 cover the existing test style and the full nine-test list

Style invariants from `tests/test_constants.py` (current state, 26 lines, 3 tests):
- Module-level `sys.path.insert(0, ...)` already present at line 5 — do not duplicate
- Imports are a single named line: `from constants import TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE` (line 7). Extend this line; do not add a second import statement
- Tests are plain `def test_*` functions — no fixtures, no `@pytest.mark.parametrize`, no class wrappers
- The disk-exists test (`test_image_files_exist_on_disk`) computes `project_root` manually with `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` and **does not** import `paths.resource_path`. The new snake disk-exists test must do the same

Out of scope for this plan (later waves):
- Editing `constants.py` (done in Plan 2.1)
- Editing `turtle_race.spec` (done in Plan 2.2)
- `git add`-ing the snake PNGs (done in Plan 2.2)
- Any `L_BASE` value assertion — `L_BASE` is a placeholder; Phase 4 owns its tuning

## Dependencies

None. This is Wave 1.

## Tasks

### Task 1 — Extend imports and add the four snake-identity invariant tests

**Files:**
- `tests/test_constants.py`

**Action:**
Extend the existing `from constants import ...` line at `tests/test_constants.py:7` to also import `SNAKE_NAMES, SNAKE_COLORS, SNAKE_LENGTHS, SNAKE_IMAGES`. Append four new test functions after the existing three:

1. `test_snake_lists_are_length_3` — assert `len(SNAKE_NAMES) == len(SNAKE_COLORS) == len(SNAKE_LENGTHS) == 3`.
2. `test_snake_image_map_has_entry_for_every_snake_name` — assert `set(SNAKE_IMAGES.keys()) == set(SNAKE_NAMES)`. Mirror the message style of the existing turtle-name test.
3. `test_snake_lengths_positional_values` — build a dict `dict(zip(SNAKE_NAMES, SNAKE_LENGTHS))` and assert it equals `{"Shadow": 6, "Ralph": 2, "Anaconda": 5}`. (Name-keyed because the by-position list `[6, 2, 5]` is easy to confuse with the 6:5:2 by-value ratio.)
4. `test_snake_image_files_exist_on_disk` — mirror `test_image_files_exist_on_disk` exactly: compute `project_root` manually, loop `SNAKE_IMAGES.items()`, assert `os.path.isfile(os.path.join(project_root, rel_path))` for each.

**Description:**
The four tests lock the snake-side parallel to the existing turtle invariants. Test 3 specifically defends against the by-position vs. by-ratio confusion called out in `RESEARCH.md` section 7. Test 4 will start failing now and will continue failing until Plan 2.2 `git add`s the PNGs (the files are physically present on disk but currently untracked — the test only checks `os.path.isfile`, so it should actually pass as soon as the import line resolves, **provided** the constants exist).

**Acceptance criteria:**
- File `tests/test_constants.py` contains four new `def test_snake_*` functions in the order listed above.
- Import line at `tests/test_constants.py:7` now also names `SNAKE_NAMES, SNAKE_COLORS, SNAKE_LENGTHS, SNAKE_IMAGES`.
- `pytest tests/test_constants.py` collects the four new tests and they fail at **import time** with `ImportError: cannot import name 'SNAKE_NAMES' from 'constants'` (because Plan 2.1 has not run yet). Collection failure on the new tests is the expected RED signal.

### Task 2 — Add the five SPECIES config-shape invariant tests

**Files:**
- `tests/test_constants.py`

**Action:**
Extend the existing import line to also import `SPECIES`. Append five test functions after the snake-identity tests:

1. `test_species_has_required_top_level_keys` — assert `set(SPECIES.keys()) == {"turtles", "snakes"}`.
2. `test_species_entries_have_required_sub_keys` — for each species key, assert `{"names", "colors", "images", "bet_layout", "shape_drawer"} <= set(SPECIES[s].keys())`.
3. `test_species_bet_layout_values_are_valid` — for each species, assert `SPECIES[s]["bet_layout"] in {"grid_2x2", "row_3"}`.
4. `test_species_racer_counts` — assert `len(SPECIES["turtles"]["names"]) == 4` and `len(SPECIES["snakes"]["names"]) == 3`.
5. `test_species_shape_drawer_is_string_sentinel` — for each species, assert `isinstance(SPECIES[s]["shape_drawer"], str)` and `SPECIES[s]["shape_drawer"] in {"turtle", "snake"}`. (Enforces the CONTEXT-1.md Decision 1 string-sentinel rule and prevents anyone from later wiring a callable here and re-introducing the `constants` ↔ `race` circular import.)

**Description:**
Locks the `SPECIES` schema. Test 5 is the critical defense against accidentally importing `race.py` into `constants.py` in a later phase.

**Acceptance criteria:**
- File `tests/test_constants.py` contains five new `def test_species_*` functions.
- Import line now also names `SPECIES`.
- All five tests fail at collection time with `ImportError: cannot import name 'SPECIES' from 'constants'`.

### Task 3 — Verify the RED state and final test file shape

**Files:**
- `tests/test_constants.py` (read-only verification)

**Action:**
Run `pytest tests/test_constants.py` and confirm the failure mode is the expected `ImportError` (collection-time failure on the new imports), not a test-logic error. Confirm the file structure: 3 original tests preserved unchanged, 9 new tests appended, single extended import line.

**Description:**
Sanity gate before handing off to Wave 2. A test-logic error here (e.g., a typo asserting the wrong dict shape) would silently turn green on bad data later — verify the failure cause is "constant not yet defined", not "test typo".

**Acceptance criteria:**
- `pytest tests/test_constants.py` exits non-zero.
- The failure message references `ImportError` or `cannot import name` on at least one of `SNAKE_NAMES`, `SNAKE_COLORS`, `SNAKE_LENGTHS`, `SNAKE_IMAGES`, `SPECIES`.
- The three existing tests (`test_image_map_has_entry_for_every_turtle_name`, `test_image_files_exist_on_disk`, `test_bet_image_size_is_positive_int`) are still present byte-for-byte.
- Total test count discoverable in the file is 12 (3 existing + 9 new), even if collection fails before they run.

## Verification

```powershell
# RED — expected failure mode is ImportError on the new constants:
pytest tests/test_constants.py

# Confirm the file structure:
python -c "import ast; tree = ast.parse(open('tests/test_constants.py').read()); print([n.name for n in tree.body if isinstance(n, ast.FunctionDef)])"
```

Expected output of the `ast` line (exact order):
```
['test_image_map_has_entry_for_every_turtle_name', 'test_image_files_exist_on_disk', 'test_bet_image_size_is_positive_int', 'test_snake_lists_are_length_3', 'test_snake_image_map_has_entry_for_every_snake_name', 'test_snake_lengths_positional_values', 'test_snake_image_files_exist_on_disk', 'test_species_has_required_top_level_keys', 'test_species_entries_have_required_sub_keys', 'test_species_bet_layout_values_are_valid', 'test_species_racer_counts', 'test_species_shape_drawer_is_string_sentinel']
```

The pytest run **must** fail at this stage — that is the TDD RED gate that Wave 2 turns green.
