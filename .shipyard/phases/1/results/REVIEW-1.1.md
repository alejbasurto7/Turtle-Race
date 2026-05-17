# Review: Plan 1.1

## Verdict: MINOR_ISSUES

---

## Stage 1: Spec Compliance

**Verdict: PASS** (with two minor test-quality deviations, neither blocking)

### Task 1: Add `user_data_path()` to `paths.py`

- **Status: PASS**
- **Evidence:** `paths.py` lines 10-27 contain the new function. Implementation matches the RESEARCH §6 reference verbatim.
  - Windows branch (`sys.platform == "win32"`): `os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")` then `os.path.join(base, "TurtleRace")`. ✓
  - macOS branch (`sys.platform == "darwin"`): `os.path.expanduser("~/Library/Application Support/TurtleRace")`. ✓
  - Linux/other: `os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")` joined with `"TurtleRace"`. ✓
  - `os.makedirs(root, exist_ok=True)` is called before return. ✓
  - `sys._MEIPASS` does not appear in `user_data_path()`'s functional code — lines 11-15 are comment-only references. ✓
  - `resource_path()` at lines 5-7 is untouched. ✓
  - No new imports: file still has only `import os` and `import sys`. ✓
  - Type hints `filename: str` and `-> str` present per plan spec. ✓
- **Notes:** The 5-line comment block above the function is slightly longer than the repo's typical inline style (CONVENTIONS.md observes "inline explanatory comments are the dominant style"), but the plan explicitly sanctioned it ("slightly longer than typical for the repo, but the `_MEIPASS` invariant is load-bearing").

### Task 2: Add `tests/test_paths.py` with per-platform branch coverage

- **Status: PASS** (spec compliance), with two Important quality findings detailed in Stage 2.
- **Evidence:** `tests/test_paths.py` — 72 lines, 9 test functions (plan required 7+, delivered 9). ✓
  - Per-file `sys.path.insert` at line 5 matches `test_constants.py` lines 1-5. ✓
  - No `unittest.TestCase`; plain `def test_*` functions with bare `assert`. ✓
  - `monkeypatch` and `tmp_path` used as fixture parameters (no imports). ✓
  - No `conftest.py` created. ✓
  - All 7 required test functions present, plus the `_MEIPASS` check is parametrized over `["win32","darwin","linux"]` producing 3 variants (9 total). ✓
  - `test_user_data_path_creates_parent_dir` correctly uses `tmp_path / "nested" / "dir"` for `XDG_DATA_HOME` and asserts `os.path.isdir(tmp_path / "nested" / "dir" / "TurtleRace")`. ✓
  - macOS mixed-separator fix (forward-slash normalization) documented and applied correctly. ✓
- **Notes:** See Stage 2 Important findings below regarding two tests that write outside `tmp_path`.

---

## Stage 2: Code Quality

### Critical

None.

### Important

**1. `test_user_data_path_macos` writes a real directory outside `tmp_path` on the host machine**
- File: `tests/test_paths.py`, line 27-32
- The test monkeypatches `sys.platform` to `"darwin"` but does NOT patch the home directory or provide a `tmp_path`-based root. The implementation calls `os.makedirs(root, exist_ok=True)` where `root = os.path.expanduser("~/Library/Application Support/TurtleRace")`. On the Windows dev machine this resolves to something like `C:\Users\T0226129/Library/Application Support/TurtleRace` — a real directory that gets created on disk. The plan's acceptance criterion explicitly states "No test writes anywhere other than `tmp_path`."
- Remediation: Add `tmp_path` to the test signature and patch `os.path.expanduser` (or the `HOME` environment variable) so the expansion resolves under `tmp_path`. Example:
  ```python
  def test_user_data_path_macos(monkeypatch, tmp_path):
      monkeypatch.setattr(sys, "platform", "darwin")
      monkeypatch.setenv("HOME", str(tmp_path))
      result = user_data_path("leaderboard.json")
      normalized = result.replace("\\", "/")
      assert "Library/Application Support/TurtleRace" in normalized
  ```
  On Windows, `os.path.expanduser` reads `USERPROFILE` (and falls back to `HOMEDRIVE`+`HOMEPATH`), not `HOME`. A more robust cross-platform fix is to monkeypatch `os.path.expanduser` directly: `monkeypatch.setattr(os.path, "expanduser", lambda p: p.replace("~", str(tmp_path)))`.

