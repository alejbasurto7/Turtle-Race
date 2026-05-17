# Security Audit — Phase 4

## Verdict: PASS

## Scope
- Commits audited: `663faac`, `24b9345`, `79b082e`, `62e821d` (base `4505aad`).
- Files changed:
  - `dialogs.py` — extended with the real leaderboard window (+~200 lines).
  - `main.py` — single call-site rename only.
  - `tools/smoke_phase_4.py` — NEW: no-GUI verification smoke (~331 lines).

## Threat model context
The project is a local desktop Tk game with no network surface, no database, no authentication, no multi-user state, and no external inputs beyond a few file-paths-by-name and the leaderboard JSON file `%APPDATA%/TurtleRace/leaderboard.json`. The realistic attacker surface for Phase 4 changes is: (a) a malicious or corrupted JSON file under `%APPDATA%`, and (b) anything that could escalate the smoke harness's tempdir into a system-wide write. Both are local-attacker scenarios with very low impact (worst case: leaderboard view raises an exception or shows garbled data).

## Findings

### Critical
- None.

### High
- None.

### Medium
- None.

### Low / Informational
- **`_FILTER_LABEL_TO_KEY` does not normalize/validate user-controllable Track combobox values.** The Track combobox values are populated from `leaderboard.known_tracks()` (which itself reads track names from the leaderboard JSON on disk). If an attacker were to write a malicious string (e.g., extremely long, or containing path-separator characters) directly into `leaderboard.json` and the user then opened the leaderboard, the string would flow into `dialog._track_combo["values"]` and back into `leaderboard.query(..., track_filter=<string>)`. The `query` function then uses it as an equality-match filter (read-only) and does NOT use it as a path component, so there is no injection or traversal vector — just a "ugly text in a combobox" outcome. Acceptable; not worth defensive validation in `dialogs.py`.
- **Tempdir handling in `tools/smoke_phase_4.py`.** `tempfile.mkdtemp(prefix="turtlerace_phase4_smoke_")` is the safe form (creates a directory atomically with default secure permissions: 0o700 on POSIX, restricted ACL on Windows). The smoke intentionally leaves the tempdir behind for inspection — same pattern as `smoke_phase_3.py`. Contents are a single race-history JSON file with no secrets, so the persistence is fine.
- **`os.environ["APPDATA"]` mutation in the smoke is process-scoped.** It does not leak to other processes and is restored implicitly when the smoke process exits. No side-effect on the user's real `%APPDATA%`.
- **`messagebox.askyesno` with `default=tkinter.messagebox.NO`.** While this is a UX-safety boundary (not a security boundary), it provides defense-in-depth against accidental destructive `reset_all()`. Positive.

## Positive observations
- **No new third-party dependencies** introduced this phase (`requirements.txt` unchanged). The new imports are all stdlib: `tkinter`, `ttk`, `tkinter.messagebox`, `tempfile`, `os`, `sys`, `json`.
- **No use of `eval`, `exec`, `pickle.loads`, `yaml.load`, `subprocess.shell=True`, or other classically dangerous deserializers or shell escapes.** Verified by grep on the diff.
- **No hardcoded secrets, API keys, tokens, JWTs, or credential strings** in any changed file. (Verified by reading the full diff.)
- **No path traversal vector.** No user-controllable string is joined into a filesystem path. All file paths flow through `paths.resource_path()` (PyInstaller-aware, unchanged this phase) or the leaderboard module's `%APPDATA%`-based path resolution (also unchanged this phase).
- **Both destructive operations** (`leaderboard.reset_session()`, `leaderboard.reset_all()`) are gated by `messagebox.askyesno(..., default=NO)` with exact CONTEXT-4 confirmation copy. The "No" default biases the user away from accidental destructive actions.
- **No infrastructure-as-code files** were touched (no Terraform/Ansible/Docker/Kubernetes/CloudFormation). IaC validation skipped per config `iac_validation: auto`.
- **Smoke harness scope is well-contained:** monkeypatches only `dialogs.*`, `audio.*`, and `tkinter.messagebox.askyesno`. Production code paths are unmodified — the smoke cannot silently disable a runtime safety check.

## Recommendations
- None blocking. No follow-ups required.
- (Optional, very low priority) If the project ever exposes the leaderboard JSON file to network-fetched content in a future phase, revisit the Track-combobox-value flow. Not relevant today.
