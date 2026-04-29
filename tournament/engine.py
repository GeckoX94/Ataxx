"""
tournament/engine.py

Tournament engine for Ataxx.
Plays N games between two AI configurations and returns aggregated statistics.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from game.board import create_board
from game.rules import get_valid_moves, apply_move
from algorithme.minimax import get_best_move
from algorithme.alphabeta import get_best_move_alpha_beta, clear_killers
from utils.random_ai import get_random_move
from utils.cache_key import clear_all_caches


# Official difficulty levels used in both the main interface and the tournament.
LEVELS = {
    "Random": {"algo": "random",    "depth": 0, "heuristic": None},
    "Easy":   {"algo": "minimax",   "depth": 2, "heuristic": "v2"},
    "Medium": {"algo": "minimax",   "depth": 3, "heuristic": "v3"},
    "Hard":   {"algo": "alphabeta", "depth": 4, "heuristic": "v4"},
}


def get_ai_move(board, config, player):
    """
    Return the move selected by an AI according to its configuration.

    Args:
        board:  Current board state (flat tuple).
        config: Configuration dict with keys 'algo', 'depth', 'heuristic'.
        player: Active player (1 or -1).

    Returns:
        Move as ((x1, y1), (x2, y2)), or None if no moves are available.
    """
    algo = config["algo"]
    if algo == "random":
        return get_random_move(board, player)
    elif algo == "minimax":
        return get_best_move(board, config["depth"], player, config["heuristic"])
    elif algo == "alphabeta":
        return get_best_move_alpha_beta(board, config["depth"], player, config["heuristic"])
    else:
        raise ValueError(f"Unknown algorithm: {algo}")


def play_one_game(config_a, config_b, first_player=1, verbose=False):
    """
    Play a single game between two AI configurations.

    Args:
        config_a:     Configuration for Player A (1).
        config_b:     Configuration for Player B (-1).
        first_player: Which player moves first (1 or -1).
        verbose:      If True, print a result line after the game.

    Returns:
        Tuple (winner, score_a, score_b, duration, move_count) where
        winner = 1 (Player A), -1 (Player B), or 0 (draw).
    """
    clear_all_caches()
    clear_killers()
    board = create_board()
    current_player = first_player
    pass_count = 0
    move_count = 0
    t_start = time.time()

    configs = {1: config_a, -1: config_b}

    while True:
        score_a = board.count(1)
        score_b = board.count(-1)

        if score_a == 0 or score_b == 0:
            break

        moves = get_valid_moves(board, current_player)

        if not moves:
            pass_count += 1
            if pass_count >= 2:
                break
            current_player = -current_player
            continue

        pass_count = 0
        move = get_ai_move(board, configs[current_player], current_player)

        if move is None:
            break

        board = apply_move(board, move, current_player)
        current_player = -current_player
        move_count += 1

    duration = time.time() - t_start
    score_a = board.count(1)
    score_b = board.count(-1)

    if score_a > score_b:
        winner = 1
    elif score_b > score_a:
        winner = -1
    else:
        winner = 0

    if verbose:
        winner_str = "Player A" if winner == 1 else ("Player B" if winner == -1 else "Draw")
        print(f"  -> {winner_str} | {score_a}-{score_b} | {move_count} moves | {duration:.1f}s")

    return winner, score_a, score_b, duration, move_count


def run_matchup(name1, name2, n_games=50, verbose=True):
    """
    Run N games between two named difficulty levels.

    Starting player alternates every game to neutralise first-mover advantage.

    Args:
        name1:   Name of the first level (key in LEVELS).
        name2:   Name of the second level (key in LEVELS).
        n_games: Number of games to play.
        verbose: If True, print a result line for each game.

    Returns:
        Dict of aggregated statistics.
    """
    config1 = LEVELS[name1]
    config2 = LEVELS[name2]

    wins1 = wins2 = draws = 0
    total_score_a = total_score_b = 0
    total_time = 0.0
    total_moves = 0
    scores_a_list = []
    scores_b_list = []

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"  {name1} (Player A) vs {name2} (Player B) -> {n_games} games")
        print(f"{'=' * 60}")

    for i in range(n_games):
        first = 1 if i % 2 == 0 else -1

        if first == 1:
            winner, score_a, score_b, dur, moves = play_one_game(
                config1, config2, first_player=1, verbose=verbose
            )
        else:
            # config2 starts as Player A this turn; flip interpretation.
            winner_raw, score_b, score_a, dur, moves = play_one_game(
                config2, config1, first_player=1, verbose=verbose
            )
            winner = -winner_raw if winner_raw != 0 else 0

        if winner == 1:
            wins1 += 1
        elif winner == -1:
            wins2 += 1
        else:
            draws += 1

        total_score_a += score_a
        total_score_b += score_b
        scores_a_list.append(score_a)
        scores_b_list.append(score_b)
        total_time += dur
        total_moves += moves

        if verbose:
            winner_str = name1 if winner == 1 else (name2 if winner == -1 else "Draw")
            first_str = "A" if first == 1 else "B"
            print(
                f"  Game {i + 1:02d}/{n_games} (starts: {first_str}) -> "
                f"{winner_str:<15s} | {score_a}-{score_b} | {moves} moves"
            )

    stats = {
        "name1": name1,
        "name2": name2,
        "n_games": n_games,
        "wins1": wins1,
        "wins2": wins2,
        "draws": draws,
        "win_rate1": wins1 / n_games * 100,
        "win_rate2": wins2 / n_games * 100,
        "draw_rate": draws / n_games * 100,
        "avg_score1": total_score_a / n_games,
        "avg_score2": total_score_b / n_games,
        "avg_time": total_time / n_games,
        "avg_moves": total_moves / n_games,
        "total_time": total_time,
        "scores1": scores_a_list,
        "scores2": scores_b_list,
    }
    return stats


def print_stats(stats):
    """Print a formatted summary table for a matchup."""
    n1, n2 = stats["name1"], stats["name2"]
    print(f"\n{'-' * 60}")
    print(f"  RESULTS: {n1} vs {n2} ({stats['n_games']} games)")
    print(f"{'-' * 60}")
    print(f"  {n1:<20} : {stats['wins1']:>3} wins  ({stats['win_rate1']:>6.1f}%)")
    print(f"  {n2:<20} : {stats['wins2']:>3} wins  ({stats['win_rate2']:>6.1f}%)")
    print(f"  {'Draws':<20} : {stats['draws']:>3}       ({stats['draw_rate']:>6.1f}%)")
    print(f"  Average score      : {stats['avg_score1']:.1f} - {stats['avg_score2']:.1f}")
    print(f"  Average time/game  : {stats['avg_time']:.1f}s")
    print(f"  Average moves/game : {stats['avg_moves']:.1f}")
    print(f"  Total duration     : {stats['total_time']:.0f}s ({stats['total_time'] / 60:.1f} min)")
    print(f"{'-' * 60}\n")