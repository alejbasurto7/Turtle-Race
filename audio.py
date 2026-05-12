import pygame

from paths import resource_path


def start_background_music(midi_rel_path):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(resource_path(midi_rel_path))
        pygame.mixer.music.play(loops=-1)
    except Exception as e:
        print(f"Could not start background music: {e}")


def stop_background_music():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass
