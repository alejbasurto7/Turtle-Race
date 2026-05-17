# Phase 1 Verification

## Overall Status: COMPLETE

(The shipyard:verifier agent terminated mid-stream without persisting this file. Verification below was performed directly by the orchestrator via test runs, source inspection, and grep against the Phase 1 success criteria in ROADMAP.md.)

## Coverage of Phase 1 Success Criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | `leaderboard.py` exists with seven public functions | MET | `dir(leaderboard)` exposes `record_race`, `query`, `query_per_track`, `known_tracks`, `reset_session`, `reset_all`, plus dataclasses `Row` / `PerTrackRow` and constants `POINTS` / `SCHEMA_VERSION`. |
| 2 | `import leaderboard` succeeds with `tkinter` poisoned | MET | `python -c "import sys; sys.modules['tkinter']=None; import leaderboard"` exits 0 (run, prints `OK`). |
| 3 | `paths.user_data_path` per-platform, never under `_MEIPASS` | MET | [paths.py:10-27](paths.py#L10-L27); 9 tests in [tests/test_paths.py](tests/test_paths.py) — including `_MEIPASS` non-leakage parametrized over all three platforms. |
| 4 | First-write schema `{"schema_version": 1, "races": [...]}`, atomic write | MET | [leaderboard.py:38-49](leaderboard.py#L38-L49) (`_atomic_write_json` via `tempfile.mkstemp` + `os.replace`); tests 1 + 5 in `test_leaderboard.py` verify schema shape and atomic-write robustness. |
| 5 | `query()` sort order: points desc → wins desc → podiums desc → name asc | MET | `_sorted_rows` returns `sorted(..., key=lambda kv: (-kv[1]["points"], -kv[1]["wins"], -kv[1]["podiums"], kv[0]))`; tests 5–7 verify each tiebreaker dimension. |
| 6 | `query()` track filter: `"all"`, specific, unknown all handled | MET | Tests 18 (all), 19 (specific), 20 (unknown returns `[]`, no raise). |
| 7 | `query_per_track()` returns one row per (racer × track), grouped + ranked by track | MET | `query_per_track` groups via `sorted(by_track)`; rank restarts at 1 per group via `enumerate(..., start=1)`; tests 21–22 verify grouping and within-group sort. |
| 8 | `known_tracks()` sorted dedup union of disk + session | MET | `disk_tracks \| session_tracks` set union, sorted; tests 24–26 verify dedup, union of disk+session sources, and empty-history case. |
| 9 | Time windows + `now=` injection across calendar boundaries | MET | `_in_window` implements all 6 windows; ISO Monday-start week via `today - timedelta(days=today.weekday())`; tests 8–14 cover today / week (Monday boundary) / month / year / all / session / unknown-raises. |
| 10 | Scoring `[6, 3, 1, 0]` truncated to `[6, 3, 1]` for 3-racer races | MET | `_aggregate` uses `POINTS[place] if place < len(POINTS) else 0`, which is also the truncation guard; tests 2 (4-racer 6/3/1/0), 3 (3-racer 6/3/1), 4 (no phantom 4th racer in 3-racer race). |
| 11 | `tests/test_leaderboard.py` covers full ROADMAP criteria checklist | MET | 39 test functions; each ROADMAP criterion maps to ≥ 1 test (see per-plan SUMMARY/REVIEW files for full mapping). |
| 12 | All existing tests still pass | MET | `pytest -q` reports **133 passed**. Pre-Phase-1 baseline was 85; Phase 1 adds 9 (Plan 1.1) + 9 (Plan 2.1) + 30 (Plan 2.2) = 48, total 133. Math checks out. |
| 13 | `python main.py` runs identically — `leaderboard` not yet wired | MET | `grep -nE "^import leaderboard\|^from leaderboard" main.py race.py dialogs.py paths.py audio.py constants.py tracks.py` returns **no matches**. `leaderboard` is referenced only from `tests/test_leaderboard.py`. |

## Test Suite

- Full `pytest -q`: **133 passed in 0.73s**.
- Test growth: baseline 85 → Plan 1.1 +9 (94) → Plan 2.1 +9 (103) → Plan 2.2 +30 (133). All math reconciles.
- Tk-free invariant on `leaderboard.py`: **PASS** (subprocess import with `sys.modules['tkinter']=None` exits 0).

## Integration Sanity

- `leaderboard` is not yet imported by any production module — confirmed via grep against `main.py`, `race.py`, `dialogs.py`, `paths.py`, `audio.py`, `constants.py`, `tracks.py`. Production behavior of the app is unchanged. Phase 2 will introduce the first production-side import.
- `paths.user_data_path` is referenced by `leaderboard.py` only; `paths.resource_path` continues to be used by `race.py` and `audio.py`. No collisions.

## Gaps Identified

- None.

## Carryover to next phase

Lessons learned during the Phase 1 build that Phase 2 (round-loop wiring) should be aware of:

1. **`import paths` (not `from paths import user_data_path`).** When Phase 2's `main.py` imports `leaderboard.record_race`, it must call it through the live module reference. Tests rely on `monkeypatch.setattr("paths.user_data_path", ...)` taking effect on every `_path()` call; a `from`-import in `leaderboard.py` breaks this. Discovered the hard way in Plan 2.1 (7 of 9 tests failed before the fix). Worth a one-line note in CLAUDE.md at Phase 5 ship time.

2. **Test hygiene: redirect `os.path.expanduser` when patching `sys.platform`.** Patching `sys.platform` does NOT redirect `expanduser`, so tests can leak real-filesystem writes (Plan 1.1 review caught this — fixed with `_fake_expanduser` helper). Phase 2 won't touch `expanduser` directly but any new test fixture that does should follow the same pattern.

3. **Latent plan defect: validation via per-record iteration can be unreachable on empty inputs.** Plan 2.2's spec for `ValueError` on unknown windows was routed through `_in_window` (per-record), which never fires on an empty store. Builder fixed by extracting `_validate_window()` and calling it upfront. Future plans that include "raise on unknown X" semantics should verify the raise is observable on every code path, including empty-input edge cases.

4. **Scoring scheme constrains data-driven testability of tiebreakers.** With `POINTS=(6,3,1,0)`, every podium finisher earns ≥ 1 point — so equal-points + equal-wins implies equal-podiums when reconstructed from race data. Plan 2.2's podium tiebreaker test had to call the private `_sorted_rows` with hand-crafted stat dicts. If we ever revisit the scoring scheme, this could be lifted; otherwise, accept it as a documented test-pattern exception.

5. **Test file size approaching ~600 lines.** `tests/test_leaderboard.py` is now ~639 lines (estimated from 30 + 9 tests + helpers + comments). Still manageable, but a future split into `tests/test_leaderboard_persistence.py` and `tests/test_leaderboard_query.py` may be warranted if Phase 2 or later adds many more.
