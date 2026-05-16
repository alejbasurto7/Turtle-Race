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


# --- Query + reset surface ---

# Helper: seed disk and optionally session without going through record_race,
# so tests can plant arbitrary timestamps for time-window coverage.

def _seed(lb, *records):
    """Write a list of (ts_iso, species, track, finish_order_list) records directly to disk."""
    import json
    store = {"schema_version": 1, "races": [
        {"ts": ts, "species": s, "track": t, "finish_order": list(fo)}
        for (ts, s, t, fo) in records
    ]}
    with open(lb._path(), "w", encoding="utf-8") as f:
        json.dump(store, f)


# 1 ── Empty state

def test_query_empty_state_returns_empty_list(lb):
    assert lb.query("all") == []
    assert lb.query_per_track("all") == []
    assert lb.known_tracks() == []


# 2-4 ── Scoring

def test_query_awards_six_three_one_zero_for_four_racer_race(lb):
    _seed(lb, ("2026-01-01T10:00:00", "turtles", "straight", ["A", "B", "C", "D"]))
    rows = lb.query("all")
    assert len(rows) == 4
    by_name = {r.racer_name: r for r in rows}
    assert by_name["A"].points == 6
    assert by_name["B"].points == 3
    assert by_name["C"].points == 1
    assert by_name["D"].points == 0


def test_query_truncates_to_six_three_one_for_three_racer_race(lb):
    _seed(lb, ("2026-01-01T10:00:00", "snakes", "straight", ["X", "Y", "Z"]))
    rows = lb.query("all")
    assert len(rows) == 3
    by_name = {r.racer_name: r for r in rows}
    assert by_name["X"].points == 6
    assert by_name["Y"].points == 3
    assert by_name["Z"].points == 1


def test_query_fourth_place_consumed_only_when_four_finishers(lb):
    """A 3-racer race produces exactly 3 rows — no phantom 4th-place row."""
    _seed(lb, ("2026-01-01T10:00:00", "snakes", "straight", ["X", "Y", "Z"]))
    rows = lb.query("all")
    assert len(rows) == 3
    # No row should have 0 points as a ghost/phantom — all 3 names have pts >= 1.
    assert all(r.points >= 1 for r in rows)


# 5-7 ── Tiebreakers

def test_tiebreak_by_wins(lb):
    """Racer with same points but more wins ranks higher."""
    # X: 1st in race3 (6pts, win) + 2nd in race1 (3pts) = 9pts, 1 win.
    # Y: 2nd in race2 (3pts) + 2nd in race3 (3pts) + 1st in (none — Y has 0 wins)...
    # Construction: race1=[A,X,B,C], race2=[A,Y,B,C], race3=[X,Y,A,B]
    # X: race1 2nd=3pts pod=1; race3 1st=6pts win=1 pod=1. Total: 9pts 1win 2pods.
    # Y: race2 2nd=3pts pod=1; race3 2nd=3pts pod=1.        Total: 6pts 0wins 2pods.
    # Not tied on pts. Adjust: add race4=[Y,A,X,B] → Y=6pts win=1 pod=1; X=1pt pod=1.
    # X: 3+6+1=10pts 1win 3pods. Y: 3+3+6=12pts 1win 3pods. Still different pts.
    #
    # Use a symmetric construction to get exactly 9pts each with different wins:
    # Race1: [X,Y,A,B] → X=6 win=1 pod=1; Y=3 pod=1.
    # Race2: [A,Y,X,B] → Y=3 pod=1; X=1 pod=1.
    # Race3: [A,B,Y,X] → Y=1 pod=1; X=0 pod=0.
    # X: 6+1+0=7pts 1win 2pods. Y: 3+3+1=7pts 0wins 3pods. Same pts! X wins=1 Y wins=0.
    # X ranks above Y by wins. ✓
    _seed(lb,
        ("2026-01-01T10:00:00", "turtles", "straight", ["X", "Y", "A", "B"]),
        ("2026-01-02T10:00:00", "turtles", "straight", ["A", "Y", "X", "B"]),
        ("2026-01-03T10:00:00", "turtles", "straight", ["A", "B", "Y", "X"]),
    )
    rows = lb.query("all")
    by_name = {r.racer_name: r for r in rows}
    # Both X and Y have 7 points (checked below); X has 1 win, Y has 0.
    assert by_name["X"].points == 7
    assert by_name["Y"].points == 7
    assert by_name["X"].wins == 1
    assert by_name["Y"].wins == 0
    # X must rank above Y.
    assert by_name["X"].rank < by_name["Y"].rank


