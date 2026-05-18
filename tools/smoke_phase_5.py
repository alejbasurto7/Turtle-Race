"""Automated source-mode smoke test for Phase 5: path-resolution + leaderboard
file-lifecycle invariants.

Scope (CONTEXT-5 Decision 4 — split-smoke):
  This smoke covers ONLY the writable-user-data path resolution and the
  leaderboard file lifecycle:
    1. paths.user_data_path("leaderboard.json") resolves under the redirected
       %APPDATA% tempdir AND auto-creates the parent directory on demand.
    2. record_race() writes a JSON file with schema_version=1 and the correct
       race count after each call.
    3. leaderboard.reset_session() clears the in-memory session but leaves the
       on-disk file byte-identical.
    4. leaderboard.reset_all() rewrites the file to exactly
       {"schema_version": 1, "races": []}.

This is NOT a re-run of tools/smoke_phase_4.py. The Phase 4 smoke covers the
menu/round/leaderboard UI contract (via main.main() monkeypatch). This smoke
is scope-limited to paths + leaderboard only — no Tk-touching module is loaded
(dialogs / main / audio / tkinter / turtle / pygame / race / constants /
tracks) — exercising the Tk-free invariant documented in CLAUDE.md.

The automated half of the Phase 5 smoke. The manual (packaged-exe) half is
tools/smoke_packaged.md, which must be run by a human before any release.

Run from the project root:

    python tools/smoke_phase_5.py

Exits 0 on success, non-zero with a "[smoke] FAIL — <reason>" diagnostic on any
verification failure.

This is a Phase 5 verification artifact (Plan 2.1). It is NOT part of pytest —
it lives under tools/, not tests/, so pytest does not collect it.

Per CONTEXT-5 Decision 6: the env-setup boilerplate (tempfile.mkdtemp +
os.environ["APPDATA"] + sys.path.insert) is intentionally duplicated from
smoke_phase_4.py. A tools/_smoke_common.py extraction was deferred to a future
maintenance pass.
"""

import json
import os
import sys
import tempfile


