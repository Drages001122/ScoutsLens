from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from config import Base


class PlayerInformation(Base):
    __tablename__ = "player_information"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, nullable=False)
    full_name = Column(String(255), nullable=False)
    team_name = Column(String(255), nullable=False)
    position = Column(String(10), nullable=False)
    salary = Column(Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "full_name": self.full_name,
            "team_name": self.team_name,
            "position": self.position,
            "salary": self.salary,
        }


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Lineup(Base):
    __tablename__ = "lineups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    total_salary = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())

    players = relationship(
        "LineupPlayer", backref="lineup", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "date": self.date.isoformat() if self.date else None,
            "total_salary": self.total_salary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "players": [player.to_dict() for player in self.players],
        }


class LineupPlayer(Base):
    __tablename__ = "lineup_players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lineup_id = Column(Integer, ForeignKey("lineups.id"), nullable=False)
    player_id = Column(Integer, nullable=False)
    full_name = Column(String(255), nullable=False)
    team_name = Column(String(255), nullable=False)
    position = Column(String(10), nullable=False)
    salary = Column(Integer, nullable=False)
    slot = Column(String(10), nullable=True)
    is_starting = Column(Boolean, nullable=False, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "lineup_id": self.lineup_id,
            "player_id": self.player_id,
            "full_name": self.full_name,
            "team_name": self.team_name,
            "position": self.position,
            "salary": self.salary,
            "slot": self.slot,
            "is_starting": self.is_starting,
        }


class PlayerGameStats(Base):
    __tablename__ = "player_game_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    personId = Column(Integer, nullable=False)
    teamName = Column(String(255), nullable=False)
    minutes = Column(Integer, nullable=False, default=0)
    threePointersMade = Column(Integer, nullable=False, default=0)
    threePointersAttempted = Column(Integer, nullable=False, default=0)
    twoPointersMade = Column(Integer, nullable=False, default=0)
    twoPointersAttempted = Column(Integer, nullable=False, default=0)
    freeThrowsMade = Column(Integer, nullable=False, default=0)
    freeThrowsAttempted = Column(Integer, nullable=False, default=0)
    reboundsOffensive = Column(Integer, nullable=False, default=0)
    reboundsDefensive = Column(Integer, nullable=False, default=0)
    assists = Column(Integer, nullable=False, default=0)
    steals = Column(Integer, nullable=False, default=0)
    blocks = Column(Integer, nullable=False, default=0)
    turnovers = Column(Integer, nullable=False, default=0)
    foulsPersonal = Column(Integer, nullable=False, default=0)
    IS_WINNER = Column(Boolean, nullable=False, default=False)
    game_date = Column(Date, nullable=False)

    @property
    def points(self):
        return (
            self.threePointersMade * 3 + self.twoPointersMade * 2 + self.freeThrowsMade
        )

    def to_dict(self):
        return {
            "id": self.id,
            "personId": self.personId,
            "teamName": self.teamName,
            "minutes": self.minutes,
            "threePointersMade": self.threePointersMade,
            "threePointersAttempted": self.threePointersAttempted,
            "twoPointersMade": self.twoPointersMade,
            "twoPointersAttempted": self.twoPointersAttempted,
            "freeThrowsMade": self.freeThrowsMade,
            "freeThrowsAttempted": self.freeThrowsAttempted,
            "reboundsOffensive": self.reboundsOffensive,
            "reboundsDefensive": self.reboundsDefensive,
            "assists": self.assists,
            "steals": self.steals,
            "blocks": self.blocks,
            "turnovers": self.turnovers,
            "foulsPersonal": self.foulsPersonal,
            "IS_WINNER": self.IS_WINNER,
            "game_date": self.game_date.isoformat() if self.game_date else None,
            "points": self.points,
        }


class PlayerInfo(BaseModel):
    id: Optional[int] = None
    player_id: int
    full_name: str
    team_name: str
    position: str
    salary: int


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: Optional[str] = None


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)
    confirm_password: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class AuthResponse(BaseModel):
    message: str
    user: UserResponse
    token: str


class LineupPlayerCreate(BaseModel):
    player_id: int
    full_name: str
    team_name: str
    position: str
    salary: int
    slot: Optional[str] = None


class LineupCreate(BaseModel):
    name: Optional[str] = None
    date: str
    starting_players: List[LineupPlayerCreate] = Field(default_factory=list)
    bench_players: List[LineupPlayerCreate] = Field(default_factory=list)


class LineupPlayerResponse(BaseModel):
    id: int
    lineup_id: int
    player_id: int
    full_name: str
    team_name: str
    position: str
    salary: int
    slot: Optional[str] = None
    is_starting: bool
    rating: Optional[float] = None


class LineupResponse(BaseModel):
    id: int
    user_id: int
    name: str
    date: str
    total_salary: int
    created_at: str
    players: List[LineupPlayerResponse]
    username: Optional[str] = None
    can_view: Optional[bool] = None
    total_rating: Optional[float] = None


class TeamResponse(BaseModel):
    team_id: int
    team_name: str


class Pagination(BaseModel):
    current_page: int
    per_page: int
    total_items: int
    total_pages: int


class PlayerStatsResponse(BaseModel):
    player_id: int
    player_name: str
    team_name: str
    position: str
    salary: int
    minutes: float
    three_pointers_made: float
    three_pointers_attempted: float
    two_pointers_made: float
    two_pointers_attempted: float
    free_throws_made: float
    free_throws_attempted: float
    offensive_rebounds: float
    defensive_rebounds: float
    assists: float
    steals: float
    blocks: float
    turnovers: float
    personal_fouls: float
    team_won: bool
    points: float
    rating: float
    games_played: Optional[int] = None


class GameStat(BaseModel):
    game_date: str
    rating: float


class PlayerGameStatsResponse(BaseModel):
    player_id: int
    game_stats: List[GameStat]


class PlayerAverageStatsResponse(BaseModel):
    player_id: int
    games_played: int
    minutes_per_game: float
    points_per_game: float
    rebounds_per_game: float
    assists_per_game: float
    steals_per_game: float
    blocks_per_game: float
    turnovers_per_game: float
    field_goal_percentage: float
    three_point_percentage: float
    free_throw_percentage: float


class ValueForMoneyPlayer(BaseModel):
    player_id: int
    player_name: str
    team_name: str
    position: str
    salary: int
    average_rating: float
    salary_rank: Optional[int] = None
    rating_rank: Optional[int] = None


class SalaryCapResponse(BaseModel):
    salary_cap: int


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str
