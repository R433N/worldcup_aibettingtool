"""Poisson baseline: distributions must be valid and recover their own moments."""

from __future__ import annotations

import numpy as np
import pytest

from app.stats.markets import expected_goals_from_matrix
from app.stats.poisson import independent_score_matrix, poisson_pmf_vector


def test_pmf_sums_to_one():
    pmf = poisson_pmf_vector(1.4, max_goals=15)
    assert pmf.sum() == pytest.approx(1.0, abs=1e-6)


def test_pmf_rejects_negative_rate():
    with pytest.raises(ValueError):
        poisson_pmf_vector(-1.0, 5)


def test_score_matrix_is_a_distribution():
    matrix = independent_score_matrix(1.6, 1.1, max_goals=12)
    assert matrix.sum() == pytest.approx(1.0)
    assert np.all(matrix >= 0)


def test_score_matrix_recovers_expected_goals():
    matrix = independent_score_matrix(1.6, 1.1, max_goals=15)
    exp_home, exp_away = expected_goals_from_matrix(matrix)
    assert exp_home == pytest.approx(1.6, abs=1e-3)
    assert exp_away == pytest.approx(1.1, abs=1e-3)
