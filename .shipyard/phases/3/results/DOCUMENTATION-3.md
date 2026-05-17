# Documentation Review — Phase 3

## Verdict: GAPS_IDENTIFIED (one low-cost fix now; one CLAUDE.md section is stale)

## Coverage Summary

| Area | Status | Notes |
|---|---|---|
| `dialogs.get_main_menu_choice()` docstring | ADEQUATE | Covers return values, X-button behavior (→ "quit"), button order, and initial focus. No action needed. |
| `dialogs.ask_play_again_choice()` docstring | ADEQUATE | Covers return values, X-button behavior (→ "menu"), button order, and initial focus. No action needed. |
| `dialogs.show_leaderboard_placeholder()` docstring | ADEQUATE | Notes Phase 4 will replace the body in-place and explicitly calls out the name/signature stability contract. No action needed. |
| `main.py` `main()` two-loop structure | GAP (low-cost) | The function has no comment or docstring. The outer `running` / inner `in_round_loop` sentinel pattern and the quit-propagation logic are non-obvious to a new contributor. A short comment at the top of the function body is warranted. |
| `tools/smoke_phase_3.py` module docstring | ADEQUATE | 30-line docstring covers purpose, flow exercised, expected outcome, invocation, pytest exclusion rationale, and the `smoke_phase_2.py` breakage note. Nothing missing. |
| CLAUDE.md "Round loop shape" section | STALE | Still describes the Phase 0/1/2 single-loop shape (`while keep_playing`, `ask_play_again()`). Phase 3 replaces this with a two-level loop and three new dialog functions. Recommend updating NOW — it actively misleads a contributor reading CLAUDE.md before Phase 4 ships. |
| CLAUDE.md "tkinter" bullet (Architecture) | MINOR STALE | Lists "three modal dialogs" and `messagebox`; Phase 3 adds two more dialogs and removes the `messagebox` call. Low priority — Phase 5 polish will sweep CLAUDE.md anyway — but worth noting. |

---

## Recommended Actions (prioritized)

### 1. Now (low-cost)

**Add a brief comment at the top of `main()` in `main.py` explaining the two-loop structure.**

The sentinel variables `running` and `in_round_loop` and the quit-propagation through both loops are genuinely non-obvious — the Phase 3 CONTEXT-3.md §Open Questions section even flagged this as an architect decision. The code is correct and clean, but a new contributor will need to trace both loops to understand why `running = False; in_round_loop = False` appears instead of a single `break`. A three-line comment pays for itself immediately.

Suggested text (insert as the first lines of the function body, before `race.make_screen()`):

```python
def main():
    # Two-level loop: outer iterates the main menu; inner iterates race rounds.
    # `running` controls the outer loop; `in_round_loop` controls the inner loop.
    # Quit from the post-race prompt sets both False so the outer loop exits cleanly
    # without re-entering the menu, allowing audio.stop + screen.bye to run once.
    race.make_screen()
    ...
```

**Update the "Round loop shape" section in CLAUDE.md.**

The current text references `while keep_playing`, `ask_play_again()` (deleted), and a single-level loop — none of which exist after Phase 3. A new contributor reading this before Phase 4 ships will get a false mental model of `main()`.

Suggested replacement for the "Round loop shape" section:

```markdown
### Round loop shape

`main()` uses a two-level loop. The **outer loop** iterates the main menu
(`get_main_menu_choice()` returns `"race" | "leaderboard" | "quit"`); the
**inner loop** iterates race rounds when `"race"` is chosen.

`running` (outer) and `in_round_loop` (inner) are the sentinel booleans. Quit
from the post-race prompt (`ask_play_again_choice()` → `"quit"`) sets both
False, so the outer loop exits cleanly without re-entering the menu — this is
intentional; `audio.stop_background_music()` and `screen.bye()` run exactly
once on the way out.

Each race round flows: `screen.clear()` → `set_background()` →
`get_user_track()` → `get_user_species()` → `create_racers(species)` →
place/draw → `get_user_bet(species)` → `run_race(racers, ...)` →
`leaderboard.record_race(...)` → `show_podium` → `celebrate` →
`announce_result` → `ask_play_again_choice()`.

The race loop itself lives in `race.run_race(...)`. It advances every racer
along its lane path by a fraction of `shared_distance` per tick (so longer
lanes like the spiral don't auto-lose), detects finishers, and runs a fixed
`COAST_TICKS` post-finish coast for visual polish.
```

### 2. Defer to Phase 5

- **CLAUDE.md "tkinter" Architecture bullet** — update the dialog count and remove the `messagebox` reference once Phase 4 ships its real leaderboard dialog. The current text is imprecise but not misleading in a way that would cause a bug.
- **CLAUDE.md "Tk image references" section** — the three new Phase 3 functions use text buttons only (no `PhotoImage`), so no new stash entries are needed. Mention only if Phase 4 adds image buttons to the leaderboard dialog.
- All other Phase 1/2 CLAUDE.md deferred items (import-paths monkeypatch rule, `%APPDATA%` data location, smoke tools note) remain deferred to Phase 5.

### 3. Skip

- **`dialogs.ask_play_again()` tombstone** — it was deleted cleanly; no deprecation comment needed. The smoke tool already notes the `smoke_phase_2.py` breakage in its module docstring.
- **New dialog function entries in "Tk image references" section** — Phase 3 dialogs are text-only; the section's guidance (retain `PhotoImage` references) does not apply to them.
- **Demanding Google-style or Sphinx-style docstrings** anywhere in dialogs.py or main.py.

---

## Verdict Rationale

Phase 3 dialog docstrings are the strongest in the codebase: all three new functions document return values, X-button semantics, and button ordering in a single concise paragraph — exactly the information a caller needs. The smoke tool docstring is equally thorough. The only genuine gaps are `main()`'s missing structural comment (the two-loop / sentinel pattern is non-trivial and undocumented) and the "Round loop shape" section in CLAUDE.md, which now describes code that no longer exists. The CLAUDE.md staleness is the higher-priority fix because it will actively mislead any contributor who reads it before Phase 4 ships.
