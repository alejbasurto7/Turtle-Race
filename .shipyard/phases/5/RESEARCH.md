# Phase 5 Research — Regression sweep, frozen build, ship polish

The Turtle Race "Snakes Racer Mode" milestone is functionally complete after Phase 4. Phase 5 is wrap-up: one new test, one docstring extension, a `.gitignore` update, a `SHIP-NOTES.md`, PROJECT.md cleanup, a CLAUDE.md fix, and a PyInstaller build pass.

## 1. `.gitignore` state

**File:** `.gitignore` (7 lines):
```
build/
dist/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.vscode/launch.json
```

- `build/` and `dist/` already cover PyInstaller output.
- `assets/midi/` NOT yet ignored → 8 untracked MIDI files in that dir.
- `assets/TeenageMutantNinjaTurtles.mid` is at `assets/` root (NOT inside `midi/`) and is tracked — `main.py:15` loads it.
- No other untracked items in `assets/`.

**Insertion point:** append `assets/midi/` after line 7. Trailing slash is correct directory pattern.

## 2. `create_racers` docstring extension

**File:** `race.py:215`+, docstring lines 234-250.

Existing docstring ends at `'o'` bullet (line 249). Insert a `Note:` block between lines 249-250:

```python
        Note:
            For ``"snakes"``, the drawer receives ``SNAKE_LENGTHS[i]`` as a
            ``length_units`` argument so each snake's stretch_len scales with
            its species-defined length (Shadow=6, Ralph=2, Anaconda=5).
            For ``"turtles"``, the drawer takes no extra argument.
```

Documents the `if species == "snakes": drawer(t, SNAKE_LENGTHS[i])` branch at lines 256-259.

## 3. `tests/test_race.py` — Anaconda test

Existing tests:
- `test_head_offset_arc_shadow` (lines 86-95)
- `test_head_offset_arc_ralph` (lines 98-107)
- Comment block (lines 109-112): turtle note, no assertion

**Insertion point:** after Ralph test (after line 107), before comment block (line 109).

**Concrete values:** Anaconda length=5, L_BASE=1.2 → stretch_len=6.0; SNAKE_UNIT_SIZE=20 → head_offset_arc = 20*6.0/2 = 60.0.

```python
def test_head_offset_arc_anaconda():
    """Anaconda: L_BASE=1.2, length_units=5 → stretch_len=6.0.
    Snake polygon SNAKE_UNIT_SIZE=20.
    head_offset_arc = 20 * 6.0 / 2 = 60.0 px along heading.
    """
    stretch_len = 1.2 * 5   # 6.0
    head_offset_arc = SNAKE_UNIT_SIZE * stretch_len / 2
    assert abs(head_offset_arc - 60.0) < 1e-9, (
        f"Anaconda head_offset_arc: expected 60.0, got {head_offset_arc}"
    )
```

No new imports — `SNAKE_UNIT_SIZE` is module-level at line 21.

## 4. `turtle_race.spec` — what to expect

**`datas=` (line 7):**
```python
datas=[('lawn.jpg', '.'), ('assets/*.jpg', 'assets'), ('assets/*.mid', 'assets'),
       ('assets/*.png', 'assets'), ('assets/snakes/*.png', 'assets/snakes')]
```

All asset paths verified present on disk. No missing-asset warnings expected.

PyInstaller destinations: `<_MEIPASS>/assets/snakes/{Shadow,Ralph,Anaconda}.png` matches `SNAKE_IMAGES` paths.

**`dist/TurtleRace.exe`** is the output (one-file mode per spec EXE block). `upx=True` set — UPX must be on PATH or it'll skip with a warning (benign).

`hiddenimports=['turtle']` set — necessary for Python's stdlib turtle in frozen builds.

`build/` and `dist/` already in `.gitignore`. ✓

**Failure-handling strategy:** if PyInstaller fails, document in SUMMARY-W.P.md but don't block Phase 5 close — spec/datas correctness can be validated by inspection.

## 5. SHIP-NOTES.md structure

