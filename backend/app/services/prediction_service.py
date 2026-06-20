"""Turns a fitted model into market probabilities for a matchup."""

from __future__ import annotations

from app.core.config import Settings
from app.domain.markets import Market
from app.services.model_service import ModelService
from app.stats.markets import (
    btts_probabilities,
    expected_goals_from_matrix,
    match_result_probabilities,
    over_under_probabilities,
)


class PredictionService:
    def __init__(self, model_service: ModelService, settings: Settings) -> None:
        self._model_service = model_service
        self._settings = settings

    def predict(self, home: str, away: str, neutral: bool = True) -> dict:
        model = self._model_service.model
        matrix = model.score_matrix(
            home, away, neutral=neutral, max_goals=self._settings.max_goals
        )
        exp_home, exp_away = expected_goals_from_matrix(matrix)
        return {
            "home": home,
            "away": away,
            "neutral": neutral,
            "expected_goals": {"home": round(exp_home, 3), "away": round(exp_away, 3)},
            "markets": {
                Market.MATCH_RESULT.value: match_result_probabilities(matrix),
                Market.OVER_UNDER_2_5.value: over_under_probabilities(matrix, 2.5),
                Market.BTTS.value: btts_probabilities(matrix),
            },
        }

    def market_probabilities(self, home: str, away: str, neutral: bool = True) -> dict[str, dict]:
        return self.predict(home, away, neutral)["markets"]
