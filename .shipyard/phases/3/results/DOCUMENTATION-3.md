# Documentation Report
**Phase:** 3 — Snakes Racer Mode (species selection + bet dispatch)

## Summary
- API/Code docs: 3 functions assessed across `dialogs.py` and `race.py`
- Architecture updates: CLAUDE.md "Turtle identity is positional" section is now stale — see recommendation below
- User-facing docs: none required (no end-user-visible text changed beyond in-app dialog titles)

---

## API Documentation

### `get_user_species()` (`dialogs.py`)
- **Type:** Reference
- **Public interfaces:** 1
- **Status:** Added with docstring — adequate

Docstring is present and accurate. It documents the return contract (`"turtles"` or `"snakes"` as a `constants.SPECIES` key) and the no-argument signature. No gap.

One minor omission: the docstring does not mention that the dialog is modal and blocks until the user makes a choice (matching the behaviour of `get_user_track()`). Not blocking — the inline comment `# force a choice` covers the mechanism — but a one-line note in the docstring would match the level of detail in `get_user_bet(species)`.

### `get_user_bet(species)` (`dialogs.py`)
- **Type:** Reference
- **Public interfaces:** 1 (signature changed)
- **Status:** Updated with docstring — complete

Docstring documents `species` arg, return type (1-based int), and `ValueError` on unrecognised `bet_layout`. The `Raises` section correctly targets `bet_layout` validation, not a bare `KeyError` on `species` itself (which would arrive before `bet_layout` is read). This is accurate.

Note: `TURTLE_NAMES` is still imported at line 8 but is no longer referenced in the module body. This is a dead import flagged as a Phase 4 cleanup item in SUMMARY-2.1. It does not affect correctness, but a future reader will wonder why it is there. The SUMMARY already tracks it.

### `create_racers(species)` (`race.py`)
- **Type:** Reference
- **Public interfaces:** 1 (docstring expanded)
- **Status:** Updated — complete

The expanded Args/Returns docstring now documents `species` as a `constants.SPECIES` key, `KeyError` on bad input, and all three racer dict keys (`'name'`, `'color'`, `'o'`). The inline comment `# Shape dispatch (shape_drawer sentinel) is Phase 4's concern.` correctly signals the deliberate stub. No gap.

### `get_user_track()` (`dialogs.py`)
- **Type:** Reference
- **Status:** No docstring — pre-existing gap, not introduced by Phase 3

`get_user_track()` has no docstring. This is not a Phase 3 regression, but it is now the only public dialog function without one. Worth adding before the codebase grows further.

---

## Module-Level Layout Constants

### `_TURTLE_GRID_LAYOUT` and `_SNAKE_ROW_LAYOUT` (`dialogs.py`, lines 13–28)
- **Type:** Reference (inline comments)
- **Status:** Adequately documented

Both constants have inline comments that explain the grid geometry (2x2 vs 1x3), the column order, and — for `_TURTLE_GRID_LAYOUT` — the correspondence to asset filename position hints. The ASCII art comment (`Leonardo (top-left)   Donatello (top-right)`) is particularly useful. No gap.

The `(row, col)` tuple convention (where `row=1` means "first data row below the header label", not row index 0) is not explained. This caused no bugs but could confuse a maintainer. A one-line comment like `# row is the tkinter grid row (1 = first data row, below the header label at row 0)` would close this.

---

## Architecture Updates

### CLAUDE.md — "Turtle identity is positional" section
- **Type:** Explanation
- **Status:** STALE — requires update

The section at `CLAUDE.md:47–54` is now materially misleading in three ways:

1. **"Turtle identity is positional"** — the heading frames racer identity as a turtle-only concept. The codebase now routes all racer identity through `SPECIES[species]`, making `TURTLE_NAMES[i]` / `TURTLE_COLORS[i]` a species-specific implementation detail, not the central invariant.

2. **`turtles[user_bet - 1]` is the user's pick** — the variable is now called `racers`, not `turtles` (since `main.py` Phase 3 commit).

3. **"`grid_layout` ([main.py:49](main.py#L49))"** — `grid_layout` was promoted to `_TURTLE_GRID_LAYOUT` in `dialogs.py` during Phase 3 Wave 1. The line reference is broken and the symbol name is wrong.

4. **Tk image references section** — still accurate, but it mentions only `dialog._bet_images`. Phase 3 added `dialog._species_images` using the same pattern. The section should reference both.

---

## CLAUDE.md Update Recommendation: Update NOW

**Recommendation: update CLAUDE.md now, not after Phase 4.**

**Reason:** The architectural change is complete. As of Phase 3, the species-dispatch path — `get_user_species()` → `create_racers(species)` → `get_user_bet(species)` — is fully wired end-to-end. CLAUDE.md currently tells any new developer three false things (wrong variable name, wrong symbol location, turtle-centric heading). Phase 4 adds shape drawing dispatch (`SHAPE_DRAWERS` in `race.py`), which is an additive extension to an already-documented system, not a restructuring of the identity model. It does not require deferring the identity section rewrite.

The "one comprehensive update" argument assumes Phase 4's changes to `race.py` are hard to separate from the identity model changes. They are not — shape dispatch is a single new dispatch table in one function. It can be documented in its own paragraph when Phase 4 lands, without requiring the identity section to remain stale in the interim.

**What to change in CLAUDE.md now:**

Section heading: rename "Turtle identity is positional" to "Racer identity and the SPECIES table".

Replace the four bullet points with:

- `constants.SPECIES` is the single source of truth for each species. It maps `"turtles"` and `"snakes"` to their `names`, `colors`, `images`, `bet_layout`, and `shape_drawer`.
- Within a species, identity is still positional: `SPECIES[species]["names"][i]` and `SPECIES[species]["colors"][i]` describe the same racer.
- `user_bet` is 1-based; `racers[user_bet - 1]` is the user's pick. The bet dialog computes this with `SPECIES[species]["names"].index(name) + 1`.
- The bet dialog layout is decoupled from name order — `_TURTLE_GRID_LAYOUT` and `_SNAKE_ROW_LAYOUT` in `dialogs.py` encode the per-species grid geometry and match asset filename position hints.

Also update the Tk image references paragraph to mention `dialog._species_images` alongside `dialog._bet_images`.

The `tkinter` bullet in the Architecture section still says "picks a turtle" — update to "picks a racer".

---

## Gaps

| Gap | Severity | File | Notes |
|-----|----------|------|-------|
| CLAUDE.md "Turtle identity is positional" stale | High | CLAUDE.md:47–54 | Three factual errors; misleads new developers about variable names and symbol locations |
| `get_user_track()` missing docstring | Low | dialogs.py:137 | Pre-existing; now the only undocumented public dialog function |
| `_TURTLE_GRID_LAYOUT` row-index convention unexplained | Low | dialogs.py:13–21 | `row=1` means tkinter grid row 1, not list index 0; non-obvious to a first reader |
| `get_user_species()` docstring omits modal/blocking behaviour | Low | dialogs.py:195 | Minor; covered by inline comment but inconsistent with `get_user_bet` docstring level |
| Dead `TURTLE_NAMES` import | Low | dialogs.py:8 | Tracked in SUMMARY-2.1 as Phase 4 cleanup; no action needed now |
