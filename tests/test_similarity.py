from courtvision.analytics.similarity import PlayerSeason, position_family, similar_players


def player(player_id: int, name: str, position: str, points: float) -> PlayerSeason:
    return PlayerSeason(
        player_id=player_id,
        name=name,
        team="TEST",
        position=position,
        games=70,
        minutes=2_000,
        points=points,
        rebounds=5,
        assists=5,
        steals=1,
        blocks=0.5,
        turnovers=2,
        ts_pct=0.6,
    )


def test_position_families() -> None:
    assert position_family("PG") == "Guard"
    assert position_family("C") == "Center"
    assert position_family("SF") == "Wing"


def test_similarity_filters_position_and_explains_result() -> None:
    target = player(1, "Target", "PG", 25)
    match = player(2, "Match", "SG", 24)
    excluded = player(3, "Center", "C", 25)

    results = similar_players(target, [target, match, excluded])

    assert len(results) == 1
    assert results[0]["player"]["name"] == "Match"
    assert len(results[0]["closest_traits"]) == 3
    assert len(results[0]["tradeoffs"]) == 2