def main():
    # ---- Step 1: env redirect BEFORE any paths/leaderboard import ----
    tmpdir = tempfile.mkdtemp(prefix="reptilerace_phase5_smoke_")
    os.environ["APPDATA"] = tmpdir
    print(f"[smoke] redirected %APPDATA% to {tmpdir}")

    # Make project root importable.
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # ---- Step 2: import paths and leaderboard; assert path resolution ----
    import paths
    import leaderboard

    data_path = paths.user_data_path("leaderboard.json")

    if not os.path.normpath(data_path).startswith(os.path.normpath(tmpdir)):
        print(
            f"[smoke] FAIL — user_data_path {data_path!r} not under tempdir {tmpdir!r}"
        )
        sys.exit(1)

    if os.path.basename(data_path) != "leaderboard.json":
        print(
            f"[smoke] FAIL — expected basename 'leaderboard.json', got {os.path.basename(data_path)!r}"
        )
        sys.exit(1)

    if not os.path.isdir(os.path.dirname(data_path)):
        print(
            f"[smoke] FAIL — parent directory {os.path.dirname(data_path)!r} was not created by user_data_path()"
        )
        sys.exit(1)

    if os.path.exists(data_path):
        print(
            f"[smoke] FAIL — expected leaderboard.json to NOT exist yet after user_data_path() call "
            f"(file is only created by the first record_race), but it exists at {data_path!r}"
        )
        sys.exit(1)

    print(f"[smoke] path resolution OK: {data_path}")

    # ---- Step 3: drive a 2-race fixture (mixed species, different tracks) ----

    # Race 1: turtles on straight (4 racers in canonical finish order)
    leaderboard.record_race("turtles", "straight", ["Phil", "Bert", "Speedy", "Slowpoke"])

    if not os.path.exists(data_path):
        print(
            f"[smoke] FAIL — leaderboard.json did not appear on disk after first record_race; "
            f"expected file at {data_path!r}"
        )
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("schema_version") != 1:
        print(
            f"[smoke] FAIL — expected schema_version=1 after first record_race, "
            f"got {data.get('schema_version')!r}"
        )
        sys.exit(1)

    if len(data.get("races", [])) != 1:
        print(
            f"[smoke] FAIL — expected 1 race in JSON after first record_race, "
            f"got {len(data.get('races', []))}"
        )
        sys.exit(1)

    print("[smoke] first record OK: 1 race, schema_version=1")

    # Race 2: snakes on spiral (3 racers)
    leaderboard.record_race("snakes", "spiral", ["Shadow", "Anaconda", "Ralph"])

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if len(data.get("races", [])) != 2:
        print(
            f"[smoke] FAIL — expected 2 races in JSON after second record_race, "
            f"got {len(data.get('races', []))}"
        )
        sys.exit(1)

    if data["races"][0].get("species") != "turtles":
        print(
            f"[smoke] FAIL — races[0].species expected 'turtles', got {data['races'][0].get('species')!r}"
        )
        sys.exit(1)

    if data["races"][0].get("track") != "straight":
        print(
            f"[smoke] FAIL — races[0].track expected 'straight', got {data['races'][0].get('track')!r}"
        )
        sys.exit(1)

    if data["races"][1].get("species") != "snakes":
        print(
            f"[smoke] FAIL — races[1].species expected 'snakes', got {data['races'][1].get('species')!r}"
        )
        sys.exit(1)

    if data["races"][1].get("track") != "spiral":
        print(
            f"[smoke] FAIL — races[1].track expected 'spiral', got {data['races'][1].get('track')!r}"
        )
        sys.exit(1)

    print("[smoke] second record OK: 2 races on disk")

    # ---- Step 4: reset_session() leaves the file present and byte-unchanged ----

    before = open(data_path, "rb").read()
    mtime_before = os.path.getmtime(data_path)

    leaderboard.reset_session()

    if not os.path.exists(data_path):
        print(
            f"[smoke] FAIL — leaderboard.json was deleted by reset_session(); "
            f"expected file to remain at {data_path!r}"
        )
        sys.exit(1)

    after = open(data_path, "rb").read()

    if before != after:
        mtime_after = os.path.getmtime(data_path)
        print(
            f"[smoke] FAIL — leaderboard.json was modified by reset_session() "
            f"(mtime before={mtime_before}, after={mtime_after}); "
            f"reset_session() must be in-memory-only"
        )
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if len(data.get("races", [])) != 2:
        print(
            f"[smoke] FAIL — expected 2 races on disk after reset_session(), "
            f"got {len(data.get('races', []))}"
        )
        sys.exit(1)

    session_rows = leaderboard.query("session", "all", "all")
    if session_rows != []:
        print(
            f"[smoke] FAIL — expected query('session', 'all', 'all') == [] after "
            f"reset_session(), got {session_rows!r}"
        )
        sys.exit(1)

    print(
        f"[smoke] reset_session OK: file unchanged on disk ({len(before)} bytes), session emptied"
    )

    # ---- Step 5: reset_all() rewrites the file to the canonical empty store ----

    leaderboard.reset_all()

    if not os.path.exists(data_path):
        print(
            f"[smoke] FAIL — leaderboard.json was deleted by reset_all(); "
            f"expected file to be rewritten (not deleted) at {data_path!r}"
        )
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data != {"schema_version": 1, "races": []}:
        print(
            f"[smoke] FAIL — expected on-disk JSON after reset_all() to be exactly "
            f'{{"schema_version": 1, "races": []}}, got {data!r}'
        )
        sys.exit(1)

    print("[smoke] reset_all OK: file rewritten to canonical empty store")

    # ---- Step 6: final PASS line ----
    print("[smoke] phase 5 smoke PASS — path resolution + file lifecycle verified")
    print(f"[smoke] (tmpdir was {tmpdir}; leaderboard.json remains there for inspection)")


if __name__ == "__main__":
    main()
