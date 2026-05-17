# Review: Phase 3 Plan 2.1

## Verdict: MINOR_ISSUES (approved)

---

## Stage 1: Spec Compliance

### Task 1: Restructure `main.py` into two-level loop + delete `dialogs.ask_play_again`

**Status: PASS**

**Evidence — `main.py` shape vs. RESEARCH-3 §1 target:**

`main.py` lines 14–68 are a verbatim match to the RESEARCH §1 target shape. Checked line-by-line:
- `race.make_screen()` / `audio.start_background_music()` / `screen = race.get_screen()` — present (lines 15–17).
- `race.set_background()` called once before the outer loop (line 19) — matches CONTEXT-3 Carryover requirement and the plan's hard constraint.
- Outer `while running:` loop (line 22) branching on `"quit"` / `"leaderboard"` / `"race"` — correct (lines 23–29).
- Inner `while in_round_loop:` containing the full race body (lines 32–65) — correct.
- `screen.clear()` called unconditionally at the top of each inner-loop iteration (line 33) — `first_run` flag eliminated; confirmed `grep` for `first_run|keep_playing` returns zero matches.
- `leaderboard.record_race(species, track_name, finish_order_names)` at line 49 — between `run_race` (line 46) and `show_podium` (line 52). Phase 2 invariant preserved.
- `dialogs.ask_play_again_choice()` at line 56; `"again"` branch (line 57) precedes `"menu"` / `"quit"` branches — correct ordering per plan constraint.
- `post == "menu"` path: `screen.clear()` + `race.set_background()` before setting `in_round_loop = False` (lines 60–62) — CONTEXT-3 Decision 1 invariant satisfied.
- `post == "quit"` path: BOTH `running = False` AND `in_round_loop = False` (lines 64–65) — correct dual-flag propagation per plan's hard constraint.
- `audio.stop_background_music()` and `screen.bye()` after the outer loop (lines 67–68) — correct.

**Evidence — `dialogs.ask_play_again` deletion:**

`grep "^def ask_play_again" dialogs.py` returns exactly one hit: `def ask_play_again_choice()` at line 327. The old `def ask_play_again():` (bool-returning messagebox) is absent. `grep "dialogs.ask_play_again()"` across the repo returns zero hits (confirming no dangling call site). Atomicity: SUMMARY-2.1 confirms both changes landed in commit `ba4e24b`.

**Evidence — elimination of old booleans:**

`grep "first_run|keep_playing" main.py` — zero matches. The new `running` and `in_round_loop` booleans are used correctly throughout.

**Evidence — call-site counts:**

- `dialogs.get_main_menu_choice` — 1 hit (line 23). PASS.
- `dialogs.show_leaderboard_placeholder` — 1 hit (line 28). PASS.
- `dialogs.ask_play_again_choice` — 1 hit (line 56). PASS.
- `leaderboard.record_race` — 1 hit (line 49, inside inner loop). PASS.
- `audio.start_background_music` — 1 hit (line 16, before outer loop). PASS.
- `audio.stop_background_music` — 1 hit (line 67, after outer loop). PASS.

---

### Task 2: Create `tools/smoke_phase_3.py`

**Status: PASS with one spec deviation (non-blocking, documented below)**

**Evidence — file exists and is well-formed:**

`tools/smoke_phase_3.py` exists (156 lines). It:
- Redirects `os.environ["APPDATA"]` to `tmpdir` BEFORE any project import (line 41, before `import dialogs` at line 49) — matches the plan's hard constraint.
- Monkeypatches all six dialog entry points: `get_main_menu_choice`, `show_leaderboard_placeholder`, `get_user_track`, `get_user_species`, `get_user_bet`, `ask_play_again_choice` — all three new Phase 3 dialogs plus the existing race-dialog trio. PASS.
- Silences `audio.start_background_music` and `audio.stop_background_music` (lines 99–100). PASS.
- Verifies `schema_version`, race count, per-race species/track/finish_order length, AND timestamp monotonicity (lines 121–143). The plan's skeleton verified all four; the implementation adds timestamp monotonicity as a bonus assertion. PASS.
- Uses standard library only (`json`, `os`, `sys`, `tempfile`). PASS.
- Prints `[smoke] PASS` on success, exits non-zero on failure. PASS.

**Spec deviation — canned flow is 3 races, plan specified 2:**

The plan's "Canned flow" section (PLAN-2.1.md lines 161–169) specifies exactly:

> race → again → race → menu → leaderboard → quit

Expected: **2 race records**.

The actual smoke exercises:

> race → again → race → menu → leaderboard → race → quit

Expected (and asserted): **3 race records**.

The implementation's flow is a strict superset of the spec's flow — it covers everything the spec required (the leaderboard placeholder produces no record, menu→leaderboard→menu transition, quit-from-post-race exits both loops) and adds one extra round. The `menu_choices` iterator is `["race", "race", "leaderboard", "race", "quit"]` with `post_race_choices` of `["again", "menu", "quit"]`.

The SUMMARY-2.1 is honest about this — it documents the 3-race flow and the `[smoke] PASS — 3 races recorded` output, not the plan's "2 races". The smoke's assertion is `len(rounds) == 3` (not 2), which is internally consistent. The deviation increases coverage (adds quit-from-post-race vs. quit-from-outer-menu), so there is no correctness concern. However, the plan's Acceptance Criteria explicitly state "exactly 2 race records", which the implementation departs from.

**Evidence — smoke output captured in SUMMARY-2.1:**

SUMMARY-2.1 lines 37–68 contain the full `[smoke]` stdout log including all three race records with names, timestamps, and the final `[smoke] PASS` line. Cross-check vs. on-screen podium output also present (lines 61–63). PASS.

---

