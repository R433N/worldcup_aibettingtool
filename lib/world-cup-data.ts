export type GroupKey =
  | "A"
  | "B"
  | "C"
  | "D"
  | "E"
  | "F"
  | "G"
  | "H"
  | "I"
  | "J"
  | "K"
  | "L";

export type Team = {
  name: string;
  shortName: string;
  group: GroupKey;
  confederation: string;
  rating: number;
};

export type Match = {
  id: number;
  group: GroupKey;
  date: string;
  localTime: string;
  venue: string;
  home: string;
  away: string;
  status: "completed" | "scheduled";
  homeScore?: number;
  awayScore?: number;
};

export type Standing = {
  team: Team;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goalsFor: number;
  goalsAgainst: number;
  goalDifference: number;
  points: number;
  form: string[];
};

export type BracketSlot = {
  match: number;
  date: string;
  venue: string;
  home: string;
  away: string;
  note?: string;
};

export type BetRecommendation = {
  fixture: string;
  market: string;
  confidence: "High" | "Medium" | "Speculative";
  signal: string;
  rationale: string;
};

export const snapshot = {
  label: "Live snapshot",
  updatedAt: "June 17, 2026, 06:25 UTC",
  source:
    "Seeded from public FIFA draw information and ESPN fixtures/results available at the snapshot time.",
};

export const qualificationRules = [
  "48 teams play in 12 groups of four.",
  "Teams play three group matches; wins are worth three points and draws one point.",
  "The top two teams in every group qualify automatically for the Round of 32.",
  "The eight best third-place teams across all groups also qualify.",
  "Third-place ranking order: points, goal difference, goals scored, team conduct score, then FIFA ranking.",
  "Round of 32 pairings involving third-place teams use FIFA's Annex C matrix of 495 combinations after all group matches finish.",
  "Knockout matches use extra time and penalties if level after 90 minutes.",
];

