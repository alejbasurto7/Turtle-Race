---
phase: snakes-racer-mode
plan: 3.1
wave: 3
dependencies: [2.1]
must_haves:
  - Universal head-position finish detection in run_race (per RESEARCH.md §2 Approach B, progress-based)
  - head_offset_progress computed ONCE per racer at race start (RESEARCH.md §10 gotcha 5)
  - Pure-trig unit tests for head-offset math (new tests/test_race.py)
  - Manual smoke gate: both species run end-to-end on all 3 tracks, snakes look snake-shaped with 6:5:2 length ratio
  - Turtle mode visually indistinguishable from Phase 3 baseline (zero regression)
  - pytest stays green
files_touched:
  - race.py
  - tests/test_race.py
tdd: true
risk: high
---

# PLAN-3.1 — Head-position finish detection + manual smoke gate

## Context

The final piece of Phase 4. Per CONTEXT-4 Decision 3 and RESEARCH.md §2, finish detection becomes universal (both species). RESEARCH.md §2 Approach B is the recommended implementation:

```
head_offset_arc = (stretch_len * shape_unit_size / 2)
head_offset_progress = head_offset_arc * (shared_distance / lane_lengths[i])
# Finish when progress[i] >= shared_distance - head_offset_progress
```

Computed once per racer at race start (RESEARCH.md §10 gotcha 5 — shapes do not change mid-race; storing in a parallel array next to `progress[]` is simpler than re-computing per tick).

`shape_unit_size` for the `classic` shape is 9 units along heading per RESEARCH.md §3. For the `turtle` shape it's also small and symmetric, so applying head-offset to turtles is a no-op behaviorally (CONTEXT-4 Decision 3).

This plan is also the **manual-smoke gate** for the entire Phase 4 milestone, per CONTEXT-4 Decision 6 and ROADMAP Phase 4 success criteria. Snakes mode must complete a full round on all 3 tracks; turtle mode must look unchanged.

If stretched-`classic` doesn't read as a snake at race scale during smoke, CONTEXT-4 Decision 1's polygon-fallback escalation kicks in (smoke-driven). Document the call in race.py as a comment.

## Tasks

<task id="1" files="tests/test_race.py" tdd="true">
  <action>Create a new file tests/test_race.py with pure-math unit tests for the head-offset conversion. Tests do NOT import race.py (which would pull in turtle screen setup) — instead they implement the formula inline as a tiny test helper, then assert the math. Cover: (a) `head_offset_progress = head_offset_arc * (shared_distance / lane_length)` at three lane-length scenarios: lane_length == shared_distance (ratio 1.0 → head_offset_progress == head_offset_arc); lane_length > shared_distance (ratio < 1, progress offset smaller); lane_length < shared_distance (ratio > 1, progress offset larger). (b) Concrete plug-in: for Shadow with `stretch_len = 3.6` (L_BASE=0.6 × length=6) and `shape_unit_size = 9`, `head_offset_arc = 9 * 3.6 / 2 = 16.2`. Assert that value. (c) For Ralph with `stretch_len = 1.2`, `head_offset_arc = 5.4`. Assert that value. (d) For turtles with `stretch_len = 1.0` and the turtle-classic effective length, document via comment that the head-offset is small enough that the behavior is unchanged — no assertion required (smoke handles it). Aim for 3-5 short asserts total.</action>
  <verify>pytest tests/test_race.py -v</verify>
  <done>The new test file is created. pytest tests/test_race.py runs and ALL of the new tests PASS (since they test the math formula directly, they're green from the moment they're written — this is TDD-as-spec-lock, not red-then-green). Full pytest is green.</done>
</task>

