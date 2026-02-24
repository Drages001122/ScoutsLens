from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Settings(BaseSettings):
    ENV: str = Field(default="dev", description="Environment: dev, staging, prod")
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this", description="Secret key for JWT"
    )

    FRONTEND_DOMAINS: List[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed frontend domains for CORS",
    )

    DATABASE_URL: str = Field(
        default="sqlite:///database/scoutslens.db",
        description="Database connection URL",
    )

    API_HOST: str = Field(default="127.0.0.1", description="API server host")
    API_PORT: int = Field(default=8000, description="API server port")

    WORKERS: int = Field(default=4, description="Number of worker processes")
    RELOAD: bool = Field(default=False, description="Enable auto-reload in development")

    LOG_LEVEL: str = Field(
        default="info", description="Logging level: debug, info, warning, error"
    )

    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True, description="Allow credentials in CORS"
    )
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["*"], description="Allowed HTTP methods for CORS"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"], description="Allowed headers for CORS"
    )

    MIDDLEWARE_CORS: bool = Field(default=True, description="Enable CORS middleware")
    MIDDLEWARE_GZIP: bool = Field(default=True, description="Enable GZIP compression")
    MIDDLEWARE_TRUSTED_HOST: bool = Field(
        default=True, description="Enable trusted host middleware"
    )

    ASYNC_DB: bool = Field(default=True, description="Use async database operations")

    MAX_REQUEST_SIZE: int = Field(
        default=10 * 1024 * 1024, description="Max request size in bytes"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()


# 数据库配置
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)


def get_settings() -> Settings:
    return settings


class MiddlewareConfig:
    @staticmethod
    def get_cors_middleware_config():
        return {
            "allow_origins": settings.FRONTEND_DOMAINS,
            "allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
            "allow_methods": settings.CORS_ALLOW_METHODS,
            "allow_headers": settings.CORS_ALLOW_HEADERS,
        }

    @staticmethod
    def get_gzip_middleware_config():
        return {
            "minimum_size": 1000,
        }

    @staticmethod
    def get_trusted_hosts_config():
        return {
            "allowed_hosts": ["*"] if settings.ENV == "dev" else [settings.API_HOST],
        }


class AsyncConfig:
    @staticmethod
    def get_uvicorn_config():
        return {
            "host": settings.API_HOST,
            "port": settings.API_PORT,
            "workers": settings.WORKERS if settings.ENV == "prod" else 1,
            "reload": settings.RELOAD,
            "log_level": settings.LOG_LEVEL,
            "access_log": True,
            "use_colors": True,
            "loop": "uvloop",
            "http": "httptools",
        }

    @staticmethod
    def get_database_config():
        return {
            "async_mode": settings.ASYNC_DB,
            "check_same_thread": False,
            "echo": settings.LOG_LEVEL == "debug",
        }
