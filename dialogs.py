import tkinter
import tkinter.messagebox

from PIL import Image, ImageTk

import tracks
from constants import (
    TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE,
    SNAKE_IMAGES, SPECIES, SPECIES_DIALOG_IMAGE_SIZE,
)
from paths import resource_path

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

    # Center on screen
    dialog.update_idletasks()
    w, h = dialog.winfo_width(), dialog.winfo_height()
    x = (dialog.winfo_screenwidth() - w) // 2
    y = (dialog.winfo_screenheight() - h) // 2
    dialog.geometry(f"+{x}+{y}")

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
        (tracks.STRAIGHT,    "Straight",    "assets/track_straight.png",    0),
        (tracks.RECTANGULAR, "Rectangular", "assets/track_rectangular.png", 1),
        (tracks.SPIRAL,      "Spiral",      "assets/track_spiral.png",      2),
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

    dialog.update_idletasks()
    w, h = dialog.winfo_width(), dialog.winfo_height()
    x = (dialog.winfo_screenwidth() - w) // 2
    y = (dialog.winfo_screenheight() - h) // 2
    dialog.geometry(f"+{x}+{y}")

    dialog.grab_set()
    dialog.wait_window()

    return selected[0]


def ask_play_again():
    return tkinter.messagebox.askyesno("Turtle Race", "Do you want to play again?")