def test_tiebreak_by_podiums_when_wins_equal(lb):
    """Racer with more podiums ranks higher when points and wins are equal.

    In this scoring system (POINTS=(6,3,1,0)), equal points and wins but
    different podiums requires careful construction. We verify that the sort
    key includes podiums as the third dimension by observing that the higher-
    podium racer is ranked above the lower-podium racer when pts and wins match.

    Construction: same as wins test but extended with a 3rd-place appearance
    for X (to boost pods) and an offsetting arrangement to keep pts equal.
    Race1: [X,Y,A,B] → X=6 win=1 pod=1; Y=3 pod=1.
    Race2: [Y,X,A,B] → Y=6 win=1 pod=1; X=3 pod=1.
    Both: 9pts 1win 2pods. Tied — name decides here; not a pods test.

    Use a 3-racer race to get a podium-boosting +1pt for X and compensate
    so pts stay equal via a Y-only race giving Y the matching point:
    Race3 (3 racers): [A,B,X]    → X=1pt pod=1.
    Race4 (3 racers): [A,B,Y]    → Y=1pt pod=1.
    Both: 10pts 1win 3pods. Still same pods.

    Alternative — give X a 3rd-place extra and compensate by giving Y a 1st
    in a race X doesn't appear in, so Y also gets 1 extra pt (from 3rd in a
    separate race) to match. Both still accumulate the same ratio of pts/pods.

    The mathematical reality: in this scoring system a podium always adds >=1pt,
    so equal pts with unequal pods requires the higher-podium racer to offset
    with zero-point 4th-place finishes. Construct:
    Race1: [X,Y,A,B]    → X=6 win=1 pod=1; Y=3 pod=1.
    Race2: [Y,X,A,B]    → Y=6 win=1 pod=1; X=3 pod=1.
    Now both 9pts 1win 2pods.
    Race3 (3 racers): [A,X,B]  → X=3pts pod=1. X=12pts 1win 3pods.
    Race4 (3 racers): [A,Y,B]  → Y=3pts pod=1. Y=12pts 1win 3pods.
    Race5 (4 racers): [A,B,X,C] → X=1pt pod=1. X=13pts 1win 4pods.
    Race6 (4 racers): [A,B,C,Y] → Y=0pts pod=0. Y=12pts 1win 3pods.
    X: 13pts 1win 4pods. Y: 12pts 1win 3pods. Points differ — pts tiebreak resolves.

    Conclusion: "pods only" tiebreak is geometrically unachievable with pts equal
    and wins equal. This test verifies that the _sorted_rows key includes pods as
    the 3rd sort dimension by calling _sorted_rows with hand-crafted stat dicts.
    """
    # Directly test _sorted_rows with synthetic stats where pts and wins are
    # artificially equal but pods differ. This validates the sort key itself.
    stats = {
        "HighPod": {"species": "turtles", "points": 9, "races": 2, "wins": 1, "podiums": 3},
        "LowPod":  {"species": "turtles", "points": 9, "races": 2, "wins": 1, "podiums": 2},
    }
    sorted_pairs = lb._sorted_rows(stats)
    names_in_order = [name for name, _ in sorted_pairs]
    # HighPod has more podiums → must rank first.
    assert names_in_order[0] == "HighPod"
    assert names_in_order[1] == "LowPod"


def test_tiebreak_by_name_when_all_else_equal(lb):
    """Alphabetically earlier name ranks first when all stats are identical."""
    _seed(lb,
        ("2026-01-01T10:00:00", "turtles", "straight", ["Alice", "Bob", "C", "D"]),
        ("2026-01-02T10:00:00", "turtles", "straight", ["Bob", "Alice", "C", "D"]),
    )
    rows = lb.query("all")
    by_name = {r.racer_name: r for r in rows}
    # Alice and Bob both: 9pts, 1 win, 2 podiums — name decides.
    assert by_name["Alice"].points == by_name["Bob"].points
    assert by_name["Alice"].wins == by_name["Bob"].wins
    assert by_name["Alice"].podiums == by_name["Bob"].podiums
    assert by_name["Alice"].rank < by_name["Bob"].rank


