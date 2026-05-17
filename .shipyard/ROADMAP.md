# ROADMAP — Turtle Race Leaderboard

## Overview

This roadmap delivers the persistent points-based leaderboard described in [.shipyard/PROJECT.md](PROJECT.md). The work is split into five phases, ordered to fail fast on the highest-risk surfaces (persistence + calendar-window arithmetic, then UI restructure) while keeping the app runnable at the end of every phase. The integration approach is additive: a new tk-free `leaderboard.py` module owns scoring/persistence/query; [paths.py](../paths.py) gains a `user_data_path()` helper parallel to the existing `resource_path()`; [dialogs.py](../dialogs.py) gains three new dialogs that follow the established `Toplevel + grab_set + wait_window + WM_DELETE no-op` pattern; and [main.py](../main.py)'s outer loop is restructured to be main-menu-driven. No existing race-loop invariants from [CLAUDE.md](../CLAUDE.md) are touched.

The five phases each correspond to one shipyard milestone with `git_strategy: per_task` producing 2–4 atomic commits per phase.

## Dependency Diagram

```
            +------------------------------------+
            | Phase 1: Persistence + Scoring     |
            |   leaderboard.py (Tk-free)         |
            |   paths.user_data_path()           |
            |   tests/test_leaderboard.py        |
            |   Risk: HIGH (schema, calendar     |
            |          windows, %APPDATA% path)  |
            +-----------------+------------------+
                              |
                              v
            +------------------------------------+
            | Phase 2: Record Hook                |
            |   main.py calls record_race(...)   |
            |   after race.run_race()            |
            |   (still uses old messagebox)      |
            |   Risk: LOW                         |
            +-----------------+------------------+
                              |
                              v
            +------------------------------------+
            | Phase 3: Menu + Post-Race Restruct  |
            |   get_main_menu_choice()           |
            |   ask_play_again_choice()          |
            |   main() outer-loop rewrite        |
            |   Risk: MEDIUM (Tk lifecycle,      |
            |          screen.clear flow)        |
            +-----------------+------------------+
                              |
                              v
            +------------------------------------+
            | Phase 4: Leaderboard View           |
            |   show_leaderboard() Toplevel      |
            |   ttk.Treeview, filters, resets    |
            |   Risk: MEDIUM (Treeview repop,    |
            |          confirm flow, GC of imgs) |
            +-----------------+------------------+
                              |
                              v
            +------------------------------------+
            | Phase 5: Polish & Ship              |
            |   CLAUDE.md addendum                |
            |   spec sanity, README touchups      |
            |   packaged-exe smoke test           |
            |   Risk: LOW                         |
            +------------------------------------+
```

Phases are strictly sequential. There is no opportunity for parallel phases here — every later phase reads symbols that an earlier phase introduces.

---

## Phase 1 — Persistence + Scoring Core

**Goal:** Stand up a Tk-free `leaderboard.py` with record/query/reset plus a `paths.user_data_path()` helper, all backed by unit tests. The running app is untouched.

**Dependencies:** None.

**Risk: HIGH** — this phase owns the design choices the rest of the feature locks onto: JSON schema, calendar-window semantics, `%APPDATA%` resolution, and tiebreaker sort. Mistakes here cascade into every later phase. The calendar-week / -month / -year arithmetic is the part most likely to bite (ISO week vs. locale week, DST boundaries on `datetime.now()`, first-of-year edge cases).

