"""
game/board.py

Board creation and display utilities for Ataxx.
The board is stored as a flat tuple of 49 elements (7x7 grid).
Player A = 1 (displayed as 'A'), Player B = -1 (displayed as 'B'), empty = 0 (displayed as '.').
"""

from .rules import board_to_flat


def create_board():
    """
    Create the initial Ataxx 7x7 board as a flat tuple of 49 elements.

    Starting positions:
        Player A (1)  at corners (0, 0) and (6, 6).
        Player B (-1) at corners (0, 6) and (6, 0).

    Returns:
        Flat tuple of 49 integers.
    """
    lst = [0] * 49
    lst[0 * 7 + 0] = 1    # (0, 0) -> Player A
    lst[6 * 7 + 6] = 1    # (6, 6) -> Player A
    lst[0 * 7 + 6] = -1   # (0, 6) -> Player B
    lst[6 * 7 + 0] = -1   # (6, 0) -> Player B
    return tuple(lst)


def print_board(board):
    """
    Print the board to stdout.

    Accepts either a flat tuple or a list-of-lists as input.
    Cells are displayed as 'A' (Player A), 'B' (Player B), or '.' (empty).

    Args:
        board: Board state (flat tuple or list-of-lists).
    """
    flat = board if isinstance(board, tuple) else board_to_flat(board)

    print("  0 1 2 3 4 5 6")
    for i in range(7):
        print(f"{i}", end=" ")
        for j in range(7):
            cell = flat[i * 7 + j]
            if cell == 1:
                print("A", end=" ")
            elif cell == -1:
                print("B", end=" ")
            else:
                print(".", end=" ")
        print()
    print()
