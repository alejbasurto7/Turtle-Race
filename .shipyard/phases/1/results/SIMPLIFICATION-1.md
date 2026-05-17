# Simplification Review — Phase 1

(Authored by the shipyard:simplifier agent; agent did not persist the file directly. Captured verbatim by the orchestrator.)

## Priority Summary
- **High:** 1 — unreachable `raise ValueError` in `_in_window`
- **Medium:** 1 — overlapping test assertions (tests 3 and 4)
- **Low:** 2 — redundant `import json` in `_seed`; verbose tiebreaker docstring

## Findings

### High Priority — Unreachable `raise ValueError` at `leaderboard.py:187`

`_in_window`'s trailing `raise ValueError(f"unknown time_window: {window!r}")` can never execute. Both public callers (`query` at line 261, `query_per_track` at line 305) call `_validate_window(time_window)` before any record iteration, so `_in_window` only ever runs with a validated window string.

**Remediation:** Delete the dead `raise` line. Add a one-line comment after the `if window == "year"` block: `# _validate_window() at each query entry point ensures window is always a known value.`

**Effort:** Trivial. **Impact:** 1 dead line removed; removes a subtle maintenance mislead (a future reader might think the inline raise is the primary guard and disable `_validate_window`).

### Medium Priority — Tests 3 and 4 are largely subset of each other

`test_query_truncates_to_six_three_one_for_three_racer_race` (line 208) and `test_query_fourth_place_consumed_only_when_four_finishers` (line 218) seed identical records (`["X","Y","Z"]` on `"straight"`) and verify overlapping assertions. Every assertion in test 4 (`len == 3`, `all(points >= 1)`) is implied by test 3's stronger assertions (`points == {6, 3, 1}`).

**Remediation options:**
- (a) Delete test 4, rename test 3 to `test_query_three_racer_race_six_three_one_no_phantom`.
- (b) Tighten test 4's assertion to `all(r.racer_name in {"X","Y","Z"} for r in rows)` — validates row identity (no ghost names), which IS independent from points-value checks.

**Effort:** Trivial. **Impact:** Eliminates a redundant test or makes the existing one genuinely additive.

**Verdict:** Defer to the next time that test section is touched. Non-urgent.

### Low Priority

1. **Redundant `import json` inside `_seed` helper** at `tests/test_leaderboard.py:178`. `json` is already imported at module level (line 1). The inner import is a no-op (Python caches modules) but misleading — implies `json` is not in scope, which is false. Delete line 178.

2. **Verbose tiebreaker docstring** at `tests/test_leaderboard.py:262-300` (38-line docstring for a 10-line test body). Documents the mathematical impossibility of constructing equal-points + equal-wins + unequal-podiums from race data given `POINTS=(6,3,1,0)`. The insight is valuable but already captured in VERIFICATION.md and SUMMARY-2.2.md. Trim to a 3-4 line note pointing to those documents.

## Non-findings — patterns that LOOK like over-engineering but are justified

- **`_path()` as a function wrapping a one-liner.** Load-bearing for `monkeypatch.setattr("paths.user_data_path", ...)` to work. Inlining it would break 7 of 9 tests in Plan 2.1 (the lesson that triggered the import-style fix). Do not collapse.
- **`_validate_window` as a separate function called from two places.** Two-caller threshold met; extraction makes intent unambiguous at each call site.
- **`_aggregate` and `_sorted_rows` as two functions.** Cohesively split — `_aggregate` is a map over history; `_sorted_rows` is a pure sort applied independently per track group in `query_per_track`.
- **`_empty_store` as a function rather than a constant.** Function returns a fresh dict each call; a constant would be a shared mutable dict (aliasing hazard).
- **`_atomic_write_json` parameterized by target_path.** Used from two distinct callers (`_save` and `_quarantine_and_reset`/`reset_all`).
- **Type annotations on private helpers.** Mildly inconsistent with the wider repo convention (sparse hints), but the return types here (`dict[str, dict]`, `list[tuple[str, dict]]`) genuinely aid readability for data-processing code. Not flagged.
- **39 tests for ~370 lines of module code.** Healthy ratio — calendar boundary logic alone warrants thorough coverage.

## Verdict

Phase 1 is clean code. One trivial High-priority fix is worth doing now (delete the dead `raise`). The redundant `import json` (Low) can ride along in the same commit — together a 2-line change. The Medium finding (test 3/4 overlap) and the verbose-docstring Low finding can wait until the test file is next touched in a Phase 2+ context.

**Recommendation:** Implement High + first Low in a single trivial commit now. Defer the rest.
