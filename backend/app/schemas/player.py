from typing import Optional

from pydantic import BaseModel


class PlayerInfo(BaseModel):
    """球员信息"""

    id: Optional[int] = None
    player_id: int
    full_name: str
    team_name: str
    position: str
    salary: int
