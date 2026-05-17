# Review: Plan 2.1

## Verdict: MINOR_ISSUES

## Findings

### Critical
- None.

### Minor
- **`_FILTER_LABEL_TO_KEY` value-level drift is unchecked.** Lines 114–123 of `tools/smoke_phase_4.py` assert that the expected display-string keys (`"All Time"`, `"Current Session"`, `"Today"`, `"This Week"`, `"This Month"`, `"This Year"`, `"All"`, `"Turtles"`, `"Snakes"`, `"None"`, `"Track"`) are present in the dict, but do not spot-check the mapped values (e.g., `_label_to_key["All Time"] == "all"`, `_label_to_key["Current Session"] == "session"`, `_label_to_key["Track"] == "track"`). Since the plan's stated purpose for this check is "regression signal if Plan 1.1's translation dict drifts", a value-level drift (e.g., someone renaming the "all" enum to "ALL_TIME") would slip past. Adding 3–4 spot-check assertions would close this gap. Non-blocking — the dict is small and stable, and the seven step assertions would still catch most real regressions via downstream behavior changes.
- **Step 4 assertion `len(rows) == 4` relies on aggregation semantics that aren't explained inline.** The comment at line 182 says "4 turtle racers → 4 unique racer entries" but doesn't note WHY (`query()` aggregates by racer name across all races; the smoke's two turtle races share no racer names with each other only because they're across different tracks — but a track-filtered query collapses to the four racers of that specific track's single race). Tightening the comment to say "single turtle race on this track → 4 unique racer aggregation entries" would make the brittleness boundary explicit for future maintainers. Cosmetic.
- **`sys.exit(1)` inside `fake_show_leaderboard` propagates as `SystemExit` through `main.main()`.** This is intentional and correct behavior per the plan ("non-zero with a diagnostic message on any verification failure"), but it means `audio.stop_background_music()` and `screen.bye()` at `main.py:76-77` will NOT run on the smoke-failure path. Acceptable for a dev-tool failure mode; documented here so the next reviewer doesn't re-discover and flag it as a leak.

### Positive
- **Spec-faithful, end-to-end coverage of the Phase 4 GUI contract surface.** All seven plan steps land in the right order with the correct API call signatures: `query(time, species, track)` and `query_per_track(time, species)` are exercised with their full positional argument shapes; `known_tracks()`, `reset_session()`, `reset_all()` each get a dedicated step; per-track rank-restart-at-1 invariant is verified.
- **`show_leaderboard_calls == 1` post-main assertion is the key regression net.** This is exactly the failure mode Phase 3's first-cut smoke missed (the leaderboard branch went unexercised because of a wrong monkeypatch target). The counter + assertion makes silent skip impossible.
- **Env redirect ordering is correct and verifiably so.** `os.environ["APPDATA"] = tmpdir` is the first non-stdlib-import line; `import dialogs` / `import audio` are deferred until after the redirect; `import leaderboard` is further deferred to inside `fake_show_leaderboard()`. The smoke would fail loudly on Windows if any of these orderings were broken (a wrong `APPDATA` resolution writes the leaderboard JSON to the real user-profile path), so the ordering is both correct AND self-checking via the final on-disk assertion at line 304.
- **Monkeypatch surface is complete and module-attribute-based.** Every callable `main.main()` could reach (`dialogs.*` × 6, `audio.*` × 2, `tkinter.messagebox.askyesno`) is patched. The `dialogs.show_leaderboard = fake_show_leaderboard` patch correctly targets the module attribute (not a local alias), which is the non-obvious gotcha PLAN-2.1's monkeypatch surface explicitly called out — and the builder got it right.
- **3-round canned plan is consistent with Phase 3's pattern.** Iterator-based monkeypatches, `round_idx` bumped on `fake_get_user_track` (the first per-round dialog), `[smoke] ...` log prefix throughout, tmpdir-via-`tempfile.mkdtemp` with the kept-on-disk-for-inspection trailing log line — all matches `smoke_phase_3.py`'s conventions, making the two smokes easy to read side-by-side.
- **No flakiness risk.** Synchronous, deterministic, no threading, no networking, no race conditions, no time-based assertions (the `Today`/`This Week`/`This Month`/`This Year` Time filters are validated only at the key-presence level, not by actual time-bucketing behavior).
- **`tools/smoke_phase_3.py`, `dialogs.py`, `main.py`, and `leaderboard.py` are confirmed unchanged.** Carryover note honored.
- **All verification commands pass independently:**
  - `python tools/smoke_phase_4.py` → exit 0, prints `[smoke] leaderboard driver PASS` and `[smoke] PASS — 3 races recorded, ...`.
  - `pytest -q` → 135 passed (smoke not in test collection).

Plan 2.1 is functionally complete. The minor findings are coverage enhancements, not blockers. Recommend proceeding to phase verification.
