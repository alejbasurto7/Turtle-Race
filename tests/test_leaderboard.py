import json
import os
import subprocess
import sys

# Make project root importable when running pytest from any cwd.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime


# --- Shared fixture (also reused by Plan 2.2 tests) ---

@pytest.fixture
def lb(monkeypatch, tmp_path):
    """Fresh leaderboard module bound to tmp_path; session state cleared."""
    import leaderboard
    monkeypatch.setattr("paths.user_data_path",
                        lambda filename: str(tmp_path / filename))
    leaderboard._SESSION_RACES.clear()
    return leaderboard


# --- Persistence + record_race ---

def test_record_race_creates_file_on_first_call(lb, tmp_path):
    lb.record_race("turtles", "straight", ["A", "B", "C", "D"])

    json_file = tmp_path / "leaderboard.json"
    assert json_file.exists(), "leaderboard.json should be created on first record_race call"

    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert len(data["races"]) == 1

    race = data["races"][0]
    assert race["species"] == "turtles"
    assert race["track"] == "straight"
    assert race["finish_order"] == ["A", "B", "C", "D"]
    # Timestamp must be parseable as a naive ISO datetime (local time, no tz suffix)
    ts = datetime.fromisoformat(race["ts"])
    assert isinstance(ts, datetime)


def test_record_race_appends_to_existing_file(lb, tmp_path):
    lb.record_race("turtles", "straight", ["A", "B", "C", "D"])
    lb.record_race("snakes", "spiral", ["Shadow", "Anaconda", "Ralph"])

    data = json.loads((tmp_path / "leaderboard.json").read_text(encoding="utf-8"))
    assert len(data["races"]) == 2
    assert data["races"][0]["species"] == "turtles"
    assert data["races"][1]["species"] == "snakes"


def test_record_race_populates_session_list(lb):
    lb.record_race("turtles", "straight", ["A", "B", "C", "D"])
    lb.record_race("snakes", "rectangular", ["Ralph", "Shadow", "Anaconda"])

    assert len(lb._SESSION_RACES) == 2
    assert lb._SESSION_RACES[0]["species"] == "turtles"
    assert lb._SESSION_RACES[0]["track"] == "straight"
    assert lb._SESSION_RACES[0]["finish_order"] == ["A", "B", "C", "D"]
    assert lb._SESSION_RACES[1]["species"] == "snakes"
    assert lb._SESSION_RACES[1]["track"] == "rectangular"
    assert lb._SESSION_RACES[1]["finish_order"] == ["Ralph", "Shadow", "Anaconda"]


def test_record_race_truncates_for_three_racer_snake_race(lb, tmp_path):
    # Persistence layer must faithfully record the original finish_order length.
    # Scoring truncation to POINTS width happens in query() (Plan 2.2).
    lb.record_race("snakes", "straight", ["Shadow", "Ralph", "Anaconda"])

    data = json.loads((tmp_path / "leaderboard.json").read_text(encoding="utf-8"))
    assert len(data["races"]) == 1
    assert len(data["races"][0]["finish_order"]) == 3


def test_atomic_write_no_partial_file_on_crash(lb, tmp_path, monkeypatch):
    # Write a valid baseline race so the file exists.
    lb.record_race("turtles", "straight", ["A", "B", "C", "D"])

    # Poison os.replace so all subsequent atomic swaps fail.
    # The second record_race calls _load() (no os.replace needed — file is valid),
    # then _save() → _atomic_write_json() → os.replace(tmp, canonical): that's the
    # first call after we patch, and it must raise without corrupting the file.
    def failing_replace(src, dst):
        raise RuntimeError("boom")

    monkeypatch.setattr(os, "replace", failing_replace)

    with pytest.raises(RuntimeError, match="boom"):
        lb.record_race("snakes", "spiral", ["Shadow", "Ralph", "Anaconda"])

    # The canonical file must still reflect only the baseline race.
    # (The tmp file was created and then unlinked by the except branch in _atomic_write_json.)
    data = json.loads((tmp_path / "leaderboard.json").read_text(encoding="utf-8"))
    assert len(data["races"]) == 1
    assert data["races"][0]["species"] == "turtles"


def test_load_returns_empty_store_when_file_missing(lb, tmp_path):
    result = lb._load()
    assert result == {"schema_version": 1, "races": []}
    # _load() must NOT create the file as a side effect
    assert not (tmp_path / "leaderboard.json").exists()


def test_corrupt_file_quarantined_and_replaced(lb, tmp_path, capsys):
    # Write syntactically invalid JSON to the canonical path.
    (tmp_path / "leaderboard.json").write_text("{not valid json", encoding="utf-8")

    result = lb._load()

    # Returns an empty store — no exception propagated.
    assert result == {"schema_version": 1, "races": []}

    # The canonical file now exists and contains a fresh empty store.
    canonical = tmp_path / "leaderboard.json"
    assert canonical.exists()
    fresh = json.loads(canonical.read_text(encoding="utf-8"))
    assert fresh == {"schema_version": 1, "races": []}

    # A quarantine file was created alongside the canonical one.
    corrupt_files = list(tmp_path.glob("leaderboard.json.corrupt-*"))
    assert len(corrupt_files) == 1

    # Stderr warning contains the required phrases.
    err = capsys.readouterr().err
    assert "leaderboard: existing file unparseable" in err
    assert "quarantined to" in err


def test_corrupt_file_wrong_shape_is_quarantined(lb, tmp_path, capsys):
    # Write valid JSON but with missing 'races' key.
    (tmp_path / "leaderboard.json").write_text(
        json.dumps({"schema_version": 1}), encoding="utf-8"
    )

    result = lb._load()

    # Same recovery behavior as for unparseable JSON.
    assert result == {"schema_version": 1, "races": []}

    canonical = tmp_path / "leaderboard.json"
    assert canonical.exists()
    fresh = json.loads(canonical.read_text(encoding="utf-8"))
    assert fresh == {"schema_version": 1, "races": []}

    corrupt_files = list(tmp_path.glob("leaderboard.json.corrupt-*"))
    assert len(corrupt_files) == 1

    err = capsys.readouterr().err
    assert "leaderboard: existing file unparseable" in err
    assert "quarantined to" in err


def test_module_is_tk_free():
    """leaderboard must import successfully even when tkinter is poisoned."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    subprocess.check_call(
        [
            sys.executable,
            "-c",
            "import sys; sys.modules['tkinter'] = None; import leaderboard",
        ],
        cwd=project_root,
    )
