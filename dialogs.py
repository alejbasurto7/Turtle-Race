import tkinter
import tkinter.messagebox
from tkinter import ttk

from PIL import Image, ImageTk

import tracks
from constants import (
    BET_IMAGE_SIZE,
    SNAKE_IMAGES, SPECIES, SPECIES_DIALOG_IMAGE_SIZE,
)
from paths import resource_path
import leaderboard

# 2×2 grid: positional order matches asset filename position hints.
#   Leonardo (top-left)    Donatello (top-right)
#   Raphael  (bottom-left) Michaelangelo (bottom-right)
_TURTLE_GRID_LAYOUT = [
    ("Leonardo",      1, 0),
    ("Donatello",     1, 1),
    ("Raphael",       2, 0),
    ("Michaelangelo", 2, 1),
]

# 1×3 row: SNAKE_NAMES order (Shadow | Ralph | Anaconda).
_SNAKE_ROW_LAYOUT = [
    ("Shadow",   1, 0),
    ("Ralph",    1, 1),
    ("Anaconda", 1, 2),
]

def _center_dialog(dialog):
    """Center ``dialog`` on the user's screen. Call after widgets are added and
    any explicit ``geometry("WxH")`` size has been set, but before
    ``grab_set()`` / ``wait_window()``. Falls back to the requested size when
    the window has not yet been mapped (so it works with both pack/grid layouts
    and dialogs that set their geometry explicitly)."""
    dialog.update_idletasks()
    w = dialog.winfo_width()
    h = dialog.winfo_height()
    if w <= 1:
        w = dialog.winfo_reqwidth()
    if h <= 1:
        h = dialog.winfo_reqheight()
    x = (dialog.winfo_screenwidth() - w) // 2
    y = (dialog.winfo_screenheight() - h) // 2
    dialog.geometry(f"+{x}+{y}")


# Maps user-facing combobox strings to leaderboard API enum values.
# Track names are leaderboard track strings already (no entry needed here);
# the "All Tracks" sentinel maps to "all" via explicit handling in _repopulate.
_FILTER_LABEL_TO_KEY = {
    # Time window
    "All Time":        "all",
    "Current Session": "session",
    "Today":           "today",
    "This Week":       "week",
    "This Month":      "month",
    "This Year":       "year",
    # Species
    "All":             "all",
    "Turtles":         "turtles",
    "Snakes":          "snakes",
    # Group by
    "None":            "none",
    "Track":           "track",
}


def get_main_menu_choice() -> str:
    """Return "race", "leaderboard", or "quit" — the user's main-menu choice.

    Toplevel modal over the lawn background. X-button (WM_DELETE_WINDOW) returns "quit"
    per CONTEXT-3 Decision 3. Three vertically stacked buttons in order Race / View
    Leaderboard / Quit. The Race button receives initial keyboard focus.
    """
    dialog = tkinter.Toplevel()
    dialog.title("Reptile Race")
    dialog.resizable(False, False)

    selected = [None]

    def make_cb(value):
        def cb():
            selected[0] = value
            dialog.destroy()
        return cb

    race_btn = tkinter.Button(dialog, text="Race", width=24, command=make_cb("race"))
    leaderboard_btn = tkinter.Button(dialog, text="View Leaderboard", width=24, command=make_cb("leaderboard"))
    quit_btn = tkinter.Button(dialog, text="Quit", width=24, command=make_cb("quit"))
    race_btn.pack(padx=20, pady=(20, 6))
    leaderboard_btn.pack(padx=20, pady=6)
    quit_btn.pack(padx=20, pady=(6, 20))
    race_btn.focus_set()  # Race is the primary action.

    dialog.protocol("WM_DELETE_WINDOW", make_cb("quit"))  # X → "quit", per CONTEXT-3 Decision 3.

    dialog.transient()
    _center_dialog(dialog)
    dialog.grab_set()
    dialog.wait_window()

    return selected[0]


