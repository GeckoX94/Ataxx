"""
algorithme/alphabeta.py

Alpha-Beta pruning avec Iterative Deepening, Killer Moves et Move Capping.

Optimisations :
- Transposition table (TT) persistante entre les coups (vidée uniquement entre parties).
- Killer moves : les coups ayant causé un cut-off bêta sont essayés en premier.
- Iterative deepening : profondeurs 1, 2, ..., max_depth, chaque passe enrichit la TT.
- Move capping : seuls les TOP_K meilleurs coups (scoring rapide) sont explorés en interne,
  ce qui réduit le facteur de branchement de ~100 à ~20 en milieu de partie.
- Move ordering : les coups non-killers sont triés par différence de pièces (O(49)).
"""

import math
import random
from game.rules import get_valid_moves, apply_move
from .heuristics import evaluate_position
from utils.cache_key import tt_lookup, tt_store


MAX_DEPTH = 10

# Nombre max de coups explorés à chaque nœud interne.
# Réduit le branching factor de ~100 à TOP_K en milieu de partie.
TOP_K = 20

_killers = [[None, None] for _ in range(MAX_DEPTH + 1)]


def _store_killer(move, depth):
    """Enregistre un killer move (cause d'un cut-off bêta)."""
    if depth > MAX_DEPTH:
        return
    k = _killers[depth]
    if move != k[0]:
        k[1] = k[0]
        k[0] = move


def _get_killers(depth):
    """Retourne les killer moves enregistrés pour cette profondeur."""
    if depth > MAX_DEPTH:
        return []
    return [m for m in _killers[depth] if m is not None]


def clear_killers():
    """Remet à zéro la table des killers (appeler entre parties)."""
    global _killers
    _killers = [[None, None] for _ in range(MAX_DEPTH + 1)]


def _fast_score(board, move, player):
    """Score rapide d'un coup : différence de pièces après application."""
    new_board = apply_move(board, move, player)
    return sum(new_board)  # A=+1, B=-1 → somme = avantage de A


def _order_moves(moves, board, player, depth):
    """
    Trie les coups : killers d'abord, puis top TOP_K coups par score rapide.

    Args:
        moves:  Liste de coups légaux.
        board:  État courant.
        player: Joueur actif.
        depth:  Profondeur actuelle (pour les killers).

    Returns:
        Liste ordonnée de coups, limitée à TOP_K + killers.
    """
    killers = _get_killers(depth)
    killer_set = set()
    killer_moves = []
    for k in killers:
        if k is not None and k in moves:
            killer_moves.append(k)
            killer_set.add(k)

    other_moves = [m for m in moves if m not in killer_set]

    # Score rapide : somme du board après le coup (pas d'heuristique complète).
    scored = []
    for move in other_moves:
        score = _fast_score(board, move, player)
        scored.append((score, move))

    # MAX veut maximiser (score élevé = bon), MIN veut minimiser (score bas = bon).
    scored.sort(key=lambda x: x[0], reverse=(player == 1))

    # On limite à TOP_K coups non-killers pour contrôler le branching factor.
    capped = [m for _, m in scored[:TOP_K]]

    return killer_moves + capped


def minimax_alpha_beta(board, depth, player, alpha, beta, heuristic_type, passed=False):
    """
    Minimax avec alpha-bêta, TT et move capping.

    Args:
        board:          État du plateau (flat tuple de 49 éléments).
        depth:          Profondeur restante.
        player:         Joueur actif (1 = MAX, -1 = MIN).
        alpha:          Meilleur score garanti pour MAX.
        beta:           Meilleur score garanti pour MIN.
        heuristic_type: Heuristique à utiliser ('v1'..'v4').
        passed:         True si le joueur précédent a passé (aucun coup disponible).

    Returns:
        Score d'évaluation du point de vue du joueur A.
    """
    alpha_orig = alpha

    # Consultation de la TT.
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

    # Nœud terminal par profondeur : évaluation heuristique.
    if depth == 0:
        moves_count = len(moves)
        opponent_count = len(opponent_moves)
        value = evaluate_position(board, player, heuristic_type, moves_count, opponent_count)
        tt_store(board, player, value, "EXACT", depth)
        return value

    # Aucun coup disponible : le joueur passe.
    if not moves:
        if passed:
            # Deux passes consécutives → fin de partie.
            value = evaluate_position(board, player, heuristic_type, 0, len(opponent_moves))
            tt_store(board, player, value, "EXACT", depth)
            return value
        value = minimax_alpha_beta(
            board, depth - 1, -player, alpha, beta, heuristic_type, passed=True
        )
        tt_store(board, player, value, "EXACT", depth)
        return value

    # Ordonnancement des coups (killers + top K).
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

    # Stockage du résultat avec le bon flag.
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
    Retourne le meilleur coup via Iterative Deepening Alpha-Beta.

    La TT est conservée entre les coups pour accumuler la connaissance
    des positions déjà vues. Elle est uniquement vidée entre parties (via
    clear_all_caches() dans Ataxx.py).

    Args:
        board:          État du plateau (flat tuple ou list-of-lists).
        depth:          Profondeur maximale de recherche.
        player:         Joueur actif (1 ou -1).
        heuristic_type: Heuristique à utiliser ('v1'..'v4').

    Returns:
        Meilleur coup sous forme ((x1, y1), (x2, y2)), ou None si aucun coup.
    """
    from game.rules import board_to_flat

    if not isinstance(board, tuple):
        board = board_to_flat(board)

    moves = get_valid_moves(board, player)
    if not moves:
        return None

    # Trier tous les coups disponibles par score rapide.
    # En cas d'égalité de score, on brise le tie de façon aléatoire
    # pour éviter que la même partie se rejoue identiquement à chaque fois.
    scored_root = sorted(
        moves,
        key=lambda m: (_fast_score(board, m, player), random.random()),
        reverse=(player == 1)
    )
    best_move = scored_root[0]

    for current_depth in range(1, depth + 1):
        # Mettre le meilleur coup de la passe précédente en tête.
        ordered = [best_move] + [m for m in scored_root if m != best_move]
        # Limiter la recherche racine à TOP_K coups.
        root_moves = ordered[:TOP_K + 1]  # +1 pour inclure best_move même si hors TOP_K

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