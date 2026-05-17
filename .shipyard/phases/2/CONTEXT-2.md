# CONTEXT — Phase 2: Wire `record_race` into the round loop

User decisions captured during `/shipyard:plan 2` Discussion Capture (2026-05-16). Binding for all downstream agents.

## Decisions

### 1. Call-site placement for `record_race`
**Decision:** Call `leaderboard.record_race(species, track_name, finish_order_names)` **immediately after `race.run_race(...)` returns and BEFORE `race.show_podium(...)`.**

**Rationale:** Records the race result the moment `finish_order` is known, so a crash or exception in `show_podium` / `celebrate` / `announce_result` still leaves the race captured on disk and in the session list. Matches ROADMAP Phase 2 wording ("between `run_race(...)` and `show_podium(...)`").

**Implications:**
- Insertion point in `main.py` is the line directly after `winning_turtle, finish_order = race.run_race(racers, track_name, user_bet)` (currently [main.py:38](main.py#L38)) and before `race.show_podium(...)` (currently around line 39–40).
- The call must execute even if subsequent steps fail. Do not wrap it in a `try/except` that swallows exceptions from `record_race` itself — if persistence fails, that's a real problem the user should see.

### 2. Adapter from `finish_order` → name list
**Decision:** Inline one-liner at the call site:
```python
finish_order_names = [racers[i]['name'] for i in finish_order]
```

**Rationale:** `racers` and `finish_order` are both already in scope in `main()`. A one-liner is shorter than a function call, requires no new public API, and follows the existing main.py style. No need for a `race.py` helper.

**Implications:**
- No changes to `race.py`'s public API.
- No new test for the adapter itself (it's a stdlib comprehension).
- The order of `racers` is positional per species (per RESEARCH-1 §3 / CLAUDE.md), and `finish_order` is a list of lane indices into that list — so the mapping is unambiguous.

### 3. Testing strategy for the wiring
**Decision:** **Manual verification** for the wiring change. The builder runs `python main.py` three times — at least one turtle race and one snake race — and confirms `%APPDATA%\TurtleRace\leaderboard.json` accumulates the expected race records (schema_version: 1, three records in chronological order). The manual verification protocol must be documented in `SUMMARY-2.1.md` with each race's metadata (species, track, finish_order observed in the running game) so the recorded JSON can be checked against ground truth.

**Rationale:** `main.py` is the live Tk/turtle/pygame entry point — it cannot be cleanly unit-tested without significant scaffolding (Screen() initialization, dialog mocking, etc.). The wiring is one line. The verifier and reviewer will inspect the diff; the manual race runs verify the end-to-end flow.

**Implications:**
- No new automated test for the wiring change.
- The builder documents the three race runs in SUMMARY-2.1.md with exact `species`, `track`, and `finish_order_names` for each, plus the JSON file contents after each run.
- The full test suite (133 tests) must remain green — `pytest` runs as part of the verification regardless.

### 4. Path-traversal basename guard on `paths.user_data_path`
**Decision:** Add `if os.path.basename(filename) != filename: raise ValueError(...)` to `paths.user_data_path()`, plus 1–2 tests in `tests/test_paths.py` covering the raise on `"../evil"` and `"subdir/x.txt"`.

**Rationale:** Phase 2 introduces the first production-side caller of `paths.user_data_path` (via `leaderboard.record_race`). The auditor flagged this as L1 (latent, no current exposure) and the user explicitly chose at Phase 1 wrap to defer the guard to Phase 2. With production callers now in play, the guard goes in defensively, and a minimal test asserts the contract.

**Implications for implementation:**
- Modify `paths.user_data_path()` to validate `filename` before joining. Raise `ValueError` with a message naming the offending input.
- Add ~2 test functions to `tests/test_paths.py` (one for `..`-style traversal, one for path-separator-style). Both use `pytest.raises(ValueError)`.
- The error must NOT silently sanitize the path — sanitization is harder to reason about than rejection. Reject and let the (internal) caller fix its call.
- The existing `leaderboard.py` call `paths.user_data_path(_FILENAME)` where `_FILENAME = "leaderboard.json"` is a basename — no change required there. The guard is purely defensive against future callers.

## Open Questions Left for the Architect

- **Exact insertion structure in `main.py`:** the architect should specify whether to insert just the bare two-line addition (`finish_order_names = ...; leaderboard.record_race(...)`) or to introduce any local variable beyond `finish_order_names`. Recommend keeping it to exactly those two lines.
- **Import order in `main.py`:** the architect should specify whether `import leaderboard` goes alphabetically (between `import dialogs` and `import race`) or grouped with `import audio` (project-internal block). Match the existing style — `main.py:1-4` already groups: `import sys`, `import audio`, `import dialogs`, `import race`. Add `import leaderboard` between `import dialogs` and `import race` for alphabetical order within the project-internal block.

## Out-of-Scope Reminders (from PROJECT.md / ROADMAP.md)

- **No UI changes.** `dialogs.py` and the existing `ask_play_again` messagebox in `main.py` stay unchanged. Phase 3 restructures the menu.
- **No outer-loop restructure.** The `while keep_playing` loop in `main.py` keeps its current shape; Phase 2 just inserts two lines inside the round body.
- **No new `requirements.txt` entries.** Stdlib only.
- **No `turtle_race.spec` changes.** The leaderboard file is generated, not bundled.

## Carryover from Phase 1 (informational)

- `import leaderboard` (not `from leaderboard import record_race`) is fine here — only `leaderboard.py` itself needed `import paths` for the monkeypatch trick. Production-side callers like `main.py` can use either form. **Recommendation:** use `import leaderboard` and call `leaderboard.record_race(...)` to keep call-site context clear and to allow tests of main.py (if ever added) to monkeypatch through the module.
- Test hygiene rule from Plan 1.1 (`_fake_expanduser` helper) still applies if any new tests in this phase touch `os.path.expanduser`. They probably won't.
