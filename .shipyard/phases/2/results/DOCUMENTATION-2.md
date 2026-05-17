# Documentation Review — Phase 2

## Verdict: COMPLETE (one low-cost addition recommended)

## Coverage Summary

| Area | Status | Notes |
|---|---|---|
| `paths.user_data_path` docstring | GAP (low-cost) | Raises `ValueError` on invalid filenames; behavior change not yet reflected at the call signature level |
| `tools/smoke_phase_2.py` docstring | ADEQUATE | 14-line module docstring covers purpose, invocation, exit codes, and scope; nothing missing |
| CLAUDE.md addendum | DEFER to Phase 5 | Per ROADMAP and Phase 1 recommendation; both the leaderboard-write fact and the smoke tool discovery belong in the Phase 5 CLAUDE.md pass |
| `main.py` wiring inline comment | SKIP | `leaderboard.record_race(species, track_name, finish_order_names)` is self-explanatory; a comment would be noise per repo convention |
| `tests/test_paths.py` banner comment | ADEQUATE | Banner `# --- Filename validation (Phase 2 basename guard) ---` is sufficient |
| README.md / docs/ | N/A | None exist; no change from Phase 1 |

---

## Recommended Actions (prioritized)

### 1. Now (low-cost)

**Add a one-line docstring to `user_data_path` in `paths.py`.**

Phase 1 correctly skipped this because the function had no exceptional behavior worth calling out over the existing inline comment. Phase 2 changed that: the function now raises `ValueError`, which is a contract obligation any future caller must know about. The existing comment block explains the `_MEIPASS` / writable-state invariant well, but it does not appear in `help()` output and is easily missed when a caller reads only the signature.

Suggested addition (insert as the first line of the function body, before the existing comment block):

```python
def user_data_path(filename: str) -> str:
    """Return the absolute path for a writable per-user data file.

    ``filename`` must be a bare basename with no path separators or
    traversal tokens (e.g. ``"leaderboard.json"``).  Raises ``ValueError``
    otherwise.  Never resolves through ``sys._MEIPASS`` — see inline
    comment for rationale.
    """
    # Reject any filename containing a path separator or parent-traversal token.
    ...
```

`resource_path` remains zero-docstring — it has no exceptional behavior. Adding a docstring only to `user_data_path` is a targeted deviation justified by the new contract.

### 2. Defer to Phase 5

- **CLAUDE.md "Resource loading" addendum** — note that `leaderboard.json` is now being written to `%APPDATA%\TurtleRace\` each round, and that writable state must never go through `resource_path()`. Also note `tools/smoke_phase_2.py` as a developer smoke-test requiring a display. Both belong in the Phase 5 CLAUDE.md polish pass alongside the `import paths` (not `from paths import`) monkeypatch rule identified in Phase 1.
- **"Round loop shape" section in CLAUDE.md** — already flagged in Phase 1 as a Phase 5 update once `main.py` becomes main-menu-driven.

### 3. Skip

- **`main.py` wiring comment** — `record_race` and its three arguments are self-describing; a comment explaining "why here" would be noise. The position before `show_podium` is obvious from the data-flow (finish order is available, podium hasn't rendered yet).
- **`tools/smoke_phase_2.py` improvements** — the module docstring already covers purpose, invocation, exit codes (`0` / non-zero), isolation strategy (`%APPDATA%` redirect), and scope exclusion from pytest. Nothing actionable missing.
- **Test docstrings** — no precedent in the repo; self-describing names are sufficient.

---

## Verdict Rationale

Phase 2 is a small wiring change. The only genuine documentation gap introduced is `user_data_path`'s new `ValueError` contract, which previously had no exceptional behavior worth surfacing at the signature level. A three-line docstring closes that gap at near-zero cost. Everything else — smoke tool, wiring comment, CLAUDE.md — is either already adequate or correctly deferred to Phase 5 per the existing project roadmap.
