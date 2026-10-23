from __future__ import annotations

import csv
from collections.abc import Iterator
from datetime import date
from pathlib import Path

REGULAR_SEASON_TYPES = {"Regular Season", "NBA Emirates Cup"}

TEAM_META = {
    1610612737: ("ATL", "Atlanta", "Hawks", "East"),
    1610612738: ("BOS", "Boston", "Celtics", "East"),
    1610612751: ("BKN", "Brooklyn", "Nets", "East"),
    1610612766: ("CHA", "Charlotte", "Hornets", "East"),
    1610612741: ("CHI", "Chicago", "Bulls", "East"),
    1610612739: ("CLE", "Cleveland", "Cavaliers", "East"),
    1610612742: ("DAL", "Dallas", "Mavericks", "West"),
    1610612743: ("DEN", "Denver", "Nuggets", "West"),
    1610612765: ("DET", "Detroit", "Pistons", "East"),
    1610612744: ("GSW", "Golden State", "Warriors", "West"),
    1610612745: ("HOU", "Houston", "Rockets", "West"),
    1610612754: ("IND", "Indiana", "Pacers", "East"),
    1610612746: ("LAC", "Los Angeles", "Clippers", "West"),
    1610612747: ("LAL", "Los Angeles", "Lakers", "West"),
    1610612763: ("MEM", "Memphis", "Grizzlies", "West"),
    1610612748: ("MIA", "Miami", "Heat", "East"),
    1610612749: ("MIL", "Milwaukee", "Bucks", "East"),
    1610612750: ("MIN", "Minnesota", "Timberwolves", "West"),
    1610612740: ("NOP", "New Orleans", "Pelicans", "West"),
    1610612752: ("NYK", "New York", "Knicks", "East"),
    1610612760: ("OKC", "Oklahoma City", "Thunder", "West"),
    1610612753: ("ORL", "Orlando", "Magic", "East"),
    1610612755: ("PHI", "Philadelphia", "76ers", "East"),
    1610612756: ("PHX", "Phoenix", "Suns", "West"),
    1610612757: ("POR", "Portland", "Trail Blazers", "West"),
    1610612758: ("SAC", "Sacramento", "Kings", "West"),
    1610612759: ("SAS", "San Antonio", "Spurs", "West"),
    1610612761: ("TOR", "Toronto", "Raptors", "East"),
    1610612762: ("UTA", "Utah", "Jazz", "West"),
    1610612764: ("WAS", "Washington", "Wizards", "East"),
}


def number(value: str | None) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def integer(value: str | None) -> int:
    return int(number(value))


def season_prefix(season: str) -> str:
    return f"2{int(season[:4]) % 100:02d}"


def included_game(row: dict[str, str], season: str) -> bool:
    return row.get("gameType") in REGULAR_SEASON_TYPES and row.get("gameId", "").startswith(
        season_prefix(season)
    )


def position_from_flags(row: dict[str, str]) -> str | None:
    positions = [
        label
        for label, column in (("G", "guard"), ("F", "forward"), ("C", "center"))
        if row.get(column) == "1"
    ]
    return "-".join(positions) or None


