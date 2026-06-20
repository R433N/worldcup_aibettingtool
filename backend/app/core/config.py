"""Application configuration via environment variables.

All tunables that affect statistical output (time-decay, Kelly fraction, value
thresholds, vig-removal method) are surfaced here so they are explicit and
auditable rather than scattered as magic numbers.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WCB_", env_file=".env", extra="ignore")

    app_name: str = "World Cup Betting Analytics"

    # Data sources
    matches_csv: Path = _DATA_DIR / "matches.csv"
    fixtures_csv: Path = _DATA_DIR / "fixtures.csv"

    # Model hyper-parameters
    time_decay_xi: float = 0.0019  # ~1-year half-life
    max_goals: int = 10

    # Market / staking parameters
    vig_method: str = "shin"  # "shin" | "proportional"
    kelly_fraction: float = 0.25  # quarter-Kelly
    kelly_cap: float = 0.05  # never stake > 5% of bankroll on one bet
    min_edge: float = 0.02  # require >= 2 percentage points of edge
    min_expected_value: float = 0.02  # require >= 2% EV

    # CORS for the local dashboard
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
