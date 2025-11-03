"""
Utilitaires de validation d'environnement pour l'application.
"""

import logging
import os
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class EnvironmentValidationError(Exception):
    """Exception levée en cas d'erreur de validation environnement."""

    pass


def validate_required_env_vars(required_vars: List[str]) -> Tuple[bool, List[str]]:
    """
    Valide que toutes les variables d'environnement requises sont présentes.

    Args:
        required_vars: Liste des noms de variables requises

    Returns:
        Tuple (is_valid, missing_vars) - is_valid=True si toutes présentes, missing_vars liste vars manquantes
    """
    missing = []
    for var_name in required_vars:
        if not os.getenv(var_name):
            missing.append(var_name)

    return len(missing) == 0, missing


def validate_secret_strength(secret: str, min_length: int = 32) -> Tuple[bool, str]:
    """
    Valide la force d'un secret (clé de chiffrement, JWT secret, etc.).

    Args:
        secret: Secret à valider
        min_length: Longueur minimale requise

    Returns:
        Tuple (is_strong, warning_message) - is_strong=True si fort, warning_message message d'avertissement
    """
    if len(secret) < min_length:
        return False, f"Secret trop court (minimum {min_length} caractères recommandé)"

    # Vérifier complexité basique
    has_upper = bool(re.search(r"[A-Z]", secret))
    has_lower = bool(re.search(r"[a-z]", secret))
    has_digit = bool(re.search(r"\d", secret))
    has_special = bool(re.search(r"[^A-Za-z0-9]", secret))

    complexity_count = sum([has_upper, has_lower, has_digit, has_special])

    if complexity_count < 2:
        return (
            False,
            "Secret peu complexe (recommandé: mélange lettres, chiffres, caractères spéciaux)",
        )

    return True, ""


def warn_missing_optional_env_vars(optional_vars: List[str]) -> None:
    """
    Affiche des warnings pour variables d'environnement optionnelles manquantes.

    Args:
        optional_vars: Liste des noms de variables optionnelles à vérifier
    """
    for var_name in optional_vars:
        if not os.getenv(var_name):
            logger.warning(
                f"Variable d'environnement optionnelle manquante: {var_name}"
            )


def validate_database_url(database_url: Optional[str]) -> Tuple[bool, str]:
    """
    Valide le format d'une URL de base de données.

    Args:
        database_url: URL de base de données à valider

    Returns:
        Tuple (is_valid, error_message) - is_valid=True si valide, error_message message d'erreur
    """
    if not database_url:
        return False, "DATABASE_URL manquante"

    # Formats supportés: mysql://, mysql+pymysql://, mysql+mysqlclient://
    valid_patterns = [
        r"^mysql://",
        r"^mysql\+pymysql://",
        r"^mysql\+mysqlclient://",
    ]

    if not any(re.match(pattern, database_url) for pattern in valid_patterns):
        return (
            False,
            f"Format DATABASE_URL invalide (attendu: mysql://... ou mysql+pymysql://...)",
        )

    return True, ""


def validate_environment() -> None:
    """
    Valide l'environnement complet de l'application.

    Vérifie:
    - Variables d'environnement requises
    - Force des secrets
    - Format URL base de données

    Raises:
        EnvironmentValidationError: Si validation échoue
    """
    errors = []
    warnings = []

    # Variables requises selon environnement
    is_production = (
        os.getenv("FLASK_ENV") == "production"
        or os.getenv("ENVIRONMENT") == "production"
    )

    required_vars = ["DATABASE_URL"]
    if is_production:
        required_vars.extend(["JWT_SECRET_KEY", "API_KEYS_ENCRYPTION_KEY"])

    # Vérifier variables requises
    is_valid, missing_vars = validate_required_env_vars(required_vars)
    if not is_valid:
        errors.append(
            f"Variables d'environnement requises manquantes: {', '.join(missing_vars)}"
        )

    # Valider DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        db_valid, db_error = validate_database_url(database_url)
        if not db_valid:
            errors.append(db_error)

    # Valider force secrets en production
    if is_production:
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        if jwt_secret:
            is_strong, warning = validate_secret_strength(jwt_secret, min_length=32)
            if not is_strong:
                warnings.append(f"JWT_SECRET_KEY: {warning}")

        encryption_key = os.getenv("API_KEYS_ENCRYPTION_KEY")
        if encryption_key:
            is_strong, warning = validate_secret_strength(encryption_key, min_length=32)
            if not is_strong:
                warnings.append(f"API_KEYS_ENCRYPTION_KEY: {warning}")

    # Variables optionnelles avec warnings
    optional_vars = ["FLASK_ENV", "FLASK_DEBUG", "REDIS_URL", "LOG_LEVEL"]
    warn_missing_optional_env_vars(optional_vars)

    # Afficher warnings
    for warning in warnings:
        logger.warning(f"⚠️  Validation environnement: {warning}")

    # Lever exception si erreurs critiques
    if errors:
        error_msg = "Erreurs de validation environnement:\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        logger.error(error_msg)
        raise EnvironmentValidationError(error_msg)
