import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import audio
import dialogs
import race


def main():
    race.make_screen()
    audio.start_background_music("assets/TeenageMutantNinjaTurtles.mid")
    screen = race.get_screen()

    keep_playing = True
    first_run = True

    while keep_playing:
        if not first_run:
            screen.clear()
        first_run = False

        race.set_background()
        track_name = dialogs.get_user_track()
        species    = dialogs.get_user_species()
        racers     = race.create_racers(species)
        n          = len(racers)
        race.draw_boundary_stones(track_name, n)
        race.place_racers_on_track(racers, track_name)
        race.draw_start_line(track_name, n)
        race.draw_finish_line(track_name, n)

        user_bet = dialogs.get_user_bet(species)

        winning_turtle, finish_order = race.run_race(racers, track_name, user_bet)

        user_won = winning_turtle is racers[user_bet - 1]['o']
        race.show_podium(racers, finish_order)
        race.celebrate(winning_turtle, user_won, racers)
        race.announce_result(winning_turtle, user_bet, racers)

        keep_playing = dialogs.ask_play_again()

    audio.stop_background_music()
    screen.bye()


if __name__ == "__main__":
    main()
