"""
Blueprint pour la gestion des préférences utilisateur et globales.
"""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from web.auth import admin_required, operator_or_admin_required
from web.database import db
from web.helpers import get_current_user_id
from web.models.preference import GlobalPreference, UserPreference
from web.models.user import User
from web.schemas.preference import PreferenceSchema

logger = logging.getLogger(__name__)

preferences_bp = Blueprint("preferences", __name__)


@preferences_bp.get("")
@jwt_required()
@operator_or_admin_required
def list_user_preferences():
    """
    Liste les préférences de l'utilisateur courant.

    GET /api/preferences

    Returns:
        Liste des préférences utilisateur
    """
    try:
        current_user_id = get_current_user_id()

        preferences = UserPreference.query.filter_by(user_id=current_user_id).all()

        schema = PreferenceSchema(many=True)
        preferences_data = schema.dump(preferences)

        return (
            jsonify(
                {
                    "success": True,
                    "preferences": preferences_data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur liste préférences: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération des préférences",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@preferences_bp.get("/<preference_key>")
@jwt_required()
@operator_or_admin_required
def get_preference(preference_key: str):
    """
    Récupère une préférence spécifique (user puis global fallback).

    GET /api/preferences/<key>

    Returns:
        Préférence avec source (user/global)
    """
    try:
        current_user_id = get_current_user_id()

        # Chercher préférence utilisateur
        user_pref = UserPreference.query.filter_by(
            user_id=current_user_id,
            preference_key=preference_key,
        ).first()

        if user_pref:
            schema = PreferenceSchema()
            return (
                jsonify(
                    {
                        "success": True,
                        "preference": schema.dump(user_pref),
                        "source": "user",
                    }
                ),
                200,
            )

        # Fallback: préférence globale
        global_pref = GlobalPreference.query.filter_by(
            preference_key=preference_key,
        ).first()

        if global_pref:
            schema = PreferenceSchema()
            return (
                jsonify(
                    {
                        "success": True,
                        "preference": schema.dump(global_pref),
                        "source": "global",
                    }
                ),
                200,
            )

        return (
            jsonify(
                {
                    "success": False,
                    "error": "Préférence introuvable",
                    "error_type": "NotFound",
                }
            ),
            404,
        )

    except Exception as e:
        logger.error(f"Erreur récupération préférence: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération de la préférence",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@preferences_bp.post("")
@jwt_required()
@operator_or_admin_required
def create_preference():
    """
    Crée ou met à jour une préférence utilisateur.

    POST /api/preferences
    Body: {"key": "...", "value": {...}}

    Returns:
        Préférence créée/mise à jour
    """
    try:
        current_user_id = get_current_user_id()
        data = request.get_json() or {}

        schema = PreferenceSchema()
        payload = schema.load(data)

        preference_key = payload["preference_key"]
        preference_value = payload["preference_value"]

        # Chercher préférence existante
        user_pref = UserPreference.query.filter_by(
            user_id=current_user_id,
            preference_key=preference_key,
        ).first()

        if user_pref:
            user_pref.set_value(preference_value)
        else:
            user_pref = UserPreference(
                user_id=current_user_id,
                preference_key=preference_key,
                preference_value=preference_value,
            )
            db.session.add(user_pref)

        db.session.commit()

        schema = PreferenceSchema()
        return (
            jsonify(
                {
                    "success": True,
                    "preference": schema.dump(user_pref),
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
        logger.error(f"Erreur création préférence: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la création de la préférence",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@preferences_bp.put("/<preference_key>")
@jwt_required()
@operator_or_admin_required
def update_preference(preference_key: str):
    """
    Met à jour une préférence utilisateur.

    PUT /api/preferences/<key>
    Body: {"value": {...}}

    Returns:
        Préférence mise à jour
    """
    try:
        current_user_id = get_current_user_id()
        data = request.get_json() or {}

        user_pref = UserPreference.query.filter_by(
            user_id=current_user_id,
            preference_key=preference_key,
        ).first()

        if not user_pref:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Préférence introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        preference_value = data.get("value")
        if preference_value is None:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Valeur requise",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        user_pref.set_value(preference_value)
        db.session.commit()

        schema = PreferenceSchema()
        return (
            jsonify(
                {
                    "success": True,
                    "preference": schema.dump(user_pref),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur mise à jour préférence: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la mise à jour de la préférence",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@preferences_bp.delete("/<preference_key>")
@jwt_required()
@operator_or_admin_required
def delete_preference(preference_key: str):
    """
    Supprime une préférence utilisateur.

    DELETE /api/preferences/<key>

    Returns:
        Confirmation suppression
    """
    try:
        current_user_id = get_current_user_id()

        user_pref = UserPreference.query.filter_by(
            user_id=current_user_id,
            preference_key=preference_key,
        ).first()

        if not user_pref:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Préférence introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        db.session.delete(user_pref)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Préférence supprimée",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur suppression préférence: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la suppression de la préférence",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@preferences_bp.get("/global")
@jwt_required()
@admin_required
def list_global_preferences():
    """
    Liste les préférences globales (admin uniquement).

    GET /api/preferences/global

    Returns:
        Liste des préférences globales
    """
    try:
        preferences = GlobalPreference.query.all()

        schema = PreferenceSchema(many=True)
        preferences_data = schema.dump(preferences)

        return (
            jsonify(
                {
                    "success": True,
                    "preferences": preferences_data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur liste préférences globales: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération des préférences globales",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@preferences_bp.post("/global")
@jwt_required()
@admin_required
def create_global_preference():
    """
    Crée ou met à jour une préférence globale (admin uniquement).

    POST /api/preferences/global
    Body: {"key": "...", "value": {...}}

    Returns:
        Préférence globale créée/mise à jour
    """
    try:
        data = request.get_json() or {}

        preference_key = data.get("key")
        preference_value = data.get("value")

        if not preference_key or preference_value is None:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Clé et valeur requises",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        # Chercher préférence existante
        global_pref = GlobalPreference.query.filter_by(
            preference_key=preference_key,
        ).first()

        if global_pref:
            global_pref.set_value(preference_value)
        else:
            global_pref = GlobalPreference(
                preference_key=preference_key,
                preference_value=preference_value,
            )
            db.session.add(global_pref)

        db.session.commit()

        schema = PreferenceSchema()
        return (
            jsonify(
                {
                    "success": True,
                    "preference": schema.dump(global_pref),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur création préférence globale: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la création de la préférence globale",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@preferences_bp.post("/export")
@jwt_required()
@operator_or_admin_required
def export_preferences():
    """
    Exporte les préférences utilisateur en JSON.

    POST /api/preferences/export

    Returns:
        JSON avec toutes les préférences utilisateur
    """
    try:
        current_user_id = get_current_user_id()

        preferences = UserPreference.query.filter_by(user_id=current_user_id).all()

        preferences_data = {
            pref.preference_key: pref.get_value() for pref in preferences
        }

        return (
            jsonify(
                {
                    "success": True,
                    "preferences": preferences_data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur export préférences: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de l'export des préférences",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@preferences_bp.post("/import")
@jwt_required()
@operator_or_admin_required
def import_preferences():
    """
    Importe des préférences depuis JSON.

    POST /api/preferences/import
    Body: {"preferences": {"key1": {...}, "key2": {...}}}

    Returns:
        Confirmation import
    """
    try:
        current_user_id = get_current_user_id()
        data = request.get_json() or {}

        preferences_data = data.get("preferences", {})

        if not isinstance(preferences_data, dict):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": 'Format invalide. Attendu: {"preferences": {"key": {...}}}',
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        imported_count = 0

        for preference_key, preference_value in preferences_data.items():
            user_pref = UserPreference.query.filter_by(
                user_id=current_user_id,
                preference_key=preference_key,
            ).first()

            if user_pref:
                user_pref.set_value(preference_value)
            else:
                user_pref = UserPreference(
                    user_id=current_user_id,
                    preference_key=preference_key,
                    preference_value=preference_value,
                )
                db.session.add(user_pref)

            imported_count += 1

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"{imported_count} préférences importées",
                    "imported_count": imported_count,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur import préférences: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de l'import des préférences",
                    "error_type": "ServerError",
                }
            ),
            500,
        )
