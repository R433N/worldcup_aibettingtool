"""Poisson scoreline model (the baseline that Dixon-Coles generalises).

Goals scored by each team are modelled as independent Poisson variables with
means ``lambda_home`` and ``lambda_away``. The joint scoreline distribution is
the outer product of the two marginal PMFs.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import poisson


def poisson_pmf_vector(rate: float, max_goals: int) -> np.ndarray:
    """PMF over 0..max_goals for a Poisson with the given rate."""
    if rate < 0:
        raise ValueError("Poisson rate must be non-negative")
    k = np.arange(0, max_goals + 1)
    return poisson.pmf(k, rate)


def independent_score_matrix(
    lambda_home: float, lambda_away: float, max_goals: int = 10
) -> np.ndarray:
    """Joint scoreline matrix P[x, y] for independent Poisson goals.

    Row index ``x`` = home goals, column index ``y`` = away goals. The matrix is
    truncated at ``max_goals`` and renormalised so it sums to exactly 1.
    """
    home = poisson_pmf_vector(lambda_home, max_goals)
    away = poisson_pmf_vector(lambda_away, max_goals)
    matrix = np.outer(home, away)
    total = matrix.sum()
    if total > 0:
        matrix = matrix / total
    return matrix
