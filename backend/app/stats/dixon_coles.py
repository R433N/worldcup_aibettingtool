"""Dixon-Coles model for soccer scorelines.

Dixon, M.J. and Coles, S.G. (1997). "Modelling Association Football Scores and
Inefficiencies in the Football Betting Market." *Journal of the Royal
Statistical Society: Series C*, 46(2), 265-280.

Model
-----
For a match between home team *i* and away team *j*:

    lambda = exp(attack_i - defence_j + home_advantage)      # home expected goals
    mu     = exp(attack_j - defence_i)                        # away expected goals

Home goals ``X`` ~ Poisson(lambda), away goals ``Y`` ~ Poisson(mu), with a
low-score dependence correction ``tau`` applied to the (0,0), (1,0), (0,1) and
(1,1) cells via the parameter ``rho``. We fit by maximum likelihood with
exponential **time-decay** weighting ``phi(t) = exp(-xi * age_days)`` so recent
matches dominate the estimate (important for fast-changing international squads).

Identifiability: attack/defence are only defined up to an additive constant, so
we impose ``mean(attack) == 0`` after fitting.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson

from app.domain.entities import MatchResult


def tau_correction(x: int, y: int, lambda_: float, mu: float, rho: float) -> float:
    """Dixon-Coles low-score dependence adjustment for cell (x, y)."""
    if x == 0 and y == 0:
        return 1.0 - lambda_ * mu * rho
    if x == 0 and y == 1:
        return 1.0 + lambda_ * rho
    if x == 1 and y == 0:
        return 1.0 + mu * rho
    if x == 1 and y == 1:
        return 1.0 - rho
    return 1.0


def dixon_coles_score_matrix(
    lambda_home: float, lambda_away: float, rho: float, max_goals: int = 10
) -> np.ndarray:
    """Joint scoreline matrix with the Dixon-Coles tau correction applied."""
    home = poisson.pmf(np.arange(max_goals + 1), lambda_home)
    away = poisson.pmf(np.arange(max_goals + 1), lambda_away)
    matrix = np.outer(home, away)
    for x in (0, 1):
        for y in (0, 1):
            matrix[x, y] *= tau_correction(x, y, lambda_home, lambda_away, rho)
    matrix = np.clip(matrix, 0.0, None)
    total = matrix.sum()
    if total > 0:
        matrix = matrix / total
    return matrix


@dataclass
class DixonColesModel:
    """A fitted Dixon-Coles model."""

    attack: dict[str, float]
    defence: dict[str, float]
    home_advantage: float
    rho: float

    @property
    def teams(self) -> list[str]:
        return sorted(self.attack)

    def expected_goals(self, home: str, away: str, neutral: bool = False) -> tuple[float, float]:
        """Return (lambda_home, lambda_away) expected goals for a fixture.

        At neutral venues the home-advantage term is dropped (relevant for the
        World Cup, where all matches except the host's are on neutral ground).
        """
        if home not in self.attack:
            raise KeyError(f"Unknown team: {home!r}")
        if away not in self.attack:
            raise KeyError(f"Unknown team: {away!r}")
        adv = 0.0 if neutral else self.home_advantage
        lambda_home = np.exp(self.attack[home] - self.defence[away] + adv)
        lambda_away = np.exp(self.attack[away] - self.defence[home])
        return float(lambda_home), float(lambda_away)

    def score_matrix(
        self, home: str, away: str, neutral: bool = False, max_goals: int = 10
    ) -> np.ndarray:
        lambda_home, lambda_away = self.expected_goals(home, away, neutral)
        return dixon_coles_score_matrix(lambda_home, lambda_away, self.rho, max_goals)


def _time_weights(played: Sequence[date], reference: date, xi: float) -> np.ndarray:
    """Exponential decay weights based on match age in days."""
    ages = np.array([(reference - d).days for d in played], dtype=float)
    ages = np.clip(ages, 0.0, None)
    return np.exp(-xi * ages)


def fit_dixon_coles(
    matches: Sequence[MatchResult],
    xi: float = 0.0019,
    max_goals: int = 10,
    reference_date: date | None = None,
) -> DixonColesModel:
    """Fit a Dixon-Coles model by weighted maximum likelihood.

    Parameters
    ----------
    matches:
        Historical results.
    xi:
        Time-decay rate per day. ~0.0019 corresponds to a half-life of roughly
        one year, a reasonable default for international football.
    """
    if not matches:
        raise ValueError("Cannot fit a model with no matches")

    teams = sorted({t for m in matches for t in (m.home, m.away)})
    n = len(teams)
    idx = {t: i for i, t in enumerate(teams)}

    home_idx = np.array([idx[m.home] for m in matches])
    away_idx = np.array([idx[m.away] for m in matches])
    hg = np.array([m.home_goals for m in matches])
    ag = np.array([m.away_goals for m in matches])
    neutral = np.array([m.neutral for m in matches], dtype=bool)

    reference = reference_date or max(m.played_on for m in matches)
    comp_w = np.array([m.competition_weight for m in matches], dtype=float)
    weights = _time_weights([m.played_on for m in matches], reference, xi) * comp_w

    # Parameter vector: [attack(n), defence(n), home_advantage, rho]
    # attack constrained to mean 0 by fixing the first team's attack as
    # -sum(others) is awkward with the optimiser, so we instead re-centre after.
    def unpack(params: np.ndarray):
        attack = params[:n]
        defence = params[n : 2 * n]
        home_adv = params[2 * n]
        rho = params[2 * n + 1]
        return attack, defence, home_adv, rho

    def neg_log_likelihood(params: np.ndarray) -> float:
        attack, defence, home_adv, rho = unpack(params)
        adv = np.where(neutral, 0.0, home_adv)
        log_lambda = attack[home_idx] - defence[away_idx] + adv
        log_mu = attack[away_idx] - defence[home_idx]
        lam = np.exp(log_lambda)
        mu = np.exp(log_mu)

        # Poisson log-pmf (drop constant log(k!) term — irrelevant to the argmax).
        ll = hg * log_lambda - lam + ag * log_mu - mu

        # Tau correction only affects low scores; compute a multiplicative factor.
        tau = np.ones_like(lam)
        m00 = (hg == 0) & (ag == 0)
        m01 = (hg == 0) & (ag == 1)
        m10 = (hg == 1) & (ag == 0)
        m11 = (hg == 1) & (ag == 1)
        tau[m00] = 1.0 - lam[m00] * mu[m00] * rho
        tau[m01] = 1.0 + lam[m01] * rho
        tau[m10] = 1.0 + mu[m10] * rho
        tau[m11] = 1.0 - rho
        # Guard against the tau term going non-positive for extreme rho.
        tau = np.clip(tau, 1e-10, None)
        ll = ll + np.log(tau)

        return -float(np.sum(weights * ll))

    x0 = np.concatenate([np.zeros(n), np.zeros(n), [0.25], [-0.05]])
    # Keep rho in a sensible range; attack/defence/home unconstrained.
    bounds = [(-3.0, 3.0)] * (2 * n) + [(-1.0, 1.0), (-0.2, 0.2)]

    result = minimize(
        neg_log_likelihood,
        x0,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 500, "ftol": 1e-10},
    )

    attack, defence, home_adv, rho = unpack(result.x)
    # Re-centre attack to mean 0 for identifiability and shift defence equally so
    # the fitted lambdas are unchanged.
    shift = float(np.mean(attack))
    attack = attack - shift
    defence = defence - shift

    return DixonColesModel(
        attack={t: float(attack[idx[t]]) for t in teams},
        defence={t: float(defence[idx[t]]) for t in teams},
        home_advantage=float(home_adv),
        rho=float(rho),
    )
