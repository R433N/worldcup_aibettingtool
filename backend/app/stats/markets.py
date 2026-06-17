"""Derive betting-market probabilities from a joint scoreline matrix.

Computing every market from a *single* scoreline distribution guarantees the
probabilities are mutually consistent (e.g. 1X2 and Over/Under cannot disagree
about the same underlying matrix).
"""

from __future__ import annotations

import numpy as np


def match_result_probabilities(matrix: np.ndarray) -> dict[str, float]:
    """1X2 probabilities from the scoreline matrix."""
    home = float(np.tril(matrix, -1).sum())  # x > y
    away = float(np.triu(matrix, 1).sum())  # x < y
    draw = float(np.trace(matrix))  # x == y
    return {"HOME": home, "DRAW": draw, "AWAY": away}


def over_under_probabilities(matrix: np.ndarray, line: float = 2.5) -> dict[str, float]:
    """Over/Under total-goals probabilities for a (half-integer) line."""
    n = matrix.shape[0]
    totals = np.add.outer(np.arange(n), np.arange(n))
    over = float(matrix[totals > line].sum())
    under = float(matrix[totals < line].sum())
    return {"OVER": over, "UNDER": under}


def btts_probabilities(matrix: np.ndarray) -> dict[str, float]:
    """Both-teams-to-score probabilities."""
    yes = float(matrix[1:, 1:].sum())
    no = float(1.0 - yes)
    return {"YES": yes, "NO": no}


def expected_goals_from_matrix(matrix: np.ndarray) -> tuple[float, float]:
    """Recover (E[home goals], E[away goals]) from the matrix (useful for tests)."""
    n = matrix.shape[0]
    goals = np.arange(n)
    home = float((matrix.sum(axis=1) * goals).sum())
    away = float((matrix.sum(axis=0) * goals).sum())
    return home, away
