from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceTable:
    name: str
    columns: tuple[str, ...]
    row_count: int


class KaggleSQLiteReader:
    """Inspect a Kaggle SQLite snapshot without assuming a fixed release schema."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        if not self.path.exists():
            raise FileNotFoundError(
                f"Source database not found at {self.path}. Download it from Kaggle first."
            )
        connection = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    def inspect(self) -> list[SourceTable]:
        with self.connect() as connection:
            names = [
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
                if not row[0].startswith("sqlite_")
            ]
            tables: list[SourceTable] = []
            for name in names:
                safe_name = name.replace('"', '""')
                columns = tuple(
                    row[1] for row in connection.execute(f'PRAGMA table_info("{safe_name}")')
                )
                count = connection.execute(f'SELECT COUNT(*) FROM "{safe_name}"').fetchone()[0]
                tables.append(SourceTable(name=name, columns=columns, row_count=count))
            return tables

    def find_table(self, *candidates: str) -> SourceTable | None:
        table_map = {table.name.casefold(): table for table in self.inspect()}
        matches = (
            table_map[name.casefold()] for name in candidates if name.casefold() in table_map
        )
        return next(matches, None)
