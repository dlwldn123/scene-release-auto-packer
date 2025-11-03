"""
Utilitaires pour la gestion des rôles et permissions.
"""

from functools import wraps
from typing import Any, Callable

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from web.models.user import UserRole


def admin_required(f: Callable) -> Callable:
    """
    Décorateur pour exiger le rôle admin.

    Args:
        f: Fonction à décorer

    Returns:
        Fonction décorée avec vérification admin
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        verify_jwt_in_request()
        claims = get_jwt()
        user_role = claims.get("role")

        if user_role != UserRole.ADMIN.value:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Accès refusé: rôle admin requis",
                        "error_type": "ForbiddenError",
                    }
                ),
                403,
            )

        return f(*args, **kwargs)

    return decorated_function


def operator_or_admin_required(f: Callable) -> Callable:
    """
    Décorateur pour exiger le rôle operator ou admin.

    Args:
        f: Fonction à décorer

    Returns:
        Fonction décorée avec vérification rôle
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        verify_jwt_in_request()
        claims = get_jwt()
        user_role = claims.get("role")

        if user_role not in (UserRole.ADMIN.value, UserRole.OPERATOR.value):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Accès refusé: authentification requise",
                        "error_type": "ForbiddenError",
                    }
                ),
                403,
            )

        return f(*args, **kwargs)

    return decorated_function
