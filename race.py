import random
import time
from turtle import Turtle, Screen

from PIL import Image, ImageTk

import tracks
from constants import MAX_PACE, TICK_DELAY, TRACK_PADDING, TURTLE_NAMES
from paths import resource_path


_screen = None

CELEBRATION_Y = 180  # vertical offset so face/text aren't hidden by the centered "play again?" dialog

STONE_COLOR = "gray30"
STONE_DIAMETER = 3


def make_screen():
    """Create the turtle Screen singleton and push its dimensions into tracks."""
    global _screen
    if _screen is not None:
        return _screen
    _screen = Screen()
    _screen.title("Turtle Race")
    _screen.setup(width=1.0, height=1.0)
    tracks.set_window_size(_screen.window_width(), _screen.window_height())
    return _screen


def get_screen():
    if _screen is None:
        raise RuntimeError("make_screen() must be called before get_screen()")
    return _screen


def set_background():
    width = _screen.window_width()
    height = _screen.window_height()
    canvas = _screen.getcanvas()
    img = Image.open(resource_path("lawn.jpg"))
    scale = max(width / img.width, height / img.height)
    new_w, new_h = int(img.width * scale), int(img.height * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - width) // 2
    top = (new_h - height) // 2
    img = img.crop((left, top, left + width, top + height))
    bg = ImageTk.PhotoImage(img)
    item = canvas.create_image(-width // 2, -height // 2, image=bg, anchor="nw")
    canvas.tag_lower(item)
    canvas._bg_photo = bg


def _draw_segment(p0, p1):
    pen = Turtle()
    pen.hideturtle()
    pen.penup()
    pen.goto(*p0)
    pen.pendown()
    pen.goto(*p1)
    pen.penup()


def draw_start_line(track_name):
    _screen.tracer(0)
    for p0, p1 in tracks.start_line_segments(track_name):
        _draw_segment(p0, p1)
    _screen.update()
    _screen.tracer(1)


def draw_boundary_stones(track_name):
    _screen.tracer(0)
    pen = Turtle()
    pen.hideturtle()
    pen.penup()
    pen.color(STONE_COLOR)
    for x, y in tracks.boundary_stones(track_name):
        pen.goto(x, y)
        pen.dot(STONE_DIAMETER, STONE_COLOR)
    _screen.update()
    _screen.tracer(1)


def draw_finish_line(track_name):
    _screen.tracer(0)
    for p0, p1 in tracks.finish_line_segments(track_name):
        _draw_segment(p0, p1)
    _screen.update()
    _screen.tracer(1)


def create_turtles(color_list):
    t = []
    for turtle_color in color_list:
        t.append({'color': turtle_color, 'o': Turtle(shape="turtle")})
    return t


def place_turtles_on_track(turtles_list, track_name):
    _screen.tracer(0)
    for i, tortuga in enumerate(turtles_list):
        x, y, heading = tracks.lane_start_pose(track_name, i)
        tortuga['o'].hideturtle()
        tortuga['o'].color(tortuga['color'])
        tortuga['o'].penup()
        tortuga['o'].setheading(heading)
        tortuga['o'].goto(x, y)
        tortuga['o'].showturtle()
    _screen.update()
    _screen.tracer(1)


def run_race(turtles_list, track_name, user_bet):
    """Race loop. All lanes advance the same expected `s` per tick, then
    each turtle's visual position is computed at `(s / shared_distance)`
    of its own path length. This keeps the race fair regardless of which
    lane has the longer perimeter.

    `shared_distance` is the midpoint between the straight-track length
    (preserves the original per-tick pace on straight) and the average lane
    length of the current track (caps how slow long tracks like spiral get),
    scaled by 1/SPEED_FACTOR so the per-tick visual movement lands at the
    target fraction of the natural pace.
    """
    SPEED_FACTOR = 0.3                       # 30% of the naive pace; tweak to taste
    lane_paths = tracks.build_lane_paths(track_name)
    lane_lengths = [tracks.path_length(p) for p in lane_paths]
    straight_length = _screen.window_width() - 2 * TRACK_PADDING
    avg_lane_length = sum(lane_lengths) / len(lane_lengths)
    shared_distance = ((straight_length + avg_lane_length) / 2) / SPEED_FACTOR
    progress = [0.0] * len(turtles_list)

    print(f"\n=== Race start: {track_name} ===")
    print(f"  shared_distance (progress target, equal for all lanes): {shared_distance:.1f}")
    print(f"  {'lane':>4}  {'name':<14} {'color':<12} {'start (x, y)':<22} {'lane_length':>11}")
    for i, turtle in enumerate(turtles_list):
        x0, y0 = lane_paths[i]["start"]
        name = TURTLE_NAMES[i] if i < len(TURTLE_NAMES) else f"#{i}"
        color = turtle['o'].pencolor()
        print(f"  {i:>4}  {name:<14} {color:<12} ({x0:>7.1f}, {y0:>7.1f})    {lane_lengths[i]:>11.1f}")

    winning_turtle = None
    winner_index = None
    first_place = False
    ticks = 0
    _screen.tracer(0)
    while not first_place:
        for i, turtle in enumerate(turtles_list):
            step = random.randint(0, MAX_PACE)
            progress[i] = min(progress[i] + step, shared_distance)
            fraction = progress[i] / shared_distance
            arc = fraction * lane_lengths[i]
            x, y, heading = tracks.position_at_arc(lane_paths[i], arc)
            turtle['o'].setheading(heading)
            turtle['o'].goto(x, y)
            if progress[i] >= shared_distance and not first_place:
                winning_turtle = turtle['o']
                winner_index = i
                first_place = True
        ticks += 1
        _screen.update()
        time.sleep(TICK_DELAY)
    _screen.tracer(1)

    print(f"--- Race end after {ticks} ticks ---")
    print(f"  {'lane':>4}  {'name':<14} {'distance':>10}  {'lane_length':>11}  {'% done':>7}")
    for i in range(len(turtles_list)):
        fraction = progress[i] / shared_distance
        distance = fraction * lane_lengths[i]
        name = TURTLE_NAMES[i] if i < len(TURTLE_NAMES) else f"#{i}"
        marker = "  <-- winner" if i == winner_index else ""
        print(f"  {i:>4}  {name:<14} {distance:>10.1f}  {lane_lengths[i]:>11.1f}  {fraction*100:>6.1f}%{marker}")
    print()

    return winning_turtle


def announce_result(winner, user_bet, turtles_list):
    _screen.tracer(0)
    if winner.pencolor() == turtles_list[user_bet - 1]['o'].pencolor():
        print(f"You won! The {winner.pencolor()} 🐢 is the winner!")
        text, color, size = "YOU WIN!", "gold", 72
    else:
        print(f"You lose. The {winner.pencolor()} 🐢 is the winner.")
        text, color, size = "SORRY, BRUH!", "tomato", 32
    writer = Turtle()
    writer.hideturtle()
    writer.penup()
    writer.goto(0, CELEBRATION_Y + 80)
    writer.color(color)
    writer.write(text, align="center", font=("Arial", size, "bold"))
    _screen.update()
    _screen.tracer(1)


def celebrate(winner, won):
    _screen.tracer(0)
    face_color = winner.pencolor()
    pen = Turtle()
    pen.hideturtle()
    pen.penup()
    pen.speed("fastest")
    pen.pensize(3)
    pen.color(face_color)

    R = 60
    cy = CELEBRATION_Y

    # Face outline
    pen.goto(0, cy - R)
    pen.setheading(0)
    pen.pendown()
    pen.circle(R)
    pen.penup()

    # Left eye
    pen.goto(-22, cy + 14)
    pen.pendown()
    pen.begin_fill()
    pen.circle(5)
    pen.end_fill()
    pen.penup()

    # Right eye
    pen.goto(14, cy + 14)
    pen.pendown()
    pen.begin_fill()
    pen.circle(5)
    pen.end_fill()
    pen.penup()

    # Mouth
    pen.pensize(4)
    if won:
        pen.goto(-24, cy - 20)
        pen.setheading(270)
        pen.pendown()
        pen.circle(24, 180)
    else:
        pen.goto(24, cy - 30)
        pen.setheading(90)
        pen.pendown()
        pen.circle(24, 180)
    pen.penup()
    _screen.update()
    _screen.tracer(1)
