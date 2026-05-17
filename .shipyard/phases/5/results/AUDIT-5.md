# Security Audit — Phase 5

## Verdict: PASS

## Scope
- Commits audited: `2a8dffa`, `20a9eb7`, `298fce8` (base `762630a`).
- Files changed:
  - `CLAUDE.md` — docs only, +11/-1.
  - `turtle_race.spec` — comment lines only, +3/-0 (no functional content changed).
  - `tools/smoke_phase_5.py` — NEW, ~191 lines (automated source-mode smoke).
  - `tools/smoke_packaged.md` — NEW, ~140 lines (human checklist).

## Threat model context
Phase 5 is the polish-and-ship phase for a local desktop Tk game. No new attack surface introduced: no network, no DB, no auth, no parsing of untrusted input. The most relevant security-adjacent concerns for this diff are (a) tempdir handling in the smoke, (b) any sensitive content in the new docs/checklist, and (c) confirming the PyInstaller `datas=` list change (or non-change) doesn't accidentally bundle anything sensitive.

## Findings

### Critical
- None.

### High
- None.

### Medium
- None.

### Low / Informational
- **`tools/smoke_phase_5.py` tempdir behavior.** Uses `tempfile.mkdtemp(prefix="turtlerace_phase5_smoke_")` — the secure-default form (POSIX 0o700 / Windows restricted ACL). Tempdir is intentionally NOT cleaned up after success, mirroring `smoke_phase_3.py` / `smoke_phase_4.py`. Contents are a single race-history JSON file with no secrets. Same pattern as prior phases; previously audited as fine.
- **`os.environ["APPDATA"]` mutation in the smoke is process-scoped.** No leak to other processes; restored implicitly on smoke process exit. Same pattern as prior phases.
- **`turtle_race.spec` change is purely additive comment.** No `datas=`, `Analysis()`, `EXE()`, `hiddenimports=`, or any other functional content modified. `git diff 762630a 20a9eb7 -- turtle_race.spec` shows only the 3-line prepend. No accidental bundling of new files into the frozen exe.
- **CLAUDE.md addendum contains no secrets, credentials, internal URLs, or PII.** It describes file paths, module names, and invariants — all of which are already public knowledge for anyone with read access to the repo.
- **`tools/smoke_packaged.md` checklist contains no secrets.** Documents a build command (`pyinstaller turtle_race.spec`), a run command (`dist\TurtleRace.exe`), and the expected `%APPDATA%\TurtleRace\leaderboard.json` file path. No credentials.

## Positive observations
- **No new third-party dependencies** introduced. `requirements.txt` unchanged.
- **No imports of `eval`, `exec`, `pickle.loads`, `yaml.load`, `subprocess.shell=True`, or any other classically dangerous deserializer or shell-escape vector** in the new `tools/smoke_phase_5.py`. Only stdlib: `json`, `os`, `sys`, `tempfile`, plus the project's own `paths` and `leaderboard`.
- **`tools/smoke_phase_5.py` is Tk-free by design and verified by grep** (`grep -cE "import tkinter|import dialogs|import main|import audio" tools/smoke_phase_5.py` → 0). This means even if the smoke were to be run in a privilege-escalated context (it should not be), it cannot create a Tk window and cannot drive GUI events.
- **No infrastructure-as-code files were touched.** `turtle_race.spec` is PyInstaller config (build-time only, not deployment infra); only comments added.
- **The CLAUDE.md addendum explicitly documents a load-bearing security-adjacent invariant** ("Do not add `import tkinter` to `leaderboard.py`") — this is a constructive contribution to future-maintenance security because it tells reviewers what to reject.
- **Cross-task coherence:** the manual checklist `smoke_packaged.md` and the automated smoke `smoke_phase_5.py` cover overlapping invariants (path resolution under `%APPDATA%`, schema_version=1, reset_all canonical shape). Overlapping verification is defense-in-depth, not bloat.

## Recommendations
- None blocking.
- (Optional, future) If the project ever exposes the leaderboard JSON file to network-fetched content, revisit `leaderboard.py`'s deserialization path (today it's `json.load` with corrupt-file quarantine, which is safe). Not relevant for Phase 5.
- (Optional, future) If `tools/_smoke_common.py` is ever extracted (deferred per CONTEXT-5 Decision 6), audit the shared module separately at that time.
