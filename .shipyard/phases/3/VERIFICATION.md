# Plan Verification — Phase 3

## Verdict: PASS

## Coverage of Phase 3 success criteria (from ROADMAP.md)

| Criterion | Plan/Task | Status |
|---|---|---|
| `dialogs.get_main_menu_choice()` returns `"race" \| "leaderboard" \| "quit"`; Toplevel + grab_set + wait_window; over the lawn background | PLAN-1.1 Task 1 | covered |
| `dialogs.ask_play_again_choice()` returns `"again" \| "menu" \| "quit"`; replaces old `ask_play_again` callsite | PLAN-1.1 Task 2 (function add) + PLAN-2.1 Task 1 (call-site replacement) | covered |
| `main()`'s outer loop reshaped into two-level structure (outer menu, inner race rounds) | PLAN-2.1 Task 1 | covered (RESEARCH §1 target shape encoded verbatim) |
| Choosing **View Leaderboard** opens placeholder Toplevel ("Coming in Phase 4"); returns to menu | PLAN-1.1 Task 3 (placeholder) + PLAN-2.1 Task 1 (wiring) | covered |
| Tk `Screen()` and `pygame.mixer` still initialized once at app start, torn down once at exit | PLAN-2.1 Task 1 "Hard constraints" prohibit recreation | covered |
| `screen.clear()` + `set_background()` called at top of each race round, not on menu entry | PLAN-2.1 Task 1 target shape; menu loop does NOT call clear+background; inner loop calls both at top of every iteration | covered |
| `pytest` remains green | PLAN-2.1 Task 1 acceptance criteria require it; baseline 135 | covered |
| All existing race-loop invariants from CLAUDE.md preserved (positional identity, head-position finish, podium scaling, MIDI shuffle) | PLAN-2.1 Task 1 explicitly forbids reordering `record_race`, hoisting, or wrapping in try/except; no changes to `race.py`, `audio.py`, or constants | covered |

## Structural Checks

| Check | Result |
|---|---|
| Task count per plan | PLAN-1.1: 3, PLAN-2.1: 2 — both ≤ 3 |
| Wave / dependency ordering | 1.1 (no deps) → 2.1 (deps on 1.1) — strictly sequential |
| Same-file parallel conflicts | None — Plan 1.1 owns `dialogs.py` additions; Plan 2.1 modifies `main.py` and DELETES the old `ask_play_again` from `dialogs.py` (atomic with the call-site replacement). The cross-plan `dialogs.py` write is fine because 2.1 strictly depends on 1.1 and the deletion is independent of 1.1's additions. |
| Acceptance-criteria testability | Objective: grep checks for new function names, grep for absence of `ask_play_again`, pytest count, smoke verification |
| Verification commands | Concrete — pytest, grep, `python tools/smoke_phase_3.py` |

## CONTEXT-3 Decision Coverage

| Decision | Implementation | Verdict |
|---|---|---|
| 1. Toplevel modal menu over lawn | PLAN-1.1 Task 1 + PLAN-2.1 Task 1 calls `race.set_background()` once before first menu open | covered |
| 2. Real-Toplevel placeholder for View Leaderboard | PLAN-1.1 Task 3 — `show_leaderboard_placeholder()` with "Coming in Phase 4" body | covered |
| 3. Menu X-button → quit | PLAN-1.1 Task 1 sets `WM_DELETE_WINDOW` to `make_cb("quit")` | covered |
| 4. Post-race X-button → main menu | PLAN-1.1 Task 2 sets `WM_DELETE_WINDOW` to `make_cb("menu")` | covered |

## Scope Creep

None. Plans touch `dialogs.py` (additions in 1.1 + one deletion in 2.1), `main.py` (full rewrite of `main()`), and a new `tools/smoke_phase_3.py`. No changes to `race.py`, `audio.py`, `constants.py`, `tracks.py`, `paths.py`, `leaderboard.py`, or the PyInstaller spec. No new third-party dependencies. The placeholder leaderboard dialog explicitly defers the real Treeview/filter/reset implementation to Phase 4.

---

# Plan Critique — Feasibility Stress Test

## Verdict: READY

## Per-plan feasibility

### PLAN-1.1 — `dialogs.py` additions

- **File path:** `dialogs.py` exists (~293 lines after Phase 2). All three new functions append to it.
- **API surface:** the three new functions (`get_main_menu_choice`, `ask_play_again_choice`, `show_leaderboard_placeholder`) are new — no existing-API mismatch concern.
- **Existing pattern:** the architect's skeleton mirrors the existing `get_user_track` / `get_user_species` / `get_user_bet` modal pattern (verified at [dialogs.py:31, 137, 194](dialogs.py)). The `selected = [None]; make_cb; transient + grab_set + wait_window` shape is correct.
- **Verify commands:** runnable via grep + pytest.

