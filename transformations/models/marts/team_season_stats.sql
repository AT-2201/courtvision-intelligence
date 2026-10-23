with team_games as (
    select
        season,
        home_team_id as team_id,
        home_score as points_for,
        away_score as points_against,
        case when home_score > away_score then 1 else 0 end as win
    from {{ source('raw', 'games') }}
    union all
    select
        season,
        away_team_id as team_id,
        away_score as points_for,
        home_score as points_against,
        case when away_score > home_score then 1 else 0 end as win
    from {{ source('raw', 'games') }}
)
select
    season,
    team_id,
    count(*) as games,
    sum(win) as wins,
    count(*) - sum(win) as losses,
    round(avg(points_for), 2) as points_per_game,
    round(avg(points_against), 2) as opponent_points_per_game,
    round(avg(points_for - points_against), 2) as point_differential
from team_games
group by 1, 2

