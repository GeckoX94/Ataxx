"""
algorithme/heuristics.py

Evaluation heuristics for Ataxx.
The board is represented as a flat tuple of 49 elements (7x7 grid).
All heuristics return a score from the perspective of Player A (1 = maximising player).
"""

# Positional weight matrix (pre-flattened for O(1) access).
# Higher weights reward central control.
_WEIGHTS_2D = [
    [1, 2, 2, 3, 2, 2, 1],
    [2, 3, 4, 4, 4, 3, 2],
    [2, 4, 5, 5, 5, 4, 2],
    [3, 4, 5, 6, 5, 4, 3],
    [2, 4, 5, 5, 5, 4, 2],
    [2, 3, 4, 4, 4, 3, 2],
    [1, 2, 2, 3, 2, 2, 1],
]
WEIGHTS = tuple(w for row in _WEIGHTS_2D for w in row)

# Pre-computed neighbor indices for each cell.
# Avoids recomputing dx/dy loops at each evaluation call.
_NEIGHBORS = []
for _i in range(7):
    for _j in range(7):
        nb = []
        for _dx in range(-1, 2):
            for _dy in range(-1, 2):
                if _dx == 0 and _dy == 0:
                    continue
                _ni, _nj = _i + _dx, _j + _dy
                if 0 <= _ni < 7 and 0 <= _nj < 7:
                    nb.append(_ni * 7 + _nj)
        _NEIGHBORS.append(tuple(nb))


def count_pieces(board):
    """
    Count pieces on a flat board tuple.

    Args:
        board: Flat tuple of 49 elements.

    Returns:
        Tuple (pieces_player_a, pieces_player_b).
    """
    p_a = p_b = 0
    for cell in board:
        if cell == 1:
            p_a += 1
        elif cell == -1:
            p_b += 1
    return p_a, p_b


def evaluate_position(board, player, heuristic_type, moves_count=0, opponent_moves_count=0):
    """
    Evaluate a board position using the requested heuristic.

    Args:
        board:                Flat tuple of 49 elements.
        player:               Current player (1 or -1).
        heuristic_type:       Heuristic to use ('v1', 'v2', 'v3', or 'v4').
        moves_count:          Number of moves available to current player.
        opponent_moves_count: Number of moves available to opponent.

    Returns:
        Numeric score from Player A's perspective (higher = better for A).
    """
    # Convert to player A/B perspective
    if player == 1:
        moves_a = moves_count
        moves_b = opponent_moves_count
    else:
        moves_a = opponent_moves_count
        moves_b = moves_count
    
    if heuristic_type == "v1":
        return heuristic_v1(board, moves_a, moves_b)
    elif heuristic_type == "v2":
        return heuristic_v2(board, moves_a, moves_b)
    elif heuristic_type == "v3":
        return heuristic_v3(board, moves_a, moves_b)
    elif heuristic_type == "v4":
        return heuristic_v4(board, moves_a, moves_b)
    else:
        return heuristic_v1(board, moves_a, moves_b)


def heuristic_v1(board, moves_a, moves_b):
    """
    Basic material heuristic: piece difference only.

    Score = 5 * (pieces_A - pieces_B).
    Sentinel values (+9999 / -9999) flag terminal positions.
    Mobility parameters are accepted for interface uniformity but not used.

    Args:
        board:   Flat tuple of 49 elements.
        moves_a: Number of legal moves available to player A (unused).
        moves_b: Number of legal moves available to player B (unused).

    Returns:
        Numeric score from Player A's perspective.
    """
    p_a = p_b = 0
    for cell in board:
        if cell == 1:
            p_a += 1
        elif cell == -1:
            p_b += 1

    if p_a == 0:
        return -9999
    if p_b == 0:
        return 9999

    return (p_a - p_b) * 5