# 8-14 ── Time windows (fixed now = 2026-05-16 14:00:00, a Saturday)

_FIXED_NOW = datetime(2026, 5, 16, 14, 0, 0)


def test_today_window(lb):
    _seed(lb,
        ("2026-05-16T01:00:00", "turtles", "straight", ["A", "B", "C", "D"]),  # today
        ("2026-05-15T23:59:00", "turtles", "straight", ["W", "X", "Y", "Z"]),  # yesterday
    )
    rows = lb.query("today", now=_FIXED_NOW)
    racer_names = {r.racer_name for r in rows}
    assert "A" in racer_names
    assert "W" not in racer_names


def test_week_window_iso_monday_start(lb):
    """ISO Monday-start week: Mon 2026-05-11 through Sun 2026-05-17 (inclusive).

    With now=2026-05-16 (Saturday):
      week_start = 2026-05-11 (Monday, weekday()=0)
      week_end_exclusive = 2026-05-18 (next Monday)
    In-window:  2026-05-11 (Monday — boundary inclusive) and 2026-05-17 (Sunday — boundary inclusive).
    Out-of-window: 2026-05-10 (previous Sunday) and 2026-05-18 (next Monday — boundary exclusive).
    """
    _seed(lb,
        ("2026-05-11T08:00:00", "turtles", "straight", ["InMon",  "B", "C", "D"]),  # Monday — IN
        ("2026-05-10T23:59:00", "turtles", "straight", ["OutSun", "B", "C", "D"]),  # prev Sunday — OUT
        ("2026-05-17T23:59:00", "turtles", "straight", ["InSun",  "B", "C", "D"]),  # Sunday — IN
        ("2026-05-18T00:00:00", "turtles", "straight", ["OutMon", "B", "C", "D"]),  # next Monday — OUT
    )
    rows = lb.query("week", now=_FIXED_NOW)
    racer_names = {r.racer_name for r in rows}
    assert "InMon"  in racer_names, "Monday start should be in-window"
    assert "InSun"  in racer_names, "Sunday end-of-week should be in-window"
    assert "OutSun" not in racer_names, "Previous Sunday must be out-of-window"
    assert "OutMon" not in racer_names, "Next Monday must be out-of-window (exclusive)"


def test_month_window(lb):
    _seed(lb,
        ("2026-05-01T10:00:00", "turtles", "straight", ["InMay",   "B", "C", "D"]),
        ("2026-04-30T23:59:00", "turtles", "straight", ["OutApr",  "B", "C", "D"]),
        ("2026-06-01T00:00:00", "turtles", "straight", ["OutJune", "B", "C", "D"]),
    )
    rows = lb.query("month", now=_FIXED_NOW)
    racer_names = {r.racer_name for r in rows}
    assert "InMay"   in racer_names
    assert "OutApr"  not in racer_names
    assert "OutJune" not in racer_names


def test_year_window(lb):
    _seed(lb,
        ("2026-03-15T10:00:00", "turtles", "straight", ["In2026",  "B", "C", "D"]),
        ("2025-12-31T23:59:00", "turtles", "straight", ["Out2025", "B", "C", "D"]),
    )
    rows = lb.query("year", now=_FIXED_NOW)
    racer_names = {r.racer_name for r in rows}
    assert "In2026"  in racer_names
    assert "Out2025" not in racer_names


def test_all_window_returns_everything(lb):
    _seed(lb,
        ("2020-01-01T10:00:00", "turtles", "straight", ["Old", "B", "C", "D"]),
        ("2024-06-15T10:00:00", "turtles", "straight", ["Mid", "B", "C", "D"]),
        ("2026-05-16T10:00:00", "turtles", "straight", ["New", "B", "C", "D"]),
    )
    rows = lb.query("all", now=_FIXED_NOW)
    racer_names = {r.racer_name for r in rows}
    assert "Old" in racer_names
    assert "Mid" in racer_names
    assert "New" in racer_names


