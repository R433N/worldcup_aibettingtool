export interface TeamRating {
  rank: number
  team: string
  attack: number
  defence: number
  overall: number
}

export interface ValueBet {
  fixture_id: string
  home: string
  away: string
  kickoff: string
  market: string
  bookmaker: string
  selection: string
  decimal_odds: number
  model_probability: number
  market_probability: number
  edge: number
  expected_value: number
  kelly_fraction: number
  is_value: boolean
}

export interface ValueBetsResponse {
  count: number
  settings: {
    vig_method: string
    min_edge: number
    min_expected_value: number
    kelly_fraction: number
    kelly_cap: number
  }
  bets: ValueBet[]
}

export interface FixtureSummary {
  fixture_id: string
  home: string
  away: string
  kickoff: string
  neutral: boolean
  markets: string[]
}

export interface SelectionValue {
  market: string
  selection: string
  decimal_odds: number
  model_probability: number
  market_probability: number
  edge: number
  expected_value: number
  kelly_fraction: number
  is_value: boolean
}

export interface MarketAnalysis {
  market: string
  bookmaker: string
  overround: number
  selections: SelectionValue[]
}

export interface FixtureAnalysis {
  fixture_id: string
  home: string
  away: string
  kickoff: string
  neutral: boolean
  markets: MarketAnalysis[]
}