**Success criteria** (all must pass before declaring the phase done):
- [ ] `leaderboard.py` exists at project root and contains: `record_race(species, track, finish_order_names)`, `query(time_window, species_filter, track_filter="all")`, `query_per_track(time_window, species_filter)`, `known_tracks()` (returns the sorted set of track names that appear in the history — used to populate the Track filter dropdown), `reset_session()`, `reset_all()`, plus module-level current-session state.
- [ ] `import leaderboard` succeeds in a headless Python with no `DISPLAY` and no Tk root — verified by `python -c "import leaderboard"` from a subprocess without `tkinter` being touched.
- [ ] `paths.user_data_path(filename)` returns `%APPDATA%/TurtleRace/<filename>` on Windows, falls back to `~/.turtle_race/<filename>` (or platform-appropriate equivalent) elsewhere, creates the parent directory if missing, and **never** returns a path inside `sys._MEIPASS`.
- [ ] Schema written on first call is exactly `{"schema_version": 1, "races": []}` plus the new race appended; whole-file rewrite is atomic enough that a mid-write crash does not corrupt the file (write-to-temp-then-replace).
- [ ] `query()` sort order matches PROJECT.md: points desc → wins desc → podiums desc → name asc.
- [ ] `query()` track filter: `"all"` returns the full set; a specific track name returns only races run on that track; an unknown track name returns an empty result without raising.
- [ ] `query_per_track()` returns one row per (racer × track) pair that has at least one race in the window, sorted by track name asc, then by points/wins/podiums/name within each track group.
- [ ] `known_tracks()` returns the sorted, deduplicated set of track names that appear in the on-disk history (used by the UI to populate the Track filter dropdown).
- [ ] Time windows `session`, `today`, `week`, `month`, `year`, `all` each return the expected subset for a fixture with races spanning multiple calendar boundaries.
- [ ] Scoring rule [6, 3, 1, 0] is correctly truncated for 3-racer (snake) races so only 6/3/1 are awarded.
- [ ] `tests/test_leaderboard.py` covers: empty-state query, 1st-place scoring, 4th-place 0-point slot, 3-racer truncation, tiebreak via wins, tiebreak via podiums, tiebreak via name, time-window filtering across calendar boundaries (use injectable `now` or `freezegun`-free monkeypatch — stdlib only), species filter `all/turtles/snakes`, track filter (`all` vs specific track vs unknown track), `query_per_track` grouping and within-group order, `known_tracks` dedup + sort, `reset_session` leaving file intact, `reset_all` wiping both, missing-file auto-creation, corrupt-file recovery (graceful fallback to empty state with a warning print).
- [ ] All existing tests still pass — `pytest` returns green.
- [ ] App still runs identically (`python main.py` produces no behavioral change; new module is unused at runtime).

**Out-of-scope for this phase:**
- Any UI changes — `dialogs.py` and `main.py` are not touched.
- Wiring `record_race` into the round loop — deferred to Phase 2.
- Reading/displaying historic data in any dialog — deferred to Phase 4.
- Migration logic for `schema_version > 1` — we ship v1 only; design to allow future versions but don't implement migrators yet.

**Approximate task count:** 3 (split: `user_data_path` + tests; `leaderboard.py` record/persist + tests; `leaderboard.py` query + reset + tests).

---

## Phase 2 — Wire Recording into the Round Loop

