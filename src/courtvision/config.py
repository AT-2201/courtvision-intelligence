from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://courtvision:courtvision@localhost:5433/courtvision",
    )
    season: str = os.getenv("COURTVISION_SEASON", "2023-24")
    source_db: str = os.getenv("COURTVISION_SOURCE_DB", "data/raw/nba.sqlite")


settings = Settings()

