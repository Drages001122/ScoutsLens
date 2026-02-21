from typing import List, Optional

from pydantic import BaseModel


class PlayerStatsResponse(BaseModel):
    """球员统计响应"""

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
    """单场比赛统计"""

    game_date: str
    rating: float


class PlayerGameStatsResponse(BaseModel):
    """球员比赛统计响应"""

    player_id: int
    game_stats: List[GameStat]


class PlayerAverageStatsResponse(BaseModel):
    """球员平均统计响应"""

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
    """性价比球员"""

    player_id: int
    player_name: str
    team_name: str
    position: str
    salary: int
    average_rating: float
    salary_rank: Optional[int] = None
    rating_rank: Optional[int] = None


class SalaryCapResponse(BaseModel):
    """薪资帽响应"""

    salary_cap: int
