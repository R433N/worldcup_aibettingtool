"""Data foundation assembly for a World Cup betting-model input warehouse."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import MatchFeatureSnapshot, OddsSnapshot
from .odds import calculate_movements
from .source_catalog import readiness_matrix, recommended_sources
from .warehouse import BettingDataWarehouse

MATCH_ID = "fifa-2026-arg-fra-001"
GENERATED_AT = "2026-07-19T18:00:00Z"


def seed_demo_warehouse(path: str | Path = ":memory:") -> BettingDataWarehouse:
    """Create a representative warehouse for tests and local demos."""
    warehouse = BettingDataWarehouse(path)
    warehouse.initialize()
    warehouse.upsert_sources(recommended_sources())
    warehouse.store_raw_payload(
        "football-data.org",
        "/v4/competitions/WC/matches",
        GENERATED_AT,
        {"match_id": MATCH_ID, "home": "Argentina", "away": "France", "status": "scheduled"},
    )
    _seed_reference_data(warehouse)
    _seed_match_data(warehouse)
    feature = build_feature_snapshot(warehouse, MATCH_ID)
    warehouse.insert_feature_snapshot(feature)
    return warehouse


def build_data_foundation_report(path: str | Path = ":memory:") -> dict[str, Any]:
    warehouse = seed_demo_warehouse(path)
    try:
        odds_movements = warehouse.odds_movements(MATCH_ID)
        feature = build_feature_snapshot(warehouse, MATCH_ID)
        return {
            "generated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "source_readiness": readiness_matrix(),
            "warehouse_counts": warehouse.table_counts(),
            "odds_movements": [asdict(row) for row in odds_movements],
            "feature_snapshot": asdict(feature),
            "update_plan": update_plan(),
            "no_prediction_policy": (
                "This layer collects, cleans, stores, and prepares data only. "
                "It does not recommend bets or generate model predictions."
            ),
        }
    finally:
        warehouse.close()


def write_data_foundation_artifacts(output_dir: str | Path = "site") -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    report = build_data_foundation_report()
    (output / "data_foundation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return output


def build_feature_snapshot(warehouse: BettingDataWarehouse, match_id: str) -> MatchFeatureSnapshot:
    connection = warehouse.connection
    match = connection.execute(
        """
        SELECT m.*, ht.name AS home_team, at.name AS away_team, v.altitude_m, v.capacity
        FROM matches m
        JOIN teams ht ON ht.team_id = m.home_team_id
        JOIN teams at ON at.team_id = m.away_team_id
        LEFT JOIN venues v ON v.venue_id = m.venue_id
        WHERE m.match_id = ?
        """,
        (match_id,),
    ).fetchone()
    home_stats = _team_recent_features(connection, match["home_team_id"])
    away_stats = _team_recent_features(connection, match["away_team_id"])
    referee = connection.execute(
        "SELECT rs.* FROM referee_stats rs WHERE rs.referee_id = ?",
        (match["referee_id"],),
    ).fetchone()
    weather = connection.execute(
        """
        SELECT * FROM weather_snapshots
        WHERE match_id = ?
        ORDER BY captured_at_utc DESC
        LIMIT 1
        """,
        (match_id,),
    ).fetchone()
    home_availability = _availability_count(connection, match_id, match["home_team_id"])
    away_availability = _availability_count(connection, match_id, match["away_team_id"])
    odds = warehouse.odds_movements(match_id)

    features: dict[str, float | int | str | None] = {
        "home_team": match["home_team"],
        "away_team": match["away_team"],
        "home_form_points_last_5": home_stats["form_points"],
        "away_form_points_last_5": away_stats["form_points"],
        "home_goals_for_avg": home_stats["goals_for_avg"],
        "away_goals_for_avg": away_stats["goals_for_avg"],
        "home_goals_against_avg": home_stats["goals_against_avg"],
        "away_goals_against_avg": away_stats["goals_against_avg"],
        "home_xg_avg": home_stats["xg_avg"],
        "away_xg_avg": away_stats["xg_avg"],
        "home_shots_avg": home_stats["shots_avg"],
        "away_shots_avg": away_stats["shots_avg"],
        "home_shots_on_target_avg": home_stats["shots_on_target_avg"],
        "away_shots_on_target_avg": away_stats["shots_on_target_avg"],
        "home_possession_avg": home_stats["possession_avg"],
        "away_possession_avg": away_stats["possession_avg"],
        "home_unavailable_players": home_availability,
        "away_unavailable_players": away_availability,
        "home_confirmed_starters": _lineup_count(connection, match_id, match["home_team_id"]),
        "away_confirmed_starters": _lineup_count(connection, match_id, match["away_team_id"]),
        "referee_yellow_cards_avg": referee["yellow_cards_avg"] if referee else None,
        "referee_red_cards_avg": referee["red_cards_avg"] if referee else None,
        "referee_penalties_avg": referee["penalties_avg"] if referee else None,
        "temperature_c": weather["temperature_c"] if weather else None,
        "wind_speed_kmh": weather["wind_speed_kmh"] if weather else None,
        "precipitation_mm": weather["precipitation_mm"] if weather else None,
        "venue_altitude_m": match["altitude_m"],
        "venue_capacity": match["capacity"],
    }
    for movement in odds:
        key = f"odds_move_{movement.sportsbook}_{movement.market}_{movement.selection}".lower()
        key = key.replace(" ", "_").replace("/", "_")
        features[f"{key}_current"] = movement.current_odds
        features[f"{key}_implied_delta"] = movement.implied_probability_delta

    return MatchFeatureSnapshot(
        match_id=match_id,
        home_team=match["home_team"],
        away_team=match["away_team"],
        kickoff_utc=match["kickoff_utc"],
        generated_at_utc=GENERATED_AT,
        features=features,
    )


def update_plan() -> list[dict[str, str]]:
    return [
        {"job": "historical_backfill", "cadence": "daily", "purpose": "World Cup results, event data, xG, historical odds"},
        {"job": "fixture_refresh", "cadence": "every 6h", "purpose": "FIFA 2026 schedule, venues, referees"},
        {"job": "prematch_refresh", "cadence": "24h/6h/1h/15m before kickoff", "purpose": "lineups, injuries, weather, odds"},
        {"job": "live_match_refresh", "cadence": "60-120s during match when provider limits allow", "purpose": "odds, incidents, shots, cards, corners"},
        {"job": "postmatch_close", "cadence": "after final whistle", "purpose": "freeze results and reconcile raw vs normalized data"},
    ]


def _seed_reference_data(warehouse: BettingDataWarehouse) -> None:
    warehouse.upsert_rows(
        "teams",
        [
            {
                "team_id": "ARG",
                "name": "Argentina",
                "fifa_code": "ARG",
                "confederation": "CONMEBOL",
                "historical_world_cup_titles": 3,
                "historical_world_cup_matches": 88,
                "historical_world_cup_goals_for": 152,
                "historical_world_cup_goals_against": 101,
            },
            {
                "team_id": "FRA",
                "name": "France",
                "fifa_code": "FRA",
                "confederation": "UEFA",
                "historical_world_cup_titles": 2,
                "historical_world_cup_matches": 73,
                "historical_world_cup_goals_for": 136,
                "historical_world_cup_goals_against": 85,
            },
        ],
    )
    warehouse.upsert_rows(
        "venues",
        [
            {
                "venue_id": "metlife",
                "name": "MetLife Stadium",
                "city": "East Rutherford",
                "country": "United States",
                "latitude": 40.8135,
                "longitude": -74.0745,
                "altitude_m": 2,
                "capacity": 82500,
                "surface": "grass",
            }
        ],
    )
    warehouse.upsert_rows("referees", [{"referee_id": "ref-001", "name": "Demo Referee", "country": "Neutral"}])
    warehouse.upsert_rows(
        "referee_stats",
        [{"referee_id": "ref-001", "matches": 18, "yellow_cards_avg": 4.6, "red_cards_avg": 0.18, "penalties_avg": 0.28}],
    )


def _seed_match_data(warehouse: BettingDataWarehouse) -> None:
    warehouse.upsert_rows(
        "matches",
        [
            {
                "match_id": MATCH_ID,
                "competition": "FIFA World Cup 2026",
                "season": "2026",
                "kickoff_utc": "2026-07-19T20:00:00Z",
                "home_team_id": "ARG",
                "away_team_id": "FRA",
                "venue_id": "metlife",
                "referee_id": "ref-001",
                "status": "scheduled",
            },
            {"match_id": "hist-arg-1", "competition": "International Friendly", "season": "2025", "kickoff_utc": "2025-11-10T20:00:00Z", "home_team_id": "ARG", "away_team_id": "FRA", "venue_id": "metlife", "referee_id": "ref-001", "status": "final"},
            {"match_id": "hist-arg-2", "competition": "International Friendly", "season": "2025", "kickoff_utc": "2025-10-10T20:00:00Z", "home_team_id": "ARG", "away_team_id": "FRA", "venue_id": "metlife", "referee_id": "ref-001", "status": "final"},
            {"match_id": "hist-arg-3", "competition": "International Friendly", "season": "2025", "kickoff_utc": "2025-09-10T20:00:00Z", "home_team_id": "ARG", "away_team_id": "FRA", "venue_id": "metlife", "referee_id": "ref-001", "status": "final"},
            {"match_id": "hist-fra-1", "competition": "International Friendly", "season": "2025", "kickoff_utc": "2025-11-11T20:00:00Z", "home_team_id": "FRA", "away_team_id": "ARG", "venue_id": "metlife", "referee_id": "ref-001", "status": "final"},
            {"match_id": "hist-fra-2", "competition": "International Friendly", "season": "2025", "kickoff_utc": "2025-10-11T20:00:00Z", "home_team_id": "FRA", "away_team_id": "ARG", "venue_id": "metlife", "referee_id": "ref-001", "status": "final"},
            {"match_id": "hist-fra-3", "competition": "International Friendly", "season": "2025", "kickoff_utc": "2025-09-11T20:00:00Z", "home_team_id": "FRA", "away_team_id": "ARG", "venue_id": "metlife", "referee_id": "ref-001", "status": "final"},
        ],
    )
    warehouse.upsert_rows(
        "match_results",
        [{"match_id": MATCH_ID, "home_goals": None, "away_goals": None, "halftime_home_goals": None, "halftime_away_goals": None, "updated_at_utc": GENERATED_AT}],
    )
    warehouse.upsert_rows(
        "team_match_stats",
        [
            {"match_id": "hist-arg-1", "team_id": "ARG", "goals_scored": 2, "goals_conceded": 0, "expected_goals": 1.8, "shots": 14, "shots_on_target": 6, "possession_pct": 58, "corners": 6, "yellow_cards": 2, "red_cards": 0},
            {"match_id": "hist-arg-2", "team_id": "ARG", "goals_scored": 1, "goals_conceded": 1, "expected_goals": 1.2, "shots": 11, "shots_on_target": 4, "possession_pct": 54, "corners": 5, "yellow_cards": 4, "red_cards": 0},
            {"match_id": "hist-arg-3", "team_id": "ARG", "goals_scored": 3, "goals_conceded": 1, "expected_goals": 2.4, "shots": 17, "shots_on_target": 8, "possession_pct": 61, "corners": 8, "yellow_cards": 1, "red_cards": 0},
            {"match_id": "hist-fra-1", "team_id": "FRA", "goals_scored": 2, "goals_conceded": 1, "expected_goals": 1.7, "shots": 13, "shots_on_target": 5, "possession_pct": 53, "corners": 7, "yellow_cards": 1, "red_cards": 0},
            {"match_id": "hist-fra-2", "team_id": "FRA", "goals_scored": 0, "goals_conceded": 0, "expected_goals": 0.9, "shots": 9, "shots_on_target": 3, "possession_pct": 49, "corners": 4, "yellow_cards": 2, "red_cards": 0},
            {"match_id": "hist-fra-3", "team_id": "FRA", "goals_scored": 3, "goals_conceded": 0, "expected_goals": 2.1, "shots": 16, "shots_on_target": 7, "possession_pct": 57, "corners": 9, "yellow_cards": 2, "red_cards": 0},
        ],
    )
    warehouse.upsert_rows(
        "player_match_stats",
        [
            {"match_id": MATCH_ID, "player_id": "p-messi", "player_name": "Lionel Messi", "team_id": "ARG", "minutes": None, "shots": None, "shots_on_target": None, "expected_goals": None, "assists": None, "yellow_cards": None, "red_cards": None},
            {"match_id": MATCH_ID, "player_id": "p-mbappe", "player_name": "Kylian Mbappe", "team_id": "FRA", "minutes": None, "shots": None, "shots_on_target": None, "expected_goals": None, "assists": None, "yellow_cards": None, "red_cards": None},
        ],
    )
    warehouse.upsert_rows(
        "availability",
        [
            {"match_id": MATCH_ID, "team_id": "ARG", "player_id": "arg-def-1", "player_name": "Argentina Defender", "status": "questionable", "reason": "minor knock", "source_name": "Public federation/team reports", "updated_at_utc": GENERATED_AT},
            {"match_id": MATCH_ID, "team_id": "FRA", "player_id": "fra-mid-1", "player_name": "France Midfielder", "status": "suspended", "reason": "yellow card accumulation", "source_name": "Public federation/team reports", "updated_at_utc": GENERATED_AT},
        ],
    )
    warehouse.upsert_rows(
        "lineups",
        [
            *[
                {"match_id": MATCH_ID, "team_id": "ARG", "player_id": f"arg-{i}", "player_name": f"Argentina Starter {i}", "role": "starter", "formation": "4-3-3", "confirmed": 0, "updated_at_utc": GENERATED_AT}
                for i in range(1, 12)
            ],
            *[
                {"match_id": MATCH_ID, "team_id": "FRA", "player_id": f"fra-{i}", "player_name": f"France Starter {i}", "role": "starter", "formation": "4-2-3-1", "confirmed": 0, "updated_at_utc": GENERATED_AT}
                for i in range(1, 12)
            ],
        ],
    )
    warehouse.upsert_rows(
        "weather_snapshots",
        [
            {
                "match_id": MATCH_ID,
                "captured_at_utc": GENERATED_AT,
                "forecast_for_utc": "2026-07-19T20:00:00Z",
                "temperature_c": 25.4,
                "wind_speed_kmh": 12.2,
                "precipitation_mm": 0.4,
                "humidity_pct": 61,
                "source_name": "Open-Meteo",
            }
        ],
    )
    warehouse.insert_odds_snapshots(
        [
            OddsSnapshot(MATCH_ID, "The Odds API Demo", "Moneyline", "Home", 2.45, "2026-07-18T12:00:00Z", True),
            OddsSnapshot(MATCH_ID, "The Odds API Demo", "Moneyline", "Draw", 3.25, "2026-07-18T12:00:00Z", True),
            OddsSnapshot(MATCH_ID, "The Odds API Demo", "Moneyline", "Away", 2.92, "2026-07-18T12:00:00Z", True),
            OddsSnapshot(MATCH_ID, "The Odds API Demo", "Moneyline", "Home", 2.35, GENERATED_AT, False),
            OddsSnapshot(MATCH_ID, "The Odds API Demo", "Moneyline", "Draw", 3.30, GENERATED_AT, False),
            OddsSnapshot(MATCH_ID, "The Odds API Demo", "Moneyline", "Away", 3.05, GENERATED_AT, False),
            OddsSnapshot(MATCH_ID, "The Odds API Demo", "Totals", "Over 2.5", 1.98, "2026-07-18T12:00:00Z", True),
            OddsSnapshot(MATCH_ID, "The Odds API Demo", "Totals", "Over 2.5", 1.91, GENERATED_AT, False),
        ]
    )


def _team_recent_features(connection, team_id: str) -> dict[str, float]:
    rows = connection.execute(
        """
        SELECT * FROM team_match_stats
        WHERE team_id = ?
        ORDER BY match_id DESC
        LIMIT 5
        """,
        (team_id,),
    ).fetchall()
    count = len(rows) or 1
    points = sum(3 if row["goals_scored"] > row["goals_conceded"] else 1 if row["goals_scored"] == row["goals_conceded"] else 0 for row in rows)
    return {
        "form_points": points,
        "goals_for_avg": round(sum(row["goals_scored"] for row in rows) / count, 2),
        "goals_against_avg": round(sum(row["goals_conceded"] for row in rows) / count, 2),
        "xg_avg": round(sum(row["expected_goals"] for row in rows) / count, 2),
        "shots_avg": round(sum(row["shots"] for row in rows) / count, 2),
        "shots_on_target_avg": round(sum(row["shots_on_target"] for row in rows) / count, 2),
        "possession_avg": round(sum(row["possession_pct"] for row in rows) / count, 2),
    }


def _availability_count(connection, match_id: str, team_id: str) -> int:
    return connection.execute(
        "SELECT COUNT(*) FROM availability WHERE match_id = ? AND team_id = ? AND status IN ('out', 'suspended', 'questionable')",
        (match_id, team_id),
    ).fetchone()[0]


def _lineup_count(connection, match_id: str, team_id: str) -> int:
    return connection.execute(
        "SELECT COUNT(*) FROM lineups WHERE match_id = ? AND team_id = ? AND role = 'starter'",
        (match_id, team_id),
    ).fetchone()[0]
