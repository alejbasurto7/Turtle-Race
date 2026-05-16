"""Side-by-side renderer for candidate snake polygon designs.

Run from the project root:

    python tools/snake_shape_options.py

A wide turtle window opens showing five candidate snake shapes labeled
1-5, each rendered at three lengths (Shadow=6, Anaconda=5, Ralph=2)
to show how the polygon scales with length_units. Pick the option you
prefer and tell Claude which number.

Click anywhere on the window to close it.

This iteration: per user reference image (a horizontal classic-snake
silhouette with sharp triangular zigzag body and tapered tail), all
options here are zigzag variants of varying intensity.
"""

import turtle


# ---------------------------------------------------------------------------
# Five candidate polygons. All defined head-at-+y / tail-at--y so they
# rotate to point East at heading=0 (matching the in-race convention).
#
# Zigzag construction: right peaks at one set of y values, left peaks at
# y values OFFSET from right peaks. As you trace the body top-to-bottom,
# the centerline shifts right/left alternately — producing a zigzag
# silhouette while keeping body thickness roughly uniform.
# ---------------------------------------------------------------------------

# Option 1 — MEDIUM ZIGZAG (closely matches user reference image)
# Body amplitude ±5, 3 peaks per side, length 19.
OPT1_MEDIUM = (
    # Head + right edge top→bottom
    ( 0, 12),     # head apex
    ( 3, 11),     # head right
    ( 3,  9),     # jaw right
    ( 5,  7),     # R PEAK 1
    ( 2,  5),     # R valley
    ( 5,  3),     # R PEAK 2
    ( 2,  1),     # R valley
    ( 5, -1),     # R PEAK 3
    ( 2, -3),     # R valley
    ( 2, -5),     # tail right
    ( 0, -7),     # tail tip
    # Left edge bottom→top
    (-2, -5),     # tail left
    (-5, -3),     # L PEAK (offset from R peaks)
    (-2, -1),     # L valley
    (-5,  1),     # L PEAK
    (-2,  3),     # L valley
    (-5,  5),     # L PEAK
    (-2,  7),     # L valley
    (-3,  9),     # jaw left
    (-3, 11),     # head left
)
OPT1_LEN = 19

# Option 2 — GENTLE ZIGZAG (smaller amplitude, more subtle wiggle)
# Body amplitude ±3, 3 peaks per side, length 19.
OPT2_GENTLE = (
    ( 0, 12),
    ( 2, 11),
    ( 2,  9),
    ( 3,  7),     # mild R PEAK
    ( 1,  5),
    ( 3,  3),
    ( 1,  1),
    ( 3, -1),
    ( 1, -3),
    ( 1, -5),
    ( 0, -7),
    (-1, -5),
    (-3, -3),     # mild L PEAK
    (-1, -1),
    (-3,  1),
    (-1,  3),
    (-3,  5),
    (-1,  7),
    (-2,  9),
    (-2, 11),
)
OPT2_LEN = 19

# Option 3 — AGGRESSIVE ZIGZAG (large amplitude, sharp peaks, longest)
# Body amplitude ±7, 4 peaks per side, length 23.
OPT3_AGGRESSIVE = (
    ( 0, 14),
    ( 3, 13),
    ( 3, 11),
    ( 7,  9),     # BIG R PEAK 1
    ( 1,  7),
    ( 7,  5),     # BIG R PEAK 2
    ( 1,  3),
    ( 7,  1),     # BIG R PEAK 3
    ( 1, -1),
    ( 7, -3),     # BIG R PEAK 4
    ( 1, -5),
    ( 1, -7),
    ( 0, -9),
    (-1, -7),
    (-1, -5),
    (-7, -3),     # BIG L PEAK (between R peaks)
    (-1, -1),
    (-7,  1),
    (-1,  3),
    (-7,  5),
    (-1,  7),
    (-7,  9),
    (-1, 11),
    (-3, 11),
    (-3, 13),
)
OPT3_LEN = 23

# Option 4 — PIXELATED ZIGZAG (right-angle stair-steps, true 8-bit Nokia look)
# Each peak is a rectangular block, no diagonals. Length 18.
OPT4_PIXEL_ZIGZAG = (
    ( 0, 10),
    ( 2, 10),
    ( 2,  8),
    ( 4,  8),     # R block 1
    ( 4,  6),
    ( 2,  6),
    ( 2,  4),
    ( 4,  4),     # R block 2
    ( 4,  2),
    ( 2,  2),
    ( 2,  0),
    ( 4,  0),     # R block 3
    ( 4, -2),
    ( 2, -2),
    ( 2, -4),
    ( 1, -4),
    ( 1, -6),
    ( 0, -6),
    ( 0, -8),
    (-1, -8),
    (-1, -6),
    (-2, -6),
    (-2, -4),
    (-4, -4),     # L block 3 (offset from R)
    (-4, -2),
    (-2, -2),
    (-2,  0),
    (-4,  0),     # L block 2
    (-4,  2),
    (-2,  2),
    (-2,  4),
    (-4,  4),     # L block 1
    (-4,  6),
    (-2,  6),
    (-2,  8),
    (-2, 10),
)
OPT4_LEN = 18

