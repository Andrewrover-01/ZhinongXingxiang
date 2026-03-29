from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "sqlite:///./zhinong.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Cache TTL in seconds.  Default: 1 hour (3600 s) for RAG results.
    CACHE_TTL: int = 3600

    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB

    APP_ENV: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_EMBEDDING_BACKEND: str = "default"  # default | openai | mock
    OPENAI_API_KEY: Optional[str] = None
    QWEN_API_KEY: Optional[str] = None


settings = Settings()
