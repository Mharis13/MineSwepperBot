#!/usr/bin/env python3
"""MineSweeperBot — TAS-style Minesweeper solver.

Usage examples
--------------
# Play one Expert game with verbose output:
    python main.py --difficulty expert --verbose

# Play 500 Intermediate games and print statistics:
    python main.py --difficulty intermediate --games 500

# Custom board (20 rows, 30 cols, 120 mines), 1000 games:
    python main.py --rows 20 --cols 30 --mines 120 --games 1000

# Display the board graphically for a single Beginner game:
    python main.py --difficulty beginner --display
"""

import argparse
import sys

from minesweeper import Bot, Difficulty


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="minesweeper-bot",
        description="TAS-style Minesweeper solver written in Python.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    diff_group = parser.add_mutually_exclusive_group()
    diff_group.add_argument(
        "--difficulty",
        choices=["beginner", "intermediate", "expert"],
        default="expert",
        help="Preset difficulty (default: expert).",
    )
    diff_group.add_argument(
        "--custom",
        nargs=3,
        metavar=("ROWS", "COLS", "MINES"),
        type=int,
        help="Custom board size: ROWS COLS MINES.",
    )

    parser.add_argument(
        "--games",
        type=int,
        default=1,
        metavar="N",
        help="Number of games to play (default: 1).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each move (only useful for a single game).",
    )
    parser.add_argument(
        "--display",
        action="store_true",
        help="Render the board after each move (implies --games 1).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible results.",
    )
    return parser


def resolve_difficulty(args: argparse.Namespace) -> Difficulty:
    if args.custom:
        rows, cols, mines = args.custom
        if mines >= rows * cols:
            print(
                f"Error: too many mines ({mines}) for a {rows}×{cols} board.",
                file=sys.stderr,
            )
            sys.exit(1)
        return Difficulty.custom(rows, cols, mines)

    mapping = {
        "beginner": Difficulty.beginner(),
        "intermediate": Difficulty.intermediate(),
        "expert": Difficulty.expert(),
    }
    return mapping[args.difficulty]


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.seed is not None:
        import random
        random.seed(args.seed)

    difficulty = resolve_difficulty(args)
    bot = Bot(difficulty)

    if args.display:
        # Display mode: single game with board rendering
        result = bot.run_once(verbose=args.verbose, display=True)
        sys.exit(0 if result.won else 1)

    if args.games == 1:
        result = bot.run_once(verbose=args.verbose)
        print(
            f"\n{'WON  ✓' if result.won else 'LOST ✗'}  "
            f"time={result.elapsed * 1000:.1f} ms  "
            f"efficiency={result.efficiency * 100:.1f} %"
        )
        sys.exit(0 if result.won else 1)

    # Batch mode
    print(
        f"\nRunning {args.games} games on {difficulty.name} "
        f"({difficulty.rows}×{difficulty.cols}, {difficulty.mines} mines)…\n"
    )
    stats = bot.run_batch(args.games, verbose=args.verbose, progress=True)
    print(f"\n{'─' * 40}")
    print(stats.summary())
    print(f"{'─' * 40}")


if __name__ == "__main__":
    main()