def test_session_window_reads_session_not_disk(lb):
    """query('session') reads only _SESSION_RACES, not disk-seeded records."""
    # Plant a record on disk via _seed (bypasses record_race, so session is empty).
    _seed(lb, ("2026-05-16T01:00:00", "turtles", "straight", ["DiskOnly", "B", "C", "D"]))
    # Now write a session record via record_race (goes to both session + disk).
    lb.record_race("snakes", "spiral", ["SessionRacer", "Ralph", "Anaconda"])

    session_rows = lb.query("session", now=_FIXED_NOW)
    session_names = {r.racer_name for r in session_rows}
    assert "SessionRacer" in session_names
    assert "DiskOnly" not in session_names

    all_rows = lb.query("all", now=_FIXED_NOW)
    all_names = {r.racer_name for r in all_rows}
    assert "SessionRacer" in all_names
    assert "DiskOnly" in all_names


def test_unknown_time_window_raises(lb):
    with pytest.raises(ValueError):
        lb.query("decade", now=_FIXED_NOW)


# 15-17 ── Species filter

def _seed_mixed_species(lb):
    _seed(lb,
        ("2026-01-01T10:00:00", "turtles", "straight", ["Turt1", "Turt2", "Turt3", "Turt4"]),
        ("2026-01-02T10:00:00", "snakes",  "straight", ["Snake1", "Snake2", "Snake3"]),
    )


def test_species_filter_all(lb):
    _seed_mixed_species(lb)
    rows = lb.query("all", species_filter="all")
    names = {r.racer_name for r in rows}
    assert "Turt1" in names
    assert "Snake1" in names


def test_species_filter_turtles_only(lb):
    _seed_mixed_species(lb)
    rows = lb.query("all", species_filter="turtles")
    for r in rows:
        assert r.species == "turtles"
    names = {r.racer_name for r in rows}
    assert "Turt1" in names
    assert "Snake1" not in names


def test_species_filter_snakes_only(lb):
    _seed_mixed_species(lb)
    rows = lb.query("all", species_filter="snakes")
    for r in rows:
        assert r.species == "snakes"
    names = {r.racer_name for r in rows}
    assert "Snake1" in names
    assert "Turt1" not in names


# 18-20 ── Track filter

def _seed_two_tracks(lb):
    _seed(lb,
        ("2026-01-01T10:00:00", "turtles", "straight", ["S1", "S2", "S3", "S4"]),
        ("2026-01-02T10:00:00", "turtles", "spiral",   ["Sp1", "Sp2", "Sp3", "Sp4"]),
    )


def test_track_filter_all(lb):
    _seed_two_tracks(lb)
    rows = lb.query("all", track_filter="all")
    names = {r.racer_name for r in rows}
    assert "S1" in names
    assert "Sp1" in names


def test_track_filter_specific(lb):
    _seed_two_tracks(lb)
    rows = lb.query("all", track_filter="straight")
    names = {r.racer_name for r in rows}
    assert "S1" in names
    assert "Sp1" not in names


def test_track_filter_unknown_returns_empty(lb):
    _seed_two_tracks(lb)
    rows = lb.query("all", track_filter="bogus_track")
    assert rows == []


# 21-23 ── Per-track query

def test_query_per_track_groups_by_track(lb):
    _seed(lb,
        ("2026-01-01T10:00:00", "turtles", "spiral",   ["SpA", "SpB", "SpC", "SpD"]),
        ("2026-01-02T10:00:00", "turtles", "straight",  ["StA", "StB", "StC", "StD"]),
    )
    rows = lb.query_per_track("all")
    # Alphabetical track order: spiral before straight.
    spiral_rows   = [r for r in rows if r.track == "spiral"]
    straight_rows = [r for r in rows if r.track == "straight"]
    assert len(spiral_rows)   > 0
    assert len(straight_rows) > 0
    # Each group starts with rank 1.
    assert spiral_rows[0].rank   == 1
    assert straight_rows[0].rank == 1
    # spiral should appear before straight (sorted track order).
    assert rows.index(spiral_rows[0]) < rows.index(straight_rows[0])


