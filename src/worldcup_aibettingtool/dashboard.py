"""Static dashboard generation for analytics and prediction pages."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from html import escape
from pathlib import Path
from typing import Any

from .live_stats import head_to_head, player_averages, summarize_live_match, team_summary
from .odds import evaluate_odds, total_money_allocation
from .predictions import build_predictions
from .probability import build_probability_snapshot
from .sample_data import BET365_MARKETS, FIXTURE, HISTORICAL_MATCHES, LIVE_EVENTS, PLAYER_LINES


def build_report() -> dict[str, Any]:
    live = summarize_live_match(FIXTURE, LIVE_EVENTS)
    probability = build_probability_snapshot(
        FIXTURE,
        HISTORICAL_MATCHES,
        live_xg_home=live["teams"][FIXTURE.home.name]["xg"],
        live_xg_away=live["teams"][FIXTURE.away.name]["xg"],
        live_minute=max(event.minute for event in LIVE_EVENTS),
    )
    odds_values = evaluate_odds(BET365_MARKETS, probability)
    return {
        "fixture": asdict(FIXTURE),
        "live": live,
        "probability": asdict(probability),
        "team_stats": [
            asdict(team_summary(FIXTURE.home.name, HISTORICAL_MATCHES)),
            asdict(team_summary(FIXTURE.away.name, HISTORICAL_MATCHES)),
        ],
        "head_to_head": head_to_head(FIXTURE.home.name, FIXTURE.away.name, HISTORICAL_MATCHES),
        "players": [asdict(row) for row in player_averages(PLAYER_LINES)],
        "odds_values": [asdict(row) for row in odds_values],
        "total_allocation_pct": total_money_allocation(odds_values),
        "predictions": _serialize(build_predictions(odds_values)),
    }


def write_dashboard(output_dir: str | Path = "site") -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    report = build_report()
    (output / "data.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output / "index.html").write_text(_index_html(report), encoding="utf-8")
    (output / "predictions.html").write_text(_predictions_html(report), encoding="utf-8")
    return output


def _index_html(report: dict[str, Any]) -> str:
    home = report["fixture"]["home"]["name"]
    away = report["fixture"]["away"]["name"]
    probability = report["probability"]
    live = report["live"]["teams"]
    return _page(
        "Live analytics",
        f"""
        <section class="hero">
          <div>
            <p class="eyebrow">Live football analytics command center</p>
            <h1>{escape(home)} vs {escape(away)}</h1>
            <p>Live stats, xG, pressure momentum, team trends, player averages, and Bet365 market value.</p>
            <div class="actions"><a href="predictions.html">Open predictions page</a></div>
          </div>
          <div class="score-card">
            <span>Live xG</span>
            <strong>{live[home]["xg"]:.2f} - {live[away]["xg"]:.2f}</strong>
            <small>{escape(home)} pressure {report["live"]["pressure_timeline"][-1]["home_pressure"]:.2f} / {escape(away)} {report["live"]["pressure_timeline"][-1]["away_pressure"]:.2f}</small>
          </div>
        </section>
        <section class="grid three">
          {_metric_card("Home win", probability["fulltime_home_win"])}
          {_metric_card("Draw", probability["fulltime_draw"])}
          {_metric_card("Away win", probability["fulltime_away_win"])}
        </section>
        <section class="panel">
          <div class="section-head">
            <h2>Pressure formula momentum</h2>
            <p>Weighted goals, shots on goal, shots, corners, dangerous attacks, and cards with 10-minute decay.</p>
          </div>
          {_pressure_svg(report["live"]["pressure_timeline"])}
        </section>
        <section class="grid two">
          {_live_team_card(home, live[home])}
          {_live_team_card(away, live[away])}
        </section>
        <section class="panel">
          <div class="section-head"><h2>Team statistics</h2><p>Recent form, H2H, totals, BTTS, clean sheets, and goal timing.</p></div>
          {_team_table(report)}
        </section>
        <section class="panel">
          <div class="section-head"><h2>Player averages</h2><p>Shots on goal, shot attempts, assists, and cards per appearance.</p></div>
          {_players_table(report["players"])}
        </section>
        """,
    )


def _predictions_html(report: dict[str, Any]) -> str:
    predictions = report["predictions"]
    probability = report["probability"]
    parlay = predictions["best_parlay"]
    return _page(
        "Predictions",
        f"""
        <section class="hero">
          <div>
            <p class="eyebrow">Predictions page</p>
            <h1>Best bets from model edge and Bet365 prices</h1>
            <p>Risk bands combine market type, odds range, model probability, and no-vig sportsbook probability.</p>
          </div>
          <div class="score-card">
            <span>Total allocation</span>
            <strong>{report["total_allocation_pct"]:.2f}%</strong>
            <small>Fractional Kelly capped per wager</small>
          </div>
        </section>
        <section class="grid four">
          {_prediction_card(predictions["low_risk"])}
          {_prediction_card(predictions["medium_risk"])}
          {_prediction_card(predictions["high_risk"])}
          {_prediction_card(predictions["best_pick"])}
        </section>
        <section class="panel parlay">
          <div>
            <p class="eyebrow">Best parlay</p>
            <h2>{parlay["combined_odds"]:.2f}x combined odds</h2>
            <p>Minimum 1.70x met: <strong>{str(parlay["minimum_odds_met"])}</strong>; 2.00x target met: <strong>{str(parlay["target_odds_met"])}</strong>.</p>
          </div>
          <ul>
            {"".join(f"<li>{escape(leg['market'])}: {escape(leg['selection'])} @ {leg['odds']:.2f}</li>" for leg in parlay["legs"])}
          </ul>
        </section>
        <section class="grid three">
          {_metric_card("HT home", probability["halftime_home_win"])}
          {_metric_card("HT draw", probability["halftime_draw"])}
          {_metric_card("HT away", probability["halftime_away_win"])}
        </section>
        <section class="grid three">
          {_metric_card("Home/draw", probability["double_chance_home_or_draw"])}
          {_metric_card("Away/draw", probability["double_chance_away_or_draw"])}
          {_metric_card("Home/away", probability["double_chance_home_or_away"])}
        </section>
        <section class="panel">
          <div class="section-head"><h2>Odds value calculator</h2><p>Sportsbook probability, no-vig market probability, model probability, ROI, edge, and allocation.</p></div>
          {_odds_table(report["odds_values"])}
        </section>
        """,
    )


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)} | WorldCup AI Betting Tool</title>
  <style>{_css()}</style>
</head>
<body>
  <nav><a href="index.html">Live analytics</a><a href="predictions.html">Predictions</a></nav>
  <main>{body}</main>
</body>
</html>"""


