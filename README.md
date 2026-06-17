# worldcup_aibettingtool

A soccer World Cup **betting value analytics platform**. It models match
scorelines with a **Dixon-Coles** model, converts bookmaker odds into vig-free
"fair" prices, and surfaces selections where the model has a positive expected
value (an *edge*) over the market — with disciplined fractional-Kelly staking.

> ⚠️ **Honest framing.** No model can reliably predict individual soccer matches,
> and the World Cup betting market is highly efficient. This tool aims for
> *well-calibrated probabilities* and *positive-EV selections*, not certainty.
> The bundled data is **synthetic sample data** for demonstration and testing.
> For analytics/education only — bet responsibly.

## Architecture

Clean, layered, and framework-light:

```
backend/app/
  domain/          Pure entities & value objects (no framework deps)
  stats/           Statistical engine (pure functions): Poisson, Dixon-Coles,
                   market derivation, odds/vig/EV/Kelly math
  services/        Application layer (fit model, predict, find value)
  infrastructure/  Data repositories (CSV sample data behind protocols)
  api/             FastAPI routes + dependency wiring
  data/            Generated sample CSVs
frontend/          React + Vite + TypeScript dashboard
```

The statistical core is intentionally isolated from FastAPI so it is trivially
unit-testable and reusable. Data access sits behind repository protocols so a
real feed (e.g. football-data.org / API-Football) can replace the sample CSVs
without touching the model or services.

### The model

- **Dixon-Coles (1997)**: per-team attack/defence strengths + home advantage,
  fit by **time-weighted maximum likelihood** (recent matches weighted more via
  exponential decay `xi`), with the low-score dependence correction `rho`.
- **Markets** (1X2, Over/Under 2.5, BTTS) are derived from a single joint
  scoreline distribution, so they are always mutually consistent.
- **Vig removal**: proportional and **Shin's method** (corrects the
  favourite-longshot bias).
- **Staking**: **fractional Kelly**, capped, never sizing on a negative edge.

## Quick start

### Backend (Python 3.11+)

```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
python -m scripts.generate_sample_data   # writes app/data/*.csv (committed already)
uvicorn app.main:app --reload            # http://localhost:8000  (docs at /docs)
```

Lint / type-check / test:

```bash
ruff check . && mypy app && pytest
```

### Frontend (Node 18+)

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173  (proxies /api -> http://localhost:8000)
```

Run the backend first; the dashboard calls it through the Vite dev proxy.

## Key API endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/health` | Liveness |
| GET | `/teams/ratings` | Fitted attack/defence ratings, ranked |
| GET | `/predict?home=&away=&neutral=` | Model market probabilities for a matchup |
| GET | `/fixtures` | Upcoming fixtures with bundled odds |
| GET | `/fixtures/{id}/analysis` | Full model-vs-market value breakdown |
| GET | `/value-bets` | All flagged +EV selections, best EV first |
