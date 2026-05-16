# Turtle Race — Leaderboard Feature

## Project Name

Turtle Race Leaderboard

## Description

Add a persistent points-based leaderboard to the existing Turtle Race game (a Tk + `turtle` + `pygame` single-process desktop app, packaged as a Windows exe via PyInstaller). Race results — both within the current session and across all sessions historically — are tracked per racer, scored using a fixed point system, and viewable from a new main-menu-driven UI with time and species filters.

The feature extends the existing round loop without changing the race mechanics. App entry becomes main-menu-driven (Race / View Leaderboard / Quit); the existing track → species → bet → race → podium flow becomes one branch of that menu. Historic data is persisted in an append-only JSON log in the per-user app-data directory so the PyInstaller-bundled exe (which is read-only) can still write between runs.

## Goals

1. Award points to racers based on finishing position (6 / 3 / 1 / 0 for 1st / 2nd / 3rd / 4th) every time a race completes.
2. Persist race results across app sessions so historic stats survive restarts.
3. Let the user view a leaderboard table filtered by **time window** (Current Session, Today, This Week, This Month, This Year, All Time), **species** (Snakes, Turtles, All), and **track** (All Tracks, or any specific named track), with a separate **per-track breakdown** view that shows each racer's stats broken out by which track they ran on.
4. Give the user explicit ways to clear stats: a **Reset Session** button (clears only the current in-memory session) and a **Reset All** button (wipes the historic JSON file).
5. Reach the leaderboard from a new main-menu screen at app startup, without disrupting the fast "race-then-race-again" loop.

## Non-Goals

- No charts, graphs, or trend visualizations — table view only.
- No CSV / spreadsheet export.
- No editing or undo of individual race records.
- No per-racer detail drill-down view.
- No cloud sync, multi-user profiles, or networked leaderboard.
- No achievement / badge system.

## Requirements

### Functional — Scoring

- **Points by finishing position:** `[6, 3, 1, 0]` for places 1–4.
- **3-racer races (snakes):** only the first three point values are consumed (6 / 3 / 1). The 0-point slot exists only when a 4th finisher exists (turtle races).
- Points are awarded immediately after `race.run_race()` returns its `finish_order`.

### Functional — Persistence

- Historic data lives in `%APPDATA%\TurtleRace\leaderboard.json` on Windows (sensible fallback on other OSes). Resolved via a new `user_data_path(filename)` helper in [paths.py](paths.py), parallel to the existing `resource_path()`.
- File schema (versioned):
  ```json
  {
    "schema_version": 1,
    "races": [
      {"ts": "2026-05-16T14:32:11", "species": "turtles", "track": "straight",
       "finish_order": ["Leonardo", "Raphael", "Donatello", "Michaelangelo"]}
    ]
  }
  ```
- The whole file is rewritten on each race (kilobyte scale — no streaming needed).
- Current-session races are kept in an in-memory module-level list in `leaderboard.py` that resets on app start.

### Functional — Query

- Public `query(time_window, species_filter, track_filter="all")` returns rows of `(rank, racer_name, species, points, races, wins, podiums)` sorted by:
  1. Points (desc)
  2. Wins (desc) — Olympic tiebreaker
  3. Podiums (desc) — total medals
  4. Racer name (asc) — alphabetical
- Public `query_per_track(time_window, species_filter)` returns rows of `(racer_name, species, track, points, races, wins, podiums)` — one row per (racer × track) pair that has at least one race — sorted by track, then by the same point/wins/podiums/name order within each track.
- Time windows: `"session" | "today" | "week" | "month" | "year" | "all"`. "Week / Month / Year" are calendar-anchored to the local clock (current calendar week / month / year), not rolling N-day windows.
- Species filter: `"all" | "turtles" | "snakes"`.
- Track filter: `"all"` or the exact track name as recorded by `race.place_racers_on_track(...)`.

### Functional — UI

- **Main menu screen** (`get_main_menu_choice()` in [dialogs.py](dialogs.py)) at app entry — Toplevel over the lawn background with three buttons: **Race**, **View Leaderboard**, **Quit**. Returns the user's choice.
- **Leaderboard window** (`show_leaderboard()`) — Toplevel with:
  - A `ttk.Notebook` with two tabs: **Overall** and **Per Track**.
  - **Overall tab:** three `ttk.Combobox` filters at top (Time, Species, Track), and a `ttk.Treeview` with columns Rank, Racer, Points, Races, Wins, Podiums.
  - **Per Track tab:** two `ttk.Combobox` filters at top (Time, Species — no Track filter here, since this tab is itself a breakdown by track), and a `ttk.Treeview` with columns Track, Rank-in-track, Racer, Points, Races, Wins, Podiums. Rows are grouped by track (sorted alphabetically by track name) with ranks restarted within each track.
  - Three bottom buttons shared across tabs: **Reset Session**, **Reset All**, **Close**. Both reset buttons require a confirmation dialog before acting.
  - Changing any filter immediately re-queries and repopulates the active tab's Treeview (no explicit Refresh button).
  - Filter state is per-tab; switching tabs preserves each tab's own filters.
