import { useEffect, useState } from 'react'
import { api } from '../api'
import type { FixtureAnalysis, FixtureSummary } from '../types'
import { kickoff, label, odds, pct, signedPct } from '../format'

function AnalysisTable({ analysis }: { analysis: FixtureAnalysis }) {
  return (
    <div className="panel">
      <h2>
        {analysis.home} <span className="muted">v</span> {analysis.away}
      </h2>
      <p className="sub">
        {kickoff(analysis.kickoff)} · {analysis.neutral ? 'Neutral venue' : 'Home venue'}
      </p>
      {analysis.markets.map((m) => (
        <div key={m.market} style={{ marginBottom: 18 }}>
          <h3 style={{ margin: '8px 0', fontSize: 15 }}>
            {m.market}{' '}
            <span className="muted" style={{ fontWeight: 400, fontSize: 13 }}>
              · {m.bookmaker} · overround {pct(m.overround)}
            </span>
          </h3>
          <table>
            <thead>
              <tr>
                <th>Selection</th>
                <th>Odds</th>
                <th>Model</th>
                <th>Fair</th>
                <th>Edge</th>
                <th>EV</th>
                <th>Stake</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {m.selections.map((s) => (
                <tr key={s.selection} className={s.is_value ? 'value-row' : ''}>
                  <td className="left">{label(s.selection)}</td>
                  <td>{odds(s.decimal_odds)}</td>
                  <td>{pct(s.model_probability)}</td>
                  <td>{pct(s.market_probability)}</td>
                  <td className={s.edge >= 0 ? 'pos' : 'neg'}>{signedPct(s.edge)}</td>
                  <td className={s.expected_value >= 0 ? 'pos' : 'neg'}>
                    {signedPct(s.expected_value)}
                  </td>
                  <td>{s.kelly_fraction > 0 ? pct(s.kelly_fraction) : '—'}</td>
                  <td>{s.is_value ? <span className="badge value">VALUE</span> : ''}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  )
}

export function Fixtures() {
  const [fixtures, setFixtures] = useState<FixtureSummary[] | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const [analysis, setAnalysis] = useState<FixtureAnalysis | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.fixtures().then(setFixtures).catch((e) => setError(String(e)))
  }, [])

  const selectFixture = (id: string) => {
    setSelected(id)
    setAnalysis(null)
    api.fixtureAnalysis(id).then(setAnalysis).catch((e) => setError(String(e)))
  }

  if (error) return <div className="error">Failed to load fixtures: {error}</div>
  if (!fixtures) return <div className="loading">Loading fixtures…</div>

  return (
    <>
      <div className="panel">
        <h2>Fixtures</h2>
        <p className="sub">Select a fixture to see the full model-vs-market breakdown.</p>
        <div className="fixture-grid">
          {fixtures.map((f) => (
            <div
              key={f.fixture_id}
              className="fixture-card"
              onClick={() => selectFixture(f.fixture_id)}
              style={{
                borderColor: selected === f.fixture_id ? 'var(--accent)' : undefined,
              }}
            >
              <div className="teams">
                {f.home} <span className="muted">v</span> {f.away}
              </div>
              <div className="meta">
                {kickoff(f.kickoff)} · {f.markets.length} markets
              </div>
            </div>
          ))}
        </div>
      </div>
      {selected && !analysis && <div className="loading">Analysing fixture…</div>}
      {analysis && <AnalysisTable analysis={analysis} />}
    </>
  )
}
