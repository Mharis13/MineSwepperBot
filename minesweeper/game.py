"""Minesweeper game engine.

Provides the core board representation, cell states, and game logic including:
- First-click safety (first reveal is never a mine)
- Flood-fill reveal for zero-adjacency cells
- Win / loss detection
"""

import random
import time
from enum import Enum
from typing import Generator, NamedTuple, Optional, Tuple


class CellState(Enum):
    HIDDEN = "hidden"
    REVEALED = "revealed"
    FLAGGED = "flagged"


class GameState(Enum):
    ONGOING = "ongoing"
    WON = "won"
    LOST = "lost"


class Difficulty(NamedTuple):
    rows: int
    cols: int
    mines: int
    name: str

    @classmethod
    def beginner(cls) -> "Difficulty":
        return cls(rows=9, cols=9, mines=10, name="Beginner")

    @classmethod
    def intermediate(cls) -> "Difficulty":
        return cls(rows=16, cols=16, mines=40, name="Intermediate")

    @classmethod
    def expert(cls) -> "Difficulty":
        return cls(rows=16, cols=30, mines=99, name="Expert")

    @classmethod
    def custom(cls, rows: int, cols: int, mines: int) -> "Difficulty":
        return cls(rows=rows, cols=cols, mines=mines, name="Custom")


class Cell:
    __slots__ = ("is_mine", "state", "adjacent_mines")

    def __init__(self) -> None:
        self.is_mine: bool = False
        self.state: CellState = CellState.HIDDEN
        self.adjacent_mines: int = 0


class Minesweeper:
    """Minesweeper game engine.

    Usage::

        game = Minesweeper(Difficulty.expert())
        game.reveal(7, 14)   # first click — mines are placed after this
        if game.game_state == GameState.WON:
            print("Won in", game.elapsed_time, "seconds")
    """

    def __init__(self, difficulty: Difficulty) -> None:
        self.rows = difficulty.rows
        self.cols = difficulty.cols
        self.num_mines = difficulty.mines
        self.difficulty = difficulty

        self.board: list[list[Cell]] = [
            [Cell() for _ in range(self.cols)] for _ in range(self.rows)
        ]
        self.game_state: GameState = GameState.ONGOING
        self._initialized: bool = False
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None

        # Statistics
        self.reveal_count: int = 0
        self.flag_count: int = 0
        self.guess_count: int = 0

    # ------------------------------------------------------------------
    # Board helpers
    # ------------------------------------------------------------------

    def neighbors(self, row: int, col: int) -> Generator[Tuple[int, int], None, None]:
        """Yield valid (row, col) pairs for all 8 neighbours."""
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    yield r, c

    # ------------------------------------------------------------------
    # Initialisation (deferred until first click for safety guarantee)
    # ------------------------------------------------------------------

    def _place_mines(self, safe_row: int, safe_col: int) -> None:
        """Place mines randomly, keeping a 3×3 area around the first click safe."""
        safe: set[Tuple[int, int]] = {(safe_row, safe_col)}
        safe.update(self.neighbors(safe_row, safe_col))

        candidates = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in safe
        ]

        count = min(self.num_mines, len(candidates))
        for r, c in random.sample(candidates, count):
            self.board[r][c].is_mine = True

        # Compute adjacency counts
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.board[r][c].is_mine:
                    self.board[r][c].adjacent_mines = sum(
                        1 for nr, nc in self.neighbors(r, c) if self.board[nr][nc].is_mine
                    )

        self._initialized = True

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def reveal(self, row: int, col: int, *, is_guess: bool = False) -> bool:
        """Reveal a cell.  Returns *True* if the cell was newly revealed safely.

        Triggers mine placement on the first call (ensuring first click is safe).
        Performs flood-fill for zero-adjacency cells.
        """
        if self.game_state != GameState.ONGOING:
            return False

        cell = self.board[row][col]
        if cell.state != CellState.HIDDEN:
            return False

        if not self._initialized:
            self._start_time = time.perf_counter()
            self._place_mines(row, col)

        if is_guess:
            self.guess_count += 1

        self._reveal_cell(row, col)
        return True

    def _reveal_cell(self, row: int, col: int) -> None:
        """Internal recursive reveal with flood-fill."""
        cell = self.board[row][col]
        if cell.state != CellState.HIDDEN:
            return

        cell.state = CellState.REVEALED
        self.reveal_count += 1

        if cell.is_mine:
            self.game_state = GameState.LOST
            self._end_time = time.perf_counter()
            return

        if cell.adjacent_mines == 0:
            for nr, nc in self.neighbors(row, col):
                if self.board[nr][nc].state == CellState.HIDDEN:
                    self._reveal_cell(nr, nc)

        self._check_win()

    def flag(self, row: int, col: int) -> bool:
        """Toggle a flag on a hidden cell.  Returns *True* on success."""
        if self.game_state != GameState.ONGOING:
            return False
        cell = self.board[row][col]
        if cell.state == CellState.HIDDEN:
            cell.state = CellState.FLAGGED
            self.flag_count += 1
            return True
        if cell.state == CellState.FLAGGED:
            cell.state = CellState.HIDDEN
            self.flag_count -= 1
            return True
        return False

    def chord(self, row: int, col: int) -> bool:
        """Chord-click: reveal all hidden neighbours of a satisfied number cell.

        A cell is satisfied when its flagged-neighbour count equals its number.
        Returns *True* if any new reveals happened.
        """
        if self.game_state != GameState.ONGOING:
            return False
        cell = self.board[row][col]
        if cell.state != CellState.REVEALED or cell.adjacent_mines == 0:
            return False

        flagged = sum(
            1 for nr, nc in self.neighbors(row, col)
            if self.board[nr][nc].state == CellState.FLAGGED
        )
        if flagged != cell.adjacent_mines:
            return False

        revealed_any = False
        for nr, nc in self.neighbors(row, col):
            if self.board[nr][nc].state == CellState.HIDDEN:
                self._reveal_cell(nr, nc)
                revealed_any = True
        return revealed_any

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def _check_win(self) -> None:
        if self.game_state != GameState.ONGOING:
            return
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.board[r][c]
                if not cell.is_mine and cell.state != CellState.REVEALED:
                    return
        self.game_state = GameState.WON
        self._end_time = time.perf_counter()

    @property
    def elapsed_time(self) -> float:
        """Elapsed wall-clock time in seconds (0 before first reveal)."""
        if self._start_time is None:
            return 0.0
        end = self._end_time if self._end_time is not None else time.perf_counter()
        return end - self._start_time

    @property
    def remaining_mines(self) -> int:
        """Mine counter: total mines minus flags placed."""
        flagged = sum(
            1
            for r in range(self.rows)
            for c in range(self.cols)
            if self.board[r][c].state == CellState.FLAGGED
        )
        return self.num_mines - flagged

    @property
    def hidden_count(self) -> int:
        """Number of still-hidden (unrevealed, unflagged) cells."""
        return sum(
            1
            for r in range(self.rows)
            for c in range(self.cols)
            if self.board[r][c].state == CellState.HIDDEN
        )
