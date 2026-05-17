# Simplification Review — Phase 3

## Priority Summary
- High: 0
- Medium: 2
- Low: 3

---

## Findings

### Medium Priority

#### 1. Structural duplication across the three new dialog functions in `dialogs.py`

- **Type:** Consolidate (with caveat — see below)
- **Effort:** Moderate
- **Locations:** `dialogs.py:38-64` (`get_main_menu_choice`), `dialogs.py:327-366` (`ask_play_again_choice`), `dialogs.py:369-399` (`show_leaderboard_placeholder`)

**Description:** All three new functions follow an identical five-step skeleton:

```python
dialog = tkinter.Toplevel()
dialog.title(...)
dialog.resizable(False, False)
# [widget construction]
dialog.protocol("WM_DELETE_WINDOW", ...)
dialog.transient()
dialog.grab_set()
dialog.wait_window()
```

The `Toplevel`-creation, `resizable`, `transient`, `grab_set`, `wait_window`, and `protocol` lines are identical boilerplate across all three. A `_modal_toplevel(title)` helper returning a configured `Toplevel` (or a context manager) could collapse about 4 lines per function.

**Why the duplication is acceptable as-is:** The three functions differ in load-bearing ways. `get_main_menu_choice` maps WM_DELETE_WINDOW to `"quit"` (Decision 3). `ask_play_again_choice` maps it to `"menu"` (Decision 4). `show_leaderboard_placeholder` maps it to `close` (equivalent to Close, Decision 2). These are distinct, documented semantic choices — not incidental variation. A shared `_modal_toplevel` helper that accepted the WM_DELETE_WINDOW handler as a parameter would abstract just 3-4 lines and introduce an additional indirection layer. Rule of Three applies for extraction; at only 3 occurrences and with modest per-site variation, the threshold is barely met.

**Suggestion:** If a fourth or fifth modal dialog is added in Phase 4 or 5 (the real `show_leaderboard` is a `ttk.Notebook` window — significantly more complex), reconsider extraction at that point. For now, accept the duplication and add a brief comment near the top of the three functions' block: `# All three follow the established modal pattern: Toplevel + grab_set + wait_window + WM_DELETE_WINDOW policy varies per dialog.`

**Impact if extracted now:** ~12 lines removed. Marginal gain; the per-dialog `WM_DELETE_WINDOW` semantics would still need per-function wiring. Defer.

---

#### 2. `screen.clear() + race.set_background()` pair repeated in `main.py`

- **Type:** Refactor
- **Effort:** Trivial
- **Locations:** `main.py:33-34` (top of inner race-rounds loop), `main.py:60-61` (`post == "menu"` branch)

