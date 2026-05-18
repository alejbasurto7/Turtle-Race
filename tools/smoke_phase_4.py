"""No-GUI-interaction smoke test for Phase 4 leaderboard view.

Exercises the renamed dialogs.show_leaderboard() by replacing it with a
programmatic driver that calls the Phase 1 leaderboard API directly — Group-by
reshape, Track-filter disable/enable logic, both reset paths, and empty-state
precondition — without ever opening a Tk Toplevel.

Mirrors the structure of tools/smoke_phase_3.py:
  - %APPDATA% redirect before any paths/leaderboard import
  - monkeypatch surface covering every dialog callable
  - iter() pattern for menu and post-race choices
  - main.main() invocation

Flow exercised:
    menu→race:
        round 1: turtles / straight   / bet=1 → "again"
        round 2: snakes  / spiral     / bet=2 → "again"
        round 3: turtles / rectangular / bet=3 → "menu"
    menu→leaderboard (fake_show_leaderboard drives API contract)
    menu→quit

Expected final state: on-disk JSON is {"schema_version": 1, "races": []}
(Reset All in the driver wiped it).

Run from the project root:

    python tools/smoke_phase_4.py

Exits 0 on success, non-zero with a diagnostic message on any verification
failure.

This is a Phase 4 verification artifact (Plan 2.1). It is NOT part of pytest —
it lives under tools/, not tests/, so pytest does not collect it.

NOTE: tools/smoke_phase_3.py is the Phase 3 historical artifact and remains
untouched per CONTEXT-4 Carryover. Its monkeypatch of
dialogs.show_leaderboard_placeholder is broken-by-design after Plan 1.1 renamed
that function — exactly as tools/smoke_phase_2.py was broken by Phase 3.
"""

import json
import os
import sys
import tempfile


