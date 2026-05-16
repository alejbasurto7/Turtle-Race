# Plan 2.2: leaderboard.py query + reset + known_tracks

## Context

Extend `leaderboard.py` with the read/reset surface: `query()`, `query_per_track()`, `known_tracks()`, `reset_session()`, and `reset_all()`. All calendar-window arithmetic, scoring (including 3-racer truncation), tiebreaker ordering, and species/track filtering live here. After this plan, Phase 1's success criteria are fully met and the module is ready to be wired into the round loop by Phase 2.

## Dependencies

- Plan 2.1 (`leaderboard.py` persistence skeleton + `record_race` + `_load` / `_save` / `_SESSION_RACES`).
- Plan 1.1 (transitively, via Plan 2.1).

## Tasks

### Task 1: Implement `query`, `query_per_track`, and `known_tracks`
**Files:** `leaderboard.py`
**Action:** modify
**TDD:** false
**Description:**

Add the read surface to `leaderboard.py` below the existing `record_race`. Use `dataclasses.dataclass(frozen=True)` for the row types — natural fit per CONTEXT-1.md "Open Questions Left for the Architect". Add `from dataclasses import dataclass` to the import block.

**Row types** (module-level, public, frozen):

```python
@dataclass(frozen=True)
class Row:
    rank: int
    racer_name: str
    species: str
    points: int
    races: int
    wins: int
    podiums: int

@dataclass(frozen=True)
class PerTrackRow:
    track: str
    rank: int
    racer_name: str
    species: str
    points: int
    races: int
    wins: int
    podiums: int
```

`PerTrackRow.rank` is the rank **within its track group** (restarts at 1 for each track), per PROJECT.md and ROADMAP.md Phase 4 success criteria.

**Private helpers:**

1. `_all_races() -> list[dict]` — returns `_load()["races"] + _SESSION_RACES`. Why concatenate rather than mutate the loaded store: session races are appended to disk by `record_race` already, so they would appear twice if we re-added them. Wait — re-read Plan 2.1: `record_race` appends to BOTH `_SESSION_RACES` and the on-disk store. So `_load()["races"]` already contains the current session's records. Therefore `_all_races()` should return just `_load()["races"]` and `_SESSION_RACES` is used ONLY for the `"session"` time-window filter to distinguish in-process records from prior-run records. Implement accordingly:
   - For non-"session" queries, the data source is `_load()["races"]`.
   - For "session" queries, the data source is `_SESSION_RACES`.
   - For `known_tracks()`, the data source is the union of both (deduped via `set`), per CONTEXT-1.md Decision 5 wording "(on-disk races) ∪ (current-session races)" — this union is still correct because Python set semantics dedupe the overlap.

   Capture this distinction explicitly: implement `_races_for_window(window: str) -> list[dict]` that returns `list(_SESSION_RACES)` for `window == "session"` and `_load()["races"]` otherwise.

2. `_in_window(ts_str: str, window: str, now: datetime) -> bool` — given an ISO-no-suffix timestamp string and a window key, return whether the record falls inside the window:
   - `"all"`: always True.
   - `"session"`: always True (caller already restricted to `_SESSION_RACES`, but accept the case defensively).
   - `"today"`: `datetime.fromisoformat(ts_str).date() == now.date()`.
   - `"week"`: ISO Monday-start per CONTEXT-1.md Decision 2. Compute `today = now.date()`; `week_start = today - timedelta(days=today.weekday())`; `week_end_exclusive = week_start + timedelta(days=7)`; check `week_start <= record_date < week_end_exclusive`.
   - `"month"`: same calendar month and year as `now`.
   - `"year"`: same calendar year as `now`.
   - For unknown window strings, raise `ValueError(f"unknown time_window: {window}")`.

3. `_species_matches(record_species: str, species_filter: str) -> bool` — `species_filter in ("all", record_species)`. Treats unknown filter values as "no match" (so an unknown filter returns an empty result, not a raise; this is consistent with the track filter behavior in ROADMAP success criteria).

