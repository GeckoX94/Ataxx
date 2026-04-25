# Command reference — Ataxx

## Main interface (clean mode)

```bash
python3 Ataxx.py
```

Launches the presentation-ready interface with two game modes and three difficulty levels:

| Level  | Algorithm | Depth | Heuristic |
|--------|-----------|-------|-----------|
| Easy   | Minimax   | 2     | v2        |
| Medium | Minimax   | 3     | v3        |
| Hard   | Minimax   | 4     | v4        |

**Modes:**
- **AI vs AI** — configure a difficulty level for each player and watch the game.
- **Player vs AI** — play as Player A against an AI of your choice.

---

## Modular evaluation interface

```bash
python3 evaluation.py
```

Used for development and report generation. Allows full manual configuration of both players.

**Display modes:**
- `tech` — shows algorithm, depth, heuristic, and per-move timing.
- `clean` — minimal output (board and scores only).

**Game modes (prompted on launch):**
- `1` — Manual: configure each player interactively (type, algorithm, depth, heuristic).
- `2` — Auto: use the predefined matchup from `config/test_config.py`.

To change the auto matchup, edit `config/test_config.py`:

```python
def get_test_matchup():
    return {
        1:  {"type": "ai", "algo": "minimax", "depth": 3, "heuristic": "v3"},
        -1: {"type": "ai", "algo": "minimax", "depth": 2, "heuristic": "v2"},
    }
```

**Available options:**

| Key        | Values                         |
|------------|--------------------------------|
| `type`     | `"ai"` / `"human"`            |
| `algo`     | `"minimax"` / `"alphabeta"`   |
| `depth`    | Integer (1-7 for alphabeta, 1-3 for minimax) |
| `heuristic`| `"v1"` / `"v2"` / `"v3"` / `"v4"` |

---

## Unit tests

```bash
python3 -m pytest test/test_rules.py -v
```

Run all unit tests with verbose output.

```bash
# Compact error display
python3 -m pytest test/test_rules.py -v --tb=short

# Single test class
python3 -m pytest test/test_rules.py::TestApplyMove -v
```

Tests cover: board creation, move generation, move application, piece conversion,
end-of-game detection, piece counting, and board format helpers.

---

## Tournament

### Quick run (5 games per matchup)

```bash
python3 tournament/run_tournament.py --quick
```

### Full run (50 games per matchup)

```bash
python3 tournament/run_tournament.py --full
```

### Custom number of games

```bash
python3 tournament/run_tournament.py --games 20
```

### Matchups

| Matchup            | Purpose                                      |
|--------------------|----------------------------------------------|
| Random vs Easy     | Show that Minimax outperforms random play    |
| Easy vs Medium     |                                              |
| Medium vs Hard     |                                              |
| Easy vs Hard       | Maximum difficulty gap                       |

### Outputs

- Console: per-game results and a final summary table.
- `tournament_results.csv` — full statistics.
- `tournament_results.png` — win rates and average scores (bar charts).
- `tournament_convergence.png` — cumulative average score convergence.

Matplotlib and NumPy are required for chart generation:

```bash
pip install matplotlib numpy
```
