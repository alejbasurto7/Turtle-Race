# CONTEXT — Phase 3: Main Menu + Post-Race Prompt Restructure

User decisions captured during `/shipyard:plan 3` Discussion Capture (2026-05-16). Binding for all downstream agents.

## Decisions

### 1. Main menu visual approach
**Decision:** Toplevel modal with three stacked buttons (Race / View Leaderboard / Quit) drawn over the lawn background.

**Rationale:** Same pattern as existing `track`/`species`/`bet` dialogs (`Toplevel` + `grab_set` + `wait_window`). Minimum new infrastructure; consistent with the established modal style. The lawn is drawn on the turtle Screen at app entry (once) so the menu Toplevel sits over a non-empty canvas.

**Implications:**
- New function `dialogs.get_main_menu_choice()` returns `"race" | "leaderboard" | "quit"`.
- The lawn background must be drawn ONCE at app entry, before the first menu opens — call `race.set_background()` after `race.make_screen()` in `main()`'s prologue, BEFORE entering the outer menu loop.
- The button labels are plain text initially ("Race", "View Leaderboard", "Quit"). Image-based buttons (like the bet dialog) are explicitly deferred to Phase 5 polish.
- Vertical stack ordering (top-to-bottom): **Race**, **View Leaderboard**, **Quit**. Race is the primary action and gets the default focus.

### 2. View Leaderboard placeholder (Phase 4 will replace)
**Decision:** A real Toplevel modal with body text "Leaderboard view coming in Phase 4" and a single **Close** button.

**Rationale:** Exercises the menu → dialog → menu flow that Phase 4's real leaderboard window will use. More faithful to the eventual UX than a `messagebox.showinfo`.

**Implications:**
- New function `dialogs.show_leaderboard_placeholder()` (or `dialogs.show_leaderboard()` — the architect picks; Phase 4 will replace this function entirely with the real implementation).
- Same modal pattern (Toplevel + grab_set + wait_window).
- The Close button is the natural exit, so WM_DELETE_WINDOW MAY also call the Close handler (rather than being a no-op).
- Phase 4 plan will replace the body of this function in-place; Phase 3 builder should leave the function name and signature stable for Phase 4 to pick up.

### 3. Main menu X-button (window-close) behavior
**Decision:** Treat as Quit — clicking X on the menu Toplevel exits the app.

**Rationale:** The menu IS the top-level interaction. X = "I'm done with this whole thing" reads naturally as Quit. Less strict than the existing dialog pattern (where X is a no-op to force a deliberate choice), but the menu has an explicit Quit button so the user-intent ambiguity is gone.

**Implications:**
- `dialogs.get_main_menu_choice()` sets `WM_DELETE_WINDOW` to a handler that returns `"quit"`.
- The other dialogs (track / species / bet / play-again / leaderboard placeholder) retain their existing X-close policies.

### 4. Post-race prompt X-button (window-close) behavior
**Decision:** Treat as Main Menu — clicking X on the post-race prompt returns the user to the main menu.

**Rationale:** The least-destructive choice for the post-race context. The user has just finished a race and is choosing what to do next; "go back to the menu" is the natural default for an ambiguous close.

**Implications:**
- `dialogs.ask_play_again_choice()` returns `"again" | "menu" | "quit"`. The WM_DELETE_WINDOW handler maps X to `"menu"`.
- Button order in the prompt (left-to-right): **Play Again**, **Main Menu**, **Quit**. Play Again is the primary action and gets the default focus.

## Out-of-Scope Reminders (from PROJECT.md / ROADMAP.md)