```markdown
# Turtle Race — Snakes Racer Mode: Ship Notes

## What Shipped
- Species selector dialog (Turtles | Snakes) per round
- Three snake racers: Shadow (black, length 6), Ralph (#E89F4F, length 2), Anaconda (green, length 5)
- Custom smooth-wave snake polygon; 6:5:2 length ratio at L_BASE=1.2
- Head-position finish detection (universal)
- Snake bet dialog (1×3 row); composite turtles/snakes species dialog images
- N-parameterized lane geometry on all 3 tracks
- Podium supports 3 or 4 finishers; snake lengths preserved
- Snake PNGs bundled in PyInstaller spec

## Architecture Pointers
Cross-reference CLAUDE.md. Key entry points:
- constants.py: SPECIES, SNAKE_NAMES/COLORS/LENGTHS/IMAGES, L_BASE
- race.py: draw_snake_shape, create_racers, place_racers_on_track, run_race
- dialogs.py: get_user_species, get_user_bet
- paths.py: resource_path() — all asset loads go through here

## Run / Test / Build
See CLAUDE.md. Quick reference:
- Dev: python main.py
- Tests: pytest (expect 85/85)
- Build: pyinstaller turtle_race.spec → dist/TurtleRace.exe

## Known Deferrals
- Spiral 3-lane visual tuning: ships as-is; open follow-up if needed
- MIDI shuffle: assets/midi/ has 9 alternate files; intentionally untracked

## Snake Assets
Snake PNGs (assets/snakes/) are user-provided (1024×1024 RGBA). The active
MIDI (assets/TeenageMutantNinjaTurtles.mid) is at assets/ root and is tracked.
The assets/midi/ directory of alternates is gitignored.

## Future Work Suggestions
- 4th species (lizards / frogs) via SPECIES config pattern
- Music shuffle from assets/midi/
- Per-round statistics
- Difficulty slider (MAX_PACE tuning)
- macOS/Linux packaging
- Spiral 3-lane geometry tuning if visual issues arise
```

## 6. PROJECT.md Open Items cleanup

**File:** `.shipyard/PROJECT.md` lines 129-134.

Strikethrough + status annotations inline (preserve history):

- ~~Ralph hex~~ — **RESOLVED:** `#E89F4F`
- ~~L_BASE concrete value~~ — **RESOLVED:** `1.2`
- ~~Classic vs polygon~~ — **RESOLVED:** custom Option 5 smooth-wave polygon registered as `"snake"`
- Spiral 3-lane visual-tuning — **DEFERRED** per CONTEXT-5 Decision 1

## 7. CLAUDE.md drift check

One small factual error at CLAUDE.md line 62: says `_SHAPE_UNIT_SIZE = 9` "calibrated for classic shape and reused for snake polygon (which is also 9 units long)" — but `race.py:201-204` shows `_SHAPE_UNIT_SIZE["snake"] = _SNAKE_POLYGON_LENGTH = 20`.

**Correction:**
> `_SHAPE_UNIT_SIZE` maps shape names to their natural length along the heading axis: `9` for `"classic"` and `"turtle"` shapes, `20` for the custom `"snake"` polygon (`_SNAKE_POLYGON_LENGTH = 20`).

No other CLAUDE.md drift. `_back_pos` + `_head_offset_arc_for` helpers are recent (Phase 4 HEAD-at-start work) but they're internal helpers; CLAUDE.md doesn't need to enumerate them.

## 8. Banned-identifier final sweep

`grep -rn "N_LANES|turtles_list|create_turtles|place_turtles_on_track|tortuga"` over `*.py` returns only:
```
tests/test_tracks.py:38:# Local constant replaces the deleted N_LANES from constants.py.
```

Clean — only the intentional prose comment from Phase 2. No regressions.

## 9. Files-affected list

| File | Action | Notes |
|---|---|---|
| `.gitignore` | Modify | Append `assets/midi/` |
| `tests/test_race.py` | Modify | Insert Anaconda test after Ralph |
| `race.py` | Modify | Extend `create_racers` docstring (Note block) |
| `.shipyard/PROJECT.md` | Modify | Strikethrough + RESOLVED/DEFERRED annotations on Open Items |
| `CLAUDE.md` | Modify | Fix line 62 _SHAPE_UNIT_SIZE description |
| `SHIP-NOTES.md` (project root) | Create | Per structure in §5 |
| `pyinstaller turtle_race.spec` | Run | Confirm exit 0 + `dist/TurtleRace.exe` exists |

No deletions, no new modules.

## 10. Gotchas

- **PyInstaller failure handling:** UPX-missing is benign. Tcl/Tk DLL issues would surface at exe launch (not build), which we're not testing per CONTEXT-5. If build fails, document and don't block Phase 5 close.
- **`assets/midi/` pattern:** trailing slash matches the directory + all contents. Affects only items under `assets/midi/`; `assets/TeenageMutantNinjaTurtles.mid` at `assets/` root is unaffected.
- **PROJECT.md Open Items:** use strikethrough (`~~text~~`), not deletion. Renders in GitHub + PyCharm markdown.
- **CLAUDE.md correction:** factual fix; the code (`race.py`) is right, only the doc is wrong.
- **Pytest baseline count:** builder should verify the pre-Phase-5 count by running `pytest --collect-only -q | tail -1` before committing. CONTEXT-5 assumes 84; if it differs, the 85/85 target adjusts accordingly.

## Uncertainty flags

- **UPX availability:** unknown in builder's environment. Either way it's benign.
- **`assets/TeenageMutantNinjaTurtles.mid` tracked status:** assumed tracked from clean git status, but builder should confirm via `git ls-files assets/TeenageMutantNinjaTurtles.mid`.
