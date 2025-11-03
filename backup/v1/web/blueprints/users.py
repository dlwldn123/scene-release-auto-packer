"""
Blueprint pour la gestion des utilisateurs (admin uniquement).
"""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from web.auth import admin_required
from web.database import db
from web.models.user import User, UserRole
from web.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema

logger = logging.getLogger(__name__)

users_bp = Blueprint("users", __name__)


@users_bp.get("")
@jwt_required()
@admin_required
def list_users():
    """
    Liste tous les utilisateurs (admin uniquement).

    GET /api/users

    Returns:
        Liste des utilisateurs
    """
    try:
        # Pagination
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        query = User.query
        total = query.count()
        users = query.limit(limit).offset(offset).all()

        logger.info(f"Utilisateurs trouvés: {len(users)}/{total}")

        schema = UserSchema(many=True)
        users_data = schema.dump(users)

        return (
            jsonify(
                {
                    "success": True,
                    "users": users_data,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur liste utilisateurs: {e}", exc_info=True)
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Erreur lors de la récupération des utilisateurs: {str(e)}",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@users_bp.get("/<int:user_id>")
@jwt_required()
@admin_required
def get_user(user_id: int):
    """
    Récupère un utilisateur spécifique (admin uniquement).

    GET /api/users/<user_id>

    Returns:
        Détails de l'utilisateur
    """
    try:
        user = User.query.get(user_id)

        if not user:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Utilisateur introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        schema = UserSchema()
        return (
            jsonify(
                {
                    "success": True,
                    "user": schema.dump(user),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur récupération utilisateur: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération de l'utilisateur",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@users_bp.post("")
@jwt_required()
@admin_required
def create_user():
    """
    Crée un nouvel utilisateur (admin uniquement).

    POST /api/users
    Body: {"username": "...", "password": "...", "email": "...", "role": "admin|operator"}

    Returns:
        Utilisateur créé
    """
    try:
        data = request.get_json() or {}
        schema = UserCreateSchema()
        payload = schema.load(data)

        # Vérifier si username existe déjà
        existing_user = User.query.filter_by(username=payload["username"]).first()
        if existing_user:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Nom d'utilisateur déjà utilisé",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Créer utilisateur
        user = User(
            username=payload["username"],
            email=payload.get("email"),
            role=UserRole(payload.get("role", "operator")),
        )
        user.set_password(payload["password"])

        db.session.add(user)
        db.session.commit()

        schema = UserSchema(exclude=["password_hash"])
        return (
            jsonify(
                {
                    "success": True,
                    "user": schema.dump(user),
                }
            ),
            201,
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
    except ValueError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Rôle invalide: {str(e)}",
                    "error_type": "ValidationError",
                }
            ),
            400,
        )
    except Exception as e:
        logger.error(f"Erreur création utilisateur: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la création de l'utilisateur",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@users_bp.put("/<int:user_id>")
@jwt_required()
@admin_required
def update_user(user_id: int):
    """
    Met à jour un utilisateur (admin uniquement).

    PUT /api/users/<user_id>
    Body: {"email": "...", "role": "admin|operator", "password": "..." (optionnel)}

    Returns:
        Utilisateur mis à jour
    """
    try:
        user = User.query.get(user_id)

        if not user:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Utilisateur introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        data = request.get_json() or {}
        schema = UserUpdateSchema()
        payload = schema.load(data)

        # Mettre à jour champs
        if "email" in payload:
            user.email = payload["email"]

        if "role" in payload:
            try:
                user.role = UserRole(payload["role"])
            except ValueError:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Rôle invalide",
                            "error_type": "ValidationError",
                        }
                    ),
                    400,
                )

        if "password" in payload and payload["password"]:
            user.set_password(payload["password"])

        db.session.commit()

        schema = UserSchema()
        return (
            jsonify(
                {
                    "success": True,
                    "user": schema.dump(user),
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
        logger.error(f"Erreur mise à jour utilisateur: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la mise à jour de l'utilisateur",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@users_bp.delete("/<int:user_id>")
@jwt_required()
@admin_required
def delete_user(user_id: int):
    """
    Supprime un utilisateur (admin uniquement).

    DELETE /api/users/<user_id>

    Returns:
        Confirmation suppression
    """
    try:
        current_user_id = get_jwt_identity()

        if int(user_id) == int(current_user_id):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Vous ne pouvez pas supprimer votre propre compte",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        user = User.query.get(user_id)

        if not user:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Utilisateur introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        db.session.delete(user)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Utilisateur supprimé",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur suppression utilisateur: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la suppression de l'utilisateur",
                    "error_type": "ServerError",
                }
            ),
            500,
        )
