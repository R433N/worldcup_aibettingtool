"""Data repositories.

The protocols define the seams that a real data feed would implement. The CSV
implementations back the bundled sample dataset. Swapping in a live provider
(football-data.org, API-Football, an internal warehouse, ...) is a matter of
writing new classes that satisfy these protocols — no change to the services or
statistical engine.
"""

from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Protocol

from app.domain.entities import Fixture, MarketOdds, MatchResult, Team


class MatchRepository(Protocol):
    def list_matches(self) -> list[MatchResult]: ...


class FixtureRepository(Protocol):
    def list_fixtures(self) -> list[Fixture]: ...
    def get_fixture(self, fixture_id: str) -> Fixture | None: ...


class TeamRepository(Protocol):
    def list_teams(self) -> list[Team]: ...


class CsvMatchRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def list_matches(self) -> list[MatchResult]:
        rows: list[MatchResult] = []
        with self._path.open(newline="") as f:
            for r in csv.DictReader(f):
                rows.append(
                    MatchResult(
                        home=r["home"],
                        away=r["away"],
                        home_goals=int(r["home_goals"]),
                        away_goals=int(r["away_goals"]),
                        played_on=date.fromisoformat(r["played_on"]),
                        neutral=bool(int(r["neutral"])),
                        competition_weight=float(r.get("competition_weight", 1.0)),
                    )
                )
        return rows


class CsvTeamRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def list_teams(self) -> list[Team]:
        if not self._path.exists():
            return []
        with self._path.open(newline="") as f:
            return [
                Team(name=r["name"], code=r["code"], confederation=r.get("confederation") or None)
                for r in csv.DictReader(f)
            ]


class CsvFixtureRepository:
    def __init__(self, fixtures_path: Path, odds_path: Path) -> None:
        self._fixtures_path = fixtures_path
        self._odds_path = odds_path

    def _load_odds(self) -> dict[str, list[MarketOdds]]:
        by_fixture_market: dict[tuple[str, str, str], dict[str, float]] = {}
        if self._odds_path.exists():
            with self._odds_path.open(newline="") as f:
                for r in csv.DictReader(f):
                    key = (r["fixture_id"], r["market"], r["bookmaker"])
                    by_fixture_market.setdefault(key, {})[r["selection"]] = float(
                        r["decimal_odds"]
                    )
        out: dict[str, list[MarketOdds]] = {}
        for (fixture_id, market, bookmaker), selections in by_fixture_market.items():
            out.setdefault(fixture_id, []).append(
                MarketOdds(market=market, bookmaker=bookmaker, selections=selections)
            )
        return out

    def list_fixtures(self) -> list[Fixture]:
        odds = self._load_odds()
        fixtures: list[Fixture] = []
        with self._fixtures_path.open(newline="") as f:
            for r in csv.DictReader(f):
                fid = r["fixture_id"]
                fixtures.append(
                    Fixture(
                        fixture_id=fid,
                        home=r["home"],
                        away=r["away"],
                        kickoff=datetime.fromisoformat(r["kickoff"]),
                        neutral=bool(int(r.get("neutral", 1))),
                        odds=odds.get(fid, []),
                    )
                )
        return fixtures

    def get_fixture(self, fixture_id: str) -> Fixture | None:
        return next((f for f in self.list_fixtures() if f.fixture_id == fixture_id), None)
