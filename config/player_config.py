"""
config/player_config.py

Interactive player configuration for the evaluation interface.
Prompts the user to choose between a human player and an AI, and if AI is
selected, to configure the algorithm, search depth, and heuristic version.
"""


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
    choice = int(input("Choice: "))

    if choice == 1:
        return {"type": "human"}

    config = {"type": "ai"}

    print("Algorithm:")
    print("1 - Minimax")
    print("2 - Alpha-Beta")
    algo_choice = int(input("Choice: "))

    config["algo"] = "alphabeta" if algo_choice == 2 else "minimax"

    min_depth, max_depth = (1, 7) if config["algo"] == "alphabeta" else (1, 3)

    while True:
        try:
            depth = int(input(f"Depth ({min_depth} to {max_depth}): "))
            if min_depth <= depth <= max_depth:
                config["depth"] = depth
                break
            else:
                print(f"Please enter a value between {min_depth} and {max_depth}.")
        except ValueError:
            print("Invalid input, please enter an integer.")

    print("Heuristic:")
    print("1 - v1")
    print("2 - v2")
    print("3 - v3")
    print("4 - v4")
    h = int(input("Choice: "))
    config["heuristic"] = f"v{h}"

    return config
