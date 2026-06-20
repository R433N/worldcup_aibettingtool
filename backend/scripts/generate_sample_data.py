"""Generate a deterministic, clearly-labelled SAMPLE dataset.

This is **synthetic** data, not real results. It exists so the platform runs
end-to-end out of the box and so tests can verify the model recovers known
("ground-truth") team strengths. In production, replace the CSV repositories
with a real feed (e.g. football-data.org / API-Football) behind the same
repository interface.

The match results are sampled from a *true* Dixon-Coles process with known
parameters. The fixtures' bookmaker odds are built from the true probabilities,
then deliberately perturbed on a few selections and loaded with a realistic
margin (vig) so that genuine +EV "value" opportunities exist for the demo.

Run:  python -m scripts.generate_sample_data
"""

from __future__ import annotations

import csv
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"

# Ground-truth team strengths (attack, defence). Higher attack => scores more;
# higher defence => concedes fewer. Mean attack is ~0 by construction.
TRUE_TEAMS: dict[str, tuple[str, str, float, float]] = {
    # name: (code, confederation, attack, defence)
    "Brazil": ("BRA", "CONMEBOL", 0.85, 0.70),
    "France": ("FRA", "UEFA", 0.80, 0.65),
    "Argentina": ("ARG", "CONMEBOL", 0.78, 0.62),
    "England": ("ENG", "UEFA", 0.70, 0.55),
    "Spain": ("ESP", "UEFA", 0.68, 0.58),
    "Germany": ("GER", "UEFA", 0.66, 0.50),
    "Portugal": ("POR", "UEFA", 0.64, 0.48),
    "Netherlands": ("NED", "UEFA", 0.60, 0.52),
    "Belgium": ("BEL", "UEFA", 0.58, 0.40),
    "Croatia": ("CRO", "UEFA", 0.45, 0.42),
    "Uruguay": ("URU", "CONMEBOL", 0.48, 0.45),
    "Italy": ("ITA", "UEFA", 0.50, 0.55),
    "Morocco": ("MAR", "CAF", 0.35, 0.50),
    "USA": ("USA", "CONCACAF", 0.30, 0.20),
    "Mexico": ("MEX", "CONCACAF", 0.32, 0.18),
    "Japan": ("JPN", "AFC", 0.34, 0.22),
    "Senegal": ("SEN", "CAF", 0.30, 0.15),
    "Switzerland": ("SUI", "UEFA", 0.33, 0.30),
    "Denmark": ("DEN", "UEFA", 0.36, 0.28),
    "South Korea": ("KOR", "AFC", 0.25, 0.05),
    "Australia": ("AUS", "AFC", 0.10, 0.00),
    "Poland": ("POL", "UEFA", 0.22, 0.10),
    "Ghana": ("GHA", "CAF", 0.15, -0.10),
    "Canada": ("CAN", "CONCACAF", 0.18, -0.05),
}

TRUE_HOME_ADV = 0.30
TRUE_RHO = -0.06
SEED = 20260617
# International teams don't really play this many games, but this is synthetic
# SAMPLE data: a larger sample lets the MLE recover the ground-truth strengths
# cleanly so the demo reflects a well-fit model rather than estimation noise.
N_MATCHES = 4000
SPAN_DAYS = 730  # ~2 recent years so time-decay keeps most matches informative
MAX_GOALS = 12


def _sample_score(rng: np.random.Generator, lam: float, mu: float) -> tuple[int, int]:
    """Sample a scoreline from the Dixon-Coles distribution via rejection on the
    low-score tau correction over an independent-Poisson proposal."""
    while True:
        x = int(rng.poisson(lam))
        y = int(rng.poisson(mu))
        if x > 1 or y > 1:
            return min(x, MAX_GOALS), min(y, MAX_GOALS)
        # Apply tau acceptance for the four low-score cells.
        if x == 0 and y == 0:
            tau = 1.0 - lam * mu * TRUE_RHO
        elif x == 0 and y == 1:
            tau = 1.0 + lam * TRUE_RHO
        elif x == 1 and y == 0:
            tau = 1.0 + mu * TRUE_RHO
        else:  # (1, 1)
            tau = 1.0 - TRUE_RHO
        if rng.random() <= min(tau, 1.0) / 1.0:
            return x, y


