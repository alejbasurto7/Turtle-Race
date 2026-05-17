---
phase: leaderboard-view
plan: 2.1
wave: 2
dependencies: [1.1]
must_haves:
  - New tools/smoke_phase_4.py exercises the real show_leaderboard() flow end-to-end with no live GUI interaction
  - Mirrors the structure of tools/smoke_phase_3.py (monkeypatch surface + %APPDATA% redirect + main()-invocation pattern)
  - Programmatically exercises the Group-by reshape, Track-filter disable/enable toggle, and both reset paths
  - Records >= 2 races on disk before opening the leaderboard so query() returns non-empty rows and known_tracks() returns a non-trivial list
  - Auto-confirms askyesno prompts via tkinter.messagebox.askyesno monkeypatch
  - Exit code 0 on success; non-zero with a diagnostic message on any verification failure
  - Does NOT touch tools/smoke_phase_3.py (left as Phase 3 historical artifact per CONTEXT-4 §"Carryover")
files_touched:
  - tools/smoke_phase_4.py
tdd: false
risk: low
---

# PLAN 2.1 — No-GUI smoke for the Phase 4 leaderboard view

## Context

Phase 4 adds the real `dialogs.show_leaderboard()` window (Plan 1.1). End-to-end verification of the GUI requires a display, which the builder may not have. Following the Phase 2 / Phase 3 precedent (`tools/smoke_phase_2.py`, `tools/smoke_phase_3.py`), Phase 4 ships a no-GUI smoke script that drives the real wiring through `main.main()` with the user-facing dialogs monkeypatched.

This smoke is distinct from Phase 3's in that it must additionally drive the **inside** of `show_leaderboard` — exercising the Group-by reshape, the Track-filter disable/enable, and the reset confirmations. The simplest way is to monkeypatch `dialogs.show_leaderboard` itself with a function that, after Plan 1.1 lands, can be programmatically driven (i.e., call the real function in a child thread / synchronously and tear it down before `wait_window` blocks — too brittle) OR (preferred) **replace** `dialogs.show_leaderboard` with a callable that exercises the underlying Phase 1 APIs in the documented sequence and asserts the observable outputs.

The architect's call: **replace `dialogs.show_leaderboard` in the smoke with a Phase-1-API driver function** that mimics the exact sequence a user would perform in the GUI (open -> see initial query result -> change Time filter -> verify result changes -> change Group by to Track -> verify per-track result shape -> change Group by back to None -> Reset Session -> verify session-scoped query empties -> Reset All -> verify everything empties). This validates the contract the GUI depends on (`_FILTER_LABEL_TO_KEY` translation + leaderboard API behavior under filter combinations + reset semantics) without ever opening a real Toplevel. The Plan 1.1 GUI wiring itself is verified by `python -c "import dialogs"` and by manual `python main.py` invocation; the smoke covers the integration-level guarantee.

## Dependencies

- Plan 1.1 must be complete: `dialogs.show_leaderboard` exists (renamed from the placeholder), `_FILTER_LABEL_TO_KEY` is defined at module scope, and `leaderboard.py` Phase 1 APIs are reachable.

## Tasks

<task id="1" files="tools/smoke_phase_4.py" tdd="false">
  <action>
Create `tools/smoke_phase_4.py` modeled on `tools/smoke_phase_3.py`. The file MUST:

1. **Set up env BEFORE any `paths`/`leaderboard` import.** Use `tempfile.mkdtemp(prefix="turtlerace_phase4_smoke_")`, assign to `os.environ["APPDATA"]`, then `sys.path.insert(0, <project root>)`.

2. **Build canned plans for the menu / round / post-race flow.** Plan exactly 3 rounds before opening the leaderboard, so the on-disk file has a non-trivial population:
   - Round 1: turtles / straight / bet=1 -> "again"
   - Round 2: snakes / spiral / bet=2 -> "again"
   - Round 3: turtles / rectangular / bet=3 -> "menu"
   - Then menu -> leaderboard (smoke driver runs here) -> menu -> quit

   Mirror `smoke_phase_3.py`'s pattern: `menu_choices = iter(["race", "leaderboard", "quit"])`, `post_race_choices = iter(["again", "again", "menu"])`, and round-indexed `rounds` list.

