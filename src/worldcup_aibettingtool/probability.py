"""Football probability model based on calibrated Poisson score matrices."""

from __future__ import annotations

from math import exp, factorial

from .live_stats import team_summary
from .models import Fixture, MatchRecord, ProbabilitySnapshot


def build_probability_snapshot(
    fixture: Fixture,
    historical_matches: list[MatchRecord],
    live_xg_home: float = 0.0,
    live_xg_away: float = 0.0,
    live_minute: int = 0,
) -> ProbabilitySnapshot:
    home_stats = team_summary(fixture.home.name, historical_matches)
    away_stats = team_summary(fixture.away.name, historical_matches)

    home_xg = _expected_goals(
        scored=home_stats.goals_for_avg,
        opponent_conceded=away_stats.goals_against_avg,
        attack_rating=fixture.home.attack_rating,
        defense_rating=fixture.away.defense_rating,
        home_advantage=0.18,
    )
    away_xg = _expected_goals(
        scored=away_stats.goals_for_avg,
        opponent_conceded=home_stats.goals_against_avg,
        attack_rating=fixture.away.attack_rating,
        defense_rating=fixture.home.defense_rating,
        home_advantage=-0.05,
    )

    elapsed_share = max(0, min(live_minute, 90)) / 90
    if live_minute:
        remaining_share = 1 - elapsed_share
        home_xg = live_xg_home + home_xg * remaining_share
        away_xg = live_xg_away + away_xg * remaining_share

    fulltime = _result_probabilities(home_xg, away_xg)
    halftime = _result_probabilities(home_xg * 0.46, away_xg * 0.46)

    return ProbabilitySnapshot(
        fulltime_home_win=fulltime["home"],
        fulltime_draw=fulltime["draw"],
        fulltime_away_win=fulltime["away"],
        halftime_home_win=halftime["home"],
        halftime_draw=halftime["draw"],
        halftime_away_win=halftime["away"],
        double_chance_home_or_draw=fulltime["home"] + fulltime["draw"],
        double_chance_away_or_draw=fulltime["away"] + fulltime["draw"],
        double_chance_home_or_away=fulltime["home"] + fulltime["away"],
        expected_home_goals=round(home_xg, 2),
        expected_away_goals=round(away_xg, 2),
        top_scorelines=_top_scorelines(home_xg, away_xg),
    )


def _expected_goals(
    scored: float,
    opponent_conceded: float,
    attack_rating: float,
    defense_rating: float,
    home_advantage: float,
) -> float:
    baseline = 1.32
    blended = 0.50 * scored + 0.35 * opponent_conceded + 0.15 * baseline
    strength = attack_rating / max(defense_rating, 0.25)
    return max(0.2, min(3.8, blended * strength + home_advantage))


def _result_probabilities(home_xg: float, away_xg: float, max_goals: int = 8) -> dict[str, float]:
    matrix = _score_matrix(home_xg, away_xg, max_goals=max_goals)
    home = draw = away = 0.0
    for home_goals, row in enumerate(matrix):
        for away_goals, probability in enumerate(row):
            if home_goals > away_goals:
                home += probability
            elif home_goals < away_goals:
                away += probability
            else:
                draw += probability
    total = home + draw + away
    return {
        "home": home / total,
        "draw": draw / total,
        "away": away / total,
    }


def _score_matrix(home_xg: float, away_xg: float, max_goals: int = 8) -> list[list[float]]:
    home_dist = [_poisson(goal, home_xg) for goal in range(max_goals + 1)]
    away_dist = [_poisson(goal, away_xg) for goal in range(max_goals + 1)]
    return [[home_prob * away_prob for away_prob in away_dist] for home_prob in home_dist]


def _poisson(goal_count: int, expected_goals: float) -> float:
    return (expected_goals**goal_count * exp(-expected_goals)) / factorial(goal_count)


def _top_scorelines(home_xg: float, away_xg: float) -> tuple[tuple[str, float], ...]:
    outcomes: list[tuple[str, float]] = []
    matrix = _score_matrix(home_xg, away_xg, max_goals=6)
    for home_goals, row in enumerate(matrix):
        for away_goals, probability in enumerate(row):
            outcomes.append((f"{home_goals}-{away_goals}", probability))
    outcomes.sort(key=lambda item: item[1], reverse=True)
    return tuple((score, round(probability, 4)) for score, probability in outcomes[:5])
