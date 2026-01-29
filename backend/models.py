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
