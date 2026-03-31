"""Terminal renderer for the Minesweeper board.

Produces a coloured ASCII representation when stdout supports ANSI escape codes,
and a plain-text fallback otherwise.
"""

from __future__ import annotations

import os
import sys

from .game import CellState, GameState, Minesweeper

# ANSI colour codes
_RESET = "\033[0m"
_BOLD = "\033[1m"
_COLOURS = {
    0: "\033[37m",   # grey
    1: "\033[34m",   # blue
    2: "\033[32m",   # green
    3: "\033[31m",   # red
    4: "\033[35m",   # magenta
    5: "\033[33m",   # yellow
    6: "\033[36m",   # cyan
    7: "\033[91m",   # bright red
    8: "\033[97m",   # white
}
_FLAG_COLOUR = "\033[31m"    # red
_MINE_COLOUR = "\033[91m"    # bright red
_HIDDEN_COLOUR = "\033[90m"  # dark grey


def _supports_colour() -> bool:
    return (
        hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
        and os.environ.get("NO_COLOR") is None
    )


def render(game: Minesweeper, *, colour: bool | None = None) -> str:
    """Return a multi-line string representing the current board state."""
    if colour is None:
        colour = _supports_colour()

    rows, cols = game.rows, game.cols
    lines: list[str] = []

    # Column header
    col_header = "     " + "".join(f"{c:2d}" for c in range(cols))
    lines.append(col_header)
    lines.append("    +" + "--" * cols + "+")

    for r in range(rows):
        row_chars: list[str] = []
        for c in range(cols):
            cell = game.board[r][c]
            ch, clr = _cell_char(cell, game.game_state, colour)
            if colour and clr:
                row_chars.append(clr + ch + _RESET)
            else:
                row_chars.append(ch)
        lines.append(f" {r:2d} |" + " ".join(row_chars) + " |")

    lines.append("    +" + "--" * cols + "+")

    # Status line
    status = _status_line(game)
    lines.append(status)

    return "\n".join(lines)


def _cell_char(
    cell,  # Cell
    state: GameState,
    colour: bool,
) -> tuple[str, str]:
    """Return (character, ansi_colour) for a cell."""
    if cell.state == CellState.FLAGGED:
        return "F", _FLAG_COLOUR if colour else ""
    if cell.state == CellState.HIDDEN:
        if state == GameState.LOST and cell.is_mine:
            return "*", _MINE_COLOUR if colour else ""
        return ".", _HIDDEN_COLOUR if colour else ""
    # Revealed
    if cell.is_mine:
        return "X", _MINE_COLOUR if colour else ""
    if cell.adjacent_mines == 0:
        return " ", ""
    n = cell.adjacent_mines
    return str(n), (_COLOURS.get(n, "") if colour else "")


def _status_line(game: Minesweeper) -> str:
    if game.game_state == GameState.WON:
        verdict = "WON  ✓"
    elif game.game_state == GameState.LOST:
        verdict = "LOST ✗"
    else:
        verdict = "ONGOING"

    remaining = game.remaining_mines
    t = game.elapsed_time
    return (
        f"  Status: {verdict}  |  Mines left: {remaining:3d}"
        f"  |  Time: {t * 1000:.1f} ms"
    )
