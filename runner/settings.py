from __future__ import annotations

from pydantic import AnyUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunnerSettings(BaseSettings):
    """Runner service settings.

    V2 contract: Runner requires DATABASE_URL and RUNNER_TOKEN.
    """

    model_config = SettingsConfigDict(env_file=None, case_sensitive=False)

    runner_token: str = Field(alias="RUNNER_TOKEN")
    database_url: AnyUrl = Field(alias="DATABASE_URL")

    runner_allowlist: str | None = Field(
        default="nearsight_collect_refresh,captorator_compose,metrics_refresh",
        alias="RUNNER_ALLOWLIST",
    )
    runner_db_schema: str = Field(default="public", alias="RUNNER_DB_SCHEMA")
    runner_allowed_origins: str | None = Field(default=None, alias="RUNNER_ALLOWED_ORIGINS")

    clawdbot_bin: str | None = Field(default=None, alias="CLAWDBOT_BIN")
    clawdbot_workdir: str | None = Field(default=None, alias="CLAWDBOT_WORKDIR")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: AnyUrl | str) -> AnyUrl | str:
        """V2 contract: DATABASE_URL must be PostgreSQL."""
        url_str = str(v)
        if not url_str or url_str.strip() == "":
            raise ValueError("DATABASE_URL is required and cannot be empty")
        if url_str.startswith("sqlite"):
            raise ValueError("V2 runner requires PostgreSQL. SQLite is not allowed.")
        if not url_str.startswith(("postgresql://", "postgres://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v


runner_settings = RunnerSettings()
