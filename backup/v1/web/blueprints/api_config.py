"""
Blueprint pour la configuration des APIs externes.
"""

import logging
from typing import Dict

import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from marshmallow import ValidationError

from web.auth import admin_required, operator_or_admin_required
from web.database import db
from web.helpers import get_current_user_id
from web.models.api_config import ApiConfig
from web.models.user import User
from web.schemas.api_config import (
    ApiConfigCreateSchema,
    ApiConfigSchema,
    ApiConfigUpdateSchema,
)

logger = logging.getLogger(__name__)

api_config_bp = Blueprint("api_config", __name__)


def _test_api_connection(api_name: str, api_data: Dict) -> tuple[bool, str]:
    """
    Test connexion à une API externe.

    Args:
        api_name: Nom de l'API (omdb, tvdb, tmdb, openlibrary)
        api_data: Dictionnaire avec clé API

    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        if api_name == "omdb":
            api_key = api_data.get("api_key")
            if not api_key:
                return False, "api_key manquante"

            # Test avec recherche simple
            response = requests.get(
                "http://www.omdbapi.com/",
                params={"apikey": api_key, "t": "test", "type": "movie"},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("Response") == "True":
                    return True, "Connexion OMDb réussie"
                elif "Error" in data:
                    return False, f"Erreur OMDb: {data.get('Error')}"

            return False, f"Erreur OMDb: {response.status_code}"

        elif api_name == "tvdb":
            api_key = api_data.get("api_key")
            user_key = api_data.get("user_key")
            if not api_key or not user_key:
                return False, "api_key et user_key requis pour TVDB"

            # Test authentification TVDB
            auth_response = requests.post(
                "https://api.thetvdb.com/login",
                json={"apikey": api_key, "userkey": user_key},
                timeout=10,
            )

            if auth_response.status_code == 200:
                return True, "Connexion TVDB réussie"
            else:
                return False, f"Erreur TVDB: {auth_response.status_code}"

        elif api_name == "tmdb":
            api_key = api_data.get("api_key")
            if not api_key:
                return False, "api_key manquante"

            # Test avec endpoint configuration
            response = requests.get(
                f"https://api.themoviedb.org/3/configuration",
                params={"api_key": api_key},
                timeout=10,
            )

            if response.status_code == 200:
                return True, "Connexion TMDb réussie"
            else:
                return False, f"Erreur TMDb: {response.status_code}"

        elif api_name == "openlibrary":
            # OpenLibrary n'a pas besoin de clé API
            # Test simple avec recherche
            response = requests.get(
                "https://openlibrary.org/search.json",
                params={"q": "test", "limit": 1},
                timeout=10,
            )

            if response.status_code == 200:
                return True, "Connexion OpenLibrary réussie"
            else:
                return False, f"Erreur OpenLibrary: {response.status_code}"

        else:
            return False, f"API {api_name} non supportée pour test"

    except requests.exceptions.Timeout:
        return False, "Timeout lors du test de connexion"
    except requests.exceptions.RequestException as e:
        return False, f"Erreur réseau: {str(e)}"
    except Exception as e:
        logger.error(f"Erreur test connexion API {api_name}: {e}", exc_info=True)
        return False, f"Erreur inattendue: {str(e)}"


@api_config_bp.get("/apis")
@jwt_required()
@operator_or_admin_required
def list_api_configs():
    """
    Liste les configurations APIs de l'utilisateur.

    GET /api/config/apis

    Returns:
        Liste des configs APIs (admin voit toutes, user voit les siennes)
    """
    try:
        current_user_id = get_current_user_id()
        claims = get_jwt()
        user_role = claims.get("role")

        # Pagination
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        # Admin peut voir toutes les configs, user seulement les siennes
        query = ApiConfig.query
        if user_role != "admin":
            query = query.filter_by(user_id=current_user_id)

        query = query.order_by(ApiConfig.created_at.desc())
        total = query.count()
        api_configs = query.limit(limit).offset(offset).all()

        schema = ApiConfigSchema(many=True)
        configs_data = schema.dump(api_configs)

        return (
            jsonify(
                {
                    "success": True,
                    "api_configs": configs_data,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur liste configs APIs: {e}", exc_info=True)
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


@api_config_bp.get("/apis/<api_name>")
@jwt_required()
@operator_or_admin_required
def get_api_config(api_name: str):
    """
    Récupère une configuration API spécifique.

    GET /api/config/apis/<api_name>

    Returns:
        Config API (sans clé en clair)
    """
    try:
        current_user_id = get_current_user_id()
        claims = get_jwt()
        user_role = claims.get("role")

        # Chercher config
        query = ApiConfig.query.filter_by(api_name=api_name)

        # Admin peut voir toutes, user seulement les siennes
        if user_role != "admin":
            query = query.filter_by(user_id=current_user_id)

        api_config = query.first()

        if not api_config:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Configuration API {api_name} introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        schema = ApiConfigSchema()
        config_data = schema.dump(api_config)

        return (
            jsonify(
                {
                    "success": True,
                    "api_config": config_data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur récupération config API: {e}", exc_info=True)
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


@api_config_bp.post("/apis")
@jwt_required()
@operator_or_admin_required
def create_api_config():
    """
    Crée ou met à jour une configuration API.

    POST /api/config/apis
    Body: {
        "api_name": "omdb",
        "api_data": {"api_key": "..."}
    }

    Returns:
        Config API créée
    """
    try:
        current_user_id = get_current_user_id()
        data = request.get_json() or {}

        schema = ApiConfigCreateSchema()
        payload = schema.load(data)

        api_name = payload["api_name"]
        api_data = payload["api_data"]

        # Chercher config existante
        api_config = ApiConfig.query.filter_by(
            user_id=current_user_id,
            api_name=api_name,
        ).first()

        if api_config:
            # Mettre à jour
            api_config.set_api_key(api_data)
        else:
            # Créer nouvelle
            api_config = ApiConfig(
                user_id=current_user_id,
                api_name=api_name,
            )
            api_config.set_api_key(api_data)
            db.session.add(api_config)

        db.session.commit()

        schema = ApiConfigSchema()
        config_data = schema.dump(api_config)

        return (
            jsonify(
                {
                    "success": True,
                    "api_config": config_data,
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
    except Exception as e:
        logger.error(f"Erreur création config API: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la création",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@api_config_bp.put("/apis/<api_name>")
@jwt_required()
@operator_or_admin_required
def update_api_config(api_name: str):
    """
    Met à jour une configuration API.

    PUT /api/config/apis/<api_name>
    Body: {
        "api_data": {"api_key": "..."}
    }

    Returns:
        Config API mise à jour
    """
    try:
        current_user_id = get_current_user_id()
        data = request.get_json() or {}

        schema = ApiConfigUpdateSchema()
        payload = schema.load(data)

        api_data = payload["api_data"]

        # Chercher config
        api_config = ApiConfig.query.filter_by(
            user_id=current_user_id,
            api_name=api_name,
        ).first()

        if not api_config:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Configuration API {api_name} introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        # Mettre à jour
        api_config.set_api_key(api_data)
        db.session.commit()

        schema = ApiConfigSchema()
        config_data = schema.dump(api_config)

        return (
            jsonify(
                {
                    "success": True,
                    "api_config": config_data,
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
        logger.error(f"Erreur mise à jour config API: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la mise à jour",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@api_config_bp.delete("/apis/<api_name>")
@jwt_required()
@admin_required
def delete_api_config(api_name: str):
    """
    Supprime une configuration API (admin uniquement).

    DELETE /api/config/apis/<api_name>

    Returns:
        Confirmation suppression
    """
    try:
        current_user_id = get_current_user_id()

        # Admin peut supprimer n'importe quelle config
        api_config = ApiConfig.query.filter_by(api_name=api_name).first()

        if not api_config:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Configuration API {api_name} introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        db.session.delete(api_config)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Configuration API {api_name} supprimée",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur suppression config API: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la suppression",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@api_config_bp.post("/apis/<api_name>/test")
@jwt_required()
@operator_or_admin_required
def test_api_connection(api_name: str):
    """
    Test connexion à une API externe.

    POST /api/config/apis/<api_name>/test

    Returns:
        Résultat du test
    """
    try:
        current_user_id = get_current_user_id()

        # Chercher config
        api_config = ApiConfig.query.filter_by(
            user_id=current_user_id,
            api_name=api_name,
        ).first()

        if not api_config:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Configuration API {api_name} introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        # Récupérer clé API (déchiffrée)
        api_data = api_config.get_api_key()

        # Tester connexion
        success, message = _test_api_connection(api_name, api_data)

        return jsonify(
            {
                "success": success,
                "message": message,
            }
        ), (200 if success else 400)

    except Exception as e:
        logger.error(f"Erreur test connexion API: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors du test de connexion",
                    "error_type": "ServerError",
                }
            ),
            500,
        )
