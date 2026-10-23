with player_games as (
    select
        stats.*,
        games.season
    from {{ ref('stg_player_game_stats') }} as stats
    inner join {{ source('raw', 'games') }} as games using (game_id)
),
aggregated as (
    select
        season,
        player_id,
        max(team_id) as team_id,
        count(distinct game_id) as games,
        sum(minutes) as minutes,
        sum(points) as points,
        sum(rebounds) as rebounds,
        sum(assists) as assists,
        sum(steals) as steals,
        sum(blocks) as blocks,
        sum(turnovers) as turnovers,
        sum(field_goals_attempted) as field_goals_attempted,
        sum(free_throws_attempted) as free_throws_attempted
    from player_games
    group by 1, 2
)
select
    *,
    round(points::numeric / nullif(games, 0), 2) as points_per_game,
    round(rebounds::numeric / nullif(games, 0), 2) as rebounds_per_game,
    round(assists::numeric / nullif(games, 0), 2) as assists_per_game,
    round(
        points::numeric / nullif(2 * (field_goals_attempted + 0.44 * free_throws_attempted), 0),
        4
    ) as true_shooting_pct
from aggregated