def _metric_card(label: str, probability: float) -> str:
    return f"""<article class="card metric"><span>{escape(label)}</span><strong>{probability:.1%}</strong></article>"""


def _live_team_card(team: str, stats: dict[str, Any]) -> str:
    rows = "".join(f"<li><span>{escape(key.replace('_', ' ').title())}</span><strong>{value}</strong></li>" for key, value in stats.items())
    return f"""<article class="card"><h3>{escape(team)} live stats</h3><ul class="stat-list">{rows}</ul></article>"""


def _team_table(report: dict[str, Any]) -> str:
    rows = "".join(
        f"""<tr><td>{escape(row["team"])}</td><td>{escape(row["recent_form"])}</td><td>{row["goals_for_avg"]:.2f}</td><td>{row["goals_against_avg"]:.2f}</td><td>{row["over_25_goals_pct"]:.1f}%</td><td>{row["cards_avg"]:.2f}</td><td>{row["corners_avg"]:.2f}</td><td>{row["btts_pct"]:.1f}%</td><td>{row["clean_sheet_pct"]:.1f}%</td><td>{escape(row["half_with_most_goals"])}</td></tr>"""
        for row in report["team_stats"]
    )
    h2h = report["head_to_head"]
    return f"""
    <p class="callout">Head-to-head: {h2h["matches"]} matches, home record {escape(str(h2h["home_team_record"]))}, {h2h["goals_avg"]:.2f} goals avg, {h2h["cards_avg"]:.2f} cards avg, {h2h["corners_avg"]:.2f} corners avg, BTTS {h2h["btts_pct"]:.1f}%.</p>
    <div class="table-wrap"><table><thead><tr><th>Team</th><th>Form</th><th>GF avg</th><th>GA avg</th><th>Over 2.5</th><th>Cards avg</th><th>Corners avg</th><th>BTTS</th><th>Clean sheets</th><th>Most goals</th></tr></thead><tbody>{rows}</tbody></table></div>
    """


