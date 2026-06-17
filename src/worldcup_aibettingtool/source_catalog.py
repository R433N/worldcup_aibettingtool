"""Catalog of reliable free or free-tier football data sources."""

from __future__ import annotations

from .models import DataSourceDescriptor


def recommended_sources() -> list[DataSourceDescriptor]:
    """Return sources ordered by usefulness for a World Cup betting warehouse."""
    return [
        DataSourceDescriptor(
            name="football-data.org",
            category="fixtures_results_tables",
            url="https://www.football-data.org/",
            free_access="Free tier with API token",
            reliability="High",
            update_cadence="Scheduled fixtures/results refresh every 6h; matchday refresh every 10m",
            betting_fields=("fixtures", "results", "standings", "goals_for", "goals_against"),
            notes="Good stable API for fixtures/results. Coverage depends on competition plan availability.",
        ),
        DataSourceDescriptor(
            name="StatsBomb Open Data",
            category="event_history_xg",
            url="https://github.com/statsbomb/open-data",
            free_access="Open GitHub data",
            reliability="High",
            update_cadence="Historical backfill; refresh weekly for new open releases",
            betting_fields=("events", "shots", "shot_location", "xg", "lineups", "player_events"),
            notes="Best free event-level source for historical World Cup modeling; not a live feed.",
        ),
        DataSourceDescriptor(
            name="Open-Meteo",
            category="weather",
            url="https://open-meteo.com/",
            free_access="Free API, no key required for typical usage",
            reliability="High",
            update_cadence="Refresh 24h, 6h, 1h, and 15m before kickoff",
            betting_fields=("temperature", "wind_speed", "precipitation", "humidity"),
            notes="Use venue coordinates; store forecast issue time with each snapshot.",
        ),
        DataSourceDescriptor(
            name="The Odds API",
            category="sportsbook_odds",
            url="https://the-odds-api.com/",
            free_access="Free tier with API key and request limits",
            reliability="Medium",
            update_cadence="Refresh pre-match every 15m; live every 60-120s when limits allow",
            betting_fields=("moneyline", "spreads", "totals", "bookmakers", "opening_current_odds"),
            notes="Free tier may not include every sportsbook or Bet365 in every region; do not scrape sportsbooks.",
        ),
        DataSourceDescriptor(
            name="football-data.co.uk",
            category="historical_odds_results",
            url="https://www.football-data.co.uk/",
            free_access="Free CSV downloads",
            reliability="High",
            update_cadence="Historical backfill; daily CSV sync",
            betting_fields=("closing_odds", "results", "totals", "asian_handicap"),
            notes="Strong source for historical odds calibration; World Cup coverage can vary by file.",
        ),
        DataSourceDescriptor(
            name="Kaggle FIFA World Cup datasets",
            category="historical_world_cup",
            url="https://www.kaggle.com/datasets",
            free_access="Free account/API token",
            reliability="Medium",
            update_cadence="Manual or daily backfill; verify dataset provenance",
            betting_fields=("historical_performance", "squads", "venues", "tournament_results"),
            notes="Useful enrichment source; validate licenses and schema drift before automated ingestion.",
        ),
        DataSourceDescriptor(
            name="OpenStreetMap / Nominatim",
            category="stadium_location",
            url="https://nominatim.org/",
            free_access="Free with usage policy",
            reliability="Medium",
            update_cadence="Venue backfill and monthly refresh",
            betting_fields=("stadium_coordinates", "altitude_proxy", "location", "timezone"),
            notes="Cache venue coordinates and respect rate limits; avoid high-volume live calls.",
        ),
        DataSourceDescriptor(
            name="Public federation/team reports",
            category="injuries_suspensions_lineups",
            url="https://www.fifa.com/",
            free_access="Public web pages/RSS where available",
            reliability="Medium",
            update_cadence="Refresh every 30m on matchday; manually verify critical changes",
            betting_fields=("injuries", "suspensions", "starting_lineups", "bench"),
            notes="Automated collection should prefer official feeds/APIs; scraping must follow terms.",
        ),
    ]


def readiness_matrix() -> list[dict[str, str]]:
    return [
        {
            "area": source.category,
            "primary_source": source.name,
            "free_access": source.free_access,
            "reliability": source.reliability,
            "cadence": source.update_cadence,
            "fields": ", ".join(source.betting_fields),
        }
        for source in recommended_sources()
    ]
