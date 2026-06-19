"""SQLite data warehouse for World Cup betting analytics inputs."""

from __future__ import annotations

import json
import hashlib
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import DataSourceDescriptor, MatchFeatureSnapshot, OddsMovement, OddsSnapshot


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sources (
  name TEXT PRIMARY KEY,
  category TEXT NOT NULL,
  url TEXT NOT NULL,
  free_access TEXT NOT NULL,
  reliability TEXT NOT NULL,
  update_cadence TEXT NOT NULL,
  betting_fields_json TEXT NOT NULL,
  notes TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_payloads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_name TEXT NOT NULL REFERENCES sources(name),
  endpoint TEXT NOT NULL,
  captured_at_utc TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  checksum TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teams (
  team_id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  fifa_code TEXT,
  confederation TEXT,
  historical_world_cup_titles INTEGER DEFAULT 0,
  historical_world_cup_matches INTEGER DEFAULT 0,
  historical_world_cup_goals_for INTEGER DEFAULT 0,
  historical_world_cup_goals_against INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS venues (
  venue_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  city TEXT NOT NULL,
  country TEXT NOT NULL,
  latitude REAL,
  longitude REAL,
  altitude_m REAL,
  capacity INTEGER,
  surface TEXT
);

CREATE TABLE IF NOT EXISTS matches (
  match_id TEXT PRIMARY KEY,
  competition TEXT NOT NULL,
  season TEXT NOT NULL,
  kickoff_utc TEXT NOT NULL,
  home_team_id TEXT NOT NULL REFERENCES teams(team_id),
  away_team_id TEXT NOT NULL REFERENCES teams(team_id),
  venue_id TEXT REFERENCES venues(venue_id),
  referee_id TEXT,
  status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS match_results (
  match_id TEXT PRIMARY KEY REFERENCES matches(match_id),
  home_goals INTEGER,
  away_goals INTEGER,
  halftime_home_goals INTEGER,
  halftime_away_goals INTEGER,
  updated_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS team_match_stats (
  match_id TEXT NOT NULL REFERENCES matches(match_id),
  team_id TEXT NOT NULL REFERENCES teams(team_id),
  goals_scored INTEGER,
  goals_conceded INTEGER,
  expected_goals REAL,
  shots INTEGER,
  shots_on_target INTEGER,
  possession_pct REAL,
  corners INTEGER,
  yellow_cards INTEGER,
  red_cards INTEGER,
  PRIMARY KEY (match_id, team_id)
);

CREATE TABLE IF NOT EXISTS player_match_stats (
  match_id TEXT NOT NULL REFERENCES matches(match_id),
  player_id TEXT NOT NULL,
  player_name TEXT NOT NULL,
  team_id TEXT NOT NULL REFERENCES teams(team_id),
  minutes INTEGER,
  shots INTEGER,
  shots_on_target INTEGER,
  expected_goals REAL,
  assists INTEGER,
  yellow_cards INTEGER,
  red_cards INTEGER,
  PRIMARY KEY (match_id, player_id)
);

CREATE TABLE IF NOT EXISTS availability (
  match_id TEXT NOT NULL REFERENCES matches(match_id),
  team_id TEXT NOT NULL REFERENCES teams(team_id),
  player_id TEXT NOT NULL,
  player_name TEXT NOT NULL,
  status TEXT NOT NULL,
  reason TEXT NOT NULL,
  source_name TEXT NOT NULL REFERENCES sources(name),
  updated_at_utc TEXT NOT NULL,
  PRIMARY KEY (match_id, player_id, status)
);

CREATE TABLE IF NOT EXISTS lineups (
  match_id TEXT NOT NULL REFERENCES matches(match_id),
  team_id TEXT NOT NULL REFERENCES teams(team_id),
  player_id TEXT NOT NULL,
  player_name TEXT NOT NULL,
  role TEXT NOT NULL,
  formation TEXT,
  confirmed INTEGER NOT NULL,
  updated_at_utc TEXT NOT NULL,
  PRIMARY KEY (match_id, player_id, role)
);

CREATE TABLE IF NOT EXISTS referees (
  referee_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  country TEXT
);

CREATE TABLE IF NOT EXISTS referee_stats (
  referee_id TEXT PRIMARY KEY REFERENCES referees(referee_id),
  matches INTEGER NOT NULL,
  yellow_cards_avg REAL NOT NULL,
  red_cards_avg REAL NOT NULL,
  penalties_avg REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_snapshots (
  match_id TEXT NOT NULL REFERENCES matches(match_id),
  captured_at_utc TEXT NOT NULL,
  forecast_for_utc TEXT NOT NULL,
  temperature_c REAL,
  wind_speed_kmh REAL,
  precipitation_mm REAL,
  humidity_pct REAL,
  source_name TEXT NOT NULL REFERENCES sources(name),
  PRIMARY KEY (match_id, captured_at_utc)
);

CREATE TABLE IF NOT EXISTS odds_snapshots (
  match_id TEXT NOT NULL REFERENCES matches(match_id),
  sportsbook TEXT NOT NULL,
  market TEXT NOT NULL,
  selection TEXT NOT NULL,
  decimal_odds REAL NOT NULL,
  captured_at_utc TEXT NOT NULL,
  is_opening INTEGER NOT NULL,
  PRIMARY KEY (match_id, sportsbook, market, selection, captured_at_utc)
);

CREATE TABLE IF NOT EXISTS feature_snapshots (
  match_id TEXT NOT NULL REFERENCES matches(match_id),
  generated_at_utc TEXT NOT NULL,
  feature_json TEXT NOT NULL,
  PRIMARY KEY (match_id, generated_at_utc)
);
"""


class BettingDataWarehouse:
    """Thin repository around the normalized SQLite warehouse."""

    def __init__(self, path: str | Path = ":memory:"):
        self.path = path
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row

    def close(self) -> None:
        self.connection.close()

    def initialize(self) -> None:
        self.connection.executescript(SCHEMA)
        self.connection.commit()

    def upsert_sources(self, sources: list[DataSourceDescriptor]) -> None:
        self.connection.executemany(
            """
            INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
              category=excluded.category,
              url=excluded.url,
              free_access=excluded.free_access,
              reliability=excluded.reliability,
              update_cadence=excluded.update_cadence,
              betting_fields_json=excluded.betting_fields_json,
              notes=excluded.notes
            """,
            [
                (
                    source.name,
                    source.category,
                    source.url,
                    source.free_access,
                    source.reliability,
                    source.update_cadence,
                    json.dumps(source.betting_fields),
                    source.notes,
                )
                for source in sources
            ],
        )
        self.connection.commit()

    def store_raw_payload(
        self, source_name: str, endpoint: str, captured_at_utc: str, payload: dict[str, Any]
    ) -> int:
        payload_json = json.dumps(payload, sort_keys=True)
        checksum = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        cursor = self.connection.execute(
            """
            INSERT INTO raw_payloads (source_name, endpoint, captured_at_utc, payload_json, checksum)
            VALUES (?, ?, ?, ?, ?)
            """,
            (source_name, endpoint, captured_at_utc, payload_json, checksum),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def upsert_rows(self, table: str, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        columns = list(rows[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        update_columns = ", ".join(f"{column}=excluded.{column}" for column in columns)
        sql = (
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) "
            f"ON CONFLICT DO UPDATE SET {update_columns}"
        )
        self.connection.executemany(sql, [[row[column] for column in columns] for row in rows])
        self.connection.commit()

    def insert_odds_snapshots(self, snapshots: list[OddsSnapshot]) -> None:
        self.upsert_rows("odds_snapshots", [asdict(snapshot) for snapshot in snapshots])

    def insert_feature_snapshot(self, snapshot: MatchFeatureSnapshot) -> None:
        self.connection.execute(
            """
            INSERT OR REPLACE INTO feature_snapshots (match_id, generated_at_utc, feature_json)
            VALUES (?, ?, ?)
            """,
            (snapshot.match_id, snapshot.generated_at_utc, json.dumps(snapshot.features, sort_keys=True)),
        )
        self.connection.commit()

    def odds_movements(self, match_id: str) -> list[OddsMovement]:
        rows = self.connection.execute(
            """
            WITH ranked AS (
              SELECT *,
                FIRST_VALUE(decimal_odds) OVER (
                  PARTITION BY match_id, sportsbook, market, selection
                  ORDER BY is_opening DESC, captured_at_utc ASC
                ) AS opening_odds,
                FIRST_VALUE(decimal_odds) OVER (
                  PARTITION BY match_id, sportsbook, market, selection
                  ORDER BY captured_at_utc DESC
                ) AS current_odds
              FROM odds_snapshots
              WHERE match_id = ?
            )
            SELECT DISTINCT match_id, sportsbook, market, selection, opening_odds, current_odds
            FROM ranked
            ORDER BY sportsbook, market, selection
            """,
            (match_id,),
        ).fetchall()
        return [
            OddsMovement(
                match_id=row["match_id"],
                sportsbook=row["sportsbook"],
                market=row["market"],
                selection=row["selection"],
                opening_odds=row["opening_odds"],
                current_odds=row["current_odds"],
                implied_probability_open=round(1 / row["opening_odds"], 4),
                implied_probability_current=round(1 / row["current_odds"], 4),
                odds_delta=round(row["current_odds"] - row["opening_odds"], 4),
                implied_probability_delta=round((1 / row["current_odds"]) - (1 / row["opening_odds"]), 4),
            )
            for row in rows
        ]

    def table_counts(self) -> dict[str, int]:
        tables = [
            "sources",
            "raw_payloads",
            "teams",
            "venues",
            "matches",
            "team_match_stats",
            "player_match_stats",
            "availability",
            "lineups",
            "referee_stats",
            "weather_snapshots",
            "odds_snapshots",
            "feature_snapshots",
        ]
        return {
            table: self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in tables
        }
