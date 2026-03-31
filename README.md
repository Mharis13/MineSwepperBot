# MineSwepperBot 🤖💣

A **TAS-style Minesweeper solver** written in pure Python that plays Minesweeper
as fast as possible using constraint-based deduction with a probabilistic fallback.

## Features

- **Constraint solver** — derives safe cells and mines from the number
  constraints on the board using subset/difference reduction (no guessing when
  a deterministic move exists).
- **Probabilistic fallback** — when no deterministic move is available, picks
  the cell with the lowest estimated mine probability.
- **First-click safety** — mines are placed *after* the first click so the
  opening is always mine-free (3×3 safe zone).
- **Flood-fill reveal** — zero-adjacency cells open up a region automatically,
  just like a real game.
- **Chord clicks** — satisfied number cells reveal all remaining hidden
  neighbours in one action.
- **Batch mode** — run thousands of games and collect statistics (win rate,
  average time, best time, efficiency).
- **Coloured board display** — ANSI-coloured board rendered in the terminal.
- **No external dependencies** — pure Python standard library (pytest for tests).

## Win rates (seed=0)

| Difficulty | Board | Mines | Win rate |
|---|---|---|---|
| Beginner | 9×9 | 10 | ~95 % |
| Intermediate | 16×16 | 40 | ~80 % |
| Expert | 16×30 | 99 | ~22 % |

## Usage

```bash
# Install test dependency (optional)
pip install -r requirements.txt

# Single Expert game with verbose move log
python main.py --difficulty expert --verbose

# 500 Intermediate games with statistics
python main.py --difficulty intermediate --games 500

# Beginner game with board displayed after each move
python main.py --difficulty beginner --display

# Custom board (20×30, 120 mines), 100 games, fixed seed
python main.py --custom 20 30 120 --games 100 --seed 42

# Run tests
python -m pytest tests/ -v
```

## Project structure

```
MineSwepperBot/
├── minesweeper/
│   ├── __init__.py      # Public API
│   ├── game.py          # Game engine (board, cells, reveal, flag, chord)
│   ├── solver.py        # Constraint-based solver + probabilistic fallback
│   ├── bot.py           # Bot orchestration and statistics
│   └── display.py       # ANSI terminal renderer
├── tests/
│   ├── test_game.py     # Game engine unit tests
│   └── test_solver.py   # Solver unit tests
├── main.py              # CLI entry point
└── requirements.txt
```

## Algorithm

1. **Extract constraints** — each revealed number cell with hidden neighbours
   produces a constraint `{cells} → k mines`.
2. **Trivial deduction** — if `k == 0` all cells are safe; if `k == |cells|`
   all cells are mines.
3. **Subset reduction** — when one constraint's cell-set is a subset of
   another's, a new reduced constraint is derived, yielding further deductions.
4. **Probabilistic guess** — when stuck, estimate each hidden cell's mine
   probability (frontier cells via constraint averages, non-frontier via global
   density) and click the safest option.

