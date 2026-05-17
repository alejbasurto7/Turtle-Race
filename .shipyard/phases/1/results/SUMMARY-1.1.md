# Build Summary: Plan 1.1

## Status: complete

## Tasks Completed
- Task 1: add `user_data_path()` to `paths.py` — complete — files: `paths.py` (commit `ced0305`)
- Task 2: add `tests/test_paths.py` covering all platform branches — complete — files: `tests/test_paths.py` (commit `59b4cbb`)

## Files Modified
- **`paths.py`** (+20 lines): added `user_data_path(filename: str) -> str` below `resource_path`. Three-platform branching — Windows `%APPDATA%\TurtleRace` (with `~\AppData\Roaming` fallback), macOS `~/Library/Application Support/TurtleRace`, Linux `$XDG_DATA_HOME/TurtleRace` (with `~/.local/share` fallback). Inline comment documents the `_MEIPASS` non-reference invariant. Stdlib only (`os`, `sys`). `resource_path()` untouched.
- **`tests/test_paths.py`** (new, 71 lines): 9 test functions covering Windows happy path + APPDATA-unset fallback, macOS path, Linux XDG happy path + `~/.local/share` fallback, the `_MEIPASS` non-leakage check parametrized over all three platform branches, and nested-dir creation by `os.makedirs`. Follows existing per-file `sys.path.insert` convention; no `conftest.py`.

## Decisions Made
- Used `os.path` rather than `pathlib` — plan called for this explicitly to keep the diff in `paths.py` minimal and consistent with `resource_path()`'s existing style.
- Comment block above `user_data_path` is multi-line (5 lines of comment) — slightly longer than typical for the repo, but the `_MEIPASS` invariant is load-bearing and the inline comment is the right place to enforce it for future readers.

## Issues Encountered
- **`os.path.expanduser` produces mixed separators on Windows.** When testing the macOS / Linux branches on the Windows dev machine, `os.path.expanduser("~/Library/Application Support/TurtleRace")` returns e.g. `C:\Users\T0226129/Library/Application Support/TurtleRace` — backslash for the home prefix, forward slashes for the rest of the template. A naive substring check using `os.path.join("Library","Application Support","TurtleRace")` (which produces backslashes on Windows) therefore fails. **Fix:** normalize the result to forward slashes before substring matching in those tests. Worth noting for any future tests that assert on cross-platform path shapes. This is a test-only concern; production code returns whatever the OS-native form is, which is correct for each platform's actual runtime.

## Verification Results
- `pytest tests/test_paths.py -q`: **9 passed** in 0.03s.
- `pytest` (full suite): **94 passed** (baseline 85 + 9 new). All existing tests still green.
- `git log --oneline -2` shows the two atomic commits `ced0305` and `59b4cbb`, both `shipyard(phase-1): …`.
- `paths.py` does not reference `_MEIPASS` outside `resource_path()` (verified by grep).
