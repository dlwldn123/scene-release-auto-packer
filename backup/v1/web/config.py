"""
Configuration améliorée avec validation de type.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional


class BaseConfig:
    """Configuration de base Flask."""

    DEBUG = False
    TESTING = False
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///test.db"
    )  # SQLite par défaut pour tests

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400")
    )  # 24h
    JWT_ALGORITHM = "HS256"

    # API Keys Encryption
    API_KEYS_ENCRYPTION_KEY = os.getenv("API_KEYS_ENCRYPTION_KEY", "")


class DevConfig(BaseConfig):
    """Configuration pour l'environnement de développement."""

    DEBUG = True


class ProdConfig(BaseConfig):
    """Configuration pour l'environnement de production."""

    DEBUG = False
    CACHE_DEFAULT_TIMEOUT = 300


def get_config_from_env() -> type:
    """
    Retourne la classe de configuration selon l'environnement.

    Returns:
        Classe de configuration (DevConfig ou ProdConfig)
    """
    env = os.getenv("APP_ENV", os.getenv("FLASK_ENV", "development")).lower()
    if env in ("prod", "production"):
        return ProdConfig
    return DevConfig


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Valide la structure de configuration.

    Args:
        config: Dictionnaire de configuration

    Returns:
        True si configuration valide

    Raises:
        ValueError: Si configuration invalide
    """
    required_sections = ["api", "nfo", "rar", "zip", "validation"]

    for section in required_sections:
        if section not in config:
            raise ValueError(f"Section de configuration manquante: {section}")

    # Validation section API
    api_config = config.get("api", {})
    if not isinstance(api_config.get("timeout", 10), (int, float)):
        raise ValueError("api.timeout doit être un nombre")

    # Validation section ZIP
    zip_config = config.get("zip", {})
    if not isinstance(zip_config.get("allowed_sizes", []), list):
        raise ValueError("zip.allowed_sizes doit être une liste")

    return True
