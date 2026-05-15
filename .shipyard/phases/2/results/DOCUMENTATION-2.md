# Documentation Report
**Phase:** 2 — Generalize tracks.py API, refactor race.py, wire main.py

## Verdict: MINOR_GAPS

Phase 2 is a refactor phase with no new user-facing features. All changes are internal API
and identifier renames. Documentation impact is low. One code-level gap exists in
`create_racers`; all architecture-level updates are correctly deferred to Phase 3.

---

## Summary

- API/Code docs: 2 files reviewed (`race.py`, `tracks.py`)
- Architecture updates: 1 section deferred (CLAUDE.md — see below)
- User-facing docs: None — no README at project root; not warranted until Phase 5

---

## API Documentation

### `race.py` — `create_racers`
- **File:** `race.py` line 135
- **Type:** Reference
- **Status:** Docstring present but incomplete

The current docstring reads:

```
Create racer dicts for the given species.

Returns a list of {'name': ..., 'color': ..., 'o': Turtle(...)}.
```

Two non-obvious behaviors are undocumented:

1. **Key lookup.** `species` must be a key in `constants.SPECIES`. Passing an unknown
   string raises `KeyError` with no helpful message. A reader of `main.py` who sees
   `create_racers("turtles")` hardcoded needs to know where valid values come from.

2. **`name` field.** The returned dicts now include `'name'` (added in Phase 2).
   `create_turtles` did not include a name field. Code downstream uses
   `racers[i]['name']` for race logging — a new consumer of `race.py` would not know
   this field is guaranteed.

Suggested replacement for the docstring body (not the code):

```python
def create_racers(species: str):
    """Create racer dicts for the given species.

    `species` must be a key in ``constants.SPECIES`` (currently ``"turtles"``
    or ``"snakes"``). Raises ``KeyError`` for unknown values.

    Returns a list of dicts, one per racer, in the order defined by
    ``SPECIES[species]["names"]``:
        {'name': str, 'color': str, 'o': Turtle}

    The ``'o'`` turtle uses ``shape="turtle"`` regardless of species;
    shape dispatch is deferred to Phase 4.
    """
```

**Severity:** Low — only `main.py` currently calls this function, and its behavior is
visible in the code. However, Phase 3 will add a species dialog that calls
`create_racers` with a runtime-determined string; the docstring will matter then.

**Recommendation:** Update the docstring in `race.py` now (it is a one-block edit) rather
than deferring. This is the one Phase 2 finding that should not wait for Phase 3.

---

### `race.py` — `draw_start_line`, `draw_finish_line`, `draw_boundary_stones`
- **File:** `race.py` lines 77, 85, 127
- **Type:** Reference
- **Status:** No docstrings — acceptable

These are thin wrappers: each calls the matching `tracks.*` function and wraps it in
`tracer(0)` / `update()` / `tracer(1)`. The behavior is self-evident from the name and
body. No docstring needed.

---

### `tracks.py` — public functions with `n` parameter
- **File:** `tracks.py`
- **Type:** Reference
- **Status:** Module docstring updated in Phase 2 (SUMMARY-1.1 confirms); acceptable

The module docstring correctly states that every public function now takes `n` (lane
count) explicitly rather than reading `N_LANES`. The per-function signatures are
documented via type annotations and, where the geometry is non-trivial, inline docstrings
(`_rectangular_lane`, `_spiral_lane`, `_rectangular_finish_y`). No additional
documentation is needed for Phase 2.

The `_build_spiral_legs` loop variable name-shadow (`n` for leg index, same identifier
as lane count) was flagged in SUMMARY-1.1 as out of scope for Phase 2. The simplifier
should resolve it in a future pass; it is a readability issue, not a documentation gap.

---

## Architecture Updates

### `CLAUDE.md` — "Turtle identity is positional" section
- **File:** `CLAUDE.md` lines 47–54 (approximately)
- **Type:** Explanation
- **Status:** Deferral confirmed — carry forward to Phase 3

This deferral was recommended in DOCUMENTATION-1.md and remains correct. Phase 2
completed the code generalization (`create_racers`, species-agnostic `race.py`) but has
not yet added the species selector or snake shape rendering. CLAUDE.md updated now
would describe a half-complete architecture.

The `racers[user_bet - 1]` reference in CLAUDE.md ("Turtle identity is positional") is
now correct in the code (`main.py` line 38 uses `racers[user_bet - 1]`), but the
surrounding prose still says "turtles" throughout. Rewriting the section once — after
Phase 3 lands the species dialog — remains the right approach.

**Planned update scope for Phase 3 documenter** (carried from DOCUMENTATION-1.md):
- Rename section to "Racer identity is positional (turtles and snakes)"
- Add a paragraph on `SPECIES` as the dispatch table (`"turtles"` / `"snakes"`)
- Note `shape_drawer` as a string sentinel resolved in Phase 4
- Update `user_bet` paragraph to use `racers[user_bet - 1]` (generic)
- Update bet dialog paragraph to mention `bet_layout` values (`"grid_2x2"` vs `"row_3"`)
- Note that `create_racers("turtles")` in `main.py` is a Phase 3 placeholder

---

## User Documentation

### README
- No README at project root.
- **Status:** No gap for Phase 2. Appropriate at ship time (Phase 5).

---

## Gaps

| Gap | File | Severity | When to fix |
|-----|------|----------|-------------|
| `create_racers` docstring missing valid `species` values and `'name'` field guarantee | `race.py` line 135 | Low | Before Phase 3 (species dialog will call this with a runtime string) |
| `SNAKE_LENGTHS` comment ratio description still misleading (carried from Phase 1) | `constants.py` line 30 | Low | Before Phase 4 (builder will read SNAKE_LENGTHS) |
| CLAUDE.md architecture section covers turtles only | `CLAUDE.md` lines 47–54 | Low | After Phase 3 lands |
| No project README | (root) | Low | Phase 5 (ship time) |
