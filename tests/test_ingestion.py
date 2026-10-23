import sqlite3

import pytest

from courtvision.ingestion.kaggle_sqlite import KaggleSQLiteReader


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

