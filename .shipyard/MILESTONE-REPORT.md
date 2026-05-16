# Milestone Report: Snakes Racer Mode

**Completed:** 2026-05-16
**Phases:** 5/5 complete
**Total commits in milestone:** 45 (from `2e52386` to `caea4d5`)
**Tests:** 85/85 passing (54 baseline → 85; +31 across the milestone)
**Frozen build:** `dist/TurtleRace.exe` ~42.8 MB (PyInstaller exit 0)

## Phase Summaries

### Phase 1: Snake constants & `SPECIES` config foundation
- Landed `SNAKE_NAMES`, `SNAKE_COLORS` (Ralph `#E89F4F`), `SNAKE_LENGTHS = [6, 2, 5]`, `SNAKE_IMAGES`, `L_BASE`, `SPECIES` config dict in `constants.py`.
- Registered `assets/snakes/*.png` in `turtle_race.spec` `datas=`.
- Added 9 invariant tests; pytest 54 → 63.
- 5 build commits. Audit CLEAN.
- Cosmetic carry: cross-plan PNG capture in commit `2681e4b` (fixed via future builder discipline).

### Phase 2: Generalize `race.py` to N racers (turtle-only parity)
- Hard refactor: every `tracks.py` function takes `n` explicitly; `N_LANES` deleted.
- `race.py` renames: `turtles_list` → `racers`, `tortuga` → `racer`, `create_turtles` → `create_racers(species)`.
- Racer dicts now include `'name'` field.
- 22 new N=3/N=4 parametrized geometry tests; pytest 54 → 76.
- 5 build commits. Manual turtle-parity smoke confirmed by user.

### Phase 3: Species + snake-aware bet dialogs
- New `get_user_species()` modal dialog with composite turtle (2×2) and snake (1×3) button images via Pillow.
- `get_user_bet()` refactored to `get_user_bet(species)` with internal `if/elif` on `bet_layout`.
- `_TURTLE_GRID_LAYOUT` + `_SNAKE_ROW_LAYOUT` hoisted to module-level.
- `main.py` wired: `track → species → bet → race → podium`.
- Smoke hotfix: race-start log crashed on Ralph's hex color (pencolor tuple); fixed by reading `racer['color']`.
- pytest 76 → 77.
- CLAUDE.md rewritten to be species-agnostic.

### Phase 4: Snake in-race shape, length, head-finish detection
- `draw_turtle_shape` + `draw_snake_shape(t, length_units)` + `_SHAPE_DRAWERS` dispatch.
- `L_BASE` tuned 0.6 → 1.2; `SNAKE_STRETCH_WID = 0.5`.
- Custom snake polygon — iterated through 3 designs via the new `tools/snake_shape_options.py` comparison tool. Final: Option 5 smooth-wave polygon (length 20).
- Universal head-position finish detection (`progress[i] >= shared_distance - head_offset_progress[i]`).
- HEAD-at-start placement via `_back_pos` + `_head_offset_arc_for` helpers.
- Win-check refactored from `pencolor()` equality to identity comparison.
- 4 cleanup carry-overs cleared: `dialogs.py` stale imports, `get_user_species` docstring, `tracks.py:_build_spiral_legs` `n` rename, win-message tuple display.
- pytest 77 → 84 (+5 head-offset math tests).
- 16 commits total (10 plan-driven + 6 smoke iterations).

### Phase 5: Regression sweep, frozen build, ship polish
- `.gitignore` += `assets/midi/`.
- Anaconda head_offset test added.
- `create_racers` docstring extended with snake-branch Note.
- PROJECT.md Open Items strikethrough cleanup.
- CLAUDE.md 3 fixes (snake polygon length 20, podium width 3.0, HEAD-at-start helpers).
- `SHIP-NOTES.md` created.
- PyInstaller build-only verification: `dist/TurtleRace.exe` produced.
- pytest 84 → 85.

## Key Decisions

