"""Audio diagnostic for the turtle-race music issue.

Runs three independent sound tests, asking Yes/No via a tkinter dialog
after each. Run from the project root with normal Python (NOT pytest):

    python tools/diagnose_audio.py

In PyCharm: right-click -> Run 'diagnose_audio', NOT 'pytest in diagnose_audio'.
"""

import ctypes
import os
import sys
import time
import tkinter
import tkinter.messagebox

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIDI_PATH = os.path.join(PROJECT_ROOT, "assets", "TeenageMutantNinjaTurtles.mid")


def banner(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def ask(question: str) -> bool:
    """Yes/No via tkinter so it works under PyCharm too."""
    root = tkinter.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    answer = tkinter.messagebox.askyesno("Audio diagnostic", question)
    root.destroy()
    return bool(answer)


# Renamed off the "test_" prefix so pytest doesn't auto-collect these.
def check_winsound_beep() -> bool:
    banner("TEST 1: winsound.Beep (system audio)")
    try:
        import winsound
        print("Playing 880 Hz tone for 1 second...")
        winsound.Beep(880, 1000)
    except Exception as e:
        print(f"FAILED: {e}")
        return False
    return ask("TEST 1 (winsound.Beep)\n\nDid you hear an 880 Hz tone?")


def check_direct_midi() -> bool:
    banner("TEST 2: direct MIDI note via winmm.midiOutShortMsg")
    winmm = ctypes.windll.winmm
    handle = ctypes.c_void_p()
    rc = winmm.midiOutOpen(ctypes.byref(handle), 0, 0, 0, 0)
    if rc != 0:
        print(f"midiOutOpen failed: {rc}")
        return False
    # Program change to a brass lead (instrument 56) on channel 0.
    winmm.midiOutShortMsg(handle, 0xC0 | (56 << 8))
    # Note on: C5 (72), velocity 110.
    winmm.midiOutShortMsg(handle, 0x90 | (72 << 8) | (110 << 16))
    print("Sending MIDI note (C5)... holding for 1.5 seconds.")
    time.sleep(1.5)
    winmm.midiOutShortMsg(handle, 0x80 | (72 << 8) | (0 << 16))
    winmm.midiOutClose(handle)
    return ask("TEST 2 (direct MIDI via winmm)\n\nDid you hear the MIDI note?")


def check_pygame_midi() -> bool:
    banner("TEST 3: pygame.mixer.music with the project's MIDI file")
    import pygame
    try:
        pygame.mixer.init()
        print("mixer init:", pygame.mixer.get_init())
        pygame.mixer.music.load(MIDI_PATH)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(loops=0)
        print("Playing for 3 seconds...")
        for _ in range(6):
            time.sleep(0.5)
            print(f"  busy={pygame.mixer.music.get_busy()}", end="\r")
        print()
        pygame.mixer.music.stop()
    except Exception as e:
        print(f"FAILED: {e}")
        return False
    return ask("TEST 3 (pygame.mixer.music)\n\nDid you hear the TMNT theme?")


def main() -> None:
    print(f"Project root: {PROJECT_ROOT}")
    print(f"MIDI file exists: {os.path.exists(MIDI_PATH)}")
    print(f"Python: {sys.version.split()[0]}  Platform: {sys.platform}")

    results = {
        "1. winsound.Beep (system audio)": check_winsound_beep(),
        "2. direct MIDI note (GS Wavetable Synth)": check_direct_midi(),
        "3. pygame.mixer.music with .mid file": check_pygame_midi(),
    }

    banner("RESULTS")
    for name, ok in results.items():
        print(f"  {'OK ' if ok else 'NO '}  {name}")
    print()
    print("Share this table -- it pinpoints which audio path is broken.")

    tkinter.messagebox.showinfo(
        "Audio diagnostic results",
        "\n".join(f"{'OK ' if ok else 'NO '}  {name}" for name, ok in results.items()),
    )


if __name__ == "__main__":
    main()
