"""Odds ingestion and value calculations."""

from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

from .models import BetMarket, OddsValue, ProbabilitySnapshot


class Bet365OddsProvider:
    """Adapter for licensed Bet365 odds exports.

    Set BET365_ODDS_JSON to a JSON file path or pass one directly. The expected
    shape is a list of {"market", "selection", "decimal_odds"} objects.
    """

    sportsbook = "Bet365"

    def __init__(self, json_path: str | Path | None = None):
        configured_path = json_path or os.getenv("BET365_ODDS_JSON")
        self.json_path = Path(configured_path) if configured_path else None

    def fetch(self) -> list[BetMarket]:
        if not self.json_path:
            raise FileNotFoundError("Set BET365_ODDS_JSON or pass a Bet365 odds export path.")
        raw = json.loads(self.json_path.read_text(encoding="utf-8"))
        return [
            BetMarket(
                market=item["market"],
                selection=item["selection"],
                decimal_odds=float(item["decimal_odds"]),
                sportsbook=self.sportsbook,
            )
            for item in raw
        ]


def evaluate_odds(markets: list[BetMarket], probabilities: ProbabilitySnapshot) -> list[OddsValue]:
    grouped: dict[str, list[BetMarket]] = defaultdict(list)
    for market in markets:
        grouped[market.market].append(market)

    values: list[OddsValue] = []
    for market_name, market_rows in grouped.items():
        implied_sum = sum(1 / row.decimal_odds for row in market_rows)
        for market in market_rows:
            sportsbook_probability = 1 / market.decimal_odds
            no_vig = sportsbook_probability / implied_sum if implied_sum else 0.0
            model_probability = _model_probability(market.market, market.selection, probabilities)
            expected_roi = market.decimal_odds * model_probability - 1
            edge = model_probability - no_vig
            values.append(
                OddsValue(
                    market=market.market,
                    selection=market.selection,
                    sportsbook=market.sportsbook,
                    decimal_odds=market.decimal_odds,
                    sportsbook_probability=round(sportsbook_probability, 4),
                    no_vig_probability=round(no_vig, 4),
                    model_probability=round(model_probability, 4),
                    expected_roi=round(expected_roi, 4),
                    edge=round(edge, 4),
                    allocation_pct=_allocation_pct(market.decimal_odds, model_probability),
                    risk=_risk_band(market.market, market.selection, market.decimal_odds),
                )
            )
    return sorted(values, key=lambda row: (row.expected_roi, row.edge), reverse=True)


def _model_probability(market: str, selection: str, probabilities: ProbabilitySnapshot) -> float:
    key = f"{market}:{selection}".lower()
    mapping = {
        "fulltime result:home": probabilities.fulltime_home_win,
        "fulltime result:draw": probabilities.fulltime_draw,
        "fulltime result:away": probabilities.fulltime_away_win,
        "halftime result:home": probabilities.halftime_home_win,
        "halftime result:draw": probabilities.halftime_draw,
        "halftime result:away": probabilities.halftime_away_win,
        "double chance:home or draw": probabilities.double_chance_home_or_draw,
        "double chance:away or draw": probabilities.double_chance_away_or_draw,
        "double chance:home or away": probabilities.double_chance_home_or_away,
    }
    if key in mapping:
        return mapping[key]
    total_xg = probabilities.expected_home_goals + probabilities.expected_away_goals
    both_score_proxy = min(probabilities.expected_home_goals, probabilities.expected_away_goals) / 1.45
    totals_mapping = {
        "total goals:over 1.5": min(0.92, total_xg / 3.2),
        "total goals:over 2.5": min(0.82, total_xg / 4.4),
        "total goals:under 3.5": max(0.18, 1 - total_xg / 5.2),
        "btts:yes": min(0.78, both_score_proxy),
        "btts:no": 1 - min(0.78, both_score_proxy),
    }
    return max(0.01, min(0.99, totals_mapping.get(key, 0.0)))


def _allocation_pct(decimal_odds: float, model_probability: float) -> float:
    b = decimal_odds - 1
    q = 1 - model_probability
    kelly = ((b * model_probability) - q) / b if b else 0.0
    return round(max(0.0, min(kelly * 0.35, 0.08)) * 100, 2)


def _risk_band(market: str, selection: str, decimal_odds: float) -> str:
    if market == "Double Chance" or decimal_odds < 1.55:
        return "Low"
    if market in {"Fulltime Result", "BTTS", "Total Goals"} and decimal_odds < 2.35:
        return "Medium"
    return "High"


def total_money_allocation(values: list[OddsValue]) -> float:
    return round(sum(value.allocation_pct for value in values if value.expected_roi > 0), 2)
