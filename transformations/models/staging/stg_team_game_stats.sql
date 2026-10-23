select
    game_id,
    team_id,
    points,
    field_goals_made,
    field_goals_attempted,
    three_points_made,
    three_points_attempted,
    free_throws_made,
    free_throws_attempted,
    offensive_rebounds,
    defensive_rebounds,
    assists,
    steals,
    blocks,
    turnovers,
    field_goals_attempted - offensive_rebounds + turnovers
        + (0.44 * free_throws_attempted) as estimated_possessions,
    (field_goals_made + (0.5 * three_points_made))
        / nullif(field_goals_attempted, 0) as effective_field_goal_pct,
    turnovers
        / nullif(field_goals_attempted + (0.44 * free_throws_attempted) + turnovers, 0)
        as turnover_pct,
    free_throws_attempted / nullif(field_goals_attempted, 0) as free_throw_rate
from {{ source('raw', 'team_game_stats') }}
