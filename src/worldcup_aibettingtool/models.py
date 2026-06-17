"""Shared football analytics domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Iterable


class EventType(StrEnum):
    SHOT = "shot"
    SHOT_ON_TARGET = "shot_on_target"
    GOAL = "goal"
    CARD = "card"
    CORNER = "corner"
    DANGEROUS_ATTACK = "dangerous_attack"


@dataclass(frozen=True)
class TeamProfile:
    name: str
    attack_rating: float = 1.0
    defense_rating: float = 1.0


@dataclass(frozen=True)
class Fixture:
    home: TeamProfile
    away: TeamProfile
    competition: str
    kickoff_utc: str


@dataclass(frozen=True)
class LiveEvent:
    minute: int
    team: str
    event_type: EventType
    player: str | None = None
    x: float | None = None
    y: float | None = None
    is_big_chance: bool = False


@dataclass(frozen=True)
class PlayerStatLine:
    player: str
    team: str
    appearances: int
    shots_on_goal: int
    shots_attempted: int
    assists: int
    cards: int

    def average(self, value: int) -> float:
        return value / self.appearances if self.appearances else 0.0


@dataclass(frozen=True)
class MatchRecord:
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    halftime_home_goals: int
    halftime_away_goals: int
    home_cards: int
    away_cards: int
    home_corners: int
    away_corners: int
    events: tuple[LiveEvent, ...] = field(default_factory=tuple)

    @property
    def total_goals(self) -> int:
        return self.home_goals + self.away_goals

    @property
    def total_cards(self) -> int:
        return self.home_cards + self.away_cards

    @property
    def total_corners(self) -> int:
        return self.home_corners + self.away_corners

    @property
    def second_half_goals(self) -> int:
        return self.total_goals - self.halftime_home_goals - self.halftime_away_goals

    def goals_for(self, team: str) -> int:
        if team == self.home_team:
            return self.home_goals
        if team == self.away_team:
            return self.away_goals
        raise ValueError(f"{team!r} did not play in this match")

    def goals_against(self, team: str) -> int:
        if team == self.home_team:
            return self.away_goals
        if team == self.away_team:
            return self.home_goals
        raise ValueError(f"{team!r} did not play in this match")

    def result_for(self, team: str) -> str:
        goals_for = self.goals_for(team)
        goals_against = self.goals_against(team)
        if goals_for > goals_against:
            return "W"
        if goals_for < goals_against:
            return "L"
        return "D"


@dataclass(frozen=True)
class TeamStats:
    team: str
    matches: int
    recent_form: str
    goals_for_avg: float
    goals_against_avg: float
    over_25_goals_pct: float
    under_25_goals_pct: float
    cards_avg: float
    over_35_cards_pct: float
    corners_avg: float
    over_85_corners_pct: float
    btts_pct: float
    clean_sheet_pct: float
    conceded_pct: float
    half_with_most_goals: str


@dataclass(frozen=True)
class PlayerAverages:
    player: str
    team: str
    shots_on_goal_avg: float
    shots_attempted_avg: float
    assists_avg: float
    cards_avg: float


@dataclass(frozen=True)
class ProbabilitySnapshot:
    fulltime_home_win: float
    fulltime_draw: float
    fulltime_away_win: float
    halftime_home_win: float
    halftime_draw: float
    halftime_away_win: float
    double_chance_home_or_draw: float
    double_chance_away_or_draw: float
    double_chance_home_or_away: float
    expected_home_goals: float
    expected_away_goals: float
    top_scorelines: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class BetMarket:
    market: str
    selection: str
    decimal_odds: float
    sportsbook: str = "Bet365"


@dataclass(frozen=True)
class DataSourceDescriptor:
    name: str
    category: str
    url: str
    free_access: str
    reliability: str
    update_cadence: str
    betting_fields: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class OddsSnapshot:
    match_id: str
    sportsbook: str
    market: str
    selection: str
    decimal_odds: float
    captured_at_utc: str
    is_opening: bool = False


@dataclass(frozen=True)
class OddsMovement:
    match_id: str
    sportsbook: str
    market: str
    selection: str
    opening_odds: float
    current_odds: float
    implied_probability_open: float
    implied_probability_current: float
    odds_delta: float
    implied_probability_delta: float


@dataclass(frozen=True)
class DataReadinessItem:
    area: str
    status: str
    source: str
    update_cadence: str
    fields: tuple[str, ...]


@dataclass(frozen=True)
class MatchFeatureSnapshot:
    match_id: str
    home_team: str
    away_team: str
    kickoff_utc: str
    generated_at_utc: str
    features: dict[str, float | int | str | None]


@dataclass(frozen=True)
class OddsValue:
    market: str
    selection: str
    sportsbook: str
    decimal_odds: float
    sportsbook_probability: float
    no_vig_probability: float
    model_probability: float
    expected_roi: float
    edge: float
    allocation_pct: float
    risk: str


@dataclass(frozen=True)
class PredictionCard:
    risk: str
    title: str
    market: str
    selection: str
    odds: float
    model_probability: float
    expected_roi: float
    allocation_pct: float
    rationale: str


def pct(value: float) -> float:
    return round(value * 100, 1)


def average(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0
