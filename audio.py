import glob
import os
import random
import threading
import time

import pygame

from paths import resource_path


_state = {
    "running": False,
    "thread": None,
    "playlist": [],
    "index": 0,
}


def _build_playlist(midi_dir_rel):
    midi_dir = resource_path(midi_dir_rel)
    files = sorted(glob.glob(os.path.join(midi_dir, "*.mid")))
    random.shuffle(files)
    return files


def _advance():
    _state["index"] += 1
    if _state["index"] >= len(_state["playlist"]):
        random.shuffle(_state["playlist"])
        _state["index"] = 0


def _player_loop():
    while _state["running"]:
        track = _state["playlist"][_state["index"]]
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Could not play {track}: {e}")
            _advance()
            time.sleep(0.5)
            continue
        # Give the mixer a moment to start before polling get_busy().
        time.sleep(0.2)
        while _state["running"] and pygame.mixer.music.get_busy():
            time.sleep(0.3)
        if not _state["running"]:
            break
        _advance()


def start_background_music(midi_dir_rel="assets/midi"):
    try:
        pygame.mixer.init()
        playlist = _build_playlist(midi_dir_rel)
        if not playlist:
            print(f"No MIDI files found in {midi_dir_rel}")
            return
        _state["playlist"] = playlist
        _state["index"] = 0
        _state["running"] = True
        t = threading.Thread(target=_player_loop, daemon=True)
        _state["thread"] = t
        t.start()
    except Exception as e:
        print(f"Could not start background music: {e}")


def stop_background_music():
    _state["running"] = False
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
