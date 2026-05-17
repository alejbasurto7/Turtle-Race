---
phase: polish-and-ship
plan: 1.1
wave: 1
dependencies: []
must_haves:
  - Append a 10-20 line addendum to CLAUDE.md under the existing "## Architecture" heading, placed AFTER the "### Round loop shape" section
  - Addendum titled "### Leaderboard (Phase 1 module, Phase 4 view)" covering the four bullets from CONTEXT-5 Decision 2 (Tk-free invariant, %APPDATA% data path, schema_version field, dialogs.show_leaderboard reaches data via public leaderboard API)
  - Correct the stale "three modal dialogs" bullet under "## Architecture" — Phase 3/4 raised the count to six (get_user_track, get_user_species, get_user_bet, ask_play_again_choice, get_main_menu_choice, show_leaderboard). Fix this in the SAME task as the addendum
  - Add a 2-line confirmation comment to the top of turtle_race.spec per CONTEXT-5 Decision 3 — leaderboard.json is generated at runtime by leaderboard.py and does NOT belong in datas=
  - Do NOT change any datas= entry, Analysis(), PYZ(), EXE(), or any other PyInstaller-functional content in turtle_race.spec
  - Do NOT create README.md (CONTEXT-5 Decision 1 explicitly skips this)
  - pytest stays green (135 passed)
files_touched:
  - CLAUDE.md
  - turtle_race.spec
tdd: false
risk: low
---

# PLAN 1.1 — CLAUDE.md addendum + turtle_race.spec comment (docs-only)

## Context

Phase 5 is "Polish and Ship". This plan delivers the documentation portion of the phase per the binding decisions in [.shipyard/phases/5/CONTEXT-5.md](../CONTEXT-5.md):

- **Decision 1:** No `README.md` is created — none exists in the project root and the ROADMAP explicitly allows skipping it ("If no README, this bullet is skipped without ceremony").
- **Decision 2:** A short (10–20 line) addendum is added to `CLAUDE.md` covering the leaderboard module's Tk-free invariant, the `%APPDATA%\TurtleRace\leaderboard.json` data path, the `schema_version: 1` field, and the fact that `dialogs.show_leaderboard()` reaches data via the public `leaderboard` API (no direct file I/O from the dialog). The addendum also corrects the stale "tkinter owns three modal dialogs" bullet (now six dialogs after Phases 3 and 4).
- **Decision 3:** A 2-line comment is added to the top of `turtle_race.spec` confirming that `leaderboard.json` is generated at runtime by `leaderboard.py` and does NOT belong in the `datas=` list. No functional spec changes.

Phase 1 / 2 / 3 / 4 are complete. This plan touches `CLAUDE.md` and `turtle_race.spec` only — no Python code, no tests. `pytest` is expected to stay trivially green (currently 135 passed).

The acceptance contract from `.shipyard/ROADMAP.md` §"Phase 5 — Polish and Ship" is satisfied by:
- ROADMAP bullet 1 ("CLAUDE.md gains a short addendum (10–20 lines) covering ...") — Task 1.
- ROADMAP bullet 2 ("turtle_race.spec is reviewed — ... confirm explicitly in the spec comment or commit message") — Task 2.
- ROADMAP bullet 3 (README) — explicitly skipped per CONTEXT-5 Decision 1.

## Dependencies

None. This is Wave 1.

## Tasks

<task id="1" files="CLAUDE.md" tdd="false">
  <action>
Make two edits to `CLAUDE.md` in the same commit:

**A. Correct the stale "three modal dialogs" bullet (line 40 of CLAUDE.md).**

Current text (verbatim):

```
- **`tkinter`** owns the three modal dialogs in [dialogs.py](dialogs.py) — track selection, species selection, bet — and the "play again?" `messagebox`. Each dialog uses `Toplevel` + `grab_set()` + `wait_window()` to block until the user chooses, with `WM_DELETE_WINDOW` no-op to force a choice.
```

Replace with:

```
- **`tkinter`** owns the six modal dialogs in [dialogs.py](dialogs.py) — `get_user_track`, `get_user_species`, `get_user_bet`, `ask_play_again_choice`, `get_main_menu_choice`, and `show_leaderboard`. Each dialog uses `Toplevel` + `grab_set()` + `wait_window()` to block until the user chooses, with `WM_DELETE_WINDOW` redirected (no-op or routed to a Close handler) so the user must pick a button.
```

Rationale: Phase 3 added the menu + post-race dialogs; Phase 4 added the leaderboard window. The "three dialogs" + "play again messagebox" wording is stale (it pre-dates `ask_play_again_choice` replacing the old `tkinter.messagebox` confirmation).

