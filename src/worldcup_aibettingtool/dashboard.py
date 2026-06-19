"""Static dashboard generation for data-foundation monitoring."""

from __future__ import annotations

import json
from dataclasses import asdict
from html import escape
from pathlib import Path
from typing import Any

from .data_foundation import build_data_foundation_report
from .live_stats import head_to_head, player_averages, summarize_live_match, team_summary
from .sample_data import FIXTURE, HISTORICAL_MATCHES, LIVE_EVENTS, PLAYER_LINES


def build_report() -> dict[str, Any]:
    live = summarize_live_match(FIXTURE, LIVE_EVENTS)
    foundation = build_data_foundation_report()
    return {
        "fixture": asdict(FIXTURE),
        "live": live,
        "team_stats": [
            asdict(team_summary(FIXTURE.home.name, HISTORICAL_MATCHES)),
            asdict(team_summary(FIXTURE.away.name, HISTORICAL_MATCHES)),
        ],
        "head_to_head": head_to_head(FIXTURE.home.name, FIXTURE.away.name, HISTORICAL_MATCHES),
        "players": [asdict(row) for row in player_averages(PLAYER_LINES)],
        "data_foundation": foundation,
    }


def write_dashboard(output_dir: str | Path = "site") -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    report = build_report()
    (output / "data.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output / "data_foundation.json").write_text(
        json.dumps(report["data_foundation"], indent=2), encoding="utf-8"
    )
    (output / "index.html").write_text(_index_html(report), encoding="utf-8")
    (output / "data_foundation.html").write_text(_foundation_html(report), encoding="utf-8")
    legacy_predictions = output / "predictions.html"
    if legacy_predictions.exists():
        legacy_predictions.unlink()
    return output


def _index_html(report: dict[str, Any]) -> str:
    home = report["fixture"]["home"]["name"]
    away = report["fixture"]["away"]["name"]
    live = report["live"]["teams"]
    counts = report["data_foundation"]["warehouse_counts"]
    return _page(
        "Live data inputs",
        f"""
        <section class="hero">
          <div>
            <p class="eyebrow">FIFA 2026 betting data foundation</p>
            <h1>{escape(home)} vs {escape(away)}</h1>
            <p>Collection, cleaning, storage, and feature preparation only. No picks or model predictions are generated here.</p>
            <div class="actions"><a href="data_foundation.html">Open data foundation</a></div>
          </div>
          <div class="score-card">
            <span>Warehouse readiness</span>
            <strong>{counts["feature_snapshots"]} feature snapshot</strong>
            <small>{counts["sources"]} sources cataloged · {counts["odds_snapshots"]} odds snapshots stored</small>
          </div>
        </section>
        <section class="panel">
          <div class="section-head">
            <h2>Live pressure and xG inputs</h2>
            <p>Weighted event momentum and xG feed the feature store, not a betting recommendation.</p>
          </div>
          {_pressure_svg(report["live"]["pressure_timeline"])}
        </section>
        <section class="grid two">
          {_live_team_card(home, live[home])}
          {_live_team_card(away, live[away])}
        </section>
        <section class="panel">
          <div class="section-head"><h2>Team form inputs</h2><p>Recent form, H2H, goals, cards, corners, BTTS, clean sheets, conceded rate, and goal timing.</p></div>
          {_team_table(report)}
        </section>
        <section class="panel">
          <div class="section-head"><h2>Player statistics inputs</h2><p>Shots on goal, shot attempts, assists, and cards per appearance.</p></div>
          {_players_table(report["players"])}
        </section>
        """,
    )


