"""Pipelines for live match stats, pressure, xG, and historical summaries."""

from __future__ import annotations

from collections import Counter, defaultdict
from math import exp, hypot

from .models import (
    EventType,
    Fixture,
    LiveEvent,
    MatchRecord,
    PlayerAverages,
    PlayerStatLine,
    TeamStats,
    average,
    pct,
)

PRESSURE_WEIGHTS = {
    EventType.GOAL: 4.0,
    EventType.SHOT_ON_TARGET: 2.0,
    EventType.SHOT: 1.0,
    EventType.CORNER: 0.8,
    EventType.DANGEROUS_ATTACK: 0.5,
    EventType.CARD: -0.4,
}


def expected_goal_value(event: LiveEvent) -> float:
    """Estimate xG from normalized pitch coordinates and event quality flags."""
    if event.event_type == EventType.GOAL:
        return 0.25 if event.x is None or event.y is None else max(_shot_xg(event), 0.25)
    if event.event_type not in {EventType.SHOT, EventType.SHOT_ON_TARGET}:
        return 0.0
    return _shot_xg(event)


def _shot_xg(event: LiveEvent) -> float:
    if event.x is None or event.y is None:
        base = 0.10
    else:
        distance = hypot(100 - event.x, 50 - event.y)
        angle_bonus = max(0.0, 1 - abs(event.y - 50) / 50)
        base = 0.04 + 0.38 * exp(-distance / 18) + 0.06 * angle_bonus
    if event.event_type == EventType.SHOT_ON_TARGET:
        base += 0.06
    if event.is_big_chance:
        base += 0.22
    return round(min(base, 0.85), 3)


def summarize_live_match(fixture: Fixture, events: list[LiveEvent]) -> dict:
    by_team = {
        fixture.home.name: _blank_live_team(),
        fixture.away.name: _blank_live_team(),
    }

    for event in events:
        if event.team not in by_team:
            continue
        team = by_team[event.team]
        if event.event_type == EventType.GOAL:
            team["goals"] += 1
            team["shots_attempted"] += 1
            team["shots_on_goal"] += 1
        elif event.event_type == EventType.SHOT_ON_TARGET:
            team["shots_attempted"] += 1
            team["shots_on_goal"] += 1
        elif event.event_type == EventType.SHOT:
            team["shots_attempted"] += 1
        elif event.event_type == EventType.CORNER:
            team["corners"] += 1
        elif event.event_type == EventType.CARD:
            team["cards"] += 1
        team["xg"] = round(team["xg"] + expected_goal_value(event), 3)

    return {
        "fixture": {
            "home": fixture.home.name,
            "away": fixture.away.name,
            "competition": fixture.competition,
            "kickoff_utc": fixture.kickoff_utc,
        },
        "teams": by_team,
        "pressure_timeline": build_pressure_timeline(fixture, events),
    }


def _blank_live_team() -> dict[str, float]:
    return {
        "goals": 0,
        "shots_attempted": 0,
        "shots_on_goal": 0,
        "corners": 0,
        "cards": 0,
        "xg": 0.0,
    }


def build_pressure_timeline(
    fixture: Fixture, events: list[LiveEvent], bucket_minutes: int = 5, lookback_minutes: int = 10
) -> list[dict[str, float]]:
    end_minute = max([90, *[event.minute for event in events]])
    buckets = range(bucket_minutes, end_minute + bucket_minutes, bucket_minutes)
    timeline = []

    for minute in buckets:
        home_pressure = _pressure_for_team(fixture.home.name, minute, events, lookback_minutes)
        away_pressure = _pressure_for_team(fixture.away.name, minute, events, lookback_minutes)
        total = max(home_pressure + away_pressure, 0.01)
        momentum = round(((home_pressure - away_pressure) / total) * 100, 1)
        timeline.append(
            {
                "minute": minute,
                "home_pressure": round(home_pressure, 2),
                "away_pressure": round(away_pressure, 2),
                "momentum": momentum,
            }
        )
    return timeline


def _pressure_for_team(team: str, minute: int, events: list[LiveEvent], lookback: int) -> float:
    pressure = 0.0
    for event in events:
        age = minute - event.minute
        if event.team != team or age < 0 or age > lookback:
            continue
        pressure += PRESSURE_WEIGHTS[event.event_type] * exp(-age / max(lookback, 1))
    return max(pressure, 0.0)


