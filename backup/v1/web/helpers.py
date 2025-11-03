"""
Helpers utilitaires pour réponses JSON standardisées et gestion erreurs.
"""

import logging
from typing import Any, Optional, Tuple

from flask import Response, jsonify
from marshmallow import Schema, ValidationError

logger = logging.getLogger(__name__)


def json_response(
    success: bool,
    data: Any = None,
    error: Optional[str] = None,
    error_type: Optional[str] = None,
    details: Optional[dict] = None,
    status_code: int = 200,
) -> Tuple[Response, int]:
    """
    Helper pour réponses JSON standardisées.

    Args:
        success: True si succès, False sinon
        data: Données à retourner (dict, list, etc.)
        error: Message d'erreur si échec
        error_type: Type d'erreur (ValidationError, NotFound, etc.)
        details: Détails supplémentaires (ex: erreurs validation)
        status_code: Code HTTP

    Returns:
        Tuple (Response, status_code)
    """
    response = {"success": success}

    if success:
        if data is not None:
            if isinstance(data, dict):
                response.update(data)
            else:
                response["data"] = data
    else:
        if error:
            response["error"] = error
        if error_type:
            response["error_type"] = error_type
        if details:
            response["details"] = details

    return jsonify(response), status_code


def log_error(
    logger_instance: logging.Logger,
    error: Exception,
    context: str = "",
    exc_info: bool = True,
) -> None:
    """
    Helper pour logging erreurs standardisé.

    Args:
        logger_instance: Logger à utiliser
        error: Exception à logger
        context: Contexte où l'erreur s'est produite
        exc_info: Inclure traceback complet
    """
    context_str = f"[{context}] " if context else ""
    logger_instance.error(f"{context_str}Erreur: {error}", exc_info=exc_info)


def get_json_or_fail(schema: Schema, data: Optional[dict] = None) -> dict:
    """
    Helper pour validation JSON avec gestion erreurs.

    Args:
        schema: Schéma Marshmallow pour validation
        data: Données JSON à valider (None = depuis request.get_json())

    Returns:
        Données validées

    Raises:
        ValidationError: Si validation échoue
    """
    from flask import request

    if data is None:
        data = request.get_json() or {}

    try:
        return schema.load(data)
    except ValidationError as e:
        raise ValidationError(
            f"Données de validation invalides: {e.messages}", field="data", value=data
        ) from e


def get_current_user_id() -> int:
    """
    Récupère l'ID de l'utilisateur courant depuis JWT.

    Returns:
        ID utilisateur (int)

    Raises:
        ValueError: Si aucun utilisateur authentifié
    """
    from flask_jwt_extended import get_jwt_identity

    identity = get_jwt_identity()
    if identity is None:
        raise ValueError("Aucun utilisateur authentifié")

    # Convertir en int si nécessaire
    return int(identity) if isinstance(identity, str) else identity
