"""
algorithme/minimax.py

Minimax search algorithm for Ataxx with transposition table and move capping.

Player A (1) is the maximising player; Player B (-1) is the minimising player.

Optimisations :
- Transposition table (TT) : évite de ré-évaluer les positions déjà vues.
- Move capping (TOP_K = 20) : seuls les TOP_K meilleurs coups (triés par
  différence de pièces, O(49)) sont explorés à chaque nœud, ce qui réduit
  le facteur de branchement de ~100 à 20 en milieu de partie.
- Pre-sort rapide dans get_best_move : tri par somme du board (pas d'heuristique
  complète), bien plus rapide que evaluate_position.
"""

import math
import random
from game.rules import get_valid_moves, apply_move
from .heuristics import evaluate_position
from utils.cache_key import tt_lookup, tt_store


# Nombre maximum de coups explorés à chaque nœud interne.
TOP_K = 20


def _fast_score(board, move, player):
    """Score rapide d'un coup : différence de pièces après application (O(49))."""
    new_board = apply_move(board, move, player)
    return sum(new_board)  # A=+1, B=-1 → somme = avantage de A


def _order_moves(moves, board, player):
    """
    Trie les coups par score rapide et retourne les TOP_K meilleurs.

    Args:
        moves:  Liste de coups légaux.
        board:  État courant.
        player: Joueur actif.

    Returns:
        Liste des TOP_K meilleurs coups triés.
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

    # No moves available: the active player passes.
    if not moves:
        if passed:
            value = evaluate_position(board, player, heuristic_type, 0, len(opponent_moves))
            tt_store(board, player, value, "EXACT", depth)
            return value
        value = minimax(board, depth - 1, -player, heuristic_type, passed=True)
        tt_store(board, player, value, "EXACT", depth)
        return value

    # Move capping : on ne garde que les TOP_K meilleurs coups.
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

    # Tri rapide par différence de pièces. En cas d'égalité de score,
    # tie-breaking aléatoire pour éviter que la même partie se rejoue
    # identiquement à chaque fois.
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