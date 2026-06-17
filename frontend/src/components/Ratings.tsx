import { useEffect, useState } from 'react'
import { api } from '../api'
import type { TeamRating } from '../types'

export function Ratings() {
  const [rows, setRows] = useState<TeamRating[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.ratings().then(setRows).catch((e) => setError(String(e)))
  }, [])

  if (error) return <div className="error">Failed to load ratings: {error}</div>
  if (!rows) return <div className="loading">Loading team ratings…</div>

  return (
    <div className="panel">
      <h2>Team Ratings</h2>
      <p className="sub">
        Dixon-Coles attack &amp; defence strengths (log scale), estimated by time-weighted maximum
        likelihood. Higher attack scores more goals; higher defence concedes fewer.
      </p>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Team</th>
            <th>Attack</th>
            <th>Defence</th>
            <th>Overall</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.team}>
              <td className="left muted">{r.rank}</td>
              <td className="left">{r.team}</td>
              <td>{r.attack.toFixed(3)}</td>
              <td>{r.defence.toFixed(3)}</td>
              <td>{r.overall.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