export const teams: Team[] = [
  { group: "A", name: "Mexico", shortName: "MEX", confederation: "CONCACAF", rating: 84 },
  { group: "A", name: "South Africa", shortName: "RSA", confederation: "CAF", rating: 72 },
  { group: "A", name: "South Korea", shortName: "KOR", confederation: "AFC", rating: 80 },
  { group: "A", name: "Czechia", shortName: "CZE", confederation: "UEFA", rating: 77 },
  { group: "B", name: "Canada", shortName: "CAN", confederation: "CONCACAF", rating: 76 },
  { group: "B", name: "Bosnia and Herzegovina", shortName: "BIH", confederation: "UEFA", rating: 74 },
  { group: "B", name: "Qatar", shortName: "QAT", confederation: "AFC", rating: 71 },
  { group: "B", name: "Switzerland", shortName: "SUI", confederation: "UEFA", rating: 82 },
  { group: "C", name: "Brazil", shortName: "BRA", confederation: "CONMEBOL", rating: 92 },
  { group: "C", name: "Morocco", shortName: "MAR", confederation: "CAF", rating: 84 },
  { group: "C", name: "Haiti", shortName: "HAI", confederation: "CONCACAF", rating: 66 },
  { group: "C", name: "Scotland", shortName: "SCO", confederation: "UEFA", rating: 78 },
  { group: "D", name: "United States", shortName: "USA", confederation: "CONCACAF", rating: 83 },
  { group: "D", name: "Paraguay", shortName: "PAR", confederation: "CONMEBOL", rating: 76 },
  { group: "D", name: "Australia", shortName: "AUS", confederation: "AFC", rating: 77 },
  { group: "D", name: "Turkiye", shortName: "TUR", confederation: "UEFA", rating: 79 },
  { group: "E", name: "Germany", shortName: "GER", confederation: "UEFA", rating: 89 },
  { group: "E", name: "Curacao", shortName: "CUW", confederation: "CONCACAF", rating: 62 },
  { group: "E", name: "Cote d'Ivoire", shortName: "CIV", confederation: "CAF", rating: 80 },
  { group: "E", name: "Ecuador", shortName: "ECU", confederation: "CONMEBOL", rating: 81 },
  { group: "F", name: "Netherlands", shortName: "NED", confederation: "UEFA", rating: 88 },
  { group: "F", name: "Japan", shortName: "JPN", confederation: "AFC", rating: 82 },
  { group: "F", name: "Sweden", shortName: "SWE", confederation: "UEFA", rating: 79 },
  { group: "F", name: "Tunisia", shortName: "TUN", confederation: "CAF", rating: 72 },
  { group: "G", name: "Belgium", shortName: "BEL", confederation: "UEFA", rating: 86 },
  { group: "G", name: "Egypt", shortName: "EGY", confederation: "CAF", rating: 80 },
  { group: "G", name: "Iran", shortName: "IRN", confederation: "AFC", rating: 76 },
  { group: "G", name: "New Zealand", shortName: "NZL", confederation: "OFC", rating: 65 },
  { group: "H", name: "Spain", shortName: "ESP", confederation: "UEFA", rating: 90 },
  { group: "H", name: "Cabo Verde", shortName: "CPV", confederation: "CAF", rating: 70 },
  { group: "H", name: "Saudi Arabia", shortName: "KSA", confederation: "AFC", rating: 71 },
  { group: "H", name: "Uruguay", shortName: "URU", confederation: "CONMEBOL", rating: 86 },
  { group: "I", name: "France", shortName: "FRA", confederation: "UEFA", rating: 93 },
  { group: "I", name: "Senegal", shortName: "SEN", confederation: "CAF", rating: 82 },
  { group: "I", name: "Iraq", shortName: "IRQ", confederation: "AFC", rating: 68 },
  { group: "I", name: "Norway", shortName: "NOR", confederation: "UEFA", rating: 84 },
  { group: "J", name: "Argentina", shortName: "ARG", confederation: "CONMEBOL", rating: 94 },
  { group: "J", name: "Algeria", shortName: "ALG", confederation: "CAF", rating: 77 },
  { group: "J", name: "Austria", shortName: "AUT", confederation: "UEFA", rating: 81 },
  { group: "J", name: "Jordan", shortName: "JOR", confederation: "AFC", rating: 69 },
  { group: "K", name: "Portugal", shortName: "POR", confederation: "UEFA", rating: 91 },
  { group: "K", name: "DR Congo", shortName: "COD", confederation: "CAF", rating: 73 },
  { group: "K", name: "Uzbekistan", shortName: "UZB", confederation: "AFC", rating: 72 },
  { group: "K", name: "Colombia", shortName: "COL", confederation: "CONMEBOL", rating: 85 },
  { group: "L", name: "England", shortName: "ENG", confederation: "UEFA", rating: 91 },
  { group: "L", name: "Croatia", shortName: "CRO", confederation: "UEFA", rating: 84 },
  { group: "L", name: "Ghana", shortName: "GHA", confederation: "CAF", rating: 75 },
  { group: "L", name: "Panama", shortName: "PAN", confederation: "CONCACAF", rating: 70 },
];

