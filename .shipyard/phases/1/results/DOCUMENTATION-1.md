# Documentation Report
**Phase:** 1 — Snake identity constants, SPECIES config, test coverage

## Verdict: MINOR_GAPS

Phase 1 is entirely internal (data structures + tests, no new UI or public callable API). Documentation impact is low. Two minor gaps are worth addressing before Phase 2/3 builders read CLAUDE.md for orientation.

---

## Summary

- API/Code docs: 1 file reviewed (`constants.py`)
- Architecture updates: 1 section in `CLAUDE.md` needs a future update (deferred to Phase 3)
- User-facing docs: None — no README at project root; `docs/` contains design artefacts only; no user-facing doc warranted at this phase

---

## API Documentation

### `constants.py`
- **File:** `constants.py`
- **Type:** Reference
- **Public interfaces added:** `SNAKE_NAMES`, `SNAKE_COLORS`, `SNAKE_LENGTHS`, `SNAKE_IMAGES`, `L_BASE`, `SPECIES`
- **Status:** Adequately documented via inline comments for Phase 1

The existing inline comment style (`# --- Snake racer identity ---`, positional-alignment notes) matches how `TURTLE_*` is documented. No additional docstrings are needed for plain list/dict constants.

One comment is potentially misleading to Phase 4 builders:

```python
SNAKE_LENGTHS = [6, 2, 5]   # positional with SNAKE_NAMES; 6:5:2 ratio is Shadow:Anaconda:Ralph by value
```

The ratio description says "Shadow:Anaconda:Ralph" but the list order is Shadow, Ralph, Anaconda (indices 0, 1, 2). A Phase 4 builder reading only the comment could infer the wrong order. Suggested replacement:

```python
SNAKE_LENGTHS = [6, 2, 5]   # positional with SNAKE_NAMES: Shadow=6, Ralph=2, Anaconda=5
```

This is the same change `test_snake_lengths_positional_values` already encodes as a dict — the comment should match the test's canonical form.

**Recommendation:** Update the comment in `constants.py` line 30 before Phase 2 begins. This is a one-line edit.

---

## Architecture Updates

### `CLAUDE.md` — "Turtle identity is positional" section
- **File:** `CLAUDE.md` lines 48–54
- **Type:** Explanation
- **Status:** Deferral recommended

The section heading and all pronouns still say "turtle." Phase 1 has introduced a parallel snake identity (same positional invariant, same `IMAGES`-keyed-by-name invariant, same 1-based bet indexing). CLAUDE.md will become actively misleading to Phase 2/3 implementers who read it expecting to learn the general pattern.

However, the full picture (species selector dialog, `get_user_bet(species)`, `create_racers`) does not exist yet. Updating CLAUDE.md now would describe a partial architecture. The right moment to update is **after Phase 3** (dialogs land), when the section can be rewritten once to cover both species coherently rather than patched twice.

**Recommendation:** Defer the CLAUDE.md architecture update to Phase 3. File a reminder in this report so the Phase 3 documenter picks it up.

Planned update scope (for Phase 3 documenter):
- Rename section from "Turtle identity is positional" to "Racer identity is positional (turtles and snakes)"
- Add a paragraph explaining `SPECIES` as the dispatch table keyed by `"turtles"` / `"snakes"`
- Note that `shape_drawer` is currently a string sentinel resolved in Phase 4
- Update the `user_bet` paragraph to say `racers[user_bet - 1]` (generic) rather than `turtles[user_bet - 1]`
- Update the bet dialog paragraph to mention `bet_layout` values (`"grid_2x2"` vs `"row_3"`)

---

## User Documentation

### README
- No README exists at project root. `docs/` contains internal design specs only.
- **Status:** No gap for Phase 1. A project-level README is appropriate at ship time (Phase 5), not before the feature is functional.

### `docs/` directory
- Contains `docs/superpowers/plans/` and `docs/superpowers/specs/` — internal design artefacts from a prior milestone. Not user-facing; no update warranted.

---

## Gaps

| Gap | File | Severity | When to fix |
|-----|------|----------|-------------|
| Misleading ratio description in `SNAKE_LENGTHS` comment | `constants.py` line 30 | Low | Before Phase 2 |
| CLAUDE.md architecture section covers turtles only | `CLAUDE.md` lines 47–54 | Low | After Phase 3 lands |
| No project README | (root) | Low | Phase 5 (ship time) |
