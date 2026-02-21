from sqlalchemy import Boolean, Column, Date, Integer, String

from app.db.session import Base


class PlayerGameStats(Base):
    """球员比赛数据模型"""

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
