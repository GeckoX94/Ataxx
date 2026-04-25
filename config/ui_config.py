"""
config/ui_config.py

User interface prompts for the evaluation interface.
"""


def ask_game_mode():
    """
    Ask the user to choose the game mode.

    Returns:
        '1' for manual configuration, '2' for automatic test configuration.
    """
    print("1 - Manual")
    print("2 - Test (auto)")
    return input("Choice: ").strip()


def ask_display_mode():
    """
    Ask the user to choose the display mode.

    Returns:
        'tech' for detailed output or 'clean' for minimal output.
    """
    return input("Display mode (tech / clean): ").strip().lower()
