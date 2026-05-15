# TESTING.md

## Overview

The test suite covers the pure-geometry layer (`constants.py` and `tracks.py`) with 45 pytest tests across two files. All UI, audio, and race-loop code (`main.py`, `race.py`, `dialogs.py`, `audio.py`) is untested. Coverage is deliberately focused on the logic that is testable without a display or Tk event loop.

## Metrics

| Metric | Value |
|--------|-------|
| Test files | 2 (`tests/test_constants.py`, `tests/test_tracks.py`) |
| Total tests collected | 45 |
| Parametrised test variants | 11 (3 tracks x several parametrised checks) |
| Source modules covered | 2 of 7 (`constants.py`, `tracks.py`) |
| Source modules not covered | 5 (`main.py`, `race.py`, `dialogs.py`, `audio.py`, `paths.py`) |
| Test runner | pytest (installed separately; not in `requirements.txt`) |
| pytest config file | None (no `pytest.ini`, `pyproject.toml [tool.pytest]`, or `setup.cfg [tool:pytest]`) |
| Coverage tooling | None configured |
| Test-to-source line ratio | ~442 test lines : ~1 063 source lines (0.42 : 1) |

## Findings

### Test Runner and Configuration

- **Runner**: pytest. Documented as the runner in `CLAUDE.md`; not listed in `requirements.txt` and must be installed separately.
  - Evidence: `CLAUDE.md` — "Run tests (pytest is not in `requirements.txt` — install it separately)"
- **No pytest config file exists.** No `pytest.ini`, `pyproject.toml`, `setup.cfg`, or `conftest.py` was found. Pytest runs with all defaults.
- **No `conftest.py`.** Each test file inserts the project root into `sys.path` manually at the top of the file.
  - Evidence: `tests/test_constants.py` lines 1–5; `tests/test_tracks.py` lines 1–5

### Test File Organisation

- **Location**: `tests/` directory at the project root. Flat structure — no subdirectories.
- **Naming**: `test_<module>.py` convention, matching the source module under test.
  - `tests/test_constants.py` tests `constants.py`
  - `tests/test_tracks.py` tests `tracks.py`
- **No fixtures or shared helpers** across files. Each file is self-contained.
- **One local helper function** defined in `test_tracks.py`: `_approx(a, b, tol=1e-6)` wraps `math.isclose` to avoid repeating tolerances. It is private to that file.
  - Evidence: `tests/test_tracks.py` lines 34–35

### What Is Tested

#### `tests/test_constants.py` (3 tests)

- `TURTLE_IMAGES` keys exactly match `TURTLE_NAMES`.
- Every image path in `TURTLE_IMAGES` resolves to an actual file on disk.
- `BET_IMAGE_SIZE` is a positive integer.
- Evidence: `tests/test_constants.py` lines 10–26

#### `tests/test_tracks.py` (42 tests)

Covers the entire public surface of `tracks.py` plus the private helpers `_build_spiral_legs` and `_boundary_paths`. Test groups:

- **Track registry** — `TRACK_NAMES` contains exactly `{STRAIGHT, RECTANGULAR, SPIRAL}`; `build_lane_paths` returns `N_LANES` paths with required keys for every track.
- **Straight track geometry** — lane length equals `WINDOW_WIDTH - 2 * TRACK_PADDING`; lanes share X, differ in Y, spaced by `LANE_SPACING`.
- **Rectangular track geometry** — average lane length matches centerline perimeter formula; each lane ends at the finish bar's Y; outer lane is longer than inner; corner headings are right turns; starts staggered diagonally; all points fit inside screen bounds.
- **Spiral track geometry** — starts staggered in both axes; all lanes end at origin; legs decrease in size; headings repeat N-E-S-W; boundary first stone at expected corner.
- **`position_at_arc` utility** — returns start correctly at arc=0; clamps past end; transitions heading correctly across corners.
- **Start and finish line segments** — segment count, orientation, and span verified for each track type.
- **Boundary stones** — non-empty for all tracks; straight forms two parallel rows; rectangular brackets racing band; spiral boundary path count is two; stones fit inside screen; stone count matches `floor(length/spacing)+1` formula.
- Evidence: `tests/test_tracks.py` throughout (lines 40–417)

### What Is Not Tested

- **`main.py`** — the round loop, `keep_playing` logic, `first_run` flag handling.
- **`race.py`** — `run_race` (race tick loop, progress/fraction logic, coasting), `show_podium`, `celebrate`, `announce_result`, `create_turtles`, `place_turtles_on_track`, `set_background`, `draw_start_line`, `draw_finish_line`, `draw_boundary_stones`. All require a live Tk/turtle display.
- **`dialogs.py`** — `get_user_bet`, `get_user_track`, `ask_play_again`. All require a Tk event loop.
- **`audio.py`** — `start_background_music`, `stop_background_music`.
- **`paths.py`** — `resource_path` (trivial one-liner, but the PyInstaller branch is untested in-process).
- [Inferred] The display-dependent modules are deliberately excluded because headless testing of `turtle` and `tkinter` would require mocking the entire Tk/Screen stack.

### Parametrisation

- `@pytest.mark.parametrize("track", TRACK_NAMES)` is used for cross-track checks (lane path shape, boundary stones non-empty, stones fit in screen, stone count formula).
  - Evidence: `tests/test_tracks.py` lines 44, 333, 400, 409

### How to Run

```powershell
# All tests
pytest

# Single file
pytest tests/test_constants.py

# Single test
pytest tests/test_constants.py::test_image_files_exist_on_disk

# With verbose output
pytest -v
```

pytest must be installed first: `pip install pytest`. It is not in `requirements.txt`.

## Summary Table

| Item | Detail | Confidence |
|------|--------|------------|
| Framework | pytest | Observed |
| Config file | None | Observed |
| `conftest.py` | Absent; path patched per-file | Observed |
| Files covered | `constants.py`, `tracks.py` | Observed |
| Files not covered | `main.py`, `race.py`, `dialogs.py`, `audio.py`, `paths.py` | Observed |
| Total tests | 45 | Observed |
| Fixture / mock usage | None | Observed |
| Coverage tooling | None | Observed |
| CI integration | Not detected | Inferred |

## Open Questions

- Should `paths.py`'s `resource_path` be tested in isolation (the `_MEIPASS` branch is never exercised by the test suite)?
- Is there a plan to add smoke tests for the race loop that mock the `Screen` object, or is the UI layer intentionally left to manual QA?
- pytest is not pinned in any requirements file — should it be added to a `requirements-dev.txt`?
