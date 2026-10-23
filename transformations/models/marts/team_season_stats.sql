with results as (
    select
        season,
        home_team_id as team_id,
        home_score as points_for,
        away_score as points_against,
        case when home_score > away_score then 1 else 0 end as win
    from {{ ref('stg_games') }}
    union all
    select
        season,
        away_team_id as team_id,
        away_score as points_for,
        home_score as points_against,
        case when away_score > home_score then 1 else 0 end as win
    from {{ ref('stg_games') }}
),
box_scores as (
    select
        games.season,
        team.*,
        opponent.points as opponent_points,
        opponent.estimated_possessions as opponent_estimated_possessions,
        team.offensive_rebounds
            / nullif(team.offensive_rebounds + opponent.defensive_rebounds, 0)
            as offensive_rebound_pct
    from {{ ref('stg_team_game_stats') }} as team
    inner join {{ ref('stg_team_game_stats') }} as opponent
        on team.game_id = opponent.game_id
        and team.team_id <> opponent.team_id
    inner join {{ ref('stg_games') }} as games using (game_id)
),
aggregated_box as (
    select
        season,
        team_id,
        sum(points) as points,
        sum(opponent_points) as opponent_points,
        sum(estimated_possessions) as possessions,
        sum(opponent_estimated_possessions) as opponent_possessions,
        avg(effective_field_goal_pct) as effective_field_goal_pct,
        avg(turnover_pct) as turnover_pct,
        avg(offensive_rebound_pct) as offensive_rebound_pct,
        avg(free_throw_rate) as free_throw_rate
    from box_scores
    group by 1, 2
),
aggregated_results as (
    select
        season,
        team_id,
        count(*) as games,
        sum(win) as wins,
        count(*) - sum(win) as losses,
        avg(points_for) as points_per_game,
        avg(points_against) as opponent_points_per_game,
        avg(points_for - points_against) as point_differential
    from results
    group by 1, 2
)
select
    results.season,
    results.team_id,
    results.games,
    results.wins,
    results.losses,
    round(results.points_per_game, 2) as points_per_game,
    round(results.opponent_points_per_game, 2) as opponent_points_per_game,
    round(results.point_differential, 2) as point_differential,
    round(100 * box.points / nullif(box.possessions, 0), 2) as offensive_rating,
    round(100 * box.opponent_points / nullif(box.opponent_possessions, 0), 2)
        as defensive_rating,
    round(box.effective_field_goal_pct, 4) as effective_field_goal_pct,
    round(box.turnover_pct, 4) as turnover_pct,
    round(box.offensive_rebound_pct, 4) as offensive_rebound_pct,
    round(box.free_throw_rate, 4) as free_throw_rate
from aggregated_results as results
inner join aggregated_box as box using (season, team_id)

