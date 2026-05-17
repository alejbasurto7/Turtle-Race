# Shipyard Non-Blocking Issues

Issues logged here by the reviewer. They do not block the current plan but should be addressed before the project is considered production-ready.

---

## Phase 1, Plan 1.1 — `paths.user_data_path()` + smoke tests

### Important: Two tests write real directories outside `tmp_path`

**`tests/test_paths.py` lines 27-32 (`test_user_data_path_macos`) and lines 44-50 (`test_user_data_path_linux_falls_back_to_local_share`)** both call `user_data_path()` without pinning the home directory to `tmp_path`. The function's `os.makedirs` call creates real directories on the host filesystem (e.g. `C:\Users\T0226129/Library/Application Support/TurtleRace` for the macOS test running on Windows). This violates the plan's acceptance criterion: "No test writes anywhere other than `tmp_path`."

Remediation: patch `HOME` (POSIX) / `USERPROFILE` + `HOMEDRIVE` + `HOMEPATH` (Windows) via `monkeypatch.setenv`, or patch `os.path.expanduser` directly, so that `os.path.expanduser("~/...")` resolves under `tmp_path`. Example for the macOS test:

```python
def test_user_data_path_macos(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(os.path, "expanduser", lambda p: p.replace("~", str(tmp_path)))
    result = user_data_path("leaderboard.json")
    normalized = result.replace("\\", "/")
    assert "Library/Application Support/TurtleRace" in normalized
```

### Suggestion: Windows fallback test also writes outside `tmp_path`

**`tests/test_paths.py` lines 20-24 (`test_user_data_path_windows_falls_back_when_appdata_unset`)** — when `APPDATA` is unset, the implementation falls back to `os.path.expanduser("~\\AppData\\Roaming")`, which creates `%APPDATA%\TurtleRace` on the real filesystem. Lower severity (the directory likely already exists; `exist_ok=True` makes it idempotent), but technically violates the no-writes-outside-tmp_path invariant.

### Suggestion: Add a comment to the `_MEIPASS` regression-guard parametrized test

**`tests/test_paths.py` lines 53-63** — the test is a deliberate regression guard (it cannot fail with the current implementation since `_MEIPASS` is never read in `user_data_path()`). A one-line comment (`# Regression guard: user_data_path must never consult _MEIPASS`) would clarify intent for future maintainers, consistent with the repo's inline-comment convention.

---

## Phase 3, Plan 1.1 — three new dialog functions

### Important: `transient()` called with no argument in new functions but absent from legacy functions

**`dialogs.py` lines 60, 362, 397** call `dialog.transient()` with no argument in the three new functions. The three legacy modal functions (`get_user_bet`, `get_user_track`, `get_user_species`) do not call `transient()` at all. `transient()` with no argument is a no-op (it would need a parent window reference to have effect), so this causes no observable behavior difference. However, it creates a within-file inconsistency.

Remediation (choose one): (a) Remove the no-op `transient()` calls from the three new functions for uniformity with the legacy functions; (b) back-fill `transient()` into the three legacy functions; or (c) pass `tkinter._default_root` (or the turtle Screen's underlying Tk root) so the call has real effect and all six dialogs become proper children of the root window. Option (c) is the most correct UX choice (the dialog will minimize/restore with the parent). Defer to Plan 2.1 or a polish plan.

### Suggestion: `show_leaderboard_placeholder` should comment the intentional absence of the `selected = [None]` sentinel

**`dialogs.py` lines 388-389** — `show_leaderboard_placeholder` uses a plain `def close(): dialog.destroy()` instead of the `make_cb` sentinel pattern used by the other five functions. This is correct (the function returns `None`, so no capture is needed), but a Phase 4 maintainer replacing the body may wonder why the pattern is absent. A one-line comment (`# No return value — close handler directly destroys the dialog, no sentinel needed.`) above `def close():` would make the intent explicit.

---

## Phase 3, Plan 2.1 — main.py restructure + smoke_phase_3.py

### RESOLVED 2026-05-17 (commit `e159fc4`): `tools/smoke_phase_3.py` — leaderboard branch may not actually be exercised

(Fixed by reordering `menu_choices = iter(["race", "leaderboard", "race", "quit"])` and adding a `leaderboard_placeholder_calls` counter with a hard assertion that it equals 1. Smoke re-verified: 3 races recorded + 1 placeholder call.)

---

#### Original report (kept for reference):


**`tools/smoke_phase_3.py` line 54** sets `menu_choices = iter(["race", "race", "leaderboard", "race", "quit"])`. Tracing the control flow:

- Outer iter 1 consumes `"race"` → enters inner loop.
  - Inner iter 1 (round 1: turtles/straight): `post_race_choices` → `"again"` → continues.
  - Inner iter 2 (round 2: snakes/spiral): `post_race_choices` → `"menu"` → exits inner loop.
- Outer iter 2 consumes `"race"` → enters inner loop again.
  - Inner iter 3 (round 3: turtles/rectangular): `post_race_choices` → `"quit"` → sets `running=False`, `in_round_loop=False`, exits both loops.
- Outer loop exits immediately (running=False). The `"leaderboard"` and final `"race"` and `"quit"` entries in `menu_choices` are **never consumed**.

This means `dialogs.show_leaderboard_placeholder` (monkeypatched at line 91) is never called, and the `menu→leaderboard→menu` transition is never exercised. The `[smoke] menu→leaderboard→menu transition executed cleanly` print at line 151 fires unconditionally and is misleading.

Remediation: Restructure `menu_choices` and `post_race_choices` so the leaderboard branch is genuinely reached. One correct sequence:

```python
# Outer: race → (2 inner rounds) → leaderboard → quit
menu_choices     = iter(["race",  "leaderboard", "quit"])
post_race_choices = iter(["again", "menu"])
rounds = [
    {"track": "straight",   "species": "turtles", "bet": 1},
    {"track": "spiral",     "species": "snakes",  "bet": 2},
]
```

This produces 2 race records, exercises the leaderboard branch, and matches the spec's documented canned flow. Alternatively, add a third race round after the leaderboard:

```python
menu_choices     = iter(["race",  "leaderboard", "race", "quit"])
post_race_choices = iter(["again", "menu",        "quit"])
```

Either way, add an assertion that `fake_show_leaderboard_placeholder` was called (e.g., count invocations with a nonlocal counter) so the claim is machine-verified rather than printed unconditionally.
