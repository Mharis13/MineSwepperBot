"""Unit tests for the Minesweeper solver."""

import random

import pytest

from minesweeper.game import CellState, Difficulty, GameState, Minesweeper
from minesweeper.solver import Constraint, Solver


# ---------------------------------------------------------------------------
# Constraint helpers
# ---------------------------------------------------------------------------

class TestConstraint:
    def test_constraint_creation(self):
        cells = frozenset([(0, 0), (0, 1)])
        c = Constraint(cells=cells, mines=1)
        assert c.mines == 1
        assert len(c.cells) == 2

    def test_constraint_equality(self):
        cells = frozenset([(1, 2), (1, 3)])
        c1 = Constraint(cells=cells, mines=1)
        c2 = Constraint(cells=cells, mines=1)
        assert c1 == c2

    def test_constraint_hashable(self):
        c = Constraint(frozenset([(0, 0)]), 1)
        s = {c}
        assert c in s


# ---------------------------------------------------------------------------
# Solver._subtract (internal utility)
# ---------------------------------------------------------------------------

class TestSubtract:
    def test_subtract_when_subset(self):
        c1 = Constraint(frozenset([(0, 0), (0, 1)]), 1)
        c2 = Constraint(frozenset([(0, 0), (0, 1), (0, 2)]), 2)
        result = Solver._subtract(c1, c2)
        assert result is not None
        assert result.cells == frozenset([(0, 2)])
        assert result.mines == 1

    def test_subtract_when_not_subset(self):
        c1 = Constraint(frozenset([(0, 0), (1, 1)]), 1)
        c2 = Constraint(frozenset([(0, 0), (0, 1)]), 1)
        result = Solver._subtract(c1, c2)
        assert result is None

    def test_subtract_when_equal(self):
        cells = frozenset([(0, 0), (0, 1)])
        c1 = Constraint(cells, 1)
        c2 = Constraint(cells, 1)
        # Subtracting equal sets → empty constraint with 0 mines
        result = Solver._subtract(c1, c2)
        assert result is not None
        assert result.cells == frozenset()
        assert result.mines == 0

    def test_subtract_invalid_negative_mines(self):
        # c1 has MORE mines than c2 — invalid, should return None
        c1 = Constraint(frozenset([(0, 0), (0, 1)]), 2)
        c2 = Constraint(frozenset([(0, 0), (0, 1), (0, 2)]), 1)
        result = Solver._subtract(c1, c2)
        assert result is None


# ---------------------------------------------------------------------------
# Solver integration — first move
# ---------------------------------------------------------------------------

class TestFirstMove:
    def test_first_move_is_centre(self):
        game = Minesweeper(Difficulty.beginner())
        solver = Solver(game)
        action, row, col, is_guess = solver.next_move()
        assert action == "reveal"
        assert row == game.rows // 2
        assert col == game.cols // 2
        assert is_guess is False


# ---------------------------------------------------------------------------
# Solver deterministic deductions
# ---------------------------------------------------------------------------

class TestDeterministicDeduction:
    def _make_trivial_game(self) -> Minesweeper:
        """Create a game where exactly one hidden cell is known to be a mine."""
        random.seed(1)
        game = Minesweeper(Difficulty.beginner())
        game.reveal(4, 4)
        return game

    def test_deduce_returns_sets(self):
        game = self._make_trivial_game()
        solver = Solver(game)
        safe, mines = solver._deduce()
        assert isinstance(safe, set)
        assert isinstance(mines, set)

    def test_safe_cells_are_not_mines(self):
        """Any cell marked safe by the solver must not be a mine."""
        random.seed(42)
        for _ in range(30):
            game = Minesweeper(Difficulty.beginner())
            game.reveal(4, 4)
            solver = Solver(game)
            safe, _ = solver._deduce()
            for r, c in safe:
                assert not game.board[r][c].is_mine, \
                    f"Solver incorrectly marked ({r},{c}) as safe but it is a mine"

    def test_mine_cells_are_mines(self):
        """Any cell marked as a mine by the solver must actually be a mine."""
        random.seed(0)
        for _ in range(30):
            game = Minesweeper(Difficulty.beginner())
            game.reveal(4, 4)
            solver = Solver(game)
            _, mines = solver._deduce()
            for r, c in mines:
                assert game.board[r][c].is_mine, \
                    f"Solver incorrectly marked ({r},{c}) as mine but it is safe"


# ---------------------------------------------------------------------------
# Solver best_guess
# ---------------------------------------------------------------------------

class TestBestGuess:
    def test_best_guess_returns_hidden_cell(self):
        random.seed(5)
        game = Minesweeper(Difficulty.beginner())
        game.reveal(4, 4)
        solver = Solver(game)
        r, c = solver._best_guess()
        assert 0 <= r < game.rows
        assert 0 <= c < game.cols
        assert game.board[r][c].state == CellState.HIDDEN

    def test_best_guess_no_revealed_cells(self):
        """Before first reveal, best_guess should still return a valid cell."""
        game = Minesweeper(Difficulty.beginner())
        solver = Solver(game)
        r, c = solver._best_guess()
        assert 0 <= r < game.rows
        assert 0 <= c < game.cols


# ---------------------------------------------------------------------------
# Full game simulation
# ---------------------------------------------------------------------------

class TestFullGame:
    def _play_game(self, difficulty: Difficulty, seed: int) -> GameState:
        random.seed(seed)
        game = Minesweeper(difficulty)
        solver = Solver(game)

        max_moves = difficulty.rows * difficulty.cols + 10
        moves = 0
        while game.game_state == GameState.ONGOING and moves < max_moves:
            action, row, col, is_guess = solver.next_move()
            if action == "flag":
                game.flag(row, col)
            else:
                game.reveal(row, col, is_guess=is_guess)
            moves += 1

        return game.game_state

    def test_beginner_terminates(self):
        """The bot must always reach a terminal state on Beginner."""
        for seed in range(10):
            state = self._play_game(Difficulty.beginner(), seed)
            assert state in (GameState.WON, GameState.LOST), \
                f"Game did not terminate with seed={seed}"

    def test_intermediate_terminates(self):
        for seed in range(5):
            state = self._play_game(Difficulty.intermediate(), seed)
            assert state in (GameState.WON, GameState.LOST)

    def test_expert_terminates(self):
        for seed in range(3):
            state = self._play_game(Difficulty.expert(), seed)
            assert state in (GameState.WON, GameState.LOST)

    def test_solver_never_wrongly_flags(self):
        """The solver should never flag a safe cell."""
        random.seed(99)
        for _ in range(20):
            game = Minesweeper(Difficulty.beginner())
            solver = Solver(game)
            max_moves = game.rows * game.cols + 10
            moves = 0
            while game.game_state == GameState.ONGOING and moves < max_moves:
                action, row, col, _ = solver.next_move()
                if action == "flag":
                    assert game.board[row][col].is_mine or not game._initialized, \
                        f"Solver flagged safe cell ({row},{col})"
                    game.flag(row, col)
                else:
                    game.reveal(row, col)
                moves += 1

    def test_win_rate_beginner_above_threshold(self):
        """Bot should win most Beginner games (threshold: >70 %)."""
        wins = 0
        n = 50
        for seed in range(n):
            state = self._play_game(Difficulty.beginner(), seed)
            if state == GameState.WON:
                wins += 1
        win_rate = wins / n
        assert win_rate > 0.70, f"Win rate {win_rate:.0%} below threshold"
