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


def get_user_species():
    """Show a modal dialog with composite species images and return the chosen species.

    Returns:
        str: ``"turtles"`` or ``"snakes"`` — a key in ``constants.SPECIES``.
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

    # Center on screen
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