# Option 5 — SMOOTH WAVE (true centerline-shift body, sinusoidal feel)
# Body is a constant-width strip whose centerline snakes left-right.
# Length 20.
OPT5_SMOOTH_WAVE = (
    # Head
    ( 0, 12),
    ( 3, 11),
    ( 3,  9),
    # Right edge — centerline alternates +2/-2 → body strip slants L-R-L-R
    ( 4,  7),     # R at y=7  (centerline+2 → x=4)
    ( 0,  4),     # R at y=4  (centerline-2 → x=0)
    ( 4,  1),     # R at y=1  (centerline+2)
    ( 0, -2),     # R at y=-2 (centerline-2)
    ( 4, -5),     # R at y=-5 (centerline+2)
    ( 1, -7),     # tail right
    ( 0, -8),     # tail tip
    # Left edge (mirror)
    (-1, -7),
    ( 0, -5),     # L at y=-5 (centerline+2 → x=0)
    (-4, -2),     # L at y=-2 (centerline-2 → x=-4)
    ( 0,  1),     # L at y=1
    (-4,  4),     # L at y=4
    ( 0,  7),     # L at y=7
    (-3,  9),     # jaw left
    (-3, 11),     # head left
)
OPT5_LEN = 20


OPTIONS = [
    ("1. Medium zigzag (REF1)",  OPT1_MEDIUM,        OPT1_LEN),
    ("2. Gentle zigzag",         OPT2_GENTLE,        OPT2_LEN),
    ("3. Aggressive zigzag",     OPT3_AGGRESSIVE,    OPT3_LEN),
    ("4. Pixelated zigzag",      OPT4_PIXEL_ZIGZAG,  OPT4_LEN),
    ("5. Smooth wave (REF2)",    OPT5_SMOOTH_WAVE,   OPT5_LEN),
]


# Three sizes representing Shadow / Anaconda / Ralph at L_BASE = 1.2
LENGTHS = [
    ("Shadow",   6, "black"),
    ("Anaconda", 5, "green"),
    ("Ralph",    2, "#E89F4F"),
]
L_BASE = 1.2
STRETCH_WID = 0.5


def render():
    screen = turtle.Screen()
    screen.setup(width=1500, height=900)
    screen.title("Snake polygon options — pick a number, click to close")
    screen.bgcolor("#bce896")
    screen.tracer(0)

    # Title
    title = turtle.Turtle()
    title.hideturtle()
    title.penup()
    title.goto(0, 400)
    title.color("black")
    title.write(
        "Snake polygon candidates (zigzag variants) — same race-time scale (L_BASE=1.2) — pick by number",
        align="center",
        font=("Arial", 14, "bold"),
    )

    col_w = 1500 // 6
    col_xs = [-2 * col_w, -col_w, 0, col_w, 2 * col_w]
    row_ys = [220, 0, -200]

    for col_idx, (label, polygon, _poly_len) in enumerate(OPTIONS):
        cx = col_xs[col_idx]
        shape_name = f"snake_opt_{col_idx + 1}"
        screen.register_shape(shape_name, polygon)

        header = turtle.Turtle()
        header.hideturtle()
        header.penup()
        header.goto(cx, 320)
        header.color("black")
        header.write(label, align="center", font=("Arial", 11, "bold"))

        for row_idx, (snake_name, length_units, color) in enumerate(LENGTHS):
            cy = row_ys[row_idx]
            t = turtle.Turtle()
            t.hideturtle()
            t.penup()
            t.shape(shape_name)
            t.color(color)
            t.shapesize(stretch_wid=STRETCH_WID, stretch_len=L_BASE * length_units)
            t.setheading(0)
            t.goto(cx, cy)
            t.showturtle()

            if col_idx == 0:
                row_label = turtle.Turtle()
                row_label.hideturtle()
                row_label.penup()
                row_label.goto(-740, cy - 12)
                row_label.color("black")
                row_label.write(
                    f"{snake_name}\n(len={length_units})",
                    align="left",
                    font=("Arial", 10, "bold"),
                )

    screen.update()
    screen.exitonclick()


if __name__ == "__main__":
    render()
