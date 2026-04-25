# Ataxx 7x7

Implementation of the **Ataxx 7x7** board game in Python with multiple AI difficulty levels and a tournament system.

## Table of contents

- [About](#about)
- [Rules of Ataxx](#rules-of-ataxx)
- [Installation](#installation)
- [Usage](#usage)
- [Difficulty levels](#difficulty-levels)
- [Project structure](#project-structure)
- [Algorithms](#algorithms)
- [Tournament](#tournament)
- [Tests](#tests)

---

## About

Ataxx is a two-player combinatorial strategy game played on a 7x7 grid. Players expand their territory by cloning pieces to adjacent cells or jumping to cells two steps away, converting all neighbouring enemy pieces in the process. The player with the most pieces when the game ends wins.

This implementation provides:

- A complete game engine with rule validation
- Three AI difficulty levels built on Minimax with heuristic evaluation
- An additional Alpha-Beta algorithm with Iterative Deepening (available in `evaluation.py`)
- Four progressive evaluation heuristics (v1 to v4)
- A tournament system with statistics, CSV export, and charts
- A full unit test suite

---

## Rules of Ataxx

### Starting position

The board starts empty except for four corner pieces:
- **Player A** occupies corners (0,0) and (6,6).
- **Player B** occupies corners (0,6) and (6,0).

### Moves

On each turn a player performs exactly one move:

1. **Clone** (distance 1): place a new piece on any empty cell adjacent to an existing piece. The original piece stays.
2. **Jump** (distance 2): move an existing piece to an empty cell exactly two steps away (Chebyshev distance). The original cell is vacated.

### Conversion

After every move, all enemy pieces adjacent to the destination cell are converted to the active player's colour.

### End of game

The game ends when:
- One player has no pieces left (immediate loss for that player), or
- Neither player can move for two consecutive turns, or
- The board is completely filled.

The player with the most pieces wins. Ties are possible.

---

## Installation

### Requirements

- Python 3.8 or higher

### Dependencies

No external dependency is required to play the game. For tournament charts:

```bash
pip install matplotlib numpy
```

---

## Usage

### Launch the main interface

```bash
python3 Ataxx.py
```

This is the clean, presentation-ready entry point. It offers:
- **AI vs AI**: choose a difficulty level for each player and watch them play.
- **Player vs AI**: play against an AI of your choice.

### Launch the modular evaluation interface

```bash
python3 evaluation.py
```

Used for development and report generation. Supports full manual configuration of both players (algorithm, depth, heuristic) and two display modes:
- `tech`: shows algorithm details and per-move timing.
- `clean`: minimal output.

---

## Difficulty levels

| Level  | Algorithm | Depth | Heuristic |
|--------|-----------|-------|-----------|
| Easy   | Minimax   | 2     | v2        |
| Medium | Minimax   | 3     | v3        |
| Hard   | Minimax   | 4     | v4        |

---

## Project structure

```
Ataxx/
├── Ataxx.py                   # Main entry point
├── evaluation.py              # Modular interface for testing and development
├── COMMANDS.md                # Command reference
├── README.md
├── algorithme/
│   ├── __init__.py
│   ├── minimax.py             # Minimax with transposition table
│   ├── alphabeta.py           # Minimax + Alpha-Beta + Iterative Deepening
│   └── heuristics.py          # Heuristics v1 to v4
├── config/
│   ├── __init__.py
│   ├── player_config.py       # Interactive player setup
│   ├── test_config.py         # Predefined matchup configurations
│   └── ui_config.py           # Display mode prompts
├── game/
│   ├── __init__.py
│   ├── board.py               # Board creation and display
│   └── rules.py               # Rules / score
├── tournament/
│   ├── __init__.py
│   ├── engine.py              # Tournament engine
│   └── run_tournament.py      # Tournament launcher
├── test/
│   ├── __init__.py
│   └── test_rules.py          # Unit tests
└── utils/
    ├── __init__.py
    ├── cache_key.py           # Zobrist hashing and transposition table
    ├── random_ai.py           # Random baseline player
    └── timer.py               # Per-move timing
```

---

## Algorithms

### Minimax

Exhaustive tree search with transposition table caching.

- Alternates between maximising (Player A) and minimising (Player B) at each level.
- Moves are pre-sorted by a shallow heuristic evaluation to improve cache efficiency.
- Results are stored in a transposition table to avoid re-evaluating identical positions.

File: [`algorithme/minimax.py`](algorithme/minimax.py)

### Alpha-Beta with Iterative Deepening

Advanced optimisations built on top of Minimax:

- **Alpha-Beta pruning**: skips branches that cannot affect the final result.
- **Iterative Deepening**: searches at depth 1, 2, ..., max_depth in sequence. Each pass fills the transposition table and improves move ordering for the next.
- **Killer moves**: moves that recently caused a beta cut-off are tried first at the same depth in sibling nodes.
- **Move ordering**: non-killer moves are sorted by quick heuristic evaluation before the recursive call.

File: [`algorithme/alphabeta.py`](algorithme/alphabeta.py)

### Heuristics

Four progressive evaluation functions, each building on the previous:

| Version | Description |
|---------|-------------|
| v1 | Piece difference + mobility bonus |
| v2 | v1 + positional weights (central control) |
| v3 | v2 + local pressure (adjacent enemy threats) |
| v4 | v3 + clustering bonus + game-phase weighting |

File: [`algorithme/heuristics.py`](algorithme/heuristics.py)

---

## Tournament

### Quick tournament (5 games per matchup)

```bash
python3 tournament/run_tournament.py --quick
```

### Full tournament (50 games per matchup)

```bash
python3 tournament/run_tournament.py --full
```

### Custom number of games

```bash
python3 tournament/run_tournament.py --games 20
```

### Matchups

The tournament runs the following matchups in order:

1. **Random vs Easy** — demonstrates that Minimax beats random play.
2. **Easy vs Medium**
3. **Medium vs Hard**
4. **Easy vs Hard** — maximum difficulty gap.

### Outputs

- Console summary table with win rates and average scores.
- `tournament_results.csv` — detailed per-matchup data.
- `tournament_results.png` — bar charts of win rates and average scores.
- `tournament_convergence.png` — Monte Carlo convergence of cumulative scores.

---

## Tests

### Run all tests

```bash
python3 -m pytest test/test_rules.py -v
```

### Run a specific test class

```bash
python3 -m pytest test/test_rules.py::TestApplyMove -v
```

### Compact output

```bash
python3 -m pytest test/test_rules.py -v --tb=short
```

The test suite covers: board creation, move generation, move application, piece conversion, end-of-game detection, piece counting, and board format conversions.
