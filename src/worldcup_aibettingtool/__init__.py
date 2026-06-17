"""WorldCup AI Betting Tool analytics package."""

from .dashboard import build_report, write_dashboard
from .data_foundation import build_data_foundation_report, seed_demo_warehouse
from .live_stats import summarize_live_match, team_summary
from .odds import JsonOddsProvider, calculate_movements, implied_probability
from .source_catalog import recommended_sources
from .warehouse import BettingDataWarehouse

__all__ = [
    "BettingDataWarehouse",
    "JsonOddsProvider",
    "build_data_foundation_report",
    "build_report",
    "calculate_movements",
    "implied_probability",
    "recommended_sources",
    "seed_demo_warehouse",
    "summarize_live_match",
    "team_summary",
    "write_dashboard",
]
