# Review: Plan 2.2

## Verdict: PASS

(Reviewer agent did not persist this file; captured verbatim by the orchestrator from the agent's structured output.)

## Findings

### Critical
- None.

### Important
- None.

### Minor / Suggestions
- **`_in_window`'s `raise ValueError` at `leaderboard.py:187` is now unreachable dead code.** With the builder-introduced `_validate_window()` called at the top of both `query` and `query_per_track`, no invalid window string can reach `_in_window`. The fallthrough `raise` serves as a defensive backstop but could be replaced with `assert False, "unreachable"` (or removed) to make the invariant explicit. Style preference, not a bug.
- **Test 6 (`test_tiebreak_by_podiums_when_wins_equal`) uses `lb._sorted_rows(...)` directly with hand-crafted stat dicts.** Acceptable workaround for a real constraint of `POINTS=(6,3,1,0)`: every podium finisher earns ≥ 1 point, so equal-points + equal-wins necessarily implies equal-podiums when constructed from race data. Calling the private sort helper validates the `-podiums` sort dimension correctly. Worth recording as a Phase 1 lesson — the scoring scheme constrains data-driven tiebreaker tests.
- **Redundant `import json` inside `_seed` helper (`tests/test_leaderboard.py:178`).** `json` is already imported at the top of the file. Harmless (Python caches imports) but unnecessary. Skipped — too minor to justify a commit.

### Positive
- `_validate_window()` addition is a clean, minimal fix for a real plan defect (unknown window strings silently returning `[]` on empty stores). No spec contradiction, no API surface change, narrowly scoped.
- Both dataclasses (`Row`, `PerTrackRow`) are `@dataclass(frozen=True)` with the exact fields specified. Sort key `(-points, -wins, -podiums, name)` matches CONTEXT-1.
- ISO Monday-start math is correct (Saturday `weekday()=5` → week_start = previous Monday) and the four boundary cases (Mon in, prev-Sun out, current-Sun in, next-Mon out) all pass.
- Session-vs-disk split (`_races_for_window("session")` reads `_SESSION_RACES`; everything else reads `_load()["races"]`) is documented in-code and prevents the double-counting failure mode noted at plan time.
- `known_tracks()` set-union semantics correctly handle the disk/session overlap idempotently.
- Test 27 actively enforces "no `import tracks`" by reading the source text.
- Backward compat: `record_race` from Plan 2.1 unchanged.

## Verification Results
- `pytest tests/test_leaderboard.py`: **39 passed** (9 from Plan 2.1 + 30 new).
- `pytest` (full): **133 passed** (94 baseline + 9 from Plan 2.1 + 30 from Plan 2.2).
- Tk-free import (`python -c "import sys; sys.modules['tkinter']=None; import leaderboard"`): PASS.
- `_validate_window` addition: appropriate — fixes a latent plan defect without spec contradiction.
- Test 6 private-API usage: acceptable given the scoring-scheme constraint.
- CONTEXT-1 Decision 2 (ISO Monday-start week): COMPLIANT — `leaderboard.py:179-182` uses `today.weekday()` arithmetic correctly.
- CONTEXT-1 Decision 4 (`now=` only on query/query_per_track): COMPLIANT — `record_race` has no `now=` parameter; both query functions use the `*, now: datetime | None = None` keyword-only form.
- CONTEXT-1 Decision 5 (no `tracks` import): COMPLIANT — grep returns no matches; Test 27 enforces.
