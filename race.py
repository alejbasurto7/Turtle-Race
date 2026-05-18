import math
import random
import time
from turtle import Turtle, Screen

from PIL import Image, ImageTk

import tracks
from constants import MAX_PACE, TICK_DELAY, TRACK_PADDING, SPECIES, L_BASE, SNAKE_STRETCH_WID, SNAKE_LENGTHS
from paths import resource_path


_screen = None

CELEBRATION_Y = 180  # vertical offset so face/text aren't hidden by the centered "play again?" dialog

STONE_COLOR = "gray30"
STONE_DIAMETER = 3

# Finish-line checker tile size (px). Chosen to divide LANE_SPACING evenly so
# adjacent per-lane bars on the STRAIGHT track tile into one continuous pattern.
FINISH_CHECKER_SIZE = 6
FINISH_CHECKER_ROWS = 2

# Canvas tag for podium medal items; raised after any _screen.update() so they
# stay on top of the turtle sprites (which turtle.py keeps tag_raising).
PODIUM_MEDAL_TAG = "podium_medal"


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
    img = Image.open(resource_path("assets/lawn.jpg"))
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
    pen.color("white")
    pen.pensize(3)
    pen.goto(*p0)
    pen.pendown()
    pen.goto(*p1)
    pen.penup()


def draw_start_line(track_name, n):
    _screen.tracer(0)
    for p0, p1 in tracks.start_line_segments(track_name, n):
        _draw_segment(p0, p1)
    _screen.update()
    _screen.tracer(1)


def draw_boundary_stones(track_name, n):
    _screen.tracer(0)
    pen = Turtle()
    pen.hideturtle()
    pen.penup()
    pen.color(STONE_COLOR)
    for x, y in tracks.boundary_stones(track_name, n):
        pen.goto(x, y)
        pen.dot(STONE_DIAMETER, STONE_COLOR)
    _screen.update()
    _screen.tracer(1)


