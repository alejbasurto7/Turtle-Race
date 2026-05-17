import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import audio
import dialogs
import leaderboard
import race


def main():
    race.make_screen()
    audio.start_background_music()
    screen = race.get_screen()

    race.set_background()                  # Lawn drawn once for the menu backdrop.

    running = True
    while running:
        choice = dialogs.get_main_menu_choice()
        if choice == "quit":
            running = False
            break
        if choice == "leaderboard":
            dialogs.show_leaderboard_placeholder()
            continue
        # choice == "race" — enter inner race-rounds loop.
        in_round_loop = True
        while in_round_loop:
            screen.clear()                              # Idempotent on first iteration's clean canvas.
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

            finish_order_names = [racers[i]['name'] for i in finish_order]
            leaderboard.record_race(species, track_name, finish_order_names)

            user_won = winning_turtle is racers[user_bet - 1]['o']
            race.show_podium(racers, finish_order)
            race.celebrate(winning_turtle, user_won, racers)
            race.announce_result(winning_turtle, user_bet, racers)

            post = dialogs.ask_play_again_choice()
            if post == "again":
                continue
            if post == "menu":
                screen.clear()
                race.set_background()                   # Refresh canvas to lawn-only for the menu.
                in_round_loop = False
            elif post == "quit":
                running = False
                in_round_loop = False

    audio.stop_background_music()
    screen.bye()


if __name__ == "__main__":
    main()
