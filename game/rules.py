"""
game/rules.py

Core rules for Ataxx: move generation, move application, and board utilities.
The board is represented as a flat tuple of 49 elements (7x7 grid).
Player A = 1, Player B = -1, empty = 0.
"""

BOARD_SIZE = 7

# All directions reachable in one move (Chebyshev distance <= 2, excluding origin).
DIRECTIONS = [
    (dx, dy)
    for dx in range(-2, 3)
    for dy in range(-2, 3)
    if not (dx == 0 and dy == 0)
]

# Adjacent directions only (distance 1), used for piece conversion after a move.
ADJ_DIRECTIONS = [
    (dx, dy)
    for dx in range(-1, 2)
    for dy in range(-1, 2)
    if not (dx == 0 and dy == 0)
]


def board_to_flat(board):
    """Convert a list-of-lists board to a flat 49-element tuple."""
    return tuple(c for row in board for c in row)


def flat_to_board(flat):
    """Convert a flat 49-element tuple to a list-of-lists (for display)."""
    return [list(flat[i * 7:(i + 1) * 7]) for i in range(7)]


def get_valid_moves(board, player):
    """
    Return all legal moves for the given player.

    Accepts either a list-of-lists or a flat tuple as input.
    Uses a set internally to deduplicate moves (a destination cell may be
    reachable from several of the player's pieces).

    Args:
        board:  Board state (flat tuple or list-of-lists).
        player: Active player (1 or -1).

    Returns:
        List of moves, each move being a pair ((x1, y1), (x2, y2)).
    """
    flat = board if isinstance(board, tuple) else board_to_flat(board)

    moves_set = set()
    for x in range(BOARD_SIZE):
        base = x * BOARD_SIZE
        for y in range(BOARD_SIZE):
            if flat[base + y] != player:
                continue
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                    if flat[nx * BOARD_SIZE + ny] == 0:
                        moves_set.add(((x, y), (nx, ny)))

    return list(moves_set)


def apply_move(board, move, player):
    """
    Apply a move and return the resulting board as a flat tuple.

    Distance 1 -> duplication: the source cell keeps its piece.
    Distance 2 -> jump: the source cell is cleared.
    After placement, all enemy pieces adjacent to the destination are converted.

    The returned tuple is immutable and directly usable as a transposition table key.

    Args:
        board:  Current board state (flat tuple or list-of-lists).
        move:   Move to apply as ((x1, y1), (x2, y2)).
        player: Active player (1 or -1).

    Returns:
        New board state as a flat tuple.

    Raises:
        ValueError: If move is None.
    """
    if move is None:
        raise ValueError("apply_move called with move=None")

    lst = list(board) if isinstance(board, tuple) else [c for row in board for c in row]

    (x1, y1), (x2, y2) = move

    # Jump (distance 2): clear source cell.
    if max(abs(x2 - x1), abs(y2 - y1)) == 2:
        lst[x1 * BOARD_SIZE + y1] = 0

    lst[x2 * BOARD_SIZE + y2] = player

    # Convert all adjacent enemy pieces.
    enemy = -player
    for ddx, ddy in ADJ_DIRECTIONS:
        nx, ny = x2 + ddx, y2 + ddy
        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            idx = nx * BOARD_SIZE + ny
            if lst[idx] == enemy:
                lst[idx] = player

    return tuple(lst)


def is_valid_move(board, move, player):
    """
    Check whether a move is legal for the given player.

    Args:
        board:  Board state (flat tuple or list-of-lists).
        move:   Move to check as ((x1, y1), (x2, y2)).
        player: Active player (1 or -1).

    Returns:
        True if the move is legal, False otherwise.
    """
    (x1, y1), (x2, y2) = move
    flat = board if isinstance(board, tuple) else board_to_flat(board)

    if flat[x1 * BOARD_SIZE + y1] != player:
        return False
    if flat[x2 * BOARD_SIZE + y2] != 0:
        return False
    if max(abs(x2 - x1), abs(y2 - y1)) > 2:
        return False
    return True


def count_valid_moves(board, player):
    """
    Fast approximate move count (utility / debugging helper).

    Counts reachable empty cells without deduplication — a destination reachable
    from two different pieces is counted twice. Faster than get_valid_moves() but
    only suitable for rough estimates; use len(get_valid_moves(...)) for exact counts.

    Args:
        board:  Board state (flat tuple or list-of-lists).
        player: Active player (1 or -1).

    Returns:
        Integer count of reachable empty cells (may overcount).
    """
    flat = board if isinstance(board, tuple) else board_to_flat(board)

    count = 0
    for x in range(BOARD_SIZE):
        base = x * BOARD_SIZE
        for y in range(BOARD_SIZE):
            if flat[base + y] != player:
                continue
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                    if flat[nx * BOARD_SIZE + ny] == 0:
                        count += 1
    return count