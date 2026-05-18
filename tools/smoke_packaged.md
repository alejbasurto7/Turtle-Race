# Phase 5 — Manual Packaged-Exe Smoke Checklist

> **This is the manual gate before any actual release.**
> The automated source-mode equivalents are in `tools/smoke_phase_5.py` — running
> both is the full Phase 5 smoke. This checklist requires a Windows host with
> PyInstaller installed and write access to `%APPDATA%\ReptileRace\`.
> Complete every step in order and record PASS or FAIL for each.

---

## Pre-flight

Before building the exe, confirm the source-mode baseline is clean:

- [ ] `pyinstaller` is installed (`pyinstaller --version` prints a version string).
- [ ] `python tools/smoke_phase_5.py` exits 0 and prints
  `[smoke] phase 5 smoke PASS — path resolution + file lifecycle verified`
  as its final substantive line. (Catches source-mode regressions before
  wasting a build cycle.)
- [ ] `pytest -q` reports **135 passed** (no regressions in the test suite).

---

## Step-by-step checklist

### Step 1 — Clean previous build artifacts

**Action:** Delete `build/` and `dist/` directories.

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
```

**Verify:** `dist/` does not exist; `build/` does not exist.

- [ ] PASS  - [ ] FAIL

---

### Step 2 — Build the exe

**Action:** Run `pyinstaller reptile_race.spec` from the project root.

```powershell
pyinstaller reptile_race.spec
```

**Verify:** command exits 0; `dist/ReptileRace.exe` exists and is larger than
0 bytes.

- [ ] PASS  - [ ] FAIL

---

### Step 3 — (Recommended) Wipe stale leaderboard state

**Action:** Remove any existing leaderboard file to make later assertions
deterministic.

```powershell
Remove-Item "$env:APPDATA\ReptileRace\leaderboard.json" -ErrorAction SilentlyContinue
```

**Verify:** `Test-Path "$env:APPDATA\ReptileRace\leaderboard.json"` returns `False`.

- [ ] PASS  - [ ] FAIL

---

### Step 4 — First launch

**Action:** Launch the packaged exe.

```powershell
.\dist\ReptileRace.exe
```

Or double-click `dist\ReptileRace.exe` from Explorer.

**Verify:** Main menu opens showing Race / View Leaderboard / Quit options.
Background music plays.

- [ ] PASS  - [ ] FAIL

---

### Step 5 — Race once

**Action:** From the main menu:

1. Choose **Race**.
2. Pick any track.
3. Pick any species.
4. Place any bet.
5. Wait for the race to complete.
6. On the post-race prompt, choose **Quit**.

**Verify:** The app exits cleanly (window closes, no error dialog or traceback).

- [ ] PASS  - [ ] FAIL

---

### Step 6 — Verify the JSON file appeared with the race

**Action:** In PowerShell, inspect the leaderboard file.

```powershell
Get-Content "$env:APPDATA\ReptileRace\leaderboard.json"
```

**Verify:**

- File exists at `%APPDATA%\ReptileRace\leaderboard.json`.
- JSON contains `"schema_version": 1`.
- `"races"` is a list with exactly 1 entry.
- That entry's `species`, `track`, and `finish_order` match the race you ran
  in Step 5.

- [ ] PASS  - [ ] FAIL

---

### Step 7 — Re-launch and confirm All-Time view shows the race

**Action:** Run `.\dist\ReptileRace.exe` again. From the main menu choose
**View Leaderboard**.

**Verify:**

- With filters at their defaults (Time = **All Time**, Species = **All**,
  Track = **All Tracks**, Group by = **None**), the Treeview shows at least
  one row corresponding to the racer that won in Step 5.
- The **Current Session** filter returns an empty Treeview (this is a fresh
  launch — the absence of current-session rows is the `_MEIPASS` regression
  canary: it confirms the leaderboard is reading from `%APPDATA%`, not from
  inside the frozen `_MEIPASS` temp directory).

- [ ] PASS  - [ ] FAIL

---

### Step 8 — Reset Session leaves the file unchanged on disk

**Action:** While still in the leaderboard view, click **Reset Session** and
confirm **Yes** on the confirmation dialog.

**Verify:**

- The Treeview empties for Time = **Current Session** (already empty since
  this is a fresh launch — confirm it stays empty).
- Switch Time to **All Time**: the historic row from Step 6 is **still
  present**.
- Open the JSON file again:

  ```powershell
  Get-Content "$env:APPDATA\ReptileRace\leaderboard.json"
  ```

  It is unchanged — still 1 race, same content as after Step 6.

- [ ] PASS  - [ ] FAIL

---

### Step 9 — Reset All wipes the file to canonical empty

**Action:** While still in the leaderboard view, click **Reset All** and
confirm **Yes** on the confirmation dialog.

**Verify:**

- The Treeview is empty for **every** Time filter including All Time.
- Open the JSON file:

  ```powershell
  Get-Content "$env:APPDATA\ReptileRace\leaderboard.json"
  ```

  It now reads exactly `{"schema_version": 1, "races": []}` (or the
  equivalent pretty-printed form — verify by content, not byte equality).

- [ ] PASS  - [ ] FAIL

---

### Step 10 — Final exit

**Action:** Close the leaderboard window, then choose **Quit** from the main
menu.

**Verify:** App exits cleanly (window closes, no error dialog or traceback).

- [ ] PASS  - [ ] FAIL

---

## Sign-off

Tested by: ________   Date: ________   Build: `dist/ReptileRace.exe`  sha256: ________

> **Note:** The automated source-mode complement to this checklist is
> `tools/smoke_phase_5.py`. Run it before each build (pre-flight Step 2 above)
> to catch path-resolution and file-lifecycle regressions without requiring a
> full PyInstaller build cycle.
