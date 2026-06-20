"""Value-betting value objects.

These capture the *output* of the analytics pipeline for a single selection:
the model probability, the vig-free market probability, the resulting edge,
expected value, and recommended (fractional Kelly) stake.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SelectionValue:
    market: str
    selection: str
    decimal_odds: float
    model_probability: float
    market_probability: float  # vig-free (fair) probability implied by the book
    edge: float  # model_probability - market_probability
    expected_value: float  # EV per unit staked = p*odds - 1
    kelly_fraction: float  # fractional-Kelly stake as a fraction of bankroll
    is_value: bool
