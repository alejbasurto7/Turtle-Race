---
phase: 3-main-menu-and-post-race-restructure
plan: 1.1
wave: 1
dependencies: []
must_haves:
  - Add `get_main_menu_choice() -> str` to `dialogs.py` returning `"race" | "leaderboard" | "quit"`.
  - Add `ask_play_again_choice() -> str` to `dialogs.py` returning `"again" | "menu" | "quit"`.
  - Add `show_leaderboard_placeholder() -> None` to `dialogs.py` (real Toplevel, body "Leaderboard view coming in Phase 4", single Close button).
  - All three functions use the established `Toplevel + grab_set + wait_window` modal pattern.
  - Menu X-button returns `"quit"`; post-race X-button returns `"menu"`; placeholder X-button is equivalent to Close.
  - Old `dialogs.ask_play_again()` stays in place untouched in this plan — Plan 2.1 deletes it as part of the `main.py` restructure (its only caller).
  - Test baseline 135 stays green.
files_touched:
  - dialogs.py
tdd: false
risk: medium
---

# Plan 1.1: Add the three new dialog functions to `dialogs.py`

## Context

Phase 3 reshapes `main.py` into a two-level loop (outer menu, inner race rounds) and adds three new dialog functions that the new loop will call. This plan owns the dialog-layer work in isolation: it adds the three new functions to `dialogs.py` without touching `main.py`. Because all three functions live in the same file, they are sequenced as three tasks within a single plan (one atomic commit per task) rather than three parallel plans that would conflict on the same file.

The old `dialogs.ask_play_again()` (bool-returning `messagebox.askyesno`) is intentionally left in place after this plan finishes — its only caller is `main.py`, and Plan 2.1 deletes both the call site and the dead function in the same atomic commit that restructures `main.py`. Leaving it here keeps Plan 1.1 atomically committable without breaking the runtime `main.py` after each task.

Per CONTEXT-3 Decision 1, button labels are plain text — no `PhotoImage` references are required for any of the three new dialogs, so the `dialog._..._images` pattern does not apply here. Tk window-close (`WM_DELETE_WINDOW`) policy varies per dialog per CONTEXT-3 Decisions 3 and 4 (menu X = quit; post-race X = menu; placeholder X = close).

The existing modal pattern in `dialogs.py` (track / species / bet dialogs at lines 31, 137, 194) is the reference shape. Each new function uses the same `selected = [None]; def make_cb(value); dialog.transient(); dialog.grab_set(); dialog.wait_window(); return selected[0]` skeleton.

## Dependencies

- Phase 2 complete (baseline commit `e38eb02`; 135 tests green).
- No dependencies on any other Phase 3 plan — this plan owns Wave 1 alone.

## Tasks

### Task 1: Add `get_main_menu_choice()` to `dialogs.py`

**Files:** `dialogs.py`
**Action:** modify
**TDD:** false
**Description:**

Add a new public function `get_main_menu_choice()` to `dialogs.py`. Place it near the top of the module's public-function block (after the existing imports and module-level constants, before `get_user_track` is fine — exact placement is the builder's call, but it MUST come before `get_user_bet` so a casual reader sees it as the new entry point).

**Signature and contract:**

```python
def get_main_menu_choice() -> str:
    """Return "race", "leaderboard", or "quit" — the user's main-menu choice.

    Toplevel modal over the lawn background. X-button (WM_DELETE_WINDOW) returns "quit"
    per CONTEXT-3 Decision 3. Three vertically stacked buttons in order Race / View
    Leaderboard / Quit. The Race button receives initial keyboard focus.
    """
```

**Modal skeleton (mirror existing pattern):**

```python
dialog = tkinter.Toplevel()
dialog.title("Turtle Race")
dialog.resizable(False, False)

selected = [None]

def make_cb(value):
    def cb():
        selected[0] = value
        dialog.destroy()
    return cb

# Three buttons, vertically stacked.
race_btn       = tkinter.Button(dialog, text="Race",             width=24, command=make_cb("race"))
leaderboard_btn = tkinter.Button(dialog, text="View Leaderboard", width=24, command=make_cb("leaderboard"))
quit_btn       = tkinter.Button(dialog, text="Quit",             width=24, command=make_cb("quit"))
race_btn.pack(padx=20, pady=(20, 6))
leaderboard_btn.pack(padx=20, pady=6)
quit_btn.pack(padx=20, pady=(6, 20))
race_btn.focus_set()                              # Race is the primary action.

dialog.protocol("WM_DELETE_WINDOW", make_cb("quit"))   # X → "quit", per CONTEXT-3 Decision 3.

dialog.transient()
dialog.grab_set()
dialog.wait_window()

return selected[0]
```

