"""Terminal renderer for the Minesweeper board.

PASO 4 — Visualización (opcional, pero recomendado para depurar)
================================================================
Implementa una función render(game) que devuelva una cadena de texto
con el estado actual del tablero para mostrarlo en la terminal.

Sugerencia de formato:

     0  1  2  3  4 ...
    +--+--+--+--+--+
  0 | .  .  1  .  . |
  1 | .  1  2  .  . |
  ...
    +--+--+--+--+--+
  Status: ONGOING | Mines left:  9 | Time: 12.3 ms

Leyenda de caracteres:
  '.'  → celda oculta (HIDDEN)
  'F'  → bandera (FLAGGED)
  ' '  → celda vacía revelada (adjacent_mines == 0)
  '1'-'8' → número de minas adyacentes
  '*'  → mina no revelada (solo se muestra al perder)
  'X'  → mina revelada (celda donde explotó)

TODO 4: Implementa render() y las funciones auxiliares que necesites.
        (Opcional) Añade colores ANSI para que sea más fácil de leer.
"""

from __future__ import annotations

from .game import CellState, GameState, Minesweeper


def render(game: Minesweeper, *, colour: bool | None = None) -> str:
    """Devuelve una representación de texto del tablero actual.

    TODO 4: implementa esta función.
    """
    raise NotImplementedError("TODO 4: implementa render()")
