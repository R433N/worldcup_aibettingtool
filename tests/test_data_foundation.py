import tempfile
import unittest
from pathlib import Path

from worldcup_aibettingtool.dashboard import build_report, write_dashboard
from worldcup_aibettingtool.data_foundation import MATCH_ID, build_data_foundation_report, seed_demo_warehouse
from worldcup_aibettingtool.ingestion import IngestionError, require_fields
from worldcup_aibettingtool.odds import OddsSnapshot, calculate_movements, implied_probability
from worldcup_aibettingtool.source_catalog import recommended_sources


class DataFoundationTest(unittest.TestCase):
    def test_source_catalog_covers_requested_data_areas(self):
        categories = {source.category for source in recommended_sources()}

        self.assertIn("fixtures_results_tables", categories)
        self.assertIn("sportsbook_odds", categories)
        self.assertIn("weather", categories)
        self.assertIn("injuries_suspensions_lineups", categories)
        self.assertIn("historical_world_cup", categories)

    def test_warehouse_seed_populates_normalized_tables(self):
        warehouse = seed_demo_warehouse()
        try:
            counts = warehouse.table_counts()

            self.assertGreaterEqual(counts["sources"], 8)
            self.assertGreaterEqual(counts["matches"], 7)
            self.assertGreaterEqual(counts["team_match_stats"], 6)
            self.assertGreaterEqual(counts["availability"], 2)
            self.assertGreaterEqual(counts["weather_snapshots"], 1)
            self.assertGreaterEqual(counts["odds_snapshots"], 8)
            self.assertEqual(counts["feature_snapshots"], 1)
        finally:
            warehouse.close()

    def test_odds_movements_use_opening_and_current_prices(self):
        snapshots = [
            OddsSnapshot(MATCH_ID, "Demo Book", "Moneyline", "Home", 2.50, "2026-07-18T12:00:00Z", True),
            OddsSnapshot(MATCH_ID, "Demo Book", "Moneyline", "Home", 2.25, "2026-07-19T12:00:00Z", False),
        ]

        movement = calculate_movements(snapshots)[0]

        self.assertEqual(implied_probability(2.50), 0.4)
        self.assertEqual(movement.opening_odds, 2.50)
        self.assertEqual(movement.current_odds, 2.25)
        self.assertGreater(movement.implied_probability_delta, 0)

    def test_feature_snapshot_contains_betting_model_inputs_not_predictions(self):
        report = build_data_foundation_report()
        features = report["feature_snapshot"]["features"]

        self.assertIn("home_xg_avg", features)
        self.assertIn("away_shots_on_target_avg", features)
        self.assertIn("referee_yellow_cards_avg", features)
        self.assertIn("temperature_c", features)
        self.assertIn("venue_altitude_m", features)
        self.assertIn("odds_move_the_odds_api_demo_moneyline_home_current", features)
        self.assertNotIn("best_pick", report)
        self.assertIn("does not recommend bets", report["no_prediction_policy"])

    def test_dashboard_writes_no_prediction_pages_and_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = write_dashboard(tmp)

            self.assertTrue((Path(output) / "index.html").exists())
            self.assertTrue((Path(output) / "data_foundation.html").exists())
            self.assertTrue((Path(output) / "data_foundation.json").exists())
            self.assertFalse((Path(output) / "predictions.html").exists())

    def test_ingestion_validation_reports_missing_fields(self):
        with self.assertRaises(IngestionError):
            require_fields({"match_id": MATCH_ID}, ("match_id", "home_team"), "fixture_feed")

    def test_build_report_keeps_live_inputs_and_foundation_together(self):
        report = build_report()

        self.assertIn("live", report)
        self.assertIn("team_stats", report)
        self.assertIn("players", report)
        self.assertIn("data_foundation", report)
        self.assertNotIn("predictions", report)


if __name__ == "__main__":
    unittest.main()
