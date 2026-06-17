from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_prediction_service
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predict", tags=["predictions"])


@router.get("")
def predict(
    home: str = Query(..., description="Home team name"),
    away: str = Query(..., description="Away team name"),
    neutral: bool = Query(True, description="Neutral venue (World Cup default)"),
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> dict:
    """Model probabilities (1X2, O/U 2.5, BTTS) for an arbitrary matchup."""
    try:
        return prediction_service.predict(home, away, neutral=neutral)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
