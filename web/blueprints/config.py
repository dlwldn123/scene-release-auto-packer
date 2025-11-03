"""Configurations blueprint."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from web.extensions import db
from web.models import Configuration, User
from web.utils.permissions import check_permission

config_bp = Blueprint("config", __name__)


@config_bp.route("/config", methods=["GET"])
@jwt_required()
def list_configurations() -> tuple[dict, int]:
    """List configurations with filters and pagination.

    Query parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 100)
        - category: Filter by category
        - key: Filter by key (partial match)

    Returns:
        JSON response with configurations list and pagination info.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Check permissions (admin only for list)
    if not check_permission(user, "config", "read"):
        return {"message": "Permission denied"}, 403

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 100, type=int)
    category = request.args.get("category", "")
    key = request.args.get("key", "")

    # Build query
    query = Configuration.query

    if category:
        query = query.filter(Configuration.category == category)

    if key:
        query = query.filter(Configuration.key.like(f"%{key}%"))

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    configurations = pagination.items

    return (
        {
            "configurations": [config.to_dict() for config in configurations],
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        },
        200,
    )


@config_bp.route("/config/<int:config_id>", methods=["GET"])
@jwt_required()
def get_configuration(config_id: int) -> tuple[dict, int]:
    """Get configuration by ID.

    Args:
        config_id: Configuration ID.

    Returns:
        JSON response with configuration data.
    """
    config = db.session.get(Configuration, config_id)

    if not config:
        return {"message": "Configuration not found"}, 404

    return {"configuration": config.to_dict()}, 200


@config_bp.route("/config/key/<key>", methods=["GET"])
@jwt_required()
def get_configuration_by_key(key: str) -> tuple[dict, int]:
    """Get configuration by key.

    Args:
        key: Configuration key.

    Returns:
        JSON response with configuration data.
    """
    config = Configuration.query.filter_by(key=key).first()

    if not config:
        return {"message": "Configuration not found"}, 404

    return {"configuration": config.to_dict()}, 200


@config_bp.route("/config", methods=["POST"])
@jwt_required()
def create_configuration() -> tuple[dict, int]:
    """Create a new configuration.

    Expected JSON:
        - key: Configuration key (required)
        - value: Configuration value (required)
        - category: Category (optional)
        - description: Description (optional)

    Returns:
        JSON response with created configuration.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Check permissions (admin only)
    if not check_permission(user, "config", "write"):
        return {"message": "Permission denied"}, 403

    data = request.get_json()

    if not data:
        return {"message": "No data provided"}, 400

    required_fields = ["key", "value"]
    for field in required_fields:
        if field not in data:
            return {"message": f"Missing required field: {field}"}, 400

    # Check if key already exists
    if Configuration.query.filter_by(key=data["key"]).first():
        return {"message": "Configuration key already exists"}, 400

    config = Configuration(
        key=data["key"],
        value=data["value"],
        category=data.get("category"),
        description=data.get("description"),
    )

    db.session.add(config)
    db.session.commit()

    return {"configuration": config.to_dict()}, 201


@config_bp.route("/config/<int:config_id>", methods=["PUT"])
@jwt_required()
def update_configuration(config_id: int) -> tuple[dict, int]:
    """Update configuration.

    Args:
        config_id: Configuration ID.

    Expected JSON:
        - key: Configuration key (optional)
        - value: Configuration value (optional)
        - category: Category (optional)
        - description: Description (optional)

    Returns:
        JSON response with updated configuration.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    config = db.session.get(Configuration, config_id)

    if not config:
        return {"message": "Configuration not found"}, 404

    # Check permissions (admin only)
    if not check_permission(user, "config", "write"):
        return {"message": "Permission denied"}, 403

    data = request.get_json()

    if not data:
        return {"message": "No data provided"}, 400

    # Update fields if provided
    if "key" in data:
        # Check if key already exists (excluding current config)
        existing = Configuration.query.filter_by(key=data["key"]).first()
        if existing and existing.id != config_id:
            return {"message": "Configuration key already exists"}, 400
        config.key = data["key"]

    if "value" in data:
        config.value = data["value"]

    if "category" in data:
        config.category = data["category"]

    if "description" in data:
        config.description = data["description"]

    db.session.commit()

    return {"configuration": config.to_dict()}, 200


@config_bp.route("/config/<int:config_id>", methods=["DELETE"])
@jwt_required()
def delete_configuration(config_id: int) -> tuple[dict, int]:
    """Delete configuration.

    Args:
        config_id: Configuration ID.

    Returns:
        JSON response.
    """
    config = db.session.get(Configuration, config_id)

    if not config:
        return {"message": "Configuration not found"}, 404

    # Check permissions (admin only)
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)
    if not current_user or not check_permission(current_user, "config", "delete"):
        return {"message": "Permission denied"}, 403

    db.session.delete(config)
    db.session.commit()

    return {"message": "Configuration deleted successfully"}, 200
