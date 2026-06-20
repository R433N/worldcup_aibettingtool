"""Market math: vig removal, EV and Kelly. These are the bankroll-critical bits."""

from __future__ import annotations

import numpy as np
import pytest

from app.stats.odds import (
    expected_value,
    fair_probabilities,
    implied_probability,
    kelly_fraction,
    overround,
)


def test_implied_probability():
    assert implied_probability(2.0) == pytest.approx(0.5)
    assert implied_probability(4.0) == pytest.approx(0.25)


def test_implied_probability_rejects_invalid_odds():
    with pytest.raises(ValueError):
        implied_probability(1.0)


def test_overround_is_positive_for_a_real_book():
    # A fair coin priced at 1.95/1.95 carries a positive margin.
    assert overround([1.95, 1.95]) == pytest.approx(2 / 1.95 - 1.0)


def test_fair_probabilities_proportional_sum_to_one():
    probs = fair_probabilities([2.1, 3.5, 3.8], method="proportional")
    assert probs.sum() == pytest.approx(1.0)
    assert np.all(probs > 0)


def test_fair_probabilities_shin_sum_to_one():
    probs = fair_probabilities([2.1, 3.5, 3.8], method="shin")
    assert probs.sum() == pytest.approx(1.0, abs=1e-9)
    assert np.all(probs > 0)


def test_shin_corrects_favourite_longshot_bias():
    # Shin's method counters the favourite-longshot bias: relative to naive
    # normalisation it assigns MORE probability to the favourite and LESS to the
    # longshot. Favourite is the first selection, longshot the last.
    odds = [1.5, 4.5, 7.0]
    prop = fair_probabilities(odds, method="proportional")
    shin = fair_probabilities(odds, method="shin")
    assert shin[0] > prop[0]
    assert shin[-1] < prop[-1]


def test_fair_probabilities_unknown_method():
    with pytest.raises(ValueError):
        fair_probabilities([2.0, 2.0], method="nope")


def test_expected_value_zero_at_fair_odds():
    # True prob 0.5 at fair decimal odds 2.0 => EV exactly 0.
    assert expected_value(0.5, 2.0) == pytest.approx(0.0)


def test_expected_value_positive_when_underpriced():
    # We think 0.55 but odds imply 0.5 => +EV.
    assert expected_value(0.55, 2.0) == pytest.approx(0.10)


def test_kelly_zero_for_non_positive_edge():
    assert kelly_fraction(0.5, 2.0) == 0.0  # EV neutral
    assert kelly_fraction(0.4, 2.0) == 0.0  # -EV


def test_kelly_matches_closed_form():
    # f* = (b p - q)/b. p=0.6, odds=2.0 => b=1, q=0.4 => f*=0.2.
    # Quarter-Kelly => 0.05; cap default 0.05 => 0.05.
    assert kelly_fraction(0.6, 2.0, fraction=0.25, cap=1.0) == pytest.approx(0.05)
    assert kelly_fraction(0.6, 2.0, fraction=1.0, cap=1.0) == pytest.approx(0.20)


def test_kelly_is_capped():
    assert kelly_fraction(0.95, 5.0, fraction=1.0, cap=0.05) == pytest.approx(0.05)
