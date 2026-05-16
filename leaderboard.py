import json
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, date, timedelta

import paths


# --- Constants ---

POINTS = (6, 3, 1, 0)
SCHEMA_VERSION = 1
_FILENAME = "leaderboard.json"


# --- Module-level session state ---

_SESSION_RACES: list[dict] = []   # populated by record_race; resets on import


# --- Private helpers ---

def _path() -> str:
    # Wrapped in a function (not a module-level constant) so that
    # monkeypatching paths.user_data_path in tests takes effect on every call.
    # Must call paths.user_data_path through the module (not a local alias)
    # so monkeypatch.setattr("paths.user_data_path", ...) intercepts it.
    return paths.user_data_path(_FILENAME)


def _empty_store() -> dict:
    return {"schema_version": SCHEMA_VERSION, "races": []}


def _atomic_write_json(data: dict, target_path: str) -> None:
    """Write *data* as JSON to *target_path* atomically using a temp file + os.replace."""
    target_dir = os.path.dirname(target_path) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".leaderboard.", suffix=".tmp", dir=target_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, target_path)   # atomic on Windows + POSIX
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _quarantine_and_reset(reason: str) -> dict:
    """Rename the corrupt file aside, write a fresh store, warn to stderr. Never raises."""
    quarantine_path = f"{_path()}.corrupt-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
    try:
        os.replace(_path(), quarantine_path)
        _atomic_write_json(_empty_store(), _path())
    except Exception:
        # If even the recovery fails, fall through — caller still gets _empty_store().
        pass
    print(
        f"leaderboard: existing file unparseable, quarantined to {quarantine_path}; starting fresh",
        file=sys.stderr,
    )
    return _empty_store()


def _load() -> dict:
    """Return the on-disk store, or an empty store if missing or corrupt."""
    path = _path()
    if not os.path.exists(path):
        # Do NOT write a file here; let _save() create it on first record.
        return _empty_store()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return _quarantine_and_reset("JSONDecodeError")
    # Structural validation
    if (
        not isinstance(data, dict)
        or "schema_version" not in data
        or "races" not in data
        or not isinstance(data["races"], list)
    ):
        return _quarantine_and_reset("invalid structure")
    return data


def _save(data: dict) -> None:
    """Persist *data* atomically to the canonical leaderboard path."""
    _atomic_write_json(data, _path())


# --- Public API ---

def record_race(species: str, track: str, finish_order_names: list[str]) -> None:
    """Append a race result to the session list and persist it to disk.

    Args:
        species: species key, e.g. "turtles" or "snakes".
        track: track name, e.g. "straight", "rectangular", "spiral".
        finish_order_names: racer names in finishing order (1st to last).
    """
    record = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "species": species,
        "track": track,
        "finish_order": list(finish_order_names),   # defensive copy
    }
    _SESSION_RACES.append(record)
    store = _load()
    store["races"].append(record)
    _save(store)


# --- Public row types (frozen dataclasses — Tk-free, no third-party deps) ---

@dataclass(frozen=True)
class Row:
    rank: int
    racer_name: str
    species: str
    points: int
    races: int
    wins: int
    podiums: int


@dataclass(frozen=True)
class PerTrackRow:
    track: str
    rank: int
    racer_name: str
    species: str
    points: int
    races: int
    wins: int
    podiums: int


# --- Private query helpers ---

_VALID_WINDOWS = frozenset({"all", "session", "today", "week", "month", "year"})


def _validate_window(window: str) -> None:
    """Raise ValueError immediately for unknown time_window values."""
    if window not in _VALID_WINDOWS:
        raise ValueError(f"unknown time_window: {window!r}")


def _races_for_window(window: str) -> list[dict]:
    """Return the appropriate race source list for the given time window.

    Session vs. disk distinction (IMPORTANT — do NOT concatenate):
    - record_race writes to BOTH _SESSION_RACES and disk atomically.
    - _load()["races"] therefore already contains current-session records.
    - For "session" queries we read _SESSION_RACES only (in-process races).
    - For all other windows we read disk only (which includes session records).
    - Concatenating both would double-count current-session races.
    """
    if window == "session":
        return list(_SESSION_RACES)
    return _load()["races"]


def _in_window(ts_str: str, window: str, now: datetime) -> bool:
    """Return True if the ISO timestamp string falls within the given window."""
    if window in ("all", "session"):
        # "all" is unconditional; "session" callers already filtered by source list.
        return True
    record_date = datetime.fromisoformat(ts_str).date()
    if window == "today":
        return record_date == now.date()
    if window == "week":
        # ISO Monday-start week (CONTEXT-1 Decision 2).
        today = now.date()
        week_start = today - timedelta(days=today.weekday())   # Monday of current week
        week_end_exclusive = week_start + timedelta(days=7)    # next Monday
        return week_start <= record_date < week_end_exclusive
    if window == "month":
        return record_date.year == now.year and record_date.month == now.month
    if window == "year":
        return record_date.year == now.year
    raise ValueError(f"unknown time_window: {window!r}")


def _species_matches(record_species: str, species_filter: str) -> bool:
    """True when species_filter is 'all' or matches the record's species exactly."""
    return species_filter in ("all", record_species)


