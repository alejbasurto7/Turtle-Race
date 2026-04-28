import os
import sys
import random
from turtle import Turtle, Screen
from constants import *


def resource_path(rel_path):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)


def get_user_input():
    bet = ""
    options = ""
    for index in range(1, len(TURTLE_COLORS) + 1):
        if index == len(TURTLE_COLORS):
            options += f"  ‣ {index}: {TURTLE_COLORS[index - 1]}"
        else:
            options += f"  ‣ {index}: {TURTLE_COLORS[index - 1]}\n"

    valid_input = False
    is_cheating_intended = False

    while not valid_input:

        bet = s.textinput(title="Turtle Racing",
                          prompt=f"Which turtle do you think will win the race?\n{options}\nEnter a number: ").lower()

        if bet.startswith(" "):
            bet = bet.strip()
            is_cheating_intended = True
            print("🤥")

        if bet.isnumeric() and int(bet) <= len(TURTLE_COLORS):
            valid_input = True

    return int(bet), is_cheating_intended


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


def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b


def announce_result(winner, bet):
    if winner.pencolor() == turtles[bet - 1]['o'].pencolor():
        print(f"You won! The {winner.pencolor()} 🐢 is the winner!")
    else:
        print(f"You lose. The {winner.pencolor()} 🐢 is the winner.")


def celebrate(winner):

    orientations = [0, 90, 180, 270]

    s.colormode(255)
    winner.penup()
    winner.home()
    # winner.color(winning_color)
    winner.shapesize(2)
    winner.pendown()
    winner.speed("fast")
    winner.pensize(15)
    winner.home()

    for i in range(5):
        winner.shapesize(2+i)
        winner.setheading(random.choice(orientations))
        winner.pencolor(random_color())
        winner.forward(30)
        winner.circle(25 * i)


# Execution starts here
s = Screen()
s.title("Turtle Race")
s.setup(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
s.bgpic(resource_path("lawn.gif"))

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

announce_result(winning_turtle, user_bet)

celebrate(winning_turtle)

s.exitonclick()
