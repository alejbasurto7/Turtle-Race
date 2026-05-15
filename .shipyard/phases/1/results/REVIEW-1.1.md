# Review: Plan 1.1

## Verdict: PASS

Both stages clean. One minor robustness suggestion noted, non-blocking.

## Findings

### Critical

None.

### Minor

- **`test_snake_lengths_positional_values` (tests/test_constants.py:39-40)** — uses `dict(zip(SNAKE_NAMES, SNAKE_LENGTHS))` then asserts equality to `{"Shadow": 6, "Ralph": 2, "Anaconda": 5}`. If `SNAKE_LENGTHS` were accidentally truncated to 2 elements, `zip` would silently produce only 2 entries and the equality check would catch that (dict mismatch). However, the test relies on `test_snake_lists_are_length_3` (run earlier) to independently catch the length mismatch. Adding `assert len(named) == 3` would make the test self-contained. Non-blocking — defense-in-depth only.

- **`test_species_entries_have_required_sub_keys` uses `<=` (subset) not `==`** — intentional per plan (minimum-schema guard), but means undocumented keys could creep into `SPECIES` later without test objection. Acceptable trade-off; document for the Phase 3 architect who will read the schema.

### Positive

- **Single import line convention respected.** `SPECIES` was added to the import line during Task 1, not via a duplicated import statement — exactly the plan's intent.
- **All 9 new tests present, in correct order**, with exact names from the plan.
- **3 original tests preserved byte-for-byte** — no collateral damage.
- **RED signal correctly produced** — `ImportError` at collection time, exit code 2.
- **Style mirrors existing pattern exactly** — no PIL, no fixtures, manual `project_root` for disk-exists, no `paths.resource_path` import.
- **Wave 2 alignment verified** — every assertion in these tests matches PLAN-2.1's planned constants. Wave 2 will go GREEN cleanly with no schema mismatch:
  - `{"Shadow": 6, "Ralph": 2, "Anaconda": 5}` ↔ `SNAKE_LENGTHS = [6, 2, 5]` with `SNAKE_NAMES = ["Shadow", "Ralph", "Anaconda"]`
  - `shape_drawer` string sentinels `{"turtle", "snake"}` ↔ planned values `"turtle"` / `"snake"`
  - `bet_layout` valid set `{"grid_2x2", "row_3"}` ↔ planned values `"grid_2x2"` / `"row_3"`
  - Racer counts 4 / 3 ↔ `TURTLE_NAMES` / `SNAKE_NAMES`

## Wave 1 Gate: OPEN — Wave 2 cleared to begin.
