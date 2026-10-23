from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from functools import cached_property
from pathlib import Path

from courtvision.analytics.similarity import PlayerSeason, similar_players


def fold_text(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", ascii_value.casefold()).strip()


class SeasonMartRepository:
    """Read the generated analytical mart used by both FastAPI and the static dashboard."""

    def __init__(self, export_path: str | Path):
        self.export_path = Path(export_path)

    @cached_property
    def data(self) -> dict[str, object]:
        raw = self.export_path.read_text(encoding="utf-8")
        prefix = "window.COURTVISION_DATA = "
        if not raw.startswith(prefix):
            raise ValueError(f"Unsupported mart export: {self.export_path}")
        return json.loads(raw.removeprefix(prefix).removesuffix(";\n"))

    @property
    def teams(self) -> list[dict[str, object]]:
        return self.data["teams"]  # type: ignore[return-value]

    @property
    def players(self) -> list[dict[str, object]]:
        return self.data["players"]  # type: ignore[return-value]

    @property
    def games(self) -> list[dict[str, object]]:
        return self.data["games"]  # type: ignore[return-value]

    def bootstrap(self) -> dict[str, object]:
        return self.data

    def team(self, abbreviation: str) -> dict[str, object] | None:
        target = abbreviation.upper()
        return next((team for team in self.teams if team["abbr"] == target), None)

    def player(self, player_id: int) -> dict[str, object] | None:
        return next((player for player in self.players if player["id"] == player_id), None)

    def game(self, game_id: str) -> dict[str, object] | None:
        return next((game for game in self.games if game["id"] == game_id), None)

    def list_players(
        self,
        *,
        search: str | None = None,
        team: str | None = None,
        position: str | None = None,
        min_games: int = 0,
        sort: str = "totalMin",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, object]:
        rows = self.players
        if search:
            query = fold_text(search)
            rows = [player for player in rows if query in fold_text(str(player["name"]))]
        if team:
            rows = [player for player in rows if player["team"] == team.upper()]
        if position:
            query_position = position.upper()
            rows = [player for player in rows if query_position in str(player["pos"]).upper()]
        rows = [player for player in rows if int(player["games"]) >= min_games]
        sort_fields = {"games", "totalMin", "pts", "reb", "ast", "stl", "blk", "ts"}
        sort_field = sort if sort in sort_fields else "totalMin"
        rows = sorted(rows, key=lambda player: float(player[sort_field]), reverse=True)
        return {
            "items": rows[offset : offset + limit],
            "total": len(rows),
            "limit": limit,
            "offset": offset,
        }

    def list_games(
        self,
        *,
        team: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, object]:
        rows = self.games
        if team:
            abbreviation = team.upper()
            rows = [game for game in rows if abbreviation in {game["home"], game["away"]}]
        if date_from:
            rows = [game for game in rows if str(game["date"]) >= date_from]
        if date_to:
            rows = [game for game in rows if str(game["date"]) <= date_to]
        return {
            "items": rows[offset : offset + limit],
            "total": len(rows),
            "limit": limit,
            "offset": offset,
        }

    def similarity(self, player_id: int, *, limit: int = 5) -> list[dict[str, object]] | None:
        target_row = self.player(player_id)
        if target_row is None:
            return None

        def convert(row: dict[str, object]) -> PlayerSeason:
            return PlayerSeason(
                player_id=int(row["id"]),
                name=str(row["name"]),
                team=str(row["team"]),
                position=str(row["pos"]),
                games=int(row["games"]),
                minutes=float(row["totalMin"]),
                points=float(row["pts"]),
                rebounds=float(row["reb"]),
                assists=float(row["ast"]),
                steals=float(row["stl"]),
                blocks=float(row["blk"]),
                turnovers=float(row["tov"]),
                ts_pct=float(row["ts"]) / 100,
            )

        target = convert(target_row)
        return similar_players(target, [convert(row) for row in self.players], limit=limit)

    def league_summary(self) -> dict[str, object]:
        qualified = [player for player in self.players if int(player["games"]) >= 58]
        return {
            "meta": self.data["meta"],
            "best_record": max(self.teams, key=lambda team: int(team["wins"])),
            "top_offense": max(self.teams, key=lambda team: float(team["ortg"])),
            "top_defense": min(self.teams, key=lambda team: float(team["drtg"])),
            "scoring_leader": max(qualified, key=lambda player: float(player["pts"])),
        }

    def quality_report(self) -> dict[str, object]:
        team_games: Counter[str] = Counter()
        for game in self.games:
            team_games[str(game["home"])] += 1
            team_games[str(game["away"])] += 1
        checks = [
            {"name": "30 franchises", "passed": len(self.teams) == 30, "observed": len(self.teams)},
            {
                "name": "1,230 unique games",
                "passed": len({game["id"] for game in self.games}) == 1230,
                "observed": len(self.games),
            },
            {
                "name": "82 games per team",
                "passed": set(team_games.values()) == {82},
                "observed": f"{min(team_games.values())}-{max(team_games.values())}",
            },
            {
                "name": "unique player IDs",
                "passed": len({player["id"] for player in self.players}) == len(self.players),
                "observed": len(self.players),
            },
            {
                "name": "complete date range",
                "passed": min(game["date"] for game in self.games) == "2023-10-24"
                and max(game["date"] for game in self.games) == "2024-04-14",
                "observed": "2023-10-24 → 2024-04-14",
            },
        ]
        return {
            "status": "passed" if all(check["passed"] for check in checks) else "failed",
            "checks": checks,
        }
