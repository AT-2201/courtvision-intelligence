select
    game_id,
    season,
    game_date,
    game_type,
    home_team_id,
    away_team_id,
    home_score,
    away_score,
    case when home_score > away_score then home_team_id else away_team_id end as winner_team_id,
    abs(home_score - away_score) as margin
from {{ source('raw', 'games') }}
where home_score is not null
  and away_score is not null
