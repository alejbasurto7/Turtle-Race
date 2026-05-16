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