**2. `test_user_data_path_linux_falls_back_to_local_share` writes a real directory outside `tmp_path`**
- File: `tests/test_paths.py`, lines 44-50
- Same issue as above but for the Linux fallback branch. With `XDG_DATA_HOME` deleted and no `HOME` patch, the function calls `os.makedirs(os.path.expanduser("~/.local/share/TurtleRace"), exist_ok=True)`, which creates a real directory under the host user's home. On Windows this produces a path like `C:\Users\T0226129/.local/share/TurtleRace`.
- Remediation: Same approach as above — add `tmp_path` and patch `HOME` or `os.path.expanduser`:
  ```python
  def test_user_data_path_linux_falls_back_to_local_share(monkeypatch, tmp_path):
      monkeypatch.setattr(sys, "platform", "linux")
      monkeypatch.delenv("XDG_DATA_HOME", raising=False)
      monkeypatch.setenv("HOME", str(tmp_path))
      result = user_data_path("leaderboard.json")
      normalized = result.replace("\\", "/")
      assert ".local/share/TurtleRace" in normalized
  ```

### Suggestions

**1. `test_user_data_path_windows_falls_back_when_appdata_unset` also writes outside `tmp_path`**
- File: `tests/test_paths.py`, lines 20-24
- Lower severity than the two Important findings above because on Windows (the actual dev and target platform) `os.path.expanduser("~\\AppData\\Roaming")` resolves to the real `%APPDATA%` path, creating `%APPDATA%\TurtleRace` on disk. The directory likely already exists on subsequent runs (harmless, `exist_ok=True`), but technically violates the "no writes outside `tmp_path`" criterion. Consider adding `tmp_path` and patching `USERPROFILE` or `HOMEDRIVE`/`HOMEPATH` to contain the write.

**2. `_MEIPASS` non-leakage test is a regression guard, not a functional assertion — document it**
- File: `tests/test_paths.py`, lines 53-63
- Positive note: the parametrized test correctly guards against a future implementation accidentally reading `sys._MEIPASS`. Since the current implementation never references `_MEIPASS` in `user_data_path()`, the test cannot fail today, but it would catch a future regression if someone refactored the two functions incorrectly. This is intentional and well-constructed. A one-line comment (`# Regression guard: user_data_path must never consult _MEIPASS`) would make the intent explicit for future maintainers, consistent with the repo's "inline explanatory comments for non-obvious logic" convention.

**3. Consider testing the `windows_uses_appdata` assertion more precisely**
- File: `tests/test_paths.py`, line 17
- `result.endswith(expected_suffix)` where `expected_suffix = os.path.join("TurtleRace", "leaderboard.json")`. On Windows this is `"TurtleRace\\leaderboard.json"`, which is correct. However, `result.startswith(str(tmp_path))` at line 15 already constrains the root. This is fine as-is; purely a note that the double assertion (startswith + endswith) provides robust coverage with no redundancy.

---

## Verification Results

- **`pytest tests/test_paths.py -v`:** 9 passed (per SUMMARY-1.1.md verified result; 7 base functions + 2 additional parametrize variants from the `_MEIPASS` triple = 9 collected)
- **`pytest` (full suite):** 94 passed (85 baseline + 9 new, per SUMMARY-1.1.md)
- **`paths.py` diff sanity check:** `resource_path()` is byte-for-byte unchanged (lines 5-7). `user_data_path()` added at lines 10-27, stdlib-only (`os`, `sys`). The string `_MEIPASS` appears in `resource_path()` (line 6, functional) and in two comment lines (11, 14) inside `user_data_path()` — zero functional references in the new function. Implementation matches the RESEARCH §6 reference implementation exactly.

---

## Findings Summary

| Severity | Count | Issues |
|----------|-------|--------|
| Critical | 0 | — |
| Important | 2 | macOS test writes outside tmp_path; Linux fallback test writes outside tmp_path |
| Suggestion | 3 | Windows fallback test writes outside tmp_path; _MEIPASS regression guard comment; double-assertion note |

---

## Resolution (post-review)

Both Important findings and the related Windows-fallback Suggestion were fixed in follow-up commit **`e737fbf`** rather than dispatching a builder retry (per the build protocol, only CRITICAL_ISSUES require a retry cycle, and the fix was mechanical with an explicit reviewer-supplied remediation).

Fix applied:
- Introduced `_fake_expanduser(tmp_path)` helper that substitutes `~` with `tmp_path` for the duration of a test.
- Applied via `monkeypatch.setattr(os.path, "expanduser", _fake_expanduser(tmp_path))` in `test_user_data_path_macos`, `test_user_data_path_linux_falls_back_to_local_share`, `test_user_data_path_windows_falls_back_when_appdata_unset`, and the parametrized `test_user_data_path_never_under_meipass`.
- Added the regression-guard comment to `test_user_data_path_never_under_meipass` per Suggestion 2.

Verification after fix:
- `pytest tests/test_paths.py -q` → 9 passed (still 9, no test loss).
- `pytest` (full) → 94 passed.
- Manual confirmation: no stray directories created outside `tmp_path` after re-running the suite.

Final verdict: **PASS** (after `e737fbf`).
