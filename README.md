# CourtVision Intelligence

CourtVision Intelligence is a portfolio-grade basketball analytics and scouting platform built on the complete 2023/24 NBA regular season. It demonstrates a reproducible data pipeline, PostgreSQL-ready warehouse, FastAPI foundation, analytical transformations and a responsive dashboard.

## What it includes

- League overview and standings
- Game browser and game-flow foundation
- Team efficiency profiles
- Player season profiles and game-log foundation
- Explainable player similarity
- Multi-player comparison workspace
- Full 30-team, 1,230-game regular-season dataset
- Verified season profiles for 572 players
- Kaggle CSV and SQLite ingestion utilities
- PostgreSQL schema and dbt-style models
- Automated tests and public static preview

The browser dashboard ships with a compact, generated JavaScript export of the full season. Raw source files are deliberately excluded from Git.

## Architecture

```text
Public Kaggle CSV snapshots
        ↓
Python discovery + season extraction
        ↓
PostgreSQL raw tables
        ↓
dbt-style staging and marts
        ↓
FastAPI analytics endpoints
        ↓
Responsive dashboard / static portfolio export
```

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,kaggle]'
docker compose up -d postgres
cp .env.example .env
courtvision init-db
uvicorn courtvision.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Rebuild the browser dataset

Download `Games.csv`, `TeamStatistics.csv`, and `PlayerStatistics.csv` from [Eoin Moore's Historical NBA Data and Player Box Scores](https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores), plus `Player Totals.csv` from [Sumitro Datta's NBA/ABA/BAA Stats](https://www.kaggle.com/datasets/sumitrodatta/nba-aba-baa-stats). Place them in `data/raw/kaggle/`, then run:

```bash
python scripts/build_season_export.py
```

The exporter validates 1,230 games and 82 decisions per team before replacing `dist/assets/data.js`.

## Testing

```bash
pytest
ruff check .
```

## Data and branding

- Game and team source: Eoin Moore's Historical NBA Data and Player Box Scores, CC0 1.0.
- Player season totals: Sumitro Datta's NBA/ABA/BAA Stats dataset, CC0 Public Domain.
- The project is educational and non-commercial.
- CourtVision Intelligence is an independent portfolio project and is not affiliated with or endorsed by the NBA.
- League and team logos are intentionally not used. Team names and abbreviations are shown as factual identifiers.

## Repository structure

```text
src/courtvision/       Python application and analytics
transformations/       dbt-style SQL models
dist/                  static portfolio dashboard
tests/                 automated tests
scripts/               data/export utilities
data/raw/              ignored local source snapshots
```

