# CourtVision Intelligence

CourtVision Intelligence is a portfolio-grade basketball analytics and scouting platform. Version 1 focuses on a complete historical season and demonstrates a reproducible data pipeline, PostgreSQL-ready warehouse, FastAPI foundation, analytical transformations and a responsive dashboard.

## Version 1

- League overview and standings
- Game browser and game-flow foundation
- Team efficiency profiles
- Player season profiles and game-log foundation
- Explainable player similarity
- Multi-player comparison workspace
- Kaggle SQLite ingestion adapter
- PostgreSQL schema and dbt-style models
- Automated tests and public static preview

The bundled browser preview contains a small, clearly labelled 2023/24 sample so the portfolio remains fast. The ingestion pipeline is designed for the full [Kaggle NBA Database](https://www.kaggle.com/datasets/wyattowalsh/basketball), which is published under CC BY-SA 4.0.

## Architecture

```text
Kaggle SQLite snapshot
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

## Load the Kaggle source

The complete source is several gigabytes and is deliberately excluded from Git. Download it manually from Kaggle, place its SQLite file at `data/raw/nba.sqlite`, then run:

```bash
courtvision inspect-source
courtvision ingest --season 2023-24
```

The inspector reports available tables and columns before ingestion. This protects the project against changes in upstream Kaggle releases.

## Testing

```bash
pytest
ruff check .
```

## Data and branding

- Data source: Wyatt Walsh's Kaggle NBA Database, CC BY-SA 4.0.
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
data/sample/           small attributed demo dataset
```