4. `_aggregate(records: list[dict]) -> dict[str, dict]` — pure scoring/aggregation. For each record, iterate `enumerate(record["finish_order"])`:
   - `place = i` (0-based index)
   - `points = POINTS[place] if place < len(POINTS) else 0` — handles the 3-racer truncation cleanly: for a 3-element finish_order, places 0/1/2 get 6/3/1 and no 0-slot is consumed.
   - For each racer name, accumulate into a dict keyed by name:
     ```python
     {"species": record["species"], "points": ..., "races": ..., "wins": ..., "podiums": ...}
     ```
     - `races` increments by 1.
     - `wins` increments by 1 if `place == 0`.
     - `podiums` increments by 1 if `place < 3`.
     - `points` increments by the awarded points.
   - First-seen species wins (don't reassign; a racer name should not appear in two species, but if it ever did we don't fight about it).

5. `_sorted_rows(stats: dict[str, dict]) -> list[tuple[str, dict]]` — return `(name, stat)` pairs sorted by `(-points, -wins, -podiums, name)`. Returning the tuple list rather than `Row` objects directly lets the caller assign rank numbers without re-sorting.

**Public functions:**

```python
def query(time_window: str,
          species_filter: str = "all",
          track_filter: str = "all",
          *, now: datetime | None = None) -> list[Row]:
```

- `if now is None: now = datetime.now()` (CONTEXT-1 Decision 4 — `now=` is the only injection point).
- Get `records = _races_for_window(time_window)`.
- Filter by `_in_window(r["ts"], time_window, now)`, `_species_matches(r["species"], species_filter)`, and track filter:
  - `track_filter == "all"` → keep all.
  - otherwise → keep iff `r["track"] == track_filter` (unknown track names → empty result, no raise).
- Pass surviving records to `_aggregate`.
- Sort via `_sorted_rows`.
- Assign 1-based rank in sort order and return `[Row(rank=i+1, racer_name=name, **stats) for i, (name, stats) in enumerate(sorted_pairs)]`.

```python
def query_per_track(time_window: str,
                    species_filter: str = "all",
                    *, now: datetime | None = None) -> list[PerTrackRow]:
```

- Same `now` defaulting and window/species filtering as above.
- Group surviving records by `record["track"]`.
- For each track group (iterate in `sorted(tracks)` order), run `_aggregate` and `_sorted_rows`, then assign rank 1..N **within the track group**.
- Emit `PerTrackRow` rows with `track=track_name`, `rank=rank_within_group`, and the same per-racer stats.

```python
def known_tracks() -> list[str]:
```

- Union the `track` values from `_load()["races"]` and `_SESSION_RACES` (CONTEXT-1 Decision 5 — derive from history only; do NOT import `tracks.TRACK_NAMES`).
- Return `sorted(set(...))`.
- Fresh install with no races → `[]`.

**Edge cases to handle explicitly:**
- Empty record set after filtering → return `[]` (both `query` and `query_per_track`).
- A racer that finishes 4th in a 4-racer race (0 points): they still appear in the result with `races=1, points=0, wins=0, podiums=0`. The 0-point slot is "consumed" in the sense that the racer is counted; the only place 4-slot truncation matters is when `len(finish_order) < 4`, in which case the 4th racer simply doesn't exist.
- `query(time_window="session", ...)` reads `_SESSION_RACES`, NOT `_load()`. After `reset_session()` (Task 2), session queries return `[]` even if disk has data.

**Acceptance Criteria:**
- `query("all")` returns rows sorted by (points desc, wins desc, podiums desc, name asc).
- `query("session", ...)` reads only `_SESSION_RACES`.
- `query("week", ..., now=fixed_datetime)` correctly classifies a record on the previous Sunday as out-of-window and a record on the current Monday as in-window when `fixed_datetime` is a Tuesday.
- 3-element `finish_order` records award 6/3/1 (no 0-slot consumption).
- 4-element records award 6/3/1/0.
- `known_tracks()` returns sorted dedup union of disk + session track values.
- All three functions are pure with respect to module state (no writes); `_SESSION_RACES` is read but not mutated by query/known_tracks.

### Task 2: Implement `reset_session` and `reset_all`
**Files:** `leaderboard.py`
**Action:** modify
**TDD:** false
**Description:**

Add the two reset functions at the bottom of `leaderboard.py`:

