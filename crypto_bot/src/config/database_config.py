from __future__ import annotations

"""Database configuration settings."""
from pydantic import BaseSettings, Field


class DatabaseConfig(BaseSettings):
    """Configuration for database connection parameters.

    The settings are designed with high performance in mind and can be
    extended via environment variables. Connection URL uses asyncpg driver.
    """

    database_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/crypto_bot",
        description="Database connection URL",
    )
    pool_size: int = Field(default=10, description="Size of the connection pool")
    max_overflow: int = Field(default=20, description="Maximum overflow connections")
    pool_timeout: int = Field(
        default=30, description="Timeout in seconds for obtaining a connection"
    )
    ssl_mode: str | None = Field(
        default=None,
        description="SSL mode for PostgreSQL. Use 'require' to enforce SSL",
    )


def get_database_config() -> DatabaseConfig:
    """Return a configuration instance."""

    return DatabaseConfig()
