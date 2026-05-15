# TURTLE_COLORS = {
#     "Raphael": "red4",
#     "Michaelangelo": "DarkOrange",
#     "Leonardo": "blue",
#     "Donatello": "DarkMagenta",
# }

TURTLE_COLORS = ["red4", "DarkOrange", "blue", "DarkMagenta"]
TURTLE_NAMES = ["Raphael", "Michaelangelo", "Leonardo", "Donatello"]
# WINDOW_WIDTH = 2550
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400
SPACING = 30
TURTLE_LENGTH = 40
TURTLE_HEIGHT = 10
MAX_PACE = 10
TICK_DELAY = 0.01   # seconds between race ticks; tweak for race duration
STARTING_Y = 100
TURTLE_IMAGES = {
    "Raphael":      "assets/turtle_3_raphael_bottom_left.jpg",
    "Michaelangelo": "assets/turtle_4_michelangelo_bottom_right.jpg",
    "Leonardo":     "assets/turtle_1_leonardo_top_left.jpg",
    "Donatello":    "assets/turtle_2_donatello_top_right.jpg",
}
BET_IMAGE_SIZE = 140  # px, square — used by the bet dialog

# --- Snake racer identity ---
SNAKE_NAMES   = ["Shadow", "Ralph", "Anaconda"]
SNAKE_COLORS  = ["black", "#E89F4F", "green"]      # positional with SNAKE_NAMES; Ralph hex per CONTEXT-1.md
SNAKE_LENGTHS = [6, 2, 5]                           # positional with SNAKE_NAMES; 6:5:2 ratio is Shadow:Anaconda:Ralph by value
SNAKE_IMAGES  = {
    "Shadow":   "assets/snakes/Shadow.png",
    "Ralph":    "assets/snakes/Ralph.png",
    "Anaconda": "assets/snakes/Anaconda.png",
}
L_BASE = 1.0   # placeholder — tuned visually in Phase 4

# --- Species config ---
SPECIES = {
    "turtles": {
        "names":        TURTLE_NAMES,
        "colors":       TURTLE_COLORS,
        "images":       TURTLE_IMAGES,
        "bet_layout":   "grid_2x2",
        "shape_drawer": "turtle",
    },
    "snakes": {
        "names":        SNAKE_NAMES,
        "colors":       SNAKE_COLORS,
        "images":       SNAKE_IMAGES,
        "bet_layout":   "row_3",
        "shape_drawer": "snake",
    },
}

# Track layout
TRACK_PADDING = 100       # px gap from screen edge to centerline rect
LANE_SPACING = 24         # px between adjacent lane centers (> default turtle shape size)
SPIRAL_STEP = 4 * LANE_SPACING  # px each spiral lap shrinks (keeps loops visually distinct)
TRACK_PREVIEW_W = 220     # preview image width in track-selection dialog
TRACK_PREVIEW_H = 140     # preview image height in track-selection dialog
