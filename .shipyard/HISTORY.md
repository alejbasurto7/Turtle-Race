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
- Ready for `/shipyard:build 3`- [2026-05-15T21:10:04Z] Session ended during build (may need /shipyard:resume)
- [2026-05-15T21:12:18Z] Session ended during build (may need /shipyard:resume)
- [2026-05-15T21:15:10Z] Session ended during build (may need /shipyard:resume)

## 2026-05-15 — Phase 3 built and verified

- Two sequential waves, one plan each (architect's third plan PLAN-2.2 dropped during planning as redundant with workflow reviewer step)
- Wave 1 PLAN-1.1: `SPECIES_DIALOG_IMAGE_SIZE` constant + `get_user_bet(species)` refactor with module-level layout constants. Verdict PASS, retries 0. Three atomic commits
- Wave 2 PLAN-2.1: `get_user_species()` with Pillow composite images (RGBA mode handling correct), `main.py` wire-up, opportunistic `n = len(racers)` hoist + `create_racers` docstring fix (SIMPLIFICATION-2 + DOCUMENTATION-2 carry-overs cleared). Verdict PASS, retries 0. Three atomic commits
- 6 build commits + 1 hotfix (`ded3720`, `b65bbc2`, `07e4183`, `c4f1271`, `75a62a2`, `9f56ace`, `be3e26a`)
- **Smoke-found bug & hotfix (`be3e26a`):** race-start diagnostic log crashed on Ralph's `#E89F4F` because `turtle.pencolor()` returns `(r,g,b)` tuple for hex strings, which `{color:<12}` format spec can't render. PROJECT.md Open Items had flagged this exact risk for Phase 4 verify; surfaced earlier than expected. Fixed by reading `racer['color']` (the configured string) instead of round-tripping through `pencolor()`.
- **CLAUDE.md updated** as part of Phase 3 wrap-up: rewrote "Turtle identity is positional" -> "Racer identity is positional, and species-dispatched"; added N-parameterized geometry section; updated Tk image-ref discipline (3 dialog lists); rewrote round-loop section; added hex pencolor caveat
- `pytest`: 77/77 throughout
- Audit: CLEAN. Simplification: LOW_PRIORITY (stale imports in dialogs.py, deferred to Phase 4). Documentation: MINOR_GAPS (`get_user_species()` docstring remaining)
- **Manual species-smoke: PASSED** — Alejandro confirmed both Turtles and Snakes reach podium after hotfix
- Untracked at end of phase: `assets/midi/` (9 .mid files Alejandro added; not part of Phase 3 scope)
- Ready for `/shipyard:plan 4`

## 2026-05-15 — Phase 4 planned

- CONTEXT-4.md locks 7 decisions: stretched `classic` shape first (polygon fallback on smoke), L_BASE=0.6, SNAKE_STRETCH_WID=0.5 (computed from lane spacing math), universal head-position finish detection (turtles too — symmetric), SHAPE_DRAWERS dispatch in race.py, cleanup scope = ALL 4 carry-forwards (dialogs.py imports, get_user_species docstring, race.py win-message fix, tracks.py _build_spiral_legs n shadow), spiral 3-lane geometry still deferred to Phase 5
- RESEARCH.md (extensive): classic polygon dimensions (10x9 at shapesize 1,1), run_race finish-check mechanism, head-offset progress-based approach, draw_turtle_shape extraction, _SHAPE_DRAWERS placement, win-message refactor strategy, 8 gotchas
- Researcher stalled mid-task — RESEARCH.md written inline from orchestrator analysis + researcher's partial findings
- 4 plans across 3 waves (architect collapsed Wave 2 from 2 plans to 1 — both touched race.py):
  - Wave 1 parallel: PLAN-1.1 (constants tune + tests) + PLAN-1.2 (dialogs.py imports + get_user_species docstring + tracks.py n rename)
  - Wave 2 sequential: PLAN-2.1 (race.py shape dispatch + win-check refactor across announce_result/celebrate/main.py)
  - Wave 3 sequential: PLAN-3.1 (universal head-offset progress adjustment + tests/test_race.py + manual smoke gate)
- Coverage verifier: PASS. Critique verifier stalled mid-task — CRITIQUE.md written inline. Verdict: READY with one minor caveat (shape_unit_size=9 hardcoded — calibrated for classic/snakes, approximated for turtle but symmetric race outcome means no behavior regression)
- Ready for `/shipyard:build 4`
