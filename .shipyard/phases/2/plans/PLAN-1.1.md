# Plan 1.1: Wire `record_race` into the round loop + harden `paths.user_data_path`

## Context

Phase 1 shipped a Tk-free `leaderboard.py` (record / query / reset / known_tracks) and a `paths.user_data_path()` helper. Both currently have zero production-side callers. Phase 2's job is to flip the switch:

1. Insert a single `leaderboard.record_race(...)` call into `main.py`'s round body so every completed race is persisted to `%APPDATA%\TurtleRace\leaderboard.json`.
2. Add a defensive basename guard to `paths.user_data_path()` (deferred from Phase 1 wrap per the auditor's L1 finding) now that production callers are in play.
3. Manually verify three end-to-end race runs (at least one turtle, at least one snake) write the expected JSON state.

No UI changes, no outer-loop restructure, no `turtle_race.spec` change, no new dependencies. The existing `ask_play_again` messagebox stays — Phase 3 owns the menu restructure.

This plan is sized to a single wave with three sequential tasks. Task 2 (paths guard) is logically independent of Task 1 (the wiring) — both touch disjoint files — but the manual verification in Task 3 depends on both being applied, and the work is so small (single-digit-minute tasks) that parallelizing across two plans would cost more orchestration than it saves. All three tasks stay in one plan, executed in order, producing three atomic commits under `git_strategy: per_task`.

## Dependencies

- Phase 1 complete (commit `cd2870f` baseline, 133 tests green). This plan imports `leaderboard.record_race` (added in Plan 1.2 of Phase 1) and modifies `paths.user_data_path` (added in Plan 1.1 of Phase 1).
- No dependencies on any other Phase 2 plan (this is the only plan in Phase 2).

## Tasks

### Task 1: Wire `leaderboard.record_race` into the round loop in `main.py`

**Files:** `main.py`
**Action:** modify
**TDD:** false
**Description:**

Insert exactly one new import and exactly two new lines of round-body code into `main.py`. No other changes — do not refactor surrounding lines, do not rename variables, do not touch the outer `while keep_playing` loop shape.

**Import change (per CONTEXT-2 §"Open Questions" and RESEARCH §2):**

Insert `import leaderboard` between `import dialogs` and `import race` in the project-internal import block, preserving alphabetical order:

```python
import audio
import dialogs
import leaderboard
import race
```

Use the bare-module form (`import leaderboard`), not `from leaderboard import record_race`, per CONTEXT-2 carryover note from Phase 1.

**Round-body change (per CONTEXT-2 Decision 1 + Decision 2, RESEARCH §1):**

The current sequence at `main.py:38-41` is:

```python
winning_turtle, finish_order = race.run_race(racers, track_name, user_bet)

user_won = winning_turtle is racers[user_bet - 1]['o']
race.show_podium(racers, finish_order)
```

Insert two lines between the `run_race` call and the `user_won` assignment, so the resulting shape is:

```python
winning_turtle, finish_order = race.run_race(racers, track_name, user_bet)

finish_order_names = [racers[i]['name'] for i in finish_order]
leaderboard.record_race(species, track_name, finish_order_names)

user_won = winning_turtle is racers[user_bet - 1]['o']
race.show_podium(racers, finish_order)
```

**Hard constraints:**

- The `record_race` call MUST be placed before `race.show_podium(...)` — per CONTEXT-2 Decision 1, this ensures the result is recorded on disk even if `show_podium`, `celebrate`, or `announce_result` raises.
- Do NOT wrap the `record_race` call in `try`/`except`. If persistence fails, the user must see it — Phase 1's `record_race` is responsible for graceful corrupt-file recovery; uncaught exceptions here would indicate a real bug (e.g., the basename guard fired on the literal string `"leaderboard.json"`, which would mean someone broke the guard).
- Do NOT introduce any new local variable beyond `finish_order_names`.
- Do NOT modify any line outside the import block and the round body (lines 38-41 region). Specifically, do not touch `user_won`, `show_podium`, `celebrate`, `announce_result`, `ask_play_again`, or the outer loop.
- `species` (str), `track_name` (str), and `racers` (list of dicts with `'name'` key) are already in scope at the insertion point per RESEARCH §1 — no parameter passing required.

**Acceptance Criteria:**

- `python -c "import main"` succeeds without error (verifies the import block is well-formed; does not run `main()`).
- `git diff main.py` shows exactly one added import line and three added body lines (the comprehension, the `record_race` call, and one blank line separator — total 4 added lines; zero deletions; zero modifications to existing lines).
- `pytest` reports 133 tests still green (no test depends on `main.py` import side effects, so adding the import is safe).
- A grep for `record_race` in `main.py` returns exactly one hit (the new call). A grep for `import leaderboard` returns exactly one hit.

---

### Task 2: Add basename guard to `paths.user_data_path` + two tests

**Files:** `paths.py`, `tests/test_paths.py`
**Action:** modify (both)
**TDD:** true — write the two tests first; they should fail (because the guard does not yet exist); then add the guard; they pass.
**Description:**

Per CONTEXT-2 Decision 4 and RESEARCH §3, add a defensive basename guard to `paths.user_data_path()` that rejects (does not sanitize) any `filename` argument that contains a path separator, parent traversal, or is the bare strings `"."` / `".."`.

**Test additions (write first; expect failure before guard is added):**

Append two new test functions to `tests/test_paths.py` under a new comment banner:

```python
# --- Filename validation (Phase 2 basename guard) ---
```

1. **`test_user_data_path_rejects_path_separator()`** — assert `pytest.raises(ValueError)` for input `"subdir/x.txt"`. On Windows hosts the test should ALSO assert `pytest.raises(ValueError)` for `"subdir\\x.txt"` (use `os.sep` to construct the second input portably — i.e., the test should additionally check an input built as `f"subdir{os.sep}x.txt"` so it covers the active platform separator regardless of host OS).
2. **`test_user_data_path_rejects_parent_traversal()`** — assert `pytest.raises(ValueError)` for input `"../evil"` AND for input `".."` (the bare-traversal case). Use two separate `with pytest.raises(ValueError):` blocks within one test function.

Both tests need `import pytest` at the top of the file if not already present (the existing `tests/test_paths.py` may already import it; check before adding).

Neither test should require `monkeypatch` for `sys.platform` — the guard fires before any platform branching, so the tests pass on every host.

**Guard implementation (add only after the two tests are red):**

Add the guard as the very first executable statement inside `user_data_path()`, before the `sys.platform` branching:

```python
def user_data_path(filename: str) -> str:
    # Reject any filename containing a path separator or parent-traversal token.
    # Callers must pass a bare basename (e.g. "leaderboard.json"); sanitization is
    # harder to reason about than rejection, so we reject and let the caller fix
    # the call site. Guards against accidental misuse by future callers.
    if (
        os.path.basename(filename) != filename
        or filename in (".", "..")
        or os.sep in filename
        or (os.altsep is not None and os.altsep in filename)
    ):
        raise ValueError(
            f"user_data_path requires a bare filename (no path separators or traversal), got: {filename!r}"
        )
    # ... existing platform branching unchanged ...
```

**Hard constraints:**

- The guard MUST raise `ValueError`, not return a sanitized path or `None`.
- The error message MUST include the offending input via `repr()` so the caller can see what was rejected.
- The guard MUST execute before `os.makedirs(...)` — never create the TurtleRace directory if the input is going to be rejected anyway.
- Do NOT modify any line of `user_data_path` outside the guard insertion. The existing Windows / macOS / Linux branches stay exactly as Phase 1 shipped them.
- Do NOT modify `resource_path()` — only `user_data_path()`.
- The existing 9 tests in `tests/test_paths.py` must remain unchanged and green. The two new tests append at the bottom of the file.
- Production callers in Phase 1's `leaderboard.py` pass the literal basename `"leaderboard.json"`, which the guard MUST accept — verify by running the full pytest suite (which exercises `leaderboard.py` via `tests/test_leaderboard.py`).

**Acceptance Criteria:**

- `pytest tests/test_paths.py -v` reports 11 tests passing (9 existing + 2 new).
- `pytest` (full suite) reports 135 tests passing (133 baseline + 2 new). No existing test fails — in particular, the Phase 1 leaderboard tests continue to pass, confirming the basename `"leaderboard.json"` survives the guard.
- `git diff paths.py` shows only the guard block added at the top of `user_data_path`'s body — no other lines touched.
- `git diff tests/test_paths.py` shows only the comment banner + two new test functions appended — no existing tests modified.
- A direct sanity invocation `python -c "import paths; paths.user_data_path('../evil')"` exits with `ValueError` (non-zero exit code). A `python -c "import paths; print(paths.user_data_path('leaderboard.json'))"` still prints a normal path.

---

### Task 3: Manual end-to-end verification + write protocol into `SUMMARY-1.1.md`

**Files:** `.shipyard/phases/2/results/SUMMARY-1.1.md` (created by builder during verification; the file itself is not a code file)
**Action:** verify + document
**TDD:** false
**Description:**

Per CONTEXT-2 Decision 3 and RESEARCH §5, the wiring change in Task 1 has no automated test — `main.py` is the live Tk/turtle/pygame entry point and cannot be unit-tested without disproportionate scaffolding. Instead, the builder performs a documented manual verification of three race runs and captures the evidence in the builder's `SUMMARY-1.1.md` artifact.

**Verification protocol (the builder MUST follow this exact sequence):**

**Pre-run setup:**

1. Delete any existing `%APPDATA%\TurtleRace\leaderboard.json` so the test starts from a clean slate. Record in the summary whether the file existed before deletion.
2. Confirm the working tree contains the Task 1 and Task 2 commits (run `git log --oneline -3`).

**Race Run #1 — TURTLE race:**

1. Launch the app: `python main.py`.
2. Pick any track. Pick **Turtles**. Pick any racer to bet on.
3. Let the race finish.
4. Observe and write down in `SUMMARY-1.1.md`:
   - Track name selected.
   - Species: `turtles`.
   - The on-screen podium finishing order (1st, 2nd, 3rd, 4th) — racer names exactly as shown.
5. Click "No" on the "play again?" messagebox to exit.
6. Open `%APPDATA%\TurtleRace\leaderboard.json` in a text editor. Copy its contents into `SUMMARY-1.1.md` under "Run #1 — JSON state".
7. Verify (and assert in the summary):
   - `schema_version` is `1`.
   - `races` array length is exactly `1`.
   - The single record's `species` is `"turtles"`, `track` matches the track selected, and `finish_order` is a list of 4 strings matching the observed podium order.
   - `ts` is an ISO-format timestamp at or near the current local clock.

**Race Run #2 — SNAKE race:**

1. Launch `python main.py` again.
2. Pick any track. Pick **Snakes**. Pick any racer to bet on.
3. Let the race finish. Click "No" to exit.
4. Record the same observations as Run #1 (track, species=`snakes`, podium order — note this is 3 racers, not 4).
5. Open the JSON file again, copy its contents into `SUMMARY-1.1.md` under "Run #2 — JSON state".
6. Verify:
   - `races` array length is now exactly `2`.
   - The new (second) record's `species` is `"snakes"`, `track` matches, `finish_order` is a list of exactly 3 strings matching the observed podium.
   - The first record from Run #1 is still present and unchanged.
   - The two records' timestamps are in non-decreasing order.

**Race Run #3 — second TURTLE race (or another snake race; builder picks):**

1. Launch `python main.py` again. Pick any combination.
2. Let the race finish. Click "No" to exit.
3. Same observation + verification as above. JSON should now contain exactly 3 records in chronological order.

**Test-suite verification (in addition to manual race runs):**

4. Run `pytest` from the project root after the three race runs. Expect 135 tests passing (133 baseline + 2 new from Task 2). Paste the final pytest summary line into `SUMMARY-1.1.md`.

**Cleanup decision:**

5. After verification, the builder MAY delete `%APPDATA%\TurtleRace\leaderboard.json` (it has no production value yet — Phase 3+ will fully exercise it). If the builder leaves the file in place, document that in `SUMMARY-1.1.md` so Phase 3's builder knows the starting state.

**Hard constraints:**

- The three race runs MUST cover at least one turtle race AND at least one snake race (per CONTEXT-2 Decision 3 — "at least one turtle race and one snake race").
- The builder MUST inspect the JSON file with their own eyes — not assume the call worked because no exception was raised.
- If ANY of the JSON state checks fails (wrong record count, wrong species string, wrong finish_order, missing schema_version), STOP the verification, do not edit the production code from inside Task 3, and surface the discrepancy via the verifier/debugger workflow.
- If the pytest suite is not green at the end, STOP and surface to the debugger workflow. Task 3 does not modify code; any test failure is a regression from Task 1 or Task 2 and must be diagnosed before this plan is considered complete.
- Document each run's observations BEFORE inspecting the JSON file (don't reverse-engineer the "observed podium" from the JSON contents — the point of this verification is to compare two independent observations).