def generate_matches() -> list[dict]:
    rng = np.random.default_rng(SEED)
    names = list(TRUE_TEAMS)
    start = date(2024, 6, 1)
    rows: list[dict] = []
    for _ in range(N_MATCHES):
        home, away = rng.choice(names, size=2, replace=False)
        a_h, d_h = TRUE_TEAMS[home][2], TRUE_TEAMS[home][3]
        a_a, d_a = TRUE_TEAMS[away][2], TRUE_TEAMS[away][3]
        # ~30% of internationals are neutral-venue / tournament; weight those higher.
        neutral = bool(rng.random() < 0.3)
        adv = 0.0 if neutral else TRUE_HOME_ADV
        lam = float(np.exp(a_h - d_a + adv))
        mu = float(np.exp(a_a - d_h))
        hg, ag = _sample_score(rng, lam, mu)
        played = start + timedelta(days=int(rng.integers(0, SPAN_DAYS)))
        rows.append(
            {
                "home": home,
                "away": away,
                "home_goals": hg,
                "away_goals": ag,
                "played_on": played.isoformat(),
                "neutral": int(neutral),
                "competition_weight": 1.0 if neutral else 0.8,
            }
        )
    rows.sort(key=lambda r: r["played_on"])
    return rows


def _decimal_from_prob(prob: float, margin: float) -> float:
    """Apply a per-selection share of the bookmaker margin and round like a book."""
    return round(1.0 / (prob * (1.0 + margin)), 2)


def generate_fixtures() -> tuple[list[dict], list[dict]]:
    """Return (fixtures rows, odds rows). Odds carry an intentional value edge."""
    from app.stats.dixon_coles import DixonColesModel
    from app.stats.markets import (
        btts_probabilities,
        match_result_probabilities,
        over_under_probabilities,
    )

    model = DixonColesModel(
        attack={n: TRUE_TEAMS[n][2] for n in TRUE_TEAMS},
        defence={n: TRUE_TEAMS[n][3] for n in TRUE_TEAMS},
        home_advantage=TRUE_HOME_ADV,
        rho=TRUE_RHO,
    )

    matchups = [
        ("Brazil", "Switzerland"),
        ("France", "Australia"),
        ("Argentina", "Mexico"),
        ("England", "USA"),
        ("Spain", "Japan"),
        ("Germany", "Morocco"),
        ("Portugal", "Ghana"),
        ("Netherlands", "Senegal"),
    ]

    margin = 0.06  # ~6% overround, typical for a sharp book
    kickoff = datetime(2026, 6, 21, 18, 0, 0)
    fixtures: list[dict] = []
    odds: list[dict] = []

    # Deterministic perturbations: nudge the book away from the true price on a
    # subset of selections to create both +EV and -EV cases.
    rng = np.random.default_rng(SEED + 1)

    for i, (home, away) in enumerate(matchups):
        fid = f"WC2026-{i + 1:02d}"
        fixtures.append(
            {
                "fixture_id": fid,
                "home": home,
                "away": away,
                "kickoff": (kickoff + timedelta(days=i // 2, hours=3 * (i % 2))).isoformat(),
                "neutral": 1,
            }
        )
        matrix = model.score_matrix(home, away, neutral=True, max_goals=MAX_GOALS)
        market_probs = {
            "1X2": match_result_probabilities(matrix),
            "OU_2.5": over_under_probabilities(matrix, 2.5),
            "BTTS": btts_probabilities(matrix),
        }
        for market, probs in market_probs.items():
            for selection, p in probs.items():
                # Perturb the *book's* implied probability around the true prob.
                bias = float(rng.normal(0.0, 0.06))
                book_p = float(np.clip(p * (1.0 + bias), 0.01, 0.97))
                odds.append(
                    {
                        "fixture_id": fid,
                        "market": market,
                        "bookmaker": "SampleBook",
                        "selection": selection,
                        "decimal_odds": _decimal_from_prob(book_p, margin),
                    }
                )

    return fixtures, odds


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    matches = generate_matches()
    write_csv(
        DATA_DIR / "matches.csv",
        matches,
        ["home", "away", "home_goals", "away_goals", "played_on", "neutral", "competition_weight"],
    )

    teams = [
        {"name": n, "code": v[0], "confederation": v[1]} for n, v in TRUE_TEAMS.items()
    ]
    write_csv(DATA_DIR / "teams.csv", teams, ["name", "code", "confederation"])

    fixtures, odds = generate_fixtures()
    write_csv(
        DATA_DIR / "fixtures.csv", fixtures, ["fixture_id", "home", "away", "kickoff", "neutral"]
    )
    write_csv(
        DATA_DIR / "odds.csv",
        odds,
        ["fixture_id", "market", "bookmaker", "selection", "decimal_odds"],
    )

    print(f"Wrote {len(matches)} matches, {len(teams)} teams, {len(fixtures)} fixtures, "
          f"{len(odds)} odds rows to {DATA_DIR}")


if __name__ == "__main__":
    main()
