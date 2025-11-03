"""
Blueprint pour la gestion des destinations FTP/SFTP par groupe.
"""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from marshmallow import ValidationError

from web.auth import admin_required, operator_or_admin_required
from web.database import db
from web.models.destination import Destination
from web.models.user import User
from web.schemas.destination import (
    DestinationCreateSchema,
    DestinationSchema,
    DestinationUpdateSchema,
)

logger = logging.getLogger(__name__)

destinations_bp = Blueprint("destinations", __name__)


@destinations_bp.get("")
@jwt_required()
@operator_or_admin_required
def list_destinations():
    """
    Liste les destinations FTP/SFTP de l'utilisateur.

    GET /api/destinations?group=MYGRP

    Returns:
        Liste des destinations
    """
    try:
        current_user_id = get_jwt_identity()
        group = request.args.get("group")

        # Pagination
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        query = Destination.query.filter_by(user_id=current_user_id)

        # Si group fourni, filtrer (via nom de destination qui contient généralement le groupe)
        if group:
            query = query.filter(Destination.name.contains(group))

        query = query.order_by(Destination.created_at.desc())
        total = query.count()
        destinations = query.limit(limit).offset(offset).all()

        schema = DestinationSchema(many=True)
        destinations_data = schema.dump(destinations)

        return (
            jsonify(
                {
                    "success": True,
                    "destinations": destinations_data,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur liste destinations: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération des destinations",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@destinations_bp.get("/<int:destination_id>")
@jwt_required()
@operator_or_admin_required
def get_destination(destination_id: int):
    """
    Récupère une destination spécifique.

    GET /api/destinations/<destination_id>

    Returns:
        Détails de la destination
    """
    try:
        current_user_id = get_jwt_identity()

        destination = Destination.query.get(destination_id)

        if not destination:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Destination introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        # Vérifier permissions
        claims = get_jwt()
        user_role = claims.get("role")

        if user_role != "admin" and destination.user_id != current_user_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Accès refusé",
                        "error_type": "ForbiddenError",
                    }
                ),
                403,
            )

        schema = DestinationSchema()
        return (
            jsonify(
                {
                    "success": True,
                    "destination": schema.dump(destination),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur récupération destination: {e}", exc_info=True)
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


@destinations_bp.post("")
@jwt_required()
@operator_or_admin_required
def create_destination():
    """
    Crée une nouvelle destination FTP/SFTP.

    POST /api/destinations
    Body: {
        "name": "...",
        "type": "ftp|sftp",
        "host": "...",
        "port": 21,
        "username": "...",
        "password": "...",
        "path": "...",
        "group": "MYGRP" (optionnel pour restriction)
    }

    Returns:
        Destination créée
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        schema = DestinationCreateSchema()
        payload = schema.load(data)

        # Créer destination
        destination = Destination(
            user_id=current_user_id,
            name=payload["name"],
            type=payload["type"],
            host=payload["host"],
            port=payload["port"],
            username=payload["username"],
            path=payload.get("path"),
        )
        destination.set_password(payload["password"])

        db.session.add(destination)
        db.session.commit()

        schema = DestinationSchema()
        return (
            jsonify(
                {
                    "success": True,
                    "destination": schema.dump(destination),
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
        logger.error(f"Erreur création destination: {e}", exc_info=True)
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


@destinations_bp.put("/<int:destination_id>")
@jwt_required()
@operator_or_admin_required
def update_destination(destination_id: int):
    """
    Met à jour une destination.

    PUT /api/destinations/<destination_id>

    Returns:
        Destination mise à jour
    """
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get("role")

        destination = Destination.query.get(destination_id)

        if not destination:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Destination introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        # Vérifier permissions
        if user_role != "admin" and destination.user_id != current_user_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Accès refusé",
                        "error_type": "ForbiddenError",
                    }
                ),
                403,
            )

        data = request.get_json() or {}
        schema = DestinationUpdateSchema()
        payload = schema.load(data)

        # Mettre à jour champs
        if "name" in payload:
            destination.name = payload["name"]
        if "host" in payload:
            destination.host = payload["host"]
        if "port" in payload:
            destination.port = payload["port"]
        if "username" in payload:
            destination.username = payload["username"]
        if "path" in payload:
            destination.path = payload["path"]
        if "password" in payload and payload["password"]:
            destination.set_password(payload["password"])

        db.session.commit()

        schema = DestinationSchema()
        return (
            jsonify(
                {
                    "success": True,
                    "destination": schema.dump(destination),
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
        logger.error(f"Erreur mise à jour destination: {e}", exc_info=True)
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


@destinations_bp.delete("/<int:destination_id>")
@jwt_required()
@operator_or_admin_required
def delete_destination(destination_id: int):
    """
    Supprime une destination.

    DELETE /api/destinations/<destination_id>

    Returns:
        Confirmation suppression
    """
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get("role")

        destination = Destination.query.get(destination_id)

        if not destination:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Destination introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        # Vérifier permissions
        if user_role != "admin" and destination.user_id != current_user_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Accès refusé",
                        "error_type": "ForbiddenError",
                    }
                ),
                403,
            )

        db.session.delete(destination)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Destination supprimée",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur suppression destination: {e}", exc_info=True)
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


@destinations_bp.get("/groups/<group>")
@jwt_required()
@operator_or_admin_required
def get_group_destinations(group: str):
    """
    Récupère les destinations pour un groupe spécifique.

    GET /api/destinations/groups/<group>

    Returns:
        Liste des destinations du groupe
    """
    try:
        current_user_id = get_jwt_identity()

        # Chercher destinations dont le nom contient le groupe
        destinations = Destination.query.filter(
            Destination.user_id == current_user_id, Destination.name.contains(group)
        ).all()

        schema = DestinationSchema(many=True)
        destinations_data = schema.dump(destinations)

        return (
            jsonify(
                {
                    "success": True,
                    "destinations": destinations_data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur destinations groupe: {e}", exc_info=True)
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


@destinations_bp.post("/<int:destination_id>/test")
@jwt_required()
@operator_or_admin_required
def test_destination(destination_id: int):
    """
    Test connexion à une destination FTP/SFTP.

    POST /api/destinations/<destination_id>/test

    Returns:
        Résultat du test de connexion
    """
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get("role")

        destination = Destination.query.get(destination_id)

        if not destination:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Destination introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        # Vérifier permissions
        if user_role != "admin" and destination.user_id != current_user_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Accès refusé",
                        "error_type": "ForbiddenError",
                    }
                ),
                403,
            )

        # Tester connexion
        from web.services.ftp_upload import FtpUploadService

        upload_service = FtpUploadService()

        success, message = upload_service.test_connection(destination)

        return jsonify(
            {
                "success": success,
                "message": message,
            }
        ), (200 if success else 400)

    except Exception as e:
        logger.error(f"Erreur test connexion destination: {e}", exc_info=True)
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