**Hard constraints:**

- WM_DELETE_WINDOW handler MUST return `"quit"` (CONTEXT-3 Decision 3) — NOT `lambda: None`.
- Vertical button order MUST be Race → View Leaderboard → Quit (CONTEXT-3 Decision 1).
- Race button MUST receive `focus_set()` so Enter activates it (primary action default focus).
- Function MUST be importable without raising — i.e., no module-level Tk calls; everything happens inside the function body.
- Do NOT add any new module-level imports beyond what `dialogs.py` already imports (`tkinter` and `tkinter.messagebox` are already present).
- Do NOT touch any existing function in `dialogs.py`. Surgical addition only.

**Acceptance Criteria:**

- `python -c "import dialogs; assert callable(dialogs.get_main_menu_choice)"` exits 0.
- `git diff dialogs.py` shows only an addition of the new function (no modifications to existing lines, no deletions).
- `pytest` reports 135 tests still passing (the function isn't unit-tested directly, but adding it must not break import-time behavior).
- A `Grep` for `def get_main_menu_choice` in `dialogs.py` returns exactly one hit.
- A `Grep` for `WM_DELETE_WINDOW.*quit` (or equivalent) inside the function body returns exactly one hit, confirming the X-button binding.

---

### Task 2: Add `ask_play_again_choice()` to `dialogs.py`

**Files:** `dialogs.py`
**Action:** modify
**TDD:** false
**Description:**

Add a new public function `ask_play_again_choice()` to `dialogs.py`. Place it adjacent to the existing `ask_play_again()` function (immediately above or below it — builder's call). The old `ask_play_again()` is NOT removed in this task; Plan 2.1 deletes it together with the only call site.

**Signature and contract:**

```python
def ask_play_again_choice() -> str:
    """Return "again", "menu", or "quit" — the user's post-race choice.

    Toplevel modal. X-button (WM_DELETE_WINDOW) returns "menu" per CONTEXT-3 Decision 4
    (the least-destructive close for the post-race context). Three horizontally arranged
    buttons in order Play Again / Main Menu / Quit. Play Again receives initial keyboard focus.
    """
```

**Modal skeleton:**

```python
dialog = tkinter.Toplevel()
dialog.title("Turtle Race")
dialog.resizable(False, False)

selected = [None]

def make_cb(value):
    def cb():
        selected[0] = value
        dialog.destroy()
    return cb

label = tkinter.Label(dialog, text="What would you like to do?", padx=20, pady=10)
label.pack()

button_row = tkinter.Frame(dialog)
button_row.pack(padx=20, pady=(0, 20))

again_btn = tkinter.Button(button_row, text="Play Again", width=12, command=make_cb("again"))
menu_btn  = tkinter.Button(button_row, text="Main Menu",  width=12, command=make_cb("menu"))
quit_btn  = tkinter.Button(button_row, text="Quit",       width=12, command=make_cb("quit"))
again_btn.pack(side="left", padx=4)
menu_btn.pack(side="left", padx=4)
quit_btn.pack(side="left", padx=4)
again_btn.focus_set()                                # Play Again is the primary action.

dialog.protocol("WM_DELETE_WINDOW", make_cb("menu"))    # X → "menu", per CONTEXT-3 Decision 4.

dialog.transient()
dialog.grab_set()
dialog.wait_window()

return selected[0]
```

**Hard constraints:**

- WM_DELETE_WINDOW handler MUST return `"menu"` (CONTEXT-3 Decision 4) — NOT `"quit"`, NOT `lambda: None`.
- Button order left-to-right MUST be Play Again → Main Menu → Quit (CONTEXT-3 Decision 4).
- Play Again button MUST receive `focus_set()`.
- Do NOT delete or modify `dialogs.ask_play_again()` (the old bool-returning function). That deletion happens in Plan 2.1 atomically with the call-site replacement.
- Do NOT touch any other existing function in `dialogs.py`.

**Acceptance Criteria:**

- `python -c "import dialogs; assert callable(dialogs.ask_play_again_choice)"` exits 0.
- `python -c "import dialogs; assert callable(dialogs.ask_play_again)"` ALSO exits 0 (old function still present at end of this task).
- `git diff dialogs.py` shows only the new function added; no existing lines modified or deleted.
- `pytest` reports 135 tests still passing.
- `Grep` for `def ask_play_again_choice` in `dialogs.py` returns exactly one hit.
- `Grep` for `WM_DELETE_WINDOW.*menu` (or equivalent) inside the new function body returns exactly one hit.

---

### Task 3: Add `show_leaderboard_placeholder()` to `dialogs.py`

**Files:** `dialogs.py`
**Action:** modify
**TDD:** false
**Description:**

Add a new public function `show_leaderboard_placeholder()` to `dialogs.py`. Place it adjacent to the other new functions added in Tasks 1 and 2.

**Signature and contract:**

```python
def show_leaderboard_placeholder() -> None:
    """Show a placeholder Toplevel modal informing the user that the leaderboard view
    is coming in Phase 4. Single Close button; X-button is equivalent to Close.

    Phase 4 will replace this function's body in-place with the real Treeview-based
    leaderboard view. The name and signature MUST stay stable so Plan 2.1 can wire
    main.py against it now.
    """
```

**Modal skeleton:**

```python
dialog = tkinter.Toplevel()
dialog.title("Leaderboard")
dialog.resizable(False, False)

label = tkinter.Label(
    dialog,
    text="Leaderboard view coming in Phase 4",
    padx=30, pady=20,
)
label.pack()

def close():
    dialog.destroy()

close_btn = tkinter.Button(dialog, text="Close", width=12, command=close)
close_btn.pack(padx=20, pady=(0, 20))
close_btn.focus_set()

dialog.protocol("WM_DELETE_WINDOW", close)        # X is equivalent to Close (CONTEXT-3 Decision 2).

dialog.transient()
dialog.grab_set()
dialog.wait_window()
```

**Hard constraints:**

- Function returns `None` implicitly (no `return` statement needed).
- WM_DELETE_WINDOW MUST be wired to the same `close` handler as the Close button — both routes dismiss the dialog identically.
- Body text MUST be exactly "Leaderboard view coming in Phase 4" (CONTEXT-3 Decision 2).
- The function MUST NOT import or call anything from `leaderboard.py`. It is a pure placeholder; Phase 4 will introduce the real query/render logic.
- Function name and signature (`show_leaderboard_placeholder() -> None`) MUST remain stable — Plan 2.1 wires `main.py` against this exact name. (Phase 4 may rename it to `show_leaderboard()` when replacing the body; that rename is Phase 4's concern, not Phase 3's.)

**Acceptance Criteria:**

- `python -c "import dialogs; assert callable(dialogs.show_leaderboard_placeholder)"` exits 0.
- `git diff dialogs.py` shows only the new function added.
- `pytest` reports 135 tests still passing.
- `Grep` for `def show_leaderboard_placeholder` in `dialogs.py` returns exactly one hit.
- `Grep` for `Coming in Phase 4` in `dialogs.py` returns exactly one hit (case-sensitive match on the literal body string — adjust if reviewer accepts the slight rephrasing "Leaderboard view coming in Phase 4").

## Verification

Run from project root after all three tasks committed:

```powershell
# Static sanity
git log --oneline -4
python -c "import dialogs; assert callable(dialogs.get_main_menu_choice); assert callable(dialogs.ask_play_again_choice); assert callable(dialogs.show_leaderboard_placeholder); print('all three new dialog functions present')"

# Old function still exists at end of Plan 1.1 (gets deleted in Plan 2.1).
python -c "import dialogs; assert callable(dialogs.ask_play_again); print('old ask_play_again still present (will be deleted in Plan 2.1)')"

# Test suite
pytest
```

Expected:

- `git log --oneline -4` shows three new commits on top of the Phase 2 baseline (`e38eb02`).
- The first `python -c` invocation prints `all three new dialog functions present` and exits 0.
- The second `python -c` invocation prints the "still present" line and exits 0.
- `pytest` reports `135 passed`.

Cross-references:
- CONTEXT-3.md Decisions 1, 2, 3, 4 (button labels and X-button policies).
- RESEARCH.md §3 (existing modal pattern reference, including the `selected[0]` sentinel idiom).
- PROJECT.md "Functional — UI" (main menu and post-race prompt requirements).