def _players_table(players: list[dict[str, Any]]) -> str:
    rows = "".join(
        f"""<tr><td>{escape(row["player"])}</td><td>{escape(row["team"])}</td><td>{row["shots_on_goal_avg"]:.2f}</td><td>{row["shots_attempted_avg"]:.2f}</td><td>{row["assists_avg"]:.2f}</td><td>{row["cards_avg"]:.2f}</td></tr>"""
        for row in players
    )
    return f"""<div class="table-wrap players-table"><table><thead><tr><th>Player</th><th>Team</th><th>SOG avg</th><th>Shots avg</th><th>Assists avg</th><th>Cards avg</th></tr></thead><tbody>{rows}</tbody></table></div>"""


def _odds_table(values: list[dict[str, Any]]) -> str:
    rows = "".join(
        f"""<tr><td>{escape(row["market"])}</td><td>{escape(row["selection"])}</td><td>{row["decimal_odds"]:.2f}</td><td>{row["sportsbook_probability"]:.1%}</td><td>{row["no_vig_probability"]:.1%}</td><td>{row["model_probability"]:.1%}</td><td>{row["expected_roi"]:.1%}</td><td>{row["edge"]:.1%}</td><td>{row["allocation_pct"]:.2f}%</td><td>{escape(row["risk"])}</td></tr>"""
        for row in values
    )
    return f"""<div class="table-wrap"><table><thead><tr><th>Market</th><th>Selection</th><th>Odds</th><th>Book prob</th><th>No-vig</th><th>Model</th><th>ROI</th><th>Edge</th><th>Allocation</th><th>Risk</th></tr></thead><tbody>{rows}</tbody></table></div>"""


def _prediction_card(card: dict[str, Any] | None) -> str:
    if not card:
        return """<article class="card pick"><span>No positive value</span><strong>Pass</strong><p>Model edge is not high enough.</p></article>"""
    return f"""<article class="card pick"><span>{escape(card["title"])}</span><strong>{escape(card["selection"])} @ {card["odds"]:.2f}</strong><p>{escape(card["market"])} · {card["model_probability"]:.1%} model · {card["expected_roi"]:.1%} ROI · {card["allocation_pct"]:.2f}% allocation</p><small>{escape(card["rationale"])}</small></article>"""


def _pressure_svg(timeline: list[dict[str, float]]) -> str:
    width, height, pad = 840, 240, 28
    points = []
    for index, row in enumerate(timeline):
        x = pad + index * ((width - pad * 2) / max(len(timeline) - 1, 1))
        y = height / 2 - (row["momentum"] / 100) * ((height - pad * 2) / 2)
        points.append(f"{x:.1f},{y:.1f}")
    return f"""<svg class="pressure" viewBox="0 0 {width} {height}" role="img" aria-label="Pressure momentum chart">
      <line x1="{pad}" y1="{height/2}" x2="{width-pad}" y2="{height/2}" />
      <polyline points="{" ".join(points)}" />
      <text x="{pad}" y="24">Home pressure</text>
      <text x="{width-pad-110}" y="{height-12}">Away pressure</text>
    </svg>"""


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return {key: _serialize(row) for key, row in value.items()}
    if isinstance(value, list):
        return [_serialize(row) for row in value]
    return value


