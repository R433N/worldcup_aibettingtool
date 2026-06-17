import tempfile
import unittest
from pathlib import Path

from worldcup_aibettingtool.dashboard import build_report, write_dashboard
from worldcup_aibettingtool.live_stats import summarize_live_match, team_summary
from worldcup_aibettingtool.odds import evaluate_odds, total_money_allocation
from worldcup_aibettingtool.predictions import build_predictions
from worldcup_aibettingtool.probability import build_probability_snapshot
from worldcup_aibettingtool.sample_data import BET365_MARKETS, FIXTURE, HISTORICAL_MATCHES, LIVE_EVENTS


class AnalyticsPipelineTest(unittest.TestCase):
    def test_live_stats_include_xg_and_pressure(self):
        live = summarize_live_match(FIXTURE, LIVE_EVENTS)

        self.assertGreater(live["teams"]["Argentina"]["xg"], 0.5)
        self.assertGreater(live["teams"]["France"]["xg"], 0.5)
        self.assertEqual(live["teams"]["Argentina"]["goals"], 1)
        self.assertEqual(live["teams"]["France"]["goals"], 1)
        self.assertEqual(live["pressure_timeline"][-1]["minute"], 90)
        self.assertIn("momentum", live["pressure_timeline"][-1])

    def test_team_summary_covers_requested_markets(self):
        summary = team_summary("Argentina", HISTORICAL_MATCHES)

        self.assertEqual(summary.team, "Argentina")
        self.assertIn(summary.recent_form[-1], {"W", "D", "L"})
        self.assertGreater(summary.goals_for_avg, 0)
        self.assertGreaterEqual(summary.over_25_goals_pct, 0)
        self.assertGreaterEqual(summary.btts_pct, 0)
        self.assertIn(summary.half_with_most_goals, {"First half", "Second half", "Even"})

    def test_probability_snapshot_sums_to_one(self):
        live = summarize_live_match(FIXTURE, LIVE_EVENTS)
        snapshot = build_probability_snapshot(
            FIXTURE,
            HISTORICAL_MATCHES,
            live["teams"]["Argentina"]["xg"],
            live["teams"]["France"]["xg"],
            84,
        )

        fulltime_total = snapshot.fulltime_home_win + snapshot.fulltime_draw + snapshot.fulltime_away_win
        halftime_total = snapshot.halftime_home_win + snapshot.halftime_draw + snapshot.halftime_away_win
        self.assertAlmostEqual(fulltime_total, 1.0, places=5)
        self.assertAlmostEqual(halftime_total, 1.0, places=5)
        self.assertAlmostEqual(
            snapshot.double_chance_home_or_draw,
            snapshot.fulltime_home_win + snapshot.fulltime_draw,
            places=5,
        )
        self.assertEqual(len(snapshot.top_scorelines), 5)

    def test_odds_value_and_predictions(self):
        report = build_report()
        values = evaluate_odds(BET365_MARKETS, build_probability_snapshot(FIXTURE, HISTORICAL_MATCHES))
        predictions = build_predictions(values)

        self.assertTrue(any(value.sportsbook == "Bet365" for value in values))
        self.assertGreaterEqual(total_money_allocation(values), 0)
        self.assertIsNotNone(predictions["best_pick"])
        self.assertGreaterEqual(predictions["best_parlay"]["combined_odds"], 1.70)
        self.assertIn("odds_values", report)

    def test_dashboard_writes_pages_and_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = write_dashboard(tmp)

            self.assertTrue((Path(output) / "index.html").exists())
            self.assertTrue((Path(output) / "predictions.html").exists())
            self.assertTrue((Path(output) / "data.json").exists())


if __name__ == "__main__":
    unittest.main()
