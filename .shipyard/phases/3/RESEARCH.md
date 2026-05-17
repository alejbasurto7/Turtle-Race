# RESEARCH — Phase 3: Main Menu + Post-Race Prompt Restructure

Phase 3 reshapes `main.py` and adds three new functions to `dialogs.py`. Most relevant patterns already documented in `.shipyard/phases/1/RESEARCH.md` and `.shipyard/phases/2/RESEARCH.md`. This file captures the Phase-3-specific findings.

## 1. Current `main.py` shape (post-Phase-2)

After Phase 2 commits `86a0830` (wiring) and `d2724a9` (cleanup), `main.py` is 57 lines:

```python
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import audio
import dialogs
import leaderboard
import race


def main():
    race.make_screen()
    audio.start_background_music()
    screen = race.get_screen()

    keep_playing = True
    first_run = True

    while keep_playing:
        if not first_run:
            screen.clear()
        first_run = False

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

        keep_playing = dialogs.ask_play_again()

    audio.stop_background_music()
    screen.bye()


if __name__ == "__main__":
    main()
```

**Post-Phase-3 target shape** (CONTEXT-3 Open Questions resolved here):

```python
def main():
    race.make_screen()
    audio.start_background_music()
    screen = race.get_screen()

    race.set_background()           # Lawn drawn once for the menu backdrop.

    running = True
    while running:
        choice = dialogs.get_main_menu_choice()
        if choice == "quit":
            running = False
            break
        if choice == "leaderboard":
            dialogs.show_leaderboard_placeholder()
            continue
        # choice == "race" -- enter inner race-rounds loop
        in_round_loop = True
        while in_round_loop:
            screen.clear()                  # Wipe any prior race elements
            race.set_background()           # Redraw lawn
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
                race.set_background()       # Clean up race elements for the menu backdrop
                in_round_loop = False
            elif post == "quit":
                running = False
                in_round_loop = False

    audio.stop_background_music()
    screen.bye()
```

**Notes for the architect:**
- The `first_run` flag from the old code is replaced by the always-clear-at-top-of-inner-loop pattern. The first iteration of the inner loop clears an already-clean (or lawn-only) screen — `screen.clear()` is idempotent and a no-op on an empty canvas.
- The `running` boolean is checked by the outer menu loop only. The inner race-rounds loop uses its own `in_round_loop` boolean. Quit propagates by setting BOTH to False.
- A single `screen.clear() + race.set_background()` after returning from the inner loop to the menu refreshes the canvas to "lawn only" so the next menu rendering sits over a clean backdrop. This matches CONTEXT-3 Decision 1's "menu drawn over the lawn" requirement.

## 2. Current `dialogs.ask_play_again()` (to be replaced)

[dialogs.py:291-292](dialogs.py#L291-L292):
```python
def ask_play_again():
    return tkinter.messagebox.askyesno("Turtle Race", "Do you want to play again?")
```

Phase 3 replaces this with `dialogs.ask_play_again_choice()` returning `"again" | "menu" | "quit"`. **Per CONTEXT-3 Open Questions: delete the old function** — no production caller uses it after Phase 3 (the one call site in `main.py` is replaced).

## 3. Existing modal dialog pattern in `dialogs.py`

All three existing modal dialogs (`get_user_track`, `get_user_species`, `get_user_bet`) use:

```python
dialog = tkinter.Toplevel()
dialog.resizable(False, False)
dialog.protocol("WM_DELETE_WINDOW", lambda: None)   # force a choice

# ... PhotoImage references stored on the dialog (e.g. dialog._track_images) ...

# ... buttons ...

dialog.transient()           # (or transient(parent))
dialog.grab_set()
dialog.wait_window()

return selected[0]
```

**Phase 3 new dialogs MUST follow this pattern** — three new functions:
- `get_main_menu_choice() -> str` — WM_DELETE → returns "quit" (CONTEXT-3 Decision 3, not no-op).
- `ask_play_again_choice() -> str` — WM_DELETE → returns "menu" (CONTEXT-3 Decision 4).
- `show_leaderboard_placeholder() -> None` — WM_DELETE → equivalent to Close (the only button). Returns nothing; the caller (`main()`) just continues the outer loop.

For the menu and post-race prompts, the "selected" sentinel pattern works the same way as `get_user_track`:
```python
selected = [None]
def make_cb(value):
    def cb():
        selected[0] = value
        dialog.destroy()
    return cb
# ... button.config(command=make_cb("race")) ...
dialog.protocol("WM_DELETE_WINDOW", make_cb("quit"))   # X → return "quit"
```

## 4. `race.make_screen`, `race.set_background`, `race.get_screen` — APIs to know

From `race.py`:
- `race.make_screen()` — initializes the turtle Screen, sets window dimensions, sets the title. Called once per app lifetime.
- `race.get_screen()` — returns the cached `Screen` instance (or `None` if `make_screen` hasn't run). Cheap.
- `race.set_background()` — calls `screen.bgpic(resource_path("lawn.jpg"))`. Idempotent; safe to call repeatedly.

`screen.clear()` is a turtle stdlib method — wipes all turtle objects and drawings but DOES NOT remove the bgpic. After `screen.clear()`, the lawn background may need to be re-set if `bgpic` was cleared. Actually — testing shows `screen.clear()` DOES clear `bgpic` on the underlying Tk canvas in some Tk versions. Safer to always re-call `set_background()` after `screen.clear()`, which is what the current Phase 2 code does.

## 5. Carryover bug from Phase 2 (informational)

`tools/smoke_phase_2.py` monkeypatches `dialogs.ask_play_again` (returning bool). Phase 3 deletes that function. After Phase 3 ships, the smoke utility will break with `AttributeError`. This is documented in Phase 2 PHASE-VERIFICATION.md "Carryover to Phase 3" and is expected — the Phase 2 smoke is a one-off verification artifact, not a regression-test suite.

Phase 3's verification can use a similar pattern (monkeypatch the new `dialogs.get_main_menu_choice` and `dialogs.ask_play_again_choice` to canned answers, then run `main.main()`). The Phase 2 smoke can be left in place as historical reference OR updated by Phase 3 if useful. **Recommendation:** Phase 3 writes its own `tools/smoke_phase_3.py` (or updates `smoke_phase_2.py` if scope allows) — the architect decides.

## 6. Test surface

Phase 3's changes are mostly Tk/GUI code that's not unit-testable without significant scaffolding. The existing 135-test suite must stay green. No new automated tests required; verification will mirror Phase 2's "smoke + static checks + manual eyeball" approach.

## 7. PyInstaller spec

No change required. Phase 3 doesn't introduce new bundled assets — text buttons only (per CONTEXT-3 Decision 1).
