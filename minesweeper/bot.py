"""Bot orchestration — runs the solver in a loop and collects statistics.

PASO 3 — Bot y estadísticas
============================
Con el motor (Paso 1) y el solucionador (Paso 2) listos, este módulo los une:

  3a. GameResult: almacena el resultado de una sola partida.
  3b. Statistics: agrega resultados de múltiples partidas.
  3c. Bot.run_once(): juega una partida completa con el solver en bucle.
  3d. Bot.run_batch(): juega N partidas y devuelve estadísticas globales.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

from .game import Difficulty, GameState, Minesweeper
from .solver import Solver


# ---------------------------------------------------------------------------
# PASO 3a — Resultado de una partida
# ---------------------------------------------------------------------------

@dataclass
class GameResult:
    """Resultado de una sola partida.

    TODO 3a: Almacena los campos necesarios:
      - won: bool          → si el bot ganó
      - elapsed: float     → tiempo en segundos
      - reveal_count: int  → total de celdas reveladas
      - flag_count: int    → total de banderas colocadas
      - guess_count: int   → cuántos movimientos fueron adivinanzas
      - difficulty: Difficulty

    Añade también una propiedad 'efficiency' que devuelva la fracción de
    reveals que fueron deterministas: max(0, 1 − guess_count / reveal_count).
    """
    won: bool
    elapsed: float
    reveal_count: int
    flag_count: int
    guess_count: int
    difficulty: Difficulty

    @property
    def efficiency(self) -> float:
        """Fracción de reveals que fueron deterministas.

        TODO 3a: implementa efficiency.
        """
        raise NotImplementedError("TODO 3a: implementa efficiency")


# ---------------------------------------------------------------------------
# PASO 3b — Estadísticas agregadas
# ---------------------------------------------------------------------------

@dataclass
class Statistics:
    """Estadísticas de múltiples partidas.

    TODO 3b: Implementa las propiedades y el método summary():
      - total, wins, losses  → contadores básicos
      - win_rate             → wins / total
      - avg_time             → media de elapsed
      - best_time            → mínimo de elapsed entre las victorias
      - avg_efficiency       → media de efficiency
      - summary()            → cadena de texto con un resumen legible
    """

    results: List[GameResult] = field(default_factory=list)

    def add(self, result: GameResult) -> None:
        self.results.append(result)

    @property
    def total(self) -> int:
        raise NotImplementedError("TODO 3b: implementa total")

    @property
    def wins(self) -> int:
        raise NotImplementedError("TODO 3b: implementa wins")

    @property
    def losses(self) -> int:
        raise NotImplementedError("TODO 3b: implementa losses")

    @property
    def win_rate(self) -> float:
        raise NotImplementedError("TODO 3b: implementa win_rate")

    @property
    def avg_time(self) -> float:
        raise NotImplementedError("TODO 3b: implementa avg_time")

    @property
    def best_time(self) -> float:
        raise NotImplementedError("TODO 3b: implementa best_time")

    @property
    def avg_efficiency(self) -> float:
        raise NotImplementedError("TODO 3b: implementa avg_efficiency")

    def summary(self) -> str:
        raise NotImplementedError("TODO 3b: implementa summary()")


# ---------------------------------------------------------------------------
# PASO 3c/3d — Bot
# ---------------------------------------------------------------------------

class Bot:
    """Bot de Minesweeper estilo TAS.

    Ejecuta el solver lo más rápido posible y registra estadísticas.

    Ejemplo de uso::

        bot = Bot(Difficulty.expert())
        result = bot.run_once(verbose=True)       # una partida
        stats = bot.run_batch(100)                # 100 partidas
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
        """Juega una sola partida y devuelve el resultado.

        TODO 3c:
          1. Crea Minesweeper(self.difficulty) y Solver(game).
          2. Mientras game.game_state == ONGOING:
               a. Obtén la jugada del solver: action, row, col, is_guess.
               b. Si display, renderiza el tablero (importa display.render).
               c. Si verbose, imprime la jugada.
               d. Ejecuta game.flag() o game.reveal() según la acción.
          3. Si display, renderiza el estado final.
          4. Construye y devuelve un GameResult con los datos de la partida.
        """
        raise NotImplementedError("TODO 3c: implementa run_once()")

    def run_batch(
        self,
        n: int,
        *,
        verbose: bool = False,
        progress: bool = True,
    ) -> Statistics:
        """Juega n partidas y devuelve estadísticas agregadas.

        TODO 3d:
          1. Crea un objeto Statistics().
          2. Para i en 1..n:
               a. Llama a run_once() y añade el resultado a stats.
               b. Si progress, imprime cada 10 % (o cada partida) el avance.
          3. Devuelve stats.
        """
        raise NotImplementedError("TODO 3d: implementa run_batch()")
