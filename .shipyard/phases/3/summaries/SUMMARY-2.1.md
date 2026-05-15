# SUMMARY-2.1.md — Phase 3 Wave 2

## Status

COMPLETE. All implementation tasks executed, verified, and committed.
pytest 77/77 green. Manual smoke gate: PENDING_HUMAN_VERIFICATION.

---

## Tasks Completed

### Task 1 — Add `get_user_species()` to `dialogs.py`
**Commit:** c4f1271
**Message:** shipyard(phase-3): add get_user_species() with composite turtle/snake button images

- Added `get_user_species()` modal dialog between `get_user_track()` and `ask_play_again()`.
- Dialog: Toplevel, title "Choose Your Racers", resizable(False,False), WM_DELETE_WINDOW no-op.
- Header label: "Which species will race?", font ("Arial",12,"bold"), columnspan=2, row=0.
- Two buttons at row=1: col 0 = Turtles, col 1 = Snakes. compound="top".
- Turtles composite: Image.new("RGBA",(200,200),(255,255,255,0)). Cell=100px.
  Each of 4 turtle JPGs converted to RGBA, resized to 100x100, pasted with alpha mask
  at (col*100,(row-1)*100) using _TURTLE_GRID_LAYOUT order (Leonardo TL, Donatello TR,
  Raphael BL, Michaelangelo BR).
- Snakes composite: Image.new("RGBA",(198,200),(255,255,255,0)). cell_w=66,cell_h=200.
  Each of 3 snake PNGs converted to RGBA, resized, pasted at (col*66,0) using
  _SNAKE_ROW_LAYOUT. Final composite resized to 200x200 via LANCZOS.
- CRITICAL RGBA handling: both composites RGBA, all sources .convert("RGBA") before paste,
  third paste() arg is image itself (alpha mask). Prevents JPG/RGBA mode mismatch.
- Image-ref retention: dialog._species_images=[] before loop; both PhotoImages appended.
- Centering: update_idletasks/winfo_screenwidth/geometry copied from get_user_track.
- Returns "turtles" or "snakes" matching SPECIES dict keys.
- Verify: callable(dialogs.get_user_species) and len(sig.parameters)==0 passed. pytest 77/77.

### Task 2 — Wire `main.py` + update `create_racers` docstring in `race.py`
**Commit:** 75a62a2
**Message:** shipyard(phase-3): wire species end-to-end in main.py and update create_racers docstring

main.py changes:
- Inserted species = dialogs.get_user_species() between get_user_track() and create_racers(species).
- Replaced hardcoded "turtles" literal with species variable in create_racers call.
- Hoisted n = len(racers) once; all three race.draw_* calls use n (S2.2).
- Fixed dialogs.get_user_bet() (no-arg, runtime-broken) to dialogs.get_user_bet(species).

race.py changes:
- Updated create_racers docstring: Args/Returns format documenting species as SPECIES key
  (KeyError on bad input) and that returned dicts include 'name', 'color', 'o' keys.

Verify: 'species' in race.create_racers.__doc__ and 'name' in __doc__: True.
        'species' Name node in ast.walk(main.py): True. pytest 77/77.

### Task 3 — Manual smoke gate + SUMMARY file
- Manual smoke: PENDING_HUMAN_VERIFICATION (checklist below).
- SUMMARY written to .shipyard/phases/3/results/SUMMARY-2.1.md and
  .shipyard/phases/3/summaries/SUMMARY-2.1.md.

---

## Files Modified

| File    | Change |
|---------|--------|
| dialogs.py | Added get_user_species() function (93 new lines) |
| main.py | Inserted species call, n hoist, fixed get_user_bet(species) |
| race.py | Updated create_racers docstring (Args/Returns format) |

---

## pytest Results

| Stage | Command | Result |
|-------|---------|--------|
| Baseline (Wave 1 end) | pytest -q | 77 passed |
| Task 1 verify | python -c + pytest -q | ok / 77 passed |
| Task 2 verify | python -c + pytest -q | ok / 77 passed |
| Final | pytest -q | 77 passed |

---

## Manual Smoke Gate — PENDING_HUMAN_VERIFICATION

Checklist for a human with a display. Run: python main.py

| Round | Track | Species | Expected | Pass/Fail |
|-------|-------|---------|----------|-----------|
| 1 | Straight | Turtles | Species dialog shows 2x2 turtle + 1x3 snake composites (images not blank). Turtles bet dialog 2x2 grid, 4 racers, 4-finisher podium. "Play again?" | PENDING |
| 2 | Rectangular | Snakes | Snake bet dialog 1x3 row (Shadow,Ralph,Anaconda; not blank). 3 racers (turtle-shaped placeholders). 3-finisher podium. | PENDING |
| 3 | Spiral | Turtles | Turtles mode visually identical to pre-Phase-3 master (zero regression). | PENDING |
| 4 | Any | Any | Pick "No" at play again. Clean exit, no Tk errors, no traceback. | PENDING |

What to look for:
1. Both species button images visible (not blank gray squares).
2. Images still visible on SECOND open of species/bet dialogs (GC retention check).
3. Turtles = 4 racers, Snakes = 3 racers. Podium shows correct count.
4. Cross-species switching (Turtles->Snakes->Turtles): no stale state, no image blanking.

Non-blocking visual nits:
- Snake composite squashed to 200x200 (3:1 wide source). Expected, by design.
- Snake PNG transparent areas may show dialog background gray. Acceptable.

---

## Phase 3 Close-Out Statement

Snakes mode reaches podium with turtle-shaped placeholders; Phase 4 wires real snake shapes.

After PENDING_HUMAN_VERIFICATION passes, Phase 3 is complete:
- All 3 tracks x 2 species = 6 race permutations reachable from UI.
- Turtles mode visually identical to pre-Phase-3 master.
- Snakes mode: correct racer count (3), correct bet dialog (1x3 row), podium.

---

## Deferred Actionables for Phase 4

| Item | Detail |
|------|--------|
| Real snake shapes | create_racers currently uses shape="turtle" for all species. Phase 4 reads SPECIES[species]["shape_drawer"] and uses custom snake polygon or registered shape. |
| L_BASE tuning | constants.py L_BASE=1.0 is placeholder for snake body-length scaling. Wire in Phase 4. |
| TURTLE_NAMES import cleanup | TURTLE_NAMES imported in dialogs.py but no longer referenced directly (all lookups via SPECIES). Remove in Phase 4 when touching dialogs.py. |
| Snake composite background | If PNG transparent areas on dialog gray look bad: pre-fill canvas with (240,240,240,255) instead of transparent. |

---

## Commit SHAs

| Task | SHA | Message |
|------|-----|---------|
| Task 1 | c4f1271 | shipyard(phase-3): add get_user_species() with composite turtle/snake button images |
| Task 2 | 75a62a2 | shipyard(phase-3): wire species end-to-end in main.py and update create_racers docstring |