def _aggregate(records: list[dict]) -> dict[str, dict]:
    """Accumulate per-racer scoring stats from a filtered list of race records.

    Scoring (CONTEXT-1 / ROADMAP):
      place 0 → POINTS[0] = 6 (win)
      place 1 → POINTS[1] = 3
      place 2 → POINTS[2] = 1
      place 3 → POINTS[3] = 0
      place >= len(POINTS) → 0 (graceful — not expected in current data)

    3-racer truncation: for a 3-element finish_order, enumerate yields indices
    0/1/2 only, so POINTS[0/1/2] = 6/3/1 are used and the 0-slot (index 3)
    is never reached. No phantom 4th-racer entry is created.
    """
    stats: dict[str, dict] = {}
    for record in records:
        for place, name in enumerate(record["finish_order"]):
            pts = POINTS[place] if place < len(POINTS) else 0
            if name not in stats:
                stats[name] = {
                    "species": record["species"],
                    "points": 0,
                    "races": 0,
                    "wins": 0,
                    "podiums": 0,
                }
            entry = stats[name]
            entry["points"] += pts
            entry["races"] += 1
            entry["wins"] += 1 if place == 0 else 0
            entry["podiums"] += 1 if place < 3 else 0
            # First-seen species wins; don't reassign on subsequent records.
    return stats


def _sorted_rows(stats: dict[str, dict]) -> list[tuple[str, dict]]:
    """Return (name, stat) pairs sorted by (-points, -wins, -podiums, name)."""
    return sorted(
        stats.items(),
        key=lambda item: (
            -item[1]["points"],
            -item[1]["wins"],
            -item[1]["podiums"],
            item[0],   # name ascending as final tiebreaker
        ),
    )


# --- Public read/query surface ---

def query(
    time_window: str,
    species_filter: str = "all",
    track_filter: str = "all",
    *,
    now: datetime | None = None,
) -> list[Row]:
    """Return ranked leaderboard rows for the given filters.

    Args:
        time_window: one of "all", "session", "today", "week", "month", "year".
        species_filter: "all", "turtles", or "snakes".
        track_filter: "all" or a specific track name; unknown names return [].
        now: injected datetime for test-time override (CONTEXT-1 Decision 4).
             Production callers omit this — it defaults to datetime.now().
    """
    _validate_window(time_window)
    if now is None:
        now = datetime.now()
    records = _races_for_window(time_window)
    filtered = [
        r for r in records
        if _in_window(r["ts"], time_window, now)
        and _species_matches(r["species"], species_filter)
        and (track_filter == "all" or r["track"] == track_filter)
    ]
    if not filtered:
        return []
    stats = _aggregate(filtered)
    sorted_pairs = _sorted_rows(stats)
    return [
        Row(
            rank=i + 1,
            racer_name=name,
            species=stat["species"],
            points=stat["points"],
            races=stat["races"],
            wins=stat["wins"],
            podiums=stat["podiums"],
        )
        for i, (name, stat) in enumerate(sorted_pairs)
    ]


def query_per_track(
    time_window: str,
    species_filter: str = "all",
    *,
    now: datetime | None = None,
) -> list[PerTrackRow]:
    """Return per-track ranked rows; rank resets to 1 within each track group.

    Track groups are returned in sorted(track) order (alphabetical ascending).

    Args:
        time_window: one of "all", "session", "today", "week", "month", "year".
        species_filter: "all", "turtles", or "snakes".
        now: injected datetime for test-time override (CONTEXT-1 Decision 4).
             Production callers omit this — it defaults to datetime.now().
    """
    _validate_window(time_window)
    if now is None:
        now = datetime.now()
    records = _races_for_window(time_window)
    filtered = [
        r for r in records
        if _in_window(r["ts"], time_window, now)
        and _species_matches(r["species"], species_filter)
    ]
    if not filtered:
        return []
    # Group records by track.
    by_track: dict[str, list[dict]] = {}
    for r in filtered:
        by_track.setdefault(r["track"], []).append(r)
    result: list[PerTrackRow] = []
    for track_name in sorted(by_track):
        group_stats = _aggregate(by_track[track_name])
        sorted_pairs = _sorted_rows(group_stats)
        for rank_within, (name, stat) in enumerate(sorted_pairs, start=1):
            result.append(
                PerTrackRow(
                    track=track_name,
                    rank=rank_within,
                    racer_name=name,
                    species=stat["species"],
                    points=stat["points"],
                    races=stat["races"],
                    wins=stat["wins"],
                    podiums=stat["podiums"],
                )
            )
    return result


def known_tracks() -> list[str]:
    """Return a sorted, deduplicated list of track names from race history.

    Sources: union of on-disk races and current-session races (CONTEXT-1 Decision 5).
    Set semantics deduplicate the overlap (session races appear in both sources
    because record_race writes to disk; the union is idempotent).
    Never imports tracks.py or constants.py — purely history-driven.
    """
    disk_tracks = {r["track"] for r in _load()["races"]}
    session_tracks = {r["track"] for r in _SESSION_RACES}
    return sorted(disk_tracks | session_tracks)


# --- Public reset surface ---

def reset_session() -> None:
    """Clear in-memory session races only; on-disk file is untouched.

    After this call:
    - query("session") returns []
    - query("all") still returns all historic records (disk unchanged)
    - known_tracks() may still include tracks from _load() (disk unchanged)
    """
    _SESSION_RACES.clear()


def reset_all() -> None:
    """Wipe both the in-memory session and the on-disk JSON file.

    Uses the same atomic write helper as record_race — no separate code path.
    After this call:
    - _SESSION_RACES is []
    - The file on disk exists and contains {"schema_version": 1, "races": []}
    - query("all") returns []
    - known_tracks() returns []
    """
    _SESSION_RACES.clear()
    _atomic_write_json(_empty_store(), _path())
