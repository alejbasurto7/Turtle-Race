"""No-GUI-interaction smoke test for Phase 2 wiring of record_race.

Exercises the FULL main() round loop three times — at least one turtle race
and at least one snake race — by monkeypatching dialogs.* to return canned
answers and audio.start_background_music to a no-op. Redirects %APPDATA% to
a tempdir so the test never touches the user's real per-user app-data dir.

The Tk window will open and animate three races; no keyboard or mouse input
required. Run from the project root:

    python tools/smoke_phase_2.py

Exits 0 on success, non-zero if the on-disk JSON doesn't match expectations.

This is a Phase 2 Task 3 substitute. It is NOT part of pytest — it requires
a display (the turtle Screen) and intentionally exercises the live wiring
rather than the unit-test-mocked surface.
"""

import json
import os
import sys
import tempfile


def main():
    # Redirect %APPDATA% so the smoke run cannot pollute the real per-user
    # data dir. Must happen BEFORE any import that resolves paths.user_data_path.
    tmpdir = tempfile.mkdtemp(prefix="turtlerace_smoke_")
    os.environ["APPDATA"] = tmpdir
    print(f"[smoke] redirected %APPDATA% to {tmpdir}")

    # Make project root importable.
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Import dialogs first so we can monkeypatch BEFORE main imports it.
    # (Module-import is sticky — Python caches dialogs in sys.modules.)
    import dialogs
    import audio

    # Canned plan: 3 rounds, mixing species + tracks.
    rounds = [
        {"track": "straight",   "species": "turtles", "bet": 1},
        {"track": "spiral",     "species": "snakes",  "bet": 2},
        {"track": "rectangular","species": "turtles", "bet": 3},
    ]
    # Advance round_idx at the start of each round (in get_user_track, the first
    # dialog called) so the index is decoupled from where ask_play_again sits in
    # the round body. Survives a Phase 3+ reorder of main()'s round-loop calls.
    round_idx = 0

    def fake_get_user_track():
        nonlocal round_idx
        round_idx += 1
        return rounds[round_idx - 1]["track"]

    def fake_get_user_species():
        return rounds[round_idx - 1]["species"]

    def fake_get_user_bet(species):
        return rounds[round_idx - 1]["bet"]

    def fake_ask_play_again():
        return round_idx < len(rounds)

    dialogs.get_user_track = fake_get_user_track
    dialogs.get_user_species = fake_get_user_species
    dialogs.get_user_bet = fake_get_user_bet
    dialogs.ask_play_again = fake_ask_play_again

    # Silence background music for the smoke run.
    audio.start_background_music = lambda: None
    audio.stop_background_music = lambda: None

    print(f"[smoke] running main() for {len(rounds)} rounds...")
    import main
    main.main()
    print(f"[smoke] main() returned")

    # Verify the on-disk JSON.
    import paths
    data_path = paths.user_data_path("leaderboard.json")
    print(f"[smoke] inspecting {data_path}")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[smoke] schema_version = {data.get('schema_version')!r}")
    print(f"[smoke] races count    = {len(data.get('races', []))}")
    for i, r in enumerate(data.get("races", [])):
        print(f"[smoke]   race {i+1}: ts={r['ts']!r} species={r['species']!r} "
              f"track={r['track']!r} finish_order={r['finish_order']!r}")

    errors = []
    if data.get("schema_version") != 1:
        errors.append(f"expected schema_version=1, got {data.get('schema_version')!r}")
    if len(data.get("races", [])) != len(rounds):
        errors.append(f"expected {len(rounds)} race records, got {len(data.get('races', []))}")

    # Timestamps should be non-decreasing across the recorded races.
    timestamps = [r["ts"] for r in data.get("races", [])]
    if timestamps != sorted(timestamps):
        errors.append(f"ts values not in chronological order: {timestamps}")

    # Check each race matches the planned round.
    for i, (planned, recorded) in enumerate(zip(rounds, data.get("races", []))):
        if recorded["species"] != planned["species"]:
            errors.append(f"race {i+1}: species {recorded['species']!r} != planned {planned['species']!r}")
        if recorded["track"] != planned["track"]:
            errors.append(f"race {i+1}: track {recorded['track']!r} != planned {planned['track']!r}")
        expected_len = 4 if planned["species"] == "turtles" else 3
        if len(recorded["finish_order"]) != expected_len:
            errors.append(
                f"race {i+1}: finish_order has {len(recorded['finish_order'])} entries, "
                f"expected {expected_len} for {planned['species']}"
            )

    if errors:
        print("\n[smoke] FAIL — verification errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"\n[smoke] PASS — all {len(rounds)} races recorded with expected schema, species, track, and finish_order length")
    print(f"[smoke] (tmpdir was {tmpdir}; leaderboard.json remains there for inspection)")


if __name__ == "__main__":
    main()
