"""Refresh schedule definitions for automated data updates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateJob:
    name: str
    cadence: str
    sources: tuple[str, ...]
    target_tables: tuple[str, ...]
    betting_markets_supported: tuple[str, ...]
    purpose: str


def default_update_jobs() -> list[UpdateJob]:
    return [
        UpdateJob(
            name="historical_world_cup_backfill",
            cadence="daily",
            sources=("StatsBomb Open Data", "football-data.co.uk", "Kaggle FIFA World Cup datasets"),
            target_tables=("teams", "matches", "team_match_stats", "player_match_stats", "odds_snapshots"),
            betting_markets_supported=("moneyline", "handicap", "totals", "BTTS"),
            purpose="Maintain historical baselines for team strength, xG, event rates, and odds calibration.",
        ),
        UpdateJob(
            name="fixture_and_venue_refresh",
            cadence="every 6h",
            sources=("football-data.org", "OpenStreetMap / Nominatim"),
            target_tables=("matches", "venues", "referees"),
            betting_markets_supported=("moneyline", "handicap", "totals"),
            purpose="Keep FIFA 2026 schedule, venue, and location context current.",
        ),
        UpdateJob(
            name="prematch_team_news_refresh",
            cadence="24h, 6h, 1h, and 15m before kickoff",
            sources=("Public federation/team reports",),
            target_tables=("availability", "lineups"),
            betting_markets_supported=("moneyline", "handicap", "totals", "BTTS"),
            purpose="Capture injuries, suspensions, and starting lineup confirmations before markets settle.",
        ),
        UpdateJob(
            name="weather_refresh",
            cadence="24h, 6h, 1h, and 15m before kickoff",
            sources=("Open-Meteo",),
            target_tables=("weather_snapshots",),
            betting_markets_supported=("totals", "corners", "cards"),
            purpose="Track venue weather factors that affect tempo, finishing, cards, and corners.",
        ),
        UpdateJob(
            name="odds_refresh",
            cadence="every 15m pre-match; 60-120s live within provider limits",
            sources=("The Odds API",),
            target_tables=("odds_snapshots",),
            betting_markets_supported=("moneyline", "handicap", "totals", "BTTS", "cards", "corners"),
            purpose="Store opening/current odds movement and sportsbook-implied probabilities.",
        ),
    ]
