"""Demo inputs that exercise every analytics pipeline without external keys."""

from __future__ import annotations

from .models import BetMarket, EventType, Fixture, LiveEvent, MatchRecord, PlayerStatLine, TeamProfile

HOME = TeamProfile("Argentina", attack_rating=1.12, defense_rating=0.91)
AWAY = TeamProfile("France", attack_rating=1.08, defense_rating=0.95)

FIXTURE = Fixture(
    home=HOME,
    away=AWAY,
    competition="World Cup Final",
    kickoff_utc="2026-07-19T20:00:00Z",
)

HISTORICAL_MATCHES = [
    MatchRecord("Argentina", "Chile", 2, 0, 1, 0, 2, 3, 6, 4),
    MatchRecord("Argentina", "Brazil", 1, 1, 0, 1, 4, 5, 5, 6),
    MatchRecord("Uruguay", "Argentina", 0, 1, 0, 0, 3, 2, 3, 7),
    MatchRecord("Argentina", "Colombia", 3, 1, 2, 0, 1, 4, 8, 3),
    MatchRecord("Ecuador", "Argentina", 1, 1, 1, 0, 2, 2, 4, 5),
    MatchRecord("France", "Netherlands", 2, 1, 1, 0, 1, 2, 7, 3),
    MatchRecord("Germany", "France", 1, 2, 0, 1, 3, 2, 5, 6),
    MatchRecord("France", "Portugal", 0, 0, 0, 0, 2, 3, 4, 5),
    MatchRecord("Spain", "France", 2, 2, 1, 1, 4, 4, 6, 6),
    MatchRecord("France", "Belgium", 3, 0, 1, 0, 2, 1, 9, 2),
    MatchRecord("Argentina", "France", 3, 3, 2, 0, 5, 3, 6, 5),
    MatchRecord("France", "Argentina", 4, 3, 1, 1, 3, 4, 7, 4),
    MatchRecord("Argentina", "France", 2, 1, 1, 0, 2, 2, 5, 5),
]

LIVE_EVENTS = [
    LiveEvent(4, "Argentina", EventType.DANGEROUS_ATTACK, "Lionel Messi"),
    LiveEvent(8, "Argentina", EventType.SHOT_ON_TARGET, "Julian Alvarez", x=88, y=47),
    LiveEvent(13, "France", EventType.CORNER, "Antoine Griezmann"),
    LiveEvent(17, "France", EventType.SHOT, "Kylian Mbappe", x=82, y=39),
    LiveEvent(22, "Argentina", EventType.GOAL, "Lionel Messi", x=91, y=51, is_big_chance=True),
    LiveEvent(31, "France", EventType.SHOT_ON_TARGET, "Kylian Mbappe", x=90, y=44, is_big_chance=True),
    LiveEvent(38, "Argentina", EventType.CORNER, "Angel Di Maria"),
    LiveEvent(44, "France", EventType.CARD, "Aurelien Tchouameni"),
    LiveEvent(52, "France", EventType.DANGEROUS_ATTACK, "Ousmane Dembele"),
    LiveEvent(57, "France", EventType.SHOT_ON_TARGET, "Kylian Mbappe", x=87, y=55),
    LiveEvent(62, "Argentina", EventType.SHOT, "Lautaro Martinez", x=80, y=62),
    LiveEvent(68, "Argentina", EventType.CARD, "Rodrigo De Paul"),
    LiveEvent(73, "France", EventType.CORNER, "Antoine Griezmann"),
    LiveEvent(79, "France", EventType.GOAL, "Kylian Mbappe", x=92, y=49, is_big_chance=True),
    LiveEvent(84, "Argentina", EventType.SHOT_ON_TARGET, "Lionel Messi", x=85, y=48),
]

PLAYER_LINES = [
    PlayerStatLine("Lionel Messi", "Argentina", 8, 14, 28, 5, 1),
    PlayerStatLine("Julian Alvarez", "Argentina", 8, 9, 22, 2, 0),
    PlayerStatLine("Angel Di Maria", "Argentina", 6, 6, 15, 4, 1),
    PlayerStatLine("Kylian Mbappe", "France", 8, 16, 31, 3, 0),
    PlayerStatLine("Antoine Griezmann", "France", 8, 7, 19, 6, 2),
    PlayerStatLine("Ousmane Dembele", "France", 7, 5, 14, 3, 1),
]

BET365_MARKETS = [
    BetMarket("Fulltime Result", "Home", 2.42),
    BetMarket("Fulltime Result", "Draw", 3.25),
    BetMarket("Fulltime Result", "Away", 2.95),
    BetMarket("Halftime Result", "Home", 3.05),
    BetMarket("Halftime Result", "Draw", 2.05),
    BetMarket("Halftime Result", "Away", 3.35),
    BetMarket("Double Chance", "Home or Draw", 1.42),
    BetMarket("Double Chance", "Away or Draw", 1.56),
    BetMarket("Double Chance", "Home or Away", 1.32),
    BetMarket("Total Goals", "Over 1.5", 1.35),
    BetMarket("Total Goals", "Over 2.5", 1.92),
    BetMarket("Total Goals", "Under 3.5", 1.48),
    BetMarket("BTTS", "Yes", 1.76),
    BetMarket("BTTS", "No", 2.02),
]
