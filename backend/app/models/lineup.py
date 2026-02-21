from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Lineup(Base):
    """阵容模型"""

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
    """阵容球员模型"""

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
