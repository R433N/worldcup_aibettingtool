export const pct = (x: number): string => `${(x * 100).toFixed(1)}%`

export const signedPct = (x: number): string =>
  `${x >= 0 ? '+' : ''}${(x * 100).toFixed(1)}%`

export const odds = (x: number): string => x.toFixed(2)

export const kickoff = (iso: string): string =>
  new Date(iso).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

export const SELECTION_LABEL: Record<string, string> = {
  HOME: 'Home',
  DRAW: 'Draw',
  AWAY: 'Away',
  OVER: 'Over 2.5',
  UNDER: 'Under 2.5',
  YES: 'BTTS Yes',
  NO: 'BTTS No',
}

export const label = (sel: string): string => SELECTION_LABEL[sel] ?? sel
