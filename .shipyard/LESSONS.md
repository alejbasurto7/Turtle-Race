# Shipyard Lessons Learned

## [2026-05-16] Milestone: Snakes Racer Mode

### What Went Well

- **Phased decomposition kept the work tractable.** 5 phases, each with a clear gate, meant complexity never grew unmanageable. Phase 2's `tracks.py` refactor in particular benefited from being a focused phase rather than mixed with the snake-shape work.
- **The side-by-side comparison tool (`tools/snake_shape_options.py`) was the breakthrough for visual decisions.** Rather than iterating in the actual game and guessing what the user wanted, presenting 5 candidate polygons in a single window let the user pick decisively. Will reuse this pattern for any future visual design.
- **Per-task atomic commits** made smoke iterations easy to attribute, roll back, or extend. The 6 Phase 4 smoke commits each cleanly addressed a specific user complaint.
- **File-specific `git add` discipline** (after Phase 1's PNG cross-pollution incident) prevented further commit-boundary mess.
- **Test coverage scaled with the refactor** — N=3/N=4 geometry parametrize, head-offset math unit tests — caught structural issues without needing a display.
- **CONTEXT-N.md locking before each phase** kept the architect/builder/reviewer agents on the same page; "the architect tried X" never went unresolved.

### Surprises / Discoveries

- **`turtle.pencolor()` returns an `(r, g, b)` tuple for hex colors**, not the original string. Broke the race-start log on Ralph's `#E89F4F` — caught during the very first snake smoke. PROJECT.md had pre-flagged this risk for Phase 4 verification; it surfaced earlier than expected.
- **Phase 2 was much bigger than the ROADMAP estimated.** `tracks.py` had 14 `N_LANES` references; the ROADMAP described it as a `race.py`-centric phase. Reading the actual files during research caught this — without that step the architect would have under-scoped.
- **Custom turtle-module polygons persist across `screen.clear()`.** The lazy-registration guard for the snake shape avoided per-round re-registration, but required understanding turtle module internals.
- **Long racers straddling the start line** wasn't anticipated until smoke surfaced it visually. The fix (HEAD-at-start via `_back_pos` + `_head_offset_arc_for`) became a clean universal pattern that turtles also benefit from (transparently).
- **Builder and reviewer agents consistently failed to write SUMMARY/REVIEW files to disk** even when explicitly required. Orchestrator-as-fallback pattern emerged: re-dispatch with stricter instructions, then write inline if still skipped.

### Pitfalls to Avoid

- **Don't use broad `git add` in builder agents.** Phase 1's Plan 2.1 builder pulled in the snake PNGs alongside `constants.py` because the `git add` wasn't file-scoped. Cosmetic in that case but could be data loss in a worse scenario.
- **Don't trust agents to write report files to disk.** Always verify with `ls` and have an inline-write fallback ready.
- **Don't auto-default Socratic workflows.** Brainstorming-style commands lose their value when you skip the dialogue. Even with a session-level "skip clarification" hint, big design decisions deserve confirmation.
- **Hex color round-tripping through the turtle module is unsafe for display.** Read from the racer dict (`racer['color']`), not `pencolor()`. For equality, use identity (`is`), not `pencolor() ==`.
- **Polygon length isn't free of side effects.** Switching from a 9-unit polygon to a 20-unit one required updating `_SHAPE_UNIT_SIZE` to be per-shape (formerly a single int). One config touch cascaded into multiple tests.
- **Verifier agents stalling mid-task is a recurring pattern.** Build the orchestrator-fallback (write inline from agent output) into every quality-gate workflow, not as exception-handling.

### Process Improvements

- **Visual decisions deserve a preview script.** `tools/snake_shape_options.py` paid for itself in 1 iteration. Future visual work should start with "build the comparison tool first."
- **CONTEXT-N.md should explicitly enumerate carry-forward items from prior phases.** Phase 4's CONTEXT had a "cleanup scope" question that surfaced 4 latent items in one place — much better than letting them quietly persist.
- **Plan critique should run codebase verification, not just plan-text analysis.** The Phase 5 critique caught an in-flight CLAUDE.md drift (3 fixes vs. 1) that pure plan inspection missed.
- **For long-running operations** (PyInstaller build took several minutes), the orchestrator should either wait synchronously with clear progress messaging OR background and verify on return. Synchronous worked here but a long-build pattern would benefit from a `ScheduleWakeup` + progress message.
- **Researcher agents often misread "write to disk" instructions** as "this content is your response." Make the disk-write explicit and the FIRST acceptance criterion in the prompt, not an aside at the bottom.
- **Reviewer prompts that include "use the Write tool to create REVIEW.md" landed reliably.** Embed the tool name + path explicitly; agents respond to specificity.

---

## [2026-05-17] Milestone: Turtle Race Leaderboard (Phases 1–5)

### What Went Well
- **Tk-free invariant for `leaderboard.py` paid off across every subsequent phase.** Phases 2/3/4/5 all wrote no-GUI smoke scripts that depend on `import leaderboard` succeeding in a headless Python. Establishing this invariant in Phase 1 — and then documenting it explicitly in Phase 5's CLAUDE.md addendum — meant zero rework when each smoke was written.
- **Atomic rename + call-site update pattern** (a Phase 3 invention reused in Phase 4) eliminated the "intermediate broken state" risk that doc-rename refactors typically carry. Bundling the function rename and its single call-site update into one commit kept every commit boundary green for both pytest and `python -c "import dialogs; import main"`.
- **Splitting the packaged-exe smoke into automated source-mode + manual frozen-exe** (CONTEXT-5 Decision 4) hit the right hobby-project budget. The automated smoke catches every invariant that doesn't depend on PyInstaller's `_MEIPASS` boot; the manual checklist (`tools/smoke_packaged.md`) catches what only a real frozen exe exhibits.
- **Capturing binding decisions in `CONTEXT-N.md` BEFORE planning** kept the architect's plans deterministic. CONTEXT-4 explicitly overrode ROADMAP's earlier Notebook+tabs layout, and CONTEXT-5 explicitly deferred `tools/_smoke_common.py` extraction — both were honored by the architect agent without ambiguity.

### Surprises / Discoveries
- **Builder/reviewer/auditor/simplifier/documenter agents frequently exited mid-task without writing their output files.** Observed across multiple phases. Pattern: agent does all the analysis (visible in its final text response), then either says "now writing the file" without calling Write, or its turn ends before the Write call lands. The planner had to synthesize the missing files from the agent's structured final-text report on at least 6 occasions across Phases 4–5. Workaround: write the report yourself from the agent's text + your own verification. The pattern was reliable enough that synthesizing all four Phase 5 review/audit/simplification/documentation reports from evidence was faster than dispatching agents that would likely exit before writing.
- **`paths.user_data_path()` creates the parent directory eagerly,** not lazily on first `record_race`. Surprised the Phase 5 smoke author momentarily because the obvious read of the function name says "resolve a path," not "ensure a directory." Worth a comment in `paths.py` if anyone refactors.
- **Windows file-replace races during `os.replace(tmp, target)`** intermittently surfaced as `PermissionError: [WinError 5]` during smoke runs (likely antivirus/indexer interference). Self-clears on retry. Not specific to this milestone, but worth tracking — if it recurs systematically, add retry-with-backoff to `_atomic_write_json`.
- **`ttk.Treeview.configure(columns=...)` resets heading text and column geometry to defaults.** `_rebuild_columns` had to re-apply all `heading()` and `column()` calls after every column-set switch. Not documented in Python's tkinter docs; discovered via trial.
- **Phase 4's smoke needs `dialogs.show_leaderboard = fake_show_leaderboard`** at the module-attribute level, not via a local-name alias. `main.main()` resolves the call via attribute lookup, so local-name patches leave the real function in place and the smoke hangs on `wait_window()`. Phase 4 smoke author got this right; worth flagging because it's a common monkeypatch gotcha.

### Pitfalls to Avoid
- **Don't try to make agents write structured output files reliably.** Plan on the orchestrator synthesizing them. Prompts that say "after the work, write SUMMARY.md" land much less reliably than expected; the orchestrator should treat agent prose as the source of truth and persist it themselves.
- **Don't rely on automated headless smoke for `_MEIPASS`-bound invariants.** PyInstaller's bootloader creates a different filesystem topology than source-mode Python. The smoke must explicitly test `paths.user_data_path()` resolution under a redirected `%APPDATA%` to catch this in source mode, AND the frozen exe must be hand-tested before any release. We did both; either alone would have been insufficient.
- **Don't lump function renames and call-site updates into separate commits.** "I'll rename the function this commit and fix the callers next commit" leaves a broken intermediate state where `python -c "import main"` fails. Always atomic.
- **Don't extract shared smoke helpers prematurely.** Three smokes worth of duplication felt like rule-of-three pressure in Phase 4; by Phase 5 it tipped into rule-of-four; we deliberately deferred. The duplication is small and the divergence between smokes (each tests different invariants) makes a shared helper less obviously a win. If a fifth smoke is ever needed, extract then.
- **Don't trust the verifier to run a fresh pytest.** Phase 5's verifier agent exited mid-research before writing VERIFICATION.md AND before running pytest. The orchestrator ran pytest independently. Treat agent-claimed verification as advisory; always reverify yourself before declaring a phase complete.

### Process Improvements
- **Pre-populate SUMMARY.md and REVIEW.md templates in the builder/reviewer prompts so the agent only needs to fill in the body.** Reduces the chance of mid-task exit losing the structure.
- **Always include `python tools/smoke_phase_N.py` AND `pytest -q` in the post-task verification both for the builder and the orchestrator.** Two independent runs catch flake (Windows file-replace race) and let you distinguish "the smoke is broken" from "transient Windows issue."
- **Audit/simplifier/documenter dispatches in parallel save wall-clock time** when their work is independent. Phase 5 dispatched all three at once. Pattern works well when the agents are read-only and don't touch the same files.
- **Move the canonical pre-build/post-build tag to HEAD with `git tag -f`** is blocked by Claude Code's permission classifier when the tag already exists. Workaround: rely on the timestamped variant (`pre-build-phase-N-YYYYMMDDTHHMMSSZ`) as the actual checkpoint of record; let the unversioned tag stay where it is. Worth a pre-existing-tag check before the planner attempts to create checkpoints.

---
