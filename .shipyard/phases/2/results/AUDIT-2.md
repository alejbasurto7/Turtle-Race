# Security Audit — Phase 2

(Captured verbatim by the orchestrator from the auditor agent's structured output; the agent did not persist this file directly.)

## Verdict: PASS — Risk Level LOW

## Threat Model Summary

Local single-user desktop game, no network surface, no auth boundary, no PII, no public input. Phase 2 makes `leaderboard.record_race` reachable from the production round loop for the first time and closes Phase 1's L1 path-traversal finding with a 4-condition basename guard on `paths.user_data_path`. All values flowing into persistence originate from hardcoded dispatch tables (`SPECIES` dict, `TRACK_NAMES`).

## Findings

### Critical / Important
- None.

### Advisory
- **Unguarded disk-write error propagates to round loop** (`main.py:42`). By deliberate CONTEXT-2 Decision 1, `leaderboard.record_race(...)` is not wrapped in `try/except`. If the call raises (disk full, ACL denial, hypothetical future `ValueError` from the basename guard), the exception propagates through `main()` and crashes the round. This is a design-acknowledged robustness concern, not a security issue. The chosen policy ("persistence failure should be visible to the user") is sound; flagged for the record so any future shift to a "best-effort persist" stance is a deliberate change rather than an oversight.

## Closed Phase 1 Findings

- **L1 (CWE-22 path traversal) — CLOSED.** Guard at `paths.py:15-23` implements all four conditions:
  1. `os.path.basename(filename) != filename` — catches embedded separators on the active platform.
  2. `filename in (".", "..")` — explicit dot-directory rejection.
  3. `os.sep in filename` — Windows `\\` / POSIX `/`.
  4. `os.altsep is not None and os.altsep in filename` — covers `"subdir/x.txt"` on Windows (`altsep == "/"`).
- Verified on this Windows host: all attack inputs (`"../evil"`, `"..\\evil"`, `"subdir/x.txt"`, `"."`, `".."`) raise `ValueError`; `"leaderboard.json"` passes. Guard fires before `os.makedirs`, so rejected calls produce no filesystem side-effects.
- **L2 (symlink/clobber in `_quarantine_and_reset`), L3 (mkstemp 0o666 on Windows), L4 (concurrent-process race):** unchanged from Phase 1. No new exposure introduced.

## Smoke Utility (`tools/smoke_phase_2.py`) review

No material security concerns:
- Zero input surface — all dialog responses are hardcoded canned plans.
- Filesystem isolation via `tempfile.mkdtemp(...)` + `os.environ["APPDATA"]` redirect before any import resolves `user_data_path`. Cannot pollute the real per-user APPDATA.
- One hygiene note: the tempdir is not removed by `finally` block, so it accumulates on repeated runs. Not a security issue — it's under `%TEMP%` with per-user ACL — but worth noting as a developer-tool cleanup pattern.
- The reviewer's Important finding (round_idx advancement coupled to `ask_play_again`) is a test-infrastructure concern, not a security issue.
- Production impact: none — file lives under `tools/` and is not imported by any production path.

## Cross-Component Analysis

Data flow from `main.py` → `leaderboard.record_race` (`main.py:41-42`):
- `species` — return value of `dialogs.get_user_species()`, constrained to keys of `constants.SPECIES`. No free-form text.
- `track_name` — return value of `dialogs.get_user_track()`, constrained to `{"straight", "rectangular", "spiral"}`. No free-form text.
- `finish_order_names` — list comprehension over `racers[i]['name']`; `racers` originate from `constants.SPECIES[species]["names"]` (hardcoded). No free-form text.

No injection surface. JSON values are all controlled enumerations defined at code-authoring time.

## Dependency / IaC / Config Changes

| Item | Status |
|---|---|
| `requirements.txt` | unchanged |
| `turtle_race.spec` | unchanged (verified by `git diff 5f2a590..HEAD -- turtle_race.spec` returning empty) |
| Config files | none in diff |
| IaC / Docker | N/A — not present in project |

## Recommendation

Proceed to ship of Phase 2. No security action required; the L1 finding is now closed and no new findings were introduced.
