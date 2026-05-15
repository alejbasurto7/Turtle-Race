# Shipyard History

## 2026-05-15 — Project initialized

- Phase: 1
- Status: ready
- Message: Project initialized
- Config: interactive mode, per-task commits, detailed reviews, all quality gates enabled, default model routing, auto context tier

## 2026-05-15 — Codebase mapped

- 7 codebase docs written to `.shipyard/codebase/` (STACK, INTEGRATIONS, ARCHITECTURE, STRUCTURE, CONVENTIONS, TESTING, CONCERNS)
- 4 mapper agents dispatched in parallel; 2 stalled and were re-dispatched

## 2026-05-15 — Project definition captured + roadmap generated

- Milestone: **Snakes Racer Mode** — species selector (Turtles vs. Snakes) after track selection; 3 new snake racers (Shadow=6 units, Ralph=2 units, Anaconda=5 units) racing in 3 redistributed lanes
- Design refined via Socratic dialogue (asset strategy, lane layout, code generalization, in-race shape, round flow)
- PROJECT.md captures full spec; ROADMAP.md has 5 dependency-ordered phases
- Phase 1 ready to plan

## 2026-05-15 — Phase 1 planned

- CONTEXT-1.md locks 3 decisions: string-sentinel `shape_drawer`, Ralph hex `#E89F4F`, commit snake PNGs in Phase 1
- RESEARCH.md captures `constants.py` insertion point, spec syntax pattern, test style conventions, 7 gotchas
- 3 plans written: PLAN-1.1 (TDD red — 9 new tests), PLAN-2.1 (constants + SPECIES, parallel), PLAN-2.2 (spec edit + git-add PNGs, parallel)
- Coverage verifier: PASS. Feasibility critique: READY.
- Ready for `/shipyard:build 1`

## 2026-05-15 — Phase 1 built and verified

- Wave 1: PLAN-1.1 added 9 failing tests (TDD red). Builder: sonnet, verdict PASS, retries 0, task type: test
- Wave 2 (parallel): PLAN-2.1 (constants + SPECIES) + PLAN-2.2 (spec edit + git-add PNGs). Both verdict PASS, retries 0
- Net: 5 commits (`2e52386`, `a79867e`, `825a044`, `2681e4b`, `c7e89ed`). `pytest` 54/54 pass
- Audit: CLEAN. Simplification: LOW_PRIORITY (project_root duplication in tests, defer). Documentation: MINOR_GAPS (SNAKE_LENGTHS comment readability + CLAUDE.md deferral)
- **Cosmetic issue:** commit `2681e4b` (Plan 2.1) bundled the snake PNGs alongside `constants.py` — was supposed to be Plan 2.2's commit. Cause: broad `git add`. End state correct; no remediation. Phase 2+ dispatches should remind builders to use file-specific `git add`.
- Ready for `/shipyard:plan 2`

## 2026-05-15 — Phase 2 planned

- Discovered Phase 2 is larger than ROADMAP anticipated: `tracks.py` (395 lines, 14 N_LANES references) carries the bulk of the geometry that needs N-parameterization, not just `race.py`
- CONTEXT-2.md locks 7 decisions: hard refactor `tracks.py` with explicit `n`, delete `N_LANES`, extend `test_tracks.py` in-place for N=3, rename `tortuga`→`racer`, identifier renames per ROADMAP, zero-regression turtle parity gate, add `name` field to racer dicts
- RESEARCH.md (594 lines) maps every `N_LANES` reference, every `race.py` rename target, `main.py` call sites, `test_tracks.py` impact, `run_race`'s `shared_distance` analysis, geometry test design
- 3 plans (one per wave, sequential):
  - PLAN-1.1: `tracks.py` hard refactor + delete `N_LANES` + tests pass `n=4`
  - PLAN-2.1: N=3 geometry tests + `race.py` rename + `create_racers` reads SPECIES
  - PLAN-3.1: `main.py` wire-up + turtle-parity smoke
