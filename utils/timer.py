"""
utils/timer.py

Per-player move timer for Ataxx.
Tracks cumulative time and per-move history for both players.
"""

import time


class Timer:
    """
    Records elapsed time per move for each player.

    Players are identified by their integer value (1 for Player A, -1 for Player B).
    """

    def __init__(self):
        self.times = {1: 0.0, -1: 0.0}
        self.history = {1: [], -1: []}

    def start(self):
        """Return the current timestamp (call before a move computation)."""
        return time.time()

    def stop(self, start_time, player):
        """
        Record elapsed time for a player's move.

        Args:
            start_time: Timestamp returned by start().
            player:     Active player (1 or -1).

        Returns:
            Elapsed time in seconds.
        """
        elapsed = time.time() - start_time
        self.times[player] += elapsed
        self.history[player].append(elapsed)
        return elapsed

    def get_total(self, player):
        """Return the total accumulated time for a player."""
        return self.times[player]

    def get_history(self, player):
        """Return the list of per-move times for a player."""
        return self.history[player]

    def print_results(self):
        """Print total time per player."""
        print("\nTotal time:")
        print(f"  Player A: {self.times[1]:.3f}s")
        print(f"  Player B: {self.times[-1]:.3f}s")

    def print_detailed_stats(self):
        """Print per-player move count, average time, and maximum time."""
        for player in [1, -1]:
            history = self.history[player]
            if history:
                avg = sum(history) / len(history)
                player_name = "A" if player == 1 else "B"
                print(f"\nPlayer {player_name}:")
                print(f"  Moves played : {len(history)}")
                print(f"  Average time : {avg:.3f}s")
                print(f"  Maximum time : {max(history):.3f}s")
