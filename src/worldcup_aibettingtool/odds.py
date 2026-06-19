"""Odds ingestion and market-implied movement calculations."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import OddsMovement, OddsSnapshot


class JsonOddsProvider:
    """Adapter for sportsbook odds exports from licensed/free-tier providers.

    Set ODDS_JSON to a JSON file path or pass one directly. The expected shape
    is a list of OddsSnapshot-compatible objects.
    """

    def __init__(self, json_path: str | Path | None = None):
        configured_path = json_path or os.getenv("ODDS_JSON")
        self.json_path = Path(configured_path) if configured_path else None

    def fetch(self) -> list[OddsSnapshot]:
        if not self.json_path:
            raise FileNotFoundError("Set ODDS_JSON or pass an odds export path.")
        raw = json.loads(self.json_path.read_text(encoding="utf-8"))
        return [
            OddsSnapshot(
                match_id=item["match_id"],
                sportsbook=item["sportsbook"],
                market=item["market"],
                selection=item["selection"],
                decimal_odds=float(item["decimal_odds"]),
                captured_at_utc=item["captured_at_utc"],
                is_opening=bool(item.get("is_opening", False)),
            )
            for item in raw
        ]


def implied_probability(decimal_odds: float) -> float:
    return round(1 / decimal_odds, 4)


def no_vig_probabilities(snapshots: list[OddsSnapshot]) -> dict[str, float]:
    implied_sum = sum(implied_probability(snapshot.decimal_odds) for snapshot in snapshots)
    if implied_sum == 0:
        return {}
    return {
        f"{snapshot.market}:{snapshot.selection}": round(implied_probability(snapshot.decimal_odds) / implied_sum, 4)
        for snapshot in snapshots
    }


def calculate_movements(snapshots: list[OddsSnapshot]) -> list[OddsMovement]:
    grouped: dict[tuple[str, str, str, str], list[OddsSnapshot]] = {}
    for snapshot in snapshots:
        key = (snapshot.match_id, snapshot.sportsbook, snapshot.market, snapshot.selection)
        grouped.setdefault(key, []).append(snapshot)

    movements = []
    for key, rows in grouped.items():
        rows.sort(key=lambda row: row.captured_at_utc)
        opening = next((row for row in rows if row.is_opening), rows[0])
        current = rows[-1]
        open_prob = implied_probability(opening.decimal_odds)
        current_prob = implied_probability(current.decimal_odds)
        movements.append(
            OddsMovement(
                match_id=key[0],
                sportsbook=key[1],
                market=key[2],
                selection=key[3],
                opening_odds=opening.decimal_odds,
                current_odds=current.decimal_odds,
                implied_probability_open=open_prob,
                implied_probability_current=current_prob,
                odds_delta=round(current.decimal_odds - opening.decimal_odds, 4),
                implied_probability_delta=round(current_prob - open_prob, 4),
            )
        )
    return sorted(movements, key=lambda row: (row.market, row.selection, row.sportsbook))
