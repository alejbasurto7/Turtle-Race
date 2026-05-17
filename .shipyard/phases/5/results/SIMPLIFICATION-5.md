# Simplification Review — Phase 5

## Verdict: clean

## Findings

### High priority (fix now or plan for Phase 5)
- None.

### Medium (consider)
- **`tools/_smoke_common.py` extraction now has 4 callers in scope.** With `smoke_phase_5.py` landing, the env-redirect + tempdir + `[smoke]` log preamble exists in four files (`smoke_phase_2.py` broken-by-design, `smoke_phase_3.py`, `smoke_phase_4.py`, `smoke_phase_5.py`). Three of them are LIVE smokes. The rule-of-three-into-four pressure is real. Per CONTEXT-5 Decision 6, this extraction was deliberately deferred from Phase 5 to avoid scope creep on the polish-and-ship phase. The decision should be revisited in any post-Phase-5 maintenance work:
  - **If a Phase 6+ is opened** for any reason (new feature, bug fix, etc.), bundle the `tools/_smoke_common.py` extraction there.
  - **If no Phase 6 is opened**, log a tracking entry in `.shipyard/ISSUES.md` so the duplication doesn't quietly grow.
- **`smoke_phase_5.py` and `smoke_phase_4.py` share their env redirect + tempdir creation pattern almost line-for-line.** The body diverges (phase_5 calls only `paths`/`leaderboard`; phase_4 also monkeypatches the dialog surface), but the first ~30 lines could become a shared helper. Same conclusion as above — defer.

### Low / aesthetic
- **Em-dash in `[smoke] phase 5 smoke PASS — path resolution + file lifecycle verified`.** Cosmetic terminal-rendering issue on default Windows code pages. Could be replaced with `--`. Cosmetic; not worth a commit on its own.
- **`smoke_packaged.md` has 13 checklist boxes (3 pre-flight + 10 steps).** Reads slightly long for a one-pass human gate, but the redundancy (re-verifying file state after Reset Session AND Reset All) is the whole point of the checklist. Don't trim.

## Positive observations
- **Phase 5 introduced zero new abstractions.** No new classes, no new module-level helpers, no new "framework"-shaped code. The smoke is procedural top-to-bottom in `main()`, matching Phase 3/4's pattern.
- **Zero dead code introduced.** Every symbol added in `tools/smoke_phase_5.py` is referenced. No unused imports.
- **No defensive try/except blocks around impossible failures.** The smoke uses bare assertions with `[smoke] FAIL — <reason>` + `sys.exit(1)` on the unhappy path. No swallow-and-fallback.
- **No verbose error messages on internal-only invariants.** The `[smoke] FAIL` strings are terse and grep-friendly.
- **The CLAUDE.md addendum is the right size** (11 lines) — well within the plan's 10–20 target. Doesn't try to summarize Phase 1's implementation; just documents the invariants downstream code depends on.
- **The `turtle_race.spec` comment is two lines and exactly two lines.** No verbosity, no temptation to expand into a full design doc.
- **No premature abstraction in either new artifact.** The smoke could have been factored into a `class Phase5Smoke` with steps as methods — it wasn't. The checklist could have been a YAML data structure with a Jinja template — it wasn't. Both are flat, scannable, and grep-friendly.

## Recommendations
- **Now:** None blocking. Ship Phase 5 as-is.
- **Post-ship / Phase 6+:** Revisit the `tools/_smoke_common.py` extraction. The rule-of-three threshold is now in rule-of-four territory.
- **Optional, never:** The em-dash in the PASS banner. Cosmetic and not worth a commit on its own.
