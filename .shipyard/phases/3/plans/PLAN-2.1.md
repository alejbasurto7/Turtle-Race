---
phase: 3-snake-species
plan: 2.1
wave: 2
dependencies: [1.1]
must_haves:
  - get_user_species() function in dialogs.py returning "turtles" or "snakes"
  - Composite images (2x2 turtles, 1x3 snakes) composed at runtime via Pillow, sized to SPECIES_DIALOG_IMAGE_SIZE
  - main.py inserts species = dialogs.get_user_species() between get_user_track() and create_racers
  - main.py passes species to create_racers(species) and get_user_bet(species)
  - Opportunistic n = len(racers) hoist (SIMPLIFICATION-2 S2.2)
  - create_racers docstring updated to mention species is a SPECIES key and racer dicts include 'name' (DOCUMENTATION-2 actionable)
  - Manual smoke gate: both species reach podium on at least one track
  - pytest green
files_touched:
  - dialogs.py
  - main.py
  - race.py
tdd: false
risk: medium
---

# PLAN-2.1 — `get_user_species()` + `main.py` wire-up + manual smoke

## Context

Phase 3 Wave 2. Depends on PLAN-1.1 (which left `dialogs.get_user_bet` requiring a `species` arg, breaking `main.py` at runtime). This plan:
1. Adds `get_user_species()` with composite turtle/snake button images.
2. Repairs `main.py` runtime by inserting the species call and passing `species` through.
3. Folds in the small `n = len(racers)` hoist and the `create_racers` docstring update (CONTEXT-3 Decision 5 explicitly allows both opportunistic edits).
4. Performs the manual-smoke gate (turtles flow unchanged + snakes flow reaches podium with turtle-shaped placeholders — Phase 4 wires real snake shapes).

CONTEXT-3 decisions in scope: 1 (composite images via Pillow), 2 (no helper extraction), 5 (`main.py` insertion + opportunistic cleanups), 6 (end-state gate).

## Tasks

<task id="1" files="dialogs.py" tdd="false">
  <action>Add `get_user_species()` to `dialogs.py`, structured as a sibling of `get_user_track()` (CONTEXT-3 Decision 2: no helper extraction). Specifics:
- `Toplevel`, `title("Choose Your Racers")`, `resizable(False, False)`, `protocol("WM_DELETE_WINDOW", lambda: None)`.
- Header `Label`: text `"Which species will race?"`, font `("Arial", 12, "bold")`, `pady=12`, `columnspan=2`.
- Two buttons side-by-side at row=1: column 0 = Turtles composite, column 1 = Snakes composite. Each button uses `compound="top"`, with the species name as the label and a `PhotoImage` of the composite at `SPECIES_DIALOG_IMAGE_SIZE` × `SPECIES_DIALOG_IMAGE_SIZE`.
- Compose images **inline** in the function body (two call sites — a helper would be over-engineered per CONTEXT-3):
  - **Turtles composite:** create a blank `Image.new("RGB", (SPECIES_DIALOG_IMAGE_SIZE, SPECIES_DIALOG_IMAGE_SIZE), "white")`. Cell size = `SPECIES_DIALOG_IMAGE_SIZE // 2`. Paste the 4 turtle JPGs in `_TURTLE_GRID_LAYOUT` order, but mapping `(row, col)` from the layout's `(1|2, 0|1)` to image coords `((row-1)*cell, col*cell)` — i.e., Leonardo top-left, Donatello top-right, Raphael bottom-left, Michaelangelo bottom-right. Each tile resized via `Image.LANCZOS` to `(cell_size, cell_size)`.
  - **Snakes composite:** `Image.new("RGB", (SPECIES_DIALOG_IMAGE_SIZE, SPECIES_DIALOG_IMAGE_SIZE), "white")`. Cell width = `SPECIES_DIALOG_IMAGE_SIZE // 3`, cell height = `SPECIES_DIALOG_IMAGE_SIZE`. Paste the 3 snake PNGs in `SNAKE_NAMES` order (Shadow | Ralph | Anaconda) at x = `i * cell_width`, each resized to `(cell_width, cell_height)`. Use `.convert("RGB")` after pasting to flatten any PNG alpha onto white.
- Wrap each composite in `ImageTk.PhotoImage`. Retain refs on `dialog._species_images = []` (CRITICAL — Tk GC blanks unrooted PhotoImages).
- Each button's `command` sets `selected[0] = "turtles"` (or `"snakes"`) and calls `dialog.destroy()`.
- Center on screen using the same `update_idletasks` / `winfo_screenwidth` pattern as `get_user_track`.
- `dialog.grab_set()`, `dialog.wait_window()`, `return selected[0]`.
Use the first turtle name (`TURTLE_NAMES[0]` resolved via `TURTLE_IMAGES`) and `SNAKE_NAMES[i]` resolved via `SNAKE_IMAGES` for the source paths; route every path through `paths.resource_path()`. Imports already needed (`PIL.Image`, `ImageTk`, `paths.resource_path`) are present in the module. Do not modify `get_user_track` or `get_user_bet`.</action>
  <verify>python -c "import dialogs, inspect; assert callable(dialogs.get_user_species); sig = inspect.signature(dialogs.get_user_species); assert len(sig.parameters) == 0; print('ok')" && pytest -q</verify>
  <done>`get_user_species` is callable with no args. Module imports without error. `pytest -q` green. (Visual correctness of composites is verified in task 3 — manual smoke.)</done>
