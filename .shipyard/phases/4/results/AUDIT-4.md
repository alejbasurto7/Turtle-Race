# Phase 4 Security Audit

## Verdict: **CLEAN**

Phase 4 is pure refactor + math + cleanups on a local desktop game. No new external surfaces, no new dependencies, no I/O beyond Tk/turtle's existing usage.

## Scope checks

### Code security (OWASP / general)

N/A — no web surface, no auth, no DB. The new code paths:
- `draw_turtle_shape(t)` / `draw_snake_shape(t, length_units)` — pure turtle-module API calls (`shape()`, `shapesize()`)
- `_SHAPE_DRAWERS` dispatch — dict lookup; key comes from constants, not user input
- `head_offset_progress` math — pure arithmetic on internal state
- `announce_result`/`celebrate` identity refactor — replaced equality of opaque tuples with `is` identity comparison; safer
- `next(r for r in racers if r['o'] is winner)` — `winner` always comes from `racers` (set by `run_race`), so `StopIteration` cannot occur in normal flow. No untrusted input here.
- `racers[i]['o'].shapesize()[1]` — `shapesize()` returns a 3-tuple for any racer with shape set. All racers have shape set in `_SHAPE_DRAWERS` before `run_race` reads this. Safe.

### Secrets scanning

Diff scanned — no secrets, API keys, credentials, or tokens introduced. Phase 4 only adds float constants, function bodies, and test arithmetic.

### Dependency vulnerabilities

`requirements.txt` unchanged. No new packages. Existing Pillow + pygame-ce versions unchanged.

### IaC

N/A — no IaC files in scope.

### Configuration security

`turtle_race.spec` unchanged. No new bundled assets in this phase. `assets/midi/` remains untracked (user-controlled; not bundled).

### Cross-cutting concerns

- The `shape_drawer` string sentinel pattern from CONTEXT-1 is preserved end-to-end. The dispatch in `_SHAPE_DRAWERS` is the only code that resolves the sentinel; `constants.py` remains import-clean.
- `next(...)` for winner_racer lookup uses `is` identity rather than equality, so it can't be spoofed by two racers sharing a color.
- `coast_remaining[i] is None` as the new race-loop guard is a clean sentinel; can't be confused with `0` or `False`.

## Findings

None.

## Notes

- The `_SHAPE_UNIT_SIZE = 9` calibration constant is `classic`-shape-specific (acceptable per CRITIQUE.md and the inline comment block in `race.py`). This is a correctness/visual-tuning concern, not a security one.
- Phase 4 also fixes the pre-existing `pencolor()` win-check fragility — two racers sharing a color could previously mis-attribute a win. Now uses identity. Net security/correctness improvement.

## One-line verdict

CLEAN — no findings, Phase 4 is clear to ship.
