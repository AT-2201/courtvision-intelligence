from __future__ import annotations


def true_shooting_percentage(points: float, fga: float, fta: float) -> float:
    denominator = 2 * (fga + 0.44 * fta)
    return round(points / denominator, 4) if denominator else 0.0


def possessions(fga: float, offensive_rebounds: float, turnovers: float, fta: float) -> float:
    return round(fga - offensive_rebounds + turnovers + 0.44 * fta, 2)


def per_100(value: float, estimated_possessions: float) -> float:
    return round(100 * value / estimated_possessions, 2) if estimated_possessions else 0.0

