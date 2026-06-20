import { useState } from 'react'
import { ValueBets } from './components/ValueBets'
import { Ratings } from './components/Ratings'
import { Fixtures } from './components/Fixtures'

type Tab = 'value' | 'fixtures' | 'ratings'

const TABS: { id: Tab; label: string }[] = [
  { id: 'value', label: 'Value Bets' },
  { id: 'fixtures', label: 'Fixtures' },
  { id: 'ratings', label: 'Team Ratings' },
]

export default function App() {
  const [tab, setTab] = useState<Tab>('value')

  return (
    <div className="app">
      <header className="hero">
        <h1>⚽ World Cup Betting Analytics</h1>
        <p>
          Dixon-Coles match modelling · vig-free fair prices · expected value &amp; fractional
          Kelly staking
        </p>
        <p className="disclaimer">
          Demo uses synthetic sample data. Markets are highly efficient — no model guarantees
          profit. For analytics/education only. Bet responsibly.
        </p>
      </header>

      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={tab === t.id ? 'active' : ''}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === 'value' && <ValueBets />}
      {tab === 'fixtures' && <Fixtures />}
      {tab === 'ratings' && <Ratings />}
    </div>
  )
}
