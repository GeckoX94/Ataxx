"""
test/test_rules.py

Unit tests for Ataxx game rules.

Covers: board creation, move generation, move application, piece conversion,
end-of-game detection, piece counting, and board conversion helpers.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from game.board import create_board
from game.rules import (
    get_valid_moves, apply_move, is_valid_move,
    count_valid_moves, BOARD_SIZE, board_to_flat, flat_to_board,
)


def empty_board():
    """Return an empty flat board (49 zeros)."""
    return tuple([0] * 49)


def place(board, pieces):
    """
    Place pieces on a flat board tuple.

    Args:
        board:  Flat tuple of 49 elements.
        pieces: Dict mapping (row, col) to player value (1 or -1).

    Returns:
        New flat tuple with the pieces placed.
    """
    lst = list(board)
    for (i, j), val in pieces.items():
        lst[i * 7 + j] = val
    return tuple(lst)


class TestCreateBoard(unittest.TestCase):
    """Board creation."""

    def test_type_is_tuple(self):
        self.assertIsInstance(create_board(), tuple)

    def test_size(self):
        self.assertEqual(len(create_board()), 49)

    def test_initial_pieces(self):
        board = create_board()
        # Player A at (0,0) and (6,6).
        self.assertEqual(board[0 * 7 + 0], 1)
        self.assertEqual(board[6 * 7 + 6], 1)
        # Player B at (0,6) and (6,0).
        self.assertEqual(board[0 * 7 + 6], -1)
        self.assertEqual(board[6 * 7 + 0], -1)

    def test_initial_counts(self):
        board = create_board()
        self.assertEqual(board.count(1), 2)
        self.assertEqual(board.count(-1), 2)
        self.assertEqual(board.count(0), 45)

    def test_board_immutable(self):
        board = create_board()
        with self.assertRaises(TypeError):
            board[0] = 99


class TestGetValidMoves(unittest.TestCase):
    """Move generation."""

    def test_initial_moves_count(self):
        """Each player has exactly 16 moves from the starting position."""
        board = create_board()
        self.assertEqual(len(get_valid_moves(board, 1)), 16)
        self.assertEqual(len(get_valid_moves(board, -1)), 16)

    def test_no_duplicates(self):
        """No move should appear twice in the returned list."""
        board = create_board()
        for player in [1, -1]:
            moves = get_valid_moves(board, player)
            self.assertEqual(len(moves), len(set(moves)),
                             f"Duplicate moves detected for player {player}")

    def test_no_moves_when_no_pieces(self):
        """A player with no pieces has no moves."""
        board = empty_board()
        board = place(board, {(0, 0): -1})
        self.assertEqual(get_valid_moves(board, 1), [])

    def test_moves_land_on_empty_cells(self):
        """All move destinations must be empty cells."""
        board = create_board()
        for player in [1, -1]:
            for (_, (nx, ny)) in get_valid_moves(board, player):
                self.assertEqual(board[nx * 7 + ny], 0,
                                 f"Move targets occupied cell ({nx}, {ny})")

    def test_moves_stay_in_bounds(self):
        """All move coordinates must be within the 7x7 grid."""
        board = create_board()
        for player in [1, -1]:
            for ((x1, y1), (x2, y2)) in get_valid_moves(board, player):
                for coord in [x1, y1, x2, y2]:
                    self.assertIn(coord, range(7))

    def test_chebyshev_distance_at_most_2(self):
        """All moves must have a Chebyshev distance of at most 2."""
        board = create_board()
        for player in [1, -1]:
            for ((x1, y1), (x2, y2)) in get_valid_moves(board, player):
                dist = max(abs(x2 - x1), abs(y2 - y1))
                self.assertLessEqual(dist, 2,
                                     f"Move distance {dist} exceeds 2: ({x1},{y1}) -> ({x2},{y2})")

    def test_source_belongs_to_player(self):
        """The source cell of every move must belong to the active player."""
        board = create_board()
        for player in [1, -1]:
            for ((x1, y1), _) in get_valid_moves(board, player):
                self.assertEqual(board[x1 * 7 + y1], player)


class TestApplyMove(unittest.TestCase):
    """Move application."""

    def test_duplication_distance_1(self):
        """Distance-1 move: source cell keeps its piece."""
        board = place(empty_board(), {(3, 3): 1})
        new_board = apply_move(board, ((3, 3), (3, 4)), 1)
        self.assertEqual(new_board[3 * 7 + 3], 1)
        self.assertEqual(new_board[3 * 7 + 4], 1)

    def test_jump_distance_2(self):
        """Distance-2 move: source cell is cleared."""
        board = place(empty_board(), {(3, 3): 1})
        new_board = apply_move(board, ((3, 3), (3, 5)), 1)
        self.assertEqual(new_board[3 * 7 + 3], 0)
        self.assertEqual(new_board[3 * 7 + 5], 1)

    def test_conversion_of_adjacent_enemies(self):
        """After a move, all enemy pieces adjacent to the destination are converted."""
        board = place(empty_board(), {
            (3, 3): 1,
            (3, 4): -1,
            (2, 4): -1,
            (4, 4): -1,
        })
        new_board = apply_move(board, ((3, 3), (3, 4)), 1)
        self.assertEqual(new_board[3 * 7 + 4], 1)
        self.assertEqual(new_board[2 * 7 + 4], 1)
        self.assertEqual(new_board[4 * 7 + 4], 1)

    def test_no_conversion_of_non_adjacent_enemies(self):
        """Enemy pieces not adjacent to the destination are not converted."""
        board = place(empty_board(), {(0, 0): 1, (6, 6): -1})
        new_board = apply_move(board, ((0, 0), (0, 1)), 1)
        self.assertEqual(new_board[6 * 7 + 6], -1)

    def test_returns_new_tuple(self):
        """apply_move does not modify the original board."""
        board = create_board()
        original = board
        moves = get_valid_moves(board, 1)
        new_board = apply_move(board, moves[0], 1)
        self.assertEqual(board, original)
        self.assertIsInstance(new_board, tuple)

    def test_piece_count_after_duplication(self):
        """Distance-1 move: the active player gains one piece."""
        board = place(empty_board(), {(3, 3): 1})
        new_board = apply_move(board, ((3, 3), (3, 4)), 1)
        self.assertEqual(new_board.count(1), 2)

    def test_piece_count_after_jump(self):
        """Distance-2 move: the active player's piece count stays the same."""
        board = place(empty_board(), {(3, 3): 1})
        new_board = apply_move(board, ((3, 3), (3, 5)), 1)
        self.assertEqual(new_board.count(1), 1)

    def test_apply_none_raises(self):
        """apply_move with move=None raises a ValueError."""
        board = create_board()
        with self.assertRaises(ValueError):
            apply_move(board, None, 1)


