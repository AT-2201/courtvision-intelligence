with player_games as (
    select
        games.season,
        games.game_date,
        stats.player_id,
        stats.team_id,
        stats.game_id,
        stats.minutes,
        stats.points,
        stats.rebounds,
        stats.assists,
        stats.steals,
        stats.blocks,
        stats.turnovers
    from {{ ref('stg_player_game_stats') }} as stats
    inner join {{ ref('stg_games') }} as games using (game_id)
)
select
    *,
    round(avg(points) over last_five, 2) as points_last_5,
    round(avg(rebounds) over last_five, 2) as rebounds_last_5,
    round(avg(assists) over last_five, 2) as assists_last_5,
    round(avg(points) over last_ten, 2) as points_last_10,
    round(avg(rebounds) over last_ten, 2) as rebounds_last_10,
    round(avg(assists) over last_ten, 2) as assists_last_10
from player_games
window
    last_five as (
        partition by season, player_id order by game_date, game_id
        rows between 4 preceding and current row
    ),
    last_ten as (
        partition by season, player_id order by game_date, game_id
        rows between 9 preceding and current row
    )