```python
def reset_session() -> None:
    _SESSION_RACES.clear()
```

- Clears the in-memory session list ONLY. The on-disk JSON file is untouched.
- Subsequent `query("session", ...)` returns `[]`.
- Subsequent `query("all", ...)` still returns all historic records (including those recorded in this session prior to the reset — they remain on disk).
- `known_tracks()` may still include tracks that no longer appear in session, since `_load()` will still surface them.

```python
def reset_all() -> None:
    _SESSION_RACES.clear()
    _atomic_write_json(_empty_store(), _path())
```

- Wipes both: in-memory session + on-disk file (replaced with `{"schema_version": 1, "races": []}`).
- Uses the same atomic write helper from Plan 2.1 — no separate code path. This is required for the Phase 4 confirmation copy "Delete all race history? This cannot be undone."
- After `reset_all()`: `known_tracks()` returns `[]`, `query("all")` returns `[]`, the file on disk is non-empty (contains the empty store), not missing.

**Acceptance Criteria:**
- `reset_session()` clears `_SESSION_RACES` and does not modify the on-disk file (verify by hashing the file bytes before and after).
- `reset_all()` overwrites the on-disk file with `_empty_store()` and clears `_SESSION_RACES`.
- Neither function raises.

### Task 3: Test the full read/reset surface in `tests/test_leaderboard.py`
**Files:** `tests/test_leaderboard.py`
**Action:** modify
**TDD:** false
**Description:**

Extend `tests/test_leaderboard.py` (already created by Plan 2.1) by appending tests below a banner `# --- Query + reset surface ---`. Reuse the `lb` fixture from Plan 2.1; do not redefine it.

**Helper for building histories** (define once inside the test file, below the `lb` fixture):

```python
def _seed(lb, *records):
    """Write a list of (ts_iso, species, track, finish_order_list) records directly to disk and session."""
    import json
    store = {"schema_version": 1, "races": [
        {"ts": ts, "species": s, "track": t, "finish_order": list(fo)}
        for (ts, s, t, fo) in records
    ]}
    with open(lb._path(), "w", encoding="utf-8") as f:
        json.dump(store, f)
```

This bypasses `record_race` so tests can plant timestamps in the past for time-window coverage without monkeypatching `datetime.now()`.

**Required tests (group by ROADMAP Phase 1 success-criteria checklist):**

Empty state:
1. `test_query_empty_state_returns_empty_list(lb)` — no records on disk, no session; `lb.query("all") == []` and `lb.query_per_track("all") == []` and `lb.known_tracks() == []`.

Scoring:
2. `test_query_awards_six_three_one_zero_for_four_racer_race(lb)` — seed one race `("turtles","straight",["A","B","C","D"])`; assert rows have points 6/3/1/0 in that name order.
3. `test_query_truncates_to_six_three_one_for_three_racer_race(lb)` — seed one race `("snakes","straight",["X","Y","Z"])`; assert exactly 3 rows with points 6/3/1; no 0-point row appears (no phantom 4th racer).
4. `test_query_fourth_place_consumed_only_when_four_finishers(lb)` — seed one 3-racer race; assert the result has 3 rows total (not 4 with a 0-point ghost).

Tiebreakers (sort order: points desc → wins desc → podiums desc → name asc):
5. `test_tiebreak_by_wins(lb)` — seed two races where racer "Alice" finishes 1st and 4th (7 points: 6+1? no — 6+0=6 wait; rebuild: 1st=6 + 3rd=1 = 7) and racer "Bob" finishes 2nd twice (3+3=6). Adjust seed so Alice and Bob tie on points but Alice has 1 win and Bob has 0. Concretely: seed `[A,B,C,D]` and `[B,A,C,D]` → A: 6+3=9 wins=1; B: 3+6=9 wins=1; still tied. Better example: seed `[A,B,C,D]` (A=6 wins=1 podiums=1) and `[B,A,C,D]` (A=3 wins=0 podiums=1; B=6 wins=1 podiums=1). A total: 9 points, 1 win, 2 podiums. B total: 9 points, 1 win, 2 podiums. Still tied → name decides → Alice before Bob. **Construct a cleaner case in the test:** seed three races where racer "Zed" wins twice (6+6+0=12, wins=2) and racer "Ann" places second three times (3+3+3=9, wins=0). Then a separate pair to force the tie: seed `[X,Y,...]` with X getting 9 points 1 win and Y getting 9 points 0 wins; assert X ranks above Y.
6. `test_tiebreak_by_podiums_when_wins_equal(lb)` — construct two racers tied on points and wins, differing only in podiums; assert the higher-podium racer ranks first.
7. `test_tiebreak_by_name_when_all_else_equal(lb)` — two racers identical in all stats; alphabetically earlier name ranks first.

