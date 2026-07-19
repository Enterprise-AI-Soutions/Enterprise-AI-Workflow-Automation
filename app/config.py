"""Application configuration via Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────────────────
    APP_NAME: str = "Enterprise AI Workflow Automation"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    SECRET_KEY: str = "changeme-in-production-use-a-long-random-string"
    ALLOWED_ORIGINS: List[str] = ["*"]

    # ── Server ────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./enterprise_ai.db"

    # ── Anthropic / Claude ────────────────────────────────────────────────
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    CLAUDE_MAX_TOKENS: int = 4096

    # ── Google Workspace ──────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
    GOOGLE_CREDENTIALS_FILE: Optional[str] = None  # path to credentials.json
    GOOGLE_TOKEN_FILE: Optional[str] = "token.json"

    # ── Airtable ──────────────────────────────────────────────────────────
    AIRTABLE_API_KEY: Optional[str] = None
    AIRTABLE_BASE_ID: Optional[str] = None

    # ── n8n ───────────────────────────────────────────────────────────────
    N8N_BASE_URL: str = "http://localhost:5678"
    N8N_API_KEY: Optional[str] = None
    N8N_WEBHOOK_URL: Optional[str] = None

    # ── Redis (optional caching) ──────────────────────────────────────────
    REDIS_URL: Optional[str] = None

    # ── Logging ───────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json | text

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def claude_enabled(self) -> bool:
        return bool(self.ANTHROPIC_API_KEY)

    @property
    def google_enabled(self) -> bool:
        return bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET)

    @property
    def airtable_enabled(self) -> bool:
        return bool(self.AIRTABLE_API_KEY)

    @property
    def n8n_enabled(self) -> bool:
        return bool(self.N8N_API_KEY)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
