"""WorldCup AI Betting Tool analytics package."""

from .dashboard import build_report, write_dashboard
from .live_stats import summarize_live_match, team_summary
from .odds import Bet365OddsProvider, evaluate_odds
from .predictions import build_predictions
from .probability import build_probability_snapshot

__all__ = [
    "Bet365OddsProvider",
    "build_predictions",
    "build_probability_snapshot",
    "build_report",
    "evaluate_odds",
    "summarize_live_match",
    "team_summary",
    "write_dashboard",
]
