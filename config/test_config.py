"""
config/test_config.py

Predefined player configurations for the evaluation interface.
Edit these functions to quickly switch between configurations without
going through the interactive setup each time.
"""


def get_test_matchup():
    """
    Standard test matchup: strong Alpha-Beta vs weaker Alpha-Beta.

    Returns:
        Dict mapping player value (1 / -1) to configuration dict.
    """
    return {
        1:  {"type": "ai", "algo": "alphabeta", "depth": 4, "heuristic": "v4"},
        -1: {"type": "ai", "algo": "alphabeta", "depth": 3, "heuristic": "v2"},
    }


def get_depth_comparison():
    """
    Depth comparison: maximum depth vs minimum depth at the same heuristic.

    Returns:
        Dict mapping player value (1 / -1) to configuration dict.
    """
    return {
        1:  {"type": "ai", "algo": "alphabeta", "depth": 6, "heuristic": "v4"},
        -1: {"type": "ai", "algo": "alphabeta", "depth": 2, "heuristic": "v1"},
    }


def get_minimax_vs_alphabeta():
    """
    Algorithm comparison: Minimax vs Alpha-Beta at equal depth and heuristic.

    Returns:
        Dict mapping player value (1 / -1) to configuration dict.
    """
    return {
        1:  {"type": "ai", "algo": "minimax",   "depth": 4, "heuristic": "v3"},
        -1: {"type": "ai", "algo": "alphabeta", "depth": 4, "heuristic": "v3"},
    }
