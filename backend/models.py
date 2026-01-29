from config import db
from datetime import datetime


class PlayerInformation(db.Model):
    __tablename__ = "player_information"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    team_name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(10), nullable=False)
    salary = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "full_name": self.full_name,
            "team_name": self.team_name,
            "position": self.position,
            "salary": self.salary,
        }


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Lineup(db.Model):
    __tablename__ = "lineups"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_salary = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    players = db.relationship('LineupPlayer', backref='lineup', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "date": self.date.isoformat() if self.date else None,
            "total_salary": self.total_salary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "players": [player.to_dict() for player in self.players]
        }


class LineupPlayer(db.Model):
    __tablename__ = "lineup_players"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lineup_id = db.Column(db.Integer, db.ForeignKey('lineups.id'), nullable=False)
    player_id = db.Column(db.Integer, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    team_name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(10), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    slot = db.Column(db.String(10), nullable=True)  # 首发位置，替补为None
    is_starting = db.Column(db.Boolean, nullable=False, default=False)

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
            "is_starting": self.is_starting
        }


class PlayerGameStats(db.Model):
    __tablename__ = "player_game_stats"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    personId = db.Column(db.Integer, nullable=False)
    teamName = db.Column(db.String(255), nullable=False)
    minutes = db.Column(db.Integer, nullable=False, default=0)
    threePointersMade = db.Column(db.Integer, nullable=False, default=0)
    threePointersAttempted = db.Column(db.Integer, nullable=False, default=0)
    twoPointersMade = db.Column(db.Integer, nullable=False, default=0)
    twoPointersAttempted = db.Column(db.Integer, nullable=False, default=0)
    freeThrowsMade = db.Column(db.Integer, nullable=False, default=0)
    freeThrowsAttempted = db.Column(db.Integer, nullable=False, default=0)
    reboundsOffensive = db.Column(db.Integer, nullable=False, default=0)
    reboundsDefensive = db.Column(db.Integer, nullable=False, default=0)
    assists = db.Column(db.Integer, nullable=False, default=0)
    steals = db.Column(db.Integer, nullable=False, default=0)
    blocks = db.Column(db.Integer, nullable=False, default=0)
    turnovers = db.Column(db.Integer, nullable=False, default=0)
    foulsPersonal = db.Column(db.Integer, nullable=False, default=0)
    IS_WINNER = db.Column(db.Boolean, nullable=False, default=False)
    game_date = db.Column(db.Date, nullable=False)

    @property
    def points(self):
        # 计算得分：三分球 * 3 + 两分球 * 2 + 罚球 * 1
        return self.threePointersMade * 3 + self.twoPointersMade * 2 + self.freeThrowsMade

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
            "points": self.points
        }