- Coverage verifier: PASS. Feasibility critique: READY.
- Builder prompts will explicitly require SUMMARY-W.P.md disk writes + file-specific `git add` (Phase 1 lessons learned)
- Ready for `/shipyard:build 2`
- [2026-05-15T19:33:03Z] Session ended during build (may need /shipyard:resume)

## 2026-05-15 — Phase 2 built and verified

- Three sequential waves, one plan each (no parallelism — each wave reshaped APIs the next wave depended on)
- Wave 1 PLAN-1.1: `tracks.py` hard refactor (12 functions take `n` explicitly, no defaults) + delete `N_LANES`. Verdict PASS, retries 0, task type: refactor. Single commit (cosmetic miss vs. per-task discipline)
- Wave 2 PLAN-2.1: 22 new N=3/N=4 parametrized geometry tests + `race.py` rename (`turtles_list`→`racers`, `tortuga`→`racer`, `create_turtles`→`create_racers(species)`) + racer dicts get `'name'` field. Verdict PASS, retries 0, task type: refactor+test. Two commits (per-task discipline restored)
- Wave 3 PLAN-3.1: `main.py` wire-up (10 call-site substitutions) + I2 docstring-comment fix from Wave 2 review. Verdict PASS pending human smoke. Two commits
- 5 build commits total (`b6a4a12`, `c3f5804`, `267559d`, `e036be0`, `a9cc82e`)
- `pytest`: 54 → 76 passed (22 new). Banned-identifier sweep: only `tests/test_tracks.py:38` (intentional prose comment)
- Audit: CLEAN (pure refactor, no surface). Simplification: LOW_PRIORITY (pre-existing `_build_spiral_legs` shadow + `main.py` repeats `len(racers)` × 3 — both deferred to Phase 3/4). Documentation: MINOR_GAPS (`create_racers` docstring incomplete — fix when wiring snakes)
- **Manual turtle-parity smoke: PASSED** — Alejandro confirmed 4-turtle race works correctly on all 3 tracks (straight, rectangular, spiral) with no visual regression
- Ready for `/shipyard:plan 3`

## 2026-05-15 — Phase 3 planned

- CONTEXT-3.md locks 7 decisions: composite turtle/snake images for species dialog (2×2 + 1×3 grids via Pillow), no dialog helper extraction (3 parallel implementations), `get_user_bet(species)` internal if/elif dispatch on `bet_layout`, snake bet 1×3 row at `BET_IMAGE_SIZE`, `main.py` species-dialog insertion with opportunistic `n` hoist, snake-mode end-state uses turtle-shape placeholders (Phase 4 wires shapes), `SPECIES_DIALOG_IMAGE_SIZE = 200`
- RESEARCH.md (565 lines): full `dialogs.py` map, refactor sketches, image-composition strategy, `main.py` change list, Tk image-retention gotchas, file-affected list
- 2 plans (one per wave, sequential):
  - PLAN-1.1: `constants.py` + `dialogs.py` foundation — `SPECIES_DIALOG_IMAGE_SIZE`, `get_user_bet(species)` refactor with `_TURTLE_GRID_LAYOUT` / `_SNAKE_ROW_LAYOUT` module-level constants
  - PLAN-2.1: `get_user_species()` + `main.py` wire-up + opportunistic `n = len(racers)` hoist + opportunistic `create_racers` docstring fix
- **PLAN-2.2 dropped during critique** — architect tried to formalize the post-build review pass as a "build" plan to force REVIEW disk writes. Redundant with the workflow's standard Step 4c reviewer dispatch. Its excellent review checklist will be embedded into the reviewer prompts I dispatch at build time.
- Coverage verifier: PASS. Feasibility critique: READY with one CAUTION (image-composition JPG/RGBA mode mismatch — builder prompt must require `img.convert("RGBA")` before paste)
- Ready for `/shipyard:build 3`