export const matches: Match[] = [
  { id: 1, group: "A", date: "Jun 11", localTime: "Completed", venue: "Mexico City", home: "Mexico", away: "South Africa", status: "completed", homeScore: 2, awayScore: 0 },
  { id: 2, group: "A", date: "Jun 11", localTime: "Completed", venue: "Zapopan", home: "South Korea", away: "Czechia", status: "completed", homeScore: 2, awayScore: 1 },
  { id: 3, group: "B", date: "Jun 12", localTime: "Completed", venue: "Toronto", home: "Canada", away: "Bosnia and Herzegovina", status: "completed", homeScore: 1, awayScore: 1 },
  { id: 4, group: "D", date: "Jun 12", localTime: "Completed", venue: "Inglewood", home: "United States", away: "Paraguay", status: "completed", homeScore: 4, awayScore: 1 },
  { id: 5, group: "B", date: "Jun 13", localTime: "Completed", venue: "Santa Clara", home: "Qatar", away: "Switzerland", status: "completed", homeScore: 1, awayScore: 1 },
  { id: 6, group: "C", date: "Jun 13", localTime: "Completed", venue: "East Rutherford", home: "Brazil", away: "Morocco", status: "completed", homeScore: 1, awayScore: 1 },
  { id: 7, group: "C", date: "Jun 13", localTime: "Completed", venue: "Foxborough", home: "Haiti", away: "Scotland", status: "completed", homeScore: 0, awayScore: 1 },
  { id: 8, group: "D", date: "Jun 13", localTime: "Completed", venue: "Vancouver", home: "Australia", away: "Turkiye", status: "completed", homeScore: 2, awayScore: 0 },
  { id: 9, group: "E", date: "Jun 14", localTime: "Completed", venue: "Houston", home: "Germany", away: "Curacao", status: "completed", homeScore: 7, awayScore: 1 },
  { id: 10, group: "F", date: "Jun 14", localTime: "Completed", venue: "Arlington", home: "Netherlands", away: "Japan", status: "completed", homeScore: 2, awayScore: 2 },
  { id: 11, group: "E", date: "Jun 14", localTime: "Completed", venue: "Philadelphia", home: "Cote d'Ivoire", away: "Ecuador", status: "completed", homeScore: 1, awayScore: 0 },
  { id: 12, group: "F", date: "Jun 14", localTime: "Completed", venue: "Guadalupe", home: "Sweden", away: "Tunisia", status: "completed", homeScore: 5, awayScore: 1 },
  { id: 13, group: "H", date: "Jun 15", localTime: "Completed", venue: "Atlanta", home: "Spain", away: "Cabo Verde", status: "completed", homeScore: 0, awayScore: 0 },
  { id: 14, group: "G", date: "Jun 15", localTime: "Completed", venue: "Seattle", home: "Belgium", away: "Egypt", status: "completed", homeScore: 1, awayScore: 1 },
  { id: 15, group: "H", date: "Jun 15", localTime: "Completed", venue: "Miami Gardens", home: "Saudi Arabia", away: "Uruguay", status: "completed", homeScore: 1, awayScore: 1 },
  { id: 16, group: "G", date: "Jun 15", localTime: "Completed", venue: "Inglewood", home: "Iran", away: "New Zealand", status: "completed", homeScore: 2, awayScore: 2 },
  { id: 17, group: "I", date: "Jun 16", localTime: "Completed", venue: "East Rutherford", home: "France", away: "Senegal", status: "completed", homeScore: 3, awayScore: 1 },
  { id: 18, group: "I", date: "Jun 16", localTime: "Completed", venue: "Foxborough", home: "Iraq", away: "Norway", status: "completed", homeScore: 1, awayScore: 4 },
  { id: 19, group: "J", date: "Jun 16", localTime: "Completed", venue: "Kansas City", home: "Argentina", away: "Algeria", status: "completed", homeScore: 3, awayScore: 0 },
  { id: 20, group: "J", date: "Jun 16", localTime: "Completed", venue: "Santa Clara", home: "Austria", away: "Jordan", status: "completed", homeScore: 3, awayScore: 1 },
  { id: 21, group: "K", date: "Jun 17", localTime: "1:00 PM ET", venue: "Houston", home: "Portugal", away: "DR Congo", status: "scheduled" },
  { id: 22, group: "L", date: "Jun 17", localTime: "4:00 PM ET", venue: "Arlington", home: "England", away: "Croatia", status: "scheduled" },
  { id: 23, group: "L", date: "Jun 17", localTime: "7:00 PM ET", venue: "Toronto", home: "Ghana", away: "Panama", status: "scheduled" },
  { id: 24, group: "K", date: "Jun 17", localTime: "10:00 PM ET", venue: "Mexico City", home: "Uzbekistan", away: "Colombia", status: "scheduled" },
  { id: 25, group: "A", date: "Jun 18", localTime: "12:00 PM ET", venue: "Atlanta", home: "Czechia", away: "South Africa", status: "scheduled" },
  { id: 26, group: "B", date: "Jun 18", localTime: "3:00 PM ET", venue: "Inglewood", home: "Switzerland", away: "Bosnia and Herzegovina", status: "scheduled" },
  { id: 27, group: "B", date: "Jun 18", localTime: "6:00 PM ET", venue: "Vancouver", home: "Canada", away: "Qatar", status: "scheduled" },
  { id: 28, group: "A", date: "Jun 18", localTime: "11:00 PM ET", venue: "Zapopan", home: "Mexico", away: "South Korea", status: "scheduled" },
  { id: 29, group: "D", date: "Jun 19", localTime: "3:00 PM ET", venue: "Seattle", home: "United States", away: "Australia", status: "scheduled" },
  { id: 30, group: "C", date: "Jun 19", localTime: "6:00 PM ET", venue: "Foxborough", home: "Scotland", away: "Morocco", status: "scheduled" },
  { id: 31, group: "C", date: "Jun 19", localTime: "9:00 PM ET", venue: "Philadelphia", home: "Brazil", away: "Haiti", status: "scheduled" },
  { id: 32, group: "D", date: "Jun 19", localTime: "12:00 AM ET", venue: "Santa Clara", home: "Turkiye", away: "Paraguay", status: "scheduled" },
  { id: 33, group: "F", date: "Jun 20", localTime: "1:00 PM ET", venue: "Houston", home: "Netherlands", away: "Sweden", status: "scheduled" },
  { id: 34, group: "E", date: "Jun 20", localTime: "4:00 PM ET", venue: "Toronto", home: "Germany", away: "Cote d'Ivoire", status: "scheduled" },
  { id: 35, group: "E", date: "Jun 20", localTime: "8:00 PM ET", venue: "Kansas City", home: "Ecuador", away: "Curacao", status: "scheduled" },
  { id: 36, group: "F", date: "Jun 20", localTime: "12:00 AM ET", venue: "Guadalupe", home: "Tunisia", away: "Japan", status: "scheduled" },
  { id: 37, group: "H", date: "Jun 21", localTime: "12:00 PM ET", venue: "Atlanta", home: "Spain", away: "Saudi Arabia", status: "scheduled" },
  { id: 38, group: "G", date: "Jun 21", localTime: "3:00 PM ET", venue: "Inglewood", home: "Belgium", away: "Iran", status: "scheduled" },
  { id: 39, group: "H", date: "Jun 21", localTime: "6:00 PM ET", venue: "Miami Gardens", home: "Uruguay", away: "Cabo Verde", status: "scheduled" },
  { id: 40, group: "G", date: "Jun 21", localTime: "9:00 PM ET", venue: "Vancouver", home: "New Zealand", away: "Egypt", status: "scheduled" },
  { id: 41, group: "J", date: "Jun 22", localTime: "1:00 PM ET", venue: "Arlington", home: "Argentina", away: "Austria", status: "scheduled" },
  { id: 42, group: "I", date: "Jun 22", localTime: "5:00 PM ET", venue: "Philadelphia", home: "France", away: "Iraq", status: "scheduled" },
  { id: 43, group: "I", date: "Jun 22", localTime: "8:00 PM ET", venue: "East Rutherford", home: "Norway", away: "Senegal", status: "scheduled" },
  { id: 44, group: "J", date: "Jun 22", localTime: "11:00 PM ET", venue: "Santa Clara", home: "Jordan", away: "Algeria", status: "scheduled" },
  { id: 45, group: "K", date: "Jun 23", localTime: "1:00 PM ET", venue: "Houston", home: "Portugal", away: "Uzbekistan", status: "scheduled" },
  { id: 46, group: "L", date: "Jun 23", localTime: "4:00 PM ET", venue: "Foxborough", home: "England", away: "Ghana", status: "scheduled" },
  { id: 47, group: "L", date: "Jun 23", localTime: "7:00 PM ET", venue: "Toronto", home: "Panama", away: "Croatia", status: "scheduled" },
  { id: 48, group: "K", date: "Jun 23", localTime: "10:00 PM ET", venue: "Zapopan", home: "Colombia", away: "DR Congo", status: "scheduled" },
  { id: 49, group: "B", date: "Jun 24", localTime: "3:00 PM ET", venue: "Vancouver", home: "Switzerland", away: "Canada", status: "scheduled" },
  { id: 50, group: "B", date: "Jun 24", localTime: "3:00 PM ET", venue: "Seattle", home: "Bosnia and Herzegovina", away: "Qatar", status: "scheduled" },
  { id: 51, group: "C", date: "Jun 24", localTime: "6:00 PM ET", venue: "Miami Gardens", home: "Scotland", away: "Brazil", status: "scheduled" },
  { id: 52, group: "C", date: "Jun 24", localTime: "6:00 PM ET", venue: "Atlanta", home: "Morocco", away: "Haiti", status: "scheduled" },
  { id: 53, group: "A", date: "Jun 24", localTime: "9:00 PM ET", venue: "Mexico City", home: "Czechia", away: "Mexico", status: "scheduled" },
  { id: 54, group: "A", date: "Jun 24", localTime: "9:00 PM ET", venue: "Guadalupe", home: "South Africa", away: "South Korea", status: "scheduled" },
  { id: 55, group: "E", date: "Jun 25", localTime: "4:00 PM ET", venue: "East Rutherford", home: "Ecuador", away: "Germany", status: "scheduled" },
  { id: 56, group: "E", date: "Jun 25", localTime: "4:00 PM ET", venue: "Philadelphia", home: "Curacao", away: "Cote d'Ivoire", status: "scheduled" },
  { id: 57, group: "F", date: "Jun 25", localTime: "7:00 PM ET", venue: "Arlington", home: "Japan", away: "Sweden", status: "scheduled" },
  { id: 58, group: "F", date: "Jun 25", localTime: "7:00 PM ET", venue: "Kansas City", home: "Tunisia", away: "Netherlands", status: "scheduled" },
  { id: 59, group: "D", date: "Jun 25", localTime: "10:00 PM ET", venue: "Inglewood", home: "Turkiye", away: "United States", status: "scheduled" },
  { id: 60, group: "D", date: "Jun 25", localTime: "10:00 PM ET", venue: "Santa Clara", home: "Paraguay", away: "Australia", status: "scheduled" },
  { id: 61, group: "I", date: "Jun 26", localTime: "3:00 PM ET", venue: "Foxborough", home: "Norway", away: "France", status: "scheduled" },
  { id: 62, group: "I", date: "Jun 26", localTime: "3:00 PM ET", venue: "Toronto", home: "Senegal", away: "Iraq", status: "scheduled" },
  { id: 63, group: "H", date: "Jun 26", localTime: "8:00 PM ET", venue: "Houston", home: "Cabo Verde", away: "Saudi Arabia", status: "scheduled" },
  { id: 64, group: "H", date: "Jun 26", localTime: "8:00 PM ET", venue: "Zapopan", home: "Uruguay", away: "Spain", status: "scheduled" },
  { id: 65, group: "G", date: "Jun 26", localTime: "11:00 PM ET", venue: "Seattle", home: "Egypt", away: "Iran", status: "scheduled" },
  { id: 66, group: "G", date: "Jun 26", localTime: "11:00 PM ET", venue: "Vancouver", home: "New Zealand", away: "Belgium", status: "scheduled" },
  { id: 67, group: "L", date: "Jun 27", localTime: "5:00 PM ET", venue: "East Rutherford", home: "Panama", away: "England", status: "scheduled" },
  { id: 68, group: "L", date: "Jun 27", localTime: "5:00 PM ET", venue: "Philadelphia", home: "Croatia", away: "Ghana", status: "scheduled" },
  { id: 69, group: "K", date: "Jun 27", localTime: "7:30 PM ET", venue: "Miami Gardens", home: "Colombia", away: "Portugal", status: "scheduled" },
  { id: 70, group: "K", date: "Jun 27", localTime: "7:30 PM ET", venue: "Atlanta", home: "DR Congo", away: "Uzbekistan", status: "scheduled" },
  { id: 71, group: "J", date: "Jun 27", localTime: "10:00 PM ET", venue: "Kansas City", home: "Algeria", away: "Austria", status: "scheduled" },
  { id: 72, group: "J", date: "Jun 27", localTime: "10:00 PM ET", venue: "Arlington", home: "Jordan", away: "Argentina", status: "scheduled" },
];

