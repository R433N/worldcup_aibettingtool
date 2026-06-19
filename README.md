# WorldCup AI Betting Tool

Data foundation and analytics dashboard for FIFA 2026 World Cup betting analytics.

The Python backend collects, cleans, stores, and prepares football data for a downstream AI model. It does **not** make betting predictions, recommend wagers, or calculate "best bets."

The Next.js frontend provides a dashboard for groups, standings, knockout-stage paths, match dashboards, charts, and bet recommendation screens.

## Technical decisions

- **SQLite warehouse first:** dependency-light, testable, and easy to migrate to Postgres when deployment needs concurrent writers.
- **Raw payload retention:** every provider response is stored before normalization so source changes can be audited and replayed.
- **Provider-neutral ingestion:** free/free-tier API and CSV feeds can plug into the same normalized schema.
- **Odds movement only:** opening and current odds are converted to sportsbook-implied probabilities; no value judgement is made.
- **Feature snapshots:** betting-useful inputs are prepared for moneyline, handicap, totals, BTTS, cards, and corners models.

## Reliable free and free-tier sources

- `football-data.org` for fixtures, results, standings, and goals data.
- `StatsBomb Open Data` for historical event data, xG, shots, player events, and lineups.
- `Open-Meteo` for venue weather forecasts.
- `The Odds API` free tier for bookmaker odds where available.
- `football-data.co.uk` for historical results and odds CSVs.
- `Kaggle FIFA World Cup datasets` for historical tournament enrichment after provenance checks.
- `OpenStreetMap / Nominatim` for stadium coordinates and location factors.
- Official FIFA/team public reports for injuries, suspensions, and lineup confirmation where permitted.

## Warehouse coverage

The schema covers:

- FIFA 2026 matches, venues, teams, referees, and results.
- Team form, recent results, goals scored/conceded, xG, shots, shots on target, possession, cards, and corners.
- Player match statistics.
- Injuries, suspensions, and starting lineups.
- Referee yellow-card, red-card, and penalty rates.
- Weather snapshots and stadium/location factors.
- Historical World Cup performance.
- Opening/current odds snapshots and implied-probability movement.
- Model-ready feature snapshots.

## Python backend

### Run locally

```bash
PYTHONPATH=src python3 -m worldcup_aibettingtool.cli build-dashboard --output site
python3 -m http.server 8000 --directory site
```

Open `http://localhost:8000`.

### Generate data artifacts only

```bash
PYTHONPATH=src python3 -m worldcup_aibettingtool.cli build-data-foundation --output site
```

This writes `site/data_foundation.json`.

### Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Next.js frontend

```bash
npm run dev
npm run build
npm run lint
npm run typecheck
```