Time windows (use a fixed `now=datetime(2026,5,16,14,0,0)` — a **Saturday**):
8. `test_today_window(lb)` — seed a record at `2026-05-16T01:00:00` (same date) and one at `2026-05-15T23:59:00` (yesterday); call `query("today", now=fixed)`; assert only the same-date record contributes.
9. `test_week_window_iso_monday_start(lb)` — seed records at `2026-05-11T08:00:00` (Monday of current ISO week — in window), `2026-05-10T23:59:00` (previous Sunday — out of window), `2026-05-17T23:59:00` (Sunday end of current week — in window), `2026-05-18T00:00:00` (next Monday — out of window). Call with `now=2026-05-16T14:00:00` (Saturday). Assert: 2 records in window; 2 records out.
10. `test_month_window(lb)` — seed records in May 2026 (in), April 2026 (out), June 2026 (out); assert only May records contribute.
11. `test_year_window(lb)` — seed records in 2026 (in) and 2025 (out); assert only 2026.
12. `test_all_window_returns_everything(lb)` — seed records spanning multiple years; `query("all", now=fixed)` returns rows from every record.
13. `test_session_window_reads_session_not_disk(lb)` — seed disk via `_seed` with one race; call `record_race` with a different race; assert `query("session", now=fixed)` contains only the recorded one, not the seeded one; `query("all")` contains both.
14. `test_unknown_time_window_raises(lb)` — `query("decade", now=fixed)` raises `ValueError`.

Species filter:
15. `test_species_filter_all(lb)` — seed one turtle and one snake race; `query("all", species_filter="all")` returns racers from both.
16. `test_species_filter_turtles_only(lb)` — same seed; `query("all", species_filter="turtles")` returns only turtle racers.
17. `test_species_filter_snakes_only(lb)` — same seed; `query("all", species_filter="snakes")` returns only snake racers.

Track filter:
18. `test_track_filter_all(lb)` — seed races on `straight` and `spiral`; `query("all", track_filter="all")` returns racers from both.
19. `test_track_filter_specific(lb)` — same seed; `query("all", track_filter="straight")` returns only racers from straight races.
20. `test_track_filter_unknown_returns_empty(lb)` — same seed; `query("all", track_filter="bogus_track")` returns `[]` and does not raise.

Per-track query:
21. `test_query_per_track_groups_by_track(lb)` — seed races on `spiral` and `straight`; assert the result is grouped (all spiral rows then all straight rows — alphabetical track order), and each group's first row has `rank=1`.
22. `test_query_per_track_within_group_sort_matches_query(lb)` — within a single track group, ordering follows the same points/wins/podiums/name tiebreakers as `query()`.
23. `test_query_per_track_species_filter(lb)` — seed mixed species; `query_per_track("all", species_filter="turtles")` returns only turtle rows.

Known tracks:
24. `test_known_tracks_dedup_and_sort(lb)` — seed races on `spiral`, `straight`, `spiral` (duplicate); `known_tracks() == ["spiral", "straight"]`.
25. `test_known_tracks_union_disk_and_session(lb)` — seed `straight` on disk via `_seed`; call `record_race` with `spiral`; assert `known_tracks() == ["spiral", "straight"]`.
26. `test_known_tracks_empty_when_no_history(lb)` — fresh `lb`, no records; `known_tracks() == []`.
27. `test_known_tracks_does_not_import_tracks_module()` — read `leaderboard.py` source as text; assert `"import tracks"` and `"from tracks"` are not present. Enforces CONTEXT-1 Decision 5.

