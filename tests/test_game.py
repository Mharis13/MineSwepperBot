"""Tests del motor del juego (game.py).

Descomenta (o escribe) cada test a medida que implementes el código.
Ejecuta los tests con:  python -m pytest tests/ -v
"""

import pytest
from minesweeper.game import Cell, CellState, Difficulty, GameState, Minesweeper


# ---------------------------------------------------------------------------
# Tests de Difficulty — puedes ejecutarlos ya, no dependen de tu código
# ---------------------------------------------------------------------------

class TestDifficulty:
    def test_beginner(self):
        d = Difficulty.beginner()
        assert d.rows == 9 and d.cols == 9 and d.mines == 10

    def test_intermediate(self):
        d = Difficulty.intermediate()
        assert d.rows == 16 and d.cols == 16 and d.mines == 40

    def test_expert(self):
        d = Difficulty.expert()
        assert d.rows == 16 and d.cols == 30 and d.mines == 99

    def test_custom(self):
        d = Difficulty.custom(5, 8, 6)
        assert d.rows == 5 and d.cols == 8 and d.mines == 6
        assert d.name == "Custom"


# ---------------------------------------------------------------------------
# Tests del tablero — descomenta cuando implementes __init__ y neighbors()
# ---------------------------------------------------------------------------

class TestBoardInit:
    @pytest.mark.skip(reason="TODO: implementa __init__ (Paso 1a)")
    def test_board_dimensions(self):
        game = Minesweeper(Difficulty.beginner())
        assert len(game.board) == 9
        assert all(len(row) == 9 for row in game.board)

    @pytest.mark.skip(reason="TODO: implementa __init__ (Paso 1a)")
    def test_all_cells_hidden_before_reveal(self):
        game = Minesweeper(Difficulty.beginner())
        for r in range(game.rows):
            for c in range(game.cols):
                assert game.board[r][c].state == CellState.HIDDEN

    @pytest.mark.skip(reason="TODO: implementa __init__ (Paso 1a)")
    def test_mines_not_placed_before_first_reveal(self):
        game = Minesweeper(Difficulty.beginner())
        assert not game._initialized
        total_mines = sum(
            1 for r in range(game.rows) for c in range(game.cols)
            if game.board[r][c].is_mine
        )
        assert total_mines == 0


# ---------------------------------------------------------------------------
# Tests de neighbors() — descomenta cuando implementes neighbors() (Paso 1a)
# ---------------------------------------------------------------------------

class TestNeighbours:
    @pytest.mark.skip(reason="TODO: implementa neighbors() (Paso 1a)")
    def test_corner_has_3_neighbours(self):
        game = Minesweeper(Difficulty.beginner())
        assert len(list(game.neighbors(0, 0))) == 3

    @pytest.mark.skip(reason="TODO: implementa neighbors() (Paso 1a)")
    def test_edge_has_5_neighbours(self):
        game = Minesweeper(Difficulty.beginner())
        assert len(list(game.neighbors(0, 4))) == 5

    @pytest.mark.skip(reason="TODO: implementa neighbors() (Paso 1a)")
    def test_centre_has_8_neighbours(self):
        game = Minesweeper(Difficulty.beginner())
        assert len(list(game.neighbors(4, 4))) == 8


# ---------------------------------------------------------------------------
# Tests de colocación de minas — descomenta cuando implementes _place_mines() (Paso 1b)
# ---------------------------------------------------------------------------

class TestFirstClickSafety:
    @pytest.mark.skip(reason="TODO: implementa _place_mines() (Paso 1b)")
    def test_first_click_not_mine(self):
        for _ in range(20):
            game = Minesweeper(Difficulty.beginner())
            game.reveal(4, 4)
            assert not game.board[4][4].is_mine

    @pytest.mark.skip(reason="TODO: implementa _place_mines() (Paso 1b)")
    def test_correct_mine_count_placed(self):
        game = Minesweeper(Difficulty.beginner())
        game.reveal(4, 4)
        total = sum(
            1 for r in range(game.rows) for c in range(game.cols)
            if game.board[r][c].is_mine
        )
        assert total == 10


# ---------------------------------------------------------------------------
# Tests de reveal / flood-fill — descomenta cuando implementes reveal() (Paso 1c/1d)
# ---------------------------------------------------------------------------

class TestReveal:
    @pytest.mark.skip(reason="TODO: implementa reveal() (Paso 1c)")
    def test_reveal_changes_state(self):
        game = Minesweeper(Difficulty.beginner())
        game.reveal(4, 4)
        assert game.board[4][4].state == CellState.REVEALED

    @pytest.mark.skip(reason="TODO: implementa reveal() (Paso 1c)")
    def test_cannot_reveal_already_revealed(self):
        game = Minesweeper(Difficulty.beginner())
        game.reveal(4, 4)
        count_after_first = game.reveal_count
        result = game.reveal(4, 4)
        assert result is False
        assert game.reveal_count == count_after_first


# ---------------------------------------------------------------------------
# Tests de banderas — descomenta cuando implementes flag() (Paso 1e)
# ---------------------------------------------------------------------------

class TestFlag:
    @pytest.mark.skip(reason="TODO: implementa flag() (Paso 1e)")
    def test_flag_hidden_cell(self):
        game = Minesweeper(Difficulty.beginner())
        result = game.flag(0, 0)
        assert result is True
        assert game.board[0][0].state == CellState.FLAGGED

    @pytest.mark.skip(reason="TODO: implementa flag() (Paso 1e)")
    def test_unflag_flagged_cell(self):
        game = Minesweeper(Difficulty.beginner())
        game.flag(0, 0)
        game.flag(0, 0)
        assert game.board[0][0].state == CellState.HIDDEN


# ---------------------------------------------------------------------------
# Tests de condición de victoria — descomenta cuando implementes _check_win() (Paso 1g)
# ---------------------------------------------------------------------------

class TestWin:
    @pytest.mark.skip(reason="TODO: implementa _check_win() (Paso 1g)")
    def test_game_state_starts_ongoing(self):
        game = Minesweeper(Difficulty.beginner())
        assert game.game_state == GameState.ONGOING