def _foundation_html(report: dict[str, Any]) -> str:
    foundation = report["data_foundation"]
    feature = foundation["feature_snapshot"]
    return _page(
        "Data foundation",
        f"""
        <section class="hero">
          <div>
            <p class="eyebrow">No-prediction data pipeline</p>
            <h1>Model-ready World Cup data</h1>
            <p>{escape(foundation["no_prediction_policy"])}</p>
          </div>
          <div class="score-card">
            <span>Feature target</span>
            <strong>{escape(feature["match_id"])}</strong>
            <small>{escape(feature["home_team"])} vs {escape(feature["away_team"])}</small>
          </div>
        </section>
        <section class="panel">
          <div class="section-head"><h2>Reliable free source catalog</h2><p>Primary feeds, access model, reliability, cadence, and betting-useful fields.</p></div>
          {_source_table(foundation["source_readiness"])}
        </section>
        <section class="grid two">
          <article class="panel">
            <h2>Warehouse coverage</h2>
            {_counts_list(foundation["warehouse_counts"])}
          </article>
          <article class="panel">
            <h2>Automatic update plan</h2>
            {_update_jobs(foundation["update_plan"])}
          </article>
        </section>
        <section class="panel">
          <div class="section-head"><h2>Opening vs current odds movement</h2><p>Sportsbook-implied probability movement only; no AI value judgement is made.</p></div>
          {_odds_movement_table(foundation["odds_movements"])}
        </section>
        <section class="panel">
          <div class="section-head"><h2>Prepared feature snapshot</h2><p>Clean model inputs for moneyline, handicap, totals, BTTS, cards, and corners markets.</p></div>
          {_feature_table(feature["features"])}
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
  <nav><a href="index.html">Live inputs</a><a href="data_foundation.html">Data foundation</a></nav>
  <main>{body}</main>
</body>
</html>"""


def _live_team_card(team: str, stats: dict[str, Any]) -> str:
    rows = "".join(
        f"<li><span>{escape(key.replace('_', ' ').title())}</span><strong>{value}</strong></li>"
        for key, value in stats.items()
    )
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


def _source_table(sources: list[dict[str, str]]) -> str:
    rows = "".join(
        f"""<tr><td>{escape(row["primary_source"])}</td><td>{escape(row["area"])}</td><td>{escape(row["free_access"])}</td><td>{escape(row["reliability"])}</td><td>{escape(row["cadence"])}</td><td>{escape(row["fields"])}</td></tr>"""
        for row in sources
    )
    return f"""<div class="table-wrap"><table><thead><tr><th>Source</th><th>Area</th><th>Access</th><th>Reliability</th><th>Cadence</th><th>Fields</th></tr></thead><tbody>{rows}</tbody></table></div>"""


def _odds_movement_table(movements: list[dict[str, Any]]) -> str:
    rows = "".join(
        f"""<tr><td>{escape(row["sportsbook"])}</td><td>{escape(row["market"])}</td><td>{escape(row["selection"])}</td><td>{row["opening_odds"]:.2f}</td><td>{row["current_odds"]:.2f}</td><td>{row["implied_probability_open"]:.1%}</td><td>{row["implied_probability_current"]:.1%}</td><td>{row["implied_probability_delta"]:+.1%}</td></tr>"""
        for row in movements
    )
    return f"""<div class="table-wrap"><table><thead><tr><th>Sportsbook</th><th>Market</th><th>Selection</th><th>Opening</th><th>Current</th><th>Open prob</th><th>Current prob</th><th>Move</th></tr></thead><tbody>{rows}</tbody></table></div>"""


def _feature_table(features: dict[str, Any]) -> str:
    rows = "".join(
        f"""<tr><td>{escape(str(key))}</td><td>{escape(str(value))}</td></tr>"""
        for key, value in sorted(features.items())
    )
    return f"""<div class="table-wrap feature-table"><table><thead><tr><th>Feature</th><th>Value</th></tr></thead><tbody>{rows}</tbody></table></div>"""


def _counts_list(counts: dict[str, int]) -> str:
    rows = "".join(
        f"<li><span>{escape(table.replace('_', ' ').title())}</span><strong>{count}</strong></li>"
        for table, count in counts.items()
    )
    return f"""<ul class="stat-list">{rows}</ul>"""


def _update_jobs(jobs: list[dict[str, str]]) -> str:
    rows = "".join(
        f"<li><strong>{escape(job['job'])}</strong><span>{escape(job['cadence'])}</span><small>{escape(job['purpose'])}</small></li>"
        for job in jobs
    )
    return f"""<ul class="job-list">{rows}</ul>"""


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


def _css() -> str:
    return """
    :root { color-scheme: dark; --bg:#08111f; --panel:#101b2e; --text:#f5f7fb; --muted:#9fb1ca; --accent:#2ee59d; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: radial-gradient(circle at top left, #16365d, var(--bg) 36rem); color:var(--text); }
    nav { position:sticky; top:0; z-index:2; display:flex; gap:1rem; padding:1rem clamp(1rem,4vw,3rem); background:rgba(8,17,31,.82); backdrop-filter: blur(12px); border-bottom:1px solid rgba(255,255,255,.08); }
    nav a, .actions a { color:var(--text); text-decoration:none; border:1px solid rgba(255,255,255,.15); padding:.65rem .9rem; border-radius:999px; }
    main { width:min(1180px, calc(100% - 2rem)); margin:0 auto; padding:2rem 0 4rem; }
    .hero { display:grid; grid-template-columns:minmax(0,1fr) 340px; gap:1.5rem; align-items:stretch; margin:1rem 0 1.5rem; }
    h1 { font-size:clamp(2.4rem,6vw,5rem); line-height:.95; margin:.25rem 0 1rem; letter-spacing:-.06em; }
    h2, h3, p { margin-top:0; }
    .eyebrow, .card span { color:var(--accent); text-transform:uppercase; letter-spacing:.12em; font-size:.75rem; font-weight:800; }
    .score-card, .card, .panel { background:linear-gradient(145deg, rgba(255,255,255,.08), rgba(255,255,255,.03)); border:1px solid rgba(255,255,255,.1); border-radius:24px; box-shadow:0 24px 80px rgba(0,0,0,.22); }
    .score-card { padding:1.5rem; display:flex; flex-direction:column; justify-content:center; }
    .score-card strong { font-size:2.35rem; line-height:1; }
    .score-card small, .section-head p, .callout, .job-list small { color:var(--muted); }
    .grid { display:grid; gap:1rem; margin:1rem 0; }
    .two { grid-template-columns:repeat(2,minmax(0,1fr)); }
    .card, .panel { padding:1.2rem; }
    .stat-list, .job-list { list-style:none; padding:0; margin:0; display:grid; gap:.6rem; }
    .stat-list li { display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,.08); padding-bottom:.45rem; }
    .job-list li { display:grid; gap:.2rem; border-bottom:1px solid rgba(255,255,255,.08); padding-bottom:.65rem; }
    .section-head { display:flex; align-items:end; justify-content:space-between; gap:1rem; }
    .pressure { width:100%; height:auto; background:rgba(0,0,0,.16); border-radius:18px; }
    .pressure line { stroke:rgba(255,255,255,.18); stroke-width:2; }
    .pressure polyline { fill:none; stroke:var(--accent); stroke-width:5; stroke-linecap:round; stroke-linejoin:round; filter:drop-shadow(0 0 10px rgba(46,229,157,.55)); }
    .pressure text { fill:var(--muted); font-size:15px; }
    .table-wrap { overflow:auto; }
    table { width:100%; border-collapse:collapse; min-width:780px; }
    .players-table table { min-width:0; }
    .players-table th, .players-table td { padding:.65rem .55rem; }
    .feature-table table { min-width:0; }
    th, td { text-align:left; padding:.8rem; border-bottom:1px solid rgba(255,255,255,.08); white-space:nowrap; }
    th { color:var(--muted); font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; }
    .callout { background:rgba(46,229,157,.08); border:1px solid rgba(46,229,157,.18); border-radius:16px; padding:1rem; }
    @media (max-width: 880px) { .hero, .two { grid-template-columns:1fr; } .section-head { display:block; } }
    """