def _draw_checkered_bar(p0, p1):
    """Tile black/white squares along segment p0->p1, centered perpendicular to it."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length    # unit vector along segment
    px, py = -uy, ux                     # perpendicular (left of direction)
    n_cols = max(1, int(round(length / FINISH_CHECKER_SIZE)))
    size = length / n_cols
    half_rows = FINISH_CHECKER_ROWS / 2
    canvas = _screen.getcanvas()
    for row in range(FINISH_CHECKER_ROWS):
        for col in range(n_cols):
            base_x = x0 + ux * col * size + px * (row - half_rows) * size
            base_y = y0 + uy * col * size + py * (row - half_rows) * size
            color = "black" if (row + col) % 2 == 0 else "white"
            c1x, c1y = base_x + ux * size, base_y + uy * size
            c2x, c2y = c1x + px * size, c1y + py * size
            c3x, c3y = base_x + px * size, base_y + py * size
            # Tk canvas y is inverted relative to turtle coords.
            canvas.create_polygon(
                base_x, -base_y, c1x, -c1y, c2x, -c2y, c3x, -c3y,
                fill=color, outline=color,
            )


def draw_finish_line(track_name, n):
    _screen.tracer(0)
    for p0, p1 in tracks.finish_line_segments(track_name, n):
        _draw_checkered_bar(p0, p1)
    _screen.update()
    _screen.tracer(1)


def draw_turtle_shape(t):
    """Apply the turtle shape to a Turtle object.

    Color is intentionally not applied here; it is set later in
    place_racers_on_track so both species follow the same placement path.
    """
    t.shape("turtle")


# Custom snake polygon — smooth-wave silhouette (Option 5 from
# tools/snake_shape_options.py). Constant-width body strip whose
# centerline shifts +2/-2 in x at alternating y levels, producing a
# sinusoidal-feeling zigzag without sharp triangular peaks.
# Head at +y (apex), tail at -y. Length 20 along heading, max width 4.
_SNAKE_POLYGON = (
    # Head
    ( 0, 12),     # head apex
    ( 3, 11),     # head right
    ( 3,  9),     # jaw right
    # Right edge — centerline alternates +2/-2 → body strip slants L-R-L-R
    ( 4,  7),     # R at y=7  (centerline+2)
    ( 0,  4),     # R at y=4  (centerline-2)
    ( 4,  1),     # R at y=1  (centerline+2)
    ( 0, -2),     # R at y=-2 (centerline-2)
    ( 4, -5),     # R at y=-5 (centerline+2)
    ( 1, -7),     # tail right
    ( 0, -8),     # tail tip
    # Left edge (mirror)
    (-1, -7),
    ( 0, -5),     # L at y=-5
    (-4, -2),     # L at y=-2
    ( 0,  1),     # L at y=1
    (-4,  4),     # L at y=4
    ( 0,  7),     # L at y=7
    (-3,  9),     # jaw left
    (-3, 11),     # head left
)
_SNAKE_POLYGON_LENGTH = 20   # length axis of _SNAKE_POLYGON (12 - (-8))
_snake_shape_registered = False


def draw_snake_shape(t, length_units):
    """Apply a custom snake polygon shape to a Turtle, scaled per length_units.

    Registers the ``snake`` shape lazily on first call (it persists across
    screen.clear() so we only register once per process). Then sets:
    - ``stretch_wid = SNAKE_STRETCH_WID`` (body thickness)
    - ``stretch_len = L_BASE * length_units`` (body length proportional to
      each snake's SNAKE_LENGTHS entry)

    Produces visually distinct lengths: Shadow (6) > Anaconda (5) > Ralph (2),
    at a 6:5:2 ratio. At L_BASE=1.2 and the polygon's 20-unit length axis,
    Shadow ≈ 144 px along heading, Anaconda ≈ 120 px, Ralph ≈ 48 px.
    """
    global _snake_shape_registered
    if not _snake_shape_registered:
        _screen.register_shape("snake", _SNAKE_POLYGON)
        _snake_shape_registered = True
    t.shape("snake")
    t.shapesize(stretch_wid=SNAKE_STRETCH_WID, stretch_len=L_BASE * length_units)


# Per-shape "natural length" along heading axis, used by run_race's
# head-position finish detection. The classic and turtle shapes are ~9 units
# (turtle is approximate but symmetric race outcome makes it harmless); the
# custom snake polygon length is _SNAKE_POLYGON_LENGTH (= 20).
_SHAPE_UNIT_SIZE = {
    "turtle": 9,
    "classic": 9,
    "snake":  _SNAKE_POLYGON_LENGTH,
}

# Resolves the string sentinel in SPECIES[species]["shape_drawer"] to a
# callable. Keyed by the same string values used in constants.SPECIES.
def _head_offset_arc_for(t):
    """Visual head-offset (px along heading) for a racer with shape t.shape()."""
    shape_name = t.shape()
    unit_size = _SHAPE_UNIT_SIZE.get(shape_name, 9)
    stretch_len = t.shapesize()[1]
    return unit_size * stretch_len / 2


def _back_pos(x, y, heading_deg, distance):
    """Return (x, y) shifted backwards by `distance` along the heading.

    Used to place a racer's CENTER behind a target point so its HEAD
    (which extends head_offset_arc forward along heading) sits at the
    target. Keeps long snakes from straddling the start/finish line.
    """
    rad = math.radians(heading_deg)
    return x - distance * math.cos(rad), y - distance * math.sin(rad)


_SHAPE_DRAWERS = {
    "turtle": draw_turtle_shape,
    "snake":  draw_snake_shape,
}


def create_racers(species: str):
    """Create the field of racers for the given species.

    Args:
        species: A key into constants.SPECIES (currently ``"turtles"`` or
            ``"snakes"``).  Raises ``KeyError`` on an unrecognised value.

    Returns:
        A list of racer dicts ordered by ``SPECIES[species]["names"]``. Each
        dict has:

        - ``'name'``:  str — the racer's name (matches
          ``SPECIES[species]["names"][i]``).
        - ``'color'``: str — pen/fill color (matches
          ``SPECIES[species]["colors"][i]``).
        - ``'o'``:     turtle.Turtle — the underlying turtle object.

    Note:
        For ``"snakes"``, the drawer receives ``SNAKE_LENGTHS[i]`` as a
        ``length_units`` argument so each snake's stretch_len scales with
        its species-defined length (Shadow=6, Ralph=2, Anaconda=5).
        For ``"turtles"``, the drawer takes no extra argument.
    """
    data = SPECIES[species]
    drawer = _SHAPE_DRAWERS[data["shape_drawer"]]
    racers = []
    for i, (name, color) in enumerate(zip(data["names"], data["colors"])):
        t = Turtle()
        if species == "snakes":
            drawer(t, SNAKE_LENGTHS[i])
        else:
            drawer(t)
        racers.append({'name': name, 'color': color, 'o': t})
    return racers


def place_racers_on_track(racers, track_name):
    n = len(racers)
    _screen.tracer(0)
    for i, racer in enumerate(racers):
        x, y, heading = tracks.lane_start_pose(track_name, i, n)
        racer['o'].hideturtle()
        racer['o'].color(racer['color'])
        racer['o'].penup()
        racer['o'].setheading(heading)
        # Place the CENTER behind the start line by head_offset so the
        # racer's HEAD sits at the lane start position. Without this,
        # long snakes straddle the start line (half their body behind).
        head_off = _head_offset_arc_for(racer['o'])
        back_x, back_y = _back_pos(x, y, heading, head_off)
        racer['o'].goto(back_x, back_y)
        racer['o'].showturtle()
    _screen.update()
    _screen.tracer(1)


def run_race(racers, track_name, user_bet):
    """Race loop. All lanes advance the same expected `s` per tick, then
    each racer's visual position is computed at `(s / shared_distance)`
    of its own path length. This keeps the race fair regardless of which
    lane has the longer perimeter.

    `shared_distance` is the midpoint between the straight-track length
    (preserves the original per-tick pace on straight) and the average lane
    length of the current track (caps how slow long tracks like spiral get),
    scaled by 1/SPEED_FACTOR so the per-tick visual movement lands at the
    target fraction of the natural pace.
    """
    SPEED_FACTOR = 0.3                       # 30% of the naive pace; tweak to taste
    n = len(racers)
    lane_paths = tracks.build_lane_paths(track_name, n)
    lane_lengths = [tracks.path_length(p) for p in lane_paths]
    straight_length = _screen.window_width() - 2 * TRACK_PADDING
    avg_lane_length = sum(lane_lengths) / len(lane_lengths)
    shared_distance = ((straight_length + avg_lane_length) / 2) / SPEED_FACTOR
    progress = [0.0] * len(racers)

    # Universal head-position finish detection (CONTEXT-4.md Decision 3).
    # Both species use the same formula: the finish line is reached when the
    # racer's HEAD crosses the goal, not its center.  Because turtles are
    # symmetric (all four share the same stretch_len = 1.0), applying the
    # same head-offset to all turtles leaves their relative race outcome
    # unchanged — it only shifts all four finish at the same earlier threshold.
    # Snakes get the real fairness benefit: longer snakes (Shadow) no longer
    # gain extra progress because their center is still behind the line.
    #
    # Formula (RESEARCH.md §2 Approach B):
    #   head_offset_arc      = shape_unit_size * stretch_len / 2
    #   head_offset_progress = head_offset_arc * (shared_distance / lane_length)
    #   finish condition     : progress[i] >= shared_distance - head_offset_progress[i]
    #
    # shape_unit_size: the polygon's natural length along the heading axis.
    # 9 for classic/turtle, 18 for the custom snake polygon — looked up in the
    # module-level _SHAPE_UNIT_SIZE dict by shape name. Turtle uses 9 as an
    # approximation (the turtle polygon is smaller) but the race outcome is
    # symmetric so this is harmless — see CRITIQUE.md.
    #
    # Clamp stays at shared_distance (not the finish threshold) because
    # coast_remaining[i] is set the moment the finish check fires, and the
    # loop uses ``coast_remaining[i] is None`` to decide which branch to enter
    # rather than comparing progress against shared_distance directly.
    # This is simpler than lowering the clamp and avoids off-by-one edge cases.
    head_offset_arc = []
    head_offset_progress = []
    for i in range(len(racers)):
        arc_off = _head_offset_arc_for(racers[i]['o'])
        head_offset_arc.append(arc_off)
        head_offset_progress.append(arc_off * (shared_distance / lane_lengths[i]))

    print(f"\n=== Race start: {track_name} ===")
    print(f"  shared_distance (progress target, equal for all lanes): {shared_distance:.1f}")
    print(f"  {'lane':>4}  {'name':<14} {'color':<12} {'start (x, y)':<22} {'lane_length':>11}  {'head_off_prog':>13}")
    for i, racer in enumerate(racers):
        x0, y0 = lane_paths[i]["start"]
        # Use the configured color string (e.g. "#E89F4F") rather than
        # racer['o'].pencolor() — turtle module normalizes hex strings to
        # (r, g, b) tuples on round-trip, which break the `{color:<12}` format spec.
        name = racer['name']
        color = racer['color']
        print(f"  {i:>4}  {name:<14} {color:<12} ({x0:>7.1f}, {y0:>7.1f})    {lane_lengths[i]:>11.1f}  {head_offset_progress[i]:>13.2f}")

    COAST_TICKS = 30                             # extra ticks racers run past the finish line
    winning_turtle = None
    finish_order = []                            # lane indices in order of crossing the line
    ticks = 0
    finish_ticks = [None] * len(racers)          # tick number each lane finished on
    coast_remaining = [None] * len(racers)       # ticks left in the post-finish coast phase
    done = [False] * len(racers)
    _screen.tracer(0)
    while not all(done):
        for i, turtle in enumerate(racers):
            if done[i]:
                continue
            step = random.randint(0, MAX_PACE)
            if coast_remaining[i] is None:
                # Still racing — advance progress and check the head-position
                # finish threshold.  Clamp at shared_distance so fraction stays
                # in [0, 1]; the finish check uses the adjusted threshold below.
                progress[i] = min(progress[i] + step, shared_distance)
                fraction = progress[i] / shared_distance
                arc = fraction * lane_lengths[i]
                x, y, heading = tracks.position_at_arc(lane_paths[i], arc)
                # Back the visual up by head_offset_arc so the HEAD tracks
                # the lane arc position (matches the head-position finish check).
                back_x, back_y = _back_pos(x, y, heading, head_offset_arc[i])
                turtle['o'].setheading(heading)
                turtle['o'].goto(back_x, back_y)
                # Head-position finish: the racer's head crosses the line when
                # progress reaches shared_distance - head_offset_progress[i].
                # For turtles this is ~4.5 progress units earlier than center;
                # for Shadow (longest snake) it is ~16 units earlier.
                if progress[i] >= shared_distance - head_offset_progress[i]:
                    finish_order.append(i)
                    finish_ticks[i] = ticks + 1
                    if winning_turtle is None:
                        winning_turtle = turtle['o']
                    coast_remaining[i] = COAST_TICKS
            else:
                # Coasting past the finish at the same visual pace they had on track.
                visual_step = step * (lane_lengths[i] / shared_distance)
                turtle['o'].forward(visual_step)
                coast_remaining[i] -= 1
                if coast_remaining[i] <= 0:
                    done[i] = True
        ticks += 1
        _screen.update()
        time.sleep(TICK_DELAY)
    _screen.tracer(1)

    place_labels = ["1st", "2nd", "3rd", "4th"]
    print(f"--- Race end after {ticks} ticks ---")
    print(f"  {'place':<5}  {'lane':>4}  {'name':<14} {'distance':>10}  {'lane_length':>11}  {'finish_tick':>11}")
    for place, lane_idx in enumerate(finish_order):
        distance = (progress[lane_idx] / shared_distance) * lane_lengths[lane_idx]
        name = racers[lane_idx]['name']
        label = place_labels[place] if place < len(place_labels) else f"{place+1}th"
        print(f"  {label:<5}  {lane_idx:>4}  {name:<14} {distance:>10.1f}  {lane_lengths[lane_idx]:>11.1f}  {finish_ticks[lane_idx]:>11}")
    print()

    return winning_turtle, finish_order


def show_podium(racers, finish_order):
    """Stage the top-3 racers on a 2-1-3 podium with gold/silver/bronze medals.

    Hides all race racers, then re-shows the top three at larger scale on
    podium platforms. Drawn over the race scene so the existing background and
    finish-line graphics stay visible behind the podium blocks.
    """
    if len(finish_order) < 3:
        return

    _screen.tracer(0)
    for racer in racers:
        racer['o'].hideturtle()

    PODIUM_W = 110
    PODIUM_HEIGHTS = {1: 140, 2: 100, 3: 70}
    # Platforms sit edge-to-edge (cx spacing == PODIUM_W) so they read as one
    # connected podium rather than three separate blocks.
    PODIUM_X = {2: -PODIUM_W, 1: 0, 3: PODIUM_W}  # left-to-right: 2, 1, 3
    # Pushed well below center so the "play again?" messagebox (which is
    # centered on the Tk root) doesn't cover the podium / medals.
    PODIUM_BASE_Y = -320
    MEDAL_COLORS = {1: "gold", 2: "silver", 3: "#cd7f32"}

    pen = Turtle()
    pen.hideturtle()
    pen.penup()
    pen.speed("fastest")

    # Pass 1: podium platforms + place numbers.
    for place in (2, 1, 3):
        cx = PODIUM_X[place]
        h = PODIUM_HEIGHTS[place]
        top_y = PODIUM_BASE_Y + h
        left = cx - PODIUM_W / 2
        right = cx + PODIUM_W / 2

        pen.color("black", "white")
        pen.goto(left, PODIUM_BASE_Y)
        pen.setheading(0)
        pen.pendown()
        pen.begin_fill()
        pen.goto(right, PODIUM_BASE_Y)
        pen.goto(right, top_y)
        pen.goto(left, top_y)
        pen.goto(left, PODIUM_BASE_Y)
        pen.end_fill()
        pen.penup()

        pen.color("black")
        pen.goto(cx, PODIUM_BASE_Y + h / 2 - 24)
        pen.write(str(place), align="center", font=("Arial", 28, "bold"))

    # Pass 2: place the winning racers on top of the platforms, then *stamp*
    # them and hide the live turtle. The stamp is a static canvas item that
    # turtle.py never re-raises on subsequent updates — unlike the live turtle
    # sprite, which RawTurtle._drawturtle calls tag_raise on every update
    # (top=True). This lets medals drawn afterward stay on top reliably.
    for place in (1, 2, 3):
        lane_idx = finish_order[place - 1]
        cx = PODIUM_X[place]
        top_y = PODIUM_BASE_Y + PODIUM_HEIGHTS[place]
        turtle = racers[lane_idx]['o']
        turtle.setheading(90)
        # Snakes preserve race-time stretch_len so the 6:5:2 length ratio
        # survives on the podium; width is bumped to 3.0 for visibility.
        # Snake center is positioned so the snake STANDS on the platform top
        # (snake's bottom edge sits at top_y).
        # Turtles get the original uniform 3.0×3.0 enlargement, centered above
        # the platform.
        if turtle.shape() == "snake":
            _, current_stretch_len, _ = turtle.shapesize()
            turtle.shapesize(stretch_wid=3.0, stretch_len=current_stretch_len, outline=2)
            snake_visible_length = current_stretch_len * _SNAKE_POLYGON_LENGTH
            turtle.goto(cx, top_y + snake_visible_length / 2)
        else:
            turtle.shapesize(stretch_wid=3.0, stretch_len=3.0, outline=2)
            turtle.goto(cx, top_y + 30)
        turtle.showturtle()
        turtle.stamp()
        turtle.hideturtle()

    # Flush: makes every hidden turtle's _drawturtle run once and set
    # _hidden_from_screen=True, so no live turtle items get tag_raised by
    # subsequent _screen.update() calls (in celebrate / announce_result).
    _screen.update()

    # Pass 3: medals drawn directly to the Tk canvas. Now that all live turtle
    # sprites are hidden, these stay on top without further tag-raising games.
    canvas = _screen.getcanvas()

    def t2c(tx, ty):  # turtle coords -> tk canvas coords (origin centered, y inverted)
        return tx, -ty

    for place in (1, 2, 3):
        cx = PODIUM_X[place]
        top_y = PODIUM_BASE_Y + PODIUM_HEIGHTS[place]
        medal_color = MEDAL_COLORS[place]

        disc_r = 18
        # Disc sits on the turtle's chest, just below center.
        disc_cx, disc_cy = t2c(cx, top_y + 18)
        # Ribbon goes from above the turtle's head down to the disc.
        rib_top_x_l, rib_top_y = t2c(cx - 10, top_y + 58)
        rib_top_x_r, _ = t2c(cx + 10, top_y + 58)

        canvas.create_line(
            rib_top_x_l, rib_top_y, disc_cx - 5, disc_cy - disc_r + 3,
            fill=medal_color, width=4, tags=PODIUM_MEDAL_TAG,
        )
        canvas.create_line(
            rib_top_x_r, rib_top_y, disc_cx + 5, disc_cy - disc_r + 3,
            fill=medal_color, width=4, tags=PODIUM_MEDAL_TAG,
        )
        canvas.create_oval(
            disc_cx - disc_r, disc_cy - disc_r,
            disc_cx + disc_r, disc_cy + disc_r,
            fill=medal_color, outline="black", width=2,
            tags=PODIUM_MEDAL_TAG,
        )

    canvas.tag_raise(PODIUM_MEDAL_TAG)
    canvas.update_idletasks()
    _screen.tracer(1)


def announce_result(winner, user_bet, racers):
    _screen.tracer(0)
    winner_racer = next(r for r in racers if r['o'] is winner)
    won = winner_racer['o'] is racers[user_bet - 1]['o']
    color_display = winner_racer['color']   # configured string (e.g. "#E89F4F"), never a float tuple
    name = winner_racer['name']
    if won:
        print(f"You won! {name} ({color_display}) is the winner!")
        text, color, size = "YOU WIN!", "gold", 72
    else:
        print(f"You lose. {name} ({color_display}) is the winner.")
        text, color, size = "SORRY, BRUH!", "tomato", 32
    writer = Turtle()
    writer.hideturtle()
    writer.penup()
    writer.goto(0, CELEBRATION_Y + 80)
    writer.color(color)
    writer.write(text, align="center", font=("Arial", size, "bold"))
    _screen.update()
    _screen.getcanvas().tag_raise(PODIUM_MEDAL_TAG)
    _screen.tracer(1)


def celebrate(winner, won, racers):
    _screen.tracer(0)
    winner_racer = next(r for r in racers if r['o'] is winner)
    face_color = winner_racer['color']   # configured string — turtle.color() accepts hex strings equally
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
    # update() re-raises every turtle sprite (RawTurtle._drawturtle passes
    # top=True), pushing the podium medals behind the winners' chests. Lift
    # the medals back to the top now that the last update is done.
    _screen.getcanvas().tag_raise(PODIUM_MEDAL_TAG)
    _screen.tracer(1)
