# TMNT Image Bet Buttons Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the four colored name buttons in the bet dialog with a 2x2 grid of TMNT character images and name captions.

**Architecture:** Add a name-keyed image-path map and a size constant to `constants.py`. Rewrite `get_user_input()` in `main.py` to lay out four image+caption buttons via `tkinter.grid()`, loading JPGs through `PIL.Image` + `ImageTk.PhotoImage`. Update `reptile_race.spec` so PyInstaller bundles the `assets/` directory.

**Tech Stack:** Python 3, tkinter, Pillow (PIL), PyInstaller.

**Spec:** `docs/superpowers/specs/2026-05-05-tmnt-image-bet-buttons-design.md`

---

## File Structure

- **Modify:** `constants.py` — add `TURTLE_IMAGES` (name → path) and `BET_IMAGE_SIZE`.
- **Modify:** `main.py` — rewrite `get_user_input()` to a 2x2 image-button grid.
- **Modify:** `reptile_race.spec` — bundle `assets/*.jpg`.
- **Create:** `tests/test_constants.py` — unit-test the image map for completeness, ordering match, and file existence.

The project has no existing test suite. We add a single small test file for the parts that are headlessly testable (the constants mapping). The Tk dialog itself is verified by manual launch.

---

### Task 1: Add image map and size constant

**Files:**
- Modify: `constants.py`

- [ ] **Step 1: Add `TURTLE_IMAGES` and `BET_IMAGE_SIZE` to `constants.py`**

Append to the bottom of `constants.py`:

```python
TURTLE_IMAGES = {
    "Raphael":      "assets/turtle_3_raphael_bottom_left.jpg",
    "Michaelangelo": "assets/turtle_4_michelangelo_bottom_right.jpg",
    "Leonardo":     "assets/turtle_1_leonardo_top_left.jpg",
    "Donatello":    "assets/turtle_2_donatello_top_right.jpg",
}
BET_IMAGE_SIZE = 140  # px, square — used by the bet dialog
```

Note: the dict key `"Michaelangelo"` matches the existing (mis)spelling already used in `TURTLE_NAMES`. Do not "fix" it — race logic depends on this exact string everywhere.

- [ ] **Step 2: Commit**

```
git add constants.py
git commit -m "Add TURTLE_IMAGES map and BET_IMAGE_SIZE constant"
```

---

### Task 2: Test the image map

**Files:**
- Create: `tests/test_constants.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_constants.py`:

```python
import os
import sys

# Make project root importable when running pytest from any cwd.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE


def test_image_map_has_entry_for_every_turtle_name():
    assert set(TURTLE_IMAGES.keys()) == set(TURTLE_NAMES), (
        "TURTLE_IMAGES keys must exactly match TURTLE_NAMES"
    )


def test_image_files_exist_on_disk():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, rel_path in TURTLE_IMAGES.items():
        full = os.path.join(project_root, rel_path)
        assert os.path.isfile(full), f"Missing image for {name}: {full}"


def test_bet_image_size_is_positive_int():
    assert isinstance(BET_IMAGE_SIZE, int)
    assert BET_IMAGE_SIZE > 0
```

- [ ] **Step 2: Install pytest if needed and run the tests**

Run: `python -m pip install pytest && python -m pytest tests/test_constants.py -v`

Expected: All 3 tests PASS. (They will also pass on a clean checkout because Task 1 is already merged.)

If any fails, fix the issue in `constants.py` before continuing.

- [ ] **Step 3: Commit**

```
git add tests/test_constants.py
git commit -m "Add unit tests for TURTLE_IMAGES map"
```

---

### Task 3: Rewrite `get_user_input()` to a 2x2 image grid

**Files:**
- Modify: `main.py:16-60`

- [ ] **Step 1: Replace the body of `get_user_input()`**

Replace the entire current `get_user_input()` (lines 16–60) with:

```python
def get_user_input():
    selected = [None]

    dialog = tkinter.Toplevel()
    dialog.title("Turtle Racing")
    dialog.resizable(False, False)
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # force a choice

    tkinter.Label(
        dialog,
        text="Which turtle do you think will win the race?",
        font=("Arial", 12, "bold"),
        pady=12,
    ).grid(row=0, column=0, columnspan=2, padx=20, pady=(12, 8))

    # 2x2 layout matching the position hints encoded in the asset filenames:
    #   Leonardo (top-left)    Donatello (top-right)
    #   Raphael (bottom-left)  Michaelangelo (bottom-right)
    grid_layout = [
        ("Leonardo", 1, 0),
        ("Donatello", 1, 1),
        ("Raphael", 2, 0),
        ("Michaelangelo", 2, 1),
    ]

    # Hold PhotoImage references on the dialog so Tk doesn't garbage-collect them.
    dialog._bet_images = []

    for name, row, col in grid_layout:
        idx = TURTLE_NAMES.index(name)  # 0-based; bet returned is idx + 1

        img = Image.open(resource_path(TURTLE_IMAGES[name]))
        img = img.resize((BET_IMAGE_SIZE, BET_IMAGE_SIZE), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        dialog._bet_images.append(photo)

        def make_cb(bet_index):
            def cb():
                selected[0] = bet_index
                dialog.destroy()
            return cb

        tkinter.Button(
            dialog,
            image=photo,
            text=name,
            compound="top",
            font=("Arial", 11, "bold"),
            padx=8,
            pady=8,
            command=make_cb(idx + 1),
        ).grid(row=row, column=col, padx=12, pady=8)

    # Center on screen
    dialog.update_idletasks()
    w, h = dialog.winfo_width(), dialog.winfo_height()
    x = (dialog.winfo_screenwidth() - w) // 2
    y = (dialog.winfo_screenheight() - h) // 2
    dialog.geometry(f"+{x}+{y}")

    dialog.grab_set()
    dialog.wait_window()

    return selected[0], False
```

Key points:
- `TURTLE_NAMES.index(name)` recovers the bet index, so the contract with `announce_result` and the cheat-mode check is unchanged.
- `compound="top"` puts the image above the text on a single button — entire cell is clickable.
- `dialog._bet_images` keeps the four `PhotoImage` objects alive for the dialog's lifetime.
- Removed the trailing `tkinter.Frame(dialog, height=10).pack()` spacer — `pack` cannot be mixed with `grid` on the same parent.

- [ ] **Step 2: Run the existing tests to make sure constants still pass**

Run: `python -m pytest tests/ -v`

Expected: 3 PASS.

- [ ] **Step 3: Manually launch the app and verify the dialog**

Run: `python main.py`

Verify:
1. The bet dialog opens centered with a 2x2 grid of four turtle images.
2. The captions read (top row, left→right): **Leonardo**, **Donatello**; (bottom row): **Raphael**, **Michaelangelo**.
3. Each caption matches the character shown in the image (Leo = blue mask, Donnie = purple, Raph = red, Mikey = orange).
4. Clicking any image closes the dialog and the race begins.
5. After picking, the win/lose announcement still works and pencolor matching is intact (try a few rounds).
6. Clicking the dialog's window-close (X) does nothing — choice is forced (existing behavior).

If any of those fail, stop and fix before moving on. Common failure: blank/empty buttons usually means the `dialog._bet_images` reference was lost — re-check that it's stored on the dialog.

- [ ] **Step 4: Commit**

```
git add main.py
git commit -m "Replace bet dialog buttons with 2x2 TMNT image grid"
```

---

### Task 4: Bundle assets in PyInstaller spec

**Files:**
- Modify: `reptile_race.spec:7`

- [ ] **Step 1: Update the `datas` line**

In `reptile_race.spec`, change line 7 from:

```python
    datas=[('lawn.jpg', '.')],
```

to:

```python
    datas=[('lawn.jpg', '.'), ('assets/*.jpg', 'assets')],
```

- [ ] **Step 2: Rebuild the executable**

Run: `python -m PyInstaller reptile_race.spec --noconfirm`

Expected: Build completes without errors. `dist/ReptileRace.exe` (or `dist/ReptileRace/`) exists.

- [ ] **Step 3: Run the bundled exe and verify images render**

Launch: `dist\ReptileRace.exe` (Windows) — open the bet dialog and confirm all four turtle images display.

If the dialog appears with empty buttons or throws "file not found" for an asset, the bundling didn't include the JPGs — re-check the `datas` glob and the build output for `assets/` files in the bundle.

- [ ] **Step 4: Commit**

```
git add reptile_race.spec
git commit -m "Bundle assets/ JPGs in PyInstaller build"
```

---

## Self-Review

**Spec coverage:**
- Constants additions → Task 1 ✓
- 2x2 layout with image+name buttons → Task 3 ✓
- Image loading via PIL + GC-safe references → Task 3 ✓
- PyInstaller bundling → Task 4 ✓
- Risk mitigations (name-keyed dict, manual visual verification, GC reference note) → Tasks 1, 3 ✓
- Out-of-scope items (no hover state, no race changes, no name/color reordering) → respected ✓

**Placeholder scan:** None.

**Type consistency:** `TURTLE_IMAGES`, `BET_IMAGE_SIZE`, `TURTLE_NAMES`, `resource_path`, `dialog._bet_images` — names used identically across all tasks.

**Notes for the implementer:** Keep the dict key `"Michaelangelo"` exactly as spelled (it's the existing, intentionally-preserved spelling in `TURTLE_NAMES`). Race-loop code matches turtles by `pencolor()`, not by name — do not change `TURTLE_COLORS`/`TURTLE_NAMES` ordering.
