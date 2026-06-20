from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_model_service
from app.services.model_service import ModelService

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/ratings")
def team_ratings(model_service: ModelService = Depends(get_model_service)) -> list[dict]:
    """Fitted attack/defence ratings for every team, ranked by overall strength."""
    return model_service.ratings()