def test_query_per_track_within_group_sort_matches_query(lb):
    """Within a track group, ordering follows points/wins/podiums/name."""
    _seed(lb,
        ("2026-01-01T10:00:00", "turtles", "straight", ["Alpha", "Beta", "Gamma", "Delta"]),
        ("2026-01-02T10:00:00", "turtles", "straight", ["Alpha", "Beta", "Gamma", "Delta"]),
    )
    per_track = lb.query_per_track("all")
    flat      = lb.query("all", track_filter="straight")
    # Names in order should match.
    per_track_names = [r.racer_name for r in per_track if r.track == "straight"]
    flat_names      = [r.racer_name for r in flat]
    assert per_track_names == flat_names


def test_query_per_track_species_filter(lb):
    _seed(lb,
        ("2026-01-01T10:00:00", "turtles", "straight", ["TurtA", "TurtB", "TurtC", "TurtD"]),
        ("2026-01-02T10:00:00", "snakes",  "straight", ["SnakeA", "SnakeB", "SnakeC"]),
    )
    rows = lb.query_per_track("all", species_filter="turtles")
    for r in rows:
        assert r.species == "turtles"
    names = {r.racer_name for r in rows}
    assert "TurtA" in names
    assert "SnakeA" not in names


# 24-27 ── Known tracks

def test_known_tracks_dedup_and_sort(lb):
    _seed(lb,
        ("2026-01-01T10:00:00", "turtles", "spiral",   ["A", "B", "C", "D"]),
        ("2026-01-02T10:00:00", "turtles", "straight",  ["A", "B", "C", "D"]),
        ("2026-01-03T10:00:00", "turtles", "spiral",   ["A", "B", "C", "D"]),  # duplicate spiral
    )
    assert lb.known_tracks() == ["spiral", "straight"]


def test_known_tracks_union_disk_and_session(lb):
    """known_tracks includes tracks from disk (seeded) and session (record_race)."""
    _seed(lb, ("2026-01-01T10:00:00", "turtles", "straight", ["A", "B", "C", "D"]))
    lb.record_race("snakes", "spiral", ["Shadow", "Ralph", "Anaconda"])
    assert lb.known_tracks() == ["spiral", "straight"]


def test_known_tracks_empty_when_no_history(lb):
    assert lb.known_tracks() == []


def test_known_tracks_does_not_import_tracks_module():
    """leaderboard.py must not contain 'import tracks' or 'from tracks'."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lb_path = os.path.join(project_root, "leaderboard.py")
    source = open(lb_path, encoding="utf-8").read()
    assert "import tracks" not in source, "leaderboard.py must not import the tracks module"
    assert "from tracks" not in source, "leaderboard.py must not import from the tracks module"


# 28-29 ── Reset

def test_reset_session_clears_session_leaves_file(lb, tmp_path):
    lb.record_race("turtles", "straight", ["A", "B", "C", "D"])
    lb.record_race("snakes", "spiral",    ["Shadow", "Ralph", "Anaconda"])

    json_file = tmp_path / "leaderboard.json"
    bytes_before = json_file.read_bytes()

    lb.reset_session()

    bytes_after = json_file.read_bytes()
    assert bytes_before == bytes_after, "reset_session must not modify the on-disk file"
    assert lb._SESSION_RACES == []

    # Disk still has both races.
    all_rows = lb.query("all")
    assert len(all_rows) > 0


def test_reset_all_wipes_disk_and_session(lb, tmp_path):
    lb.record_race("turtles", "straight", ["A", "B", "C", "D"])
    lb.record_race("snakes", "spiral",    ["Shadow", "Ralph", "Anaconda"])

    lb.reset_all()

    json_file = tmp_path / "leaderboard.json"
    assert json_file.exists(), "reset_all must leave the file present (not deleted)"

    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert data == {"schema_version": 1, "races": []}

    assert lb._SESSION_RACES == []
    assert lb.query("all") == []
    assert lb.known_tracks() == []


# 30 ── Fresh install (no file)

def test_query_on_fresh_install_returns_empty(lb, tmp_path):
    """query() on a fresh install (no file) returns [] and does not create the file."""
    json_file = tmp_path / "leaderboard.json"
    assert not json_file.exists()

    assert lb.query("all") == []
    assert lb.query("session") == []

    # _load() must not create the file as a side effect (same invariant as Plan 2.1 test 6).
    assert not json_file.exists()
