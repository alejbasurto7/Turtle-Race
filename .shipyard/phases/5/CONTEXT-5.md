# Phase 5 — Discussion Capture

Decisions locked before research/architect/builder dispatch. Phase 5 is the final wrap-up — keep it small and decisive.

## Decision 1 — Spiral 3-lane visual tuning: DEFERRED ENTIRELY

The deferred-since-Phase-2 spiral 3-lane geometry tuning is NOT in Phase 5 scope. Snake mode on the spiral track ships as-is. Document the deferral in the final SHIP-NOTES.md as a known follow-up.

**Rationale:** ship the milestone fast. If spiral-3 looks off in production use, open a follow-up plan. Pre-emptive tuning without a concrete visual complaint is wasted work.

## Decision 2 — `assets/midi/` MIDI files: LEAVE UNTRACKED

The 9 MIDI files Alejandro added to `assets/midi/` stay untracked. NOT part of this project's scope. Don't commit them, don't wire them up, don't delete them. Add `assets/midi/` to `.gitignore` to suppress the "untracked" noise in `git status` going forward.

## Decision 3 — Frozen build: BUILD-ONLY verification

Run `pyinstaller turtle_race.spec` and confirm:
- Exit code 0
- `dist/TurtleRace.exe` exists
- No errors/warnings about missing assets

**Skip** the manual smoke from the frozen `dist/TurtleRace.exe` itself (trust the dev-build smoke result from Phase 4). If pyinstaller fails or warns about missing assets, fix and re-run.

## Decision 4 — Carry-forward polish: include the 2 trivial items, defer the rest

**Include in Phase 5:**
- **Anaconda concrete head_offset test in `tests/test_race.py`** (SIMPLIFICATION-4 S4.4) — 3 lines, completes the species triple. `head_offset_arc = 20 * 6.0 / 2 = 60.0` for Anaconda (stretch_len = 1.2 * 5 = 6.0).
- **`create_racers` docstring length_units branch mention** (DOCUMENTATION-4 actionable) — 1-2 lines noting the `species == "snakes"` branch passes `SNAKE_LENGTHS[i]` to the drawer.

**Defer to future cleanup:**
- `winner_racer` lookup helper extraction (SIMPLIFICATION-4 S4.3) — rule-of-two; deferral fine.
- Anything else not explicitly listed.

## Decision 5 — Final regression sweep

- `pytest` full suite — 84 baseline + 1 new Anaconda test = expect 85/85
- Banned-identifier grep one more time — confirm no `tortuga`, `turtles_list`, `create_turtles`, `place_turtles_on_track`, `N_LANES` regressions snuck in
- Lightweight manual smoke (1 round each species on 1 track) to confirm the final state is what shipped — NOT the full matrix (already smoked iteratively through Phase 4)

## Decision 6 — Phase 5 deliverables

1. **`SHIP-NOTES.md`** at the project root — captures the milestone end-state for future-Alejandro:
   - What ships (turtle + snake species, 3 tracks, head-position fairness, etc.)
   - Known deferrals (spiral 3-lane visual tuning, MIDI files untracked)
   - How to run, test, build (cross-reference to CLAUDE.md commands)
   - Future-work suggestions
2. **`.gitignore` update** — add `assets/midi/`
3. **`tests/test_race.py`** — add Anaconda test
4. **`race.py`** — extend `create_racers` docstring
5. **`pyinstaller` build pass** — proves the spec/datas bundling works end-to-end

## Decision 7 — Final ship-time documentation pass

- CLAUDE.md was updated in Phase 3 and Phase 4. Verify it's still accurate for the final state. Tiny touch-ups OK if anything drifted.
- PROJECT.md "Open Items" section — clean up resolved items (Ralph color, L_BASE, classic-vs-polygon decision are all resolved).

## Builder/agent reminders (still relevant)

1. **Write SUMMARY-W.P.md to disk before returning.**
2. **Reviewers MUST write REVIEW-W.P.md to disk.**
3. **File-specific `git add`.**
4. **Per-task atomic commits.**

## Out-of-scope reminders

- No new features (e.g., music shuffle from MIDI files).
- No new tests beyond the Anaconda one.
- No new modules.
- No structural refactors (winner_racer helper, etc.).
- No CI setup, GitHub Actions, badges, etc.

This is a wrap-up phase. Get the milestone done.