**B. Append a new subsection to the `## Architecture` section, immediately after the existing `### Round loop shape` block (which ends at line 88 — the paragraph closing "...removed during the Phase 2 generalization.").**

The new subsection title is `### Leaderboard (Phase 1 module, Phase 4 view)`. Length: 10–20 lines of body text (target ~15). It MUST cover all four bullets from CONTEXT-5 Decision 2:

1. The `leaderboard.py` module is **Tk-free**; `import leaderboard` succeeds without a display. This is a load-bearing invariant for the no-GUI smoke scripts (`tools/smoke_phase_3.py`, `tools/smoke_phase_4.py`, and `tools/smoke_phase_5.py`).
2. The on-disk store lives at `%APPDATA%\TurtleRace\leaderboard.json` on Windows and `~/.local/share/TurtleRace/leaderboard.json` (or `~/Library/Application Support/TurtleRace/leaderboard.json` on macOS) elsewhere, resolved via `paths.user_data_path()` — parallel to the existing `paths.resource_path()` but for **writable per-user data**, NOT bundled resources. The JSON file is generated at runtime — it is NOT a [turtle_race.spec](turtle_race.spec) `datas=` entry.
3. The JSON schema includes a `schema_version: 1` field (`leaderboard.SCHEMA_VERSION`). Future migrations will dispatch on this field; there is no migrator today.
4. `dialogs.show_leaderboard()` reaches the data **only via the public `leaderboard` API** (`query`, `query_per_track`, `known_tracks`, `reset_session`, `reset_all`) — no direct file I/O from the dialog. This keeps the Tk-free invariant intact (the GUI module imports `leaderboard`, not the other way around).

