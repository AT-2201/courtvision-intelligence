from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import Engine
from sqlalchemy.dialects.postgresql import insert

from courtvision.db import Base
from courtvision.ingestion.season_csv import SeasonCSVReader
from courtvision.models import Game, Player, PlayerGameStat, Team, TeamGameStat


def batches(rows: Iterable[dict[str, object]], size: int) -> Iterable[list[dict[str, object]]]:
    batch: list[dict[str, object]] = []
    for row in rows:
        batch.append(row)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


class PostgresWarehouseLoader:
    """Idempotent PostgreSQL loader for the normalized raw layer."""

    def __init__(self, engine: Engine, *, batch_size: int = 2_000):
        self.engine = engine
        self.batch_size = batch_size

    def _upsert(
        self,
        model: type[Team | Player | Game | PlayerGameStat | TeamGameStat],
        rows: Iterable[dict[str, object]],
        conflict_columns: list[str],
    ) -> int:
        loaded = 0
        table = model.__table__
        update_columns = [column.name for column in table.columns if column.name != "id"]
        with self.engine.begin() as connection:
            for batch in batches(rows, self.batch_size):
                statement = insert(table).values(batch)
                statement = statement.on_conflict_do_update(
                    index_elements=conflict_columns,
                    set_={column: getattr(statement.excluded, column) for column in update_columns},
                )
                connection.execute(statement)
                loaded += len(batch)
        return loaded

    def load(self, reader: SeasonCSVReader) -> dict[str, int]:
        Base.metadata.create_all(bind=self.engine)
        return {
            "teams": self._upsert(Team, reader.teams(), ["team_id"]),
            "players": self._upsert(Player, reader.players(), ["player_id"]),
            "games": self._upsert(Game, reader.games(), ["game_id"]),
            "team_game_stats": self._upsert(
                TeamGameStat, reader.team_game_stats(), ["game_id", "team_id"]
            ),
            "player_game_stats": self._upsert(
                PlayerGameStat, reader.player_game_stats(), ["game_id", "player_id"]
            ),
        }
