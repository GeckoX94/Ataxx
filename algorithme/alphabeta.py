"""
algorithme/alphabeta.py

Alpha-Beta pruning with Iterative Deepening, Killer Moves and Move Capping.

Optimisations:
- Persistent transposition table (TT) across moves (cleared only between games).
- Killer moves: moves that caused a beta cut-off are tried first.
- Iterative deepening: depths 1, 2, ..., max_depth, each pass enriches the TT.
- Move capping: only the TOP_K best moves (fast scoring) are explored internally,
  reducing the branching factor from ~100 to ~20 in mid-game.
- Move ordering: non-killer moves are sorted by piece difference (O(49)).
"""

import math
import random
from game.rules import get_valid_moves, apply_move
from .heuristics import evaluate_position
from utils.cache_key import tt_lookup, tt_store


MAX_DEPTH = 10

# Maximum number of moves explored at each internal node.
# Reduces the branching factor from ~100 to TOP_K in mid-game.
TOP_K = 20

_killers = [[None, None] for _ in range(MAX_DEPTH + 1)]


def _store_killer(move, depth):
    """Store a killer move (cause of a beta cut-off)."""
    if depth > MAX_DEPTH:
        return
    k = _killers[depth]
    if move != k[0]:
        k[1] = k[0]
        k[0] = move


def _get_killers(depth):
    """Return the killer moves stored for this depth."""
    if depth > MAX_DEPTH:
        return []
    return [m for m in _killers[depth] if m is not None]


def clear_killers():
    """Reset the killer move table (call between games)."""
    global _killers
    _killers = [[None, None] for _ in range(MAX_DEPTH + 1)]


def _fast_score(board, move, player):
    """Fast move score: piece difference after applying the move."""
    new_board = apply_move(board, move, player)
    return sum(new_board)  # A=+1, B=-1 -> sum = A's advantage


def _order_moves(moves, board, player, depth):
    """
    Sort moves: killers first, then top TOP_K moves by fast score.

    Args:
        moves:  List of legal moves.
        board:  Current board state.
        player: Active player.
        depth:  Current depth (for killer lookup).

    Returns:
        Ordered list of moves, capped at TOP_K + killers.
    """
    killers = _get_killers(depth)
    killer_set = set()
    killer_moves = []
    for k in killers:
        if k is not None and k in moves:
            killer_moves.append(k)
            killer_set.add(k)

    other_moves = [m for m in moves if m not in killer_set]

    # Fast score: board sum after the move (no full heuristic).
    scored = []
    for move in other_moves:
        score = _fast_score(board, move, player)
        scored.append((score, move))

    # MAX wants to maximise (high score = good), MIN wants to minimise (low score = good).
    scored.sort(key=lambda x: x[0], reverse=(player == 1))

    # Cap to TOP_K non-killer moves to control the branching factor.
    capped = [m for _, m in scored[:TOP_K]]

    return killer_moves + capped


def minimax_alpha_beta(board, depth, player, alpha, beta, heuristic_type, passed=False):
    """
    Minimax with alpha-beta, TT and move capping.

    Args:
        board:          Board state (flat tuple of 49 elements).
        depth:          Remaining search depth.
        player:         Active player (1 = MAX, -1 = MIN).
        alpha:          Best score guaranteed for MAX.
        beta:           Best score guaranteed for MIN.
        heuristic_type: Heuristic to use ('v1'..'v4').
        passed:         True if the previous player had no moves and passed.

    Returns:
        Evaluation score from Player A's perspective.
    """
    alpha_orig = alpha

    # Transposition table lookup.
    tt_entry = tt_lookup(board, player, depth)
    if tt_entry is not None:
        tt_score, tt_flag = tt_entry
        if tt_flag == "EXACT":
            return tt_score
        elif tt_flag == "LOWER":
            alpha = max(alpha, tt_score)
        elif tt_flag == "UPPER":
            beta = min(beta, tt_score)
        if alpha >= beta:
            return tt_score

    moves = get_valid_moves(board, player)
    opponent_moves = get_valid_moves(board, -player)

    # Terminal node by depth: heuristic evaluation.
    if depth == 0:
        moves_count = len(moves)
        opponent_count = len(opponent_moves)
        value = evaluate_position(board, player, heuristic_type, moves_count, opponent_count)
        tt_store(board, player, value, "EXACT", depth)
        return value

    # No moves available: active player passes.
    if not moves:
        if passed:
            # Two consecutive passes -> end of game.
            value = evaluate_position(board, player, heuristic_type, 0, len(opponent_moves))
            tt_store(board, player, value, "EXACT", depth)
            return value
        value = minimax_alpha_beta(
            board, depth - 1, -player, alpha, beta, heuristic_type, passed=True
        )
        tt_store(board, player, value, "EXACT", depth)
        return value

    # Move ordering (killers + top K).
    ordered_moves = _order_moves(moves, board, player, depth)

    if player == 1:
        value = -math.inf
        for move in ordered_moves:
            new_board = apply_move(board, move, player)
            value = max(
                value,
                minimax_alpha_beta(new_board, depth - 1, -1, alpha, beta, heuristic_type, False)
            )
            alpha = max(alpha, value)
            if alpha >= beta:
                _store_killer(move, depth)
                break
    else:
        value = math.inf
        for move in ordered_moves:
            new_board = apply_move(board, move, player)
            value = min(
                value,
                minimax_alpha_beta(new_board, depth - 1, 1, alpha, beta, heuristic_type, False)
            )
            beta = min(beta, value)
            if alpha >= beta:
                _store_killer(move, depth)
                break

    # Store result with the correct flag.
    if value <= alpha_orig:
        flag = "UPPER"
    elif value >= beta:
        flag = "LOWER"
    else:
        flag = "EXACT"
    tt_store(board, player, value, flag, depth)

    return value


def get_best_move_alpha_beta(board, depth, player, heuristic_type):
    """
    Return the best move via Iterative Deepening Alpha-Beta.

    The TT is preserved across moves to accumulate knowledge of already-seen
    positions. It is only cleared between games (via clear_all_caches()
    in Ataxx.py).

    Args:
        board:          Board state (flat tuple or list-of-lists).
        depth:          Maximum search depth.
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

    # Sort all available moves by fast score.
    # On score ties, break randomly to avoid identical game replays.
    scored_root = sorted(
        moves,
        key=lambda m: (_fast_score(board, m, player), random.random()),
        reverse=(player == 1)
    )
    best_move = scored_root[0]

    for current_depth in range(1, depth + 1):
        # Put the best move from the previous pass at the front.
        ordered = [best_move] + [m for m in scored_root if m != best_move]
        # Cap root search to TOP_K moves.
        root_moves = ordered[:TOP_K + 1]  # +1 to include best_move even if outside TOP_K

        if player == 1:
            best_value = -math.inf
            alpha, beta = -math.inf, math.inf
            for move in root_moves:
                new_board = apply_move(board, move, player)
                value = minimax_alpha_beta(
                    new_board, current_depth - 1, -1, alpha, beta, heuristic_type, False
                )
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, best_value)
        else:
            best_value = math.inf
            alpha, beta = -math.inf, math.inf
            for move in root_moves:
                new_board = apply_move(board, move, player)
                value = minimax_alpha_beta(
                    new_board, current_depth - 1, 1, alpha, beta, heuristic_type, False
                )
                if value < best_value:
                    best_value = value
                    best_move = move
                beta = min(beta, best_value)

    return best_move