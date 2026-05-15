# Phase 1 — Discussion Capture

Decisions locked before planning dispatch. The architect, researcher, and builder must respect these.

## Decision 1 — `shape_drawer` strategy

**String sentinel in `SPECIES`, dispatched in `race.py`.**

```python
# constants.py
SPECIES = {
    "turtles": {..., "shape_drawer": "turtle"},
    "snakes":  {..., "shape_drawer": "snake"},
}
```

`race.create_racers()` resolves the string to the actual callable via a small dispatch table inside `race.py` (e.g., `SHAPE_DRAWERS = {"turtle": draw_turtle_shape, "snake": draw_snake_shape}`). The dispatch table can be empty in Phase 1 — Phase 4 wires real drawers in.

**Why:** Keeps `constants.py` import-clean (no `race.py` dependency, no circular import risk). `SPECIES` is feature-complete at the end of Phase 1 — no future schema edits.

**Phase 1 test:** Assert `SPECIES[s]["shape_drawer"]` is a string for each species and ∈ a valid set (e.g., `{"turtle", "snake"}`).

## Decision 2 — Ralph's color hex

**`"#E89F4F"`** — warm orange-tan. Stronger visual distinction from black Shadow and green Anaconda than the more desaturated `#D2A679`.

Set as `SNAKE_COLORS = ["black", "#E89F4F", "green"]` (positional with `SNAKE_NAMES = ["Shadow", "Ralph", "Anaconda"]`).

**Risk to verify in Phase 4:** confirm `turtle.color("#E89F4F")` and `turtle.pencolor()` round-trip cleanly — turtle module sometimes normalizes hex.

## Decision 3 — Snake PNG commit scope

**Commit `assets/snakes/Shadow.png`, `Ralph.png`, `Anaconda.png` as part of Phase 1.**

They're currently untracked. The Phase 1 task that adds `SNAKE_IMAGES` and the on-disk-exists test should also `git add` these files so:
- Fresh clones pass `pytest`
- PyInstaller's `datas=` glob has files to bundle
- The species dialog and snake bet dialog have real art from day one of Phase 3

**Note on size:** 3 × 1024×1024 RGBA PNGs. Acceptable for a local game repo; no LFS needed.
