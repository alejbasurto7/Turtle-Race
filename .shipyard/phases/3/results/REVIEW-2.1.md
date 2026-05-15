---
phase: 3-snake-species
plan: 2.1
wave: 2
reviewer: claude-sonnet-4-6
verdict: PASS
---

# REVIEW-2.1 — Phase 3 Wave 2

## Pre-Check: Prior Findings

REVIEW-1.1 recorded one Minor finding: `SNAKE_NAMES` not imported in `dialogs.py` despite the plan's Task 2 action requiring it. Wave 2 touched `dialogs.py` but did not add the import. The finding recurs (see Minor section below). No critical findings from prior reviews to re-check.

---

## Stage 1: Spec Compliance

**Verdict: PASS**

All three tasks are correctly implemented. Two noted deviations: one is a beneficial upgrade over the plan's literal spec (RGBA vs RGB composites, blessed by CRITIQUE.md), and one is a recurring stale-import issue.

---

### Task 1: `get_user_species()` in `dialogs.py`

**Status: PASS**

**Evidence:**

- `dialogs.py:194` — `def get_user_species():` present, no parameters. Callable check satisfied.
- `dialogs.py:202-205` — `Toplevel()`, `title("Choose Your Racers")`, `resizable(False, False)`, `protocol("WM_DELETE_WINDOW", lambda: None)`. Modal pattern parity with `get_user_track` confirmed.
- `dialogs.py:207-212` — header `Label` with text `"Which species will race?"`, font `("Arial", 12, "bold")`, `pady=12`, `columnspan=2`, `row=0`. Matches spec exactly.
- `dialogs.py:215` — `dialog._species_images = []` initialized before any `PhotoImage` is created. Both `turtle_photo` (line 233) and `snake_photo` (line 260) appended immediately after creation. GC-retention discipline confirmed.
- `dialogs.py:217-222` — `make_cb` closure pattern used; `"turtles"` and `"snakes"` (lowercase) are the values set in `selected[0]`. Return values match `SPECIES` dict keys.
- `dialogs.py:236-245` — Turtles button: `compound="top"`, `text="Turtles"` (capitalized display label), `command=make_cb("turtles")`, `grid(row=1, column=0)`. Correct.
- `dialogs.py:263-272` — Snakes button: `compound="top"`, `text="Snakes"`, `command=make_cb("snakes")`, `grid(row=1, column=1)`. Correct.
- `dialogs.py:275-279` — centering via `update_idletasks` / `winfo_screenwidth` / `geometry`. Identical pattern to `get_user_track`.
- `dialogs.py:281-282` — `grab_set()` then `wait_window()`. Modal correctness preserved.
- `dialogs.py:284` — `return selected[0]`.

**Image composition correctness (THE BIG CHECK):**

- `dialogs.py:225` — `Image.new("RGBA", (SPECIES_DIALOG_IMAGE_SIZE, SPECIES_DIALOG_IMAGE_SIZE), (255, 255, 255, 0))`. The plan specified `"RGB"` but the CRITIQUE.md explicitly recommended `"RGBA"` to handle the JPG/PNG mode mismatch. The builder followed the CRITIQUE over the plan's literal spec. This is the correct choice — pasting an RGBA source onto an RGB destination without an alpha mask corrupts the snake PNGs' transparent areas into black.
- `dialogs.py:228` — `img.convert("RGBA")` called before every paste. Both turtle JPGs and snake PNGs are explicitly up-converted. No bare RGB→RGBA coercion gap.
- `dialogs.py:232` and `dialogs.py:256` — `composite.paste(img, (x, y), img)`. Third argument (the alpha mask) is the image itself. Correct — PIL uses the alpha channel of the mask argument to blend.
- Snake composite: `Image.new("RGBA", (cell_w * 3, cell_h), ...)` at `dialogs.py:250`, then `snake_composite.resize((SPECIES_DIALOG_IMAGE_SIZE, SPECIES_DIALOG_IMAGE_SIZE), Image.LANCZOS)` at `dialogs.py:257-259`. Final composite is 200×200. Correct.
- Turtles composite coordinate math: `x = col * cell`, `y = (row - 1) * cell` at `dialogs.py:230-231`. Leonardo (1,0)→(0,0) top-left, Donatello (1,1)→(100,0) top-right, Raphael (2,0)→(0,100) bottom-left, Michaelangelo (2,1)→(100,100) bottom-right. Matches spec's `_TURTLE_GRID_LAYOUT` positional order.
- Snakes composite: `x = col * cell_w` at `dialogs.py:255`. Shadow col=0→x=0, Ralph col=1→x=66, Anaconda col=2→x=132. Matches `SNAKE_NAMES` order.

