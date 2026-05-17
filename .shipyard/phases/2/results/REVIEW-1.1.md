# Review: Phase 2 Plan 1.1

## Verdict: MINOR_ISSUES (approved — deferred suggestions on tooling artifact)

(Authored by the shipyard:reviewer agent; the agent did not persist this file directly. Captured verbatim by the orchestrator from the agent's structured output.)

## Findings

### Critical
- None.

### Important
- **`tools/smoke_phase_2.py` advances `round_idx` at close-of-round.** `round_idx[0]` is incremented inside `fake_ask_play_again`, but `fake_get_user_track`/`get_user_species`/`get_user_bet` all read `rounds[round_idx[0]]` at round entry. This works today because `main()`'s round loop happens to call `ask_play_again` last — but if a future phase (3 onward) reorders those calls, the smoke could silently read the wrong canned plan entry and report a misleading PASS. Test-infrastructure issue only; no production-code impact. Non-blocking; smoke script is a Phase 2 artifact and Phase 3 will replace its own verification path. **Deferred** — not worth a re-commit for a single-use tool.

### Minor / Suggestions
- **Smoke script doesn't assert non-decreasing timestamps.** ROADMAP Phase 2 success criterion mentions chronological order; the smoke checks species/track/finish_order length but not `ts`. A 3-line addition would close the gap. **Deferred** — the ts ordering is structurally guaranteed by `record_race`'s use of `datetime.now()` per record and the smoke captured ascending timestamps in the actual run output (22:30:22 / 22:31:25 / 22:31:54).
- **`test_user_data_path_rejects_path_separator` Windows/POSIX divergence is uncommented.** On Windows, `os.sep="\\"` and `os.altsep="/"` produce two distinct test inputs covering both branches. On POSIX, they collapse to identical strings (`os.sep=="/"`, `os.altsep is None`). Test still passes on POSIX but only exercises one branch. A one-line comment would aid maintainability. **Deferred** — repo convention is sparse comments; this isn't load-bearing.
- **Phase 1 carryover findings fully resolved.** `tests/test_paths.py` applies `_fake_expanduser(tmp_path)` consistently in all four Phase 1 fixed tests. No recurring pattern.

### Positive
- `main.py` insertion is surgical — exactly 1 import + 3 round-body lines + 0 modifications to existing lines. `record_race` placed correctly before `show_podium` per CONTEXT-2 Decision 1.
- Basename guard structurally sound: rejects (not sanitizes), all 4 conditions covered (`basename != filename`, `"."`/`".."`, `os.sep`, `os.altsep`), `ValueError` with `repr(filename)` in the message, fires before `os.makedirs`. `"leaderboard.json"` survives the guard so Phase 1's 39 leaderboard tests stay green.
- TDD discipline followed for Task 2 (tests red → guard → tests green).
- Smoke substitute exercises the real `main()` loop through the real `race.run_race`, real `record_race`, real `paths.user_data_path` against a redirected tempdir. End-to-end coverage equivalent to the manual protocol's intent; only the human-eyeballing-podium independence is absent (acknowledged in SUMMARY).
- All CONTEXT-2 decisions (1–4) verifiably implemented.

## Verification Results
- `pytest tests/test_paths.py -q`: **11 passed** (9 existing + 2 new guard tests).
- `pytest -q` (full): **135 passed** (133 baseline + 2 new). Phase 1's 39 leaderboard tests still green.
- `python -c "import main"`: exits 0.
- `python -c "import paths; paths.user_data_path('../evil')"`: raises `ValueError` with `'../evil'` in the message.
- `python -c "import paths; print(paths.user_data_path('leaderboard.json'))"`: prints a `TurtleRace/leaderboard.json` path, exits 0.
- Task 3 substitute faithfulness: PASS — 3 races (1 snake + 2 turtle) recorded with correct schema, species, track, finish_order length; cross-checked against on-screen podium output in SUMMARY-1.1.md.

## Resolution

All findings are non-blocking. The one Important finding is a smoke-script-only concern that will not survive Phase 3's wiring restructure regardless. Tasks 1–3 are accepted as-is. Plan complete.
