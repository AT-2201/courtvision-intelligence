from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()
STATIC_DIR = Path(__file__).resolve().parents[3] / "dist"


@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "courtvision-intelligence", "version": "0.1.0"}


@router.get("/api/v1/methodology")
def methodology() -> dict[str, object]:
    return {
        "season": "2023-24",
        "source": "Kaggle NBA Database",
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


@router.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")

