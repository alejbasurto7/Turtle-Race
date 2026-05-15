# Review: Plan 2.1

## Verdict: PASS

Both tasks correctly implemented. Two "important" findings: I1 is the planned/scoped runtime breakage of `main.py` (Wave 3 fixes); I2 is a minor style miss to fold into Wave 3.

## Findings

### Critical

None.

### Important

- **I1 — `main.py` calls removed APIs and is broken at runtime; `draw_*` calls miss the new `n` argument.** *This is the planned, scoped runtime breakage* documented in PLAN-2.1: "main.py is NOT touched here — it will be temporarily broken (calls `create_turtles` which no longer exists). That is intentional and resolved in Plan 3.1." Broken surface = exactly the 7 call sites enumerated in RESEARCH.md Section 3, no expansion. Remediation: execute Plan 3.1.
- **I2 — `# Shape dispatch (shape_drawer sentinel) is Phase 4's concern.` placed inside `create_racers` docstring body, not as a `#` code comment.** Functionally inert (lives as a string), but reads awkwardly and breaks docstring norms. Remediation in Wave 3: move outside the docstring as an actual `#` comment in the function body.

### Minor / Suggestions

- **S2 — pre-existing `_build_spiral_legs` loop variable `n` shadow** (`tracks.py:195`, `for n in range(max_legs):`) still unaddressed. Pre-existing from before Phase 2; out of scope here. Re-flag for a future cleanup pass.
- **S1 — per-task commits improved over Wave 1** — 2 commits this time (`c3f5804` tests, `267559d` race.py refactor), a marked improvement over Wave 1's single commit. SUMMARY-2.1.md being bundled into the refactor commit is acceptable (it's an artifact, not source).
- **CONTEXT-2.md style-break note format:** builder used a docstring at `tests/test_tracks.py:1-5` instead of a `#` comment. Functionally equivalent for discoverability; acceptable per builder's documented Decision 1.

### Positive

- **Test surface complete:** all 6 (track, N) pairs from RESEARCH.md covered with meaningful assertions (distinct positions, within-bounds, symmetric spacing for straight, spiral-arc-end at origin, finish-line segment counts). 22 new invocations across 5 parametrized test functions, exactly matching the plan.
- **`race.py` refactor exhaustive:**
  - All 14 `turtles_list` sites replaced with `racers`
  - All 4 `tortuga` sites replaced with `racer`
  - `create_turtles` → `create_racers(species)` reads `SPECIES[species]["names"]` + `["colors"]`
  - Racer dict has `'name'`, `'color'`, `'o'` (per CONTEXT-2.md Decision 7)
  - Both `TURTLE_NAMES` logging sites now use `racers[i]['name']` — no fallback conditional
  - All 5 `tracks.*` call sites pass `n` (= `len(racers)`)
  - `TURTLE_NAMES` import dropped; `SPECIES` imported
  - No back-compat aliases (zero grep matches for old names in `race.py`)
- **`run_race`'s `shared_distance`** (lines 180-181) uses `sum(lane_lengths) / len(lane_lengths)` — N-safe (as RESEARCH.md Section 2 predicted).
- **Wave 3 API ready:** `race.create_racers(species)`, `race.place_racers_on_track(racers, track_name)`, `race.draw_*(track_name, n)`, `race.run_race(racers, track_name, user_bet)`, `race.show_podium(racers, finish_order)`, `race.announce_result(winner, user_bet, racers)` — all signatures match what PLAN-3.1 expects.
- **Test suite green:** 76/76 pass (54 from baseline + 22 new geometry tests).

## Wave 2 Gate: OPEN — Wave 3 cleared. I2 (docstring-comment fix) should be folded into Wave 3's first commit.

Critical: 0 | Important: 2 | Minor: 3
