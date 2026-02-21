from typing import List, Optional

from pydantic import BaseModel, Field


class LineupPlayerCreate(BaseModel):
    """阵容球员创建请求"""

    player_id: int
    full_name: str
    team_name: str
    position: str
    salary: int
    slot: Optional[str] = None


class LineupCreate(BaseModel):
    """阵容创建请求"""

    name: Optional[str] = None
    date: str
    starting_players: List[LineupPlayerCreate] = Field(default_factory=list)
    bench_players: List[LineupPlayerCreate] = Field(default_factory=list)


class LineupPlayerResponse(BaseModel):
    """阵容球员响应"""

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
    """阵容响应"""

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
