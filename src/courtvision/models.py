from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from courtvision.db import Base


class Team(Base):
    __tablename__ = "teams"

    team_id: Mapped[int] = mapped_column(primary_key=True)
    abbreviation: Mapped[str] = mapped_column(String(4), unique=True, index=True)
    city: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(80))
    conference: Mapped[str | None] = mapped_column(String(10))


class Player(Base):
    __tablename__ = "players"

    player_id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(140), index=True)
    position: Mapped[str | None] = mapped_column(String(30))


class Game(Base):
    __tablename__ = "games"

    game_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    season: Mapped[str] = mapped_column(String(10), index=True)
    game_date: Mapped[date] = mapped_column(Date, index=True)
    game_type: Mapped[str] = mapped_column(String(40), default="Regular Season")
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"))
    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)


class PlayerGameStat(Base):
    __tablename__ = "player_game_stats"
    __table_args__ = (
        UniqueConstraint("game_id", "player_id", name="uq_player_game"),
        Index("ix_player_game_season", "player_id", "game_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.game_id"))
    player_id: Mapped[int] = mapped_column(ForeignKey("players.player_id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"))
    started: Mapped[bool] = mapped_column(Boolean, default=False)
    minutes: Mapped[float] = mapped_column(Float, default=0)
    points: Mapped[int] = mapped_column(Integer, default=0)
    rebounds: Mapped[int] = mapped_column(Integer, default=0)
    assists: Mapped[int] = mapped_column(Integer, default=0)
    steals: Mapped[int] = mapped_column(Integer, default=0)
    blocks: Mapped[int] = mapped_column(Integer, default=0)
    turnovers: Mapped[int] = mapped_column(Integer, default=0)
    field_goals_made: Mapped[int] = mapped_column(Integer, default=0)
    field_goals_attempted: Mapped[int] = mapped_column(Integer, default=0)
    three_points_made: Mapped[int] = mapped_column(Integer, default=0)
    three_points_attempted: Mapped[int] = mapped_column(Integer, default=0)
    free_throws_made: Mapped[int] = mapped_column(Integer, default=0)
    free_throws_attempted: Mapped[int] = mapped_column(Integer, default=0)
    plus_minus: Mapped[float] = mapped_column(Float, default=0)


class TeamGameStat(Base):
    __tablename__ = "team_game_stats"
    __table_args__ = (
        UniqueConstraint("game_id", "team_id", name="uq_team_game"),
        Index("ix_team_game_team", "team_id", "game_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.game_id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.team_id"))
    points: Mapped[int] = mapped_column(Integer, default=0)
    field_goals_made: Mapped[int] = mapped_column(Integer, default=0)
    field_goals_attempted: Mapped[int] = mapped_column(Integer, default=0)
    three_points_made: Mapped[int] = mapped_column(Integer, default=0)
    three_points_attempted: Mapped[int] = mapped_column(Integer, default=0)
    free_throws_made: Mapped[int] = mapped_column(Integer, default=0)
    free_throws_attempted: Mapped[int] = mapped_column(Integer, default=0)
    offensive_rebounds: Mapped[int] = mapped_column(Integer, default=0)
    defensive_rebounds: Mapped[int] = mapped_column(Integer, default=0)
    assists: Mapped[int] = mapped_column(Integer, default=0)
    steals: Mapped[int] = mapped_column(Integer, default=0)
    blocks: Mapped[int] = mapped_column(Integer, default=0)
    turnovers: Mapped[int] = mapped_column(Integer, default=0)


class PlayByPlayEvent(Base):
    __tablename__ = "play_by_play_events"
    __table_args__ = (Index("ix_pbp_game_sequence", "game_id", "event_number"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.game_id"))
    event_number: Mapped[int] = mapped_column(Integer)
    period: Mapped[int] = mapped_column(Integer)
    clock: Mapped[str | None] = mapped_column(String(12))
    event_type: Mapped[str | None] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(String(500))
    team_id: Mapped[int | None] = mapped_column(Integer)
    player_id: Mapped[int | None] = mapped_column(Integer)
    score_home: Mapped[int | None] = mapped_column(Integer)
    score_away: Mapped[int | None] = mapped_column(Integer)