def get_user_bet(species):
    """Show the species-appropriate bet dialog and return a 1-based racer index.

    Args:
        species: A key in constants.SPECIES — either "turtles" or "snakes".

    Returns:
        int: 1-based index into SPECIES[species]["names"] for the chosen racer.

    Raises:
        ValueError: If SPECIES[species]["bet_layout"] is an unrecognised value.
    """
    bet_layout = SPECIES[species]["bet_layout"]
    species_names = SPECIES[species]["names"]
    species_images = SPECIES[species]["images"]

    selected = [None]

    dialog = tkinter.Toplevel()
    dialog.resizable(False, False)
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # force a choice

    # Hold PhotoImage references on the dialog so Tk doesn't garbage-collect them.
    # Initialised before the if/elif so both branches append to the same list.
    dialog._bet_images = []

    def make_cb(bet_index):
        def cb():
            selected[0] = bet_index
            dialog.destroy()
        return cb

    if bet_layout == "grid_2x2":
        dialog.title("Turtle Racing")

        tkinter.Label(
            dialog,
            text="Which turtle do you think will win the race?",
            font=("Arial", 12, "bold"),
            pady=12,
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(12, 8))

        for name, row, col in _TURTLE_GRID_LAYOUT:
            idx = species_names.index(name)  # 0-based; bet returned is idx + 1

            img = Image.open(resource_path(species_images[name]))
            img = img.resize((BET_IMAGE_SIZE, BET_IMAGE_SIZE), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            dialog._bet_images.append(photo)

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

    elif bet_layout == "row_3":
        dialog.title("Snake Racing")

        tkinter.Label(
            dialog,
            text="Which snake do you think will win the race?",
            font=("Arial", 12, "bold"),
            pady=12,
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(12, 8))

        for name, row, col in _SNAKE_ROW_LAYOUT:
            idx = species_names.index(name)  # 0-based; bet returned is idx + 1

            img = Image.open(resource_path(species_images[name]))
            img = img.resize((BET_IMAGE_SIZE, BET_IMAGE_SIZE), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            dialog._bet_images.append(photo)

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

    else:
        raise ValueError(f"Unknown bet_layout: {bet_layout!r}")

    _center_dialog(dialog)
    dialog.grab_set()
    dialog.wait_window()

    return selected[0]


def get_user_track():
    selected = [None]

    dialog = tkinter.Toplevel()
    dialog.title("Race Track")
    dialog.resizable(False, False)
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)

    tkinter.Label(
        dialog,
        text="Pick a race track",
        font=("Arial", 12, "bold"),
        pady=12,
    ).grid(row=0, column=0, columnspan=3, padx=20, pady=(12, 8))

    dialog._track_images = []

    layout = [
        (tracks.STRAIGHT,    "Straight",    "assets/tracks/track_straight.png",    0),
        (tracks.RECTANGULAR, "Rectangular", "assets/tracks/track_rectangular.png", 1),
        (tracks.SPIRAL,      "Spiral",      "assets/tracks/track_spiral.png",      2),
    ]

    for track_name, label, image_path, col in layout:
        img = Image.open(resource_path(image_path))
        photo = ImageTk.PhotoImage(img)
        dialog._track_images.append(photo)

        def make_cb(name):
            def cb():
                selected[0] = name
                dialog.destroy()
            return cb

        tkinter.Button(
            dialog,
            image=photo,
            text=label,
            compound="top",
            font=("Arial", 11, "bold"),
            padx=8,
            pady=8,
            command=make_cb(track_name),
        ).grid(row=1, column=col, padx=12, pady=8)

    _center_dialog(dialog)
    dialog.grab_set()
    dialog.wait_window()

    return selected[0]


def get_user_species():
    """Modal dialog: ask the user to pick between Turtles and Snakes.

    Blocks (via grab_set() + wait_window()) until the user clicks one of the
    two species buttons. The WM_DELETE_WINDOW handler is a no-op, so the
    dialog cannot be dismissed without making a choice.

    Returns:
        str: ``"turtles"`` or ``"snakes"`` — keys into ``constants.SPECIES``.
    """
    selected = [None]

    dialog = tkinter.Toplevel()
    dialog.title("Choose Your Racers")
    dialog.resizable(False, False)
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # force a choice

    tkinter.Label(
        dialog,
        text="Which species will race?",
        font=("Arial", 12, "bold"),
        pady=12,
    ).grid(row=0, column=0, columnspan=2, padx=20, pady=(12, 8))

    # Hold PhotoImage references so Tk doesn't garbage-collect them.
    dialog._species_images = []

    def make_cb(value):
        def cb():
            selected[0] = value
            dialog.destroy()
        return cb

    # --- Turtles composite: 2×2 grid of the 4 turtle JPGs ---
    cell = SPECIES_DIALOG_IMAGE_SIZE // 2  # 100 px per cell
    turtle_composite = Image.new("RGBA", (SPECIES_DIALOG_IMAGE_SIZE, SPECIES_DIALOG_IMAGE_SIZE), (255, 255, 255, 0))
    for name, row, col in _TURTLE_GRID_LAYOUT:
        img = Image.open(resource_path(SPECIES["turtles"]["images"][name]))
        img = img.convert("RGBA")
        img = img.resize((cell, cell), Image.LANCZOS)
        x = col * cell
        y = (row - 1) * cell
        turtle_composite.paste(img, (x, y), img)
    turtle_photo = ImageTk.PhotoImage(turtle_composite)
    dialog._species_images.append(turtle_photo)

    tkinter.Button(
        dialog,
        image=turtle_photo,
        text="Turtles",
        compound="top",
        font=("Arial", 11, "bold"),
        padx=8,
        pady=8,
        command=make_cb("turtles"),
    ).grid(row=1, column=0, padx=12, pady=8)

    # --- Snakes composite: 1×3 row of the 3 snake PNGs ---
    cell_w = SPECIES_DIALOG_IMAGE_SIZE // 3  # 66 px per cell
    cell_h = SPECIES_DIALOG_IMAGE_SIZE       # 200 px tall (full height, squashed to square on resize)
    snake_composite = Image.new("RGBA", (cell_w * 3, cell_h), (255, 255, 255, 0))
    for name, _row, col in _SNAKE_ROW_LAYOUT:
        img = Image.open(resource_path(SPECIES["snakes"]["images"][name]))
        img = img.convert("RGBA")
        img = img.resize((cell_w, cell_h), Image.LANCZOS)
        x = col * cell_w
        snake_composite.paste(img, (x, 0), img)
    snake_composite = snake_composite.resize(
        (SPECIES_DIALOG_IMAGE_SIZE, SPECIES_DIALOG_IMAGE_SIZE), Image.LANCZOS
    )
    snake_photo = ImageTk.PhotoImage(snake_composite)
    dialog._species_images.append(snake_photo)

    tkinter.Button(
        dialog,
        image=snake_photo,
        text="Snakes",
        compound="top",
        font=("Arial", 11, "bold"),
        padx=8,
        pady=8,
        command=make_cb("snakes"),
    ).grid(row=1, column=1, padx=12, pady=8)

    _center_dialog(dialog)
    dialog.grab_set()
    dialog.wait_window()

    return selected[0]


def ask_play_again_choice() -> str:
    """Return "again", "menu", or "quit" — the user's post-race choice.

    Toplevel modal. X-button (WM_DELETE_WINDOW) returns "menu" per CONTEXT-3 Decision 4
    (the least-destructive close for the post-race context). Three horizontally arranged
    buttons in order Play Again / Main Menu / Quit. Play Again receives initial keyboard focus.
    """
    dialog = tkinter.Toplevel()
    dialog.title("Reptile Race")
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
    menu_btn = tkinter.Button(button_row, text="Main Menu", width=12, command=make_cb("menu"))
    quit_btn = tkinter.Button(button_row, text="Quit", width=12, command=make_cb("quit"))
    again_btn.pack(side="left", padx=4)
    menu_btn.pack(side="left", padx=4)
    quit_btn.pack(side="left", padx=4)
    again_btn.focus_set()  # Play Again is the primary action.

    dialog.protocol("WM_DELETE_WINDOW", make_cb("menu"))  # X → "menu", per CONTEXT-3 Decision 4.

    dialog.transient()
    _center_dialog(dialog)
    dialog.grab_set()
    dialog.wait_window()

    return selected[0]


def show_leaderboard() -> None:
    """Show the leaderboard window with four filters, a Treeview, and three buttons.

    Single Toplevel modal (no Notebook). Layout:
    - Row 0: filter row — Time / Species / Track / Group by ttk.Combobox widgets.
    - Row 1: inline empty-state label ("No races recorded"), shown only when the
             filtered query returns zero rows.
    - Row 2: ttk.Treeview with vertical scrollbar; columns reshape based on Group by
             (None → Rank/Racer/Points/Races/Wins/Podiums;
              Track → Track/Rank/Racer/Points/Races/Wins/Podiums).
    - Row 3: button row — Reset Session / Reset All / Close.

    Filter changes immediately re-query and repopulate the Treeview. The Track
    combobox is automatically disabled when Group by = Track (redundant then) and
    re-enabled with its previously-selected value when Group by returns to None.
    Reset Session and Reset All are each gated by a messagebox.askyesno confirmation
    with default=NO. X-button is equivalent to Close (dialog.destroy).
    """
    dialog = tkinter.Toplevel()
    dialog.title("Leaderboard")
    dialog.resizable(True, True)
    dialog.geometry("640x420")

    # --- Row 0: filter frame ---
    filter_frame = tkinter.Frame(dialog)
    filter_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

    tkinter.Label(filter_frame, text="Time:").grid(row=0, column=0, padx=(0, 2))
    dialog._time_combo = ttk.Combobox(
        filter_frame,
        values=["All Time", "Current Session", "Today", "This Week", "This Month", "This Year"],
        state="readonly",
        width=14,
    )
    dialog._time_combo.set("All Time")
    dialog._time_combo.grid(row=0, column=1, padx=(0, 8))

    tkinter.Label(filter_frame, text="Species:").grid(row=0, column=2, padx=(0, 2))
    dialog._species_combo = ttk.Combobox(
        filter_frame,
        values=["All", "Turtles", "Snakes"],
        state="readonly",
        width=8,
    )
    dialog._species_combo.set("All")
    dialog._species_combo.grid(row=0, column=3, padx=(0, 8))

    tkinter.Label(filter_frame, text="Track:").grid(row=0, column=4, padx=(0, 2))
    dialog._track_combo = ttk.Combobox(
        filter_frame,
        values=["All Tracks"],
        state="readonly",
        width=12,
    )
    dialog._track_combo.set("All Tracks")
    dialog._track_combo.grid(row=0, column=5, padx=(0, 8))

    tkinter.Label(filter_frame, text="Group by:").grid(row=0, column=6, padx=(0, 2))
    dialog._group_combo = ttk.Combobox(
        filter_frame,
        values=["None", "Track"],
        state="readonly",
        width=7,
    )
    dialog._group_combo.set("None")
    dialog._group_combo.grid(row=0, column=7)

    # --- Row 1: empty-state label (created up front, hidden immediately) ---
    dialog._empty_label = tkinter.Label(dialog, text="No races recorded")
    dialog._empty_label.grid(row=1, column=0, pady=4)
    dialog._empty_label.grid_remove()  # hidden; re-.grid() restores position without re-specifying coords

    # --- Row 2: Treeview + vertical scrollbar ---
    dialog.rowconfigure(2, weight=1)
    dialog.columnconfigure(0, weight=1)

    tree_frame = tkinter.Frame(dialog)
    tree_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=4)
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)

    dialog._tree = ttk.Treeview(
        tree_frame,
        columns=("rank", "racer", "points", "races", "wins", "podiums"),
        show="headings",
        height=12,
    )

    # Default column setup for Group by = None
    dialog._tree.heading("rank",    text="Rank")
    dialog._tree.heading("racer",   text="Racer")
    dialog._tree.heading("points",  text="Points")
    dialog._tree.heading("races",   text="Races")
    dialog._tree.heading("wins",    text="Wins")
    dialog._tree.heading("podiums", text="Podiums")

    dialog._tree.column("rank",    width=50,  anchor="center")
    dialog._tree.column("racer",   width=120, anchor="w")
    dialog._tree.column("points",  width=70,  anchor="center")
    dialog._tree.column("races",   width=70,  anchor="center")
    dialog._tree.column("wins",    width=70,  anchor="center")
    dialog._tree.column("podiums", width=70,  anchor="center")

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=dialog._tree.yview)
    dialog._tree.configure(yscrollcommand=scrollbar.set)

    dialog._tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    # --- Row 3: button row ---
    def _on_reset_session():
        if tkinter.messagebox.askyesno(
            "Reset Session",
            "Clear current session stats?",
            default=tkinter.messagebox.NO,
            parent=dialog,
        ):
            leaderboard.reset_session()
            _refresh_track_combo()
            _repopulate()

    def _on_reset_all():
        if tkinter.messagebox.askyesno(
            "Reset All",
            "Delete all race history? This cannot be undone.",
            default=tkinter.messagebox.NO,
            parent=dialog,
        ):
            leaderboard.reset_all()
            _refresh_track_combo()
            _repopulate()

    btn_frame = tkinter.Frame(dialog)
    btn_frame.grid(row=3, column=0, pady=(4, 8))

    tkinter.Button(btn_frame, text="Reset Session", width=14, command=_on_reset_session).pack(side="left", padx=6)
    tkinter.Button(btn_frame, text="Reset All",     width=14, command=_on_reset_all).pack(side="left", padx=6)
    tkinter.Button(btn_frame, text="Close",         width=10, command=dialog.destroy).pack(side="left", padx=6)

    # --- Filter callbacks ---

    def _refresh_track_combo():
        """Refresh Track combobox values from leaderboard history; preserve selection if still valid."""
        current = dialog._track_combo.get()
        known = leaderboard.known_tracks()
        new_values = ["All Tracks"] + known
        dialog._track_combo["values"] = new_values
        if current in new_values:
            dialog._track_combo.set(current)
        else:
            dialog._track_combo.set("All Tracks")

    def _rebuild_columns(group_by_key):
        """Reconfigure Treeview columns for the active group-by key."""
        if group_by_key == "none":
            cols = ("rank", "racer", "points", "races", "wins", "podiums")
            dialog._tree.configure(columns=cols)
            headings = {"rank": "Rank", "racer": "Racer", "points": "Points",
                        "races": "Races", "wins": "Wins", "podiums": "Podiums"}
            widths   = {"rank": 50,  "racer": 120, "points": 70,
                        "races": 70, "wins":  70,  "podiums": 70}
            anchors  = {"rank": "center", "racer": "w", "points": "center",
                        "races": "center", "wins": "center", "podiums": "center"}
        else:  # "track"
            cols = ("track", "rank", "racer", "points", "races", "wins", "podiums")
            dialog._tree.configure(columns=cols)
            headings = {"track": "Track", "rank": "Rank", "racer": "Racer",
                        "points": "Points", "races": "Races", "wins": "Wins", "podiums": "Podiums"}
            widths   = {"track": 110, "rank": 50,  "racer": 110, "points": 70,
                        "races": 70,  "wins": 70,  "podiums": 70}
            anchors  = {"track": "w", "rank": "center", "racer": "w",
                        "points": "center", "races": "center", "wins": "center", "podiums": "center"}
        for col in cols:
            dialog._tree.heading(col, text=headings[col])
            dialog._tree.column(col, width=widths[col], anchor=anchors[col])

    def _repopulate():
        """Read current filter values, query leaderboard, and repopulate the Treeview."""
        time_key    = _FILTER_LABEL_TO_KEY[dialog._time_combo.get()]
        species_key = _FILTER_LABEL_TO_KEY[dialog._species_combo.get()]
        group_by_key = _FILTER_LABEL_TO_KEY[dialog._group_combo.get()]

        # Single delete pass before batch insert — flicker-free.
        dialog._tree.delete(*dialog._tree.get_children())

        if group_by_key == "none":
            track_label = dialog._track_combo.get()
            track_key   = "all" if track_label == "All Tracks" else track_label
            rows = leaderboard.query(time_key, species_key, track_key)
            for row in rows:
                dialog._tree.insert("", "end", values=(
                    row.rank, row.racer_name, row.points, row.races, row.wins, row.podiums,
                ))
        else:  # group_by_key == "track"
            # Track filter is disabled; ignore its value per CONTEXT-4 Decision 2.
            rows = leaderboard.query_per_track(time_key, species_key)
            for row in rows:
                dialog._tree.insert("", "end", values=(
                    row.track, row.rank, row.racer_name, row.points, row.races, row.wins, row.podiums,
                ))

        # Toggle empty-state label.
        if len(rows) == 0:
            dialog._empty_label.grid()
        else:
            dialog._empty_label.grid_remove()

    def _on_filter_change(event=None):
        _repopulate()

    def _on_group_by_change(event=None):
        # 1. Read new group_by_key.
        group_by_key = _FILTER_LABEL_TO_KEY[dialog._group_combo.get()]
        # 2. Toggle Track combobox state; preserve selected value.
        dialog._track_combo.configure(state="disabled" if group_by_key == "track" else "readonly")
        # 3. Reshape columns.
        _rebuild_columns(group_by_key)
        # 4. Repopulate.
        _repopulate()

    dialog._time_combo.bind("<<ComboboxSelected>>",    _on_filter_change)
    dialog._species_combo.bind("<<ComboboxSelected>>", _on_filter_change)
    dialog._track_combo.bind("<<ComboboxSelected>>",   _on_filter_change)
    dialog._group_combo.bind("<<ComboboxSelected>>",   _on_group_by_change)

    # --- Initial population ---
    _refresh_track_combo()
    _repopulate()

    # --- Modal lifecycle ---
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.transient()
    _center_dialog(dialog)
    dialog.grab_set()
    dialog.wait_window()
