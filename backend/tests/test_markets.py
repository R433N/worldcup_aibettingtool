"""Market derivation: every market is a valid distribution and they are mutually
consistent because they come from one scoreline matrix."""

from __future__ import annotations

import pytest

from app.stats.dixon_coles import dixon_coles_score_matrix
from app.stats.markets import (
    btts_probabilities,
    match_result_probabilities,
    over_under_probabilities,
)


@pytest.fixture
def matrix():
    return dixon_coles_score_matrix(1.7, 1.0, rho=-0.05, max_goals=12)


def test_1x2_sums_to_one(matrix):
    probs = match_result_probabilities(matrix)
    assert sum(probs.values()) == pytest.approx(1.0)
    # Stronger home side should be favoured.
    assert probs["HOME"] > probs["AWAY"]


def test_over_under_sums_to_one(matrix):
    probs = over_under_probabilities(matrix, 2.5)
    assert probs["OVER"] + probs["UNDER"] == pytest.approx(1.0)


def test_btts_sums_to_one(matrix):
    probs = btts_probabilities(matrix)
    assert probs["YES"] + probs["NO"] == pytest.approx(1.0)


def test_all_probabilities_are_valid(matrix):
    for probs in (
        match_result_probabilities(matrix),
        over_under_probabilities(matrix, 2.5),
        btts_probabilities(matrix),
    ):
        for p in probs.values():
            assert 0.0 <= p <= 1.0
