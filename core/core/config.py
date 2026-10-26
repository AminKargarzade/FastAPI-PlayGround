from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str

    # Keep the real secret in .env, not in source code.
    JWT_SECRET_KEY: str

    # False for local HTTP development; True in production with HTTPS.
    COOKIE_SECURE: bool = True

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
