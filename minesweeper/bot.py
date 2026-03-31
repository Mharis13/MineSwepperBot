"""Bot orchestration — runs the solver in a loop and collects statistics."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

from .game import Difficulty, GameState, Minesweeper
from .solver import Solver


@dataclass
class GameResult:
    """Result of a single game run."""

    won: bool
    elapsed: float
    reveal_count: int
    flag_count: int
    guess_count: int
    difficulty: Difficulty

    @property
    def efficiency(self) -> float:
        """Fraction of reveals that were deterministic (no guess needed)."""
        if self.reveal_count == 0:
            return 0.0
        return max(0.0, 1.0 - self.guess_count / self.reveal_count)


@dataclass
class Statistics:
    """Aggregated statistics across multiple games."""

    results: List[GameResult] = field(default_factory=list)

    def add(self, result: GameResult) -> None:
        self.results.append(result)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def wins(self) -> int:
        return sum(1 for r in self.results if r.won)

    @property
    def losses(self) -> int:
        return self.total - self.wins

    @property
    def win_rate(self) -> float:
        return self.wins / self.total if self.total else 0.0

    @property
    def avg_time(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.elapsed for r in self.results) / self.total

    @property
    def best_time(self) -> float:
        wins = [r.elapsed for r in self.results if r.won]
        return min(wins) if wins else 0.0

    @property
    def avg_efficiency(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.efficiency for r in self.results) / self.total

    def summary(self) -> str:
        lines = [
            f"Games played : {self.total}",
            f"Wins         : {self.wins}  ({self.win_rate * 100:.1f} %)",
            f"Losses       : {self.losses}",
            f"Avg time     : {self.avg_time * 1000:.1f} ms",
            f"Best time    : {self.best_time * 1000:.1f} ms",
            f"Avg efficiency: {self.avg_efficiency * 100:.1f} %",
        ]
        return "\n".join(lines)


class Bot:
    """TAS-style Minesweeper bot.

    Runs the solver as fast as possible and records game statistics.

    Usage::

        bot = Bot(Difficulty.expert())
        result = bot.run_once(verbose=True)      # single game
        stats = bot.run_batch(100, verbose=False)  # 100 games
        print(stats.summary())
    """

    def __init__(self, difficulty: Difficulty) -> None:
        self.difficulty = difficulty

    def run_once(
        self,
        *,
        verbose: bool = False,
        display: bool = False,
    ) -> GameResult:
        """Play a single game and return the result."""
        from .display import render  # avoid circular import at module level

        game = Minesweeper(self.difficulty)
        solver = Solver(game)

        if verbose:
            print(f"\n{'=' * 50}")
            print(f"  {self.difficulty.name} — {self.difficulty.rows}×{self.difficulty.cols}"
                  f", {self.difficulty.mines} mines")
            print(f"{'=' * 50}")

        while game.game_state == GameState.ONGOING:
            action, row, col, is_guess = solver.next_move()

            if display:
                print(render(game))

            if verbose:
                marker = " [GUESS]" if is_guess else ""
                print(f"  {action.upper():6s}  ({row:2d},{col:2d}){marker}")

            if action == "flag":
                game.flag(row, col)
            else:
                game.reveal(row, col, is_guess=is_guess)

        if display:
            print(render(game))

        result = GameResult(
            won=game.game_state == GameState.WON,
            elapsed=game.elapsed_time,
            reveal_count=game.reveal_count,
            flag_count=game.flag_count,
            guess_count=game.guess_count,
            difficulty=self.difficulty,
        )

        if verbose:
            status = "WON  ✓" if result.won else "LOST ✗"
            print(f"\n  Result     : {status}")
            print(f"  Time       : {result.elapsed * 1000:.1f} ms")
            print(f"  Efficiency : {result.efficiency * 100:.1f} %")

        return result

    def run_batch(
        self,
        n: int,
        *,
        verbose: bool = False,
        progress: bool = True,
    ) -> Statistics:
        """Play *n* games and return aggregated statistics.

        Parameters
        ----------
        n:
            Number of games to play.
        verbose:
            Print details for every game.
        progress:
            Print a progress bar / running tally every 10 games.
        """
        stats = Statistics()
        start = time.perf_counter()

        for i in range(1, n + 1):
            result = self.run_once(verbose=verbose)
            stats.add(result)

            if progress and (i % max(1, n // 10) == 0 or i == n):
                elapsed_total = time.perf_counter() - start
                rate = i / elapsed_total if elapsed_total > 0 else 0
                print(
                    f"  [{i:>{len(str(n))}}/{n}]  "
                    f"win-rate={stats.win_rate * 100:5.1f}%  "
                    f"speed={rate:.0f} games/s"
                )

        return stats
