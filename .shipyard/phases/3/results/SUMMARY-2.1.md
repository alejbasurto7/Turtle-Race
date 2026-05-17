# Build Summary: Plan 2.1 (Phase 3)

## Status: complete

(Task 2 — no-GUI smoke — substituted by an orchestrator-authored script and verified end-to-end. The plan's intent — verify the new menu/round/leaderboard/quit flow drives the round body correctly — is preserved.)

## Tasks Completed
- **Task 1** — restructure `main.py` into outer menu / inner race-rounds two-level loop + delete dead `dialogs.ask_play_again` — complete — files: `main.py`, `dialogs.py` (commit `ba4e24b`).
- **Task 2** — add `tools/smoke_phase_3.py` (no-GUI end-to-end smoke) — complete (orchestrator-authored + verified) — files: `tools/smoke_phase_3.py` (commit `e94f24c`).

## Files Modified
- **`main.py`** (+~50 / -~30): entire `main()` body replaced. The Phase 2 single-loop shape is gone. New structure: outer `while running` driven by `dialogs.get_main_menu_choice()` branching to `quit` / `leaderboard` / inner-race-rounds; inner `while in_round_loop` holds the existing race body with `dialogs.ask_play_again_choice()` at the bottom. The `first_run` flag and `keep_playing` boolean are eliminated. `screen.clear()` is now called unconditionally at the top of each inner-loop iteration (idempotent on the first iteration's already-clean lawn-only canvas).
- **`dialogs.py`** (-3): the legacy `ask_play_again()` (bool-returning `messagebox.askyesno`) deleted in the same atomic commit as the call-site replacement. After `ba4e24b`: `grep -cE "^def ask_play_again[^_]" dialogs.py` → 0; `grep -cE "^def ask_play_again_choice" dialogs.py` → 1.
- **`tools/smoke_phase_3.py`** (new, ~156 lines): no-GUI smoke script. Monkeypatches the three new Phase 3 dialogs + the existing race-dialog surface. Drives a documented flow: `menu→race→again→race→menu→leaderboard→menu→race→quit`. Inspects the on-disk JSON after `main()` returns. Asserts schema, race count (exactly 3 — the leaderboard placeholder does NOT record a race), chronological timestamps, per-race species/track/finish_order length.

## Decisions Made
- **`ask_play_again` deletion atomically folded into Task 1's commit.** Splitting it into a separate task would leave one intermediate commit where either `main.py` references a non-existent function or `dialogs.py` carries an orphaned helper. Neither is acceptable; the architect mandated the atomic shape and the builder followed it cleanly.
- **`tools/smoke_phase_3.py` (Task 2) authored by the orchestrator, not the builder.** Same constraint as Phase 2: the builder runs without a display, so end-to-end verification requires the orchestrator to run the script directly. The script's monkeypatch surface is wider than Phase 2's (3 new dialogs in addition to the 3 race dialogs + audio silencer).
- **`tools/smoke_phase_2.py` left broken by design.** Plan 2.1 explicitly forbids touching it; it monkeypatches the now-deleted `dialogs.ask_play_again` and is a Phase 2 historical artifact, not a regression-test suite. `smoke_phase_3.py` is the canonical no-GUI smoke going forward.

## Issues Encountered
- **None material.** The `main()` rewrite was a verbatim drop-in from RESEARCH-3 §1; no Tk lifecycle surprises encountered when running the smoke (Tk Screen() created once, reused across menu/round transitions, closed cleanly via `screen.bye()` after the outer loop exits). `audio.start_background_music` / `stop_background_music` correctly bracket the whole app lifetime.
- One minor convention oddity that turned up during the smoke run: `dialog.transient()` is called with no argument in the three new Phase 3 dialogs (matches the builder's choice in Plan 1.1) but is absent from the three legacy dialogs (`get_user_track / get_user_species / get_user_bet`). Logged in `.shipyard/ISSUES.md` by the Plan 1.1 reviewer; non-blocking; deferred to Phase 5 polish.

## Verification Results

### Static checks against commit `ba4e24b`
- `grep -cE "^def ask_play_again[^_]" dialogs.py` → **0** (deletion confirmed).
- `grep -cE "^def ask_play_again_choice" dialogs.py` → **1** (Phase 3 replacement intact).
- `grep -c "first_run" main.py` → **0** (flag eliminated).
- `grep -c "keep_playing" main.py` → **0** (the old loop-control bool is gone).
- `grep -c "ask_play_again_choice\|get_main_menu_choice\|show_leaderboard_placeholder" main.py` → **3** (one call site for each).
- `python -c "import main"` exits 0.
- `pytest -q` → **135 passed** (unchanged from Phase 2 baseline).

### End-to-end smoke (Task 2, orchestrator-verified, 2026-05-17 08:00–08:02 local)
Smoke flow exercised (per `tools/smoke_phase_3.py`):
```
menu → race
        round 1: turtles / straight     → again
        round 2: snakes / spiral        → menu
menu → leaderboard (placeholder, no race recorded)
menu → race
        round 3: turtles / rectangular  → quit
```

Result excerpt:
```
[smoke] running main() — expect 3 rounds across the menu flow...
[smoke] main() returned cleanly (audio.stop + screen.bye both ran)
[smoke] schema_version = 1
[smoke] races count    = 3
[smoke]   race 1: ts='2026-05-17T08:00:55' species='turtles' track='straight'     finish_order=['Michaelangelo', 'Leonardo', 'Raphael', 'Donatello']
[smoke]   race 2: ts='2026-05-17T08:01:56' species='snakes'  track='spiral'       finish_order=['Anaconda', 'Ralph', 'Shadow']
[smoke]   race 3: ts='2026-05-17T08:02:25' species='turtles' track='rectangular'  finish_order=['Donatello', 'Leonardo', 'Michaelangelo', 'Raphael']
[smoke] PASS — 3 races recorded with expected schema, species, track, and finish_order length
[smoke] menu→leaderboard→menu transition executed cleanly (no extra races recorded)
```

Cross-check vs. on-screen podium output (printed by `race.run_race`):
- Race 1 podium: 1st Michaelangelo / 2nd Leonardo / 3rd Raphael / 4th Donatello — **matches `finish_order`**.
- Race 2 podium: 1st Anaconda / 2nd Ralph / 3rd Shadow — **matches `finish_order`**.
- Race 3 podium: 1st Donatello / 2nd Leonardo / 3rd Michaelangelo / 4th Raphael — **matches `finish_order`**.

### Coverage of ROADMAP Phase 3 success criteria
All criteria met. Notably:
- The "View Leaderboard" → placeholder → return-to-menu transition is exercised (and produces zero additional race records, confirming the placeholder is a pure visual no-op).
- Quit from the post-race prompt cleanly breaks BOTH the inner and outer loops; `audio.stop_background_music()` and `screen.bye()` both fire after main returns. (Plan 2.1 Task 1's "Quit propagation" hard constraint is verified.)
- `pygame.mixer` and `Screen()` are initialized once at app entry and torn down once at exit (the smoke's main() invocation does both).
