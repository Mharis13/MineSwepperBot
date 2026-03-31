"""Minesweeper constraint-based solver with probabilistic fallback.

Algorithm
---------
1. **Constraint extraction** — every revealed number cell with hidden neighbours
   produces a constraint ``{cells} → k mines``.
2. **Trivial deduction** — if ``k == 0`` all cells are safe; if ``k == |cells|``
   all cells are mines.
3. **Subset / difference reduction** — when one constraint's cell-set is a
   subset of another's, a new reduced constraint is derived, which often yields
   additional trivial deductions.
4. **Probabilistic guessing** — when no deterministic move exists, estimate each
   hidden cell's mine probability and pick the safest option (lowest probability).
   Non-frontier cells use a global estimate; frontier cells use a per-constraint
   weighted average.

The solver is designed for speed (pure Python, no external dependencies) and
correctness; it will not flag a cell unless it is 100 % certain it is a mine.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from .game import CellState, GameState, Minesweeper


# ---------------------------------------------------------------------------
# Constraint representation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Constraint:
    """A single Minesweeper constraint: *mines* mines among *cells*."""

    cells: FrozenSet[Tuple[int, int]]
    mines: int

    def __repr__(self) -> str:
        return f"Constraint(mines={self.mines}, cells={len(self.cells)})"


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------

class Solver:
    """Stateless solver — call :meth:`next_move` to get the next action."""

    def __init__(self, game: Minesweeper) -> None:
        self.game = game
        self._first_move = True

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def next_move(self) -> Tuple[str, int, int, bool]:
        """Return the next recommended move as ``(action, row, col, is_guess)``.

        *action* is one of ``"reveal"`` or ``"flag"``.
        *is_guess* is ``True`` when the move is probabilistic (no deterministic
        solution was found).
        """
        game = self.game

        # First move: pick centre cell for the best statistical opening
        if self._first_move:
            self._first_move = False
            r = game.rows // 2
            c = game.cols // 2
            return ("reveal", r, c, False)

        safe, mines = self._deduce()

        if mines:
            r, c = next(iter(mines))
            return ("flag", r, c, False)

        if safe:
            r, c = next(iter(safe))
            return ("reveal", r, c, False)

        # Probabilistic guess
        r, c = self._best_guess()
        return ("reveal", r, c, True)

    # ------------------------------------------------------------------
    # Constraint building
    # ------------------------------------------------------------------

    def _get_constraints(self) -> List[Constraint]:
        """Build one constraint per satisfied revealed number cell."""
        game = self.game
        constraints: List[Constraint] = []

        for r in range(game.rows):
            for c in range(game.cols):
                cell = game.board[r][c]
                if cell.state != CellState.REVEALED:
                    continue
                if cell.adjacent_mines == 0:
                    continue

                hidden: FrozenSet[Tuple[int, int]] = frozenset(
                    (nr, nc)
                    for nr, nc in game.neighbors(r, c)
                    if game.board[nr][nc].state == CellState.HIDDEN
                )
                flagged = sum(
                    1
                    for nr, nc in game.neighbors(r, c)
                    if game.board[nr][nc].state == CellState.FLAGGED
                )
                remaining = cell.adjacent_mines - flagged
                if hidden:
                    constraints.append(Constraint(hidden, remaining))

        return constraints

    # ------------------------------------------------------------------
    # Deterministic deduction
    # ------------------------------------------------------------------

    def _deduce(self) -> Tuple[Set[Tuple[int, int]], Set[Tuple[int, int]]]:
        """Return (safe_cells, mine_cells) derived by constraint reasoning."""
        constraints = self._get_constraints()
        safe: Set[Tuple[int, int]] = set()
        mines: Set[Tuple[int, int]] = set()

        changed = True
        while changed:
            changed = False

            # Trivial deductions
            for c in constraints:
                if c.mines == 0:
                    new = c.cells - safe
                    if new:
                        safe.update(new)
                        changed = True
                elif c.mines == len(c.cells):
                    new = c.cells - mines
                    if new:
                        mines.update(new)
                        changed = True

            # Subset reduction: derive new constraints
            new_constraints: List[Constraint] = []
            constraint_set = set(constraints)
            for i, c1 in enumerate(constraints):
                for c2 in constraints[i + 1:]:
                    derived = self._subtract(c1, c2)
                    if derived is not None and derived not in constraint_set:
                        new_constraints.append(derived)
                        constraint_set.add(derived)
                        changed = True
                    derived = self._subtract(c2, c1)
                    if derived is not None and derived not in constraint_set:
                        new_constraints.append(derived)
                        constraint_set.add(derived)
                        changed = True
            constraints.extend(new_constraints)

        # Remove already-revealed / flagged cells (shouldn't be in hidden sets,
        # but guard defensively)
        game = self.game
        not_hidden: Set[Tuple[int, int]] = {
            (r, c)
            for r in range(game.rows)
            for c in range(game.cols)
            if game.board[r][c].state != CellState.HIDDEN
        }
        safe -= not_hidden
        mines -= not_hidden

        return safe, mines

    @staticmethod
    def _subtract(c1: Constraint, c2: Constraint) -> Optional[Constraint]:
        """If *c1* ⊆ *c2*, return the reduced constraint *c2 − c1*."""
        if not c1.cells or not c1.cells.issubset(c2.cells):
            return None
        diff_cells = c2.cells - c1.cells
        diff_mines = c2.mines - c1.mines
        if diff_mines < 0 or diff_mines > len(diff_cells):
            return None
        return Constraint(frozenset(diff_cells), diff_mines)

    # ------------------------------------------------------------------
    # Probabilistic fallback
    # ------------------------------------------------------------------

    def _best_guess(self) -> Tuple[int, int]:
        """Pick the hidden cell with the lowest estimated mine probability."""
        game = self.game
        constraints = self._get_constraints()

        # All hidden cells
        hidden: List[Tuple[int, int]] = [
            (r, c)
            for r in range(game.rows)
            for c in range(game.cols)
            if game.board[r][c].state == CellState.HIDDEN
        ]
        if not hidden:
            # Should not happen, but fall back gracefully
            return (game.rows // 2, game.cols // 2)

        # Frontier cells: appear in at least one constraint
        frontier: Set[Tuple[int, int]] = set()
        for c in constraints:
            frontier.update(c.cells)

        non_frontier = [cell for cell in hidden if cell not in frontier]

        # Estimate total remaining mines (flagged mines subtracted)
        flagged_count = sum(
            1
            for r in range(game.rows)
            for c in range(game.cols)
            if game.board[r][c].state == CellState.FLAGGED
        )
        remaining_mines = game.num_mines - flagged_count

        # Non-frontier probability (mines uniformly distributed)
        if non_frontier:
            # Estimate how many mines are outside the frontier
            # Use a conservative lower-bound: remaining − max possible in frontier
            max_frontier_mines = sum(c.mines for c in constraints) if constraints else 0
            non_frontier_mines = max(0, remaining_mines - max_frontier_mines)
            nf_prob = non_frontier_mines / len(non_frontier) if non_frontier else 1.0
        else:
            nf_prob = 1.0

        # Frontier probability per cell (weighted average over constraints)
        mine_prob_sum: Dict[Tuple[int, int], float] = {}
        mine_prob_cnt: Dict[Tuple[int, int], int] = {}
        for c in constraints:
            if not c.cells:
                continue
            p = c.mines / len(c.cells)
            for cell in c.cells:
                mine_prob_sum[cell] = mine_prob_sum.get(cell, 0.0) + p
                mine_prob_cnt[cell] = mine_prob_cnt.get(cell, 0) + 1

        def probability(cell: Tuple[int, int]) -> float:
            if cell in frontier and mine_prob_cnt.get(cell, 0) > 0:
                return mine_prob_sum[cell] / mine_prob_cnt[cell]
            return nf_prob

        # Among non-frontier cells, prefer centre of board (better opening)
        if non_frontier and nf_prob < min(
            (mine_prob_sum.get(cell, nf_prob * mine_prob_cnt.get(cell, 1))
             / max(mine_prob_cnt.get(cell, 1), 1))
            for cell in frontier
        ) if frontier else True:
            cr, cc = game.rows // 2, game.cols // 2
            return min(non_frontier, key=lambda x: abs(x[0] - cr) + abs(x[1] - cc))

        best = min(hidden, key=probability)
        return best
