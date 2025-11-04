"""Flask configuration classes."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class BaseConfig:
    """Base configuration class."""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = False
    TESTING = False
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "mysql+pymysql://user:password@localhost/ebook_scene_packer"
    )

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400")
    )  # 24h
    JWT_REFRESH_TOKEN_EXPIRES = int(
        os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "604800")
    )  # 7 days
    JWT_ALGORITHM = "HS256"

    # Caching
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "true").lower() == "true"
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")

    # API Keys Encryption
    API_KEYS_ENCRYPTION_KEY = os.getenv("API_KEYS_ENCRYPTION_KEY", "")


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_ECHO = True
    CACHE_DEFAULT_TIMEOUT = 60


class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_ECHO = False
    CACHE_DEFAULT_TIMEOUT = 300


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    JWT_SECRET_KEY = "test-secret-key"
    WTF_CSRF_ENABLED = False


def get_config(config_name: str | None = None) -> type[BaseConfig]:
    """Get configuration class by name.

    Args:
        config_name: Configuration name ('development', 'production', 'testing').

    Returns:
        Configuration class.
    """
    config_map: dict[str, type[BaseConfig]] = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    return config_map.get(config_name, DevelopmentConfig)
