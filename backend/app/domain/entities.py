"""Core domain entities.

These are framework-agnostic dataclasses. They intentionally know nothing about
HTTP, persistence, or the statistical engine. Keeping them pure makes the domain
easy to reason about and test.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class Team:
    """A national team."""

    name: str
    code: str  # FIFA-style 3-letter code, e.g. "BRA"
    confederation: str | None = None


@dataclass(frozen=True, slots=True)
class MatchResult:
    """A completed historical match used to fit the model.

    ``competition_weight`` lets us down-weight friendlies relative to
    competitive fixtures (a real data-quality lever in international football).
    """

    home: str
    away: str
    home_goals: int
    away_goals: int
    played_on: date
    neutral: bool = False
    competition_weight: float = 1.0

    def outcome(self) -> str:
        if self.home_goals > self.away_goals:
            return "HOME"
        if self.home_goals < self.away_goals:
            return "AWAY"
        return "DRAW"


@dataclass(frozen=True, slots=True)
class MarketOdds:
    """Bookmaker decimal odds for a single market on a fixture.

    ``selections`` maps a selection key (e.g. "HOME", "OVER_2.5") to decimal odds.
    """

    market: str
    bookmaker: str
    selections: dict[str, float]


@dataclass(frozen=True, slots=True)
class Fixture:
    """An upcoming match to be analysed, with associated bookmaker odds."""

    fixture_id: str
    home: str
    away: str
    kickoff: datetime
    neutral: bool = True  # World Cup matches are at neutral venues (except host)
    odds: list[MarketOdds] = field(default_factory=list)
