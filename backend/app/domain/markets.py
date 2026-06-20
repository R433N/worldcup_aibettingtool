"""Betting market definitions.

A *market* is a set of mutually exclusive, collectively exhaustive selections
(e.g. 1X2 = HOME/DRAW/AWAY). Keeping selection keys centralised avoids the
classic bug of mismatched string keys between the model and the odds feed.
"""

from __future__ import annotations

from enum import StrEnum


class Market(StrEnum):
    MATCH_RESULT = "1X2"
    OVER_UNDER_2_5 = "OU_2.5"
    BTTS = "BTTS"


# Canonical selection keys per market.
SELECTIONS: dict[Market, tuple[str, ...]] = {
    Market.MATCH_RESULT: ("HOME", "DRAW", "AWAY"),
    Market.OVER_UNDER_2_5: ("OVER", "UNDER"),
    Market.BTTS: ("YES", "NO"),
}


def selections_for(market: Market) -> tuple[str, ...]:
    return SELECTIONS[market]