def team_summary(team: str, matches: list[MatchRecord], recent_n: int = 5) -> TeamStats:
    team_matches = [match for match in matches if team in {match.home_team, match.away_team}]
    recent = team_matches[-recent_n:]
    form = "".join(match.result_for(team) for match in recent) or "N/A"
    first_half_goals = sum(match.halftime_home_goals + match.halftime_away_goals for match in team_matches)
    second_half_goals = sum(match.second_half_goals for match in team_matches)

    return TeamStats(
        team=team,
        matches=len(team_matches),
        recent_form=form,
        goals_for_avg=round(average(match.goals_for(team) for match in team_matches), 2),
        goals_against_avg=round(average(match.goals_against(team) for match in team_matches), 2),
        over_25_goals_pct=pct(_rate(match.total_goals > 2.5 for match in team_matches)),
        under_25_goals_pct=pct(_rate(match.total_goals <= 2.5 for match in team_matches)),
        cards_avg=round(average(_cards_for(match, team) for match in team_matches), 2),
        over_35_cards_pct=pct(_rate(match.total_cards > 3.5 for match in team_matches)),
        corners_avg=round(average(_corners_for(match, team) for match in team_matches), 2),
        over_85_corners_pct=pct(_rate(match.total_corners > 8.5 for match in team_matches)),
        btts_pct=pct(_rate(match.home_goals > 0 and match.away_goals > 0 for match in team_matches)),
        clean_sheet_pct=pct(_rate(match.goals_against(team) == 0 for match in team_matches)),
        conceded_pct=pct(_rate(match.goals_against(team) > 0 for match in team_matches)),
        half_with_most_goals=_half_with_most_goals(first_half_goals, second_half_goals),
    )


def head_to_head(home: str, away: str, matches: list[MatchRecord]) -> dict[str, float | str | int]:
    pair = [
        match
        for match in matches
        if {match.home_team, match.away_team} == {home, away}
    ]
    result_counts = Counter(match.result_for(home) for match in pair)
    return {
        "matches": len(pair),
        "home_team_record": f"{result_counts['W']}W-{result_counts['D']}D-{result_counts['L']}L",
        "goals_avg": round(average(match.total_goals for match in pair), 2),
        "cards_avg": round(average(match.total_cards for match in pair), 2),
        "corners_avg": round(average(match.total_corners for match in pair), 2),
        "btts_pct": pct(_rate(match.home_goals > 0 and match.away_goals > 0 for match in pair)),
    }


def player_averages(players: list[PlayerStatLine]) -> list[PlayerAverages]:
    return [
        PlayerAverages(
            player=player.player,
            team=player.team,
            shots_on_goal_avg=round(player.average(player.shots_on_goal), 2),
            shots_attempted_avg=round(player.average(player.shots_attempted), 2),
            assists_avg=round(player.average(player.assists), 2),
            cards_avg=round(player.average(player.cards), 2),
        )
        for player in players
    ]


def player_live_totals(events: list[LiveEvent]) -> dict[str, dict[str, int]]:
    totals: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for event in events:
        if not event.player:
            continue
        if event.event_type in {EventType.GOAL, EventType.SHOT_ON_TARGET}:
            totals[event.player]["shots_attempted"] += 1
            totals[event.player]["shots_on_goal"] += 1
        elif event.event_type == EventType.SHOT:
            totals[event.player]["shots_attempted"] += 1
        elif event.event_type == EventType.CARD:
            totals[event.player]["cards"] += 1
    return {player: dict(stats) for player, stats in totals.items()}


def _rate(values) -> float:
    values = list(values)
    return sum(1 for value in values if value) / len(values) if values else 0.0


def _cards_for(match: MatchRecord, team: str) -> int:
    return match.home_cards if team == match.home_team else match.away_cards


def _corners_for(match: MatchRecord, team: str) -> int:
    return match.home_corners if team == match.home_team else match.away_corners


def _half_with_most_goals(first_half_goals: int, second_half_goals: int) -> str:
    if first_half_goals > second_half_goals:
        return "First half"
    if second_half_goals > first_half_goals:
        return "Second half"
    return "Even"