def main():
    # ---- env redirect BEFORE any paths/leaderboard import ----
    tmpdir = tempfile.mkdtemp(prefix="reptilerace_phase4_smoke_")
    os.environ["APPDATA"] = tmpdir
    print(f"[smoke] redirected %APPDATA% to {tmpdir}")

    # Make project root importable.
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Import the modules we need to monkeypatch BEFORE main.main() is called.
    import dialogs
    import audio

    # ---- canned plans ----
    # Outer menu choices, in execution order. The flow is:
    #   menu → race  (enters inner round loop)
    #     round 1 → "again"  (stays in inner loop)
    #     round 2 → "again"  (stays in inner loop)
    #     round 3 → "menu"   (exits inner loop)
    #   menu → leaderboard   (fake driver runs; returns to menu)
    #   menu → quit          (outer loop exits)
    menu_choices = iter(["race", "leaderboard", "quit"])

    # 3 rounds: turtles/straight, snakes/spiral, turtles/rectangular.
    rounds = [
        {"track": "straight",    "species": "turtles", "bet": 1},
        {"track": "spiral",      "species": "snakes",  "bet": 2},
        {"track": "rectangular", "species": "turtles", "bet": 3},
    ]

    # Post-race choices: stay in the round loop for rounds 1+2, exit for round 3.
    post_race_choices = iter(["again", "again", "menu"])

    # Per-round index, advanced at the start of each race body (first dialog called).
    round_idx = 0

    # Verification counter for the leaderboard branch.
    show_leaderboard_calls = 0

    def fake_get_main_menu_choice():
        return next(menu_choices)

    def fake_show_leaderboard():
        """Programmatic driver for the Phase 4 leaderboard contract.

        Replaces the real dialogs.show_leaderboard() Toplevel so the smoke
        can run without an interactive display. Exercises every hard-constraint
        behavior from CONTEXT-4: Group-by reshape, Track-filter disable/enable
        rationale, both reset paths, and empty-state precondition.

        Calls the real leaderboard Phase 1 API — query / query_per_track /
        known_tracks / reset_session / reset_all — with the same argument
        values the GUI uses, translated via dialogs._FILTER_LABEL_TO_KEY.
        """
        nonlocal show_leaderboard_calls
        show_leaderboard_calls += 1
        print("[smoke] entering fake_show_leaderboard — driving Phase 1 API contract")

        # Import from sys.modules (already loaded by record_race calls above).
        import leaderboard

        # Verify the translation dict the GUI relies on exists and has expected keys.
        _label_to_key = dialogs._FILTER_LABEL_TO_KEY
        print(
            f"[smoke] _FILTER_LABEL_TO_KEY has {len(_label_to_key)} entries: "
            f"{list(_label_to_key.keys())}"
        )
        expected_label_keys = {
            "All Time", "Current Session", "Today",
            "This Week", "This Month", "This Year",
            "All", "Turtles", "Snakes",
            "None", "Track",
        }
        missing = expected_label_keys - set(_label_to_key.keys())
        if missing:
            print(f"[smoke] FAIL — _FILTER_LABEL_TO_KEY is missing expected keys: {missing}")
            sys.exit(1)

        errors = []

        # ------------------------------------------------------------------
        # Step 1: Initial state — Time="All Time", Species="All", Track="All"
        #         Group by="None" → leaderboard.query("all", "all", "all")
        # ------------------------------------------------------------------
        print("[smoke] Step 1: query(all, all, all)")
        rows = leaderboard.query("all", "all", "all")
        print(f"[smoke]   -> {len(rows)} rows")
        if len(rows) < 6:
            errors.append(
                f"Step 1: expected >= 6 rows for 3 mixed-species races, got {len(rows)}"
            )

        # ------------------------------------------------------------------
        # Step 2: Change Time to "Current Session"
        #         GUI maps "Current Session" -> "session" via _FILTER_LABEL_TO_KEY
        # ------------------------------------------------------------------
        print("[smoke] Step 2: query(session, all, all)")
        rows = leaderboard.query("session", "all", "all")
        print(f"[smoke]   -> {len(rows)} rows")
        if len(rows) < 6:
            errors.append(
                f"Step 2: expected >= 6 session rows for 3 in-process races, got {len(rows)}"
            )

        # ------------------------------------------------------------------
        # Step 3: Change Group by to "Track" → Track combobox auto-disables.
        #         GUI calls query_per_track(time, species) — no track arg.
        # ------------------------------------------------------------------
        print("[smoke] Step 3: query_per_track(all, all) — Group by=Track")
        per_track_rows = leaderboard.query_per_track("all", "all")
        tracks_in_result = {r.track for r in per_track_rows}
        print(f"[smoke]   -> {len(per_track_rows)} per-track rows across tracks: {tracks_in_result}")
        for expected_track in ("straight", "spiral", "rectangular"):
            if expected_track not in tracks_in_result:
                errors.append(
                    f"Step 3: expected track {expected_track!r} in per-track result, "
                    f"got {tracks_in_result}"
                )
        # Rank must restart at 1 within each track group.
        for t_name in tracks_in_result:
            group = [r for r in per_track_rows if r.track == t_name]
            min_rank = min(r.rank for r in group)
            if min_rank != 1:
                errors.append(
                    f"Step 3: rank for track {t_name!r} does not start at 1 "
                    f"(min_rank={min_rank})"
                )

        # ------------------------------------------------------------------
        # Step 4: Change Group by back to "None"; apply Track filter="straight".
        #         GUI re-enables Track combobox (value preserved).
        # ------------------------------------------------------------------
        print("[smoke] Step 4: query(all, all, straight) — Track filter applied")
        rows = leaderboard.query("all", "all", "straight")
        print(f"[smoke]   -> {len(rows)} rows for 'straight' track")
        # straight is a turtle race with 4 racers → 4 unique racer entries.
        if len(rows) != 4:
            errors.append(
                f"Step 4: expected 4 rows for straight (4 turtle racers), got {len(rows)}"
            )

        # ------------------------------------------------------------------
        # Step 5: known_tracks() reflects all 3 planned rounds.
        # ------------------------------------------------------------------
        print("[smoke] Step 5: known_tracks()")
        tracks_seen = leaderboard.known_tracks()
        print(f"[smoke]   -> {tracks_seen}")
        if set(tracks_seen) != {"straight", "spiral", "rectangular"}:
            errors.append(
                f"Step 5: expected {{straight, spiral, rectangular}}, "
                f"got {set(tracks_seen)}"
            )

        # ------------------------------------------------------------------
        # Step 6: Reset Session.
        #         GUI confirms via askyesno (auto-patched to True globally),
        #         then calls leaderboard.reset_session().
        # ------------------------------------------------------------------
        print("[smoke] Step 6: reset_session()")
        leaderboard.reset_session()
        session_rows = leaderboard.query("session", "all", "all")
        print(f"[smoke]   -> session rows after reset: {len(session_rows)}")
        if session_rows != []:
            errors.append(
                f"Step 6: expected [] after reset_session(), got {session_rows}"
            )
        # Historic (all-time) data on disk must survive.
        all_rows_after_session_reset = leaderboard.query("all", "all", "all")
        print(f"[smoke]   -> all-time rows survive reset_session: {len(all_rows_after_session_reset)}")
        if len(all_rows_after_session_reset) < 6:
            errors.append(
                f"Step 6: expected >= 6 all-time rows after reset_session(), "
                f"got {len(all_rows_after_session_reset)}"
            )

        # ------------------------------------------------------------------
        # Step 7: Reset All.
        #         GUI confirms via askyesno, then calls leaderboard.reset_all().
        # ------------------------------------------------------------------
        print("[smoke] Step 7: reset_all()")
        leaderboard.reset_all()
        all_rows_after_reset_all = leaderboard.query("all", "all", "all")
        print(f"[smoke]   -> all-time rows after reset_all: {len(all_rows_after_reset_all)}")
        if all_rows_after_reset_all != []:
            errors.append(
                f"Step 7: expected [] after reset_all(), got {all_rows_after_reset_all}"
            )
        tracks_after_reset_all = leaderboard.known_tracks()
        if tracks_after_reset_all != []:
            errors.append(
                f"Step 7: expected known_tracks()==[] after reset_all(), "
                f"got {tracks_after_reset_all}"
            )
        # Reload JSON directly and assert canonical empty-store shape.
        import paths
        data_path = paths.user_data_path("leaderboard.json")
        with open(data_path, "r", encoding="utf-8") as f:
            disk_data = json.load(f)
        if disk_data != {"schema_version": 1, "races": []}:
            errors.append(
                f"Step 7: on-disk JSON after reset_all() expected "
                f'{{"schema_version": 1, "races": []}}, got {disk_data!r}'
            )

        if errors:
            print("\n[smoke] FAIL — leaderboard driver errors:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)

        print("[smoke] leaderboard driver PASS")
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

    # ---- monkeypatch ----
    # Patch dialogs module attributes (not local names) so main.main()'s
    # module-attribute lookups resolve to the fakes.
    dialogs.get_main_menu_choice  = fake_get_main_menu_choice
    dialogs.show_leaderboard      = fake_show_leaderboard   # Plan 1.1: renamed from _placeholder
    dialogs.get_user_track        = fake_get_user_track
    dialogs.get_user_species      = fake_get_user_species
    dialogs.get_user_bet          = fake_get_user_bet
    dialogs.ask_play_again_choice = fake_ask_play_again_choice

    # Silence background music.
    audio.start_background_music = lambda: None
    audio.stop_background_music  = lambda: None

    # Defensively auto-confirm any askyesno calls that reach tkinter (the driver
    # above calls leaderboard.reset_* directly, bypassing the GUI buttons, but
    # guard against future code paths accidentally reaching askyesno).
    import tkinter.messagebox
    tkinter.messagebox.askyesno = lambda *a, **kw: True

    print(f"[smoke] running main() — 3 rounds then leaderboard driver then quit...")
    import main
    main.main()
    print("[smoke] main() returned cleanly (audio.stop + screen.bye both ran)")

    # ---- verify post-main state ----
    # Reset All in fake_show_leaderboard wiped both session and disk; the
    # on-disk JSON must be the canonical empty store.
    import paths
    data_path = paths.user_data_path("leaderboard.json")
    print(f"[smoke] inspecting on-disk JSON at {data_path}")
    with open(data_path, "r", encoding="utf-8") as f:
        final_data = json.load(f)

    if final_data != {"schema_version": 1, "races": []}:
        print(
            f"[smoke] FAIL — post-main JSON expected "
            f'{{"schema_version": 1, "races": []}}, got {final_data!r}'
        )
        sys.exit(1)

    # Leaderboard driver must have been called exactly once.
    if show_leaderboard_calls != 1:
        print(
            f"[smoke] FAIL — expected show_leaderboard to be called exactly 1 time, "
            f"got {show_leaderboard_calls} — menu→leaderboard branch not exercised"
        )
        sys.exit(1)

    print(
        f"\n[smoke] PASS — 3 races recorded, all Phase 1 API contract surfaces "
        f"verified (Group-by, Track-filter, reset_session, reset_all, known_tracks)"
    )
    print(f"[smoke] (tmpdir was {tmpdir}; leaderboard.json remains there for inspection)")


if __name__ == "__main__":
    main()
