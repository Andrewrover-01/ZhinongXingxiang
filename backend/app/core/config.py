from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_WEAK_DEFAULT_SECRET = "dev-secret-key-change-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "sqlite:///./zhinong.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Cache TTL in seconds.  Default: 1 hour (3600 s) for RAG results.
    CACHE_TTL: int = 3600

    SECRET_KEY: str = _WEAK_DEFAULT_SECRET  # Must be overridden via SECRET_KEY env var in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour; use shorter TTL to limit stolen-token exposure

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

    APP_ENV: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_EMBEDDING_BACKEND: str = "default"  # default | openai | mock
    OPENAI_API_KEY: Optional[str] = None
    QWEN_API_KEY: Optional[str] = None

    @model_validator(mode="after")
    def _require_strong_secret_key_in_production(self) -> "Settings":
        if self.APP_ENV == "production" and self.SECRET_KEY == _WEAK_DEFAULT_SECRET:
            raise ValueError(
                "SECRET_KEY must be set to a strong random value in production. "
                "Set the SECRET_KEY environment variable to at least 32 random bytes."
            )
        if self.APP_ENV == "production" and self.DATABASE_URL.startswith("sqlite"):
            raise ValueError(
                "SQLite is not suitable for production use. "
                "Set the DATABASE_URL environment variable to a PostgreSQL or other "
                "production-grade database connection string."
            )
        return self


settings = Settings()