### PLAN-2.1 — `main.py` restructure + cleanup + smoke

- **File paths:** `main.py` (57 lines after Phase 2) exists. `tools/` dir exists. `tools/smoke_phase_3.py` is new (no conflict).
- **API surface:** All function references are real:
  - `race.make_screen`, `race.get_screen`, `race.set_background`, `race.create_racers`, `race.draw_boundary_stones`, `race.place_racers_on_track`, `race.draw_start_line`, `race.draw_finish_line`, `race.run_race`, `race.show_podium`, `race.celebrate`, `race.announce_result` — all exist in `race.py`.
  - `audio.start_background_music`, `audio.stop_background_music` — exist in `audio.py`.
  - `leaderboard.record_race` — exists in `leaderboard.py` (Phase 1).
  - The three new dialogs (`get_main_menu_choice`, `show_leaderboard_placeholder`, `ask_play_again_choice`) — provided by Plan 1.1 (dependency declared).
  - The existing dialogs (`get_user_track`, `get_user_species`, `get_user_bet`) — exist.
- **`ask_play_again` deletion atomicity:** Plan 2.1 Task 1 modifies both `main.py` and `dialogs.py` in the same atomic commit. This avoids an intermediate state where either `main.py` calls a non-existent function or `dialogs.py` carries an orphaned helper. Correct sequencing.
- **`first_run` elimination:** RESEARCH §1's target shape replaces the conditional clear with an unconditional clear at the top of the inner loop. The very first iteration clears an already-clean canvas (lawn-only after the prologue's `set_background()`), which `screen.clear()` handles as a no-op. No semantic regression.
- **Quit propagation:** `running = False` set by either the menu Quit branch or the post-race Quit branch; the inner loop's `in_round_loop` is also set to False on post-race Quit so the inner loop exits cleanly before the outer loop checks `running`. Both loops exit normally, so `audio.stop_background_music()` + `screen.bye()` always run.
- **Smoke approach:** mirrors Phase 2's pattern (`%APPDATA%` redirect, monkeypatch dialog surface, run `main()`, inspect JSON). The new smoke must monkeypatch the new `get_main_menu_choice` and `ask_play_again_choice` rather than the old `ask_play_again`. Feasibility confirmed by Phase 2's working precedent.

## Cross-plan findings

- **Plan 1.1 / Plan 2.1 file overlap on `dialogs.py`:** Plan 1.1 adds three new functions; Plan 2.1 deletes one existing function (`ask_play_again`). The two operations are independent (different lines, different function names) so there's no merge-time conflict. Plan 2.1 is correctly declared as depending on Plan 1.1, so it runs strictly after.
- **No forward references** between waves beyond the declared dependency.
- **Phase 2 smoke breakage** is documented in Plan 2.1's Context block as expected (per CONTEXT-3's "Carryover from Phase 2" note). The architect explicitly forbids Plan 2.1 from touching `tools/smoke_phase_2.py` — correct, as the old smoke is a historical artifact.

## Risk register

- **Tk event-loop quirks with `transient()` without an explicit parent.** The existing dialogs call `dialog.transient()` with no argument. This works in Tk because the implicit parent is the most-recently-created Toplevel or the root. New dialogs created from the same module should inherit the same behavior. If a future refactor introduces an explicit `tkinter.Tk()` root, the menu's `transient()` may need a parent argument. Non-blocking — matches existing convention.
- **Inner-loop entry from menu after a prior race round.** Plan 2.1 explicitly handles this by calling `screen.clear()` + `set_background()` after `post == "menu"` so the next menu opens over a clean lawn. Without this, leftover race elements would bleed through. The plan's hard constraint is correct.
- **Quit from post-race vs. quit from menu** — both paths now have to run the same cleanup. The single `running` sentinel + always-run `audio.stop_background_music()` + `screen.bye()` after the outer loop satisfies this. The inner loop never `sys.exit()`s or returns early. Correct.
- **First inner-loop iteration's idempotent clear** — relies on `screen.clear()` being safe on an already-clean canvas. This is a documented turtle stdlib behavior; no risk.

## Complexity flags

- 3 files touched across both plans: `dialogs.py` (additions + 1 deletion), `main.py` (full `main()` rewrite), `tools/smoke_phase_3.py` (new). Under the 10-file / 3-directory thresholds.
- `main.py`'s `main()` function grows from ~30 lines to ~50 lines but stays one function (no helper extraction). Acceptable — the two-loop structure is the load-bearing change.

## Headline

Plans are feasible and ready to build. The atomic deletion of `ask_play_again` together with the `main.py` restructure is the architect's most important decision and is correctly sequenced. The Phase 2 smoke is left broken by design (already documented as carryover). Proceed with `/shipyard:build 3`.
