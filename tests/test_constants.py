import os
import sys

# Make project root importable when running pytest from any cwd.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import TURTLE_NAMES, TURTLE_IMAGES, BET_IMAGE_SIZE


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
