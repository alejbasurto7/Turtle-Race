# Phase 3 Plan Critique — Feasibility Stress Test

## Verdict: **READY** (after dropping PLAN-2.2)

Plans 1.1 and 2.1 are feasible and well-grounded against the actual codebase. **PLAN-2.2 was dropped** as redundant with the build workflow's standard reviewer dispatch — its checklist content will be folded into the reviewer prompts at build time.

## PLAN-2.2 disposition: DROPPED

**Architect's intent (sound):** Phase 2 reviewer agents consistently skipped writing `REVIEW-W.P.md` to disk. PLAN-2.2 elevated review to a "plan" with the disk artifact as the formal acceptance criterion to force the write.

**Problem with the implementation:** The Shipyard `/shipyard:build` workflow's Step 4c automatically dispatches a reviewer agent for each completed plan. If PLAN-2.2 itself runs as a "build" plan whose tasks are review work, then:
- The build workflow's Step 4c would then dispatch *yet another* reviewer for PLAN-2.2 — reviewer reviewing a review
- The build workflow expects builder agents (`shipyard:builder`) to do code work, not review work
- Standard `SUMMARY-2.2.md` and `REVIEW-2.2.md` would be produced for a plan that has neither implementation nor verifiable test coverage

**Resolution:** PLAN-2.2 deleted. Its review checklist (signature parity, layout constant placement, modal correctness, image-ref retention, branch parity, no helper extraction, regression scan, Phase 4 carry-over capture) is **excellent** and will be embedded verbatim into the standard reviewer prompts that the build workflow dispatches for PLAN-1.1 and PLAN-2.1.

**Forced disk-write mechanism (instead):** Each reviewer prompt the orchestrator dispatches in `/shipyard:build 3` will include the explicit instruction:

> WRITE `.shipyard/phases/3/results/REVIEW-{W}.{P}.md` to disk before returning. This is the primary acceptance criterion. If the agent returns review findings as chat text without the file on disk, the work is INCOMPLETE.

Fallback: if a reviewer still skips the disk write, the orchestrator writes the REVIEW file inline from the agent's chat output — same pattern that worked in Phase 1 and Phase 2.

## PLAN-1.1 — Wave 1: constants + `get_user_bet(species)` refactor

**Verdict: READY**

- **File paths exist:** ✓ `dialogs.py` (line 11 has `def get_user_bet():`), `constants.py`, `tests/test_constants.py`.
- **API surface accurate:**
  - `dialogs.get_user_bet()` is currently a zero-arg function at `dialogs.py:11` — plan correctly identifies this as the refactor target.
  - `main.py:34` calls `dialogs.get_user_bet()` (zero args) — plan correctly identifies this as the call site that will be runtime-broken after Wave 1 lands (intentional, fixed in Wave 2).
  - `constants.SPECIES`, `BET_IMAGE_SIZE`, `TURTLE_NAMES`, `TURTLE_IMAGES`, `SNAKE_NAMES`, `SNAKE_IMAGES` all present.
- **Verification commands runnable:** `pytest`, `python -c "from dialogs import get_user_bet; import inspect; assert 'species' in inspect.signature(get_user_bet).parameters"`.
- **Intentional runtime breakage** (same pattern as Phase 2 Wave 1): `main.py` still calls `get_user_bet()` zero-arg; that call breaks at runtime until Wave 2 wires `species`. `pytest` stays green because no test exercises `get_user_bet()` directly (it's a Tk-modal dialog, not unit-testable without a display). Acceptable.
- **Complexity:** 1 file refactored + 1 constant + 1 optional test. Low.

## PLAN-2.1 — Wave 2: `get_user_species()` + `main.py` wire-up + manual smoke

**Verdict: READY (with mode-conversion caveat)**

- **File paths exist:** ✓ All required files including the 4 turtle JPGs and 3 snake PNGs (`assets/snakes/{Shadow,Ralph,Anaconda}.png`).
- **API surface accurate** for `race.create_racers`, `main.py` call sites, etc.
- **Image composition feasibility — CAUTION:**
  - Turtle source assets are **JPG (RGB mode)**; snake source assets are **PNG (RGBA mode)**. PIL `Image.paste()` between RGB destination and RGBA source needs explicit alpha handling, or the alpha channel becomes literal color data.
  - **Recommended approach:** create the composite as `Image.new("RGBA", (w, h), (255, 255, 255, 0))`, convert each source to RGBA via `img.convert("RGBA")` before paste, then either keep as RGBA or composite onto white before `ImageTk.PhotoImage`. This handles the mode mismatch cleanly.
  - The plan should mention this explicitly. If not currently in PLAN-2.1, the architect or builder needs to bake this into the implementation. Builder prompt should include this constraint.
- **`n = len(racers)` hoist:** mechanical — `main.py` currently calls `len(racers)` 3 times in adjacent lines (28-32 area). Easy win.
- **`create_racers` docstring add** (DOCUMENTATION-2 actionable): mention `species` is a `SPECIES` key and returned dicts include `'name'`. Trivial.
- **Manual smoke:** the gate. Same `PENDING_HUMAN_VERIFICATION` pattern as Phase 2 — no autonomous way to verify Tk rendering.
- **Complexity:** 3 files modified, possibly 1 docstring update to `race.py`. Low-Medium.

## Cross-plan analysis

### Wave ordering

- Wave 1 (PLAN-1.1) → Wave 2 (PLAN-2.1). Sequential and correct.
- PLAN-2.1 depends on PLAN-1.1 — `get_user_bet(species)` signature must exist before `main.py` can pass `species` to it.

### File conflicts

- Wave 1: `dialogs.py` + `constants.py` + optionally `tests/test_constants.py`.
- Wave 2: `dialogs.py` (additional — new `get_user_species`) + `main.py` + optionally `race.py`.
- Sequential waves; no in-wave parallelism. No conflicts.

### Builder-prompt reminders

Both plans include the carried-forward Phase 2 reminders (SUMMARY disk write, file-specific `git add`, per-task commits). Good.

### Image-composition note for PLAN-2.1's builder

When dispatching the PLAN-2.1 builder, the orchestrator MUST include this guidance in the prompt:

> For the species dialog composite images, handle the JPG/RGBA mode mismatch explicitly. Convert each source image to RGBA via `img.convert("RGBA")` before pasting onto a composite canvas. The PIL paste operation otherwise silently corrupts the snake alpha channel into color data.

## Items to be aware of (not blocking)

1. **Image composition mode mismatch** — see PLAN-2.1 caveat above. Builder prompt to include explicit guidance.
2. **Tk modal correctness is the hidden risk** — pytest can't catch it. Manual smoke is the only gate. Reviewers should verify image-ref retention (`dialog._species_images = []`) line by line.
3. **PLAN-2.2 dropped** — its checklist content embedded into reviewer prompts at build time.

## Summary

Phase 3 is READY to execute. Two plans, sequential waves. Drop PLAN-2.2; bake its checklist into reviewer dispatches. Image-composition mode handling note for PLAN-2.1's builder. Total work scope: ~150 lines added across 3-4 files, 1 new dialog, 1 function refactor, 1 main.py wire-up.
