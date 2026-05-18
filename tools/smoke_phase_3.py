"""No-GUI-interaction smoke test for Phase 3 main-menu / round-loop restructure.

Exercises the new outer-menu / inner-race-rounds two-level loop by monkeypatching
both the existing race-dialog surface (`get_user_track / get_user_species /
get_user_bet`) and the three new Phase 3 dialogs (`get_main_menu_choice /
ask_play_again_choice / show_leaderboard_placeholder`), redirecting %APPDATA% to
a tempdir, and running `main.main()`.

Flow exercised:
    menu→race → round 1 (turtle) → again
              → round 2 (snake)   → menu
    menu→leaderboard (placeholder no-op, returns to menu)
    menu→race → round 3 (turtle)  → quit

Expected: 3 race records on disk; the quit path exits main() cleanly so
audio.stop_background_music() and screen.bye() both run.

Run from the project root:

    python tools/smoke_phase_3.py

Exits 0 on success, non-zero if the on-disk JSON doesn't match expectations.

This is a Phase 3 verification artifact (Plan 2.1 Task 2 substitute). It is NOT
part of pytest — it requires a display (the turtle Screen) and intentionally
exercises the live wiring through main().

NOTE: tools/smoke_phase_2.py is now broken by design (it monkeypatches the
deleted dialogs.ask_play_again). That is documented in CONTEXT-3.md Carryover.
"""

import json
import os
import sys
import tempfile


def main():
    # Redirect %APPDATA% BEFORE any import that resolves paths.user_data_path.
    tmpdir = tempfile.mkdtemp(prefix="reptilerace_phase3_smoke_")
    os.environ["APPDATA"] = tmpdir
    print(f"[smoke] redirected %APPDATA% to {tmpdir}")

    # Make project root importable.
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Import the dialog and audio modules first so we can monkeypatch them
    # before main.main() walks the new flow.
    import dialogs
    import audio

    # ---- canned plans ----
    # Outer menu choices, in execution order. The flow is:
    #   menu → race  (enters inner loop)
    #     round 1 → "again"  (stays in inner loop)
    #     round 2 → "menu"   (exits inner loop)
    #   menu → leaderboard   (placeholder no-op; returns to menu)
    #   menu → race  (enters inner loop)
    #     round 3 → "quit"   (exits both loops)
    menu_choices = iter(["race", "leaderboard", "race", "quit"])

    # Inner race-rounds: 3 rounds total. Each round needs (track, species, bet).
    rounds = [
        {"track": "straight",   "species": "turtles", "bet": 1},
        {"track": "spiral",     "species": "snakes",  "bet": 2},
        {"track": "rectangular","species": "turtles", "bet": 3},
    ]

    # Post-race choices, in order of races completed: again, menu, quit.
    post_race_choices = iter(["again", "menu", "quit"])

    # Per-round index, advanced at the start of each race body (first dialog called).
    round_idx = 0

    # Verification counters for branches the smoke claims to exercise.
    leaderboard_placeholder_calls = 0

    def fake_get_main_menu_choice():
        return next(menu_choices)

    def fake_show_leaderboard_placeholder():
        # No-op stub for the smoke; the real placeholder just opens a Toplevel
        # the user dismisses. We just return control to the menu loop.
        nonlocal leaderboard_placeholder_calls
        leaderboard_placeholder_calls += 1
        return None

    def fake_get_user_track():
        nonlocal round_idx
        round_idx += 1
        return rounds[round_idx - 1]["track"]

    def fake_get_user_species():
        return rounds[round_idx - 1]["species"]

    def fake_get_user_bet(species):
        return rounds[round_idx - 1]["bet"]

    def fake_ask_play_again_choice():
        return next(post_race_choices)

    dialogs.get_main_menu_choice         = fake_get_main_menu_choice
    dialogs.show_leaderboard_placeholder = fake_show_leaderboard_placeholder
    dialogs.get_user_track               = fake_get_user_track
    dialogs.get_user_species             = fake_get_user_species
    dialogs.get_user_bet                 = fake_get_user_bet
    dialogs.ask_play_again_choice        = fake_ask_play_again_choice

    # Silence background music.
    audio.start_background_music = lambda: None
    audio.stop_background_music  = lambda: None

    print(f"[smoke] running main() — expect {len(rounds)} rounds across the menu flow...")
    import main
    main.main()
    print(f"[smoke] main() returned cleanly (audio.stop + screen.bye both ran)")

    # ---- verify on-disk JSON ----
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

    # Timestamps should be non-decreasing.
    timestamps = [r["ts"] for r in data.get("races", [])]
    if timestamps != sorted(timestamps):
        errors.append(f"ts values not in chronological order: {timestamps}")

    # Each race matches the planned round.
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

    # Leaderboard placeholder must have been invoked exactly once during the flow.
    if leaderboard_placeholder_calls != 1:
        errors.append(
            f"expected show_leaderboard_placeholder to be called exactly 1 time, "
            f"got {leaderboard_placeholder_calls} — the menu→leaderboard branch was not exercised"
        )

    if errors:
        print("\n[smoke] FAIL — verification errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"\n[smoke] PASS — {len(rounds)} races recorded with expected schema, species, track, and finish_order length")
    print(f"[smoke] menu→leaderboard→menu transition executed cleanly ({leaderboard_placeholder_calls} placeholder call, no extra races recorded)")
    print(f"[smoke] (tmpdir was {tmpdir}; leaderboard.json remains there for inspection)")


if __name__ == "__main__":
    main()
