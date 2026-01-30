import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app: Flask):
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "database", "ScoutsLens.db"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        from models import (
            Lineup,
            LineupPlayer,
            PlayerGameStats,
            PlayerInformation,
            User,
        )

        db.create_all()