</task>

<task id="2" files="main.py, race.py" tdd="false">
  <action>Wire species end-to-end and fold in the two opportunistic Phase-2 actionables.
**main.py** (replace the body of the `while keep_playing` block):
```python
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

user_won = winning_turtle.pencolor() == racers[user_bet - 1]['o'].pencolor()
race.show_podium(racers, finish_order)
race.celebrate(winning_turtle, user_won)
race.announce_result(winning_turtle, user_bet, racers)
```
The hardcoded `"turtles"` literal at `main.py:28` and the no-arg `get_user_bet()` at `main.py:34` are replaced. `n = len(racers)` is computed once and reused (SIMPLIFICATION-2 S2.2).
**race.py** (DOCUMENTATION-2 actionable): locate `create_racers(species)` and add or extend its docstring to read approximately:
```
"""Create the field of racers for the given species.

Args:
    species: A key into constants.SPECIES (currently "turtles" or "snakes").

Returns:
    A list of racer dicts ordered by SPECIES[species]["names"]. Each dict has:
      - 'name':  str — the racer's name (matches SPECIES[species]["names"][i]).
      - 'color': str — pen/fill color (matches SPECIES[species]["colors"][i]).
      - 'o':     turtle.Turtle — the underlying turtle object.
"""
```
If `create_racers` already has a docstring, extend it rather than replacing — preserve any existing prose. Do not change `create_racers` behavior. Do not touch any other `race.py` function.</action>
  <verify>python -c "import ast, inspect, race; src = inspect.getsource(race.create_racers); assert 'species' in race.create_racers.__doc__ and 'name' in race.create_racers.__doc__, race.create_racers.__doc__; print('docstring ok')" && python -c "import ast; tree = ast.parse(open('main.py', encoding='utf-8').read()); names = [n.id for n in ast.walk(tree) if isinstance(n, ast.Name)]; assert 'species' in names; print('main.py uses species')" && pytest -q</verify>
  <done>`create_racers.__doc__` mentions both `species` and `name`. `main.py` references the local `species` variable. `pytest -q` green. The `n = len(racers)` hoist appears exactly once in `main.py` (no duplicate `len(racers)` calls in the loop body).</done>
</task>

<task id="3" files=".shipyard/phases/3/summaries/SUMMARY-2.1.md" tdd="false">
  <action>Run the manual smoke gate (CONTEXT-3 Decision 6) and write the phase summary.
**Smoke procedure** (`python main.py`):
1. Round 1: pick **Straight** track, pick **Turtles**, pick any turtle to bet on. Confirm: 2x2 turtle bet dialog appears, race runs with 4 turtles, podium shows 4 finishers, "play again?" prompt appears.
2. Round 2: pick **Yes** to play again, pick **Rectangular** track, pick **Snakes**, pick any snake. Confirm: species dialog showed both composites (2x2 turtles + 1x3 snakes), snake bet dialog showed Shadow | Ralph | Anaconda in a row, race runs with 3 racers (turtle-shaped placeholders — Phase 4 ships real snake shapes), podium shows 3 finishers.
3. Round 3: play again, pick **Spiral** track, pick **Turtles** again, confirm zero regression vs. Round 1 visuals (per CONTEXT-3 Decision 6: turtles mode must remain visually identical to current master).
4. Close the window via the "play again? No" path. Confirm clean exit (no Tk errors, no traceback).
Note any visual issues (composite alignment, dialog sizing, snake bet button sizing) — these are non-blocking unless they prevent reaching the podium.
Then write `.shipyard/phases/3/summaries/SUMMARY-2.1.md` containing:
- Tasks completed (PLAN-2.1 task 1, 2, 3).
- Commit SHAs for tasks 1 and 2 (this task is doc-only, may or may not commit depending on team convention — at minimum commit the SUMMARY file).
- pytest result (count + green/red).
- Smoke matrix outcome (table: round / track / species / pass-fail / notes).
- Phase-3 close-out statement: "Snakes mode reaches podium with turtle-shaped placeholders; Phase 4 wires real snake shapes." Or, if smoke failed, list the blocker explicitly so the next plan picks it up.
- Any deferred actionables to surface for Phase 4 (e.g., L_BASE tuning hints, dialog sizing tweaks).</action>
  <verify>powershell -Command "Test-Path .shipyard/phases/3/summaries/SUMMARY-2.1.md" && powershell -Command "(Get-Content .shipyard/phases/3/summaries/SUMMARY-2.1.md -Raw).Length -gt 500"</verify>
  <done>`SUMMARY-2.1.md` exists at `.shipyard/phases/3/summaries/SUMMARY-2.1.md`, is non-trivial (>500 chars), contains the smoke matrix and the explicit phase close-out statement. Smoke gate passed (or, if it failed, the blocker is recorded with enough detail for Phase 4 to act on).</done>
</task>

## Reminders for the builder

1. **Write `SUMMARY-2.1.md` to disk before returning** — it is the formal acceptance criterion of task 3. Phase 2 builders consistently skipped this; do not.
2. Per-task atomic commits. Tasks 1 and 2 each get their own commit; task 3 commits the SUMMARY file (and any uncommitted bookkeeping).
3. **File-specific `git add`** only. Never `git add .` or `-A`.
4. If the manual smoke (task 3) reveals a runtime crash (not just a visual nit), STOP, record the failure in `SUMMARY-2.1.md`, and do not mark the phase complete. The smoke is a gate, not a formality.
