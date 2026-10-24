from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

TEAM_META = {
    1610612737: ("ATL", "Atlanta Hawks", "East"),
    1610612738: ("BOS", "Boston Celtics", "East"),
    1610612751: ("BKN", "Brooklyn Nets", "East"),
    1610612766: ("CHA", "Charlotte Hornets", "East"),
    1610612741: ("CHI", "Chicago Bulls", "East"),
    1610612739: ("CLE", "Cleveland Cavaliers", "East"),
    1610612742: ("DAL", "Dallas Mavericks", "West"),
    1610612743: ("DEN", "Denver Nuggets", "West"),
    1610612765: ("DET", "Detroit Pistons", "East"),
    1610612744: ("GSW", "Golden State Warriors", "West"),
    1610612745: ("HOU", "Houston Rockets", "West"),
    1610612754: ("IND", "Indiana Pacers", "East"),
    1610612746: ("LAC", "LA Clippers", "West"),
    1610612747: ("LAL", "Los Angeles Lakers", "West"),
    1610612763: ("MEM", "Memphis Grizzlies", "West"),
    1610612748: ("MIA", "Miami Heat", "East"),
    1610612749: ("MIL", "Milwaukee Bucks", "East"),
    1610612750: ("MIN", "Minnesota Timberwolves", "West"),
    1610612740: ("NOP", "New Orleans Pelicans", "West"),
    1610612752: ("NYK", "New York Knicks", "East"),
    1610612760: ("OKC", "Oklahoma City Thunder", "West"),
    1610612753: ("ORL", "Orlando Magic", "East"),
    1610612755: ("PHI", "Philadelphia 76ers", "East"),
    1610612756: ("PHX", "Phoenix Suns", "West"),
    1610612757: ("POR", "Portland Trail Blazers", "West"),
    1610612758: ("SAC", "Sacramento Kings", "West"),
    1610612759: ("SAS", "San Antonio Spurs", "West"),
    1610612761: ("TOR", "Toronto Raptors", "East"),
    1610612762: ("UTA", "Utah Jazz", "West"),
    1610612764: ("WAS", "Washington Wizards", "East"),
}


def number(value: str | None) -> float:
    try:
        return float(value or 0)
    except ValueError:
        return 0.0


def integer(value: str | None) -> int:
    return int(number(value))


def season_game_prefix(season: str) -> str:
    start_year = int(season.split("-", maxsplit=1)[0])
    return f"2{start_year % 100:02d}"


