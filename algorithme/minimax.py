"""
algorithme/minimax.py

Minimax search algorithm for Ataxx with transposition table and move capping.

Player A (1) is the maximising player; Player B (-1) is the minimising player.

Optimisations:
- Transposition table (TT): avoids re-evaluating already-seen positions.
- Move capping (TOP_K = 20): only the TOP_K best moves (sorted by piece
  difference, O(49)) are explored at each node, reducing the branching
  factor from ~100 to 20 in mid-game.
- Fast pre-sort in get_best_move: sorted by board sum (no full heuristic),
  much faster than calling evaluate_position on every candidate.
"""

import math
import random
from game.rules import get_valid_moves, apply_move
from .heuristics import evaluate_position
from utils.cache_key import tt_lookup, tt_store


# Maximum number of moves explored at each internal node.
TOP_K = 20


def _fast_score(board, move, player):
    """Fast move score: piece difference after applying the move (O(49))."""
    new_board = apply_move(board, move, player)
    return sum(new_board)  # A=+1, B=-1 -> sum = A's advantage


def _order_moves(moves, board, player):
    """
    Sort moves by fast score and return the TOP_K best.

    Args:
        moves:  List of legal moves.
        board:  Current board state.
        player: Active player.

    Returns:
        List of the TOP_K best moves, sorted.
    """
    scored = [(_fast_score(board, m, player), m) for m in moves]
    scored.sort(key=lambda x: x[0], reverse=(player == 1))
    return [m for _, m in scored[:TOP_K]]


def minimax(board, depth, player, heuristic_type, passed=False):
    """
    Recursive Minimax search with transposition table and move capping.

    Args:
        board:          Current board state (flat tuple of 49 elements).
        depth:          Remaining search depth.
        player:         Active player (1 = MAX, -1 = MIN).
        heuristic_type: Heuristic to use for leaf evaluation ('v1'..'v4').
        passed:         True if the previous player had no moves and passed.

    Returns:
        Evaluation score from Player A's perspective.
    """
    tt_entry = tt_lookup(board, player, depth)
    if tt_entry is not None:
        score, flag = tt_entry
        if flag == "EXACT":
            return score

    moves = get_valid_moves(board, player)
    opponent_moves = get_valid_moves(board, -player)

    # Leaf node: evaluate and cache.
    if depth == 0:
        moves_count = len(moves)
        opponent_count = len(opponent_moves)
        value = evaluate_position(board, player, heuristic_type, moves_count, opponent_count)
        tt_store(board, player, value, "EXACT", depth)
        return value

    # No moves available: active player passes.
    if not moves:
        if passed:
            value = evaluate_position(board, player, heuristic_type, 0, len(opponent_moves))
            tt_store(board, player, value, "EXACT", depth)
            return value
        value = minimax(board, depth - 1, -player, heuristic_type, passed=True)
        tt_store(board, player, value, "EXACT", depth)
        return value

    # Move capping: keep only the TOP_K best moves.
    ordered_moves = _order_moves(moves, board, player)

    if player == 1:
        best_value = -math.inf
        for move in ordered_moves:
            new_board = apply_move(board, move, player)
            value = minimax(new_board, depth - 1, -1, heuristic_type, False)
            best_value = max(best_value, value)
        tt_store(board, player, best_value, "EXACT", depth)
        return best_value
    else:
        best_value = math.inf
        for move in ordered_moves:
            new_board = apply_move(board, move, player)
            value = minimax(new_board, depth - 1, 1, heuristic_type, False)
            best_value = min(best_value, value)
        tt_store(board, player, best_value, "EXACT", depth)
        return best_value


def get_best_move(board, depth, player, heuristic_type):
    """
    Return the best move for the given player using Minimax.

    Moves are pre-sorted by fast piece-difference score (not full heuristic)
    before the search, which improves TT hit rates without the overhead of
    calling evaluate_position on every candidate.

    Args:
        board:          Current board state (flat tuple or list-of-lists).
        depth:          Search depth.
        player:         Active player (1 or -1).
        heuristic_type: Heuristic to use ('v1'..'v4').

    Returns:
        Best move as ((x1, y1), (x2, y2)), or None if no moves are available.
    """
    from game.rules import board_to_flat

    if not isinstance(board, tuple):
        board = board_to_flat(board)

    moves = get_valid_moves(board, player)
    if not moves:
        return None

    # Fast sort by piece difference. On score ties, random tie-breaking
    # to avoid identical game replays.
    scored = [(_fast_score(board, m, player), m) for m in moves]
    scored.sort(key=lambda x: (x[0], random.random()), reverse=(player == 1))
    root_moves = [m for _, m in scored[:TOP_K]]

    best_move = root_moves[0]

    if player == 1:
        best_value = -math.inf
        for move in root_moves:
            new_board = apply_move(board, move, player)
            value = minimax(new_board, depth - 1, -1, heuristic_type, False)
            if value > best_value:
                best_value = value
                best_move = move
    else:
        best_value = math.inf
        for move in root_moves:
            new_board = apply_move(board, move, player)
            value = minimax(new_board, depth - 1, 1, heuristic_type, False)
            if value < best_value:
                best_value = value
                best_move = move

    return best_move