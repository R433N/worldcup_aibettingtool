"""Dixon-Coles: tau correction, valid distributions, neutral-venue handling, and
the headline test — recovering known 'ground-truth' parameters from simulated
data (a parameter-recovery / calibration check)."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from app.domain.entities import MatchResult
from app.stats.dixon_coles import (
    DixonColesModel,
    dixon_coles_score_matrix,
    fit_dixon_coles,
    tau_correction,
)


def test_tau_correction_cells():
    lam, mu, rho = 1.5, 1.2, -0.05
    assert tau_correction(0, 0, lam, mu, rho) == pytest.approx(1.0 - lam * mu * rho)
    assert tau_correction(0, 1, lam, mu, rho) == pytest.approx(1.0 + lam * rho)
    assert tau_correction(1, 0, lam, mu, rho) == pytest.approx(1.0 + mu * rho)
    assert tau_correction(1, 1, lam, mu, rho) == pytest.approx(1.0 - rho)
    assert tau_correction(2, 3, lam, mu, rho) == 1.0  # unaffected


def test_dc_score_matrix_is_a_distribution():
    matrix = dixon_coles_score_matrix(1.5, 1.2, rho=-0.05, max_goals=12)
    assert matrix.sum() == pytest.approx(1.0)
    assert np.all(matrix >= 0)


def test_neutral_venue_drops_home_advantage():
    model = DixonColesModel(
        attack={"A": 0.5, "B": 0.0},
        defence={"A": 0.3, "B": 0.0},
        home_advantage=0.3,
        rho=-0.05,
    )
    lam_home, _ = model.expected_goals("A", "B", neutral=False)
    lam_neutral, _ = model.expected_goals("A", "B", neutral=True)
    assert lam_home > lam_neutral  # home advantage inflates home goals


def _simulate(rng, teams, attack, defence, home_adv, rho, n, start):
    rows = []
    names = list(teams)
    for _ in range(n):
        home, away = rng.choice(names, size=2, replace=False)
        lam = float(np.exp(attack[home] - defence[away] + home_adv))
        mu = float(np.exp(attack[away] - defence[home]))
        # Independent-Poisson sampling is sufficient for parameter recovery; the
        # tau correction only perturbs four low-score cells slightly.
        hg, ag = int(rng.poisson(lam)), int(rng.poisson(mu))
        played = start + timedelta(days=int(rng.integers(0, 700)))
        rows.append(MatchResult(home, away, hg, ag, played))
    return rows


def test_recovers_known_parameters():
    rng = np.random.default_rng(42)
    teams = ["A", "B", "C", "D", "E", "F"]
    true_attack = {"A": 0.6, "B": 0.3, "C": 0.1, "D": -0.1, "E": -0.4, "F": -0.5}
    true_defence = {"A": 0.5, "B": 0.2, "C": 0.0, "D": -0.1, "E": -0.3, "F": -0.3}
    # Centre truth the same way the fitter centres attack (mean 0).
    a_mean = np.mean(list(true_attack.values()))
    centred_attack = {t: v - a_mean for t, v in true_attack.items()}
    centred_defence = {t: v - a_mean for t, v in true_defence.items()}

    matches = _simulate(
        rng, teams, true_attack, true_defence, home_adv=0.3, rho=-0.05, n=4000,
        start=date(2024, 1, 1),
    )
    # xi=0 disables time decay so every match counts equally (cleanest recovery).
    model = fit_dixon_coles(matches, xi=0.0, max_goals=10)

    fitted_attack = np.array([model.attack[t] for t in teams])
    fitted_defence = np.array([model.defence[t] for t in teams])
    target_attack = np.array([centred_attack[t] for t in teams])
    target_defence = np.array([centred_defence[t] for t in teams])

    # Strong rank/level agreement and home advantage close to truth.
    assert np.corrcoef(fitted_attack, target_attack)[0, 1] > 0.95
    assert np.corrcoef(fitted_defence, target_defence)[0, 1] > 0.95
    assert np.max(np.abs(fitted_attack - target_attack)) < 0.15
    assert model.home_advantage == pytest.approx(0.3, abs=0.08)


def test_fit_rejects_empty():
    with pytest.raises(ValueError):
        fit_dixon_coles([])
