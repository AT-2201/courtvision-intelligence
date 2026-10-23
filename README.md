# CourtVision Intelligence

CourtVision Intelligence is an end-to-end basketball analytics and scouting platform for the complete 2023/24 NBA regular season. It is designed as a data engineering and data analytics portfolio project: raw public data is validated, loaded into a PostgreSQL-ready warehouse, transformed into analytical marts, served through FastAPI, and presented in a responsive dark-themed dashboard.

**Live demo:** [at-2201.github.io/courtvision-intelligence](https://at-2201.github.io/courtvision-intelligence/)

## What the project demonstrates

### Data engineering

- Repeatable CSV ingestion for games, teams, players, team box scores, and player box scores
- Idempotent, batched PostgreSQL upserts with natural-key conflict handling
- A normalized warehouse model with teams, players, games, team-game stats, and player-game stats
- dbt staging and mart layers for reusable business logic
- Automated source audits and API data-quality checks
- CI checks for Python quality, tests, and frontend JavaScript syntax

### Data analytics

- League KPIs and standings across all 30 teams
- Team pace, offensive rating, defensive rating, net rating, and Four Factors
- Player totals, per-game output, shooting efficiency, and recent form
- Explainable player similarity based on standardized statistical profiles
- Search-driven multi-player comparison with radar charts
- Game, team, player, scouting, and comparison workflows

## Architecture

```text
Kaggle CSV snapshots
        │
        ▼
Python ingestion + source audit
        │
        ▼
PostgreSQL normalized warehouse
  teams · players · games
  team_game_stats · player_game_stats
        │
        ▼
dbt staging models
        │
        ▼
Analytical marts
  team_season_stats
  player_season_stats
  player_recent_form
        │
        ▼
FastAPI v1 endpoints
        │
        ├────────► live dashboard
        └────────► static portfolio export
```

The interface uses the API when it is running locally. The hosted portfolio build falls back to a validated, generated season mart, so the same complete dataset remains explorable without operating a public database server.

## Dataset coverage

The ingestion audit for the 2023/24 regular season currently validates:

| Entity | Rows |
| --- | ---: |
| Teams | 30 |
| Games | 1,230 |
| Team-game records | 2,460 |
| Player-game records | 26,095 |
| Unique players | 570 |

Every team has 82 game decisions, game IDs are unique, and the season date range is checked before the static mart is exported.

## Run locally

Requirements: Python 3.11+, Docker, and the source CSV files described below.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,kaggle,warehouse]'
cp .env.example .env
docker compose up -d postgres
courtvision audit-csv --season 2023-24
courtvision load-warehouse --season 2023-24
cd transformations
dbt build --profiles-dir .
cd ..
uvicorn courtvision.main:app --reload
```

Open `http://127.0.0.1:8000` for the dashboard or `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Source data setup

Download the CSV snapshots from [Historical NBA Data and Player Box Scores](https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores) and place them in `data/raw/kaggle/`:

- `Games.csv`
- `TeamStatistics.csv`
- `PlayerStatistics.csv`
- `Players.csv`

Raw data is intentionally excluded from Git. The repository contains code and generated presentation assets, not redistributed source snapshots.

Run the source audit before loading anything:

```bash
courtvision audit-csv --season 2023-24 --input-dir data/raw/kaggle
```

The warehouse loader is safe to rerun: records are upserted in configurable batches instead of being appended as duplicates.

## API foundation

| Endpoint | Purpose |
| --- | --- |
| `GET /api/v1/health` | Service health and version |
| `GET /api/v1/bootstrap` | Complete dashboard mart |
| `GET /api/v1/summary` | League-level KPIs |
| `GET /api/v1/data-quality` | Published quality checks |
| `GET /api/v1/teams` | Team profiles and standings data |
| `GET /api/v1/teams/{abbreviation}` | One team profile |
| `GET /api/v1/players` | Searchable, filterable player profiles |
| `GET /api/v1/players/{player_id}` | One player profile |
| `GET /api/v1/players/{player_id}/similar` | Explainable similarity results |
| `GET /api/v1/games` | Paginated games with team filters |
| `GET /api/v1/games/{game_id}` | One game record |

## Transformation layer

The dbt project separates source cleanup from business-facing models:

- **Staging:** typed games, player-game stats, and team-game stats
- **Team mart:** standings, pace, ratings, shooting, and Four Factors
- **Player mart:** primary team, totals, per-game production, and shooting efficiency
- **Recent-form mart:** rolling five- and ten-game player output

This structure keeps metric definitions testable and reusable by the API, dashboards, reports, and future prediction models.

## Rebuild the portfolio dataset

```bash
python scripts/build_season_export.py
```

The exporter validates 1,230 games and 82 decisions per team before replacing `dist/assets/data.js`.

## Test and quality checks

```bash
ruff check .
pytest
node --check dist/assets/app.js
```

The test suite covers metric calculations, similarity behavior, ingestion filters, batching, API filtering, error handling, full-season coverage, and data-quality status.

## Repository structure

```text
src/courtvision/
  ingestion/          CSV readers and warehouse loader
  analytics/          metrics and similarity logic
  api/                FastAPI routes and mart repository
transformations/      dbt sources, staging models, and marts
dist/                 responsive portfolio dashboard
scripts/              season export tooling
tests/                automated unit and API tests
data/raw/              ignored local source snapshots
```

## Data and branding

- Data source: Eoin Moore's Historical NBA Data and Player Box Scores, licensed CC0 1.0 on Kaggle.
- CourtVision Intelligence is an independent educational portfolio project and is not affiliated with or endorsed by the NBA.
- League and team logos are not used. Team names and abbreviations appear only as factual identifiers.