export const bracketSlots: BracketSlot[] = [
  { match: 73, date: "Jun 28", venue: "Inglewood", home: "Runner-up Group A", away: "Runner-up Group B" },
  { match: 74, date: "Jun 29", venue: "Foxborough", home: "Winner Group E", away: "Best 3rd A/B/C/D/F", note: "Annex C matrix decides the exact group." },
  { match: 75, date: "Jun 29", venue: "Guadalupe", home: "Winner Group F", away: "Runner-up Group C" },
  { match: 76, date: "Jun 29", venue: "Houston", home: "Winner Group C", away: "Runner-up Group F" },
  { match: 77, date: "Jun 30", venue: "East Rutherford", home: "Winner Group I", away: "Best 3rd C/D/F/G/H", note: "Annex C matrix decides the exact group." },
  { match: 78, date: "Jun 30", venue: "Arlington", home: "Runner-up Group E", away: "Runner-up Group I" },
  { match: 79, date: "Jun 30", venue: "Mexico City", home: "Winner Group A", away: "Best 3rd C/E/F/H/I", note: "Annex C matrix decides the exact group." },
  { match: 80, date: "Jul 1", venue: "Atlanta", home: "Winner Group L", away: "Best 3rd E/H/I/J/K", note: "Annex C matrix decides the exact group." },
  { match: 81, date: "Jul 1", venue: "Santa Clara", home: "Winner Group D", away: "Best 3rd B/E/F/I/J", note: "Annex C matrix decides the exact group." },
  { match: 82, date: "Jul 1", venue: "Seattle", home: "Winner Group G", away: "Best 3rd A/E/H/I/J", note: "Annex C matrix decides the exact group." },
  { match: 83, date: "Jul 2", venue: "Toronto", home: "Runner-up Group K", away: "Runner-up Group L" },
  { match: 84, date: "Jul 2", venue: "Inglewood", home: "Winner Group H", away: "Runner-up Group J" },
  { match: 85, date: "Jul 2", venue: "Vancouver", home: "Winner Group B", away: "Best 3rd E/F/G/I/J", note: "Annex C matrix decides the exact group." },
  { match: 86, date: "Jul 3", venue: "Miami Gardens", home: "Winner Group J", away: "Runner-up Group H" },
  { match: 87, date: "Jul 3", venue: "Kansas City", home: "Winner Group K", away: "Best 3rd D/E/I/J/L", note: "Annex C matrix decides the exact group." },
  { match: 88, date: "Jul 3", venue: "Arlington", home: "Runner-up Group D", away: "Runner-up Group G" },
];