**No issues.** The RGBA upgrade over the plan's "RGB" spec is a net quality improvement blessed by CRITIQUE.md and produces correct behavior.

---

### Task 2: `main.py` wire-up + `create_racers` docstring in `race.py`

**Status: PASS**

**Evidence:**

- `main.py:28` — `species = dialogs.get_user_species()` inserted between `get_user_track()` (line 27) and `create_racers(species)` (line 29). Insertion position matches spec exactly.
- `main.py:29` — `race.create_racers(species)`. Hardcoded `"turtles"` literal is gone.
- `main.py:36` — `dialogs.get_user_bet(species)`. Runtime breakage from Wave 1 is fixed.
- `main.py:30` — `n = len(racers)` hoisted once. Lines 31, 33, 34 each use `n` for `draw_boundary_stones`, `draw_start_line`, `draw_finish_line`. No residual `len(racers)` call in the loop body. SIMPLIFICATION-2 S2.2 confirmed.
- `main.py:40` — `user_won = winning_turtle.pencolor() == racers[user_bet - 1]['o'].pencolor()`. Matches the plan's specified body verbatim.
- `race.py:135-151` — `create_racers` docstring present: Args section mentions `species` as a key into `constants.SPECIES`, notes `KeyError` on unrecognised value; Returns section documents `'name'`, `'color'`, `'o'` dict keys. Both `species` and `name` appear in `__doc__`. Verification command criteria satisfied.

---

### Task 3: SUMMARY-2.1.md + smoke gate

**Status: PASS (with acknowledged PENDING)**

**Evidence:**

- `.shipyard/phases/3/results/SUMMARY-2.1.md` exists and is non-trivial (>500 chars confirmed by reading: the file is ~3,000 chars).
- SUMMARY contains: tasks completed table, commit SHAs for tasks 1 and 2, pytest results (77/77 across all stages), smoke matrix (4 rows with PENDING status), and the required phase close-out statement: "Snakes mode reaches podium with turtle-shaped placeholders; Phase 4 wires real snake shapes."
- Stray `.shipyard/phases/3/summaries/` directory: `Glob` search returns no matches — directory has been removed. No traces remain.
- The PENDING status on all smoke rows is documented explicitly in the SUMMARY ("PENDING_HUMAN_VERIFICATION"). This is the expected pattern per the plan (autonomous agents have no display for Tk rendering verification).

---

## Stage 2: Code Quality

### Critical

None.

---

### Important

- **`SNAKE_NAMES` still not imported in `dialogs.py`** (`dialogs.py:7-10`) — recurring Minor from REVIEW-1.1
  - This was flagged in REVIEW-1.1 as a spec deviation from PLAN-1.1's Task 2 action. Wave 2 touched `dialogs.py` extensively (added 93 lines) but did not add the import. The comment on `dialogs.py:23` explicitly references `SNAKE_NAMES` by name, making the missing import a documentation/intent mismatch.
  - Runtime impact: zero. `_SNAKE_ROW_LAYOUT` hardcodes names as string literals.
  - Remediation: Add `SNAKE_NAMES` to the import block at `dialogs.py:7-10`, making it `from constants import (TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE, SNAKE_NAMES, SNAKE_IMAGES, SPECIES, SPECIES_DIALOG_IMAGE_SIZE,)`. Defer to Phase 4 when `dialogs.py` is next touched.