def heuristic_v2(board, moves_a, moves_b):
    """
    Positional heuristic: weighted piece placement and piece count bonus.

    Each piece contributes its positional weight (center > edges), rewarding
    central control in addition to raw piece count.

    Args:
        board:   Flat tuple of 49 elements.
        moves_a: Number of legal moves available to player A.
        moves_b: Number of legal moves available to player B.

    Returns:
        Numeric score from Player A's perspective.
    """
    p_a = p_b = 0
    score = 0
    for idx in range(49):
        cell = board[idx]
        if cell == 1:
            p_a += 1
            score += WEIGHTS[idx]
        elif cell == -1:
            p_b += 1
            score -= WEIGHTS[idx]

    if p_a == 0:
        return -9999
    if p_b == 0:
        return 9999

    return score + (p_a - p_b) * 10


def heuristic_v3(board, moves_a, moves_b):
    """
    Positional heuristic with offensive pressure bonus.

    Extends v2 by rewarding pieces that are adjacent to enemy pieces:
    each adjacent enemy represents a conversion opportunity (the piece
    can be captured on the next duplication). This is an offensive bonus,
    not a threat penalty — pieces close to enemies are dangerous for them.
    The same logic applies symmetrically for Player B (reducing the score).

    Args:
        board:   Flat tuple of 49 elements.
        moves_a: Number of legal moves available to player A (unused).
        moves_b: Number of legal moves available to player B (unused).

    Returns:
        Numeric score from Player A's perspective.
    """
    p_a = p_b = 0
    score = 0

    for idx in range(49):
        cell = board[idx]
        if cell == 0:
            continue
        if cell == 1:
            p_a += 1
            score += WEIGHTS[idx]
            for nb_idx in _NEIGHBORS[idx]:
                if board[nb_idx] == -1:
                    score += 1
        else:
            p_b += 1
            score -= WEIGHTS[idx]
            for nb_idx in _NEIGHBORS[idx]:
                if board[nb_idx] == 1:
                    score -= 1

    if p_a == 0:
        return -9999
    if p_b == 0:
        return 9999

    return score + (p_a - p_b) * 8


def heuristic_v4(board, moves_a, moves_b):
    """
    Full heuristic combining position, pressure, clustering, and game-phase weighting.

    This heuristic accounts for:
    - Positional weights (central control).
    - Local pressure (adjacent enemy threats).
    - Clustering bonus (allied pieces grouped together are harder to convert).
    - Game-phase adaptation (piece count bonus increases as the board fills up).

    Args:
        board:   Flat tuple of 49 elements.
        moves_a: Number of legal moves available to player A.
        moves_b: Number of legal moves available to player B.

    Returns:
        Numeric score from Player A's perspective.
    """
    p_a = p_b = 0
    score = 0

    for idx in range(49):
        cell = board[idx]
        if cell == 0:
            continue

        if cell == 1:
            p_a += 1
        else:
            p_b += 1

        enemy = -cell
        enemy_count = 0
        ally_count = 0

        for nb_idx in _NEIGHBORS[idx]:
            nb = board[nb_idx]
            if nb == enemy:
                enemy_count += 1
            elif nb == cell:
                ally_count += 1

        w = WEIGHTS[idx]
        # Pressure penalty is amplified when surrounded by 3+ enemies.
        pressure = enemy_count - (5 if enemy_count >= 3 else 0)
        clustering = ally_count * 0.5

        if cell == 1:
            score += w + pressure + clustering
        else:
            score -= w + pressure + clustering

    if p_a == 0:
        return -9999
    if p_b == 0:
        return 9999

    empty_cells = 49 - p_a - p_b

    # Adapt weights based on game phase (no mobility bonus for fairness).
    if empty_cells > 20:
        # Opening: position and clustering matter.
        pass
    elif empty_cells > 10:
        # Mid-game: balance position and piece count.
        score += 5 * (p_a - p_b)
    else:
        # End-game: piece count dominates.
        score += 10 * (p_a - p_b)

    return score