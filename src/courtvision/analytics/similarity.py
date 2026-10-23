from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp, sqrt
from statistics import fmean, pstdev

METRICS = ("points", "rebounds", "assists", "steals", "blocks", "turnovers", "ts_pct")
LABELS = {
    "points": "Points",
    "rebounds": "Rebounds",
    "assists": "Assists",
    "steals": "Steals",
    "blocks": "Blocks",
    "turnovers": "Turnovers",
    "ts_pct": "True shooting",
}


@dataclass(frozen=True)
class PlayerSeason:
    player_id: int
    name: str
    team: str
    position: str
    games: int
    minutes: float
    points: float
    rebounds: float
    assists: float
    steals: float
    blocks: float
    turnovers: float
    ts_pct: float


def position_family(position: str) -> str:
    value = position.upper().strip()
    if "G" in value and "F" not in value:
        return "Guard"
    if "C" in value and "G" not in value:
        return "Center"
    return "Wing"


def similar_players(
    target: PlayerSeason,
    players: list[PlayerSeason],
    *,
    limit: int = 5,
    minimum_minutes: float = 500,
) -> list[dict[str, object]]:
    family = position_family(target.position)
    pool = [
        player
        for player in players
        if player.player_id != target.player_id
        and player.minutes >= minimum_minutes
        and position_family(player.position) == family
    ]
    comparison_pool = [target, *pool]
    spreads = {
        metric: pstdev(getattr(player, metric) for player in comparison_pool) or 1.0
        for metric in METRICS
    }

    records: list[dict[str, object]] = []
    for player in pool:
        metric_gaps = {
            metric: abs(getattr(target, metric) - getattr(player, metric)) / spreads[metric]
            for metric in METRICS
        }
        distance = sqrt(fmean(gap * gap for gap in metric_gaps.values()))
        score = round(100 * exp(-0.65 * distance), 1)
        ordered = sorted(metric_gaps, key=metric_gaps.get)
        closest = [
            {
                "metric": LABELS[metric],
                "target": round(getattr(target, metric), 2),
                "candidate": round(getattr(player, metric), 2),
            }
            for metric in ordered[:3]
        ]
        tradeoffs = [
            {
                "metric": LABELS[metric],
                "difference": round(getattr(player, metric) - getattr(target, metric), 2),
            }
            for metric in reversed(ordered[-2:])
        ]
        records.append(
            {
                "player": asdict(player),
                "similarity": score,
                "closest_traits": closest,
                "tradeoffs": tradeoffs,
            }
        )

    return sorted(records, key=lambda item: item["similarity"], reverse=True)[:limit]
