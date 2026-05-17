# Plan Verification — Phase 2

## Verdict: PASS

## Coverage of Phase 2 success criteria (from ROADMAP.md)

| Criterion | Plan/Task | Status |
|---|---|---|
| Single `record_race(...)` call inserted between `run_race(...)` and `show_podium(...)` in `main.py` | PLAN-1.1 Task 1 | covered (CONTEXT-2 Decision 1 implements the placement) |
| Inline adapter `[racers[i]['name'] for i in finish_order]` for finish_order → names | PLAN-1.1 Task 1 (per CONTEXT-2 Decision 2) | covered |
| Species comes from existing per-round species selection; track from existing `track_name`; both already in scope at the insertion point | PLAN-1.1 Task 1 + RESEARCH §1 lists the in-scope variables | covered |
| After one race, `%APPDATA%\TurtleRace\leaderboard.json` exists with `schema_version: 1` and one race record | PLAN-1.1 Task 3 (Race Run #1) | covered |
| After three races, file contains three records in chronological order; at least one turtle and one snake race | PLAN-1.1 Task 3 (Runs #1–#3 with mandated species mix) | covered |
| Existing post-race messagebox flow unchanged — `ask_play_again` still Yes/No | PLAN-1.1 Task 1's "Hard constraints" forbid touching the outer loop or `ask_play_again` | covered |
| `pytest` remains green | All three task acceptance criteria require it; final count 135 (133 + 2 new from Task 2) | covered |
| Path-traversal basename guard on `paths.user_data_path` (auditor L1, deferred to Phase 2) | PLAN-1.1 Task 2 (per CONTEXT-2 Decision 4) | covered |

## Structural Checks

| Check | Result |
|---|---|
| Task count per plan | PLAN-1.1: 3 — within the ≤3 limit |
| Wave / dependency ordering | Single wave, single plan, sequential within | OK |
| Same-file parallel conflicts | N/A (only one plan in this phase) |
| Acceptance-criteria testability | All objective — pytest counts, grep results, JSON inspection commands, file diff stats |
| Verification commands | Concrete PowerShell + pytest invocations, including `git diff e38eb02..HEAD -- ...` (note: `e38eb02` predates Phase 1 — the architect appears to have used a pre-Phase-1 SHA; should be `cd2870f` for "after Phase 1" baseline. Non-blocking — the verification commands still work with any prior SHA as the diff anchor) |

## CONTEXT-2 Decision Coverage

| Decision | Implementation | Verdict |
|---|---|---|
| 1. Call before `show_podium` | PLAN-1.1 Task 1 specifies insertion immediately after `run_race` and before `show_podium`; "Hard constraints" forbid reordering | covered |
| 2. Inline adapter | PLAN-1.1 Task 1 shows the exact one-liner; "Hard constraints" forbid a separate `race.py` helper | covered |
| 3. Manual verification | PLAN-1.1 Task 3 is the dedicated verification task; protocol mandates ≥1 turtle race AND ≥1 snake race, observe-before-inspect ordering | covered |
| 4. Basename guard + tests | PLAN-1.1 Task 2 is TDD; tests first (red), then guard. Rejects `..`, `.`, embedded `/` or `\` separators. Raises `ValueError`, never sanitizes | covered |

## Scope Creep Findings

None. The plan does not touch `dialogs.py`, `race.py`, `constants.py`, `tracks.py`, the spec file, or any UI code. It modifies exactly `main.py`, `paths.py`, and appends to `tests/test_paths.py`. No new dependencies.

---

# Plan Critique — Feasibility Stress Test

## Verdict: READY

## Per-task feasibility

### Task 1 — `main.py` wiring

- **File path:** `main.py` exists (53 lines).
- **Insertion point:** confirmed — `main.py:38` is `winning_turtle, finish_order = race.run_race(racers, track_name, user_bet)`; `main.py:41` is `race.show_podium(racers, finish_order)`. The two new lines fit cleanly between them.
- **Variables in scope:** `racers`, `track_name`, `species`, `finish_order` all assigned by line 38 in the round body (per RESEARCH §1).
- **Import placement:** project-internal block at `main.py:8-10` is alphabetical (`audio`, `dialogs`, `race`). Inserting `import leaderboard` between `dialogs` and `race` preserves the order.
- **API surface:** `leaderboard.record_race(species, track, finish_order_names)` is the signature shipped in Phase 1 commit `3814dd5` — exact match for the plan's call.

### Task 2 — basename guard

- **File paths:** `paths.py` exists (27 lines after Phase 1); `tests/test_paths.py` exists (9 tests after Phase 1 hygiene fix).
- **API surface:** `paths.user_data_path(filename: str) -> str` exists. The guard is added at the top of the body, before the existing platform branching — no API change.
- **Existing test compatibility:** The 9 existing tests in `tests/test_paths.py` all pass arguments that are bare basenames (`"leaderboard.json"`, `"x"`). None will be rejected by the new guard.
- **Phase 1 leaderboard tests compatibility:** `leaderboard._path()` calls `paths.user_data_path(_FILENAME)` where `_FILENAME = "leaderboard.json"`. This basename passes the guard. The 39 tests in `tests/test_leaderboard.py` continue to pass.
- **Verify commands:** `python -c "import paths; paths.user_data_path('../evil')"` will exit with a non-zero status and a `ValueError` traceback — the architect's `Select-String 'ValueError'` check will fire.

### Task 3 — manual verification

- **Files referenced:** `.shipyard/phases/2/results/SUMMARY-1.1.md` does not yet exist — task explicitly creates it.
- **Test count claim:** "135 expected" = 133 baseline + 2 new (Task 2). Math checks out.
- **Race run feasibility:** The user is on Windows; `python main.py` runs the Tk + turtle + pygame app; `%APPDATA%\TurtleRace\leaderboard.json` is the standard Windows app-data path. All preconditions hold.

## Cross-task findings

- **No forward references between tasks.** Task 1 uses `leaderboard.record_race` (introduced in Phase 1). Task 2 is independent of Task 1 (different file). Task 3 depends on Tasks 1 and 2 both being applied — the plan correctly orders them sequentially.
- **No same-wave file conflict.** Each task touches a disjoint surface (`main.py` / `paths.py + tests/test_paths.py` / no code change). Sequential ordering eliminates any conflict concern.
- **Stale SHA in Verification block:** the architect's `git diff e38eb02..HEAD -- main.py paths.py tests/test_paths.py` command uses `e38eb02` as the anchor, which predates Phase 1. The correct anchor for "after Phase 1" is `cd2870f` (the cleanup commit) or `7eab897` (the Phase 1 build-complete commit). Non-blocking — the diff still works against any prior SHA, just produces more output than intended.

## Risk register

- **`record_race` raises if disk write fails** — the plan forbids wrapping the call in `try/except` (correct: persistence failure should be visible). On a misconfigured `%APPDATA%` (e.g. read-only filesystem, exotic permission setup), the game would crash on the first race. Acceptable risk — `%APPDATA%` is per-user writable by Windows convention; the auditor already noted this. Mitigation: the corrupt-file recovery path in `_quarantine_and_reset` (Phase 1) handles unparseable existing files; only a literal write failure (disk full, ACL denial) would propagate. No mitigation needed for Phase 2.
- **Stale leaderboard.json from previous Phase 1 manual smoke tests.** Task 3's "Pre-run setup" mandates the builder delete any existing file before Run #1. If the builder skips this, the JSON will already contain records from prior Phase 1 testing, and the "exactly N races after N runs" check will fail. The plan explicitly addresses this.

## Complexity flags

- 3 files touched: `main.py`, `paths.py`, `tests/test_paths.py` — well under the 10-file threshold.
- 2 directories: project root, `tests/` — well under the 3-directory threshold.
- No high-risk complexity.

## Headline

Plan is feasible and ready to build. One cosmetic note (stale SHA in the diff command, non-blocking). Builder should proceed with `/shipyard:build 2`.
