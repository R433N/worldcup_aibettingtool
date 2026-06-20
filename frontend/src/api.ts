import type {
  FixtureAnalysis,
  FixtureSummary,
  TeamRating,
  ValueBetsResponse,
} from './types'

const BASE = '/api'

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText} for ${path}`)
  }
  return (await res.json()) as T
}

export const api = {
  ratings: () => getJson<TeamRating[]>('/teams/ratings'),
  valueBets: () => getJson<ValueBetsResponse>('/value-bets'),
  fixtures: () => getJson<FixtureSummary[]>('/fixtures'),
  fixtureAnalysis: (id: string) =>
    getJson<FixtureAnalysis>(`/fixtures/${id}/analysis`),
}
