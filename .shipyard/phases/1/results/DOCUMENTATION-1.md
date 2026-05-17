# Documentation Review — Phase 1

## Verdict: GAPS_IDENTIFIED (minor — all low-cost or deferred)

## Coverage Summary

| Area | Status | Notes |
|---|---|---|
| Module docstring (`leaderboard.py`) | MISSING | No top-of-file docstring; module purpose, schema version, and Tk-free invariant are undocumented at the module level |
| Public function docstrings | ADEQUATE | `record_race`, `query`, `query_per_track`, `known_tracks`, `reset_session`, `reset_all` all have docstrings meeting the repo's terse standard |
| Public dataclass docstrings | MISSING | `Row` and `PerTrackRow` have no docstrings; fields are self-describing but the distinction between the two types is not stated |
| Public constants (`POINTS`, `SCHEMA_VERSION`) | MISSING | Exported without any comment or docstring; `POINTS` ordering (1st=6, 2nd=3, 3rd=1, 4th=0) is non-obvious |
| `paths.user_data_path` docstring | CONSISTENT (no action needed) | Uses inline comment block, matching `resource_path`'s style exactly; no formal docstring is warranted |
| CLAUDE.md addendum | DEFER to Phase 5 | PROJECT.md §File-by-File Change Map already calls this out; VERIFICATION.md carryover item 1 flags the `import paths` monkeypatch lesson — both should land in CLAUDE.md at ship time |
| README.md | NOT APPLICABLE | No project README exists in the repo root; feature is incomplete until Phase 4 |
| `docs/` architecture | NOT APPLICABLE | `docs/` contains only feature-plan files (`docs/superpowers/`), not an architecture overview; no existing doc to update |

---

## Recommended Actions (prioritized)

### 1. Now (low-cost, can be done by any phase's builder as a one-liner)

**Add a module docstring to `leaderboard.py`** (line 1, before the imports).

Suggested text — terse, matches `tracks.py` convention:

```python
"""Scoring, persistence, and query surface for race leaderboard data.

Tk-free by design: this module must remain importable without a display.
Historic data lives in user_data_path("leaderboard.json") (never inside
the PyInstaller bundle). All writes go through user_data_path(), never
resource_path(). Schema version: SCHEMA_VERSION = 1.
"""
```

**Add inline comments to `POINTS` and `SCHEMA_VERSION`** (leaderboard.py lines 13-14):

```python
POINTS = (6, 3, 1, 0)    # points awarded for 1st/2nd/3rd/4th place
SCHEMA_VERSION = 1        # increment when the JSON structure changes
```

**Add brief class-level comments to `Row` and `PerTrackRow`** (the dataclass header lines):

```python
@dataclass(frozen=True)
class Row:
    """Leaderboard row returned by query() — one entry per racer."""
    ...

@dataclass(frozen=True)
class PerTrackRow:
    """Leaderboard row returned by query_per_track() — one entry per (racer x track) pair."""
    ...
```

### 2. Defer to Phase 5

**CLAUDE.md addendum** — the following two items are flagged in VERIFICATION.md as Phase 5 carryovers and belong there, not now:

- The `import paths` (not `from paths import user_data_path`) rule and why it matters for monkeypatching (VERIFICATION.md carryover item 1).
- The `%APPDATA%\TurtleRace\leaderboard.json` data location and the invariant that writable files never go through `resource_path()`. PROJECT.md §Resource loading already mandates this for assets; the parallel rule for writable state is a natural addendum to the "Resource loading (PyInstaller-aware)" section in CLAUDE.md.

The "Round loop shape" section in CLAUDE.md will also need updating in Phase 5 when `main.py` becomes main-menu-driven — that is explicitly out of scope for Phase 1.

### 3. Skip

- **`paths.user_data_path` formal docstring** — the five-line comment block already conveys the `_MEIPASS` invariant clearly and matches `resource_path`'s zero-docstring style exactly. Converting to a docstring would diverge from the existing convention for no practical gain.
- **Test file docstrings** — test functions are self-describing by name; the repo has no precedent for test docstrings.
- **Private function docstrings** beyond what already exists — `_path`, `_empty_store`, `_load`, `_save`, `_races_for_window`, `_in_window`, `_species_matches`, `_aggregate`, `_sorted_rows` all have inline comments or minimal docstrings adequate for the codebase scale.

---

## Verdict Rationale

Phase 1 delivers a well-documented internal module: all six public functions carry docstrings that meet the repo's terse standard, and the key design decisions (monkeypatch strategy, atomic writes, session/disk separation) are explained in-line where the code lives. The only genuine gaps are a missing module-level docstring and uncommented public constants — both low-cost and appropriate to fix now. CLAUDE.md and README updates correctly belong in Phase 5 per the project roadmap.
