# CONVENTIONS.md

## Overview

Turtle Race is a small, single-developer Python codebase (~1 063 source lines across 7 modules). There are no linter, formatter, or type-checker config files present. The code is clean and consistent by informal convention rather than enforced tooling. Type hints appear only in `tracks.py` and only for a handful of low-level helper functions.

## Metrics

| Metric | Value |
|--------|-------|
| Source Python files (root) | 7 (`main.py`, `constants.py`, `race.py`, `dialogs.py`, `audio.py`, `paths.py`, `tracks.py`) |
| Total source lines (root modules) | 1 063 |
| Linter config files found | 0 (no `.flake8`, `pyproject.toml`, `setup.cfg`, `mypy.ini`, `ruff.toml`) |
| Type-annotated functions | ~4, all in `tracks.py` |
| TODO / FIXME / HACK occurrences | 0 |
| Commented-out code blocks | 2 (both in `constants.py`) |

## Findings

### Linting and Formatting

- **No linter or formatter is configured.** No `.flake8`, `pyproject.toml`, `setup.cfg`, `mypy.ini`, `ruff.toml`, or `.pylintrc` was found at the project root. Code style is maintained by convention alone.
  - Evidence: `requirements.txt` and all root config files — none reference flake8, black, ruff, or mypy.
- [Inferred] The code follows PEP 8 formatting informally — 4-space indentation, blank lines between top-level definitions, lines that appear to stay under ~100 characters.

### Type Hints

- **Sparse, localised to `tracks.py`.** Only `tracks.py` uses type annotations, and only on a subset of its helper functions.
  - Evidence: `tracks.py` lines 45–48 — `set_window_size(width: float, height: float) -> None`
  - Evidence: `tracks.py` lines 51–52 — `_window() -> tuple[float, float]`
  - Evidence: `tracks.py` lines 55–57 — `_lane_coefficient(lane_idx: int) -> float`
  - Evidence: `tracks.py` line 16 — `from __future__ import annotations` guards forward references
- All other modules (`main.py`, `race.py`, `dialogs.py`, `audio.py`, `paths.py`, `constants.py`) have zero type annotations.

### Naming Conventions

- **Module names**: lowercase, single-word (`main`, `race`, `dialogs`, `audio`, `tracks`, `paths`, `constants`).
- **Constants**: `UPPER_SNAKE_CASE` throughout `constants.py` — e.g., `TURTLE_COLORS`, `MAX_PACE`, `TICK_DELAY`, `LANE_SPACING`.
  - Evidence: `constants.py` lines 8–33
- **Module-level non-constant variables**: `_lower_snake_case` with a leading underscore to signal internal/private — e.g., `_screen`, `_window_w`, `_window_h`.
  - Evidence: `race.py` line 13, `tracks.py` lines 41–42
- **Functions**: `snake_case`. Public functions use plain names (`make_screen`, `run_race`, `draw_finish_line`); internal helpers get a leading underscore (`_draw_segment`, `_draw_checkered_bar`, `_straight_lane`, `_rectangular_lane`, `_build_spiral_legs`, `_boundary_paths`).
  - Evidence: `race.py` lines 30, 65, 98; `tracks.py` lines 65, 74
- **Local variables**: `snake_case`. Short names used freely inside tight loops (`t`, `i`, `cx`, `dx`, `ux`).
  - Evidence: `race.py` lines 136–138 (`t`, `turtle_color`); `dialogs.py` lines 39–61

### Module Organisation and Import Style

- **Import ordering**: stdlib first, then third-party, then local — separated by blank lines. Consistent across all modules.
  - Evidence: `race.py` lines 1–10 (stdlib `math`, `random`, `time`, `turtle`; third-party `PIL`; local `tracks`, `constants`, `paths`)
  - Evidence: `dialogs.py` lines 1–8 (stdlib `tkinter`; third-party `PIL`; local `tracks`, `constants`, `paths`)
- **Asset path resolution**: all asset lookups go through `resource_path()` from `paths.py`. No raw `open()` calls on asset files outside this helper.
  - Evidence: `paths.py` lines 5–7; called in `race.py` line 52, `dialogs.py` lines 42 and 101, `audio.py` line 9

### Comment Style

- **Inline explanatory comments** are the dominant style, used to explain non-obvious logic (coordinate system inversions, Tk garbage-collection traps, tag-raising order).
  - Evidence: `race.py` lines 106–107 (`# unit vector along segment`, `# perpendicular (left of direction)`)
  - Evidence: `race.py` lines 419–422 (explains why `tag_raise` is called after `_screen.update()`)
- **Block comments above sections** used inside long functions to separate passes (e.g., `# Pass 1: ...`, `# Pass 2: ...`, `# Pass 3: ...` in `show_podium`).
  - Evidence: `race.py` lines 265, 289, 312
- **Module-level docstrings**: only `tracks.py` has one; other modules have none.
  - Evidence: `tracks.py` lines 1–14
- **Function docstrings**: sparse. `make_screen`, `run_race`, `show_podium`, `_draw_checkered_bar`, `_lane_coefficient` have them; most functions do not.
  - Evidence: `race.py` lines 31, 99, 156–166, 237–241; `tracks.py` lines 56–57
- **Commented-out code**: two blocks in `constants.py` — the original dict form of `TURTLE_COLORS` and a commented-out wider `WINDOW_WIDTH`. These are left as reference, not dead production code.
  - Evidence: `constants.py` lines 1–6, 10

### Error Handling

- **Silent degradation for non-critical paths**: audio failures are caught and printed, not raised.
  - Evidence: `audio.py` lines 8–12 (`try/except Exception as e: print(...)`)
- **Pass-through suppression for cleanup**: `stop_background_music` swallows all exceptions silently.
  - Evidence: `audio.py` lines 15–19 (`except Exception: pass`)
- **Encoding guard at startup**: `sys.stdout.reconfigure(encoding="utf-8")` wrapped in a bare `except Exception: pass` to tolerate environments that don't support reconfigure.
  - Evidence: `main.py` lines 3–6
- **Deliberate `RuntimeError`** raised if `get_screen()` is called before `make_screen()` — the one place a hard failure is intentional.
  - Evidence: `race.py` lines 43–45

### Print-based Logging

- No logging framework is used. Race-start metadata and finish results are logged via `print()` statements directly.
  - Evidence: `race.py` lines 176–183 (race start log), lines 224–231 (finish order log)
- Win/loss outcomes also print to stdout with emoji.
  - Evidence: `race.py` lines 353–354

## Summary Table

| Item | Detail | Confidence |
|------|--------|------------|
| Linter | None configured | Observed |
| Formatter | None configured | Observed |
| Type hints | Only `tracks.py`, ~4 functions | Observed |
| Constant naming | `UPPER_SNAKE_CASE` | Observed |
| Private symbol prefix | Leading underscore `_` | Observed |
| Import order | stdlib, third-party, local | Observed |
| Comment style | Inline + section headers; sparse docstrings | Observed |
| Error handling | Silent for audio/encoding; hard fail for screen init | Observed |
| Logging | `print()` only | Observed |
| Commented-out code | 2 blocks in `constants.py`, kept as reference | Observed |

## Open Questions

- Is there a plan to add a linter (e.g., ruff) given the project now has test infrastructure?
- The `cheat_mode` path mentioned in CLAUDE.md is wired but never activated — should it be removed or documented as intentional dead code?
