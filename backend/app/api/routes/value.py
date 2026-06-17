from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import Container, get_container, get_value_service
from app.services.value_service import ValueService

router = APIRouter(prefix="/value-bets", tags=["value"])


@router.get("")
def value_bets(
    container: Container = Depends(get_container),
    value_service: ValueService = Depends(get_value_service),
) -> dict:
    """All flagged +EV value selections across every fixture, best EV first."""
    fixtures = container.fixtures.list_fixtures()
    bets = value_service.best_value_bets(fixtures)
    return {
        "count": len(bets),
        "settings": {
            "vig_method": container.settings.vig_method,
            "min_edge": container.settings.min_edge,
            "min_expected_value": container.settings.min_expected_value,
            "kelly_fraction": container.settings.kelly_fraction,
            "kelly_cap": container.settings.kelly_cap,
        },
        "bets": bets,
    }
