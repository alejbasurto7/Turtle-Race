import os
import sys
import random
import tkinter
import tkinter.messagebox
from turtle import Turtle, Screen
from PIL import Image, ImageTk
from constants import *


def resource_path(rel_path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)


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
    ).pack(padx=30)

    for i, name in enumerate(TURTLE_NAMES):
        def make_cb(idx):
            def cb():
                selected[0] = idx + 1
                dialog.destroy()
            return cb
        tkinter.Button(
            dialog,
            text=name,
            bg=TURTLE_COLORS[i],
            fg="white",
            font=("Arial", 11, "bold"),
            width=20,
            pady=6,
            command=make_cb(i),
        ).pack(padx=30, pady=4)

    tkinter.Frame(dialog, height=10).pack()

    # Center on screen
    dialog.update_idletasks()
    w, h = dialog.winfo_width(), dialog.winfo_height()
    x = (dialog.winfo_screenwidth() - w) // 2
    y = (dialog.winfo_screenheight() - h) // 2
    dialog.geometry(f"+{x}+{y}")

    dialog.grab_set()
    dialog.wait_window()

    return selected[0], False


def draw_start_line():
    start_line = Turtle()
    start_line.hideturtle()
    start_line.penup()
    start_line.goto(-(WINDOW_WIDTH / 2) + TURTLE_LENGTH, WINDOW_HEIGHT / 2)
    start_line.right(90)
    start_line.pendown()
    start_line.forward(WINDOW_HEIGHT)


def create_turtles(color_list):
    t = []
    for turtle_color in color_list:
        t.append({'color': turtle_color, 'o': Turtle(shape="turtle")})
    return t


def set_turtles_start_line(turtles_list):
    starting_x = -(WINDOW_WIDTH / 2) + 20
    turtles_number = len(turtles_list)
    y_position = 50 + ((turtles_number * TURTLE_HEIGHT) + (SPACING * (turtles_number - 1)))/2
    for tortuga in turtles_list:
        tortuga['o'].color(tortuga['color'])
        tortuga['o'].penup()
        tortuga['o'].goto(x=starting_x, y=y_position)
        y_position -= SPACING


def announce_result(winner, bet):
    if winner.pencolor() == turtles[bet - 1]['o'].pencolor():
        print(f"You won! The {winner.pencolor()} 🐢 is the winner!")
        writer = Turtle()
        writer.hideturtle()
        writer.penup()
        writer.goto(0, 0)
        writer.color("gold")
        writer.write("YOU WIN!", align="center", font=("Arial", 72, "bold"))
    else:
        print(f"You lose. The {winner.pencolor()} 🐢 is the winner.")
        writer = Turtle()
        writer.hideturtle()
        writer.penup()
        writer.goto(0, 30)
        writer.color("tomato")
        writer.write("SORRY, BRUH!", align="center", font=("Arial", 32, "bold"))


def celebrate(winner, won):
    face_color = winner.pencolor()
    winner.penup()
    winner.home()
    winner.hideturtle()
    winner.speed("normal")
    winner.pensize(3)
    winner.color(face_color)

    R = 60

    # Face outline
    winner.penup()
    winner.goto(0, -R)
    winner.setheading(0)
    winner.pendown()
    winner.circle(R)

    # Left eye
    winner.penup()
    winner.goto(-22, 14)
    winner.pendown()
    winner.begin_fill()
    winner.circle(5)
    winner.end_fill()

    # Right eye
    winner.penup()
    winner.goto(14, 14)
    winner.pendown()
    winner.begin_fill()
    winner.circle(5)
    winner.end_fill()

    # Mouth
    winner.penup()
    winner.pensize(4)
    if won:
        # Smile: start west of center (0,-20), face south → arc goes through bottom → arch down
        winner.goto(-24, -20)
        winner.setheading(270)
        winner.pendown()
        winner.circle(24, 180)
    else:
        # Frown: start east of center (0,-30), face north → arc goes through top → arch up
        winner.goto(24, -30)
        winner.setheading(90)
        winner.pendown()
        winner.circle(24, 180)


# Execution starts here
s = Screen()
s.title("Turtle Race")
s.setup(width=1.0, height=1.0)
WINDOW_WIDTH = s.window_width()
WINDOW_HEIGHT = s.window_height()


def set_background():
    canvas = s.getcanvas()
    img = Image.open(resource_path("lawn.jpg"))
    scale = max(WINDOW_WIDTH / img.width, WINDOW_HEIGHT / img.height)
    new_w, new_h = int(img.width * scale), int(img.height * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - WINDOW_WIDTH) // 2
    top = (new_h - WINDOW_HEIGHT) // 2
    img = img.crop((left, top, left + WINDOW_WIDTH, top + WINDOW_HEIGHT))
    bg = ImageTk.PhotoImage(img)
    item = canvas.create_image(-WINDOW_WIDTH // 2, -WINDOW_HEIGHT // 2, image=bg, anchor="nw")
    canvas.tag_lower(item)
    canvas._bg_photo = bg

keep_playing = True
first_run = True

while keep_playing:
    if not first_run:
        s.clear()
    first_run = False

    set_background()
    turtles = create_turtles(TURTLE_COLORS)
    set_turtles_start_line(turtles)

    user_bet, cheat_mode = get_user_input()

    # Start of race
    first_place = False
    is_race_on = True

    while is_race_on:

        for turtle in turtles:

            # Cheat mode ###############################################################
            #  Favoring this turtle...
            if turtle['o'].pencolor() == turtles[user_bet - 1]['o'].pencolor() and cheat_mode:
                random_distance = random.randint(2, MAX_PACE)
            #   ...over the rest
            else:
                random_distance = random.randint(0, MAX_PACE)
            # ##########################################################################

            turtle['o'].forward(random_distance)

            # If the turtle crosses the finish line
            if turtle['o'].xcor() >= ((WINDOW_WIDTH - TURTLE_LENGTH) / 2) and not first_place:
                winning_turtle = turtle['o']
                first_place = True
                is_race_on = False

    user_won = winning_turtle.pencolor() == turtles[user_bet - 1]['o'].pencolor()
    celebrate(winning_turtle, user_won)
    announce_result(winning_turtle, user_bet)

    keep_playing = tkinter.messagebox.askyesno("Turtle Race", "Do you want to play again?")

s.bye()
