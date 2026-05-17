---
phase: 3-main-menu-and-post-race-restructure
plan: 2.1
wave: 2
dependencies: [1.1]
must_haves:
  - Restructure `main()` into a two-level loop (outer menu loop + inner race-rounds loop) per RESEARCH §1's target shape.
  - Single `running` boolean shared by both loops for clean Quit propagation; inner loop additionally uses `in_round_loop`.
  - Lawn background drawn ONCE at app entry (before the first menu); also re-drawn at the top of each inner race-round iteration (after `screen.clear()`).
  - `first_run` flag is eliminated — always clear at the top of the inner loop (idempotent on the first iteration's already-clean canvas).
  - `audio.start_background_music()` / `stop_background_music()` continue to bracket the WHOLE app lifetime (started once at entry, stopped once at exit).
  - `leaderboard.record_race(...)` call site stays in the same relative position (between `run_race` and `show_podium`) — now inside the inner race-rounds loop body.
  - Delete `dialogs.ask_play_again()` (the old bool-returning function) in the same atomic commit that replaces its only call site in `main.py`.
  - Add a no-GUI smoke script `tools/smoke_phase_3.py` that exercises the new menu → race → menu → quit flow without manual clicks.
  - Test baseline 135 stays green.
files_touched:
  - main.py
  - dialogs.py
  - tools/smoke_phase_3.py
tdd: false
risk: medium
---

# Plan 2.1: Restructure `main.py` into two-level loop + delete dead `ask_play_again` + add Phase 3 smoke

## Context

With the three new dialog functions present in `dialogs.py` (Plan 1.1), `main.py` can be restructured to be main-menu-driven without breaking the runtime at any commit boundary. This plan owns the `main.py` restructure (Task 1), the `ask_play_again` cleanup (folded into Task 1 because the call-site replacement and the dead-function deletion are the same atomic change), and a Phase 3 no-GUI smoke script (Task 2) that exercises the new control flow end-to-end without manual clicks.

The restructure follows RESEARCH §1's target shape exactly: outer `while running` loop that calls `get_main_menu_choice()` and branches on `"race" | "leaderboard" | "quit"`; inner `while in_round_loop` loop that holds the existing race body plus the new `ask_play_again_choice()`-based post-race prompt. Quit from either prompt propagates by setting `running = False`. The `first_run` flag from the Phase 2 code is replaced by always clearing the screen at the top of the inner loop — `screen.clear()` is idempotent on an empty canvas, so the very first inner-loop iteration (immediately after `make_screen()` + initial `set_background()`) clears nothing harmful.

`tools/smoke_phase_3.py` mirrors `tools/smoke_phase_2.py` but monkeypatches the three NEW dialog functions plus the still-existing `get_user_track / get_user_species / get_user_bet`. It must redirect `%APPDATA%` to a tempdir BEFORE any path resolution (same pattern as Phase 2's smoke). Verifies a 3-iteration flow that produces 2 race records: `menu→race` → `race→again` → `race→menu` → `menu→quit`. The Phase 2 smoke (`tools/smoke_phase_2.py`) is left in place as historical reference (it will fail post-Plan-2.1 because `dialogs.ask_play_again` no longer exists — this is documented in Phase 2's PHASE-VERIFICATION.md and is expected; do NOT update or delete the Phase 2 smoke from this plan).

## Dependencies

- **Plan 1.1** complete: `dialogs.get_main_menu_choice`, `dialogs.ask_play_again_choice`, and `dialogs.show_leaderboard_placeholder` must all exist with the documented signatures. Plan 2.1 imports nothing new in `dialogs.py` — it just calls them.
- Phase 2 baseline (commit `e38eb02`) plus the three commits from Plan 1.1.

## Tasks

### Task 1: Restructure `main.py` into outer menu / inner race-rounds two-level loop + delete dead `dialogs.ask_play_again`

**Files:** `main.py`, `dialogs.py`
**Action:** modify (both)
**TDD:** false
**Description:**

Rewrite `main()` to match RESEARCH §1's target shape. Delete the old `dialogs.ask_play_again` in the same commit since its only caller (`main.py`'s `keep_playing = dialogs.ask_play_again()` line) is being replaced — leaving the dead function would violate the "no dead helpers" convention noted in CONTEXT-3 Open Questions.