3. **Define a `fake_show_leaderboard()` driver** that, instead of opening a Toplevel, exercises the contract programmatically. Inside the driver:

   - Import `leaderboard` and `dialogs` (for `_FILTER_LABEL_TO_KEY`).
   - Define `_label_to_key = dialogs._FILTER_LABEL_TO_KEY` (read the dict the GUI uses; if Plan 1.1 changed its name, fail loudly).
   - Step 1 — initial state (Time="All Time", Species="All", Track="All Tracks", Group by="None"):
     - `rows = leaderboard.query("all", "all", "all")`
     - Assert `len(rows) >= 6` (3 races x at least 2 unique racers per race, conservative lower bound).
   - Step 2 — change Time to "Current Session":
     - `rows = leaderboard.query("session", "all", "all")`
     - Assert `len(rows) >= 6` (session covers the same 3 races in-process).
   - Step 3 — change Group by to "Track" -> Track combobox would disable; per-track view:
     - `per_track_rows = leaderboard.query_per_track("all", "all")`
     - Assert all 3 distinct track names appear among `{r.track for r in per_track_rows}`: `straight`, `spiral`, `rectangular`.
     - Assert that for each track, rank starts at 1 (`min(r.rank for r in per_track_rows if r.track == name) == 1`).
   - Step 4 — change Group by back to "None"; verify Track combobox would re-enable. Apply Track filter = "straight":
     - `rows = leaderboard.query("all", "all", "straight")`
     - Assert all returned rows refer only to the straight race's finishers (asserted indirectly: `len(rows)` matches the 4-racer turtle round count; specifically `len(rows) == 4`).
   - Step 5 — known_tracks reflects the planned 3 rounds:
     - `tracks_seen = leaderboard.known_tracks()`
     - Assert `set(tracks_seen) == {"straight", "spiral", "rectangular"}`.
   - Step 6 — Reset Session: monkeypatch `tkinter.messagebox.askyesno` to return `True`, call `leaderboard.reset_session()` directly (simulating what the GUI button does on Yes):
     - `leaderboard.reset_session()`
     - Assert `leaderboard.query("session", "all", "all") == []`.
     - Assert `len(leaderboard.query("all", "all", "all")) >= 6` (historic data on disk survives).
   - Step 7 — Reset All:
     - `leaderboard.reset_all()`
     - Assert `leaderboard.query("all", "all", "all") == []`.
     - Assert `leaderboard.known_tracks() == []`.
     - Re-load the JSON file directly and assert `data == {"schema_version": 1, "races": []}`.
   - On any failed assertion, print `[smoke] FAIL — <reason>` and `sys.exit(1)`.
   - On success, print `[smoke] leaderboard driver PASS` and return.

4. **Monkeypatch the full surface** before calling `main.main()`:
   - `dialogs.get_main_menu_choice = lambda: next(menu_choices)`
   - `dialogs.show_leaderboard = fake_show_leaderboard`  (the renamed-in-Plan-1.1 function)
   - `dialogs.get_user_track / get_user_species / get_user_bet / ask_play_again_choice` — same iterator pattern as Phase 3 smoke.
   - `audio.start_background_music = lambda: None` and `audio.stop_background_music = lambda: None`.
   - Also monkeypatch `tkinter.messagebox.askyesno = lambda *a, **kw: True` defensively (the driver above bypasses the GUI buttons, but if any code path inadvertently reaches `askyesno`, auto-confirm rather than blocking).

5. **After `main.main()` returns**, verify the on-disk JSON is `{"schema_version": 1, "races": []}` (Reset All in the driver wiped it). Print a clean PASS line and exit 0.

6. **Print one diagnostic line per significant step** (mirror the Phase 3 smoke's `[smoke] ...` prefix style).

Do NOT modify `tools/smoke_phase_3.py`. It is the Phase 3 historical smoke and remains functional against the renamed `show_leaderboard` (the smoke imports `dialogs.show_leaderboard_placeholder` — which IS broken-by-design after Plan 1.1, exactly as `tools/smoke_phase_2.py` was broken by Phase 3; documented under CONTEXT-4 Carryover).

NOTE on `dialogs._FILTER_LABEL_TO_KEY`: the smoke reads this dict via `dialogs._FILTER_LABEL_TO_KEY` to verify the translation table the GUI uses exists and contains the expected keys. The smoke driver does not strictly need it (it calls `leaderboard.query` with the enum values directly), but printing `[smoke] _FILTER_LABEL_TO_KEY has N entries: ...` provides a useful regression signal if Plan 1.1's translation dict drifts.
  </action>
  <verify>python tools/smoke_phase_4.py</verify>
  <done>`python tools/smoke_phase_4.py` exits 0 and prints `[smoke] leaderboard driver PASS` plus a final PASS line. The script must NOT require a display: it runs to completion on a builder that has Tk available but no interactive session (matches Phase 3 smoke's environment). After the script runs, the JSON in the tempdir contains `{"schema_version": 1, "races": []}` (the smoke's Reset All step wiped it). `pytest -q` still reports 135 passed (the smoke is not part of pytest collection — it lives under `tools/`, not `tests/`).</done>
</task>

## Acceptance Criteria

- `tools/smoke_phase_4.py` exists, follows the Phase 3 smoke's structural pattern, and exits 0 when run from the project root.
- The smoke exercises every CONTEXT-4 hard-constraint behavior (Group-by reshape, Track-filter disable rationale, both reset paths, empty-state precondition) at the API contract level — independent of the live Tk widget tree.
- The smoke does NOT modify `tools/smoke_phase_3.py` (CONTEXT-4 Carryover preserves it as historical artifact).
- The smoke does NOT modify `dialogs.py`, `main.py`, or `leaderboard.py` — it is a verification artifact only.
- `pytest -q` continues to report 135 passed (the smoke lives in `tools/`, not `tests/`).

## Verification

```powershell
python tools/smoke_phase_4.py            # exits 0, prints PASS
pytest -q                                # 135 passed (unchanged)
grep -nE "fake_show_leaderboard|_FILTER_LABEL_TO_KEY|reset_session|reset_all|query_per_track|known_tracks" tools/smoke_phase_4.py
                                         # >= 6 hits — confirms all major contract surfaces exercised
grep -cE "^def show_leaderboard\b" dialogs.py       # 1 — Plan 1.1 invariant preserved
```

The orchestrator runs `python tools/smoke_phase_4.py` after the builder finishes; the builder's environment may also run it directly (no display required since `show_leaderboard` is monkeypatched).
