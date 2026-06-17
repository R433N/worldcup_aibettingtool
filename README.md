# WorldCup AI Betting Tool

Sports analytics pipelines for football match intelligence, live momentum, live xG, Bet365 odds value, and prediction pages.

## What is included

- Live stats pipeline for score, shots, shots on goal, corners, cards, xG, and pressure/momentum chart data.
- Probability model for full-time result, half-time result, home win, away win, draw, and double chance.
- Team statistics for recent form, head-to-head, goals over/under, cards over/under, corners over/under, BTTS, clean sheets, conceded rate, and half with most goals.
- Player statistics for average shots on goal, shots attempted, assists, and cards.
- Bet365 odds adapter for licensed JSON exports, sportsbook implied probability, no-vig probability, model edge, expected ROI, and bankroll allocation.
- Predictions page with low-risk, medium-risk, high-risk, best pick, and a best parlay that targets 2.00x and requires at least 1.70x.

## Run locally

```bash
PYTHONPATH=src python -m worldcup_aibettingtool.cli build-dashboard --output site
python -m http.server 8000 --directory site
```

Open `http://localhost:8000`.

## Tests

```bash
PYTHONPATH=src python -m unittest
```

## Bet365 odds input

The project intentionally uses a provider adapter instead of scraping. To load a licensed Bet365 export, set `BET365_ODDS_JSON` to a JSON file containing:

```json
[
  {"market": "Fulltime Result", "selection": "Home", "decimal_odds": 2.42},
  {"market": "Fulltime Result", "selection": "Draw", "decimal_odds": 3.25},
  {"market": "Fulltime Result", "selection": "Away", "decimal_odds": 2.95}
]
```

The bundled sample data is Bet365-labeled demo data for development and testing only.
