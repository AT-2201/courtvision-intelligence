from __future__ import annotations

import argparse

from courtvision.config import settings
from courtvision.db import create_schema
from courtvision.ingestion.kaggle_sqlite import KaggleSQLiteReader


def main() -> None:
    parser = argparse.ArgumentParser(prog="courtvision")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init-db", help="Create PostgreSQL tables")
    subparsers.add_parser("inspect-source", help="Inspect the Kaggle SQLite schema")
    ingest = subparsers.add_parser("ingest", help="Validate a season before warehouse loading")
    ingest.add_argument("--season", default=settings.season)
    args = parser.parse_args()

    if args.command == "init-db":
        create_schema()
        print("CourtVision schema created.")
        return

    reader = KaggleSQLiteReader(settings.source_db)
    tables = reader.inspect()
    if args.command == "inspect-source":
        for table in tables:
            print(f"{table.name}: {table.row_count:,} rows · {len(table.columns)} columns")
        return

    required = {
        "teams": reader.find_table("team", "teams", "dim_team"),
        "players": reader.find_table("player", "players", "dim_player"),
        "games": reader.find_table("game", "games", "dim_game", "fact_game"),
    }
    missing = [label for label, table in required.items() if table is None]
    if missing:
        raise SystemExit(f"Cannot ingest: missing source areas: {', '.join(missing)}")
    print(f"Source validated for {args.season}. Full row loading is the next milestone.")


if __name__ == "__main__":
    main()

