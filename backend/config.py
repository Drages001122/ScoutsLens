import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app: Flask):
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "database", "scoutslens.db"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        # These imports are necessary for db.create_all() to create the tables
        # Do not remove them even if they appear unused
        from models import Lineup  # noqa: F401
        from models import LineupPlayer  # noqa: F401
        from models import PlayerGameStats  # noqa: F401
        from models import PlayerInformation  # noqa: F401
        from models import User  # noqa: F401

        db.create_all()