**Goal:** Insert a single `leaderboard.record_race(species, track, finish_order_names)` call in [main.py](../main.py) immediately after `race.run_race(...)` returns. Verify the JSON file appears in `%APPDATA%\TurtleRace\` after a run.

**Dependencies:** Phase 1.

**Risk: LOW** — single call site, well-defined inputs, no UI change.

**Success criteria:**
- [ ] A single `record_race(...)` call is inserted in `main.py` between `run_race(...)` and `show_podium(...)`. The species string comes from the existing per-round species selection; the track from the existing `track_name`; the finish-order names from a tiny adapter that maps `finish_order` (currently a list of racer dicts or turtle handles — confirmed against current `race.run_race` return type) to a list of `str` names.
- [ ] After one full race from source, `%APPDATA%\TurtleRace\leaderboard.json` exists, contains `schema_version: 1`, and lists exactly one race with the correct `species`, `track`, and 3- or 4-entry `finish_order`.
- [ ] After two more races (one of each species), the file lists exactly three races in chronological order.
- [ ] Existing post-race messagebox flow is unchanged; the app still asks "play again?" with yes/no as before.
- [ ] `pytest` remains green (Phase 1 tests untouched, no new tests required beyond optional manual verification).

**Risk notes:**
- Need to confirm whether `race.run_race`'s `finish_order` is a list of racer dicts, names, or live `Turtle` objects — the adapter must convert to names cleanly. (Quick `Grep` during the plan stage.)
- The PyInstaller `_MEIPASS` boundary is only meaningful in the frozen build; the source run will write under the user's real `%APPDATA%`. Confirm the source-run path is not accidentally `<project>/leaderboard.json`.

**Out-of-scope for this phase:**
- Reading or displaying the data anywhere.
- Restructuring the outer loop or post-race prompt — deferred to Phase 3.
- Any session-vs-historic UI distinction — deferred to Phase 4.

**Approximate task count:** 1–2 (finish-order adapter + record call; manual verification documented in commit message).

---

## Phase 3 — Main Menu and Post-Race Prompt Restructure

**Goal:** Restructure `main()` to be main-menu-driven. Add `get_main_menu_choice()` (Race / View Leaderboard / Quit) and `ask_play_again_choice()` (Play Again / Main Menu / Quit) to [dialogs.py](../dialogs.py). The "View Leaderboard" choice can be a temporary stub that pops a placeholder message — the real window comes in Phase 4.

**Dependencies:** Phase 2.

**Risk: MEDIUM** — touches the main control flow and the Tk/turtle lifecycle. The existing CLAUDE.md invariant is that `Screen()` is created once and reused via `screen.clear()`; the new menu must not break this. Also need to make sure `pygame.mixer` start/stop still bracket the whole app lifetime, not per-round.

**Success criteria:**
- [ ] `dialogs.get_main_menu_choice()` returns one of `"race" | "leaderboard" | "quit"` and uses the established `Toplevel + grab_set + wait_window + WM_DELETE no-op` pattern, drawn over the lawn background.
- [ ] `dialogs.ask_play_again_choice()` returns one of `"again" | "menu" | "quit"` via three buttons; the old `ask_play_again()` callsite in `main.py` is replaced.
- [ ] `main()`'s outer loop is reshaped into a two-level structure: an outer "menu" loop and an inner "race rounds" loop. Choosing **Race** from the menu enters the inner loop; the inner loop's post-race prompt offers Play Again (re-enter inner loop top), Main Menu (break to outer), or Quit (terminate cleanly).
- [ ] Choosing **View Leaderboard** opens a placeholder Toplevel ("Coming in Phase 4") and returns to the menu when dismissed. (Real window in Phase 4.)
- [ ] Tk `Screen()` and `pygame.mixer` are still initialized once at app start and torn down once at exit — verified by running the app, racing twice, returning to the menu, racing once more, then quitting; no double-init crashes or "screen already exists" errors.
- [ ] `screen.clear()` + `set_background()` are still called at the top of each race round, not on menu entry (menu draws over its own Toplevel, not the turtle canvas).
- [ ] `pytest` remains green.
- [ ] All existing race-loop invariants from CLAUDE.md preserved (positional identity, head-position finish, podium scaling, MIDI shuffle).

**Risk notes:**
- The current `ask_play_again` returns bool; three return values requires updating every caller. Confirm there is only one call site in `main.py`.
- `screen.clear()` between menu and race transitions: the existing pattern is `clear()` at the top of each round; verify the new outer loop preserves this exactly. Calling `clear()` while a Toplevel is grabbing input can cause flicker — order matters.
- Avoid recreating dialogs that hold image references; if the menu lives across many race rounds, its `PhotoImage`s must be retained across reopen (or recreated each open — both work, but the choice affects perceived responsiveness).
- The "menu over lawn background" UX needs a decision: paint the lawn behind the menu Toplevel, or use a self-contained background. Lean toward Toplevel-over-canvas for visual continuity with the existing dialogs.

**Out-of-scope for this phase:**
- The real leaderboard window (placeholder only).
- Treeview, filters, reset buttons — deferred to Phase 4.

**Approximate task count:** 3 (menu dialog; post-race dialog; main.py outer-loop restructure with placeholder).

---

## Phase 4 — Leaderboard View

**Goal:** Implement the real `show_leaderboard()` Toplevel as a **single-view window** (no Notebook): four filter combos (Time, Species, Track, Group by) above a single `ttk.Treeview` that reshapes its columns based on `Group by`, plus three bottom buttons (Reset Session, Reset All, Close). End-to-end feature complete.

**Dependencies:** Phase 3.

**Risk: MEDIUM** — `ttk.Treeview` column-reshape on `Group by` change is the primary risk vector (must reconfigure `columns`, `heading`, and `column` setup AND repopulate without flicker). The two reset confirmation dialogs use `tkinter.messagebox.askyesno` for a native, familiar UX.

**Success criteria:**
- [ ] `dialogs.show_leaderboard()` opens a `Toplevel` containing four `ttk.Combobox` filters (Time, Species, Track, Group by), one `ttk.Treeview`, an inline empty-state label, and three bottom buttons (Reset Session / Reset All / Close).
- [ ] Combobox values: Time = `Current Session, Today, This Week, This Month, This Year, All Time`; Species = `All, Turtles, Snakes`; Track = `All Tracks` plus each value returned by `leaderboard.known_tracks()` (populated when the window opens; refreshed after any reset); Group by = `None, Track`. Defaults: `All Time`, `All`, `All Tracks`, `None`.
- [ ] All combos are `state="readonly"` so the user cannot type custom values.
- [ ] When `Group by = None`: Treeview has columns Rank / Racer / Points / Races / Wins / Podiums; rows come from `leaderboard.query(time, species, track)`.
- [ ] When `Group by = Track`: Treeview has columns Track / Rank-in-track / Racer / Points / Races / Wins / Podiums; rows come from `leaderboard.query_per_track(time, species)` (no track filter applied at the query layer); rows are visually grouped by track (sorted alphabetically by track name) with ranks restarting per track.
- [ ] When `Group by = Track` is selected, the **Track filter combobox is automatically disabled** (greyed out via `state="disabled"`). When `Group by` switches back to `None`, the Track filter is re-enabled (back to `state="readonly"`). Toggling `Group by` does not lose the Track filter's previously selected value.
- [ ] Changing any filter immediately re-queries and repopulates the Treeview — no explicit Refresh button. Repopulation does not flicker visibly on a typical-size dataset (`delete(*get_children())` then batch `insert`).
- [ ] When the filtered result is empty, an inline label below the filter row reads `No races recorded` and the Treeview is empty. The label is hidden when the result is non-empty.
- [ ] **Reset Session** uses `tkinter.messagebox.askyesno("Reset Session", "Clear current session stats?")` with default focus on No. On Yes: calls `leaderboard.reset_session()`, refreshes the Track combobox values (in case session-only tracks disappear), and re-queries. Historic data on disk untouched.
- [ ] **Reset All** uses `tkinter.messagebox.askyesno("Reset All", "Delete all race history? This cannot be undone.")` with default focus on No. On Yes: calls `leaderboard.reset_all()`, resets the Track combobox to `["All Tracks"]` only, and re-queries (table becomes empty). The JSON file is overwritten to `{schema_version: 1, races: []}`.
- [ ] **Close** dismisses the window and returns control to the main menu.
- [ ] Window is properly modal over the menu (`grab_set` + `wait_window` + WM_DELETE redirected to the Close handler).
- [ ] Restarting the app preserves historic data; the **Current Session** filter shows only races run since the latest start.
- [ ] All Phase 1–3 success criteria still hold; `pytest` remains green.

**Risk notes:**
- `ttk.Treeview` column-reshape on Group-by change requires reconfiguring `columns`, `heading()`, and `column()` for the active column set, then repopulating. Encapsulate in a `_rebuild_columns(group_by)` helper.
- `ttk.Treeview` column sizing on Windows can shift between Python versions — set explicit `width=` and `anchor=` on each column.
- The placeholder body in `dialogs.show_leaderboard_placeholder()` (from Phase 3) is replaced in-place by Phase 4. **The function name stays `show_leaderboard_placeholder` OR is renamed to `show_leaderboard`** — architect's call; rename requires updating `main.py:32`. Recommendation: rename to `show_leaderboard()` and update the one call site atomically.
- All four combos must be `state="readonly"`; the Track combo additionally toggles between `"readonly"` and `"disabled"` based on Group by.
- The PhotoImage GC pattern (`dialog._..._images`) is irrelevant here — Treeview rows are text-only, no images.

**Out-of-scope for this phase:**
- Editing or deleting individual race records (non-goal in PROJECT.md).
- Per-racer drilldown views (non-goal).
- CSV export, charts, achievements (non-goals).
- The Notebook + tabbed structure that earlier roadmap revisions specified — replaced by the single-view + Group-by approach in CONTEXT-4 Decision 1.

**Approximate task count:** 3 (build the show_leaderboard window with filter row + Treeview + empty-state label; wire filter callbacks including Group-by column-reshape and Track-filter disable/enable; add reset confirmations + rename function and update main.py call site).

---

## Phase 5 — Polish and Ship

**Goal:** Documentation, spec sanity check, and a packaged-exe smoke test. The feature is functionally complete after Phase 4; this phase makes it shippable.

**Dependencies:** Phase 4.

**Risk: LOW** — mostly documentation. The packaging smoke test could surface a `_MEIPASS` path bug if Phase 1's `user_data_path` was implemented wrong; that's the one place a regression could appear.

**Success criteria:**
- [ ] [CLAUDE.md](../CLAUDE.md) gains a short addendum (10–20 lines) covering: the new main-menu entry point, the `%APPDATA%\TurtleRace\leaderboard.json` data path, the `leaderboard.py` module's Tk-free invariant, and a pointer to the JSON schema version field.
- [ ] [turtle_race.spec](../turtle_race.spec) is reviewed — no new `datas=` entries are required (the leaderboard file is generated at runtime, not bundled), but confirm explicitly in the spec comment or commit message.
- [ ] README (if one exists / once one exists) — describe how to view the leaderboard and where data is stored. (If no README, this bullet is skipped without ceremony.)
- [ ] Build `dist/TurtleRace.exe` via `pyinstaller turtle_race.spec`; run the exe; race once; quit; confirm `%APPDATA%\TurtleRace\leaderboard.json` now contains that race; re-launch the exe and verify the **All Time** view shows it.
- [ ] Smoke-test all reset paths from the packaged exe: Reset Session leaves the JSON file present and unchanged; Reset All wipes it to `{schema_version: 1, races: []}`.
- [ ] All previous-phase success criteria still hold.
- [ ] `pytest` remains green.

**Risk notes:**
- If `user_data_path()` accidentally falls back to a path inside `_MEIPASS` in the frozen build, the exe will appear to work for one run and then "lose" data on every relaunch (because `_MEIPASS` is recreated per launch). The smoke test of relaunching and seeing the prior race is what catches this.
- If `pygame.mixer` or `tkinter` import differently in the frozen build than in source, surface that here, not later.

**Out-of-scope for this phase:**
- Any new functionality.
- Changes to scoring, filters, or UI.
- Performance optimization beyond verifying no obvious regression.

**Approximate task count:** 2 (docs touchup; packaged-exe smoke test with a written checklist in the commit message).

---

## Summary

| Phase | Goal | Risk | Approx. Tasks | Status |
|------:|------|:----:|:-------------:|:------:|
| 1 | Persistence + scoring core (Tk-free) | HIGH | 3 plans / 7+1 commits | **COMPLETE** (2026-05-16) |
| 2 | Wire `record_race` into round loop + paths basename guard | LOW | 1 plan / 3+1 commits | **COMPLETE** (2026-05-16) |
| 3 | Main menu + post-race restructure | MED | 2 plans / 5+1 commits | **COMPLETE** (2026-05-17) |
| 4 | Leaderboard view (Notebook: Overall + Per Track tabs, filters, resets) | MED | 4 | pending |
| 5 | Polish, docs, packaged-exe smoke test | LOW | 2 | pending |

Total: 13–14 atomic commits across 5 sequential phases, each leaving the app in a runnable state.