<task id="2" files="race.py" tdd="false">
  <action>In race.py `run_race` (around lines 175-256, per RESEARCH.md §2): before the race loop (after `place_racers_on_track`, around the `progress = [0.0] * len(racers)` line, ~line 194), compute a parallel array `head_offset_progress = []` of the same length as `racers`. For each racer i: read `stretch_len = racers[i]['o'].shapesize()[1]` (turtle.shapesize() returns the tuple `(stretch_wid, stretch_len, outline)`; index 1 is stretch_len); compute `head_offset_arc = 9 * stretch_len / 2` with an inline comment citing RESEARCH.md §3 (shape_unit_size = 9 along heading for both classic and turtle); compute `head_offset_progress.append(head_offset_arc * (shared_distance / lane_lengths[i]))`. Then modify the finish check (around line 228): the existing `if progress[i] >= shared_distance:` becomes `if progress[i] >= shared_distance - head_offset_progress[i]:`. Also update the progress-clamp on line 222 so racers don't overrun: change `progress[i] = min(progress[i] + step, shared_distance)` to `progress[i] = min(progress[i] + step, shared_distance - head_offset_progress[i] + step)` — OR simpler: leave the clamp at `shared_distance` (clamping above the finish threshold is harmless) and only change the comparison. Pick the simpler one and document the choice with a comment. Add a 1-2 line comment block above the new code explaining that head-offset is universal (both species) per CONTEXT-4 Decision 3 — turtles are symmetric so this doesn't change their behavior; snakes get the fairness fix.</action>
  <verify>pytest && python -c "import race; import inspect; src = inspect.getsource(race.run_race); assert 'head_offset_progress' in src, 'head_offset_progress not wired'; print('OK')"</verify>
  <done>pytest stays fully green. The smoke `python -c` prints `OK`. The finish-check line in run_race subtracts `head_offset_progress[i]` from `shared_distance`. The parallel array is computed exactly once per race, before the loop.</done>
</task>

<task id="3" files="" tdd="false">
  <action>**Manual smoke gate** — the Phase 4 acceptance criterion. Launch the game and run the following matrix; capture observations in SUMMARY-3.1.md. (a) Turtles × straight: bet on a turtle, race finishes with 4 finishers, podium correct, play-again works. Visually identical to Phase 3 — no shape/size regression. (b) Turtles × rectangular: same checks. (c) Turtles × spiral: same checks. (d) Snakes × straight: snake bet dialog appears (3-snake row); pick one; race shows 3 SNAKE-SHAPED racers (NOT turtle-shaped); Shadow visibly longer than Anaconda visibly longer than Ralph; all fit within their lane boundaries; podium shows 3 finishers; play-again works. (e) Snakes × rectangular: same checks; specifically watch for whether the head-position finish gives a visually-fair race (longer snakes don't get an unfair lead/lag at the finish line). Run 3-5 rounds to eyeball fairness. (f) Snakes × spiral: same checks; note in SUMMARY any visual issues — but per CONTEXT-4 Decision 7, spiral 3-lane geometry tuning is OUT OF SCOPE and deferred to Phase 5; only fix issues that are SHAPE-caused (e.g., snake too thick to fit corner). (g) Alternating round test: Turtles round → Snakes round → Turtles round. No crashes, no image-GC blanking, no leftover shapes from prior round. **Decision gate (CONTEXT-4 Decision 1):** if the stretched-classic shape does NOT read as a snake at race scale, document the observation and consider the polygon-fallback escalation. If you escalate, do it in this task — add a `screen.register_shape("snake", polygon)` call ONCE at startup (RESEARCH.md §10 gotcha 6 — register_shape persists across screen.clear(), so register at module-import not in the round loop) and switch `draw_snake_shape` to `t.shape("snake")` instead of `t.shape("classic")`. If shape reads OK, ship as-is and note the decision in SUMMARY-3.1.md.</action>
  <verify>python main.py</verify>
  <done>All 6 (track × species) combinations reach the podium without crashing. Snakes are visibly snake-shaped (not turtle-shaped) and visibly in 6:5:2 length ratio. Turtle mode looks identical to Phase 3 (no regression). The alternating-round test produces no Tk state leaks or image artifacts. SUMMARY-3.1.md captures the smoke observations and the Decision 1 (stretched-classic vs polygon-fallback) call.</done>
</task>

## Notes for the builder

- Per-task atomic commits. Task 1 commits tests/test_race.py alone. Task 2 commits race.py alone. Task 3 either commits nothing (smoke-only) OR commits a polygon-fallback escalation in race.py if the visual gate forces it — that decision is yours during smoke.
- Per CONTEXT-4 Decision 6, Phase 4 is COMPLETE at the end of this plan. Picking Snakes must produce a 3-snake race with snake-shaped racers in the correct length ratio; picking Turtles must remain visually indistinguishable from Phase 3.
- Per CONTEXT-4 Decision 7, do NOT attempt to retune spiral 3-lane entry geometry here — that is deferred to Phase 5. Record observations only.
- If `L_BASE = 0.6` or `SNAKE_STRETCH_WID = 0.5` look wrong during smoke (Shadow too short, snakes too fat, etc.), it's acceptable to tweak the constants — but cite the change clearly in SUMMARY-3.1.md and re-run the smoke matrix.
- Write SUMMARY-3.1.md to disk before returning.