class SeasonCSVReader:
    """Stream one normalized season from the public Kaggle CSV snapshot."""

    def __init__(self, directory: str | Path, season: str = "2023-24"):
        self.directory = Path(directory)
        self.season = season

    def _rows(self, filename: str) -> Iterator[dict[str, str]]:
        path = self.directory / filename
        if not path.exists():
            raise FileNotFoundError(f"Required source file not found: {path}")
        with path.open(newline="", encoding="utf-8-sig") as handle:
            yield from csv.DictReader(handle)

    def teams(self) -> Iterator[dict[str, object]]:
        for team_id, (abbreviation, city, name, conference) in TEAM_META.items():
            yield {
                "team_id": team_id,
                "abbreviation": abbreviation,
                "city": city,
                "name": name,
                "conference": conference,
            }

    def games(self) -> Iterator[dict[str, object]]:
        for row in self._rows("Games.csv"):
            if not included_game(row, self.season):
                continue
            yield {
                "game_id": row["gameId"],
                "season": self.season,
                "game_date": date.fromisoformat(row["gameDate"][:10]),
                "game_type": row["gameType"],
                "home_team_id": integer(row["hometeamId"]),
                "away_team_id": integer(row["awayteamId"]),
                "home_score": integer(row["homeScore"]),
                "away_score": integer(row["awayScore"]),
            }

    def players(self) -> Iterator[dict[str, object]]:
        season_players: dict[int, str] = {}
        for row in self._rows("PlayerStatistics.csv"):
            if not included_game(row, self.season):
                continue
            player_id = integer(row["personId"])
            season_players.setdefault(player_id, f"{row['firstName']} {row['lastName']}")

        yielded: set[int] = set()
        for row in self._rows("Players.csv"):
            player_id = integer(row["personId"])
            if player_id not in season_players:
                continue
            yielded.add(player_id)
            yield {
                "player_id": player_id,
                "full_name": season_players[player_id],
                "position": position_from_flags(row),
            }

        for player_id, full_name in season_players.items():
            if player_id not in yielded:
                yield {"player_id": player_id, "full_name": full_name, "position": None}

    def player_game_stats(self) -> Iterator[dict[str, object]]:
        for row in self._rows("PlayerStatistics.csv"):
            if not included_game(row, self.season):
                continue
            minutes = number(row["numMinutes"])
            if minutes <= 0:
                continue
            yield {
                "game_id": row["gameId"],
                "player_id": integer(row["personId"]),
                "team_id": integer(row["playerteamId"]),
                "started": bool(row.get("startingPosition")),
                "minutes": minutes,
                "points": integer(row["points"]),
                "rebounds": integer(row["reboundsTotal"]),
                "assists": integer(row["assists"]),
                "steals": integer(row["steals"]),
                "blocks": integer(row["blocks"]),
                "turnovers": integer(row["turnovers"]),
                "field_goals_made": integer(row["fieldGoalsMade"]),
                "field_goals_attempted": integer(row["fieldGoalsAttempted"]),
                "three_points_made": integer(row["threePointersMade"]),
                "three_points_attempted": integer(row["threePointersAttempted"]),
                "free_throws_made": integer(row["freeThrowsMade"]),
                "free_throws_attempted": integer(row["freeThrowsAttempted"]),
                "plus_minus": number(row["plusMinusPoints"]),
            }

    def team_game_stats(self) -> Iterator[dict[str, object]]:
        for row in self._rows("TeamStatistics.csv"):
            if not included_game(row, self.season):
                continue
            yield {
                "game_id": row["gameId"],
                "team_id": integer(row["teamId"]),
                "points": integer(row["teamScore"]),
                "field_goals_made": integer(row["fieldGoalsMade"]),
                "field_goals_attempted": integer(row["fieldGoalsAttempted"]),
                "three_points_made": integer(row["threePointersMade"]),
                "three_points_attempted": integer(row["threePointersAttempted"]),
                "free_throws_made": integer(row["freeThrowsMade"]),
                "free_throws_attempted": integer(row["freeThrowsAttempted"]),
                "offensive_rebounds": integer(row["reboundsOffensive"]),
                "defensive_rebounds": integer(row["reboundsDefensive"]),
                "assists": integer(row["assists"]),
                "steals": integer(row["steals"]),
                "blocks": integer(row["blocks"]),
                "turnovers": integer(row["turnovers"]),
            }

    def audit(self) -> dict[str, int]:
        games = list(self.games())
        team_rows = list(self.team_game_stats())
        player_rows = list(self.player_game_stats())
        return {
            "teams": len(TEAM_META),
            "games": len(games),
            "team_game_rows": len(team_rows),
            "player_game_rows": len(player_rows),
            "unique_players": len({row["player_id"] for row in player_rows}),
        }