**Acceptance Criteria:**

- `.shipyard/phases/2/results/SUMMARY-1.1.md` exists and contains, at minimum:
  - A "Verification Protocol" section restating the three-run scheme.
  - A "Run #1 — Observations" block (track, species, podium) and "Run #1 — JSON state" block (the JSON file contents).
  - The same pair of blocks for Run #2 and Run #3.
  - A "Cross-check" subsection per run confirming species / track / finish_order match between observation and JSON.
  - A final "pytest" subsection showing the test count (135 expected) and pass/fail status.
- Across the three runs, at least one race is `species: "turtles"` with a 4-entry `finish_order`, and at least one race is `species: "snakes"` with a 3-entry `finish_order`. This validates the scoring truncation invariant (`[6,3,1,0]` → `[6,3,1]` for 3-racer races) by exercising the recording path.
- `pytest` final summary shows 135 passed, 0 failed.

## Verification

Run from the project root after all three tasks are committed:

```powershell
# Static sanity
git log --oneline -3
python -c "import main"                         # imports clean, including new `import leaderboard`
python -c "import paths; print(paths.user_data_path('leaderboard.json'))"
python -c "import paths; paths.user_data_path('../evil')" 2>&1 | Select-String 'ValueError'

# Test suite
pytest                                          # full suite
pytest tests/test_paths.py -v                   # focused

# Diff inspection
git diff e38eb02..HEAD -- main.py paths.py tests/test_paths.py
```