- **Post-race prompt** (`ask_play_again_choice()`) — replaces the current `messagebox.askyesno`. Three buttons: **Play Again**, **Main Menu**, **Quit**. Returns the chosen action.
- All new dialogs follow the existing pattern: `Toplevel` + `grab_set()` + `wait_window()` + `WM_DELETE_WINDOW` no-op to force a deliberate choice.

### Functional — Reset

- **Reset Session** — clears the in-memory current-session list only; the JSON file is not touched. Historic data survives.
- **Reset All** — wipes the JSON file (overwrites with `{schema_version: 1, races: []}`) and also clears the in-memory session list. Confirmation copy: "Delete all race history? This cannot be undone."

### Functional — Round Loop

- `main()` outer loop becomes main-menu-driven: `Race` enters the existing round flow; `View Leaderboard` opens the leaderboard then returns to the menu; `Quit` exits cleanly.
- A single `leaderboard.record_race(species, track, finish_order_names)` call is inserted in [main.py](main.py) right after `race.run_race()` returns.
- Tk root and the turtle `Screen()` are still created once at app start and reused across menu ↔ race transitions (same pattern as today's between-round reuse).

## Non-Functional Requirements

- **Resource resolution:** all I/O against bundled assets continues to use `resource_path()`; the new historic store uses `user_data_path()` and must never be created inside the PyInstaller bundle.
- **PyInstaller compatibility:** no new bundled assets are required (the leaderboard file is *generated*, not shipped). [turtle_race.spec](turtle_race.spec) needs no new `datas=` entries unless we add new images/fonts to the new dialogs.
- **Schema forward-compat:** `schema_version: 1` is written from day one so future format changes can migrate cleanly.
- **No regression** in the existing race loop (positional racer identity, head-position finish detection, podium scaling, MIDI shuffle, etc.) — those invariants from [CLAUDE.md](CLAUDE.md) are preserved.
- **Testability:** `leaderboard.py` is pure-Python with no Tk imports, so its scoring/query/reset logic is unit-testable without a display.

## Success Criteria

1. Running the game opens the main menu first; choosing **Race** flows through the existing track → species → bet → race → podium sequence unchanged from the user's perspective.
2. After each race, the user can pick **Play Again** / **Main Menu** / **Quit**; the choice routes correctly.
3. From the main menu, **View Leaderboard** opens a window with **Overall** and **Per Track** tabs. The Overall tab shows correct racers/points/races/wins/podiums for the selected time × species × track filter; the Per Track tab shows the same stats broken out by track (one Treeview group per track) for the selected time × species filter.
4. Restarting the app preserves historic data; the "Current Session" filter shows only races run since the latest start.
5. Points are awarded correctly for both 3-racer (snake) and 4-racer (turtle) races; the 4th-place 0-point slot is consumed only when a 4th finisher exists.
6. **Reset Session** clears in-memory session stats but historic data survives; **Reset All** wipes both, after a confirmation dialog.
7. Tied racers are sorted by Wins → Podiums → alphabetical name.
8. The packaged `dist/TurtleRace.exe` can read and write the leaderboard file (i.e., the historic store lives in `%APPDATA%\TurtleRace\`, not next to the exe).
9. `pytest` passes, including new `tests/test_leaderboard.py` covering scoring, time windows, species filter, tiebreaker order, session reset, all-reset, and missing-file creation.

## Constraints

- **Technical:**
  - Must coexist with the existing single-process Tk + turtle + pygame.mixer architecture; no new top-level runtime.
  - Must remain importable without a display (so `leaderboard.py` cannot import Tk at module level).
  - Must respect the `_MEIPASS` boundary — historic data is written outside the PyInstaller bundle.
  - Python standard library only for leaderboard logic (`json`, `datetime`, `pathlib`, `os`); no new third-party dependencies in `requirements.txt`. Tk's `ttk.Treeview` is stdlib.
- **UX:**
  - All new dialogs must use the established modal pattern (`Toplevel` + `grab_set` + `wait_window` + WM_DELETE no-op) for consistency with the existing track / species / bet dialogs.
- **Scope:** the deliberate non-goals above are off-limits for this feature; revisit only if requested as a follow-up.

## File-by-File Change Map (informational; the plan stage will firm this up)

**New**
- `leaderboard.py` — scoring, persistence, query, reset.
- `tests/test_leaderboard.py` — unit tests for the above.

**Modified**
- [paths.py](paths.py) — add `user_data_path()`.
- [dialogs.py](dialogs.py) — add `get_main_menu_choice()`, `show_leaderboard()`, `ask_play_again_choice()`.
- [main.py](main.py) — restructure to main-menu-driven outer loop; replace post-race messagebox; record each race.
- [CLAUDE.md](CLAUDE.md) — short addendum on the new main-menu entry point and the `%APPDATA%` data path.