export const knockoutRounds = [
  { round: "Round of 32", dates: "Jun 28-Jul 3", matches: 16 },
  { round: "Round of 16", dates: "Jul 4-Jul 7", matches: 8 },
  { round: "Quarterfinals", dates: "Jul 9-Jul 11", matches: 4 },
  { round: "Semifinals", dates: "Jul 14-Jul 15", matches: 2 },
  { round: "Third place", dates: "Jul 18", matches: 1 },
  { round: "Final", dates: "Jul 19", matches: 1 },
];

export const betRecommendations: BetRecommendation[] = [
  {
    fixture: "Mexico vs South Korea",
    market: "Both teams to score or over 1.5 goals",
    confidence: "Medium",
    signal: "Both opened with wins and South Korea already created two goals against Czechia.",
    rationale: "Mexico have host advantage and a clean sheet, but the pace matchup points to transition chances at both ends.",
  },
  {
    fixture: "Germany vs Cote d'Ivoire",
    market: "Germany draw no bet",
    confidence: "High",
    signal: "Germany lead the tournament with +6 goal difference after one match.",
    rationale: "Cote d'Ivoire also won, so the safer recommendation protects against a lower-tempo draw.",
  },
  {
    fixture: "France vs Iraq",
    market: "France team total over 1.5",
    confidence: "High",
    signal: "France scored three against Senegal while Iraq allowed four against Norway.",
    rationale: "The matchup favors France's shot volume and reduces reliance on a full-match handicap.",
  },
  {
    fixture: "England vs Croatia",
    market: "Under 3.5 goals",
    confidence: "Medium",
    signal: "Both teams enter their opener with high ratings and conservative knockout-level incentives.",
    rationale: "This is a pre-match model lean because Group L has not started in the live snapshot.",
  },
  {
    fixture: "Argentina vs Austria",
    market: "Argentina to qualify from Group J",
    confidence: "High",
    signal: "Argentina opened +3 and Austria opened +2, making the head-to-head a group-control match.",
    rationale: "Argentina's rating plus early goal difference gives them multiple paths even if Matchday 2 is tight.",
  },
];