class TestIsValidMove(unittest.TestCase):
    """Move validation."""

    def test_valid_duplication(self):
        board = place(empty_board(), {(3, 3): 1})
        self.assertTrue(is_valid_move(board, ((3, 3), (3, 4)), 1))

    def test_invalid_wrong_player(self):
        board = place(empty_board(), {(3, 3): -1})
        self.assertFalse(is_valid_move(board, ((3, 3), (3, 4)), 1))

    def test_invalid_destination_occupied(self):
        board = place(empty_board(), {(3, 3): 1, (3, 4): -1})
        self.assertFalse(is_valid_move(board, ((3, 3), (3, 4)), 1))

    def test_invalid_distance_3(self):
        board = place(empty_board(), {(0, 0): 1})
        self.assertFalse(is_valid_move(board, ((0, 0), (0, 3)), 1))


class TestEndGame(unittest.TestCase):
    """End-of-game detection."""

    def test_no_pieces_means_no_moves(self):
        """A player with no pieces returns an empty move list."""
        board = place(empty_board(), {(3, 3): -1})
        self.assertEqual(get_valid_moves(board, 1), [])

    def test_both_players_have_moves_at_start(self):
        """From the starting position, both players have available moves."""
        board = create_board()
        self.assertGreater(len(get_valid_moves(board, 1)), 0)
        self.assertGreater(len(get_valid_moves(board, -1)), 0)

    def test_full_board_no_moves(self):
        """A completely filled board leaves no moves for either player."""
        board = tuple([1 if i < 25 else -1 for i in range(49)])
        self.assertEqual(get_valid_moves(board, 1), [])
        self.assertEqual(get_valid_moves(board, -1), [])


class TestCountValidMoves(unittest.TestCase):
    """Move counting."""

    def test_count_positive_when_moves_exist(self):
        """count_valid_moves returns a positive value when moves are available."""
        board = create_board()
        for player in [1, -1]:
            if len(get_valid_moves(board, player)) > 0:
                self.assertGreater(count_valid_moves(board, player), 0)

    def test_count_zero_when_no_pieces(self):
        """count_valid_moves returns 0 when the player has no pieces."""
        self.assertEqual(count_valid_moves(empty_board(), 1), 0)


class TestBoardConversions(unittest.TestCase):
    """Board format conversion helpers."""

    def test_roundtrip_flat_to_list_to_flat(self):
        """Converting to list-of-lists and back produces the original tuple."""
        board = create_board()
        self.assertEqual(board, board_to_flat(flat_to_board(board)))

    def test_list_values_match_flat(self):
        """The list-of-lists representation has the correct values at key positions."""
        board = create_board()
        as_list = flat_to_board(board)
        self.assertEqual(as_list[0][0], 1)
        self.assertEqual(as_list[0][6], -1)
        self.assertEqual(as_list[6][0], -1)
        self.assertEqual(as_list[6][6], 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
