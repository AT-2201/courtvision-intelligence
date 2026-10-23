from scripts.build_season_export import (
    is_regular_season_row,
    normalized_name,
    season_game_prefix,
)


def test_2023_24_game_prefix() -> None:
    assert season_game_prefix("2023-24") == "223"


def test_regular_season_includes_in_season_tournament_but_not_final() -> None:
    assert is_regular_season_row(
        {"gameType": "NBA Emirates Cup", "gameId": "22300420"}, "223"
    )
    assert not is_regular_season_row(
        {"gameType": "NBA Emirates Cup", "gameId": "52300001"}, "223"
    )


def test_player_names_match_across_accented_sources() -> None:
    assert normalized_name("Luka Dončić") == normalized_name("Luka Doncic")