const groupOrder: GroupKey[] = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"];

const teamByName = new Map(teams.map((team) => [team.name, team]));

export function getGroups() {
  return groupOrder.map((group) => ({
    group,
    teams: teams.filter((team) => team.group === group),
  }));
}

export function getGroupStandings(): Array<{ group: GroupKey; standings: Standing[] }> {
  return groupOrder.map((group) => ({
    group,
    standings: calculateStandings(group),
  }));
}

export function getThirdPlaceRace(): Standing[] {
  return getGroupStandings()
    .map(({ standings }) => standings[2])
    .sort(compareStandings)
    .map((standing, index) => ({
      ...standing,
      form: index < 8 ? [...standing.form, "ADV"] : [...standing.form, "OUT"],
    }));
}

export function getUpcomingMatches(limit = 8) {
  return matches.filter((match) => match.status === "scheduled").slice(0, limit);
}

export function getCompletedMatches(limit = 8) {
  return matches
    .filter((match) => match.status === "completed")
    .slice(-limit)
    .reverse();
}

function calculateStandings(group: GroupKey): Standing[] {
  const standings = teams
    .filter((team) => team.group === group)
    .map<Standing>((team) => ({
      team,
      played: 0,
      won: 0,
      drawn: 0,
      lost: 0,
      goalsFor: 0,
      goalsAgainst: 0,
      goalDifference: 0,
      points: 0,
      form: [],
    }));
  const byTeam = new Map(standings.map((standing) => [standing.team.name, standing]));

  matches
    .filter((match) => match.group === group && match.status === "completed")
    .forEach((match) => {
      const home = byTeam.get(match.home);
      const away = byTeam.get(match.away);

      if (!home || !away || match.homeScore === undefined || match.awayScore === undefined) {
        return;
      }

      applyResult(home, match.homeScore, match.awayScore);
      applyResult(away, match.awayScore, match.homeScore);
    });

  return standings.sort(compareStandings);
}

