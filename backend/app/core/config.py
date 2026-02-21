import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """应用配置类 - 使用纯Python实现，避免Pydantic的复杂问题"""

    def __init__(self):
        self.env = os.getenv("ENV", "dev")
        self.secret_key = os.getenv("SECRET_KEY", "")
        self.access_token_expire_days = 7
        self.algorithm = "HS256"

        if not self.secret_key:
            raise ValueError("SECRET_KEY environment variable is not set")

        frontend_domains_str = os.getenv("FRONTEND_DOMAINS", "")
        self.frontend_domains = [
            domain.strip()
            for domain in frontend_domains_str.split(",")
            if domain.strip()
        ]

        db_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "database",
            "scoutslens.db",
        )
        self.database_url = f"sqlite:///{db_path}"


settings = Settings()