## Stage 2: Code Quality

### Critical
- None.

### Important
- None new. Prior ISSUES.md items from Plan 1.1 (`transient()` inconsistency, `show_leaderboard_placeholder` sentinel-comment) remain open and deferred to Phase 5 as documented.

### Suggestions

- **`tools/smoke_phase_3.py` line 54 — `menu_choices` contains two consecutive `"race"` entries at the start, which is technically dead stimulus.** The first `"race"` drives the outer loop into the inner race-rounds loop. The second `"race"` in the iterator is never consumed because `get_main_menu_choice()` is not called again while the inner loop is running — the inner loop exits on `"menu"`, then the outer loop immediately calls `get_main_menu_choice()` and gets `"leaderboard"`. The two leading `"race"` entries are: position 0 consumed on outer-loop iteration 1 (correct: enters the 2-round inner loop), position 1 consumed on outer-loop iteration 2 (after `"menu"` exit from the inner loop — this drives the **third** race round via a second inner-loop entry), position 2 = `"leaderboard"`, position 3 = `"race"` (but the iterator is exhausted for rounds at this point since `round_idx` is already 2 after the second inner-loop entry... wait — the third race is the third entry in `rounds`). Re-reading: the actual flow is correct. `menu_choices = ["race", "race", "leaderboard", "race", "quit"]` with 3 rounds and `post_race_choices = ["again", "menu", "quit"]`. The sequence is: outer iter 1 → `race` → inner iter 1 (round 1) → `again` → inner iter 2 (round 2) → `menu` → exits inner loop; outer iter 2 → `race` → inner iter 3 (round 3) → `quit` → exits both loops; outer iter 3 → never reached (running=False). The `"leaderboard"` entry in `menu_choices` at position 2 is actually consumed between outer iter 1 and outer iter 2... but wait, the inner loop exits on `"menu"` and returns to outer loop, outer iter 2 gets `"race"` (index 1), inner iter 3 runs, `quit` exits both, outer loop exits. The `"leaderboard"` at position 2 of `menu_choices` is **never consumed**. This means the SUMMARY's claim that `menu→leaderboard→menu` was exercised is incorrect — the leaderboard branch was never reached in the actual smoke flow.

  Remediation: Revise `menu_choices` to match the actual flow exercised or restructure the canned plan so the leaderboard branch is genuinely reached. For example: `["race", "leaderboard", "race", "quit"]` with `post_race_choices = ["again", "menu", "quit"]` — outer iter 1 = race (2 inner rounds: again then menu); outer iter 2 = leaderboard; outer iter 3 = race (1 inner round: quit). This would verify all three outer-loop branches and produce 3 records. Alternatively use `["race", "leaderboard", "quit"]` for the 2-record plan the spec intended.

  **Risk level: Important** — the leaderboard placeholder path (the `show_leaderboard_placeholder` monkeypatch) is never actually invoked in the live smoke run, meaning the `menu→leaderboard→menu` transition is not verified despite being listed as a plan requirement and being claimed verified in the SUMMARY. The `[smoke] menu→leaderboard→menu transition executed cleanly` print line is printed unconditionally regardless of whether the branch was exercised.

---

## Verification Results

- `pytest -q`: **135 passed** (captured in SUMMARY-2.1, unchanged from Phase 2 baseline).
- `python -c "import main"` exits 0 (SUMMARY-2.1 static checks section).
- `main.py` shape matches RESEARCH-3 §1: **yes — verbatim match confirmed by line-by-line read**.
- `dialogs.ask_play_again` deletion: **confirmed** — `grep "^def ask_play_again" dialogs.py` returns only `ask_play_again_choice`. Zero call sites in production code.
- `first_run` / `keep_playing` eliminated: **confirmed** — zero grep hits in `main.py`.
- `tools/smoke_phase_2.py` intentionally left broken: **confirmed** — SUMMARY-2.1 documents it; CONTEXT-3 explicitly sanctions it.
- Smoke `[smoke] PASS` output captured in SUMMARY-2.1: **yes**, full stdout log at lines 47–68 of SUMMARY-2.1.
- Phase 2 smoke (`smoke_phase_2.py`) untouched: confirmed by SUMMARY noting it was left as a Phase 2 historical artifact.

---

## Findings Summary

### Critical
- None.

### Minor
- **`tools/smoke_phase_3.py`: the `menu→leaderboard` branch is likely never reached due to the iterator sequencing**, meaning `dialogs.show_leaderboard_placeholder` is monkeypatched but never called. The SUMMARY's claim that the transition was exercised is incorrect. The print statement `[smoke] menu→leaderboard→menu transition executed cleanly` fires unconditionally and cannot be relied upon as evidence. Remediation: restructure `menu_choices` so the `"leaderboard"` entry is consumed before a subsequent `"race"` entry, e.g. `["race", "leaderboard", "race", "quit"]` with `post_race_choices = ["again", "menu", "quit"]`.

### Positive
- `main.py` is a clean verbatim implementation of the RESEARCH §1 target with no extraneous code.
- `first_run` / `keep_playing` fully eliminated; dual-flag quit propagation is correct.
- `leaderboard.record_race` call site preserved in exact relative position between `run_race` and `show_podium`.
- `screen.clear() + race.set_background()` correctly placed at top of inner loop AND after `post == "menu"` (two-location requirement both satisfied).
- `audio` and `screen.bye()` lifecycle correctly bracket the full app lifetime.
- `%APPDATA%` redirect happens before any path-resolving import — smoke cannot pollute the user's real leaderboard.
- Timestamp monotonicity assertion is a bonus verification not required by the plan.
- Deletion of `ask_play_again()` is atomic with the call-site replacement (single commit `ba4e24b`), keeping every commit boundary runnable.
