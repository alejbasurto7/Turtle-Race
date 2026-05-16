import json
import os
import sys
import tempfile
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
