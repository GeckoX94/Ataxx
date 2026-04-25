"""
utils/random_ai.py

Random player for Ataxx. Used as a baseline opponent in tournaments to
demonstrate that any search-based AI performs better than random play.
"""

import random
from game.rules import get_valid_moves


def get_random_move(board, player):
    """
    Return a random legal move for the given player.

    Args:
        board:  Current board state (flat tuple or list-of-lists).
        player: Active player (1 or -1).

    Returns:
        A random move as ((x1, y1), (x2, y2)), or None if no moves are available.
    """
    moves = get_valid_moves(board, player)
    if moves:
        return random.choice(moves)
    return None
