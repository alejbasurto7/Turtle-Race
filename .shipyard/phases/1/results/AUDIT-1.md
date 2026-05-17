# Security Audit — Phase 1

## Verdict: PASS_WITH_NOTES

## Threat Model Summary

Turtle Race is a local, single-user desktop game with no network socket, no authentication layer, no user-generated text input, and no PII. The only new attack surface introduced in Phase 1 is a writable file at `%APPDATA%\TurtleRace\leaderboard.json`, owned and readable exclusively by the current user. All findings are therefore at Low or Informational severity — there is no exploitable vulnerability introduced in this phase.

## Findings

### Critical
- None.

### High
- None.

### Medium
- None.

### Low / Informational

**[L1] Path traversal latent risk in `user_data_path(filename)`**
- Location: `paths.py:27`
- Description: The `filename` parameter is joined into the per-user data directory without sanitization (`os.path.join(root, filename)`). A caller passing `"..\\..\\evil"` or an absolute path such as `"C:\\Windows\\System32\\calc.exe"` would resolve outside the intended `TurtleRace\` directory. Note: `os.path.join` drops all preceding components when it encounters an absolute path, so `user_data_path("C:\\Windows\\foo")` returns `"C:\\Windows\\foo"` outright.
- Current exposure: Zero. The only caller in this phase is `leaderboard._path()`, which passes the hardcoded string `"leaderboard.json"`. No user input reaches this parameter.
- Future risk: If Phase 2 or later introduces a caller that accepts a UI-supplied filename (e.g., an export path), the unsanitized join becomes a local file write primitive.
- Remediation (for Phase 2+ callers, not urgent now): Validate that `os.path.basename(filename) == filename` and that `filename` does not contain `os.sep` or `..` before joining. Or document the function as strictly internal and enforce via a module-private underscore prefix.
- CWE-22 (Path Traversal).

**[L2] Symlink / clobber risk in `_quarantine_and_reset`**
- Location: `leaderboard.py:57-65`
- Description: `os.replace(_path(), quarantine_path)` renames the corrupt file to a timestamped path in the same directory. On systems where another OS user has write access to `%APPDATA%\TurtleRace\` (not the case for standard Windows per-user `%APPDATA%`, but possible if the directory was manually permissioned or on a shared drive), an adversary could pre-plant a symlink at the quarantine path to redirect the rename to an arbitrary target.
- Current exposure: Negligible. Standard Windows `%APPDATA%\Roaming\` ACLs allow only the profile owner and SYSTEM to write; no other local user can plant a symlink there.
- Remediation: Informational only. If this code is ever ported to a multi-user POSIX environment with a shared data directory, use `tempfile.mkstemp` in the quarantine directory and set mode `0o600` explicitly.
- CWE-61 (UNIX Symbolic Link Following).

**[L3] `mkstemp` temp file mode is 0o666 on Windows (no umask enforcement)**
- Location: `leaderboard.py:40`
- Description: `tempfile.mkstemp()` creates the temp file with OS-default permissions. On POSIX, the effective mode is `0o600` after applying `umask`. On Windows there is no umask; the file inherits the parent directory ACL. Testing confirms the mode is `0o100666` on this machine. This means during the brief window between `mkstemp` creation and `os.replace`, the temp file is world-readable (by other users on the same machine who can access the directory). In practice `%APPDATA%` is per-user, so no other standard user can read it — but the mode is still wider than necessary.
- Remediation: After `os.fdopen(fd, ...)` completes, `os.chmod(tmp_path, 0o600)` could narrow the window, but this is a no-op on Windows in most ACL configurations. On POSIX this is meaningful; on Windows it is cosmetic. Accept as-is given the per-user directory ACL provides the effective control.

**[L4] Concurrent-process race on quarantine + fresh-write**
- Location: `leaderboard.py:57-65`
- Description: If two game processes ran simultaneously (unusual but not impossible — e.g., two terminal windows), and both observed a corrupt file at the same instant, both could attempt `_quarantine_and_reset`. The second rename would fail (`FileNotFoundError` — file already moved by the first process) and be silently swallowed by the outer `except Exception: pass`. The second process would then attempt to write a fresh store over the file the first process just wrote atomically. Worst outcome: the user sees an empty history view for one session. Not a data-loss or security risk; `_atomic_write_json` prevents half-written files.
- Remediation: Note only. A file lock (e.g., `msvcrt.locking` on Windows, `fcntl.flock` on POSIX) would fully resolve this, but is unnecessary for a single-instance desktop game. If Phase 2+ adds a "launch multiple game windows" mode, revisit.

## Per-dimension verdicts

| # | Dimension | Verdict |
|---|---|---|
| 1 | Secrets scan (API keys, tokens, PEM blocks) | PASS — no findings in any changed file |
| 2 | Path traversal (`user_data_path` unsanitized join) | LOW — no exposed caller today; note for future (L1) |
| 3 | Symlink / quarantine clobber | LOW — informational; per-user APPDATA ACL is effective mitigation (L2) |
| 4 | Atomic write temp-file permissions | LOW — `mkstemp` is correct primitive; Windows mode 0o666 is cosmetic given directory ACL (L3) |
| 5 | JSON parsing safety (`json.load`) | PASS — stdlib JSON is not pickle; no RCE vector; file is in user's own APPDATA |
| 6 | Corrupt-file recovery race (concurrent processes) | NOTE — not a security issue; worst case is empty history view for one session (L4) |
| 7 | `os.makedirs` directory permissions | PASS — `%APPDATA%\Roaming\` inherits per-user ACL on Windows; `exist_ok=True` is correct |
| 8 | Dependency vulnerability check | PASS — `requirements.txt` unchanged; no new packages introduced; `pillow` and `pygame-ce` are unchanged |
| 9 | Configuration secrets | PASS — no `*.json`, `*.yml`, `*.yaml`, `*.toml`, `*.ini`, `*.env`, `*.cfg` files changed |
| 10 | IaC / Docker / PyInstaller spec / supply chain | PASS — `turtle_race.spec` unchanged; no IaC files in scope |

## Dependency / IaC / Config changes

- `requirements.txt` diff: none (file not in phase diff)
- `turtle_race.spec` diff: none (confirmed via `git diff 1f0afc8..HEAD -- turtle_race.spec`)
- Config files (`*.json`, `*.yml`, `*.yaml`, `*.toml`, `*.ini`, `*.env*`, `*.cfg`) diff: none

## Recommendations

1. **[Future Phase 2+, Small effort]** If any code path ever passes a variable (rather than a hardcoded string literal) into `user_data_path()`, add a `basename`-equality guard at the top of the function: `if os.path.basename(filename) != filename: raise ValueError(...)`. This costs two lines and eliminates L1 entirely for all future callers.

2. **[Existing issue, already in ISSUES.md]** The two `test_paths.py` tests that write real directories outside `tmp_path` (macOS and Linux fallback tests) should be fixed to use the `_fake_expanduser` helper that was already added for other tests in the same file. This is a test hygiene issue, not a security issue, and is already tracked in `.shipyard/ISSUES.md`.

3. **[Informational]** The `_quarantine_and_reset` stderr print (leaderboard.py:62-65) emits the full quarantine file path to stderr. In a packaged `.exe` with `console=False`, stderr is discarded. This is acceptable. If a future build enables a log file, ensure the quarantine path does not contain any user-identifying information beyond the timestamp — it does not currently.
