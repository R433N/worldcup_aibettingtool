"""Dependency wiring (a tiny composition root).

A single cached container builds repositories and services from settings. The
``ModelService`` fits the Dixon-Coles model lazily on first use and caches it, so
the expensive MLE runs once per process rather than per request.
"""

from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.infrastructure.repositories import (
    CsvFixtureRepository,
    CsvMatchRepository,
    CsvTeamRepository,
)
from app.services.model_service import ModelService
from app.services.prediction_service import PredictionService
from app.services.value_service import ValueService


class Container:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.matches = CsvMatchRepository(settings.matches_csv)
        self.teams = CsvTeamRepository(settings.matches_csv.parent / "teams.csv")
        self.fixtures = CsvFixtureRepository(
            settings.fixtures_csv, settings.fixtures_csv.parent / "odds.csv"
        )
        self.model_service = ModelService(self.matches, settings)
        self.prediction_service = PredictionService(self.model_service, settings)
        self.value_service = ValueService(self.prediction_service, settings)


@lru_cache
def get_container() -> Container:
    return Container(get_settings())


def get_model_service() -> ModelService:
    return get_container().model_service


def get_prediction_service() -> PredictionService:
    return get_container().prediction_service


def get_value_service() -> ValueService:
    return get_container().value_service
