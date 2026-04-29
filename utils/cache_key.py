"""
utils/cache_key.py

Zobrist hashing and transposition table for Ataxx.

The board (flat tuple of 49 elements) is hashed using Zobrist hashing: each
(cell_index, cell_value) pair is XOR-ed with a random 64-bit integer, producing
a compact 64-bit integer key suitable for use as a transposition table key. The transposition
table maps (hash, player) keys to (score, flag, depth) entries.
"""

import random

_rng = random.Random(42)

# Three possible cell values: -1 -> index 0, 0 -> index 1, 1 -> index 2.
_ZOBRIST = tuple(
    tuple(_rng.getrandbits(64) for _ in range(3))
    for _ in range(49)
)


def board_hash(board):
    """
    Compute the Zobrist hash of a flat 49-element board tuple.

    Args:
        board: Flat tuple of 49 integers (-1, 0, or 1).

    Returns:
        64-bit integer hash.
    """
    h = 0
    z = _ZOBRIST
    for i in range(49):
        h ^= z[i][board[i] + 1]
    return h


_transposition_table = {}


def tt_lookup(board, player, depth):
    """
    Look up a position in the transposition table.

    Returns the stored entry only if it was computed at a depth >= the
    requested depth (deeper search -> more reliable score).

    Args:
        board:  Flat tuple of 49 elements.
        player: Active player (1 or -1).
        depth:  Current search depth.

    Returns:
        (score, flag) tuple if a valid entry exists, None otherwise.
    """
    key = (board_hash(board), player)
    entry = _transposition_table.get(key)

    if entry is None:
        return None

    score, flag, stored_depth = entry
    if stored_depth >= depth:
        return score, flag

    return None


def tt_store(board, player, score, flag, depth):
    """
    Store a position evaluation in the transposition table.

    An existing entry is replaced only if the new search depth is greater or equal
    (deeper results are more reliable; equal depth refreshes the stored flag).

    Args:
        board:  Flat tuple of 49 elements.
        player: Active player (1 or -1).
        score:  Evaluation score.
        flag:   Bound type: 'EXACT', 'LOWER', or 'UPPER'.
        depth:  Search depth at which the score was computed.
    """
    key = (board_hash(board), player)
    entry = _transposition_table.get(key)

    if entry is None or depth >= entry[2]:
        _transposition_table[key] = (score, flag, depth)


def clear_all_caches():
    """Clear the transposition table (call between independent games)."""
    _transposition_table.clear()