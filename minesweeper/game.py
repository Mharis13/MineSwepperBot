"""Minesweeper game engine.

PASO 1 — Motor del juego
========================
Aquí debes implementar la lógica central del buscaminas:

  1a. Representación del tablero y estados de las celdas.
  1b. Colocación de minas DESPUÉS del primer click (seguridad garantizada).
  1c. Cálculo de adyacencias (cuántas minas rodean cada celda).
  1d. Revelar una celda:
        - Si es mina → LOST.
        - Si tiene 0 minas adyacentes → flood-fill (revelar cascada).
        - Si tiene N minas adyacentes → mostrar el número.
  1e. Marcar/desmarcar celdas con bandera.
  1f. Chord-click: si una celda número ya tiene todas sus banderas colocadas,
      revelar automáticamente todos sus vecinos ocultos restantes.
  1g. Detectar condición de victoria (todas las celdas seguras reveladas).
"""

import random
import time
from enum import Enum
from typing import Generator, NamedTuple, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums y tipos de datos — ya definidos, no necesitas cambiarlos
# ---------------------------------------------------------------------------

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
    """Una celda del tablero."""
    __slots__ = ("is_mine", "state", "adjacent_mines")

    def __init__(self) -> None:
        self.is_mine: bool = False
        self.state: CellState = CellState.HIDDEN
        self.adjacent_mines: int = 0


# ---------------------------------------------------------------------------
# Motor principal — AQUÍ empieza tu trabajo
# ---------------------------------------------------------------------------

