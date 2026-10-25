from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str

    # Keep the real secret in .env, not in source code.
    JWT_SECRET_KEY: str

    # False for local HTTP development; True in production with HTTPS.
    COOKIE_SECURE: bool = True

    model_config = SettingsConfigDict(
        env_file="core/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