Suggested text (the architect's recommended wording — the builder is free to lightly edit for tone but must preserve all four facts above):

```markdown
### Leaderboard (Phase 1 module, Phase 4 view)

[leaderboard.py](leaderboard.py) is the persistence and scoring core. It is **Tk-free** — `import leaderboard` succeeds in a headless Python with no `DISPLAY` and no Tk root. The three no-GUI smoke scripts (`tools/smoke_phase_3.py`, `tools/smoke_phase_4.py`, `tools/smoke_phase_5.py`) depend on this invariant: they import `leaderboard` directly and never instantiate a `Tk()` root. Do not add `import tkinter` (or any Tk-touching helper) to `leaderboard.py`.

The on-disk store lives at `%APPDATA%\TurtleRace\leaderboard.json` on Windows (`~/.local/share/TurtleRace/leaderboard.json` on Linux, `~/Library/Application Support/TurtleRace/leaderboard.json` on macOS), resolved via `paths.user_data_path("leaderboard.json")`. `user_data_path()` is the writable-per-user-data sibling of `resource_path()` — it **never** returns a path inside `sys._MEIPASS`. The JSON file is **generated at runtime** by `leaderboard._save()`; it is NOT a [turtle_race.spec](turtle_race.spec) `datas=` entry.

The schema is `{"schema_version": 1, "races": [...]}` (constant `leaderboard.SCHEMA_VERSION`). Future migrations dispatch on `schema_version`; only v1 ships today. Writes are atomic (tempfile + `os.replace`) and unparseable input is quarantined to `<path>.corrupt-<ts>` and replaced with a fresh empty store.

[dialogs.py](dialogs.py)'s `show_leaderboard()` reads data **only** through the public `leaderboard` API — `query`, `query_per_track`, `known_tracks`, `reset_session`, `reset_all` — never via direct file I/O. This direction (`dialogs` imports `leaderboard`, never the reverse) keeps the Tk-free invariant intact.
```

Do NOT modify any other section of CLAUDE.md. Do NOT change the Commands section. Do NOT touch `### Resource loading`, `### Racer identity is positional, and species-dispatched`, `### Shape dispatch and finish detection`, `### N-parameterized track geometry`, `### Tk image references`, or `### Round loop shape`.
  </action>
  <verify>python -c "import dialogs; import main; import leaderboard" ; pytest -q</verify>
  <done>`python -c "import dialogs; import main; import leaderboard"` exits 0 (these are doc-only edits — imports must be unchanged). `pytest -q` reports `135 passed`. `grep -nE "^### Leaderboard \(Phase 1 module, Phase 4 view\)" CLAUDE.md` returns exactly 1 hit. `grep -cE "owns the six modal dialogs" CLAUDE.md` returns 1. `grep -cE "owns the three modal dialogs" CLAUDE.md` returns 0 (stale line gone). `grep -cE "schema_version" CLAUDE.md` returns >= 1. `grep -cE "user_data_path" CLAUDE.md` returns >= 1. `grep -cE "Tk-free" CLAUDE.md` returns >= 1. The new subsection sits AFTER `### Round loop shape` and BEFORE EOF (no new top-level `##` headings are introduced).</done>
</task>

<task id="2" files="turtle_race.spec" tdd="false">
  <action>
Prepend a 2-line comment block to the very top of `turtle_race.spec` (above the existing `block_cipher = None` line). The comment confirms the CONTEXT-5 Decision 3 audit conclusion: `leaderboard.json` is a runtime-generated user-data file, NOT a bundled resource, and therefore does not need a `datas=` entry.

The exact text to prepend (two `#` comment lines plus one blank line for readability):

```
# Note: %APPDATA%/TurtleRace/leaderboard.json is generated at runtime by
# leaderboard.py — it is NOT a bundled resource and does NOT belong in datas=.

block_cipher = None
```

Do NOT modify the `Analysis(...)` call, the `datas=` tuple, the `hiddenimports=` list, the `PYZ(...)` call, the `EXE(...)` call, or any other functional argument. The only edit is the two-line `#` comment prepended to the file (followed by one blank line and then the unchanged `block_cipher = None`).

After saving, the file must still be a valid PyInstaller spec — Python comments at the top of a `.spec` file are inert.
  </action>
  <verify>python -c "import ast; ast.parse(open('turtle_race.spec', encoding='utf-8').read())" ; pytest -q</verify>
  <done>`python -c "import ast; ast.parse(open('turtle_race.spec', encoding='utf-8').read())"` exits 0 (the spec parses as valid Python). `pytest -q` reports `135 passed`. `grep -nE "leaderboard\.json is generated at runtime" turtle_race.spec` returns 1 hit at line 1 or 2 (the top of the file). `grep -cE "NOT belong in datas=" turtle_race.spec` returns 1. `grep -cE "^block_cipher = None" turtle_race.spec` still returns 1. `grep -cE "^datas=\[" turtle_race.spec` is unchanged from before the edit (the architect notes the existing spec has `datas=` inline within the `Analysis(...)` call on line 7 — that line MUST remain byte-identical). `grep -cE "'lawn\.jpg', '\.'" turtle_race.spec` still returns 1 (existing data tuple untouched). `grep -cE "leaderboard\.json" turtle_race.spec` returns exactly 1 (only the new comment, NOT a datas entry).</done>
</task>

## Acceptance Criteria

- `CLAUDE.md` contains a new `### Leaderboard (Phase 1 module, Phase 4 view)` subsection under `## Architecture`, placed after `### Round loop shape`.
- The new subsection mentions all four facts from CONTEXT-5 Decision 2: Tk-free invariant, `%APPDATA%\TurtleRace\leaderboard.json` data path via `paths.user_data_path()`, `schema_version: 1` field, and `dialogs.show_leaderboard()` reaching data only via the public `leaderboard` API.
- The stale "tkinter owns the three modal dialogs" bullet in `CLAUDE.md` is replaced with the corrected six-dialog version listing all current dialogs by name.
- `turtle_race.spec` has a 2-line comment at the very top confirming `leaderboard.json` is runtime-generated and not a `datas=` entry. No functional spec content (Analysis / PYZ / EXE / datas / hiddenimports) is changed.
- No `README.md` is created (CONTEXT-5 Decision 1).
- `pytest -q` reports 135 passed at the tip of every commit in this plan.
- `python -c "import dialogs; import main; import leaderboard"` exits 0 at the tip of every commit.

## Verification

After both tasks:

```powershell
python -c "import dialogs; import main; import leaderboard"   # exits 0
pytest -q                                                      # 135 passed
python -c "import ast; ast.parse(open('turtle_race.spec', encoding='utf-8').read())"   # exits 0

# CLAUDE.md addendum landed in the right place
grep -nE "^### Leaderboard \(Phase 1 module, Phase 4 view\)" CLAUDE.md   # exactly 1 hit
grep -cE "owns the six modal dialogs" CLAUDE.md                          # 1
grep -cE "owns the three modal dialogs" CLAUDE.md                        # 0  (stale line gone)
grep -cE "schema_version" CLAUDE.md                                      # >= 1
grep -cE "user_data_path" CLAUDE.md                                      # >= 1
grep -cE "Tk-free" CLAUDE.md                                             # >= 1

# turtle_race.spec comment landed at the top, no functional change
grep -nE "leaderboard\.json is generated at runtime" turtle_race.spec    # 1 hit at line 1 or 2
grep -cE "NOT belong in datas=" turtle_race.spec                         # 1
grep -cE "^block_cipher = None" turtle_race.spec                         # 1
grep -cE "'lawn\.jpg', '\.'" turtle_race.spec                            # 1  (existing datas tuple untouched)

# README explicitly NOT created
test ! -f README.md
```

These edits are documentation-only. No new tests are added; the existing 135-test suite remains the single regression signal.
