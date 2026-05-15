# Phase 2 — Discussion Capture

Decisions locked before research/architect/builder dispatch. The downstream agents must respect these.

## Decision 1 — `tracks.py` N parameterization: hard refactor, no default

Every function in `tracks.py` that currently reads `N_LANES` from constants must take an `n` (or `n_lanes`) parameter explicitly. **No default value.** Callers must pass `n` always.

Affected `tracks.py` references (14 from grep):
- Line 20: `from constants import N_LANES` — replace with no import (or keep `LANE_SPACING` etc., just remove `N_LANES`)
- Lines 57, 115, 165, 181, 215, 217, 268, 274, 294, 295, 302, 315, 377, 383 — every usage gets `n` from a function parameter

**Why hard refactor (not default-arg):** Forces all callers (`race.py`, `tests/test_tracks.py`) to pass `n` explicitly. Eliminates silent N=4 fallback that could hide bugs in the snake path. Slightly more invasive but no ambiguity.

## Decision 2 — Remove `N_LANES` from `constants.py`

Delete the line `N_LANES = 4` (currently at `constants.py:57`).

Pair with Decision 1: every caller passes `n` explicitly, so no constant is needed.

**Phase 2 Verification check:** `grep -n "N_LANES" .` returns zero results across the entire codebase.

**Side note:** the `# Track layout` comment block in `constants.py` keeps `TRACK_PADDING`, `LANE_SPACING`, `SPIRAL_STEP`, `TRACK_PREVIEW_W/H`. Only `N_LANES` goes.

## Decision 3 — `test_tracks.py`: extend in-place, parameterize existing tests for N=3 and N=4

Extend the existing file (do NOT add a separate `test_tracks_n_param.py`).

**Style trade-off:** CONVENTIONS.md notes existing tests avoid `pytest.parametrize`. For Phase 2, two approaches are acceptable — architect chooses based on what reads cleaner against the existing test bodies:

- **Approach A:** Use `pytest.mark.parametrize` over `(track, n)` tuples. Concise but breaks the no-parametrize convention.
- **Approach B:** Duplicate each existing test into `<test_name>_n3` and `<test_name>_n4` plain functions. Matches the existing style but adds line count.

If approach A is used, document the style break in `tests/test_tracks.py` with a short module-level comment. If approach B is used, name the new functions consistently.

Existing tests currently use `N_LANES` constant — they need updating regardless to pass `n` explicitly into the refactored `tracks.py` functions.

## Decision 4 — Rename `tortuga` → `racer` in `race.py`

The Spanish-mixed loop variable (`for tortuga in turtles_list`, `race.py:144`) gets renamed to `racer` for consistency with the broader `turtles_list` → `racers` rename. Touch any other `tortuga` occurrences in race.py during this phase.

**Why:** Phase 2 is already heavily touching race.py for the generalization. Renaming `tortuga` while we're in there keeps naming species-agnostic and coherent.

## Decision 5 — Identifier renames (confirmation of ROADMAP)

- `turtles_list` → `racers` everywhere (`race.py`, `main.py`)
- `create_turtles(color_list)` → `create_racers(species: str)` — reads `SPECIES[species]["names"]` and `SPECIES[species]["colors"]`
- `place_turtles_on_track(turtles_list, ...)` → `place_racers_on_track(racers, ...)`
- `turtle` parameter names inside race-loop iterators stay as `turtle` (they're `turtle.Turtle` instances — type-meaningful name)
- No back-compat aliases (per ROADMAP)

## Decision 6 — End-state behavior: turtles-only race must still work

At end of Phase 2, `python main.py` must still launch a 4-turtle race on each of the 3 tracks with **zero visual regression** vs. `master` pre-Phase-2. The species selector dialog (Phase 3) is NOT in scope for Phase 2 — `main.py` passes a hardcoded `species="turtles"` to `create_racers` and `get_user_bet` until Phase 3 lands.

## Decision 7 — `create_racers` data shape

`create_racers(species)` returns the **same dict shape** the existing code expects: `[{'o': turtle.Turtle(...), 'color': c}, ...]`. ROADMAP suggested extending the dict with `'name'` (`{'o': ..., 'color': ..., 'name': ...}`); do this in Phase 2 since Phase 3/4 will need it.

## Builder/agent reminders for Phase 2 dispatches

Phase 1 surfaced two recurring issues — bake these into every Phase 2 builder/reviewer prompt:

1. **Write the SUMMARY/REVIEW file before returning.** Phase 1 builders and reviewers consistently skipped the disk write. Make this an explicit acceptance criterion in the prompt.
2. **Use file-specific `git add`** (e.g., `git add race.py` not `git add .`). Phase 1's Plan 2.1 commit accidentally bundled Plan 2.2's PNGs because of a broad `git add`.
