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


def test_species_has_required_top_level_keys():
    assert set(SPECIES.keys()) == {"turtles", "snakes"}


def test_species_entries_have_required_sub_keys():
    required = {"names", "colors", "images", "bet_layout", "shape_drawer"}
    for s in SPECIES:
        assert required <= set(SPECIES[s].keys()), (
            f"SPECIES['{s}'] is missing required sub-keys"
        )


def test_species_bet_layout_values_are_valid():
    valid = {"grid_2x2", "row_3"}
    for s in SPECIES:
        assert SPECIES[s]["bet_layout"] in valid, (
            f"SPECIES['{s}']['bet_layout'] must be one of {valid}"
        )


def test_species_racer_counts():
    assert len(SPECIES["turtles"]["names"]) == 4
    assert len(SPECIES["snakes"]["names"]) == 3


def test_species_shape_drawer_is_string_sentinel():
    valid = {"turtle", "snake"}
    for s in SPECIES:
        assert isinstance(SPECIES[s]["shape_drawer"], str), (
            f"SPECIES['{s}']['shape_drawer'] must be a str"
        )
        assert SPECIES[s]["shape_drawer"] in valid, (
            f"SPECIES['{s}']['shape_drawer'] must be one of {valid}"
        )