- **No real leaderboard window** — placeholder only. Phase 4 will replace the placeholder with the Treeview-based view (filters, reset buttons, Per-Track tab, etc.).
- **No new race mechanics**. The inner round body keeps its current shape:
  ```
  set_background()
  track_name = dialogs.get_user_track()
  species    = dialogs.get_user_species()
  racers     = race.create_racers(species)
  ... draw stones / place racers / draw lines ...
  user_bet = dialogs.get_user_bet(species)
  winning_turtle, finish_order = race.run_race(...)
  finish_order_names = [...]
  leaderboard.record_race(species, track_name, finish_order_names)
  user_won = ...
  show_podium / celebrate / announce_result
  ```
  Only the post-race prompt and the surrounding loop scaffolding change.
- **No new third-party deps. No `turtle_race.spec` change** (Phase 5 will revisit).

## Carryover-driven design choices (no user decision needed)

- **Tk `Screen()` and `pygame.mixer` lifecycle.** Both initialized once at app entry, torn down once at exit. The menu does NOT recreate the Screen or restart pygame between iterations. (CLAUDE.md "Resource loading" invariant.)
- **`screen.clear()` placement.** The current code clears the screen at the top of each race round (except the first run). After Phase 3 this still applies — clear at the top of each iteration of the *inner* race-rounds loop. The outer menu loop does NOT clear the screen; the menu Toplevel covers the lawn well enough.
- **`set_background()` placement.** Called once at app entry (before the menu opens for the first time). Then re-drawn at the top of each race round (because the race draws boundary stones, start line, finish line, racers over the lawn — `screen.clear()` wipes those, so `set_background()` must redraw the lawn).
- **`audio.start_background_music()` / `stop_background_music()`.** Bracket the whole app lifetime. Started once after `make_screen()`; stopped once before `screen.bye()` on app exit. Plays through the menu, the race, the podium, everything — same as today.
- **MIDI shuffle behavior** introduced in earlier commits is preserved.

## Carryover from Phase 2 (informational)

- **`tools/smoke_phase_2.py` will break after Phase 3** because it monkeypatches `dialogs.ask_play_again` (returning bool) which no longer exists — Phase 3 replaces it with `dialogs.ask_play_again_choice()` (returning a string). Phase 3 should leave a note in SUMMARY for Phase 5 or for any future debugging session, but does NOT need to fix the smoke (it was a one-off Phase 2 verification artifact). Phase 3 will define its own no-GUI verification path during its build.
- **`leaderboard.record_race(...)` call site** stays in the same relative position (between `run_race` and `show_podium`), but now lives inside the inner race-rounds loop body rather than the (former) single outer loop body.
- **`import leaderboard` in main.py** remains. Phase 3 may need to also import the new menu functions from `dialogs`; the existing `import dialogs` still works since the new functions are added to that module.

## Open Questions Left for the Architect

- **`first_run` flag elimination.** The current code uses a `first_run` boolean to skip `screen.clear()` on the very first iteration. After Phase 3, the inner loop's first iteration is also a "first run" if it follows the menu → race transition. The architect should design the inner loop so `screen.clear()` is called at the top of every iteration EXCEPT the very first time the inner loop is entered for the first time in the app's life (where the canvas is already clean post-`make_screen()` + initial `set_background()`). Alternatives: (a) carry a module-level or main-local `first_round_ever` flag; (b) just always clear, accepting that the very first clear on an empty canvas is a no-op; (c) initialize the inner loop with a clear+background as its first action regardless.
- **`dialogs.ask_play_again()` removal vs. keep-and-deprecate.** The existing function returns bool. After Phase 3, no caller uses it. The architect should choose: (a) delete it cleanly; (b) leave a `# DEPRECATED — use ask_play_again_choice` comment. **Recommendation:** delete it cleanly. The codebase doesn't carry dead helpers.
- **How `main()` exits when the user picks Quit from any prompt.** Currently exits the while loop, then calls `audio.stop_background_music()` + `screen.bye()`. After Phase 3, Quit from the menu should hit the same exit path; Quit from the post-race prompt should break out of BOTH the inner race-rounds loop AND the outer menu loop. A single `running = False` sentinel that both loops check is the cleanest approach. The architect specifies.