**Target `main()` body (per RESEARCH §1, ~50 lines, drop-in replacement of the entire function):**

```python
def main():
    race.make_screen()
    audio.start_background_music()
    screen = race.get_screen()

    race.set_background()                  # Lawn drawn once for the menu backdrop.

    running = True
    while running:
        choice = dialogs.get_main_menu_choice()
        if choice == "quit":
            running = False
            break
        if choice == "leaderboard":
            dialogs.show_leaderboard_placeholder()
            continue
        # choice == "race" — enter inner race-rounds loop.
        in_round_loop = True
        while in_round_loop:
            screen.clear()                              # Idempotent on first iteration's clean canvas.
            race.set_background()
            track_name = dialogs.get_user_track()
            species    = dialogs.get_user_species()
            racers     = race.create_racers(species)
            n          = len(racers)
            race.draw_boundary_stones(track_name, n)
            race.place_racers_on_track(racers, track_name)
            race.draw_start_line(track_name, n)
            race.draw_finish_line(track_name, n)

            user_bet = dialogs.get_user_bet(species)

            winning_turtle, finish_order = race.run_race(racers, track_name, user_bet)

            finish_order_names = [racers[i]['name'] for i in finish_order]
            leaderboard.record_race(species, track_name, finish_order_names)

            user_won = winning_turtle is racers[user_bet - 1]['o']
            race.show_podium(racers, finish_order)
            race.celebrate(winning_turtle, user_won, racers)
            race.announce_result(winning_turtle, user_bet, racers)

            post = dialogs.ask_play_again_choice()
            if post == "again":
                continue
            if post == "menu":
                screen.clear()
                race.set_background()                   # Refresh canvas to lawn-only for the menu.
                in_round_loop = False
            elif post == "quit":
                running = False
                in_round_loop = False

    audio.stop_background_music()
    screen.bye()
```

**`dialogs.py` change (same commit):**

Delete the `ask_play_again()` function entirely. After this commit:
- `Grep` for `def ask_play_again\b` in `dialogs.py` returns ZERO hits.
- `Grep` for `def ask_play_again_choice` returns exactly one hit (the new function from Plan 1.1).
- No code in the repository calls `dialogs.ask_play_again()` anymore.

**Hard constraints (control flow):**

- The `record_race` call site MUST stay between `run_race` and `show_podium`, exactly as Phase 2 left it. Do NOT reorder, hoist, or guard with try/except.
- The `screen.clear()` + `race.set_background()` pair after `post == "menu"` is REQUIRED — without it, the next main-menu Toplevel sits over leftover race elements (boundary stones, finish line, racer images), which fails CONTEXT-3 Decision 1's "menu drawn over the lawn" invariant.
- The initial `race.set_background()` at app entry (BEFORE the outer loop) is REQUIRED so the very first `get_main_menu_choice()` sits over the lawn, not a blank canvas (CONTEXT-3 Decision 1 + Carryover-driven design choices §"`set_background()` placement").
- `audio.start_background_music()` MUST be called exactly once, before the outer loop. `audio.stop_background_music()` MUST be called exactly once, after both loops exit. Music plays continuously through menu and race transitions (no pause / restart).
- `screen.bye()` MUST be called exactly once at the very end.
- The `running` and `in_round_loop` booleans MUST both be set to False when `post == "quit"` — this is the ONLY way Quit propagates from the inner loop to outer-loop exit. Do NOT use `sys.exit`, `return`, or `break` to escape from the inner loop on Quit — both flags being set causes the inner `while` to exit, then the outer `while running` sees `running = False` and exits cleanly.
- `if post == "again": continue` MUST come BEFORE the menu/quit branches — `continue` falls through to the top of the inner loop, which re-clears and re-draws. Do NOT skip the `screen.clear()` for the "again" branch; the existing Phase 2 code's `first_run` skip is removed deliberately.
- The `first_run` boolean from the Phase 2 code MUST be DELETED. Do NOT preserve it; do NOT reintroduce it under a different name. The new pattern relies on `screen.clear()` being idempotent on an already-clean canvas (the first inner-loop iteration immediately after `make_screen()` + `set_background()` runs clear on what is essentially a lawn-only canvas, which is harmless).

