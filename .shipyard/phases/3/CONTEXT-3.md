# Phase 3 — Discussion Capture

Decisions locked before research/architect/builder dispatch.

## Decision 1 — Species dialog button images: COMPOSITE

The two buttons in the new `get_user_species()` dialog display **composite** images — all 4 turtles for the Turtles button, all 3 snakes for the Snakes button.

**Rationale:** Single-character buttons (one Leonardo, one Shadow) understate what the user is choosing between. Composites communicate "you're picking a species, with these specific characters."

**Composite approach:**
- Use existing **Pillow** (already a dependency) to compose images at dialog-open time. No pre-rendered files committed; composition is in-memory.
- **Turtles composite:** 2×2 grid of the 4 turtle JPGs in the same positional order as the bet dialog grid (Leonardo top-left, Donatello top-right, Raphael bottom-left, Michelangelo bottom-right). Mirrors the `grid_layout` in `dialogs.get_user_bet`.
- **Snakes composite:** 1×3 row of the 3 snake PNGs in the same order as `SNAKE_NAMES` (Shadow | Ralph | Anaconda).
- Each composite resized to the target button size after composition.

**Implementation hint for the architect:** add a small private helper in `dialogs.py` (e.g., `_compose_grid(image_paths, rows, cols, cell_size)`) returning a `PIL.Image`. Two callers from `get_user_species`. Alternatively, hardcode the two composites inline if the helper feels over-engineered for two call sites — architect's call.

**New constant in `constants.py`:** `SPECIES_DIALOG_IMAGE_SIZE = 200` (larger than `BET_IMAGE_SIZE = 140` since the species choice should be visually impactful — the user is picking a whole game mode, not just a single racer).

## Decision 2 — Dialog refactor: keep 3 parallel implementations

Do NOT extract a `_modal_image_button_dialog(...)` helper. Each of `get_user_track`, `get_user_bet`, `get_user_species` stays as its own function with the full Tk boilerplate (Toplevel, grab_set, wait_window, centering, image-ref retention).

**Rationale:** The dialogs differ in number of buttons, layout (grid vs. row), label text, and image-source logic enough that a helper would either need many parameters or limit each caller's flexibility. Phase 3 is medium-risk (Tk modal correctness); the smaller the change, the safer.

**Style:** Keep the new `get_user_species` consistent with `get_user_track`'s structure — it's the closest sibling (single horizontal row of buttons).

## Decision 3 — `get_user_bet(species)` dispatch: internal branching

`get_user_bet(species)` is **one function** with if/elif on `SPECIES[species]["bet_layout"]`:

```python
def get_user_bet(species):
    bet_layout = SPECIES[species]["bet_layout"]
    if bet_layout == "grid_2x2":
        # existing turtle 2x2 grid logic, parameterized by species
    elif bet_layout == "row_3":
        # new snake row-of-3 logic
    else:
        raise ValueError(f"Unknown bet_layout: {bet_layout}")
```

**Rationale:** Both layouts visible side-by-side in the same function. Easier to spot inconsistencies. Total function length stays under ~100 lines.

**Bet-index convention (preserved):** 1-based index into `SPECIES[species]["names"]` — matches turtle convention. For snakes: bet `1` = Shadow, `2` = Ralph, `3` = Anaconda.

**Existing turtle `grid_layout` constant in `dialogs.py`:** keep as `_TURTLE_GRID_LAYOUT` module-level (move out of the function body so the snake row layout can sit beside it as `_SNAKE_ROW_LAYOUT`). This keeps the if/elif body short.

## Decision 4 — Snake bet dialog layout

- 1 row × 3 columns of buttons
- Each button: snake PNG resized to `BET_IMAGE_SIZE` (= 140), with the snake's name as the button label below the image
- Order: `SNAKE_NAMES` order (Shadow | Ralph | Anaconda)
- Same modal/centering pattern as `get_user_bet` for turtles

## Decision 5 — `main.py` changes

Insert `species = dialogs.get_user_species()` between `get_user_track()` (line 27 today) and `create_racers(...)` (line 28 today). Pass `species` into `create_racers(species)` and `get_user_bet(species)` — replacing the hardcoded `"turtles"` literal.

Updated `main.py` call order:
```python
track_name = dialogs.get_user_track()
species    = dialogs.get_user_species()       # NEW
race.draw_boundary_stones(track_name, ...)    # but this needs n now...
racers     = race.create_racers(species)
n          = len(racers)                      # opportunistic SIMPLIFICATION-2 fix (S2.2)
race.place_racers_on_track(racers, track_name)
race.draw_start_line(track_name, n)
race.draw_finish_line(track_name, n)
race.draw_boundary_stones(track_name, n)      # ↑ moved AFTER create_racers (G7 already addressed in Phase 2)
user_bet   = dialogs.get_user_bet(species)    # was get_user_bet()
```

**Optional opportunistic cleanups (architect's call whether to fold in):**
- Hoist `n = len(racers)` once (SIMPLIFICATION-2 S2.2 from Phase 2 — recommended since we're already touching `main.py`)
- Add docstring to `create_racers(species)` mentioning `species` is a `SPECIES` key and returned dicts include `'name'` (DOCUMENTATION-2 actionable from Phase 3)

## Decision 6 — Phase 3 end-state: snake mode reaches the podium

End of Phase 3, picking **Snakes** must:
1. Show the snake bet dialog
2. Run a 3-racer race using **turtle-shaped placeholders** (snake shape is Phase 4's job)
3. Reach the podium with 3 finishers
4. Loop back via "play again"

Picking **Turtles** must remain visually identical to current master (zero regression).

This is the manual-smoke gate for Phase 3 — same as Phase 2's parity gate, expanded to cover both species.

## Decision 7 — `tests/test_constants.py` impact

Adding `SPECIES_DIALOG_IMAGE_SIZE = 200` to `constants.py` likely warrants a tiny test (mirror `test_bet_image_size_is_positive_int`). Architect to decide whether to add it; non-blocking either way.

## Builder/agent reminders for Phase 3

Carrying forward from Phase 2's lessons (still relevant):
1. **Write SUMMARY-W.P.md to disk before returning.** Hard acceptance criterion.
2. **File-specific `git add`.** No `git add .` or `git add -A`.
3. **Per-task atomic commits.** Phase 2 mostly improved on this — keep the discipline.
4. **Reviewers must write REVIEW-W.P.md to disk** — Phase 2 reviewers consistently skipped this. Make it explicit in their prompt.
