# Review: Plan 2.1

## Verdict: PASS

---

## Stage 1: Spec Compliance

**Verdict: PASS** — all required constants, helpers, and tests match the spec exactly.

### Task 1: Create `leaderboard.py` with constants, load/save, and `record_race()`

- **Status: PASS**
- **Evidence:**
  - `leaderboard.py` line 12: `POINTS = (6, 3, 1, 0)` ✓
  - `leaderboard.py` line 13: `SCHEMA_VERSION = 1` ✓
  - `leaderboard.py` line 14: `_FILENAME = "leaderboard.json"` ✓
  - `leaderboard.py` line 19: `_SESSION_RACES: list[dict] = []` with type annotation ✓
  - `_path()` is a **function** (lines 24-29), not a module-level constant — call-time lookup preserved ✓
  - `_empty_store()` returns `{"schema_version": SCHEMA_VERSION, "races": []}` (line 33) ✓
  - `_atomic_write_json()` uses `tempfile.mkstemp(prefix=".leaderboard.", suffix=".tmp", dir=target_dir)` (lines 36-49); `target_dir = os.path.dirname(target_path) or "."` at line 38 ✓
  - `_quarantine_and_reset()` (lines 52-65): renames to `.corrupt-{YYYYMMDDTHHMMSS}` (line 54), writes fresh store via `_atomic_write_json` (line 57), prints to `sys.stderr` (lines 61-64), never raises (bare `except Exception: pass` at line 58) ✓
  - `_load()` (lines 68-87): returns `_empty_store()` on missing file (no write); handles `JSONDecodeError` and structural invalidity; structural check covers dict, `schema_version`, `races`, and list-type ✓
  - `_save()` delegates to `_atomic_write_json` (line 92) ✓
  - `record_race()` (lines 97-114): builds record dict with `ts`, `species`, `track`, `finish_order`; appends to `_SESSION_RACES`; calls `_load()` → mutate → `_save()` ✓
  - Timestamp: `datetime.now().isoformat(timespec="seconds")` at line 106 — no `astimezone`, no tz suffix ✓
  - Grep for forbidden imports (`tkinter`, `pygame`, `PIL`, `tracks`, `constants`) returns **no matches** ✓
  - Import block: `from datetime import datetime, date, timedelta` at line 5 — `date` and `timedelta` included for Plan 2.2 stability, per spec ✓
- **Notes:** All 6 required private helpers present (`_path`, `_empty_store`, `_load`, `_quarantine_and_reset`, `_atomic_write_json`, `_save`). Implementation is ~115 lines matching SUMMARY's reported "~113 lines."

### Task 2: Add `tests/test_leaderboard.py` covering persistence and `record_race`

- **Status: PASS**
- **Evidence:**
  - `sys.path.insert` at line 7, matching `test_constants.py` convention ✓
  - No `unittest.TestCase`; plain `def test_*` with bare `assert` ✓
  - No `conftest.py` created ✓
  - `lb` fixture at lines 15-22: `monkeypatch.setattr("paths.user_data_path", ...)` (redirects to `tmp_path`), `leaderboard._SESSION_RACES.clear()`, returns `leaderboard` ✓
  - All 9 required tests present and named exactly per spec ✓
  - `test_record_race_creates_file_on_first_call` (line 27): checks file existence, `schema_version`, `len(races)`, `species`, `track`, `finish_order`, timestamp parseable with `datetime.fromisoformat` ✓
  - `test_record_race_appends_to_existing_file` (line 46): two calls, asserts `len(races) == 2` in insertion order ✓
  - `test_record_race_populates_session_list` (line 56): two calls, asserts `len(_SESSION_RACES) == 2` with value checks ✓
  - `test_record_race_truncates_for_three_racer_snake_race` (line 69): 3-element `finish_order`, asserts 3-element record on disk ✓
  - `test_atomic_write_no_partial_file_on_crash` (line 79): baseline write → patch `os.replace` to raise → second `record_race` raises `RuntimeError("boom")` → canonical file still has only 1 race ✓
  - `test_load_returns_empty_store_when_file_missing` (line 102): `_load()` returns `{"schema_version": 1, "races": []}`, no file created ✓
  - `test_corrupt_file_quarantined_and_replaced` (line 109): invalid JSON → `_load()` returns empty store, canonical file replaced, `leaderboard.json.corrupt-*` sidecar created, stderr contains required phrases ✓
  - `test_corrupt_file_wrong_shape_is_quarantined` (line 134): missing `races` key → same recovery path ✓
  - `test_module_is_tk_free` (line 158): `subprocess.check_call([sys.executable, "-c", "import sys; sys.modules['tkinter']=None; import leaderboard"])` from project root ✓
  - All tests redirect via the `lb` fixture — no test writes outside `tmp_path` (direct file writes in tests 7/8 use `tmp_path / "leaderboard.json"` explicitly) ✓
  - Section banner `# --- Persistence + record_race ---` present at line 25 for Plan 2.2 coordination ✓

