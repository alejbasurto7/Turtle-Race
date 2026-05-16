# Plan 2.1: leaderboard.py persistence layer + record_race + session state

## Context

Create the new top-level `leaderboard.py` module — Tk-free, stdlib-only — and establish its persistence foundation: JSON load/save with atomic write, module-level current-session state, corrupt-file quarantine recovery, and the public `record_race()` entry point. After this plan, race results can be recorded to disk and to an in-memory session list; querying and resetting are added in Plan 2.2.

## Dependencies

- Plan 1.1 (paths.user_data_path) — `_save()` and `_load()` call `paths.user_data_path("leaderboard.json")` to resolve the target path.

## Tasks

### Task 1: Create `leaderboard.py` with constants, load/save, and `record_race()`
**Files:** `leaderboard.py` (new)
**Action:** create
**TDD:** false
**Description:**

Create `leaderboard.py` at the project root. The module must be Tk-free: imports allowed are `json`, `os`, `sys`, `tempfile`, `datetime` (specifically `from datetime import datetime, date, timedelta` — `date` and `timedelta` are used by Plan 2.2 but importing them here keeps the import block stable), and `paths`. Do not import `tkinter`, `turtle`, `pygame`, `PIL`, `tracks`, `constants`, `race`, `dialogs`, or `audio`.

**Module-level constants (UPPER_SNAKE_CASE per CONVENTIONS.md):**

```python
POINTS = (6, 3, 1, 0)
SCHEMA_VERSION = 1
_FILENAME = "leaderboard.json"
```

**Module-level state:**

```python
_SESSION_RACES: list[dict] = []   # populated by record_race; resets on import
```

Type-annotate this single module-level variable to document the contract (the codebase otherwise has sparse annotations per CONVENTIONS.md; this one is load-bearing for readers).

**Private helpers to implement:**

