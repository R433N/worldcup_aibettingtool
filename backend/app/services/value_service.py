"""The value engine: compares model probabilities against the market.

For each fixture/market/selection we:
  1. read the model probability from the prediction service,
  2. strip the bookmaker margin to a fair market probability,
  3. compute edge (model - fair), EV (p*odds - 1) and a fractional-Kelly stake,
  4. flag the selection as 'value' when it clears the configured thresholds.
"""

from __future__ import annotations

from dataclasses import asdict

from app.core.config import Settings
from app.domain.entities import Fixture
from app.domain.value import SelectionValue
from app.services.prediction_service import PredictionService
from app.stats.odds import expected_value, fair_probabilities, kelly_fraction, overround


class ValueService:
    def __init__(self, predictions: PredictionService, settings: Settings) -> None:
        self._predictions = predictions
        self._settings = settings

    def analyse_fixture(self, fixture: Fixture) -> dict:
        model_markets = self._predictions.market_probabilities(
            fixture.home, fixture.away, neutral=fixture.neutral
        )

        analysed_markets: list[dict] = []
        for book in fixture.odds:
            model_probs = model_markets.get(book.market)
            if not model_probs:
                continue

            # Keep selection order stable for vig removal across the market.
            selections = list(book.selections.keys())
            odds = [book.selections[s] for s in selections]
            fair = fair_probabilities(odds, method=self._settings.vig_method)
            fair_map = dict(zip(selections, fair, strict=True))

            values: list[SelectionValue] = []
            for s in selections:
                o = book.selections[s]
                p_model = float(model_probs.get(s, 0.0))
                p_fair = float(fair_map[s])
                edge = p_model - p_fair
                ev = expected_value(p_model, o)
                kelly = kelly_fraction(
                    p_model,
                    o,
                    fraction=self._settings.kelly_fraction,
                    cap=self._settings.kelly_cap,
                )
                is_value = (
                    edge >= self._settings.min_edge
                    and ev >= self._settings.min_expected_value
                    and kelly > 0.0
                )
                values.append(
                    SelectionValue(
                        market=book.market,
                        selection=s,
                        decimal_odds=o,
                        model_probability=round(p_model, 4),
                        market_probability=round(p_fair, 4),
                        edge=round(edge, 4),
                        expected_value=round(ev, 4),
                        kelly_fraction=round(kelly, 4),
                        is_value=is_value,
                    )
                )

            analysed_markets.append(
                {
                    "market": book.market,
                    "bookmaker": book.bookmaker,
                    "overround": round(overround(odds), 4),
                    "selections": [asdict(v) for v in values],
                }
            )

        return {
            "fixture_id": fixture.fixture_id,
            "home": fixture.home,
            "away": fixture.away,
            "kickoff": fixture.kickoff.isoformat(),
            "neutral": fixture.neutral,
            "markets": analysed_markets,
        }

    def best_value_bets(self, fixtures: list[Fixture]) -> list[dict]:
        """Flatten all fixtures to a single list of +value selections, best first."""
        bets: list[dict] = []
        for fixture in fixtures:
            analysis = self.analyse_fixture(fixture)
            for market in analysis["markets"]:
                for sel in market["selections"]:
                    if sel["is_value"]:
                        bets.append(
                            {
                                "fixture_id": analysis["fixture_id"],
                                "home": analysis["home"],
                                "away": analysis["away"],
                                "kickoff": analysis["kickoff"],
                                "market": market["market"],
                                "bookmaker": market["bookmaker"],
                                **sel,
                            }
                        )
        bets.sort(key=lambda b: b["expected_value"], reverse=True)
        return bets
