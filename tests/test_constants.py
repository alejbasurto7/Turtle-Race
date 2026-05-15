import os
import sys

# Make project root importable when running pytest from any cwd.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE, SNAKE_NAMES, SNAKE_COLORS, SNAKE_LENGTHS, SNAKE_IMAGES, SPECIES


def test_image_map_has_entry_for_every_turtle_name():
    assert set(TURTLE_IMAGES.keys()) == set(TURTLE_NAMES), (
        "TURTLE_IMAGES keys must exactly match TURTLE_NAMES"
    )


def test_image_files_exist_on_disk():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, rel_path in TURTLE_IMAGES.items():
        full = os.path.join(project_root, rel_path)
        assert os.path.isfile(full), f"Missing image for {name}: {full}"


def test_bet_image_size_is_positive_int():
    assert isinstance(BET_IMAGE_SIZE, int)
    assert BET_IMAGE_SIZE > 0


def test_snake_lists_are_length_3():
    assert len(SNAKE_NAMES) == len(SNAKE_COLORS) == len(SNAKE_LENGTHS) == 3


def test_snake_image_map_has_entry_for_every_snake_name():
    assert set(SNAKE_IMAGES.keys()) == set(SNAKE_NAMES), (
        "SNAKE_IMAGES keys must exactly match SNAKE_NAMES"
    )


def test_snake_lengths_positional_values():
    named = dict(zip(SNAKE_NAMES, SNAKE_LENGTHS))
    assert named == {"Shadow": 6, "Ralph": 2, "Anaconda": 5}


def test_snake_image_files_exist_on_disk():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name, rel_path in SNAKE_IMAGES.items():
        full = os.path.join(project_root, rel_path)
        assert os.path.isfile(full), f"Missing image for {name}: {full}"
