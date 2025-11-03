"""
Blueprint pour l'authentification JWT.
"""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError

from web.database import db
from web.models.user import User
from web.schemas.auth import LoginSchema

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    """
    Authentification et génération du token JWT.

    POST /api/auth/login
    Body: {"username": "admin", "password": "password"}

    Returns:
        {"success": True, "token": "...", "user_id": 1, "role": "admin", "expires_in": 86400}
    """
    try:
        data = request.get_json() or {}
        schema = LoginSchema()
        payload = schema.load(data)

        username = payload["username"]
        password = payload["password"]

        # Rechercher utilisateur
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Nom d'utilisateur ou mot de passe incorrect",
                        "error_type": "AuthenticationError",
                    }
                ),
                401,
            )

        # Mettre à jour dernière connexion
        user.update_last_login()

        # Créer token JWT
        additional_claims = {
            "role": user.role.value,
            "user_id": user.id,
        }
        access_token = create_access_token(
            identity=str(user.id),  # JWT identity doit être une string
            additional_claims=additional_claims,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "token": access_token,
                    "user_id": user.id,
                    "role": user.role.value,
                    "expires_in": 86400,  # 24h
                }
            ),
            200,
        )

    except ValidationError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Données de validation invalides",
                    "error_type": "ValidationError",
                    "details": e.messages,
                }
            ),
            400,
        )
    except Exception as e:
        logger.error(f"Erreur authentification: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de l'authentification",
                    "error_type": "AuthenticationError",
                }
            ),
            500,
        )


@auth_bp.post("/logout")
@jwt_required()
def logout():
    """
    Logout (invalide le token côté client).

    POST /api/auth/logout

    Note: JWT étant stateless, l'invalidation réelle nécessiterait
    une blacklist de tokens. Pour MVP, on retourne simplement succès.
    """
    return (
        jsonify(
            {
                "success": True,
                "message": "Déconnexion réussie",
            }
        ),
        200,
    )


@auth_bp.post("/refresh")
@jwt_required()
def refresh():
    """
    Rafraîchir le token JWT.

    POST /api/auth/refresh

    Returns:
        Nouveau token avec mêmes claims
    """
    current_user_id = get_jwt_identity()
    claims = get_jwt()

    user = User.query.get(int(current_user_id))  # Convertir string en int pour query
    if not user:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Utilisateur introuvable",
                    "error_type": "AuthenticationError",
                }
            ),
            401,
        )

    # Créer nouveau token
    additional_claims = {
        "role": user.role.value,
        "user_id": user.id,
    }
    access_token = create_access_token(
        identity=str(user.id),  # JWT identity doit être une string
        additional_claims=additional_claims,
    )

    return (
        jsonify(
            {
                "success": True,
                "token": access_token,
                "expires_in": 86400,
            }
        ),
        200,
    )


@auth_bp.get("/me")
@jwt_required()
def me():
    """
    Retourne les informations de l'utilisateur courant.

    GET /api/auth/me

    Returns:
        {"success": True, "user": {"id": 1, "username": "admin", "role": "admin", "email": "..."}}
    """
    current_user_id = get_jwt_identity()
    claims = get_jwt()

    user = User.query.get(int(current_user_id))  # Convertir string en int pour query
    if not user:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Utilisateur introuvable",
                    "error_type": "AuthenticationError",
                }
            ),
            401,
        )

    return (
        jsonify(
            {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.value,
                    "email": user.email,
                    "last_login": (
                        user.last_login.isoformat() if user.last_login else None
                    ),
                },
            }
        ),
        200,
    )
