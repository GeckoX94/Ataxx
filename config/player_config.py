"""
config/player_config.py

Interactive player configuration for the evaluation interface.
Prompts the user to choose between a human player and an AI, and if AI is
selected, to configure the algorithm, search depth, and heuristic version.
"""


def _ask_int(prompt, valid_range=None):
    """
    Prompt the user for an integer, retrying on invalid input.

    Args:
        prompt:      Text shown to the user.
        valid_range: Optional (min, max) tuple; retries if value is out of range.

    Returns:
        Valid integer entered by the user.
    """
    while True:
        try:
            value = int(input(prompt))
            if valid_range is None or valid_range[0] <= value <= valid_range[1]:
                return value
            print(f"Please enter a value between {valid_range[0]} and {valid_range[1]}.")
        except ValueError:
            print("Invalid input, please enter an integer.")


def setup_player(player_id):
    """
    Interactively configure a player.

    Args:
        player_id: Display identifier (e.g., 'A' or 'B').

    Returns:
        Configuration dict with keys 'type', and optionally 'algo', 'depth', 'heuristic'.
    """
    print(f"\n--- Player {player_id} configuration ---")

    print("1 - Human")
    print("2 - AI")
    choice = _ask_int("Choice: ", (1, 2))

    if choice == 1:
        return {"type": "human"}

    config = {"type": "ai"}

    print("Algorithm:")
    print("1 - Minimax")
    print("2 - Alpha-Beta")
    algo_choice = _ask_int("Choice: ", (1, 2))

    config["algo"] = "alphabeta" if algo_choice == 2 else "minimax"

    min_depth, max_depth = 1, 7

    depth = _ask_int(f"Depth ({min_depth} to {max_depth}): ", (min_depth, max_depth))
    config["depth"] = depth

    print("Heuristic:")
    print("1 - v1")
    print("2 - v2")
    print("3 - v3")
    print("4 - v4")
    h = _ask_int("Choice: ", (1, 4))
    config["heuristic"] = f"v{h}"

    return config