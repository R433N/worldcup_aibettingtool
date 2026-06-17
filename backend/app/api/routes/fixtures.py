from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import Container, get_container, get_value_service
from app.services.value_service import ValueService

router = APIRouter(prefix="/fixtures", tags=["fixtures"])


@router.get("")
def list_fixtures(container: Container = Depends(get_container)) -> list[dict]:
    """Upcoming fixtures with their bundled bookmaker odds."""
    return [
        {
            "fixture_id": f.fixture_id,
            "home": f.home,
            "away": f.away,
            "kickoff": f.kickoff.isoformat(),
            "neutral": f.neutral,
            "markets": [o.market for o in f.odds],
        }
        for f in container.fixtures.list_fixtures()
    ]


@router.get("/{fixture_id}/analysis")
def analyse_fixture(
    fixture_id: str,
    container: Container = Depends(get_container),
    value_service: ValueService = Depends(get_value_service),
) -> dict:
    """Full value analysis (model vs market) for a single fixture."""
    fixture = container.fixtures.get_fixture(fixture_id)
    if fixture is None:
        raise HTTPException(status_code=404, detail=f"Unknown fixture: {fixture_id}")
    return value_service.analyse_fixture(fixture)