**Description:** The two-line pair `screen.clear(); race.set_background()` appears twice in `main()`, performing the same operation (wipe the race canvas, redraw the lawn backdrop) for two different reasons: once at the top of each race round (to clear the previous round's drawing), and once on the `"menu"` post-race exit (to restore the lawn before the menu opens). The pair is short but the two call sites have subtly different semantic intent that a helper name could make explicit.

**Suggestion:** Extract a one-liner named `_restore_lawn(screen)` or leave it as-is. The case for extraction: it gives a single name to the operation ("restore the lawn backdrop"), making both call sites self-documenting. The case against: it is only 2 lines and the two call sites differ in their preceding context (one is top-of-loop, one is a post-race transition). A helper would make the code shorter but not meaningfully clearer. The CONTEXT-3 Carryover section explicitly reasons about this placement; inline code with a one-line comment at each site is an adequate alternative.

**Net recommendation:** If the pair grows to a third call site (e.g., when `show_leaderboard` in Phase 4 transitions back to the menu), extract then. For now, a one-line comment at `main.py:61` clarifying `# Redraw lawn so the menu backdrop is clean` suffices. This is a near-miss for extraction, not a clear win.

**Impact if extracted:** 2 lines saved across 2 call sites. Not material.

---

### Low Priority

1. **`dialog.transient()` no-op calls in all three new dialog functions.** `dialogs.py:60, 362, 397`. Already logged in ISSUES.md (Phase 3 Plan 1.1 Important). Not re-flagged as new; confirmed still open and unresolved. Trivial removal or fixup.

2. **`smoke_phase_3.py` shares ~60 lines of identical boilerplate with `smoke_phase_2.py`.** Both scripts: redirect `%APPDATA%` via `os.environ`, insert the project root into `sys.path`, import `dialogs` and `audio`, patch `audio.start/stop_background_music` to `lambda: None`, load and inspect the on-disk JSON after `main.main()` returns, accumulate `errors[]`, and exit non-zero on failure. The shared structure is substantial. However, each smoke is a phase-verification artifact scoped to a single phase's specific canned flows and assertion sets — they are not intended to be general-purpose test harnesses. A shared `tools/_smoke_helpers.py` with a `redirect_appdata()`, `silence_audio()`, and `verify_json(data, rounds, errors)` helper would reduce the shared mass. Rule of Three: only 2 smoke scripts exist currently; a third (Phase 4) would hit the threshold. **Defer extraction until Phase 4 needs its own smoke.** Effort if deferred: Moderate at that point (refactor 3 scripts simultaneously). Effort if done now with `smoke_phase_2.py` broken-by-design: Trivial for `smoke_phase_3.py` alone (extract helpers, Phase 2 smoke remains broken).

3. **`smoke_phase_3.py` docstring on `fake_show_leaderboard_placeholder` (lines 82-84) narrates the implementation rather than the intent.** The comment `# No-op stub for the smoke; the real placeholder just opens a Toplevel / the user dismisses. We just return control to the menu loop.` is correct but describes what the real function does, not why the stub does nothing. A shorter `# Stub: the menu loop calls this; we count the call and return.` would be tighter. Trivial.

---

## Non-findings (worth explicitly noting)

- **`selected = [None]` / `make_cb` sentinel pattern** — not flagged. Established repo convention; appears in all dialogs uniformly.

- **`dialogs.ask_play_again` deletion** — confirmed clean. `grep "^def ask_play_again[^_]" dialogs.py` returns zero hits. No dangling call sites in any production file. The atomic commit (`ba4e24b`) is the correct approach; flagged as a positive in REVIEW-2.1 and reinforced here.

- **`menu_choices` iterator sequencing bug in `smoke_phase_3.py`** — confirmed fixed in the committed version. The file at HEAD contains `menu_choices = iter(["race", "leaderboard", "race", "quit"])` (the corrected REVIEW-2.1 sequence), plus a `leaderboard_placeholder_calls` counter that is asserted to equal 1 post-run. The previously flagged ISSUES.md entry (Phase 3 Plan 2.1 Important) is resolved. This finding is closed.

- **`first_run` / `keep_playing` flags** — confirmed eliminated. `main.py` has zero hits. The two-boolean (`running`, `in_round_loop`) control structure is correct and without dead state.

- **Dead imports in `main.py`** — none. All six imports (`sys`, `audio`, `dialogs`, `leaderboard`, `race`, and indirectly `tracks` via `race`) are used in the current `main()` body.

- **`show_leaderboard_placeholder` docstring** — appropriately detailed given the Phase 4 handoff note ("Phase 4 will replace this function's body in-place"). The comment explaining the function name must stay stable is load-bearing design intent, not AI bloat.

- **`get_main_menu_choice` and `ask_play_again_choice` docstrings** — appropriately terse. They state the return values, the WM_DELETE_WINDOW policy, and the CONTEXT-3 decision references. No restating of the function name.

- **No try/except guards around code that cannot fail** — confirmed. None of the three new dialog functions wrap their `Toplevel` creation or `grab_set` in try/except.

- **No over-defensive null checks** — confirmed. The `selected[0]` is set before `dialog.destroy()` in every code path (all three WM_DELETE_WINDOW handlers call `make_cb(value)` which sets then destroys, or `close()` which just destroys with `None` as the accepted return value for `show_leaderboard_placeholder`).

- **`tools/smoke_phase_2.py`** — broken by design; intentionally not analyzed for simplification (Phase 2 historical artifact, documented in CONTEXT-3 Carryover).

- **Phase 1 open findings** — the unreachable `raise ValueError` in `leaderboard.py:187` (High) and redundant `import json` in test file (Low) from the Phase 1 simplification report: not re-introduced in Phase 3 (Phase 3 does not touch `leaderboard.py` or `tests/test_leaderboard.py`). Remain open per their original status.

---

## Verdict

Phase 3 production code (`dialogs.py`, `main.py`) is clean and well-structured. The two Medium findings are both near-misses for extraction — the modal-pattern duplication is justified by per-dialog semantic differences explicitly documented in CONTEXT-3, and the `screen.clear() + race.set_background()` repetition is 2 lines at 2 call sites with different surrounding intent. Neither warrants action before Phase 4 ships. The three Low findings are cosmetic or deferred-by-design (smoke boilerplate consolidation deferred until a third smoke script justifies the extraction). The most significant Phase 3 code event — the `menu_choices` sequencing bug caught by REVIEW-2.1 and corrected before the phase closed — is confirmed resolved in the committed version. No simplification is required before Phase 4 begins.
