# Plan Critique — Phase 1

**Verdict:** **CAUTION** (one stale fact, no blocking issues)

(The shipyard:verifier plan-critique agent terminated mid-stream without persisting this file. Critique below was assembled by the orchestrator from direct codebase inspection that had already been performed during the planning session — RESEARCH.md was generated from the same source reads, so the findings here corroborate it rather than duplicate work.)

## Per-plan findings

### PLAN-1.1 — `paths.user_data_path()` + tests

- **File paths:** `paths.py` exists at the project root (7 lines, verified). `tests/test_paths.py` is correctly marked as new — no conflict with existing tests.
- **API surface:** `paths.resource_path()` exists with the expected signature ([paths.py:5-7](paths.py#L5-L7)). The plan correctly adds `user_data_path()` below it without modifying `resource_path`.
- **Verify commands:** Runnable. `pytest tests/test_paths.py -v` is the standard pattern used by existing tests. The `python -c "import sys; sys.modules['tkinter'] = None; import paths"` poisoning check works.
- **Risk:** none material.

### PLAN-2.1 — `leaderboard.py` skeleton + `record_race`

- **File paths:** `leaderboard.py` is new; `tests/test_leaderboard.py` is new. No conflicts.
- **API surface:** All references are to symbols the plan itself introduces (no external dependencies beyond `paths.user_data_path`).
- **Verify commands:** Runnable.
- **`paths.user_data_path` monkeypatch path:** Plan 2.1's `lb` fixture uses `monkeypatch.setattr("paths.user_data_path", lambda f: str(tmp_path / f))`. This is the **correct** path-string form — `paths.user_data_path` is a module-level function (after Plan 1.1 lands), so the dotted-string lookup resolves. The architect also wrapped the `leaderboard._path()` helper as a function (not a module-level constant) so the monkeypatch is observed on every call — this is a non-obvious correctness requirement that the architect explicitly called out in their summary.
- **Atomic write portability:** `tempfile.mkstemp(prefix=..., suffix=..., dir=target_dir)` + `os.replace(tmp_path, target)` is the right primitive on Windows. Confirmed against RESEARCH §8.
- **`datetime.fromisoformat`:** Used in Plan 2.2 (not 2.1), but verified — Python ≥ 3.7 accepts ISO strings without tz. The project ships as a PyInstaller exe; no Python version constraint is documented in `requirements.txt` but the project uses 3.10-style `int | None` type hints, so 3.10+ is in play. Safe.
- **Risk:** none material.

### PLAN-2.2 — query / reset / known_tracks + full test surface

- **File paths:** `leaderboard.py` (modified — depends on Plan 2.1's skeleton). `tests/test_leaderboard.py` (extended — depends on Plan 2.1's fixture).
- **API surface mismatch — `race.run_race`:** Plan 2.2 does not call `race.run_race`. Plan 2.1 doesn't either. The integration point (`finish_order_names = [racers[i]['name'] for i in finish_order]`) is documented for Phase 2 only. Not in scope for these critiques.
- **Track-name strings:** All test fixtures use lowercase `"straight"`, `"spiral"`, `"rectangular"`, matching [tracks.py:27-29](tracks.py#L27-L29).
- **Forward references between 2.1 and 2.2** — verified:
  - `_path()` → introduced in Plan 2.1 Task 1, used in Plan 2.2 Task 1 (`known_tracks`) and Task 2 (`reset_all` via `_atomic_write_json(_empty_store(), _path())`). ✓
  - `_empty_store()` → introduced in Plan 2.1 Task 1, used in Plan 2.2 Task 2 (`reset_all`). ✓
  - `_atomic_write_json(data, target)` → introduced in Plan 2.1 Task 1, used in Plan 2.2 Task 2 (`reset_all`). ✓
  - `_SESSION_RACES` → introduced in Plan 2.1 Task 1, mutated by `reset_session` (Plan 2.2 Task 2) and read by `query`/`known_tracks` (Plan 2.2 Task 1). ✓
  - `_load()` → introduced in Plan 2.1 Task 1, called by `query`/`known_tracks` (Plan 2.2 Task 1). ✓
  - `lb` pytest fixture → introduced in Plan 2.1 Task 2, reused in Plan 2.2 Task 3 with explicit "do not redefine" instruction. ✓
- **ISO-week math:** Plan 2.2 Task 1 specifies `today - timedelta(days=today.weekday())` (Monday is weekday=0). Test 9 (`test_week_window_iso_monday_start`) seeds dates relative to a Saturday `2026-05-16` and asserts Monday `2026-05-11` is in-window and previous Sunday `2026-05-10` is out. The math is correct for a non-DST date (no DST gotcha in May at this hour).
- **`now=` injection adherence:** `query` and `query_per_track` carry `*, now: datetime | None = None`; `record_race` does not. Matches CONTEXT-1 Decision 4 exactly.
- **`known_tracks` and `tracks` module:** Plan 2.2 Task 1 explicitly says "Do NOT import `tracks.TRACK_NAMES`"; Test 27 enforces this via source-text grep. Matches CONTEXT-1 Decision 5.
- **Test count claim — STALE:** Plan 2.1 and Plan 2.2 verification sections both say "existing 45 + …". Actual `pytest --collect-only -q` returns **85 tests collected**. Not a blocker; the arithmetic in the verification text is wrong but the substantive criterion ("all existing tests still pass") is unaffected. Builder should report the actual final count, which will be **85 + 7 + 9 + 30 = 131**.

## Cross-plan findings

- **Same-wave (`2.*`) file conflict:** Plans 2.1 and 2.2 both modify `leaderboard.py` and `tests/test_leaderboard.py`. The architect handled this correctly by declaring `Dependencies: Plan 2.1` in Plan 2.2, sequencing the work. The numbering `2.1` / `2.2` is logical-grouping, not parallelism — the builder must read the Dependencies block, not infer parallelism from the wave number.
- **Forward references:** All Plan-2.2 references to Plan-2.1 symbols are correctly introduced; see per-plan section above.
- **CONTEXT-1.md decision-to-code-shape spot-check:**
  - Decision 1 (local time, no tz): `datetime.now().isoformat(timespec="seconds")` — ✓
  - Decision 2 (ISO Monday-start week): `today - timedelta(days=today.weekday())` — ✓
  - Decision 3 (corrupt-file quarantine): `os.replace(_path(), quarantine_path)` + stderr print — ✓
  - Decision 4 (`now=` on query/query_per_track only): keyword-only param introduced; `record_race` excluded — ✓
  - Decision 5 (`known_tracks` history-only): explicit forbid of `import tracks`; Test 27 enforces — ✓

## Risk register

- **Stale "45 tests" arithmetic in Plan 2.1 / 2.2 Verification sections.** Mitigation: builder reports actual count. Non-blocking.
- **`record_race` writes to both session list and disk** — `query("all")` reads disk only, `query("session")` reads session only. Plan 2.2 Task 1 calls this out explicitly in a multi-paragraph comment after a self-correction (the architect initially wrote the wrong implementation and corrected it in-line). The builder must preserve that comment so a future reader does not "fix" the apparent inconsistency.
- **`monkeypatch.setattr("paths.user_data_path", ...)` resolution.** Tests rely on `leaderboard._path()` re-resolving the symbol on each call (rather than caching at import). This is correct per Plan 2.1, but a subtle invariant — if a future refactor inlines `_path()` or caches the result, tests will silently break. Mitigation: keep `_path()` as documented; consider adding a one-line comment in the implementation.
- **DST and `datetime.now()` naïveté.** Plan 2.2's calendar-week arithmetic uses `date.weekday()`, which is DST-immune (it's pure calendar). The `today/now` window check uses `datetime.now()` which is wall-clock; "today" can therefore have a different number of hours during DST transitions. No tests target this, but it's not a Phase 1 correctness issue — the user's tests will pass on any specific `now=fixed` value the test injects.

## Complexity flags

- File scope: 2 production files (`paths.py`, `leaderboard.py`) + 2 test files. 4 files total — well under the 10-file threshold.
- Directory crossing: project root + `tests/` — 2 directories, well under the 3-dir threshold.
- No high-risk complexity.

## Headline

Plans are feasible. One stale fact (existing test count), no blocking issues. Builder should proceed with `/shipyard:build 1`.
