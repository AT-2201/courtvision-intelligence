from pathlib import Path

from scripts.build_season_export import (
    build_export,
    is_regular_season_row,
    normalized_name,
    season_game_prefix,
)


def test_2023_24_game_prefix() -> None:
    assert season_game_prefix("2023-24") == "223"


def test_regular_season_includes_in_season_tournament_but_not_final() -> None:
    assert is_regular_season_row({"gameType": "NBA Emirates Cup", "gameId": "22300420"}, "223")
    assert not is_regular_season_row({"gameType": "NBA Emirates Cup", "gameId": "52300001"}, "223")


def test_player_names_match_across_accented_sources() -> None:
    assert normalized_name("Luka Dončić") == normalized_name("Luka Doncic")


def test_export_contains_player_logs_and_game_comparison_stats() -> None:
    export = build_export(Path("data/raw/kaggle"), "2023-24")
    luka = next(player for player in export["players"] if player["name"] == "Luka Dončić")
    logs = export["playerLogs"][str(luka["id"])]

    assert len(logs) == luka["games"]
    assert {"pts", "reb", "ast", "plusMinus", "opp"} <= logs[0].keys()
    assert {"homeStats", "awayStats", "homeQuarters", "awayQuarters"} <= export["games"][0].keys()
