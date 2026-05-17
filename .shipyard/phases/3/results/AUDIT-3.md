# Security Audit — Phase 3

(Captured verbatim by the orchestrator from the auditor agent's structured output; the agent did not persist this file directly.)

## Verdict: PASS — Risk Level LOW

## Threat Model Summary

Phase 3 is GUI plumbing only — three new Tk modal dialogs, a restructured two-level loop in `main.py`, and a no-GUI smoke utility. No new network, I/O, or auth surface. All values flowing through the new control structure are hardcoded string literals bound at button-callback construction time. STRIDE applied: no spoofing/elevation surface (no identity), no tampering surface (no user free-form text), no information disclosure (no new logs/displays of stored data), no denial-of-service surface beyond existing `grab_set`+`wait_window`, no repudiation concern (the `record_race` call site is preserved in the same relative position).

## Findings

### Critical / Important
- None.

### Low / Informational

**[L-P3-1] Theoretical `None` return from `get_main_menu_choice()` if Tk root is destroyed externally** — `dialogs.py:42`, `main.py:23-30`. `selected = [None]` is initialized; all four destruction paths route through `make_cb(value)` with concrete string literals, so under normal operation `selected[0]` ∈ `{"race", "leaderboard", "quit"}`. If the underlying Tk root is destroyed externally (e.g., Task Manager kill) while the dialog is open, `wait_window()` could return with `selected[0] is None`. In `main.py`, a `None` choice would not match `"quit"`/`"leaderboard"` and fall through to the implicit `"race"` branch. **Realistic exposure: near-zero** — requires OS-level forceful termination of a single-user local game. **Optional remediation:** `assert choice in ("race","leaderboard","quit")` for explicit-fail on the implausible case. CWE-617. Non-blocking.

**[L-P3-2] Smoke tempdir not cleaned up on exit** (carried from Phase 2) — `tools/smoke_phase_3.py:40`. `tempfile.mkdtemp(...)` creates a per-run directory under `%TEMP%` that's never removed. Developer-tool hygiene only; no security implication. Optional `try/finally: shutil.rmtree(tmpdir, ignore_errors=True)` if cleanup matters.

## Cross-Component Data Flow

- **Menu choice constrained to "race" | "leaderboard" | "quit": PASS.** Verified by `dialogs.py:31-64` inspection — string literals bound at button-callback construction time; closure captures `value` at definition, not at call.
- **`record_race` input chain (controlled enumeration): PASS — unchanged from Phase 2.** `species`, `track_name`, and `finish_order_names` all originate from hardcoded dispatch tables (`constants.SPECIES`, `tracks.*` constants, `SPECIES[species]["names"]`).
- **Exit cleanup runs on all intentional paths: PASS.** Menu Quit → `running=False; break`. Post-race Quit → both flags False, inner exits, outer condition fails. Menu X → `make_cb("quit")` → same as Menu Quit. Post-race X → `"menu"` → returns to outer loop (not quit). All paths reach `audio.stop_background_music()` + `screen.bye()` at `main.py:67-68`.

## Closed / Unchanged Prior-Phase Findings

| Finding | Status |
|---|---|
| L1 path-traversal (Phase 1) | CLOSED in Phase 2 by basename guard. Unchanged. |
| L2 symlink/quarantine clobber (Phase 1) | Unchanged. Informational. |
| L3 mkstemp 0o666 on Windows (Phase 1) | Unchanged. Informational. |
| L4 concurrent-process race (Phase 1) | Unchanged. Informational. |
| Phase 2 Advisory: unguarded `record_race` disk errors | Carries forward by design (CONTEXT-2 Decision 1: "persistence failure should be visible"). |
| ISSUES.md item "Phase 3 Plan 2.1 — leaderboard branch may not actually be exercised" | **RESOLVED** in commit `e159fc4` (smoke fix). ISSUES.md should be updated to mark closed. |

## Dependency / IaC / Configuration Changes

| Item | Status |
|---|---|
| `requirements.txt` | unchanged |
| `turtle_race.spec` | unchanged |
| Config files | none in diff |
| IaC / Docker | N/A |

## Recommendation

Proceed to ship of Phase 3. No security action required. Optional 1-line `assert` on the menu-choice return would close L-P3-1 if desired.
