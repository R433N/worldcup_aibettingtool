"""API smoke + behaviour tests against the bundled sample data."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture(scope="module")
def client():
    return TestClient(create_app())


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_team_ratings_ranked(client):
    r = client.get("/teams/ratings")
    assert r.status_code == 200
    ratings = r.json()
    assert len(ratings) == 24
    overalls = [row["overall"] for row in ratings]
    assert overalls == sorted(overalls, reverse=True)  # ranked best-first
    # Brazil is the strongest team in the ground-truth sample data.
    assert ratings[0]["team"] == "Brazil"


def test_predict_probabilities_sum_to_one(client):
    r = client.get("/predict", params={"home": "Brazil", "away": "Australia"})
    assert r.status_code == 200
    body = r.json()
    one_x_two = body["markets"]["1X2"]
    assert sum(one_x_two.values()) == pytest.approx(1.0, abs=1e-6)
    assert one_x_two["HOME"] > one_x_two["AWAY"]  # Brazil strongly favoured


def test_predict_unknown_team_404(client):
    r = client.get("/predict", params={"home": "Atlantis", "away": "Brazil"})
    assert r.status_code == 404


def test_fixtures_listed(client):
    r = client.get("/fixtures")
    assert r.status_code == 200
    assert len(r.json()) == 8


def test_fixture_analysis_structure(client):
    r = client.get("/fixtures/WC2026-01/analysis")
    assert r.status_code == 200
    body = r.json()
    assert body["fixture_id"] == "WC2026-01"
    assert len(body["markets"]) >= 1
    sel = body["markets"][0]["selections"][0]
    expected_keys = (
        "model_probability",
        "market_probability",
        "edge",
        "expected_value",
        "kelly_fraction",
        "is_value",
    )
    for key in expected_keys:
        assert key in sel


def test_value_bets_present_and_sorted(client):
    r = client.get("/value-bets")
    assert r.status_code == 200
    body = r.json()
    assert body["count"] >= 1  # sample odds are seeded to contain value
    evs = [b["expected_value"] for b in body["bets"]]
    assert evs == sorted(evs, reverse=True)
    for b in body["bets"]:
        assert b["expected_value"] >= body["settings"]["min_expected_value"]
        assert b["edge"] >= body["settings"]["min_edge"]