def _css() -> str:
    return """
    :root { color-scheme: dark; --bg:#08111f; --panel:#101b2e; --panel2:#14243c; --text:#f5f7fb; --muted:#9fb1ca; --accent:#2ee59d; --away:#ff6b6b; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: radial-gradient(circle at top left, #16365d, var(--bg) 36rem); color:var(--text); }
    nav { position:sticky; top:0; z-index:2; display:flex; gap:1rem; padding:1rem clamp(1rem,4vw,3rem); background:rgba(8,17,31,.82); backdrop-filter: blur(12px); border-bottom:1px solid rgba(255,255,255,.08); }
    nav a, .actions a { color:var(--text); text-decoration:none; border:1px solid rgba(255,255,255,.15); padding:.65rem .9rem; border-radius:999px; }
    main { width:min(1180px, calc(100% - 2rem)); margin:0 auto; padding:2rem 0 4rem; }
    .hero { display:grid; grid-template-columns: minmax(0, 1fr) 320px; gap:1.5rem; align-items:stretch; margin:1rem 0 1.5rem; }
    h1 { font-size:clamp(2.5rem, 6vw, 5rem); line-height:.95; margin:.25rem 0 1rem; letter-spacing:-.06em; }
    h2, h3, p { margin-top:0; }
    .eyebrow, .card span { color:var(--accent); text-transform:uppercase; letter-spacing:.12em; font-size:.75rem; font-weight:800; }
    .score-card, .card, .panel { background:linear-gradient(145deg, rgba(255,255,255,.08), rgba(255,255,255,.03)); border:1px solid rgba(255,255,255,.1); border-radius:24px; box-shadow:0 24px 80px rgba(0,0,0,.22); }
    .score-card { padding:1.5rem; display:flex; flex-direction:column; justify-content:center; }
    .score-card strong { font-size:3rem; line-height:1; }
    .score-card small, .card p, .card small, .section-head p, .callout { color:var(--muted); }
    .grid { display:grid; gap:1rem; margin:1rem 0; }
    .two { grid-template-columns:repeat(2,minmax(0,1fr)); }
    .three { grid-template-columns:repeat(3,minmax(0,1fr)); }
    .four { grid-template-columns:repeat(4,minmax(0,1fr)); }
    .card, .panel { padding:1.2rem; }
    .metric strong { display:block; font-size:2.4rem; margin-top:.4rem; }
    .pick strong { display:block; font-size:1.35rem; margin:.5rem 0; }
    .stat-list { list-style:none; padding:0; margin:0; display:grid; gap:.5rem; }
    .stat-list li { display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,.08); padding-bottom:.45rem; }
    .section-head { display:flex; align-items:end; justify-content:space-between; gap:1rem; }
    .pressure { width:100%; height:auto; background:rgba(0,0,0,.16); border-radius:18px; }
    .pressure line { stroke:rgba(255,255,255,.18); stroke-width:2; }
    .pressure polyline { fill:none; stroke:var(--accent); stroke-width:5; stroke-linecap:round; stroke-linejoin:round; filter:drop-shadow(0 0 10px rgba(46,229,157,.55)); }
    .pressure text { fill:var(--muted); font-size:15px; }
    .table-wrap { overflow:auto; }
    table { width:100%; border-collapse:collapse; min-width:780px; }
    .players-table table { min-width:0; }
    .players-table th, .players-table td { padding:.65rem .55rem; }
    th, td { text-align:left; padding:.8rem; border-bottom:1px solid rgba(255,255,255,.08); white-space:nowrap; }
    th { color:var(--muted); font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; }
    .callout { background:rgba(46,229,157,.08); border:1px solid rgba(46,229,157,.18); border-radius:16px; padding:1rem; }
    .parlay { display:grid; grid-template-columns:1fr 1fr; gap:1rem; align-items:center; }
    .parlay li { margin:.5rem 0; }
    @media (max-width: 880px) { .hero, .two, .three, .four, .parlay { grid-template-columns:1fr; } .section-head { display:block; } }
    """
