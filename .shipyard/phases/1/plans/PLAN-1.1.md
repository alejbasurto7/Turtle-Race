# Plan 1.1: paths.user_data_path() + smoke tests

## Context

Add a `user_data_path(filename)` helper to `paths.py` so the upcoming `leaderboard.py` can write `leaderboard.json` into the user's per-user app-data directory — never inside the PyInstaller `sys._MEIPASS` bundle. This is the foundation for Phase 1: every leaderboard write goes through this function, so it must be correct on all three target platforms (Windows, macOS, Linux) and explicitly safe in both source-run and frozen-exe modes.

## Dependencies

None — first plan in Phase 1.

## Tasks

### Task 1: Add `user_data_path()` to `paths.py`
**Files:** `paths.py`
**Action:** modify
**TDD:** false
**Description:**

Add a new public function `user_data_path(filename: str) -> str` directly below the existing `resource_path()` in `paths.py`. Implement the three-platform branching pattern from RESEARCH §6:

- Windows (`sys.platform == "win32"`): root = `%APPDATA%\TurtleRace` (fallback to `os.path.expanduser("~\\AppData\\Roaming\\TurtleRace")` if `APPDATA` is unset).
- macOS (`sys.platform == "darwin"`): root = `~/Library/Application Support/TurtleRace`.
- Linux / other: root = `$XDG_DATA_HOME/TurtleRace` (fallback to `~/.local/share/TurtleRace`).

After resolving `root`, call `os.makedirs(root, exist_ok=True)` and return `os.path.join(root, filename)`.

**Hard constraints:**
- The function must NEVER reference `sys._MEIPASS`. Unlike `resource_path()`, this is writable user state, not a bundled resource. Add an inline comment to this effect.
- Use only the stdlib modules already imported by `paths.py` (`os`, `sys`). Do not add `pathlib` — `os.path` + `os.makedirs` is sufficient and keeps the diff minimal.
- Match the existing code style in `paths.py`: no type hints on `resource_path`, so adding them on `user_data_path` is optional. Per CONVENTIONS.md the rest of the codebase is annotation-free; add the `filename: str` and `-> str` annotations only because RESEARCH §6 explicitly specifies them and they document the contract.
- Do not modify `resource_path()`.

**Acceptance Criteria:**
- `paths.user_data_path("leaderboard.json")` returns a path under `%APPDATA%\TurtleRace\` on Windows.
- The parent directory exists after the call (verified by `os.path.isdir(os.path.dirname(result))`).
- The string `_MEIPASS` does not appear anywhere in `paths.py`'s `user_data_path` implementation.
- `python -c "from paths import user_data_path; print(user_data_path('x'))"` prints a path and exits 0.

### Task 2: Add `tests/test_paths.py` with per-platform branch coverage
**Files:** `tests/test_paths.py` (new)
**Action:** create
**TDD:** false
**Description:**

Create a new test file `tests/test_paths.py` following the existing test-file convention (RESEARCH §4, TESTING.md):

- First 4 lines: `sys.path` insert of the project root, matching the pattern in `tests/test_constants.py` and `tests/test_tracks.py` (no `conftest.py` exists; per-file path insert is the convention).
- Use plain `def test_*` functions with bare `assert` — no `unittest.TestCase`.
- Use pytest's built-in `monkeypatch` and `tmp_path` fixtures (no imports needed; just declare them as test-function parameters).

**Required tests (one function each):**

1. `test_user_data_path_windows_uses_appdata(monkeypatch, tmp_path)` — `monkeypatch.setattr(sys, "platform", "win32")`; `monkeypatch.setenv("APPDATA", str(tmp_path))`; assert `user_data_path("leaderboard.json")` starts with `str(tmp_path)` and ends with `TurtleRace\\leaderboard.json` (or `TurtleRace/leaderboard.json` — use `os.path.join` to build the expected suffix so it works on the host OS).
2. `test_user_data_path_windows_falls_back_when_appdata_unset(monkeypatch)` — `monkeypatch.setattr(sys, "platform", "win32")`; `monkeypatch.delenv("APPDATA", raising=False)`; assert the result contains `"TurtleRace"` and does not raise.
3. `test_user_data_path_macos(monkeypatch)` — `monkeypatch.setattr(sys, "platform", "darwin")`; assert the result contains `Library/Application Support/TurtleRace`.
4. `test_user_data_path_linux_uses_xdg(monkeypatch, tmp_path)` — `monkeypatch.setattr(sys, "platform", "linux")`; `monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))`; assert the result starts with `str(tmp_path)` and ends with `TurtleRace` + sep + filename.
5. `test_user_data_path_linux_falls_back_to_local_share(monkeypatch)` — `monkeypatch.setattr(sys, "platform", "linux")`; `monkeypatch.delenv("XDG_DATA_HOME", raising=False)`; assert `".local/share/TurtleRace"` (or platform-equivalent separator) appears in the result.
6. `test_user_data_path_never_under_meipass(monkeypatch)` — set `sys._MEIPASS` to a sentinel string `"/MEIPASS_SENTINEL"` via `monkeypatch.setattr(sys, "_MEIPASS", "/MEIPASS_SENTINEL", raising=False)`; call `user_data_path("x")`; assert `"MEIPASS_SENTINEL"` is NOT in the result on any platform branch (parametrize over `["win32", "darwin", "linux"]`).
7. `test_user_data_path_creates_parent_dir(monkeypatch, tmp_path)` — on the linux branch with `XDG_DATA_HOME=tmp_path/nested/dir`, call `user_data_path("x")`, assert `os.path.isdir(tmp_path / "nested" / "dir" / "TurtleRace")`.

**Acceptance Criteria:**
- `pytest tests/test_paths.py -v` passes all 7+ test functions.
- Each test uses `monkeypatch` to control `sys.platform` / env vars and `tmp_path` where filesystem writes are involved.
- No test writes anywhere other than `tmp_path`.

## Verification

Run from the project root:

```powershell
pytest tests/test_paths.py -v
pytest                              # full suite still green
python -c "import sys; sys.modules['tkinter'] = None; import paths; print(paths.user_data_path('leaderboard.json'))"
```

Expected:
- `pytest tests/test_paths.py -v` reports 7+ passed.
- Full `pytest` reports all existing 45 tests still pass plus the new ones (52+ total).
- The `python -c` invocation prints a path containing `TurtleRace` and does not raise. The `tkinter` poisoning confirms `paths` is Tk-free (it already is; this guards against accidental regressions).

Cross-references:
- ROADMAP.md Phase 1 success criterion: "`paths.user_data_path(filename)` returns `%APPDATA%/TurtleRace/<filename>` on Windows, falls back to `~/.turtle_race/<filename>` (or platform-appropriate equivalent) elsewhere, creates the parent directory if missing, and never returns a path inside `sys._MEIPASS`."
- CONTEXT-1.md does not constrain this task directly (it constrains the leaderboard module that consumes the helper).
- RESEARCH §6 provides the exact reference implementation.
