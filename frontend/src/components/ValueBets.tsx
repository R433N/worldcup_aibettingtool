import { useEffect, useState } from 'react'
import { api } from '../api'
import type { ValueBetsResponse } from '../types'
import { kickoff, label, odds, pct, signedPct } from '../format'

export function ValueBets() {
  const [data, setData] = useState<ValueBetsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.valueBets().then(setData).catch((e) => setError(String(e)))
  }, [])

  if (error) return <div className="error">Failed to load value bets: {error}</div>
  if (!data) return <div className="loading">Fitting model & scanning the market…</div>

  return (
    <div className="panel">
      <h2>Value Bets</h2>
      <p className="sub">
        {data.count} selection{data.count === 1 ? '' : 's'} where the model edge clears{' '}
        {pct(data.settings.min_edge)} and EV clears {pct(data.settings.min_expected_value)}.
        Vig removed via <span className="chip">{data.settings.vig_method}</span>; stakes are{' '}
        {data.settings.kelly_fraction}× Kelly, capped at {pct(data.settings.kelly_cap)} of bankroll.
      </p>
      {data.count === 0 ? (
        <p className="muted">No value found — the market is efficient right now.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Match</th>
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
            {data.bets.map((b, i) => (
              <tr key={i} className="value-row">
                <td className="left">
                  <div>
                    {b.home} <span className="muted">v</span> {b.away}
                  </div>
                  <div className="muted" style={{ fontSize: 12 }}>
                    {kickoff(b.kickoff)} · {b.market}
                  </div>
                </td>
                <td className="left">{label(b.selection)}</td>
                <td>{odds(b.decimal_odds)}</td>
                <td>{pct(b.model_probability)}</td>
                <td>{pct(b.market_probability)}</td>
                <td className="pos">{signedPct(b.edge)}</td>
                <td className="pos">{signedPct(b.expected_value)}</td>
                <td>{pct(b.kelly_fraction)}</td>
                <td>
                  <span className="badge value">VALUE</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
