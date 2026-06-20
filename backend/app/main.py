"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import fixtures, health, predictions, teams, value
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "Soccer World Cup betting value analytics. Dixon-Coles model with "
            "time-decay weighting, vig removal, expected value and fractional "
            "Kelly staking. Bundled data is SYNTHETIC sample data for demo/testing."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(teams.router)
    app.include_router(predictions.router)
    app.include_router(fixtures.router)
    app.include_router(value.router)

    @app.get("/", tags=["meta"])
    def root() -> dict:
        return {
            "name": settings.app_name,
            "version": __version__,
            "docs": "/docs",
            "disclaimer": (
                "For analytics/education only. Markets are highly efficient; "
                "no model guarantees profit. Bet responsibly."
            ),
        }

    return app


app = create_app()
