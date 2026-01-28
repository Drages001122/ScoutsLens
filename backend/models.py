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
