from __future__ import annotations

from pydantic import AnyUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Single source of truth for configuration.

    Contract invariants:
    - DATABASE_URL is the only DB connection key.
    - In V2, control plane must be Postgres-only (no SQLite fallback).
    - No module besides settings may read env vars.
    - DATABASE_URL must be present and non-empty (fail fast).
    """

    model_config = SettingsConfigDict(env_file=None, case_sensitive=False)

    app_env: str = Field(alias="APP_ENV")
    database_url: AnyUrl = Field(alias="DATABASE_URL")
    secret_key: str = Field(alias="SECRET_KEY")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    db_schema: str = Field(default="public", alias="DB_SCHEMA")
    db_require_postgres: bool = Field(default=True, alias="DB_REQUIRE_POSTGRES")

    # Admin bootstrap (optional)
    admin_username: str | None = Field(default=None, alias="ADMIN_USERNAME")
    admin_password: str | None = Field(default=None, alias="ADMIN_PASSWORD")
    admin_email: str | None = Field(default=None, alias="ADMIN_EMAIL")
    bootstrap_token: str | None = Field(default=None, alias="BOOTSTRAP_TOKEN")

    # Feature flags
    nearsight_enabled: bool = Field(default=False, alias="NEARSIGHT_ENABLED")
    captorator_enabled: bool = Field(default=False, alias="CAPTORATOR_ENABLED")
    jobs_enabled: bool = Field(default=False, alias="JOBS_ENABLED")
    notion_enabled: bool = Field(default=False, alias="NOTION_ENABLED")
    runner_enabled: bool = Field(default=False, alias="RUNNER_ENABLED")
    metrics_enabled: bool = Field(default=False, alias="FEATURE_METRICS")

    # Ops API key (required in production)
    ops_api_key: str | None = Field(default=None, alias="OPS_API_KEY")

    # Runner integration
    runner_url: str | None = Field(default=None, alias="RUNNER_URL")
    runner_token_outbound: str | None = Field(default=None, alias="RUNNER_TOKEN_OUTBOUND")
    control_plane_base_url: str | None = Field(default=None, alias="CONTROL_PLANE_BASE_URL")

    # CORS
    cors_origins: str | None = Field(default=None, alias="CORS_ORIGINS")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: AnyUrl | str) -> AnyUrl | str:
        """V2 contract: DATABASE_URL must be present and PostgreSQL-only."""
        url_str = str(v)
        if not url_str or url_str.strip() == "":
            raise ValueError("DATABASE_URL is required and cannot be empty")
        if url_str.startswith("sqlite"):
            raise ValueError("V2 requires PostgreSQL. SQLite is not allowed. DATABASE_URL must start with postgresql://")
        if not url_str.startswith(("postgresql://", "postgres://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string (postgresql:// or postgres://)")
        return v


settings = Settings()  # validated on import