Expected:

- `git log --oneline -3` shows three new commits (one per task) on top of `e38eb02`.
- `python -c "import main"` exits 0 with no output.
- The `paths.user_data_path('leaderboard.json')` invocation prints a path containing `TurtleRace` and exits 0.
- The `paths.user_data_path('../evil')` invocation raises `ValueError` (Select-String picks up the traceback line).
- `pytest` reports `135 passed`.
- `pytest tests/test_paths.py -v` reports 11 tests passing.
- The `git diff` shows: `main.py` +4 lines / -0 lines; `paths.py` +~10 lines / -0 lines (guard block); `tests/test_paths.py` +~15 lines / -0 lines (banner + 2 tests).
- Manual race-run evidence is captured in `.shipyard/phases/2/results/SUMMARY-1.1.md` per Task 3's acceptance criteria.

Cross-references:
- ROADMAP.md Phase 2 success criteria (record call inserted between `run_race` and `show_podium`; JSON file accumulates correctly across runs; existing messagebox unchanged; pytest green).
- CONTEXT-2.md Decisions 1–4 (all four binding decisions are implemented across the three tasks).
- RESEARCH.md §1 (exact `main.py` insertion point), §2 (import placement), §3 (basename guard shape), §4 (test file conventions), §5 (manual verification protocol).
