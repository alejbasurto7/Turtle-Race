# Documentation Review — Phase 4

## Verdict: adequate

All meaningful public API changes are documented. CLAUDE.md is current. The
one actionable gap (a non-obvious invariant inside `_rebuild_columns`) is
low-cost to fix, but optional for a solo project.

---

## Public API docs (function docstrings, module-level docs)

**`dialogs.show_leaderboard()` — adequate.**

The docstring covers every caller-visible surface:

- Layout (rows 0–3, what lives in each row).
- Column reshape behavior under both `Group by` values, with the exact column
  sequences spelled out.
- Track combobox auto-disable/re-enable semantic and value preservation.
- Reset confirmation default=NO policy.
- X-button equivalent to Close.

The one detail the docstring omits is the Track combobox default value list
(`["All Tracks"] + leaderboard.known_tracks()` populated at open time,
refreshed after each reset). This is the kind of dynamic-population behavior
that trips up callers who expect a static list. However, for a single-developer
project where the caller is `main.py` calling the function opaquely, the
omission does not create a practical hazard.

**`_FILTER_LABEL_TO_KEY` — adequate.**

The module-level comment explains what it is and why "All Tracks" is handled
outside it (inline in `_repopulate`). That inline comment
(`# Track filter is disabled; ignore its value per CONTEXT-4 Decision 2.`)
is present on dialogs.py line 585 and covers the non-obvious bypass.

**Inner helpers — adequate.**

All three inner helpers have docstrings:
- `_refresh_track_combo` — one-line docstring, sufficient.
- `_rebuild_columns` — one-line docstring ("Reconfigure Treeview columns for
  the active group-by key"). See Inline code comments section below for a
  potential addition.
- `_repopulate` — one-line docstring, sufficient.

---

## Architecture docs (CLAUDE.md)

**"Round loop shape" section — current.**

The Phase 3 DOCUMENTATION-3 report flagged this section as stale (still
describing `while keep_playing` / `ask_play_again()`). That fix was applied
before Phase 4: CLAUDE.md line 82 now correctly reads `dialogs.get_main_menu_choice()
returns "race" | "leaderboard" | "quit"`, and the race-round flow on line 86
includes `leaderboard.record_race(...)`. The section is accurate as of the
current codebase.

**`main()` structural comment — present.**

The Phase 3 DOCUMENTATION-3 "NOW" action to add a comment at the top of
`main()` explaining the two-loop / sentinel pattern was also completed.
`main.py` lines 15–18 contain the four-line comment. No action needed.

**"tkinter" Architecture bullet — minor stale (no action needed).**

The bullet still says "three modal dialogs" and mentions the `messagebox`.
Phase 3 added `get_main_menu_choice`, `ask_play_again_choice`, and Phase 4
adds `show_leaderboard` — six dialogs total now, no raw `messagebox` call.
This is cosmetic. ROADMAP.md Phase 5 explicitly reserves a CLAUDE.md sweep;
defer the count update there.

**Leaderboard module — not in CLAUDE.md (intentional).**

ROADMAP.md Phase 5 success criteria include: "CLAUDE.md gains a short addendum
(10–20 lines) covering: the new main-menu entry point, the `%APPDATA%` data
path, the `leaderboard.py` Tk-free invariant, and a pointer to the JSON schema
version field." That work is out of scope for Phase 4 and should not be done
now. Recording it here as a confirmed Phase 5 TODO so it is not forgotten.

---

## User-facing docs (README.md, in-app help, etc.)

No README.md exists in the project root. ROADMAP.md Phase 5 notes: "If no
README, this bullet is skipped without ceremony." No action.

The leaderboard window is self-explanatory from its own UI (filter labels,
button labels, empty-state label). No in-app help text is warranted.

---

## Inline code comments

**`_rebuild_columns` — one non-obvious WHY is missing.**

The function re-applies headings/widths/anchors unconditionally after every
`configure(columns=...)` call. To a reader, the loop looks redundant because
headings were set up at widget-creation time. The WHY is non-obvious: Tk's
Treeview resets heading text and column geometry to defaults across a
`configure(columns=...)` call, so the re-application is mandatory, not
defensive.

SUMMARY-1.1.md §Decisions records this explicitly:
  "`_rebuild_columns` reconfigures via `dialog._tree.configure(columns=...)` then
  re-applies headings/widths/anchors in a loop. Tk's Treeview does NOT preserve
  heading text or column geometry across `configure(columns=...)` — they reset to
  defaults — so the loop is necessary, not redundant."

This is exactly the kind of WHY that justifies a comment per CLAUDE.md's
guideline. The current one-line docstring ("Reconfigure Treeview columns for
the active group-by key") does not capture it. A single inline comment on the
`configure()` call would close this gap.

**`_repopulate` Track bypass comment — adequate.**

Line 585 (`# Track filter is disabled; ignore its value per CONTEXT-4 Decision 2.`)
explains the WHY (disabling prevents nonsensical filter combinations, not a bug)
and cites the design authority. Sufficient.

**`dialog._empty_label.grid_remove()` — adequate.**

Line 467 has an inline comment explaining that `grid_remove()` is used (not
`grid_forget()`) so position metadata is preserved for the subsequent `grid()`
call. The WHY is present.

---

## Recommended actions

| Action | Priority | Rationale |
| --- | --- | --- |
| Add a one-line comment on the `_rebuild_columns` `configure()` call noting that Tk resets heading/column geometry across this call | LOW | The only WHY in the function body that isn't self-evident; SUMMARY-1.1.md already has the text, just not in the code |
| Phase 5: add CLAUDE.md addendum on leaderboard module, `%APPDATA%` data path, Tk-free invariant, JSON schema version | PHASE-5 | Explicitly required by ROADMAP.md Phase 5 success criteria — do not do now |
| Phase 5: update "tkinter" Architecture bullet (dialog count, no raw messagebox) | PHASE-5 | Cosmetic staleness; ROADMAP.md Phase 5 reserves the sweep |

The single LOW-priority action (the `_rebuild_columns` WHY comment) is the
only Phase-4-NOW candidate. Everything else is either already correct or
deliberately deferred to Phase 5.