function applyResult(standing: Standing, goalsFor: number, goalsAgainst: number) {
  standing.played += 1;
  standing.goalsFor += goalsFor;
  standing.goalsAgainst += goalsAgainst;
  standing.goalDifference = standing.goalsFor - standing.goalsAgainst;

  if (goalsFor > goalsAgainst) {
    standing.won += 1;
    standing.points += 3;
    standing.form.push("W");
  } else if (goalsFor < goalsAgainst) {
    standing.lost += 1;
    standing.form.push("L");
  } else {
    standing.drawn += 1;
    standing.points += 1;
    standing.form.push("D");
  }
}

function compareStandings(a: Standing, b: Standing) {
  return (
    b.points - a.points ||
    b.goalDifference - a.goalDifference ||
    b.goalsFor - a.goalsFor ||
    b.team.rating - a.team.rating ||
    a.team.name.localeCompare(b.team.name)
  );
}

export function getGroupLeaderChart() {
  return getGroupStandings().map(({ group, standings }) => {
    const leader = standings[0];
    return {
      group,
      team: leader.team.shortName,
      name: leader.team.name,
      points: leader.points,
      goalDifference: leader.goalDifference,
      progress: Math.max(8, (leader.points / 9) * 100),
    };
  });
}

export function getTeam(name: string) {
  return teamByName.get(name);
}