- **`TURTLE_NAMES` and `TURTLE_IMAGES` are imported but unused** (`dialogs.py:8`)
  - After the Phase 3 Wave 1 refactor, all turtle-related lookups in `get_user_bet` now go through `SPECIES[species]["names"]` and `SPECIES[species]["images"]`. `TURTLE_NAMES` and `TURTLE_IMAGES` are no longer referenced anywhere in `dialogs.py`.
  - This is a stale import that linters (flake8 `F401`) will flag.
  - The SUMMARY correctly identifies this under "Deferred Actionables for Phase 4."
  - Remediation: Remove `TURTLE_NAMES` and `TURTLE_IMAGES` from the import at `dialogs.py:8` in Phase 4 when `dialogs.py` is next modified.

---

### Suggestions

- **`show_podium` guard `len(finish_order) < 3` silently skips the podium for 3-racer races only if fewer than 3 finish** (`race.py:263`). For exactly 3 snakes, `len(finish_order) == 3` so the guard passes correctly. However, if a race ever produces fewer than 3 finishers (e.g., due to a future early-exit bug), the podium silently returns without any indication. This is pre-existing behavior and outside Phase 3 scope — note for Phase 4.
  - Remediation: Out of scope for Phase 3. Consider adding a fallback for partial podiums in Phase 4.

- **`main.py:40` win-check uses `pencolor()` comparison** — fragile if two racers share the same color (`race.py:372` is the same pattern). Pre-existing issue from Phase 2 REVIEW carry-over. Not introduced by this wave.
  - Remediation: Out of scope for Phase 3. Phase 4 should add a `'name'`-based identity check.

---

## Carry-over to Phase 4

The following items were observed in scope but are explicitly deferred beyond Phase 3:

| Item | Location | Detail |
|------|----------|---------|
| Real snake shapes | `race.py:156` | `create_racers` uses `shape="turtle"` for all species. Phase 4 reads `SPECIES[species]["shape_drawer"]` and calls `draw_snake_shape(t, length_units)` (or registers a custom turtle shape). |
| `L_BASE` placeholder | `constants.py:37` | `L_BASE = 1.0` is a stub for snake body-length scaling. Phase 4 tunes this value visually. |
| `_build_spiral_legs` `n` shadow | `tracks.py` (Phase 1/2 carry) | Inner variable `n` shadowing the outer `n` parameter. Noted in Phase 1 review; not introduced by Phase 3. |
| `main.py:40` `pencolor()` win-check fragility | `main.py:40`, `race.py:372` | Identity check by color breaks if two racers share a color. Should use `racer['name']` comparison instead. |
| Head-position finish detection | `race.py` | Current finish detection uses progress fraction; Phase 4 to implement head-position detection for visual accuracy. |
| `TURTLE_NAMES` + `TURTLE_IMAGES` stale imports | `dialogs.py:8` | Remove when next touching `dialogs.py` in Phase 4. |
| `SNAKE_NAMES` missing import | `dialogs.py:7-10` | Add alongside the stale-import cleanup. |
| CLAUDE.md "Turtle identity is positional" section | `CLAUDE.md` | Needs comprehensive rewrite to reflect species-agnostic `SPECIES` dict architecture. Deferred since Phase 2. |
| Snake composite background tone | `dialogs.py:250` | PNG transparent areas render as dialog background gray. If visually unacceptable, pre-fill with `(240, 240, 240, 255)` to match Tk default. Non-blocking per SUMMARY. |

---

## Summary

**Verdict: PASS — APPROVE**

All three tasks are correctly implemented and match the spec. The single spec deviation — using `Image.new("RGBA", ...)` instead of the plan's `"RGB"` — is a justified quality upgrade explicitly recommended by CRITIQUE.md and produces the correct behavior for mixed JPG/PNG source assets. The smoke gate remains PENDING human verification as expected. No critical issues.

Critical: 0 | Important: 2 | Suggestions: 2
