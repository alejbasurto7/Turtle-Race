---
plan: PLAN-3.1
wave: 3
phase: snakes-racer-mode
builder: claude-sonnet-4-6
date: 2026-05-15
status: TASKS_1_2_COMPLETE | TASK_3_PENDING_HUMAN_VERIFICATION
---

# SUMMARY-3.1 — Head-position finish detection + manual smoke gate

## Baseline

79/79 tests passed before any changes (Wave 1+2 state confirmed).
No `tests/test_race.py` existed at baseline.

---

## Task 1 — tests/test_race.py (pure-math unit tests)

**File created:** `tests/test_race.py`

Tests do NOT import `race.py`. A local `_head_offset_progress()` helper
mirrors the formula verbatim so the math is assertable without Tk/turtle.

**Tests added (5 total):**

| Test | What it asserts |
|---|---|
| test_head_offset_progress_ratio_equal | ratio=1.0 → head_offset_progress == head_offset_arc |
| test_head_offset_progress_ratio_less_than_one | lane_length=2x → offset halved |
| test_head_offset_progress_ratio_greater_than_one | lane_length=0.5x → offset doubled |
| test_head_offset_arc_shadow | stretch_len=3.6, arc=16.2 px |
| test_head_offset_arc_ralph | stretch_len=1.2, arc=5.4 px |

Result: 84/84 tests pass (79 prior + 5 new).

Commit: test(race): add pure-math unit tests for head-offset progress formula

---

## Task 2 — race.py head_offset_progress wired into run_race

**File modified:** `race.py` — `run_race()` only.

Parallel array computed once per race after place_racers_on_track:

    _SHAPE_UNIT_SIZE = 9
    head_offset_progress = []
    for i in range(len(racers)):
        stretch_len = racers[i]['o'].shapesize()[1]
        head_offset_arc = _SHAPE_UNIT_SIZE * stretch_len / 2
        head_offset_progress.append(head_offset_arc * (shared_distance / lane_lengths[i]))

Finish check changed from:
    if progress[i] >= shared_distance:
to:
    if progress[i] >= shared_distance - head_offset_progress[i]:

Loop guard changed from `if progress[i] < shared_distance:` to
`if coast_remaining[i] is None:` so the racing branch cannot re-enter after
finish fires at the new (lower) threshold. coast_remaining[i] is set to
COAST_TICKS at finish moment and remains non-None thereafter.

Clamp stays at shared_distance (plan recommendation — simpler than lowering).

Verification commands:
  pytest --tb=short -q                          -> 84 passed
  python -c "import race; import inspect; ..."  -> OK

Commit: feat(race): add universal head-position finish detection in run_race

---

## Stretch_len values and head_offset sanity check

stretch_len = L_BASE * length_units, L_BASE=0.6
SNAKE_LENGTHS = [6, 2, 5] for [Shadow, Ralph, Anaconda]

Per-racer stretch_len and head_offset_arc (= 9 * stretch_len / 2):

  Shadow:    stretch_len=3.60, head_offset_arc=16.20 px
  Anaconda:  stretch_len=3.00, head_offset_arc=13.50 px
  Ralph:     stretch_len=1.20, head_offset_arc= 5.40 px
  Turtles:   stretch_len=1.00, head_offset_arc= 4.50 px (all 4, same)

Example head_offset_progress at shared_distance=3000, lane_length=1500 (ratio=2.0):

  Shadow:    head_offset_progress=32.40
  Anaconda:  head_offset_progress=27.00
  Ralph:     head_offset_progress=10.80
  Each turtle: head_offset_progress=9.00

Fairness check: on the straight track, Shadow finishes 16.2 progress units
earlier than a zero-offset check; Ralph finishes 5.4 units earlier. With the
offset, both heads cross the line at the same expected visual moment given
equal luck — fair regardless of snake length.

shape_unit_size=9 caveat (CRITIQUE.md): calibrated for classic (snakes).
For turtle shape it is approximate, but all 4 turtles share the same
stretch_len=1.0 so the offset is identical and race ranking is unaffected.

---

## Task 3 — Manual smoke gate

Status: PENDING_HUMAN_VERIFICATION

Task 3 requires a live Tk/turtle window. Run `python main.py` and complete:

Turtle mode — all 3 tracks:
  [ ] Turtles x Straight: 4 turtles race, podium correct, play-again works,
      visually identical to Phase 3 (no shape/size regression)
  [ ] Turtles x Rectangular: same checks
  [ ] Turtles x Spiral: same checks

Snake mode — all 3 tracks:
  [ ] Snakes x Straight: snake bet dialog (3-snake row); 3 SNAKE-SHAPED racers
      (NOT turtle-shaped); Shadow > Anaconda > Ralph visible length ratio;
      all fit in lane; 3-finisher podium; play-again works
  [ ] Snakes x Rectangular: same; run 3-5 rounds, eyeball head-position
      fairness (longer snakes should not finish late/early vs. visual head)
  [ ] Snakes x Spiral: same; note any visual issues (geometry tuning deferred
      to Phase 5 per CONTEXT-4 Decision 7)

Species alternation:
  [ ] Turtles round -> Snakes round -> Turtles round: no crashes, no image-GC
      blanking, no leftover shapes from prior round

Decision 1 gate (CONTEXT-4):
  If stretched-classic does NOT read as a snake at race scale, escalate per
  the PHASE-4-PLACEHOLDER comment in draw_snake_shape (race.py). Document
  the decision (ship as-is or escalate) in smoke notes.

Win-message check:
  [ ] When Ralph wins, message shows color string, not a float tuple.

---

## Implementation tradeoffs

progress-clamp vs. finish-threshold:
  Option "keep clamp at shared_distance" selected (plan recommendation).
  Required changing the loop guard from `progress < shared_distance` to
  `coast_remaining[i] is None` to prevent the racing branch from re-entering
  after finish fires at the new (lower) threshold.

shape_unit_size approximation:
  Accepted for Phase 4. If post-smoke turtle finish feels off, the constant
  can be made per-shape dispatched by t.shape().

---

## Commits (this wave)

  95f42d8  test(race): add pure-math unit tests for head-offset progress formula
  f810a69  feat(race): add universal head-position finish detection in run_race

## Files touched

  tests/test_race.py  NEW — 5 pure-math unit tests, no race.py import
  race.py             Modified run_race: +head_offset_progress, +finish threshold, guard fix
