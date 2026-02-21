import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = None
engine = None
SessionLocal = None
Base = declarative_base()


def init_db():
    global SQLALCHEMY_DATABASE_URL, engine, SessionLocal
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "database", "scoutslens.db"
    )
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_config():
    env = os.getenv("ENV", "dev")
    assert env in ["dev", "prod"], f"Invalid ENV: {env}"

    frontend_domains = os.getenv("FRONTEND_DOMAINS", "").split(",")
    frontend_domains = [domain.strip() for domain in frontend_domains if domain.strip()]

    return {
        "env": env,
        "frontend_domains": frontend_domains,
    }
