# CONTEXT — Phase 1: Persistence + Scoring Core

User decisions captured during `/shipyard:plan 1` Discussion Capture (2026-05-16). These are not architect/builder recommendations — they were chosen by the user and must be followed by all downstream agents.

## Decisions

### 1. Timestamp format & timezone
**Decision:** Local time, ISO 8601 with no timezone suffix (e.g. `2026-05-16T14:32:11`).

**Implications for implementation:**
- `record_race(...)` calls `datetime.now()` (no `.astimezone(timezone.utc)`).
- Format with `.isoformat(timespec="seconds")`.
- Parsing back uses `datetime.fromisoformat(ts)` — returns a naive datetime in local time.
- All time-window comparisons happen in local time. No tz conversions anywhere.
- "Today" is bounded by the local-clock midnight of the user's machine.

### 2. Week start day
**Decision:** Monday (ISO week).

**Implications for implementation:**
- "This Week" runs Monday 00:00 through Sunday 23:59:59 of the current ISO week.
- Use `date.isocalendar()` or `date.weekday()` (Mon=0).
- Compute week_start as `today - timedelta(days=today.weekday())`.
- No locale lookup; this is a hard rule.

### 3. Corrupt-file recovery
**Decision:** Warn (stderr), quarantine the broken file, start fresh.

**Implications for implementation:**
- On load, if `json.load` raises `JSONDecodeError` (or the parsed structure fails schema validation), the loader:
  1. Renames the original file to `leaderboard.json.corrupt-{YYYYMMDDTHHMMSS}` (local timestamp).
  2. Writes a fresh `{"schema_version": 1, "races": []}` to the canonical path.
  3. Prints one line to `sys.stderr`: `leaderboard: existing file unparseable, quarantined to <path>; starting fresh`.
- No exceptions propagate to the caller. The game keeps running.
- The quarantine file is never read again by the game; it exists only for the user to inspect.

### 4. Test-time injection of `now`
**Decision:** Optional `now=None` keyword argument on `query()` and `query_per_track()`.

**Implications for implementation:**
- Function signatures:
  - `query(time_window: str, species_filter: str = "all", track_filter: str = "all", *, now: datetime | None = None) -> list[Row]`
  - `query_per_track(time_window: str, species_filter: str = "all", *, now: datetime | None = None) -> list[PerTrackRow]`
- When `now is None`, use `datetime.now()` (matches the local-time decision above).
- Production callers in `main.py` / `dialogs.py` omit `now=`. Only tests pass it.
- No module-level `_NOW` hook, no monkeypatching. The parameter is the only injection point.

### 5. Track filter dropdown source
**Decision:** Only tracks that appear in the on-disk history.

**Implications for implementation:**
- `known_tracks() -> list[str]` returns the sorted, deduplicated set of `track` values from the union of (on-disk races) and (current-session races).
- On a fresh install with no races, `known_tracks()` returns `[]`; the UI then shows only the `"All Tracks"` option.
- No reference to `constants.py`, `tracks.py`, or any canonical track list in `leaderboard.py`. The module is purely data-driven.
- After `reset_all()`, `known_tracks()` returns `[]` again — the UI must re-read it (per Phase 4 success criteria).

## Open Questions Left for the Architect

These are implementation choices that don't need user input but are worth being deliberate about:

- **Atomic write strategy** — `tempfile.NamedTemporaryFile` in the same directory + `os.replace()` is the obvious cross-platform pattern. Architect should confirm and use it.
- **Where the `Row` / `PerTrackRow` types live** — `dataclasses.dataclass(frozen=True)` is the natural fit. Architect decides on field types and exact names.
- **How `current_session_races` is exposed** — internal list vs. read-only accessor. Architect call; preference is to keep it private (`_SESSION_RACES`) and only expose it through the query/reset functions.
- **Test fixture for the JSON file path** — `pytest`'s `tmp_path` plus monkeypatching `paths.user_data_path` is the clean approach; architect should specify.

## Out-of-Scope Reminders (from PROJECT.md / ROADMAP.md)

- No UI changes in Phase 1. `dialogs.py` and `main.py` stay untouched.
- No third-party dependencies. Stdlib only (`json`, `datetime`, `pathlib`, `os`, `sys`, `tempfile`).
- No schema migration code yet — ship v1 only.
- Module must remain importable without a display (`leaderboard` cannot import `tkinter` at module level, even transitively).