**Hard constraints (`dialogs.py` deletion):**

- ONLY the body and `def` line of `ask_play_again()` are removed. The surrounding functions (including the newly-added `ask_play_again_choice` from Plan 1.1) are not touched.
- This is the same commit as the `main.py` restructure — `dialogs.ask_play_again` becomes orphaned at the exact moment its only call site is replaced. The two changes are atomic to keep the repo in a runnable state at every commit boundary.

**Acceptance Criteria:**

- `python -c "import main"` succeeds.
- `python -c "import dialogs; assert not hasattr(dialogs, 'ask_play_again') or dialogs.ask_play_again is dialogs.ask_play_again_choice"` — actually simpler: `python -c "import dialogs; assert not hasattr(dialogs, 'ask_play_again'), 'old ask_play_again should be deleted'"` exits 0.
- `python -c "import dialogs; assert callable(dialogs.ask_play_again_choice)"` exits 0 (new function still present).
- `Grep` for `\bdef ask_play_again\b` in `dialogs.py` returns ZERO hits.
- `Grep` for `dialogs.ask_play_again\(\)` (the bool-call form) across the repo (excluding `tools/smoke_phase_2.py` and `.shipyard/`) returns ZERO hits.
- `Grep` for `first_run` in `main.py` returns ZERO hits.
- `Grep` for `keep_playing` in `main.py` returns ZERO hits (replaced by `running` / `in_round_loop`).
- `Grep` for `dialogs.get_main_menu_choice` in `main.py` returns exactly one hit.
- `Grep` for `dialogs.ask_play_again_choice` in `main.py` returns exactly one hit.
- `Grep` for `dialogs.show_leaderboard_placeholder` in `main.py` returns exactly one hit.
- `Grep` for `leaderboard.record_race` in `main.py` returns exactly one hit (still inside the inner loop).
- `Grep` for `audio.start_background_music` in `main.py` returns exactly one hit (still bracketing the whole loop, not inside it).
- `Grep` for `audio.stop_background_music` in `main.py` returns exactly one hit (still after both loops, before `screen.bye()`).
- `pytest` reports 135 tests passing. No baseline regression.

---

### Task 2: Create `tools/smoke_phase_3.py` and run it to verify the new control flow

**Files:** `tools/smoke_phase_3.py` (new), `.shipyard/phases/3/results/SUMMARY-2.1.md` (created by builder, captures evidence)
**Action:** create + verify
**TDD:** false
**Description:**

Create a no-GUI smoke script mirroring `tools/smoke_phase_2.py` but for the Phase 3 control flow. It monkeypatches the three NEW dialog functions plus the existing race-dialog trio, redirects `%APPDATA%` to a tempdir, runs `main.main()`, and asserts the resulting JSON contains exactly the expected number of race records.

**Canned flow (the smoke must orchestrate exactly this sequence):**

1. Iteration 1 of outer loop: `get_main_menu_choice()` → `"race"`.
   - Inner iteration 1: turtle race on `straight`. After race: `ask_play_again_choice()` → `"again"`.
   - Inner iteration 2: snake race on `spiral`. After race: `ask_play_again_choice()` → `"menu"`.
2. Iteration 2 of outer loop: `get_main_menu_choice()` → `"leaderboard"` (placeholder dismissed immediately).
3. Iteration 3 of outer loop: `get_main_menu_choice()` → `"quit"`.

Expected post-run JSON state: exactly 2 race records (one turtles/straight with 4-entry finish_order, one snakes/spiral with 3-entry finish_order); the `"leaderboard"` and `"quit"` outer-loop iterations record nothing.

**Skeleton (closely follows `tools/smoke_phase_2.py`):**

