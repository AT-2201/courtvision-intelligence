import sqlite3

import pytest

from courtvision.ingestion.kaggle_sqlite import KaggleSQLiteReader
from courtvision.ingestion.season_csv import included_game, position_from_flags, season_prefix
from courtvision.ingestion.warehouse import batches


def test_inspects_source_schema(tmp_path) -> None:
    source = tmp_path / "source.sqlite"
    with sqlite3.connect(source) as connection:
        connection.execute("create table player (player_id integer, name text)")
        connection.execute("insert into player values (1, 'Example Player')")

    tables = KaggleSQLiteReader(source).inspect()

    assert tables[0].name == "player"
    assert tables[0].columns == ("player_id", "name")
    assert tables[0].row_count == 1


def test_missing_source_is_clear(tmp_path) -> None:
    with pytest.raises(FileNotFoundError, match="Download it from Kaggle"):
        KaggleSQLiteReader(tmp_path / "missing.sqlite").inspect()


def test_season_csv_filters_regular_season_and_cup_games() -> None:
    assert season_prefix("2023-24") == "223"
    assert included_game({"gameId": "22300001", "gameType": "Regular Season"}, "2023-24")
    assert included_game({"gameId": "22300420", "gameType": "NBA Emirates Cup"}, "2023-24")
    assert not included_game({"gameId": "52300001", "gameType": "NBA Emirates Cup"}, "2023-24")


def test_position_flags_and_batches_are_normalized() -> None:
    assert position_from_flags({"guard": "1", "forward": "1", "center": "0"}) == "G-F"
    assert list(batches(({"id": value} for value in range(5)), 2)) == [
        [{"id": 0}, {"id": 1}],
        [{"id": 2}, {"id": 3}],
        [{"id": 4}],
    ]
