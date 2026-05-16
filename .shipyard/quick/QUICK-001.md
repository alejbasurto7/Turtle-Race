# Quick Task 001: Shuffled MIDI playlist soundtrack

**Requested:** 2026-05-16
**Description:** Replace the single hard-coded background MIDI with a shuffled playlist drawn from `assets/midi/`. Tracks play one after another and loop forever (reshuffled on each pass).

## Plan
1. Rewrite [audio.py](../../audio.py): build playlist via `glob('assets/midi/*.mid')`, shuffle it, drive playback from a daemon thread that polls `pygame.mixer.music.get_busy()` and advances to the next track when it ends (reshuffling on wrap).
2. Update [main.py](../../main.py) call site: drop the file-path argument so `start_background_music()` uses the default `"assets/midi"` directory.
3. Update [turtle_race.spec](../../turtle_race.spec) `datas=` to bundle `assets/midi/*.mid` into the frozen build.

## Files
- audio.py: rewrite (playlist + thread)
- main.py: change one call
- turtle_race.spec: add one datas tuple

## Verification
- `python -c "import audio; print(len(audio._build_playlist('assets/midi')))"` → 9
- `pytest -q` → 85 passed
- Manual smoke test: `python main.py` plays a MIDI, advances to a different one when it ends.

## Result
**Status:** complete
**Files Modified:**
- audio.py: replaced single-track loader with shuffled-playlist daemon thread
- main.py: `start_background_music()` now called with no args (defaults to `assets/midi`)
- turtle_race.spec: added `('assets/midi/*.mid', 'assets/midi')` to bundle MIDI playlist
**Notes:** Threaded poller chosen over `pygame.mixer.music.set_endevent()` because the Tk-based app has no pygame event pump. The daemon thread exits cleanly when `stop_background_music()` flips `_state["running"]` to False. Playlist reshuffles each time the index wraps, so the "loop" is not a fixed order.
**Completed:** 2026-05-16
