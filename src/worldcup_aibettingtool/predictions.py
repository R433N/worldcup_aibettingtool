"""Prediction selection for best bets and parlay construction."""

from __future__ import annotations

from .models import OddsValue, PredictionCard


def build_predictions(values: list[OddsValue]) -> dict[str, PredictionCard | dict]:
    positive = [value for value in values if value.expected_roi > 0 and value.allocation_pct > 0]
    by_risk = {
        "Low": _best_for_risk(positive, "Low"),
        "Medium": _best_for_risk(positive, "Medium"),
        "High": _best_for_risk(positive, "High"),
    }
    best_pick = max(positive, key=lambda row: (row.expected_roi, row.model_probability), default=None)
    return {
        "low_risk": _card(by_risk["Low"], "Low-risk value"),
        "medium_risk": _card(by_risk["Medium"], "Medium-risk value"),
        "high_risk": _card(by_risk["High"], "High-risk value"),
        "best_pick": _card(best_pick, "Best single pick"),
        "best_parlay": build_best_parlay(positive),
    }


def build_best_parlay(values: list[OddsValue], minimum_odds: float = 1.70, target_odds: float = 2.00) -> dict:
    candidates = sorted(
        values,
        key=lambda row: (row.edge, row.model_probability, -row.decimal_odds),
        reverse=True,
    )
    legs: list[OddsValue] = []
    odds = 1.0
    for candidate in candidates:
        if any(candidate.market == leg.market for leg in legs):
            continue
        legs.append(candidate)
        odds *= candidate.decimal_odds
        if odds >= target_odds:
            break
    if odds < minimum_odds and candidates:
        for candidate in candidates:
            if candidate in legs:
                continue
            legs.append(candidate)
            odds *= candidate.decimal_odds
            if odds >= minimum_odds:
                break

    probability = 1.0
    expected_roi = odds - 1
    for leg in legs:
        probability *= leg.model_probability
    if legs:
        expected_roi = odds * probability - 1

    return {
        "title": "Best parlay",
        "minimum_odds_met": odds >= minimum_odds,
        "target_odds_met": odds >= target_odds,
        "combined_odds": round(odds, 2),
        "model_probability": round(probability, 4),
        "expected_roi": round(expected_roi, 4),
        "legs": [
            {
                "market": leg.market,
                "selection": leg.selection,
                "odds": leg.decimal_odds,
                "edge": leg.edge,
            }
            for leg in legs
        ],
    }


def _best_for_risk(values: list[OddsValue], risk: str) -> OddsValue | None:
    risk_values = [value for value in values if value.risk == risk]
    return max(risk_values, key=lambda row: (row.expected_roi, row.edge), default=None)


def _card(value: OddsValue | None, title: str) -> PredictionCard | None:
    if value is None:
        return None
    return PredictionCard(
        risk=value.risk,
        title=title,
        market=value.market,
        selection=value.selection,
        odds=value.decimal_odds,
        model_probability=value.model_probability,
        expected_roi=value.expected_roi,
        allocation_pct=value.allocation_pct,
        rationale=(
            f"Model probability {value.model_probability:.1%} vs no-vig market "
            f"{value.no_vig_probability:.1%}; edge {value.edge:.1%}."
        ),
    )
