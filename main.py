import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import audio
import dialogs
import race
from constants import TURTLE_COLORS


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
        race.draw_boundary_stones(track_name)
        turtles_list = race.create_turtles(TURTLE_COLORS)
        race.place_turtles_on_track(turtles_list, track_name)
        race.draw_start_line(track_name)
        race.draw_finish_line(track_name)

        user_bet = dialogs.get_user_bet()

        winning_turtle = race.run_race(turtles_list, track_name, user_bet)

        user_won = winning_turtle.pencolor() == turtles_list[user_bet - 1]['o'].pencolor()
        race.celebrate(winning_turtle, user_won)
        race.announce_result(winning_turtle, user_bet, turtles_list)

        keep_playing = dialogs.ask_play_again()

    audio.stop_background_music()
    screen.bye()


if __name__ == "__main__":
    main()