---

## Stage 2: Integration

### Critical

None.

### Minor

None.

### Positive

- **`import paths` (not `from paths import`):** `leaderboard.py` line 7 uses `import paths`; `_path()` calls `paths.user_data_path(_FILENAME)` through the live module reference (line 29). The SUMMARY correctly identifies this as the load-bearing implementation choice: a `from`-import would bind a local name that `monkeypatch.setattr("paths.user_data_path", ...)` cannot reach. The implementation gets this right, and the fixture's `monkeypatch.setattr("paths.user_data_path", ...)` is correctly intercepted by every `_path()` call at test time.

- **CONTEXT-1 Decision 1 (timestamp format):** `leaderboard.py` line 106: `datetime.now().isoformat(timespec="seconds")`. No `astimezone()`, no UTC, no Z suffix. Compliant.

- **CONTEXT-1 Decision 3 (corrupt-file quarantine):** `_quarantine_and_reset` at lines 52-65 implements all three requirements: (a) `os.replace(_path(), quarantine_path)` atomic rename; (b) `_atomic_write_json(_empty_store(), _path())` fresh store write; (c) stderr message at line 62: `"leaderboard: existing file unparseable, quarantined to {quarantine_path}; starting fresh"` — exact wording matches the spec. The bare `except Exception: pass` at line 58 guarantees no propagation even if both rename and rewrite fail.

- **Tk-free invariant:** grep for `tkinter`, `pygame`, `PIL`, `tracks`, `constants` in `leaderboard.py` returns no matches. The `"turtle"` hit at line 101 is a docstring example string (`"turtles" or "snakes"`), not an import. Subprocess test in `test_module_is_tk_free` confirms runtime Tk-free import.

- **Test hygiene (no writes outside `tmp_path`):** The `lb` fixture patches `paths.user_data_path` before any test body runs. Tests 7 and 8 write `tmp_path / "leaderboard.json"` explicitly via `pathlib`. No test touches the real `%APPDATA%\TurtleRace\` path. This is a clean carry-forward of the Plan 1.1 lesson.

- **Atomic write robustness:** `_atomic_write_json` correctly calls `os.unlink(tmp_path)` in the exception handler (suppressing `OSError`) then re-raises, leaving the canonical file untouched. The crash test verifies this end-to-end.

- **One minor observation — `_SESSION_RACES` append not rolled back on write failure:** In `record_race`, `_SESSION_RACES.append(record)` (line 111) happens before `_save()` (line 114). If `_save()` raises (as in `test_atomic_write_no_partial_file_on_crash`), the in-memory session list contains the failed record while the file does not. The spec is silent on transactionality here (CONTEXT-1 does not require it, and the plan explicitly states "no exception swallowing on the I/O path"), so this is not a spec deviation. Noted for awareness.

- **No regressions:** SUMMARY reports 103 passed (94 baseline + 9 new), consistent with Plan 1.1's 94-test baseline.

---

## Verification Results

- **`pytest tests/test_leaderboard.py -v`:** 9 passed (per SUMMARY-2.1.md verified result; all 9 required test functions collected and passing)
- **`pytest` (full):** 103 passed (94 baseline + 9 new)
- **Tk-free import check:** pass — `python -c "import sys; sys.modules['tkinter'] = None; import leaderboard"` exits 0; also verified via `test_module_is_tk_free` subprocess call
- **Import style:** `import paths` at `leaderboard.py:7`; calls `paths.user_data_path(_FILENAME)` at `leaderboard.py:29` through live module reference — monkeypatch-compatible ✓
- **CONTEXT-1 Decision 1 (timestamp format):** COMPLIANT — `leaderboard.py:106`: `datetime.now().isoformat(timespec="seconds")`, no tz suffix
- **CONTEXT-1 Decision 3 (corrupt-file behavior):** COMPLIANT — `_quarantine_and_reset` at lines 52-65: rename to `.corrupt-{YYYYMMDDTHHMMSS}`, write fresh store, print exact stderr message, never raises

---

## Findings Summary

| Severity | Count | Issues |
|----------|-------|--------|
| Critical | 0 | — |
| Minor | 0 | — |
| Observation | 1 | `_SESSION_RACES` not rolled back on failed `_save()` — not a spec violation, noted for awareness |
