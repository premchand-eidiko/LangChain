from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATABASE_URL = "sqlite:///" + str(PROJECT_ROOT / "data" / "production_ai_agent.db")
DEFAULT_UPLOAD_DIR = str(PROJECT_ROOT / "data" / "uploads")
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    database_url: str = DEFAULT_DATABASE_URL
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    upload_dir: str = DEFAULT_UPLOAD_DIR
    search_api_key: str = ""
    llm_api_key: str = ""
    groq_api_key: str = ""
    llm_provider: str = "groq"
    llm_model: str = "openai/gpt-oss-20b"
    jwt_secret: str = "development-only-change-this-secret"
    jwt_algorithm: str = "HS256"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_base_url: str = "https://cloud.langfuse.com"
    langfuse_environment: str = "development"
    langfuse_sample_rate: float = 1.0

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
