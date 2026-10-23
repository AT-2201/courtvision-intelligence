from __future__ import annotations

import argparse

from courtvision.config import settings
from courtvision.db import create_schema, engine
from courtvision.ingestion.kaggle_sqlite import KaggleSQLiteReader
from courtvision.ingestion.season_csv import SeasonCSVReader
from courtvision.ingestion.warehouse import PostgresWarehouseLoader


def main() -> None:
    parser = argparse.ArgumentParser(prog="courtvision")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init-db", help="Create PostgreSQL tables")
    subparsers.add_parser("inspect-source", help="Inspect the Kaggle SQLite schema")
    ingest = subparsers.add_parser("ingest", help="Validate a season before warehouse loading")
    ingest.add_argument("--season", default=settings.season)
    audit = subparsers.add_parser("audit-csv", help="Audit the normalized season CSV source")
    audit.add_argument("--season", default=settings.season)
    audit.add_argument("--input-dir", default=settings.source_csv_dir)
    load = subparsers.add_parser("load-warehouse", help="Upsert a CSV season into PostgreSQL")
    load.add_argument("--season", default=settings.season)
    load.add_argument("--input-dir", default=settings.source_csv_dir)
    load.add_argument("--batch-size", default=2_000, type=int)
    args = parser.parse_args()

    if args.command == "init-db":
        create_schema()
        print("CourtVision schema created.")
        return

    if args.command in {"audit-csv", "load-warehouse"}:
        csv_reader = SeasonCSVReader(args.input_dir, args.season)
        if args.command == "audit-csv":
            for label, count in csv_reader.audit().items():
                print(f"{label}: {count:,}")
            return
        counts = PostgresWarehouseLoader(engine, batch_size=args.batch_size).load(csv_reader)
        for label, count in counts.items():
            print(f"{label}: {count:,} rows upserted")
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