class Minesweeper:
    """Motor del juego Minesweeper.

    Ejemplo de uso::

        game = Minesweeper(Difficulty.expert())
        game.reveal(7, 14)   # primer click — minas se colocan después de esto
        if game.game_state == GameState.WON:
            print("Ganado en", game.elapsed_time, "segundos")
    """

    def __init__(self, difficulty: Difficulty) -> None:
        self.rows = difficulty.rows
        self.cols = difficulty.cols
        self.num_mines = difficulty.mines
        self.difficulty = difficulty

        # TODO 1a: Crear el tablero 2D de celdas (lista de listas de Cell)
        self.board: list[list[Cell]] = [
            [Cell() for _ in range(self.cols)] for _ in range(self.rows)
        ]

        self.game_state: GameState = GameState.ONGOING
        self._initialized: bool = False          # se vuelve True tras el 1er click
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None

        # Contadores de estadísticas
        self.reveal_count: int = 0
        self.flag_count: int = 0
        self.guess_count: int = 0

    # ------------------------------------------------------------------
    # PASO 1a — Vecinos
    # ------------------------------------------------------------------

    def neighbors(self, row: int, col: int) -> Generator[Tuple[int, int], None, None]:
        """Devuelve los (row, col) válidos de los 8 vecinos de una celda.

        TODO 1a: Itera los desplazamientos (-1, 0, 1) × (-1, 0, 1),
                 salta el (0, 0) propio, y devuelve solo los que estén
                 dentro de los límites del tablero.
        """
        raise NotImplementedError("TODO 1a: implementa neighbors()")

    # ------------------------------------------------------------------
    # PASO 1b — Colocación de minas (diferida al 1er click)
    # ------------------------------------------------------------------

    def _place_mines(self, safe_row: int, safe_col: int) -> None:
        """Coloca minas aleatoriamente, manteniendo segura la zona 3×3 del 1er click.

        TODO 1b:
          1. Crea el conjunto 'safe' con (safe_row, safe_col) y todos sus vecinos.
          2. Recoge todos los (r, c) del tablero que NO estén en 'safe'.
          3. Elige aleatoriamente `self.num_mines` de esos candidatos
             (usa random.sample) y márcalos como mina.
          4. Recorre todo el tablero y calcula adjacent_mines para cada
             celda no-mina (cuenta cuántas de sus vecinas son minas).
          5. Pon self._initialized = True.
        """
        raise NotImplementedError("TODO 1b: implementa _place_mines()")

    # ------------------------------------------------------------------
    # PASO 1c/1d — Revelar
    # ------------------------------------------------------------------

    def reveal(self, row: int, col: int, *, is_guess: bool = False) -> bool:
        """Revela la celda (row, col). Devuelve True si la celda fue revelada.

        TODO 1c:
          1. Si el juego no está ONGOING, devuelve False.
          2. Si la celda no está HIDDEN (ya revelada o con bandera), devuelve False.
          3. Si es el primer click (not self._initialized):
               - Guarda self._start_time = time.perf_counter()
               - Llama a self._place_mines(row, col)
          4. Si is_guess, incrementa self.guess_count.
          5. Llama a self._reveal_cell(row, col).
          6. Devuelve True.
        """
        raise NotImplementedError("TODO 1c: implementa reveal()")

    def _reveal_cell(self, row: int, col: int) -> None:
        """Reveal interno con flood-fill recursivo.

        TODO 1d:
          1. Si la celda no está HIDDEN, termina.
          2. Cambia su estado a REVEALED e incrementa self.reveal_count.
          3. Si es mina:
               - Cambia game_state a LOST.
               - Guarda self._end_time = time.perf_counter().
               - Termina.
          4. Si adjacent_mines == 0 (celda vacía), llama recursivamente a
             _reveal_cell() en todos los vecinos HIDDEN (flood-fill).
          5. Llama a self._check_win().
        """
        raise NotImplementedError("TODO 1d: implementa _reveal_cell()")

    # ------------------------------------------------------------------
    # PASO 1e — Banderas
    # ------------------------------------------------------------------

    def flag(self, row: int, col: int) -> bool:
        """Alterna bandera en una celda oculta. Devuelve True si tuvo efecto.

        TODO 1e:
          1. Si el juego no está ONGOING, devuelve False.
          2. Si está HIDDEN → ponla en FLAGGED, incrementa flag_count, devuelve True.
          3. Si está FLAGGED → ponla en HIDDEN, decrementa flag_count, devuelve True.
          4. En cualquier otro caso devuelve False.
        """
        raise NotImplementedError("TODO 1e: implementa flag()")

    # ------------------------------------------------------------------
    # PASO 1f — Chord
    # ------------------------------------------------------------------

    def chord(self, row: int, col: int) -> bool:
        """Chord-click: revela vecinos ocultos de una celda número ya satisfecha.

        Una celda está satisfecha cuando el número de banderas vecinas es igual
        a su valor de adjacent_mines.

        TODO 1f:
          1. Si el juego no está ONGOING, devuelve False.
          2. Si la celda no está REVEALED o es 0, devuelve False.
          3. Cuenta las banderas vecinas.
          4. Si la cuenta no iguala adjacent_mines, devuelve False.
          5. Llama a _reveal_cell() en cada vecino HIDDEN.
          6. Devuelve True si se reveló al menos uno.
        """
        raise NotImplementedError("TODO 1f: implementa chord()")

    # ------------------------------------------------------------------
    # PASO 1g — Victoria
    # ------------------------------------------------------------------

    def _check_win(self) -> None:
        """Comprueba si todas las celdas seguras han sido reveladas.

        TODO 1g:
          1. Si game_state no es ONGOING, termina.
          2. Recorre el tablero; si alguna celda no-mina no está REVEALED, termina.
          3. Si el bucle completa sin encontrar ninguna → WON.
             Guarda self._end_time = time.perf_counter().
        """
        raise NotImplementedError("TODO 1g: implementa _check_win()")

    # ------------------------------------------------------------------
    # Propiedades de consulta — implementa estas también
    # ------------------------------------------------------------------

    @property
    def elapsed_time(self) -> float:
        """Tiempo transcurrido en segundos (0.0 antes del primer reveal).

        TODO: devuelve el tiempo entre _start_time y _end_time (o ahora si
              la partida sigue en curso). Si _start_time es None, devuelve 0.0.
        """
        raise NotImplementedError("TODO: implementa elapsed_time")

    @property
    def remaining_mines(self) -> int:
        """Contador de minas: total menos banderas colocadas.

        TODO: cuenta las celdas con estado FLAGGED y réstaselas a num_mines.
        """
        raise NotImplementedError("TODO: implementa remaining_mines")

    @property
    def hidden_count(self) -> int:
        """Número de celdas todavía ocultas (ni reveladas ni con bandera).

        TODO: cuenta las celdas con estado HIDDEN.
        """
        raise NotImplementedError("TODO: implementa hidden_count")