```python
"""No-GUI smoke test for Phase 3's two-level loop + new dialog functions.

Monkeypatches the new menu/post-race dialogs plus the existing race-flow
dialogs, redirects %APPDATA% to a tempdir, runs main.main(), and asserts
the resulting leaderboard.json contains exactly the planned race records.

Exits 0 on success, non-zero with a printed error list on failure.

Phase 2's tools/smoke_phase_2.py is now broken (it monkeypatches the
removed dialogs.ask_play_again); this script replaces it for live
verification of the Phase 3 control flow.
"""

import json
import os
import sys
import tempfile


def main():
    tmpdir = tempfile.mkdtemp(prefix="turtlerace_smoke3_")
    os.environ["APPDATA"] = tmpdir
    print(f"[smoke3] redirected %APPDATA% to {tmpdir}")

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    import dialogs
    import audio

    # Outer-loop menu choices: race, then leaderboard, then quit.
    menu_choices = iter(["race", "leaderboard", "quit"])
    # Inner-loop post-race choices: again (continue), then menu (exit inner loop).
    post_choices = iter(["again", "menu"])
    # Race rounds: 1 turtle (4 racers), 1 snake (3 racers).
    rounds = [
        {"track": "straight", "species": "turtles", "bet": 1},
        {"track": "spiral",   "species": "snakes",  "bet": 2},
    ]
    round_idx = 0

    def fake_get_main_menu_choice():
        return next(menu_choices)

    def fake_ask_play_again_choice():
        return next(post_choices)

    def fake_show_leaderboard_placeholder():
        print("[smoke3] placeholder dismissed")
        return None

    def fake_get_user_track():
        nonlocal round_idx
        round_idx += 1
        return rounds[round_idx - 1]["track"]

    def fake_get_user_species():
        return rounds[round_idx - 1]["species"]

    def fake_get_user_bet(species):
        return rounds[round_idx - 1]["bet"]

    dialogs.get_main_menu_choice         = fake_get_main_menu_choice
    dialogs.ask_play_again_choice        = fake_ask_play_again_choice
    dialogs.show_leaderboard_placeholder = fake_show_leaderboard_placeholder
    dialogs.get_user_track               = fake_get_user_track
    dialogs.get_user_species             = fake_get_user_species
    dialogs.get_user_bet                 = fake_get_user_bet

    audio.start_background_music = lambda: None
    audio.stop_background_music  = lambda: None

    print(f"[smoke3] running main() — expect 2 races recorded")
    import main as main_mod
    main_mod.main()
    print(f"[smoke3] main() returned")

    import paths
    data_path = paths.user_data_path("leaderboard.json")
    print(f"[smoke3] inspecting {data_path}")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[smoke3] schema_version = {data.get('schema_version')!r}")
    print(f"[smoke3] races count    = {len(data.get('races', []))}")
    for i, r in enumerate(data.get("races", [])):
        print(f"[smoke3]   race {i+1}: ts={r['ts']!r} species={r['species']!r} "
              f"track={r['track']!r} finish_order={r['finish_order']!r}")

    errors = []
    if data.get("schema_version") != 1:
        errors.append(f"expected schema_version=1, got {data.get('schema_version')!r}")
    if len(data.get("races", [])) != 2:
        errors.append(f"expected 2 race records, got {len(data.get('races', []))}")

    # The two recorded races must match the planned rounds (in order).
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
        print("\n[smoke3] FAIL — verification errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"\n[smoke3] PASS — 2 races recorded with expected schema, species, track, and finish_order length")
    print(f"[smoke3] outer menu loop visited race / leaderboard / quit choices as planned")
    print(f"[smoke3] (tmpdir was {tmpdir})")


if __name__ == "__main__":
    main()
```

**Smoke run protocol (the builder MUST follow):**

1. Run `python tools/smoke_phase_3.py` from the project root.
2. A Tk window opens and animates two races (one turtle, one snake) without any manual interaction. The window closes when `main()` returns.
3. The script prints `[smoke3] PASS` and exits 0 on success.
4. On the same console, also run `pytest` from project root and confirm 135 tests still pass.
5. Capture both outputs (the smoke script stdout AND the final `pytest` summary line) into `.shipyard/phases/3/results/SUMMARY-2.1.md` under headings "Smoke run" and "Test suite".

**Hard constraints:**

