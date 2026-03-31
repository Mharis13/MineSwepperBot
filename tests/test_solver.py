"""Tests del solucionador (solver.py).

Descomenta cada test a medida que implementes el código.
Ejecuta los tests con:  python -m pytest tests/ -v
"""

import random

import pytest

from minesweeper.game import CellState, Difficulty, GameState, Minesweeper
from minesweeper.solver import Constraint, Solver


# ---------------------------------------------------------------------------
# Tests de Constraint — puedes ejecutarlos ya, no dependen de tu código
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
# Tests de _subtract — descomenta cuando implementes _subtract() (Paso 2c)
# ---------------------------------------------------------------------------

class TestSubtract:
    @pytest.mark.skip(reason="TODO: implementa _subtract() (Paso 2c)")
    def test_subtract_when_subset(self):
        c1 = Constraint(frozenset([(0, 0), (0, 1)]), 1)
        c2 = Constraint(frozenset([(0, 0), (0, 1), (0, 2)]), 2)
        result = Solver._subtract(c1, c2)
        assert result is not None
        assert result.cells == frozenset([(0, 2)])
        assert result.mines == 1

    @pytest.mark.skip(reason="TODO: implementa _subtract() (Paso 2c)")
    def test_subtract_when_not_subset(self):
        c1 = Constraint(frozenset([(0, 0), (1, 1)]), 1)
        c2 = Constraint(frozenset([(0, 0), (0, 1)]), 1)
        result = Solver._subtract(c1, c2)
        assert result is None

    @pytest.mark.skip(reason="TODO: implementa _subtract() (Paso 2c)")
    def test_subtract_invalid_negative_mines(self):
        c1 = Constraint(frozenset([(0, 0), (0, 1)]), 2)
        c2 = Constraint(frozenset([(0, 0), (0, 1), (0, 2)]), 1)
        result = Solver._subtract(c1, c2)
        assert result is None


# ---------------------------------------------------------------------------
# Tests del primer movimiento — descomenta cuando implementes next_move() (Paso 2)
# ---------------------------------------------------------------------------

class TestFirstMove:
    @pytest.mark.skip(reason="TODO: implementa next_move() (Paso 2)")
    def test_first_move_is_centre(self):
        game = Minesweeper(Difficulty.beginner())
        solver = Solver(game)
        action, row, col, is_guess = solver.next_move()
        assert action == "reveal"
        assert row == game.rows // 2
        assert col == game.cols // 2
        assert is_guess is False


# ---------------------------------------------------------------------------
# Tests de deducción — descomenta cuando implementes _deduce() (Paso 2b/2c)
# ---------------------------------------------------------------------------

class TestDeterministicDeduction:
    @pytest.mark.skip(reason="TODO: implementa _deduce() (Paso 2b/2c)")
    def test_safe_cells_are_not_mines(self):
        """Cualquier celda marcada como segura por el solver NO debe ser mina."""
        random.seed(42)
        for _ in range(30):
            game = Minesweeper(Difficulty.beginner())
            game.reveal(4, 4)
            solver = Solver(game)
            safe, _ = solver._deduce()
            for r, c in safe:
                assert not game.board[r][c].is_mine

    @pytest.mark.skip(reason="TODO: implementa _deduce() (Paso 2b/2c)")
    def test_mine_cells_are_mines(self):
        """Cualquier celda marcada como mina por el solver SÍ debe ser mina."""
        random.seed(0)
        for _ in range(30):
            game = Minesweeper(Difficulty.beginner())
            game.reveal(4, 4)
            solver = Solver(game)
            _, mines = solver._deduce()
            for r, c in mines:
                assert game.board[r][c].is_mine


# ---------------------------------------------------------------------------
# Tests de juego completo — descomenta cuando todo lo anterior funcione
# ---------------------------------------------------------------------------

class TestFullGame:
    @pytest.mark.skip(reason="TODO: implementa todo el Paso 1 y 2 primero")
    def test_beginner_terminates(self):
        """El bot siempre debe alcanzar un estado terminal en Beginner."""
        for seed in range(10):
            random.seed(seed)
            game = Minesweeper(Difficulty.beginner())
            solver = Solver(game)
            max_moves = game.rows * game.cols + 10
            moves = 0
            while game.game_state == GameState.ONGOING and moves < max_moves:
                action, row, col, is_guess = solver.next_move()
                if action == "flag":
                    game.flag(row, col)
                else:
                    game.reveal(row, col, is_guess=is_guess)
                moves += 1
            assert game.game_state in (GameState.WON, GameState.LOST)