def normalized_name(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", ascii_value.lower())


NAME_ALIASES = {
    "gogabitadze": "gabitadze",  # Source typo: first name stored as "ga".
    "jeenathanwilliams": "natewilliams",
    "kjmartin": "kenyonmartinjr",
}

TEAM_ALIASES = {"BRK": "BKN", "CHO": "CHA", "PHO": "PHX"}


def is_regular_season_row(row: dict[str, str], prefix: str) -> bool:
    # The 66 in-season tournament games count in the NBA regular-season
    # standings but are labelled separately in the source. The championship
    # game has a different game-id prefix and is therefore excluded here.
    included_types = {"Regular Season", "NBA Emirates Cup"}
    return row.get("gameType") in included_types and row.get("gameId", "").startswith(prefix)


def build_export(input_dir: Path, season: str) -> dict[str, object]:
    prefix = season_game_prefix(season)

    raw_games: list[dict[str, str]] = []
    standings = {team_id: {"wins": 0, "losses": 0} for team_id in TEAM_META}
    with (input_dir / "Games.csv").open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if not is_regular_season_row(row, prefix):
                continue
            home_id = integer(row["hometeamId"])
            away_id = integer(row["awayteamId"])
            winner = integer(row["winner"])
            if home_id not in TEAM_META or away_id not in TEAM_META:
                continue
            standings[home_id]["wins" if winner == home_id else "losses"] += 1
            standings[away_id]["wins" if winner == away_id else "losses"] += 1
            raw_games.append(row)

    team_rows_by_game: dict[str, dict[int, dict[str, str]]] = defaultdict(dict)
    with (input_dir / "TeamStatistics.csv").open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if is_regular_season_row(row, prefix):
                team_rows_by_game[row["gameId"]][integer(row["teamId"])] = row

    team_totals = {team_id: defaultdict(float, {"games": 0}) for team_id in TEAM_META}
    for rows in team_rows_by_game.values():
        if len(rows) != 2:
            continue
        team_ids = list(rows)
        for team_id in team_ids:
            row = rows[team_id]
            opponent_id = team_ids[1] if team_ids[0] == team_id else team_ids[0]
            opponent = rows[opponent_id]
            possessions = (
                number(row["fieldGoalsAttempted"])
                - number(row["reboundsOffensive"])
                + number(row["turnovers"])
                + 0.44 * number(row["freeThrowsAttempted"])
            )
            opponent_possessions = (
                number(opponent["fieldGoalsAttempted"])
                - number(opponent["reboundsOffensive"])
                + number(opponent["turnovers"])
                + 0.44 * number(opponent["freeThrowsAttempted"])
            )
            totals = team_totals[team_id]
            totals["games"] += 1
            totals["points"] += number(row["teamScore"])
            totals["opponent_points"] += number(row["opponentScore"])
            totals["possessions"] += possessions
            totals["opponent_possessions"] += opponent_possessions
            totals["pace"] += (possessions + opponent_possessions) / 2

    teams = []
    for team_id, (abbr, name, conference) in TEAM_META.items():
        totals = team_totals[team_id]
        games = totals["games"] or 1
        teams.append(
            {
                "abbr": abbr,
                "name": name,
                "conference": conference,
                "wins": standings[team_id]["wins"],
                "losses": standings[team_id]["losses"],
                "ppg": round(totals["points"] / games, 1),
                "oppg": round(totals["opponent_points"] / games, 1),
                "ortg": round(100 * totals["points"] / totals["possessions"], 1),
                "drtg": round(100 * totals["opponent_points"] / totals["opponent_possessions"], 1),
                "pace": round(totals["pace"] / games, 1),
            }
        )
    teams.sort(key=lambda team: (-team["wins"], team["name"]))

    games = []
    for row in raw_games:
        home_id = integer(row["hometeamId"])
        away_id = integer(row["awayteamId"])
        home_abbr, home_name, _ = TEAM_META[home_id]
        away_abbr, away_name, _ = TEAM_META[away_id]
        home_score = integer(row["homeScore"])
        away_score = integer(row["awayScore"])
        winner_name = home_name if home_score > away_score else away_name
        game_team_rows = team_rows_by_game.get(row["gameId"], {})
        home_stats = game_team_rows.get(home_id, {})
        away_stats = game_team_rows.get(away_id, {})

        def period_scores(stats: dict[str, str]) -> list[int]:
            periods = [integer(stats.get(f"q{quarter}Points")) for quarter in range(1, 5)]
            overtime = integer(stats.get("otAllPoints"))
            if overtime:
                periods.append(overtime)
            return periods

        def team_game_summary(stats: dict[str, str]) -> dict[str, int | float]:
            return {
                "fgPct": round(number(stats.get("fieldGoalsPercentage")) * 100, 1),
                "threePct": round(number(stats.get("threePointersPercentage")) * 100, 1),
                "ftPct": round(number(stats.get("freeThrowsPercentage")) * 100, 1),
                "reb": integer(stats.get("reboundsTotal")),
                "ast": integer(stats.get("assists")),
                "tov": integer(stats.get("turnovers")),
                "stl": integer(stats.get("steals")),
                "blk": integer(stats.get("blocks")),
                "paint": integer(stats.get("pointsInThePaint")),
                "fastBreak": integer(stats.get("pointsFastBreak")),
                "biggestLead": integer(stats.get("biggestLead")),
                "leadChanges": integer(stats.get("leadChanges")),
            }

        home_quarters = period_scores(home_stats)
        away_quarters = period_scores(away_stats)
        games.append(
            {
                "id": row["gameId"],
                "date": row["gameDate"][:10],
                "away": away_abbr,
                "home": home_abbr,
                "awayScore": away_score,
                "homeScore": home_score,
                "quarters": home_quarters,
                "homeQuarters": home_quarters,
                "awayQuarters": away_quarters,
                "homeStats": team_game_summary(home_stats),
                "awayStats": team_game_summary(away_stats),
                "note": f"{winner_name} won by {abs(home_score - away_score)} points.",
            }
        )
    games.sort(key=lambda game: (game["date"], game["id"]), reverse=True)

    player_lookup: dict[str, dict[str, object]] = {}
    player_logs: dict[int, list[dict[str, object]]] = defaultdict(list)
    with (input_dir / "PlayerStatistics.csv").open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if not is_regular_season_row(row, prefix):
                continue
            minutes = number(row["numMinutes"])
            player_id = integer(row["personId"])
            team_id = integer(row["playerteamId"])
            if team_id not in TEAM_META:
                continue
            key = normalized_name(f"{row['firstName']} {row['lastName']}")
            totals = player_lookup.setdefault(
                key,
                {
                    "id": player_id,
                    "name": f"{row['firstName']} {row['lastName']}",
                    "team_minutes": defaultdict(float),
                },
            )
            if minutes > 0:
                totals["team_minutes"][team_id] += minutes
                opponent_id = integer(row["opponentteamId"])
                opponent = TEAM_META.get(opponent_id, ("UNK", "Unknown", ""))[0]
                player_logs[player_id].append(
                    {
                        "gameId": row["gameId"],
                        "date": row["gameDate"][:10],
                        "team": TEAM_META[team_id][0],
                        "opp": opponent,
                        "home": bool(integer(row["home"])),
                        "win": bool(integer(row["win"])),
                        "started": bool(row.get("startingPosition")),
                        "min": round(minutes, 1),
                        "pts": integer(row["points"]),
                        "reb": integer(row["reboundsTotal"]),
                        "ast": integer(row["assists"]),
                        "stl": integer(row["steals"]),
                        "blk": integer(row["blocks"]),
                        "tov": integer(row["turnovers"]),
                        "fgm": integer(row["fieldGoalsMade"]),
                        "fga": integer(row["fieldGoalsAttempted"]),
                        "tpm": integer(row["threePointersMade"]),
                        "tpa": integer(row["threePointersAttempted"]),
                        "ftm": integer(row["freeThrowsMade"]),
                        "fta": integer(row["freeThrowsAttempted"]),
                        "plusMinus": integer(row["plusMinusPoints"]),
                    }
                )

    # Basketball Reference-derived totals provide one verified season row per player.
    # Prefer the aggregate 2TM/3TM row for traded players. The game-level source above
    # supplies NBA person IDs and the team on which each player logged most minutes.
    season_year = str(int(season.split("-", maxsplit=1)[0]) + 1)
    official_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    with (input_dir / "Player Totals.csv").open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row.get("season") == season_year and row.get("lg") == "NBA":
                official_rows[row["player_id"]].append(row)

    players = []
    for rows in official_rows.values():
        row = next((item for item in rows if item["team"].endswith("TM")), rows[0])
        key = normalized_name(row["player"])
        lookup_key = NAME_ALIASES.get(key, key)
        source_player = player_lookup.get(lookup_key)
        if source_player is None:
            # Suffix differences such as Jr., II and III are common between sources.
            stripped = re.sub(r"(jr|sr|ii|iii|iv)$", "", lookup_key)
            source_player = next(
                (
                    value
                    for candidate, value in player_lookup.items()
                    if re.sub(r"(jr|sr|ii|iii|iv)$", "", candidate) == stripped
                ),
                None,
            )
        if source_player is None:
            raise ValueError(f"Could not match official player row: {row['player']}")

        games_played = integer(row["g"])
        if row["team"].endswith("TM"):
            team_id = max(source_player["team_minutes"], key=source_player["team_minutes"].get)
            team = TEAM_META[team_id][0]
        else:
            team = TEAM_ALIASES.get(row["team"], row["team"])
        true_shooting_denominator = 2 * (number(row["fga"]) + 0.44 * number(row["fta"]))
        players.append(
            {
                "id": source_player["id"],
                "name": row["player"],
                "team": team,
                "pos": row["pos"],
                "games": games_played,
                "min": round(number(row["mp"]) / games_played, 1),
                "pts": round(number(row["pts"]) / games_played, 1),
                "reb": round(number(row["trb"]) / games_played, 1),
                "ast": round(number(row["ast"]) / games_played, 1),
                "stl": round(number(row["stl"]) / games_played, 1),
                "blk": round(number(row["blk"]) / games_played, 1),
                "tov": round(number(row["tov"]) / games_played, 1),
                "ts": round(100 * number(row["pts"]) / true_shooting_denominator, 1)
                if true_shooting_denominator
                else 0.0,
                "totalMin": integer(row["mp"]),
            }
        )
    players.sort(key=lambda player: (-player["totalMin"], player["name"]))
    exported_player_ids = {player["id"] for player in players}
    exported_logs = {
        str(player_id): sorted(logs, key=lambda item: (item["date"], item["gameId"]), reverse=True)
        for player_id, logs in player_logs.items()
        if player_id in exported_player_ids
    }

    return {
        "meta": {
            "season": season,
            "seasonType": "Regular Season",
            "teamCount": len(teams),
            "gameCount": len(games),
            "playerCount": len(players),
            "playerGameCount": sum(len(logs) for logs in exported_logs.values()),
            "source": "Eoin Moore + Sumitro Datta · Kaggle",
            "license": "CC0 1.0",
            "seasonEnd": str(date(2024, 4, 14)),
        },
        "teams": teams,
        "players": players,
        "games": games,
        "playerLogs": exported_logs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the CourtVision browser export")
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/kaggle"))
    parser.add_argument("--season", default="2023-24")
    parser.add_argument("--output", type=Path, default=Path("dist/assets/data.js"))
    args = parser.parse_args()

    export = build_export(args.input_dir, args.season)
    if export["meta"]["gameCount"] != 1230:
        raise SystemExit(
            f"Expected 1,230 regular-season games, found {export['meta']['gameCount']:,}."
        )
    invalid_teams = [
        team["abbr"] for team in export["teams"] if team["wins"] + team["losses"] != 82
    ]
    if invalid_teams:
        raise SystemExit(f"Expected 82 games for every team; invalid: {invalid_teams}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "window.COURTVISION_DATA = "
        + json.dumps(export, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(
        f"Exported {export['meta']['teamCount']} teams, "
        f"{export['meta']['playerCount']} players and "
        f"{export['meta']['gameCount']} games to {args.output}."
    )


if __name__ == "__main__":
    main()
