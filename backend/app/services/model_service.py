"""Fits and holds the Dixon-Coles model.

Fitting is moderately expensive (an MLE optimisation), so we fit once and cache.
``refit`` allows re-fitting after the underlying data changes.
"""

from __future__ import annotations

from typing import Any

from app.core.config import Settings
from app.infrastructure.repositories import MatchRepository
from app.stats.dixon_coles import DixonColesModel, fit_dixon_coles


class ModelService:
    def __init__(self, matches: MatchRepository, settings: Settings) -> None:
        self._matches = matches
        self._settings = settings
        self._model: DixonColesModel | None = None

    @property
    def model(self) -> DixonColesModel:
        if self._model is None:
            self.refit()
        assert self._model is not None
        return self._model

    def refit(self) -> DixonColesModel:
        self._model = fit_dixon_coles(
            self._matches.list_matches(),
            xi=self._settings.time_decay_xi,
            max_goals=self._settings.max_goals,
        )
        return self._model

    def ratings(self) -> list[dict[str, Any]]:
        """Per-team attack/defence ratings, sorted by overall strength.

        We expose a single ``overall = attack + defence`` score for ranking, but
        the underlying attack/defence are what drive predictions.
        """
        m = self.model
        rows: list[dict[str, Any]] = [
            {
                "team": t,
                "attack": round(m.attack[t], 4),
                "defence": round(m.defence[t], 4),
                "overall": round(m.attack[t] + m.defence[t], 4),
            }
            for t in m.teams
        ]
        rows.sort(key=lambda r: r["overall"], reverse=True)
        for rank, row in enumerate(rows, start=1):
            row["rank"] = rank
        return rows
