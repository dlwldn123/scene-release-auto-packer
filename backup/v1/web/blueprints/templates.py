"""
Blueprint pour la gestion des templates NFO.
"""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from web.auth import admin_required, operator_or_admin_required
from web.database import db
from web.models.template import NfoTemplate
from web.models.user import User
from web.schemas.template import (
    TemplateCreateSchema,
    TemplateRenderSchema,
    TemplateSchema,
)

logger = logging.getLogger(__name__)

templates_bp = Blueprint("templates", __name__)


@templates_bp.get("")
@jwt_required()
@operator_or_admin_required
def list_templates():
    """
    Liste tous les templates NFO disponibles.

    GET /api/templates

    Returns:
        Liste des templates
    """
    try:
        # Pagination
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        query = NfoTemplate.query.order_by(NfoTemplate.created_at.desc())
        total = query.count()
        templates = query.limit(limit).offset(offset).all()

        schema = TemplateSchema(many=True)
        templates_data = schema.dump(templates)

        return (
            jsonify(
                {
                    "success": True,
                    "templates": templates_data,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur liste templates: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération des templates",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@templates_bp.get("/<int:template_id>")
@jwt_required()
@operator_or_admin_required
def get_template(template_id: int):
    """
    Récupère un template NFO spécifique.

    GET /api/templates/<id>

    Returns:
        Détails du template
    """
    try:
        template = NfoTemplate.query.get(template_id)

        if not template:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Template introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        schema = TemplateSchema()
        template_data = schema.dump(template)

        return (
            jsonify(
                {
                    "success": True,
                    "template": template_data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur récupération template: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération du template",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@templates_bp.post("")
@jwt_required()
@admin_required
def create_template():
    """
    Crée un nouveau template NFO (admin uniquement).

    POST /api/templates
    Body: {"name": "...", "description": "...", "content": "...", "variables": {...}}

    Returns:
        Template créé
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}

        schema = TemplateCreateSchema()
        payload = schema.load(data)

        # Vérifier si template par défaut demandé
        is_default = payload.get("is_default", False)

        # Si ce template devient défaut, désactiver les autres
        if is_default:
            existing_defaults = NfoTemplate.query.filter_by(is_default=True).all()
            for t in existing_defaults:
                t.is_default = False

        template = NfoTemplate(
            name=payload["name"],
            description=payload.get("description"),
            content=payload["content"],
            variables=payload.get("variables", {}),
            is_default=is_default,
            created_by=current_user_id,
        )

        db.session.add(template)
        db.session.commit()

        schema = TemplateSchema()
        return (
            jsonify(
                {
                    "success": True,
                    "template": schema.dump(template),
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
        logger.error(f"Erreur création template: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la création du template",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@templates_bp.put("/<int:template_id>")
@jwt_required()
@admin_required
def update_template(template_id: int):
    """
    Met à jour un template NFO (admin uniquement).

    PUT /api/templates/<id>
    Body: {"name": "...", "description": "...", "content": "...", "variables": {...}}

    Returns:
        Template mis à jour
    """
    try:
        template = NfoTemplate.query.get(template_id)

        if not template:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Template introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        data = request.get_json() or {}
        schema = TemplateCreateSchema()
        payload = schema.load(data, partial=True)

        # Mise à jour champs
        if "name" in payload:
            template.name = payload["name"]
        if "description" in payload:
            template.description = payload.get("description")
        if "content" in payload:
            template.content = payload["content"]
        if "variables" in payload:
            template.set_variables(payload["variables"])

        # Gestion is_default
        if "is_default" in payload:
            is_default = payload["is_default"]
            if is_default and not template.is_default:
                # Désactiver les autres templates par défaut
                existing_defaults = NfoTemplate.query.filter_by(is_default=True).all()
                for t in existing_defaults:
                    t.is_default = False
            template.is_default = is_default

        db.session.commit()

        schema = TemplateSchema()
        return (
            jsonify(
                {
                    "success": True,
                    "template": schema.dump(template),
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
        logger.error(f"Erreur mise à jour template: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la mise à jour du template",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@templates_bp.delete("/<int:template_id>")
@jwt_required()
@admin_required
def delete_template(template_id: int):
    """
    Supprime un template NFO (admin uniquement).

    DELETE /api/templates/<id>

    Returns:
        Confirmation suppression
    """
    try:
        template = NfoTemplate.query.get(template_id)

        if not template:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Template introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        # Empêcher suppression template par défaut
        if template.is_default:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Impossible de supprimer le template par défaut",
                        "error_type": "ValidationError",
                    }
                ),
                400,
            )

        db.session.delete(template)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Template supprimé",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur suppression template: {e}", exc_info=True)
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la suppression du template",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@templates_bp.post("/<int:template_id>/render")
@jwt_required()
@operator_or_admin_required
def render_template(template_id: int):
    """
    Rendu un template avec des variables données.

    POST /api/templates/<id>/render
    Body: {"variables": {...}}

    Returns:
        Template rendu
    """
    try:
        template = NfoTemplate.query.get(template_id)

        if not template:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Template introuvable",
                        "error_type": "NotFound",
                    }
                ),
                404,
            )

        data = request.get_json() or {}
        schema = TemplateRenderSchema()
        payload = schema.load(data)

        variables = payload.get("variables", {})

        # Rendre le template
        from web.services.template_renderer import render_nfo_template

        rendered_content = render_nfo_template(template.content, variables)

        return (
            jsonify(
                {
                    "success": True,
                    "rendered_content": rendered_content,
                    "template_id": template.id,
                    "template_name": template.name,
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
        logger.error(f"Erreur rendu template: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors du rendu du template",
                    "error_type": "ServerError",
                }
            ),
            500,
        )


@templates_bp.get("/default")
@jwt_required()
@operator_or_admin_required
def get_default_template():
    """
    Récupère le template par défaut.

    GET /api/templates/default

    Returns:
        Template par défaut
    """
    try:
        template = NfoTemplate.query.filter_by(is_default=True).first()

        if not template:
            # Retourner template système par défaut
            from src.packaging.nfo import _load_template

            default_content = _load_template(None)

            return (
                jsonify(
                    {
                        "success": True,
                        "template": {
                            "id": None,
                            "name": "Template système par défaut",
                            "description": "Template intégré par défaut",
                            "content": default_content,
                            "is_default": True,
                        },
                    }
                ),
                200,
            )

        schema = TemplateSchema()
        return (
            jsonify(
                {
                    "success": True,
                    "template": schema.dump(template),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Erreur récupération template par défaut: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Erreur lors de la récupération du template par défaut",
                    "error_type": "ServerError",
                }
            ),
            500,
        )
