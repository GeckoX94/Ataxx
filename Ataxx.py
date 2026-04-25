"""
Ataxx.py

Main entry point for the Ataxx 7x7 game.
This is the clean, presentation-ready interface used for grading.

Three AI difficulty profiles are available, and two game modes:
    - AI vs AI
    - Player vs AI

Difficulty profiles:
    1 - Easy   : Minimax, depth 2, heuristic v2
    2 - Medium : Minimax, depth 3, heuristic v3
    3 - Hard   : Alpha-Beta, depth 4, heuristic v4
"""

from game import create_board, print_board, get_valid_moves, apply_move
from algorithme.minimax import get_best_move
from algorithme.alphabeta import get_best_move_alpha_beta, clear_killers
from utils.timer import Timer
from utils.cache_key import clear_all_caches


PROFILES = {
    "easy":   {"algo": "minimax",    "depth": 2, "heuristic": "v2"},
    "medium": {"algo": "minimax",    "depth": 3, "heuristic": "v3"},
    "hard":   {"algo": "alphabeta",  "depth": 4, "heuristic": "v4"},
}

PROFILE_LABELS = {
    "1": "easy",
    "2": "medium",
    "3": "hard",
}


def show_main_menu():
    """Display the main menu and return the user's choice."""
    print("\n" + "=" * 50)
    print("   ATAXX 7x7")
    print("=" * 50)
    print()
    print("  1) AI vs AI")
    print("  2) Player vs AI")
    print("  3) Quit")
    print()
    return input("Choice (1/2/3): ").strip()


def show_profile_menu():
    """Display the difficulty profile selection menu."""
    print()
    print("  Difficulty levels:")
    print("  1) Easy   - Minimax, depth 2, heuristic v2")
    print("  2) Medium - Minimax, depth 3, heuristic v3")
    print("  3) Hard   - Alpha-Beta, depth 4, heuristic v4")
    print()


def select_profile(prompt):
    """
    Prompt the user to select a difficulty profile.

    Args:
        prompt: Message shown before the input field.

    Returns:
        Profile key string ('easy', 'medium', or 'hard').
    """
    print(prompt)
    choice = input("  Choice (1/2/3): ").strip()
    return PROFILE_LABELS.get(choice, "easy")


def display_board(board):
    """Print the board with current scores."""
    score_a = board.count(1)
    score_b = board.count(-1)
    print()
    print_board(board)
    print(f"  Score -> Player A: {score_a}  |  Player B: {score_b}")
    print()


def ai_move(board, profile_key, player, timer):
    """
    Compute and return the AI's move.

    Args:
        board:       Current board state.
        profile_key: Difficulty key ('easy', 'medium', 'hard').
        player:      Active player (1 or -1).
        timer:       Timer instance for recording move time.

    Returns:
        Move as ((x1, y1), (x2, y2)).
    """
    profile = PROFILES[profile_key]
    start = timer.start()
    if profile["algo"] == "alphabeta":
        move = get_best_move_alpha_beta(board, profile["depth"], player, profile["heuristic"])
    else:
        move = get_best_move(board, profile["depth"], player, profile["heuristic"])
    elapsed = timer.stop(start, player)
    player_name = "A" if player == 1 else "B"
    print(f"  Player {player_name} plays in {elapsed:.3f}s.")
    return move


def play_ai_vs_ai():
    """Run a game between two AI players."""
    clear_all_caches()
    clear_killers()

    print("\n" + "=" * 50)
    print("   AI vs AI")
    print("=" * 50)

    show_profile_menu()
    profile_a = select_profile("Player A difficulty:")
    profile_b = select_profile("Player B difficulty:")

    print()
    print(f"  Player A: {profile_a.upper()}  |  Player B: {profile_b.upper()}")
    print("=" * 50)

    board = create_board()
    current_player = 1
    pass_count = 0
    timer = Timer()

    while True:
        score_a = board.count(1)
        score_b = board.count(-1)

        if score_a == 0 or score_b == 0:
            break

        display_board(board)

        moves = get_valid_moves(board, current_player)
        player_name = "A" if current_player == 1 else "B"

        if not moves:
            print(f"  Player {player_name} passes.")
            pass_count += 1
            current_player = -current_player
            if pass_count >= 2:
                print("\n  Game over (two consecutive passes).")
                break
            continue

        pass_count = 0
        profile_key = profile_a if current_player == 1 else profile_b
        move = ai_move(board, profile_key, current_player, timer)

        board = apply_move(board, move, current_player)
        current_player = -current_player

    # Final result.
    score_a = board.count(1)
    score_b = board.count(-1)
    display_board(board)

    if score_a > score_b:
        print("  Player A wins!")
    elif score_b > score_a:
        print("  Player B wins!")
    else:
        print("  Draw!")

    print("=" * 50)


def play_player_vs_ai():
    """Run a game between a human player and an AI."""
    clear_all_caches()
    clear_killers()

    print("\n" + "=" * 50)
    print("   Player vs AI")
    print("=" * 50)

    show_profile_menu()
    profile_key = select_profile("AI difficulty:")

    print()
    print(f"  You play as Player A (A). The AI plays as Player B ({profile_key.upper()}).")
    print("=" * 50)

    board = create_board()
    current_player = 1
    pass_count = 0
    timer = Timer()

    while True:
        score_a = board.count(1)
        score_b = board.count(-1)

        if score_a == 0 or score_b == 0:
            break

        display_board(board)

        moves = get_valid_moves(board, current_player)
        player_name = "A (you)" if current_player == 1 else "B (AI)"

        if not moves:
            print(f"  Player {player_name} passes.")
            pass_count += 1
            current_player = -current_player
            if pass_count >= 2:
                print("\n  Game over (two consecutive passes).")
                break
            continue

        pass_count = 0

        if current_player == 1:
            # Human turn.
            print("  Available moves:")
            for i, m in enumerate(moves):
                print(f"    {i}: {m}")
            try:
                choice = int(input("  Your move (index): "))
                if 0 <= choice < len(moves):
                    move = moves[choice]
                else:
                    print("  Invalid choice, try again.")
                    continue
            except ValueError:
                print("  Invalid input, try again.")
                continue
        else:
            # AI turn.
            move = ai_move(board, profile_key, current_player, timer)

        board = apply_move(board, move, current_player)
        current_player = -current_player

    # Final result.
    score_a = board.count(1)
    score_b = board.count(-1)
    display_board(board)

    if score_a > score_b:
        print("  You win!")
    elif score_b > score_a:
        print("  The AI wins!")
    else:
        print("  Draw!")

    print("=" * 50)


def main():
    """Main game loop."""
    while True:
        choice = show_main_menu()

        if choice == "1":
            play_ai_vs_ai()
        elif choice == "2":
            play_player_vs_ai()
        elif choice == "3":
            print("\n  Goodbye!\n")
            break
        else:
            print("  Invalid choice, please try again.")


if __name__ == "__main__":
    main()