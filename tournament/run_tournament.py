"""
tournament/run_tournament.py

Full tournament runner between all AI difficulty levels.

Usage:
    python3 tournament/run_tournament.py           # 50 games per matchup (default)
    python3 tournament/run_tournament.py --quick   # 5 games per matchup
    python3 tournament/run_tournament.py --full    # 50 games per matchup
    python3 tournament/run_tournament.py --games N # N games per matchup

Outputs:
    - Console summary table
    - tournament_results.csv
    - tournament_results.png  (win rates and average scores)
    - tournament_convergence.png  (Monte Carlo convergence of cumulative scores)
"""

import sys
import os
import argparse
import time
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tournament.engine import run_matchup, print_stats

try:
    import matplotlib.pyplot as plt  # type: ignore
    import numpy as np  # type: ignore
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def save_stats_to_csv(all_stats, output_file="tournament_results.csv"):
    """
    Save tournament statistics to a CSV file.

    Args:
        all_stats:   List of stats dicts returned by run_matchup.
        output_file: Output file path.
    """
    if not all_stats:
        return

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Matchup', 'Games', 'Wins_P1', 'Wins_P2', 'Draws',
            'WinRate_P1', 'WinRate_P2', 'AvgScore_P1', 'AvgScore_P2',
            'AvgTime_s', 'AvgMoves',
        ])
        writer.writeheader()

        for s in all_stats:
            writer.writerow({
                'Matchup':     f"{s['name1']} vs {s['name2']}",
                'Games':       s['n_games'],
                'Wins_P1':     s['wins1'],
                'Wins_P2':     s['wins2'],
                'Draws':       s['draws'],
                'WinRate_P1':  f"{s['win_rate1']:.1f}%",
                'WinRate_P2':  f"{s['win_rate2']:.1f}%",
                'AvgScore_P1': f"{s['avg_score1']:.1f}",
                'AvgScore_P2': f"{s['avg_score2']:.1f}",
                'AvgTime_s':   f"{s['avg_time']:.1f}",
                'AvgMoves':    f"{s['avg_moves']:.1f}",
            })

    print(f"\n  Results saved to: {output_file}")


def plot_results(all_stats):
    """
    Generate and save result charts.

    Chart 1: Win rates and average scores per matchup (bar chart).
    Chart 2: Cumulative average score convergence (Monte Carlo illustration).

    Args:
        all_stats: List of stats dicts returned by run_matchup.
    """
    if not HAS_MATPLOTLIB or not all_stats:
        return

    matchups = [f"{s['name1']}\nvs\n{s['name2']}" for s in all_stats]
    win_rates_1 = [s['win_rate1'] for s in all_stats]
    win_rates_2 = [s['win_rate2'] for s in all_stats]
    x = range(len(matchups))
    width = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Win rates.
    axes[0].bar([i - width / 2 for i in x], win_rates_1, width, label='Player 1', color='#2E86AB')
    axes[0].bar([i + width / 2 for i in x], win_rates_2, width, label='Player 2', color='#A23B72')
    axes[0].set_ylabel('Win rate (%)')
    axes[0].set_title('Win rates per matchup')
    axes[0].set_xticks(list(x))
    axes[0].set_xticklabels(matchups, fontsize=9)
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.3)
    axes[0].set_ylim(0, 100)

    # Average scores.
    scores_1 = [s['avg_score1'] for s in all_stats]
    scores_2 = [s['avg_score2'] for s in all_stats]
    axes[1].bar([i - width / 2 for i in x], scores_1, width, label='Player 1', color='#2E86AB')
    axes[1].bar([i + width / 2 for i in x], scores_2, width, label='Player 2', color='#A23B72')
    axes[1].set_ylabel('Average score')
    axes[1].set_title('Average scores per matchup')
    axes[1].set_xticks(list(x))
    axes[1].set_xticklabels(matchups, fontsize=9)
    axes[1].legend()
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig('tournament_results.png', dpi=100, bbox_inches='tight')
    print("  Chart saved to: tournament_results.png")

    # Convergence chart (Monte Carlo cumulative average).
    if all_stats and 'scores1' in all_stats[0]:
        fig2, ax = plt.subplots(figsize=(10, 6))

        for stats in all_stats[:4]:
            cumsum = np.cumsum(stats['scores1'])
            count = np.arange(1, len(stats['scores1']) + 1)
            cumulative_avg = cumsum / count
            ax.plot(
                count, cumulative_avg,
                marker='o', markersize=4, alpha=0.7,
                label=f"{stats['name1']} vs {stats['name2']}"
            )

        ax.set_xlabel('Game number')
        ax.set_ylabel('Cumulative average score (Player 1)')
        ax.set_title('Score convergence (Monte Carlo)')
        ax.legend()
        ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig('tournament_convergence.png', dpi=100, bbox_inches='tight')
        print("  Convergence chart saved to: tournament_convergence.png")


def main():
    parser = argparse.ArgumentParser(description="Ataxx Tournament")
    parser.add_argument("--quick",  action="store_true", help="5 games per matchup")
    parser.add_argument("--full",   action="store_true", help="50 games per matchup (default)")
    parser.add_argument("--games",  type=int, default=None, help="Custom number of games")
    args = parser.parse_args()

    if args.games:
        n = args.games
    elif args.quick:
        n = 5
    else:
        n = 50

    # Matchups: progress from weakest to strongest to tell a clear story.
    matchups = [
        ("Random", "Easy"),     # Show that Easy > Random (search beats random play).
        ("Easy",   "Medium"),
        ("Medium", "Hard"),
        ("Easy",   "Hard"),     # Maximum gap for illustration.
    ]

    print(f"\n{'#' * 60}")
    print(f"#  ATAXX TOURNAMENT -> {n} games per matchup")
    print(f"#  {len(matchups)} matchup(s) total")
    print(f"{'#' * 60}\n")

    t_global = time.time()
    all_stats = []

    for name1, name2 in matchups:
        stats = run_matchup(name1, name2, n_games=n, verbose=True)
        print_stats(stats)
        all_stats.append(stats)

    total = time.time() - t_global

    # Global summary table.
    print(f"\n{'#' * 60}")
    print(f"#  SUMMARY")
    print(f"{'#' * 60}\n")
    print(f"  {'Matchup':<35} {'W.P1':>5} {'W.P2':>5} {'Draw':>5} {'%P1':>7} {'Time':>7}")
    print(f"  {'-' * 35} {'-' * 5} {'-' * 5} {'-' * 5} {'-' * 7} {'-' * 7}")
    for s in all_stats:
        matchup = f"{s['name1']} vs {s['name2']}"
        print(
            f"  {matchup:<35} {s['wins1']:>5} {s['wins2']:>5} {s['draws']:>5} "
            f"{s['win_rate1']:>6.1f}% {s['avg_time']:>6.1f}s"
        )

    print(f"\n  Total tournament duration: {total:.0f}s ({total / 60:.1f} min)")
    print(f"{'#' * 60}\n")

    save_stats_to_csv(all_stats)
    plot_results(all_stats)


if __name__ == "__main__":
    main()
