from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{_PROJECT_ROOT}/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    storage_path: Path
    max_file_size: int = 10 * 1024 * 1024 # 10MB
    max_retry_attempts: int = 3
    log_level: str = "INFO"
    demo_user_email: str = "demo@local.test"

settings = Settings()