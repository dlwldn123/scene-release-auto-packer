"""
Blueprint pour la gestion des chemins par groupe et type de release.
"""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from web.auth import admin_required, operator_or_admin_required
from web.database import db
from web.models.preference import GlobalPreference, UserPreference
from web.schemas.paths import PathConfigSchema

logger = logging.getLogger(__name__)

paths_bp = Blueprint("paths", __name__)


def _get_path_key(group: str, release_type: str) -> str:
    """Génère la clé de préférence pour les chemins."""
    return f"paths:{group}:{release_type}"


@paths_bp.get("/<group>/<release_type>")
@jwt_required()
@operator_or_admin_required
def get_path_config(group: str, release_type: str):
    """
    Récupère la configuration de chemin pour un groupe et type de release.

    GET /api/paths/<group>/<release_type>

    Returns:
        Configuration chemin (user puis global fallback)
    """
    try:
        current_user_id = get_jwt_identity()
        preference_key = _get_path_key(group, release_type)

        # Chercher préférence utilisateur
        user_pref = UserPreference.query.filter_by(
            user_id=current_user_id,
            preference_key=preference_key,
        ).first()

        if user_pref:
            return (
                jsonify(
                    {
                        "success": True,
                        "config": user_pref.get_value(),
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
            return (
                jsonify(
                    {
                        "success": True,
                        "config": global_pref.get_value(),
                        "source": "global",
                    }
                ),
                200,
            )

        # Valeur par défaut
        return (
            jsonify(
                {
                    "success": True,
                    "config": {
                        "output_dir": "releases",
                        "destination_dir": None,
                    },
                    "source": "default",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur récupération config chemin: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération de la configuration",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@paths_bp.post("/<group>/<release_type>")
@jwt_required()
@operator_or_admin_required
def set_path_config(group: str, release_type: str):
    """
    Définit la configuration de chemin pour un groupe et type de release.

    POST /api/paths/<group>/<release_type>
    Body: {"output_dir": "...", "destination_dir": "..."}

    Returns:
        Configuration sauvegardée
    """
    try:
        current_user_id = get_jwt_identity()
        preference_key = _get_path_key(group, release_type)
        data = request.get_json() or {}

        schema = PathConfigSchema()
        config = schema.load(data)

        # Chercher préférence existante
        user_pref = UserPreference.query.filter_by(
            user_id=current_user_id,
            preference_key=preference_key,
        ).first()

        if user_pref:
            user_pref.set_value(config)
        else:
            user_pref = UserPreference(
                user_id=current_user_id,
                preference_key=preference_key,
                preference_value=config,
            )
            db.session.add(user_pref)

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "config": config,
                    "message": "Configuration sauvegardée",
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
        logger.error(f"Erreur sauvegarde config chemin: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la sauvegarde",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@paths_bp.get("/groups")
@jwt_required()
@operator_or_admin_required
def list_group_paths():
    """
    Liste toutes les configurations de chemins par groupe.

    GET /api/paths/groups

    Returns:
        Liste des configurations par groupe
    """
    try:
        current_user_id = get_jwt_identity()

        # Récupérer toutes les préférences de chemins utilisateur
        user_prefs = UserPreference.query.filter(
            UserPreference.user_id == current_user_id,
            UserPreference.preference_key.like("paths:%"),
        ).all()

        # Organiser par groupe
        groups = {}
        for pref in user_prefs:
            # Extraire groupe et type depuis la clé "paths:GROUP:TYPE"
            parts = pref.preference_key.split(":", 2)
            if len(parts) == 3:
                group = parts[1]
                release_type = parts[2]

                if group not in groups:
                    groups[group] = {}

                groups[group][release_type] = pref.get_value()

        return (
            jsonify(
                {
                    "success": True,
                    "groups": groups,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur liste chemins groupes: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@paths_bp.post("/groups/<group>/global")
@jwt_required()
@admin_required
def set_global_group_paths(group: str):
    """
    Définit les configurations de chemins globales pour un groupe (admin uniquement).

    POST /api/paths/groups/<group>/global
    Body: {"EBOOK": {"output_dir": "...", "destination_dir": "..."}, "TV": {...}}

    Returns:
        Confirmation
    """
    try:
        data = request.get_json() or {}

        if not isinstance(data, dict):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Format invalide",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        saved_count = 0

        for release_type, config in data.items():
            preference_key = _get_path_key(group, release_type)

            schema = PathConfigSchema()
            validated_config = schema.load(config)

            # Chercher préférence globale existante
            global_pref = GlobalPreference.query.filter_by(
                preference_key=preference_key,
            ).first()

            if global_pref:
                global_pref.set_value(validated_config)
            else:
                global_pref = GlobalPreference(
                    preference_key=preference_key,
                    preference_value=validated_config,
                )
                db.session.add(global_pref)

            saved_count += 1

        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"{saved_count} configurations sauvegardées",
                    "saved_count": saved_count,
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
        logger.error(f"Erreur sauvegarde chemins globaux: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la sauvegarde",
                    "error_type": "ServerError",
                }
            ),
            500,
        )