Reset:
28. `test_reset_session_clears_session_leaves_file(lb, tmp_path)` — `record_race` twice (records appear on both disk and session); read the file bytes; call `reset_session()`; read the file bytes again; assert equal; assert `_SESSION_RACES == []`; assert `query("all")` still returns both racers.
29. `test_reset_all_wipes_disk_and_session(lb, tmp_path)` — `record_race` twice; call `reset_all()`; assert `(tmp_path / "leaderboard.json").exists()`; load JSON and assert `{"schema_version": 1, "races": []}`; assert `_SESSION_RACES == []`; assert `query("all") == []`; assert `known_tracks() == []`.

Missing file & corrupt file (already covered in Plan 2.1, but re-verify the end-to-end now that query exists):
30. `test_query_on_fresh_install_returns_empty(lb)` — no file present; `query("all") == []` and `query("session") == []` and the call did not create the file (matches Plan 2.1 test 6 but exercised through the public query surface).

**Acceptance Criteria:**
- `pytest tests/test_leaderboard.py -v` reports the Plan 2.1 tests (9) + these (30) = 39 passed.
- Each ROADMAP Phase 1 success-criteria checkbox maps to at least one test (cross-reference the test names against the checklist).
- The Tk-free invariant test from Plan 2.1 still passes after adding dataclass imports.

## Verification

```powershell
pytest tests/test_leaderboard.py -v
pytest                                              # full suite green
python -c "import sys; sys.modules['tkinter'] = None; import leaderboard; print(leaderboard.query('all'))"
python main.py                                      # app still runs unchanged (close window after main menu / track selection)
```

Expected:
- `pytest tests/test_leaderboard.py -v` reports 39 passed.
- Full `pytest` reports green: existing 45 + Plan 1.1 (7) + Plan 2.1 (9) + Plan 2.2 (30) = 91+ tests pass.
- The Tk-poisoning import still succeeds (`dataclasses` is stdlib and Tk-free).
- `python main.py` launches and runs identically to before — `leaderboard.py` is not yet wired into `main.py` (that's Phase 2). This satisfies ROADMAP Phase 1's "App still runs identically" criterion.

**ROADMAP Phase 1 success-criteria checklist** (copy here so the builder has the full checkbox set to verify):
- [ ] `leaderboard.py` exists with the seven public functions.
- [ ] `import leaderboard` succeeds with `tkinter` poisoned in `sys.modules`.
- [ ] `paths.user_data_path` returns correct paths per platform and never under `_MEIPASS` (Plan 1.1).
- [ ] First-write schema is `{"schema_version": 1, "races": [...]}` with atomic write (Plan 2.1).
- [ ] `query()` sort order: points desc → wins desc → podiums desc → name asc.
- [ ] `query()` track filter: `all`, specific, unknown all handled.
- [ ] `query_per_track()` returns one row per (racer × track) with within-group ranks, sorted by track asc.
- [ ] `known_tracks()` returns sorted dedup union of on-disk + session track values.
- [ ] Time windows `session | today | week | month | year | all` each correct across calendar boundaries via `now=` injection.
- [ ] Scoring `[6, 3, 1, 0]` truncated to `[6, 3, 1]` for 3-racer races.
- [ ] `tests/test_leaderboard.py` covers: empty-state, 1st-place, 4th-place 0-slot, 3-racer truncation, tiebreak via wins/podiums/name, time windows across boundaries (stdlib only via `now=`), species filter, track filter (all/specific/unknown), `query_per_track` grouping + within-group order, `known_tracks` dedup+sort, `reset_session` leaves file intact, `reset_all` wipes both, missing-file auto-creation, corrupt-file recovery with stderr warning.
- [ ] All existing tests still pass.
- [ ] `python main.py` runs identically (module is unused at runtime in Phase 1).

Cross-references:
- CONTEXT-1.md Decisions 2 (ISO week), 4 (`now=` injection), 5 (`known_tracks` derived from history only) are all implemented here.
- Plan 2.1 owns Decisions 1 (timestamp format) and 3 (corrupt-file quarantine).
- RESEARCH §3 (track names are lowercase strings — `"straight"`, `"rectangular"`, `"spiral"`) and §4 (test conventions) inform the test fixtures.
