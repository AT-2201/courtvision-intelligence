from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from courtvision.api.routes import router

app = FastAPI(
    title="CourtVision Intelligence API",
    version="0.1.0",
    description="Basketball analytics and scouting API foundation.",
)
app.include_router(router)

static_dir = Path(__file__).resolve().parents[2] / "dist"
app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

