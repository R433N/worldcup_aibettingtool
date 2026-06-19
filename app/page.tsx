import {
  betRecommendations,
  bracketSlots,
  getCompletedMatches,
  getGroupLeaderChart,
  getGroups,
  getGroupStandings,
  getThirdPlaceRace,
  getUpcomingMatches,
  knockoutRounds,
  qualificationRules,
  snapshot,
  type Match,
  type Standing,
} from "@/lib/world-cup-data";

const groupStandings = getGroupStandings();
const groups = getGroups();
const thirdPlaceRace = getThirdPlaceRace();
const upcomingMatches = getUpcomingMatches(10);
const completedMatches = getCompletedMatches(6);
const leaderChart = getGroupLeaderChart();

const completedCount = completedMatches.length;
const totalCompleted = groupStandings.reduce(
  (count, group) => count + group.standings.reduce((sum, standing) => sum + standing.played, 0),
  0,
) / 2;

export default function Home() {
  return (
    <main className="shell">
      <section className="hero">
        <div className="heroCopy">
          <p className="eyebrow">FIFA World Cup 2026 analytics</p>
          <h1>Live groups, standings, bracket paths, and bet signals in one match dashboard.</h1>
          <p className="heroText">
            A responsive command center for the expanded 48-team format, seeded with the current
            group snapshot and the official Round of 32 qualification logic.
          </p>
          <div className="heroActions">
            <a href="#standings">View standings</a>
            <a href="#knockout" className="secondary">
              Knockout bracket
            </a>
          </div>
        </div>
        <div className="heroPanel">
          <span>{snapshot.label}</span>
          <strong>{snapshot.updatedAt}</strong>
          <p>{snapshot.source}</p>
          <div className="statGrid">
            <Metric label="Groups" value="12" />
            <Metric label="Teams" value="48" />
            <Metric label="Completed group matches" value={String(totalCompleted)} />
            <Metric label="Round of 32 slots" value="32" />
          </div>
        </div>
      </section>

      <section className="section overviewGrid" aria-label="Tournament overview">
        <article className="card span2">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Qualification model</p>
              <h2>How teams reach the knockout stage</h2>
            </div>
            <span className="pill">2026 format</span>
          </div>
          <div className="ruleGrid">
            {qualificationRules.map((rule, index) => (
              <div className="rule" key={rule}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <p>{rule}</p>
              </div>
            ))}
          </div>
        </article>

        <article className="card">
          <p className="eyebrow">Draw groups</p>
          <h2>All live groups</h2>
          <div className="groupList">
            {groups.map(({ group, teams }) => (
              <div className="groupChip" key={group}>
                <strong>Group {group}</strong>
                <span>{teams.map((team) => team.shortName).join(" / ")}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="section" id="standings">
        <div className="sectionHeader">
          <div>
            <p className="eyebrow">Standings dashboard</p>
            <h2>Group tables with automatic qualification bands</h2>
          </div>
          <span className="pill">Top 2 advance + best 8 thirds</span>
        </div>
        <div className="standingsGrid">
          {groupStandings.map(({ group, standings }) => (
            <StandingsCard key={group} group={group} standings={standings} />
          ))}
        </div>
      </section>

      <section className="section split">
        <article className="card">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Chart</p>
              <h2>Group leader points pace</h2>
            </div>
            <span className="pill">Max 9 pts</span>
          </div>
          <div className="barChart">
            {leaderChart.map((leader) => (
              <div className="barRow" key={leader.group}>
                <span>Group {leader.group}</span>
                <div className="barTrack">
                  <div style={{ width: `${leader.progress}%` }} />
                </div>
                <strong>
                  {leader.team} {leader.points} pts
                </strong>
              </div>
            ))}
          </div>
        </article>

        <article className="card">
          <div className="sectionHeader">
            <div>
              <p className="eyebrow">Wild-card race</p>
              <h2>Best third-place teams</h2>
            </div>
            <span className="pill">Live projection</span>
          </div>
          <div className="thirdRace">
            {thirdPlaceRace.map((standing, index) => (
              <div className="raceRow" key={standing.team.name}>
                <span className={index < 8 ? "seed advance" : "seed danger"}>{index + 1}</span>
                <strong>{standing.team.name}</strong>
                <small>Group {standing.team.group}</small>
                <em>
                  {standing.points} pts / {formatGoalDifference(standing.goalDifference)}
                </em>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="section split" id="matches">
        <MatchPanel title="Recent results" label={`${completedCount} latest`} matches={completedMatches} />
        <MatchPanel title="Next fixtures" label="Upcoming" matches={upcomingMatches} />
      </section>

      <section className="section" id="knockout">
        <div className="sectionHeader">
          <div>
            <p className="eyebrow">Knockout stage</p>
            <h2>Round of 32 bracket slots and path overview</h2>
          </div>
          <span className="pill">Annex C-aware</span>
        </div>
        <div className="bracketLayout">
          <div className="roundList">
            {knockoutRounds.map((round) => (
              <div className="roundCard" key={round.round}>
                <span>{round.dates}</span>
                <strong>{round.round}</strong>
                <small>{round.matches} match{round.matches > 1 ? "es" : ""}</small>
              </div>
            ))}
          </div>
          <div className="bracketGrid">
            {bracketSlots.map((slot) => (
              <article className="bracketCard" key={slot.match}>
                <div>
                  <span>Match {slot.match}</span>
                  <small>
                    {slot.date} - {slot.venue}
                  </small>
                </div>
                <strong>{slot.home}</strong>
                <i>vs</i>
                <strong>{slot.away}</strong>
                {slot.note ? <p>{slot.note}</p> : null}
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section" id="bets">
        <div className="sectionHeader">
          <div>
            <p className="eyebrow">Bet recommendation screen</p>
            <h2>Model-readable picks with confidence and rationale</h2>
          </div>
          <span className="pill">For analytics workflows</span>
        </div>
        <div className="betGrid">
          {betRecommendations.map((recommendation) => (
            <article className="betCard" key={recommendation.fixture}>
              <span className={`confidence ${recommendation.confidence.toLowerCase()}`}>
                {recommendation.confidence}
              </span>
              <h3>{recommendation.fixture}</h3>
              <strong>{recommendation.market}</strong>
              <p>{recommendation.signal}</p>
              <small>{recommendation.rationale}</small>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function StandingsCard({ group, standings }: { group: string; standings: Standing[] }) {
  return (
    <article className="standingsCard">
      <div className="tableTop">
        <h3>Group {group}</h3>
        <span>{standings.reduce((total, team) => total + team.played, 0) / 2}/6 played</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Team</th>
            <th>P</th>
            <th>GD</th>
            <th>Pts</th>
            <th>Form</th>
          </tr>
        </thead>
        <tbody>
          {standings.map((standing, index) => (
            <tr key={standing.team.name}>
              <td>
                <span className={index < 2 ? "rank auto" : index === 2 ? "rank third" : "rank"}>
                  {index + 1}
                </span>
                <strong>{standing.team.name}</strong>
                <small>{standing.team.shortName}</small>
              </td>
              <td>{standing.played}</td>
              <td>{formatGoalDifference(standing.goalDifference)}</td>
              <td>
                <strong>{standing.points}</strong>
              </td>
              <td>
                <div className="form">
                  {standing.form.length ? standing.form.map((item) => <span key={item}>{item}</span>) : <em>-</em>}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </article>
  );
}

function MatchPanel({ title, label, matches }: { title: string; label: string; matches: Match[] }) {
  return (
    <article className="card">
      <div className="sectionHeader">
        <div>
          <p className="eyebrow">Match dashboard</p>
          <h2>{title}</h2>
        </div>
        <span className="pill">{label}</span>
      </div>
      <div className="matchList">
        {matches.map((match) => (
          <div className="matchCard" key={match.id}>
            <div>
              <span>Group {match.group}</span>
              <small>
                {match.date} - {match.localTime} - {match.venue}
              </small>
            </div>
            <strong>
              {match.home}
              {match.status === "completed" ? ` ${match.homeScore}` : ""}
            </strong>
            <i>vs</i>
            <strong>
              {match.status === "completed" ? `${match.awayScore} ` : ""}
              {match.away}
            </strong>
          </div>
        ))}
      </div>
    </article>
  );
}

function formatGoalDifference(value: number) {
  return value > 0 ? `+${value}` : String(value);
}
