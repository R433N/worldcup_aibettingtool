"""Odds, vig removal, expected value and staking math.

References
---------
- Vig (overround) removal: proportional (a.k.a. "basic"/normalisation) and
  Shin (1992, 1993) which models a fraction ``z`` of insider/informed money.
- Kelly criterion (Kelly, 1956) for log-optimal bankroll growth. We expose a
  ``fraction`` multiplier because full Kelly is too aggressive once you account
  for estimation error in the model probabilities.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def implied_probability(decimal_odds: float) -> float:
    """Raw (vig-inclusive) probability implied by a single decimal price."""
    if decimal_odds <= 1.0:
        raise ValueError("Decimal odds must be > 1.0")
    return 1.0 / decimal_odds


def overround(decimal_odds: Sequence[float]) -> float:
    """Bookmaker margin for a market = sum(1/odds) - 1 (a.k.a. the 'vig')."""
    return float(np.sum([1.0 / o for o in decimal_odds]) - 1.0)


def fair_probabilities(
    decimal_odds: Sequence[float], method: str = "proportional"
) -> np.ndarray:
    """Remove the bookmaker margin to recover vig-free ('fair') probabilities.

    Parameters
    ----------
    decimal_odds:
        Decimal odds for every selection in a single market.
    method:
        - ``"proportional"``: divide each implied prob by the booksum. Simple but
          biases probabilities toward favourites (the "favourite-longshot" issue).
        - ``"shin"``: Shin's method, which assumes a proportion ``z`` of money is
          from insiders and solves for it. Generally better calibrated.
    """
    odds = np.asarray(decimal_odds, dtype=float)
    if np.any(odds <= 1.0):
        raise ValueError("All decimal odds must be > 1.0")
    raw = 1.0 / odds

    if method == "proportional":
        return raw / raw.sum()
    if method == "shin":
        return _shin_probabilities(raw)
    raise ValueError(f"Unknown vig-removal method: {method!r}")


def _shin_probabilities(raw: np.ndarray, max_iter: int = 200, tol: float = 1e-12) -> np.ndarray:
    """Solve Shin's model for the insider fraction ``z`` via fixed-point iteration.

    Fair prob_i = (sqrt(z^2 + 4(1-z) * raw_i^2 / booksum) - z) / (2(1-z)),
    with the standard update z = (sum_i adj_i - 2) / (n - 2). Falls back to the
    proportional method when n <= 2 (the update is undefined there).
    """
    n = len(raw)
    booksum = raw.sum()
    if n <= 2:
        return raw / booksum

    z = 0.0
    for _ in range(max_iter):
        adj = np.sqrt(z * z + 4.0 * (1.0 - z) * raw * raw / booksum)
        new_z = float((adj.sum() - 2.0) / (n - 2.0))
        new_z = min(max(new_z, 0.0), 0.5)
        if abs(new_z - z) < tol:
            z = new_z
            break
        z = new_z

    adj = np.sqrt(z * z + 4.0 * (1.0 - z) * raw * raw / booksum)
    probs = (adj - z) / (2.0 * (1.0 - z))
    return probs / probs.sum()


def expected_value(probability: float, decimal_odds: float) -> float:
    """EV per unit staked for a back bet = p * odds - 1.

    EV > 0 means the bet is +EV (theoretically profitable long-run).
    """
    return probability * decimal_odds - 1.0


def kelly_fraction(
    probability: float, decimal_odds: float, fraction: float = 0.25, cap: float = 0.05
) -> float:
    """Recommended stake as a fraction of bankroll (fractional, capped Kelly).

    Full Kelly f* = (b*p - q) / b, with b = odds - 1, q = 1 - p. We scale by
    ``fraction`` (default quarter-Kelly) for safety and cap the result so a single
    bet can never risk an outsized share of the bankroll. Negative edges return 0.
    """
    b = decimal_odds - 1.0
    if b <= 0:
        return 0.0
    q = 1.0 - probability
    full = (b * probability - q) / b
    if full <= 0:
        return 0.0
    return float(min(full * fraction, cap))
