from fastapi.testclient import TestClient

from courtvision.main import app


def test_health() -> None:
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json()["service"] == "courtvision-intelligence"


def test_bootstrap_exposes_complete_season() -> None:
    response = TestClient(app).get("/api/v1/bootstrap")

    assert response.status_code == 200
    assert response.json()["meta"]["gameCount"] == 1230


def test_players_support_search_filter_sort_and_pagination() -> None:
    response = TestClient(app).get(
        "/api/v1/players",
        params={"search": "doncic", "team": "DAL", "min_games": 50, "sort": "pts"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["name"] == "Luka Dončić"


def test_similarity_endpoint_is_explainable() -> None:
    player = TestClient(app).get("/api/v1/players", params={"search": "Luka"}).json()["items"][0]
    response = TestClient(app).get(f"/api/v1/players/{player['id']}/similar")

    assert response.status_code == 200
    assert len(response.json()["items"]) == 5
    assert response.json()["items"][0]["closest_traits"]


def test_player_game_log_endpoint_returns_recent_box_scores() -> None:
    player = TestClient(app).get("/api/v1/players", params={"search": "Luka"}).json()["items"][0]
    response = TestClient(app).get(f"/api/v1/players/{player['id']}/games", params={"limit": 5})

    assert response.status_code == 200
    assert response.json()["total"] == player["games"]
    assert len(response.json()["items"]) == 5
    assert response.json()["items"][0]["date"] >= response.json()["items"][-1]["date"]


def test_data_quality_report_passes_release_gates() -> None:
    response = TestClient(app).get("/api/v1/data-quality")

    assert response.status_code == 200
    assert response.json()["status"] == "passed"
    assert all(check["passed"] for check in response.json()["checks"])


def test_unknown_resource_returns_404() -> None:
    response = TestClient(app).get("/api/v1/teams/XYZ")

    assert response.status_code == 404
