select
    id,
    game_id,
    player_id,
    team_id,
    minutes,
    points,
    rebounds,
    assists,
    steals,
    blocks,
    turnovers,
    field_goals_made,
    field_goals_attempted,
    three_points_made,
    three_points_attempted,
    free_throws_made,
    free_throws_attempted,
    plus_minus
from {{ source('raw', 'player_game_stats') }}
where minutes >= 0

