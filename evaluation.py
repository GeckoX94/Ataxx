"""
evaluation.py

Modular game interface for development and report generation.
Supports manual player configuration or predefined test matchups,
with two display modes: 'tech' (detailed) and 'clean' (minimal).

Usage:
    python3 evaluation.py
"""

from game import create_board, print_board, get_valid_moves, apply_move
from algorithme.minimax import get_best_move
from algorithme.alphabeta import get_best_move_alpha_beta, clear_killers
from utils.timer import Timer
from config.player_config import setup_player
from config.test_config import get_test_matchup
from config.ui_config import ask_game_mode, ask_display_mode
from utils.cache_key import clear_all_caches


def play_game():
    """
    Run a single game with interactively configured players.

    The user first selects a game mode (manual or auto), then a display mode.
    In manual mode each player is configured individually; in auto mode a
    predefined matchup from test_config.py is used.
    """
    clear_all_caches()
    clear_killers()
    board = create_board()
    current_player = 1
    pass_count = 0
    timer = Timer()

    # Select game mode.
    game_mode = ask_game_mode()

    if game_mode == "2":
        players_config = get_test_matchup()
    else:
        players_config = {
            1:  setup_player("A"),
            -1: setup_player("B"),
        }

    # Select display mode.
    mode = ask_display_mode()
    is_tech = (mode == "tech")

    print(f"\n======================")
    print(f"MODE: {mode.upper()}")
    print(f"======================\n")

    while True:
        pieces_a = board.count(1)
        pieces_b = board.count(-1)

        if pieces_a == 0 or pieces_b == 0:
            break

        print_board(board)
        moves = get_valid_moves(board, current_player)
        player_name = "A" if current_player == 1 else "B"

        if len(moves) == 0:
            print(f"Player {player_name} has no moves and passes.")
            pass_count += 1
            current_player = -current_player

            if pass_count >= 2:
                print("Game over (two consecutive passes).")
                break
            continue
        else:
            pass_count = 0

        print(f"Player {player_name}")

        if is_tech:
            for i, move in enumerate(moves):
                print(f"  {i}: {move}")

        config = players_config[current_player]

        if config["type"] == "human":
            try:
                choice = int(input("Your move (index): "))
                if 0 <= choice < len(moves):
                    move = moves[choice]
                else:
                    print("Invalid choice.")
                    continue
            except ValueError:
                print("Invalid input.")
                continue

        else:
            print("AI is thinking...")

            if is_tech:
                print(f"  algo={config['algo']}  depth={config['depth']}  heuristic={config['heuristic']}")

            start_time = timer.start()

            if config["algo"] == "minimax":
                move = get_best_move(
                    board, config["depth"], current_player, config["heuristic"]
                )
            elif config["algo"] == "alphabeta":
                move = get_best_move_alpha_beta(
                    board, config["depth"], current_player, config["heuristic"]
                )
            else:
                raise ValueError(f"Unknown algorithm: {config['algo']}")

            elapsed = timer.stop(start_time, current_player)

            if is_tech:
                print(f"  Player {player_name} time: {elapsed:.3f}s")

        if move is None:
            print("Error: no move found.")
            break

        board = apply_move(board, move, current_player)
        current_player = -current_player

    # End of game.
    score_a = board.count(1)
    score_b = board.count(-1)

    print_board(board)

    if is_tech:
        timer.print_results()
        timer.print_detailed_stats()

    print(f"Final score -> Player A: {score_a} | Player B: {score_b}")

    if score_a > score_b:
        print("Player A wins.")
    elif score_b > score_a:
        print("Player B wins.")
    else:
        print("Draw.")

    print("Game over.")


if __name__ == "__main__":
    play_game()