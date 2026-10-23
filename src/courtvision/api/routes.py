from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from courtvision.api.repository import SeasonMartRepository

router = APIRouter()
STATIC_DIR = Path(__file__).resolve().parents[3] / "dist"
repository = SeasonMartRepository(STATIC_DIR / "assets" / "data.js")


@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "courtvision-intelligence", "version": "0.2.0"}


@router.get("/api/v1/methodology")
def methodology() -> dict[str, object]:
    return {
        "season": "2023-24",
        "source": "Eoin Moore and Sumitro Datta public Kaggle datasets",
        "similarity": {
            "candidate_pool": "same broad position family",
            "metrics": [
                "points",
                "rebounds",
                "assists",
                "steals",
                "blocks",
                "turnovers",
                "true shooting percentage",
            ],
            "normalization": "league-position standard deviation",
            "warning": "Similarity describes statistical profile, not player quality.",
        },
    }


@router.get("/api/v1/bootstrap")
def bootstrap() -> dict[str, object]:
    """Return the dashboard-ready analytical mart in one request."""
    return repository.bootstrap()


@router.get("/api/v1/summary")
def summary() -> dict[str, object]:
    return repository.league_summary()


@router.get("/api/v1/data-quality")
def data_quality() -> dict[str, object]:
    return repository.quality_report()


@router.get("/api/v1/teams")
def teams() -> dict[str, object]:
    return {"items": repository.teams, "total": len(repository.teams)}


@router.get("/api/v1/teams/{abbreviation}")
def team_detail(abbreviation: str) -> dict[str, object]:
    team = repository.team(abbreviation)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/api/v1/players")
def players(
    search: str | None = None,
    team: str | None = None,
    position: str | None = None,
    min_games: int = Query(default=0, ge=0, le=82),
    sort: str = "totalMin",
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, object]:
    return repository.list_players(
        search=search,
        team=team,
        position=position,
        min_games=min_games,
        sort=sort,
        limit=limit,
        offset=offset,
    )


@router.get("/api/v1/players/{player_id}")
def player_detail(player_id: int) -> dict[str, object]:
    player = repository.player(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/api/v1/players/{player_id}/similar")
def player_similarity(
    player_id: int, limit: int = Query(default=5, ge=1, le=20)
) -> dict[str, object]:
    matches = repository.similarity(player_id, limit=limit)
    if matches is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return {"player_id": player_id, "items": matches, "total": len(matches)}


@router.get("/api/v1/games")
def games(
    team: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, object]:
    return repository.list_games(
        team=team, date_from=date_from, date_to=date_to, limit=limit, offset=offset
    )


@router.get("/api/v1/games/{game_id}")
def game_detail(game_id: str) -> dict[str, object]:
    game = repository.game(game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