| Decision | Phase | Rationale |
|---|---|---|
| Composite species-dialog images | 3 | Single-character buttons understate species choice |
| Internal if/elif dispatch in `get_user_bet` | 3 | One cohesive function, both layouts visible |
| Universal head-position finish detection | 4 | Symmetric for turtles, fair for snakes; one code path |
| Progress-based head-offset (not position-based) | 4 | Folds into existing progress array; computed once per race |
| HEAD-at-start placement universal | 4 | Long snakes shouldn't straddle the start line |
| Snake polygon Option 5 (smooth-wave) | 4 | User-selected from 5 visualized candidates |
| L_BASE = 1.2, SNAKE_STRETCH_WID = 0.5 | 4 | Computed from lane-spacing math; smoke-tuned |
| `_SHAPE_UNIT_SIZE` per-shape dict | 4 | Snake polygon length differs from classic; dict avoids hardcoding |
| Identity-based win check (`is`) | 4 | Eliminates pre-existing pencolor() fragility |
| Spiral 3-lane tuning DEFERRED | 5 | No concrete visual complaint; ship; open follow-up if needed |
| `assets/midi/` left untracked | 5 | User's personal collection; not project scope |

## Documentation Status

- **CLAUDE.md:** rewritten in Phase 3, corrected in Phase 5 (3 fixes for shape dispatch / podium width / HEAD-at-start helpers). Reflects final code state.
- **SHIP-NOTES.md (NEW):** milestone summary at project root.
- **PROJECT.md:** Open Items annotated with RESOLVED/DEFERRED inline.
- **No `docs/` directory** for user-facing docs (out of scope; existing `docs/codebase/` from Shipyard map remains).

## Known Issues / Deferrals

- **Spiral 3-lane visual tuning:** deferred per CONTEXT-5; no concrete complaint received.
- **MIDI shuffle feature:** `assets/midi/` has 9 alternate `.mid` files; intentionally untracked. Possible future milestone.
- **Frozen-exe smoke:** PyInstaller build was verified to produce `dist/TurtleRace.exe`; the exe itself was not launched (per CONTEXT-5 build-only scope). Dev-build smoke covered runtime behavior.

## Audit Trail Across the Milestone

| Phase | Audit | Simplification | Documentation |
|---|---|---|---|
| 1 | CLEAN | LOW_PRIORITY (test duplication) | MINOR_GAPS |
| 2 | CLEAN | LOW_PRIORITY (carry-overs) | MINOR_GAPS |
| 3 | CLEAN | LOW_PRIORITY (stale imports) | MINOR_GAPS |
| 4 | CLEAN | LOW_PRIORITY (most addressed mid-phase) | MINOR_GAPS (CLAUDE.md updated) |
| 5 | CLEAN | NO_FINDINGS | NO_GAPS |

Zero critical security findings across the entire milestone.

## Metrics

- **Files created:** 13 source/asset files (3 snake PNGs, `tools/snake_shape_options.py`, `SHIP-NOTES.md`, `tests/test_race.py`, plus Shipyard `.shipyard/` infrastructure)
- **Files modified:** 7 source files (`constants.py`, `race.py`, `tracks.py`, `main.py`, `dialogs.py`, `tests/test_constants.py`, `tests/test_tracks.py`); `CLAUDE.md`, `.gitignore`, `turtle_race.spec`, `.shipyard/PROJECT.md`, `.shipyard/ROADMAP.md`
- **Total commits in milestone:** 45 (from `2e52386` to `caea4d5`)
- **Tests added:** +31 (54 → 85)
- **Test categories added:** snake constants invariants (9), N=3/N=4 geometry parametrized (22, replacing some implicit duplicates), head-offset math (3 ratio + 3 species)
- **Tags created:** 15 (per-phase pre-build, post-plan, post-build)

## Tools / Infrastructure Added

- `tools/snake_shape_options.py` — side-by-side polygon renderer; reusable for any future shape iteration.

## Acknowledgments

- Snake PNG art provided by user (Alejandro): `assets/snakes/{Shadow,Ralph,Anaconda}.png` (1024×1024 RGBA).
- Final snake polygon design (Option 5 smooth-wave) selected by user from the comparison tool.
- 6 smoke iterations in Phase 4 driven by user visual feedback on snake shape, length, podium scaling, and start-line placement.

## Ship Ready

All 5 phases COMPLETE. 85/85 tests pass. PyInstaller build clean. Zero critical findings. Milestone is ready for delivery.