1. `_path() -> str` — returns `paths.user_data_path(_FILENAME)`. Wrap in a function so tests can monkeypatch `paths.user_data_path` and have the change reflected on every call (don't compute the path at import time).

2. `_empty_store() -> dict` — returns `{"schema_version": SCHEMA_VERSION, "races": []}`. Used by `_load()` on missing/corrupt files and by Plan 2.2's `reset_all()`.

3. `_load() -> dict` — read and return the on-disk store. Behavior:
   - If `_path()` does not exist, return `_empty_store()` (do NOT write it; let `_save()` handle creation on first write).
   - If it exists, attempt `json.load`. On `json.JSONDecodeError` OR if the parsed object is not a dict OR is missing the `schema_version` or `races` keys OR `races` is not a list, treat as corrupt — see corrupt-file quarantine below.
   - On successful load, return the parsed dict as-is (no shape coercion; trust schema_version=1 for now).

4. `_quarantine_and_reset(reason: str) -> dict` — invoked by `_load()` when corruption is detected. Per CONTEXT-1.md Decision 3:
   - Build quarantine path: `f"{_path()}.corrupt-{datetime.now().strftime('%Y%m%dT%H%M%S')}"`.
   - `os.replace(_path(), quarantine_path)` (atomic rename of the broken file).
   - Write `_empty_store()` to `_path()` using the same atomic-write logic as `_save()` (extract a helper, e.g., `_atomic_write_json(data: dict, target: str) -> None`, that both `_save()` and `_quarantine_and_reset()` call).
   - Print to stderr exactly: `leaderboard: existing file unparseable, quarantined to <quarantine_path>; starting fresh` (use `print(..., file=sys.stderr)`).
   - Return `_empty_store()`.
   - Never raise to caller.

5. `_atomic_write_json(data: dict, target_path: str) -> None` — per RESEARCH §8:
   - `target_dir = os.path.dirname(target_path) or "."`
   - `fd, tmp_path = tempfile.mkstemp(prefix=".leaderboard.", suffix=".tmp", dir=target_dir)`
   - Write the JSON via `os.fdopen(fd, "w", encoding="utf-8")` with `json.dump(data, f, indent=2)`.
   - `os.replace(tmp_path, target_path)` — atomic on Windows + POSIX.
   - On any exception during write, attempt `os.unlink(tmp_path)` (suppress `OSError`) and re-raise.

6. `_save(data: dict) -> None` — calls `_atomic_write_json(data, _path())`. Existence of the parent directory is guaranteed by `paths.user_data_path` (`os.makedirs(root, exist_ok=True)` runs every call).

**Public function:**

`record_race(species: str, track: str, finish_order_names: list[str]) -> None`

- Build a record:
  ```python
  record = {
      "ts": datetime.now().isoformat(timespec="seconds"),
      "species": species,
      "track": track,
      "finish_order": list(finish_order_names),   # defensive copy
  }
  ```
- Append `record` to `_SESSION_RACES`.
- Call `store = _load()`; `store["races"].append(record)`; `_save(store)`.
- No return value, no exception swallowing on the I/O path (only the corrupt-file branch is swallowed, inside `_load`).

**Constraints reminder:**
- Timestamps: local time, ISO no suffix (CONTEXT-1 Decision 1).
- `record_race` does NOT take a `now=` kwarg (CONTEXT-1 Decision 4 limits the injection point to `query` / `query_per_track`, not `record_race`). The timestamp uses real local time at record time.
- Module must pass `python -c "import sys; sys.modules['tkinter'] = None; import leaderboard"` — verified in the test plan and in the Verification section below.

**Acceptance Criteria:**
- `leaderboard.py` exists at the project root.
- `python -c "import leaderboard; print(leaderboard.POINTS, leaderboard.SCHEMA_VERSION)"` prints `(6, 3, 1, 0) 1`.
- `python -c "import sys; sys.modules['tkinter'] = None; import leaderboard"` exits 0.
- `record_race("turtles", "straight", ["Leonardo","Raphael","Donatello","Michaelangelo"])` writes a JSON file at `paths.user_data_path("leaderboard.json")` containing schema_version 1 and exactly one race record with the expected shape.
- The grep `grep -n "tkinter\|turtle\|pygame\|PIL\|tracks\|constants" leaderboard.py` returns no matches.

### Task 2: Add `tests/test_leaderboard.py` covering persistence and `record_race`
**Files:** `tests/test_leaderboard.py` (new)
**Action:** create
**TDD:** false
**Description:**

Create the test file using the same conventions as the existing test files (project-root `sys.path` insert at top, no `conftest.py`, plain `def test_*` with `assert`). Subsequent tests for query/reset will be added by Plan 2.2 to the same file — coordinate by putting persistence tests at the top of the file under a comment banner `# --- Persistence + record_race ---`.

**Shared fixture pattern** (define once near the top of the file; reuse in every test):

```python
import pytest

@pytest.fixture
def lb(monkeypatch, tmp_path):
    """Fresh leaderboard module bound to tmp_path; session state cleared."""
    import leaderboard
    monkeypatch.setattr("paths.user_data_path",
                        lambda filename: str(tmp_path / filename))
    leaderboard._SESSION_RACES.clear()
    return leaderboard
```

Tests reuse this fixture so each test gets a clean tmp_path and an empty `_SESSION_RACES`. The fixture monkeypatches the `paths.user_data_path` symbol that `leaderboard._path()` looks up at call time (this is why Task 1 wraps the lookup in `_path()` rather than computing at import).

**Required tests:**

1. `test_record_race_creates_file_on_first_call(lb, tmp_path)` — fresh tmp_path, no file present; call `lb.record_race("turtles", "straight", ["A","B","C","D"])`; assert `(tmp_path / "leaderboard.json").exists()`; load JSON; assert `schema_version == 1`, `len(races) == 1`, `races[0]["species"] == "turtles"`, `races[0]["track"] == "straight"`, `races[0]["finish_order"] == ["A","B","C","D"]`, and `races[0]["ts"]` parses with `datetime.fromisoformat(...)`.
2. `test_record_race_appends_to_existing_file(lb)` — call `record_race` twice with different args; assert the on-disk file has exactly 2 races in insertion order.
3. `test_record_race_populates_session_list(lb)` — call `record_race` twice; assert `len(lb._SESSION_RACES) == 2` and the recorded values match.
4. `test_record_race_truncates_for_three_racer_snake_race(lb)` — call with 3-element finish_order; assert the on-disk record has a 3-element `finish_order` list (no zero-pad). Scoring truncation happens in `query()` (Plan 2.2); this test verifies the persistence layer faithfully records the original length.
5. `test_atomic_write_no_partial_file_on_crash(lb, tmp_path, monkeypatch)` — write a baseline race via `record_race`; then monkeypatch `os.replace` to raise `RuntimeError("boom")`; call `record_race` again and assert it raises; then assert the on-disk JSON still reflects only the baseline race (the failed second write must not have corrupted the file). After the test, restore `os.replace` (handled automatically by `monkeypatch` teardown).
6. `test_load_returns_empty_store_when_file_missing(lb)` — call `lb._load()` directly with no file on disk; assert `result == {"schema_version": 1, "races": []}`; assert no file was created as a side effect.
7. `test_corrupt_file_quarantined_and_replaced(lb, tmp_path, capsys)` — manually write `"{not valid json"` to `(tmp_path / "leaderboard.json")`; call `lb._load()`; assert it returns `{"schema_version": 1, "races": []}`; assert the canonical file now exists and contains an empty store; assert a file matching `leaderboard.json.corrupt-*` exists in `tmp_path`; assert `capsys.readouterr().err` contains `"leaderboard: existing file unparseable"` and `"quarantined to"`; assert no exception propagated.
8. `test_corrupt_file_wrong_shape_is_quarantined(lb, tmp_path, capsys)` — write `{"schema_version": 1}` (missing `races` key) to disk; call `lb._load()`; assert the same recovery behavior as test 7.
9. `test_module_is_tk_free()` — top-level subprocess invocation: `subprocess.check_call([sys.executable, "-c", "import sys; sys.modules['tkinter']=None; import leaderboard"])` from the project root. Asserts the import succeeds without Tk.

**Acceptance Criteria:**
- `pytest tests/test_leaderboard.py -v` reports 9 passed (covering persistence + record_race only; query/reset tests come in Plan 2.2).
- The fixture pattern is reusable by Plan 2.2 tests with no modification.
- Full `pytest` remains green (Plan 1.1 tests + existing 45 + these 9).

## Verification

```powershell
pytest tests/test_leaderboard.py -v
pytest                                            # full suite green
python -c "import sys; sys.modules['tkinter'] = None; import leaderboard"
python -c "import leaderboard; leaderboard.record_race('turtles','straight',['A','B','C','D']); print(open(__import__('paths').user_data_path('leaderboard.json')).read())"
```

Expected:
- `pytest tests/test_leaderboard.py -v` reports 9 passed.
- Full `pytest` reports green (Plan 1.1 tests + existing 45 + these 9 ≥ 61 total).
- The `tkinter` poisoning import succeeds.
- The final `python -c` writes and prints a JSON file with one race; subsequent calls to that one-liner accumulate races on disk. (Manual cleanup of the resulting file in real `%APPDATA%` is optional; this is the user's actual data dir.)

Cross-references:
- ROADMAP Phase 1 success criteria covered here: schema first-write shape; atomic write robustness; missing-file auto-creation behavior of `_load`; corrupt-file recovery with stderr warning.
- CONTEXT-1.md Decisions 1 (timestamp format) and 3 (corrupt-file quarantine) are both implemented in this plan.
- RESEARCH §8 (atomic write) is the reference pattern for `_atomic_write_json`.