- `tools/smoke_phase_3.py` MUST redirect `%APPDATA%` via `os.environ["APPDATA"]` BEFORE the first import that triggers `paths.user_data_path` resolution. Same pattern as Phase 2's smoke. Otherwise the smoke pollutes the user's real `%APPDATA%\TurtleRace\leaderboard.json`.
- The smoke MUST monkeypatch the dialog functions on the `dialogs` module BEFORE `import main as main_mod` runs (else `main` may bind to the unpatched originals via `from dialogs import ...` — though `main.py` uses `import dialogs` not `from dialogs import`, so this is defensive; honor it anyway).
- The smoke MUST NOT touch `tools/smoke_phase_2.py`. That file is documented as broken-by-design after Phase 3; this plan does not delete or update it (CONTEXT-3 Carryover from Phase 2).
- Do NOT add `tools/smoke_phase_3.py` to `turtle_race.spec`'s `datas=` list. It is a dev-only tool, not a packaged asset.
- The smoke MUST NOT add new third-party dependencies. Standard library only (`json`, `os`, `sys`, `tempfile`).

**Acceptance Criteria:**

- `tools/smoke_phase_3.py` exists.
- Running `python tools/smoke_phase_3.py` exits 0 and prints `[smoke3] PASS — 2 races recorded` on the final non-blank line group.
- The smoke's tempdir contains a `leaderboard.json` with exactly 2 race records: one `{"species": "turtles", "track": "straight"}` with 4-name `finish_order`, one `{"species": "snakes", "track": "spiral"}` with 3-name `finish_order`. (The smoke script itself asserts this; manual inspection is optional.)
- The user's real `%APPDATA%\TurtleRace\leaderboard.json` is NOT modified by running the smoke (verified by checking its `mtime` / contents before and after, or simply by trusting the `os.environ["APPDATA"]` redirect — the builder's call).
- `pytest` after the smoke run still reports 135 tests passing.
- `.shipyard/phases/3/results/SUMMARY-2.1.md` exists and contains both the smoke output and the pytest summary line, plus a one-paragraph note that `tools/smoke_phase_2.py` is now broken-by-design (forward-pointer to Phase 5 if anyone wonders why).

## Verification

Run from project root after both tasks committed:

```powershell
# Static sanity
git log --oneline -6
python -c "import main"
python -c "import dialogs; assert not hasattr(dialogs, 'ask_play_again'); assert callable(dialogs.ask_play_again_choice); assert callable(dialogs.get_main_menu_choice); assert callable(dialogs.show_leaderboard_placeholder); print('dialogs surface clean')"

# Static checks on main.py shape
Select-String -Path main.py -Pattern 'first_run'        # expect: no matches
Select-String -Path main.py -Pattern 'keep_playing'      # expect: no matches
Select-String -Path main.py -Pattern 'running'           # expect: matches
Select-String -Path main.py -Pattern 'in_round_loop'     # expect: matches
Select-String -Path main.py -Pattern 'record_race'       # expect: 1 match
Select-String -Path main.py -Pattern 'start_background_music'  # expect: 1 match
Select-String -Path main.py -Pattern 'stop_background_music'   # expect: 1 match

# Smoke script
python tools/smoke_phase_3.py                                  # expect: [smoke3] PASS, exit 0

# Test suite
pytest                                                         # expect: 135 passed
```

Expected:

- `git log --oneline -6` shows the 3 Plan 1.1 commits plus this plan's 2 task commits on top of `e38eb02`.
- All `Select-String` checks match the expected match-count comments above.
- `python tools/smoke_phase_3.py` exits 0 with `[smoke3] PASS` on the final line group.
- `pytest` reports `135 passed`.

Cross-references:
- CONTEXT-3.md Carryover-driven design choices (Tk Screen / pygame.mixer lifecycle, `screen.clear` placement, `set_background` placement, music brackets).
- CONTEXT-3.md Open Questions (first_run elimination → option (c) carry-the-implicit-pattern; ask_play_again deletion → option (a) delete cleanly; Quit propagation → single `running` sentinel + secondary `in_round_loop` sentinel).
- RESEARCH.md §1 (target `main.py` shape — copy verbatim into Task 1).
- RESEARCH.md §2 (old `ask_play_again` location — `dialogs.py:291-292`).
- RESEARCH.md §5 (Phase 2 smoke breaks; document in SUMMARY for Phase 5).
- ROADMAP.md Phase 3 success criteria (all bullets satisfied by Tasks 1 and 2).
