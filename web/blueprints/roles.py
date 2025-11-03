"""Roles blueprint."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from web.extensions import db
from web.models import Permission, Role, User
from web.utils.permissions import check_permission

roles_bp = Blueprint("roles", __name__)


@roles_bp.route("/roles", methods=["GET"])
@jwt_required()
def list_roles() -> tuple[dict, int]:
    """List roles with filters and pagination.

    Query parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - name: Filter by name (partial match)

    Returns:
        JSON response with roles list and pagination info.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    name = request.args.get("name", "")

    # Build query
    query = Role.query

    if name:
        query = query.filter(Role.name.like(f"%{name}%"))

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    roles = pagination.items

    return (
        {
            "roles": [role.to_dict() for role in roles],
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        },
        200,
    )


@roles_bp.route("/roles/<int:role_id>", methods=["GET"])
@jwt_required()
def get_role(role_id: int) -> tuple[dict, int]:
    """Get role by ID.

    Args:
        role_id: Role ID.

    Returns:
        JSON response with role data.
    """
    role = db.session.get(Role, role_id)

    if not role:
        return {"message": "Role not found"}, 404

    return {"role": role.to_dict()}, 200


@roles_bp.route("/roles", methods=["POST"])
@jwt_required()
def create_role() -> tuple[dict, int]:
    """Create a new role.

    Expected JSON:
        - name: Role name (required)
        - description: Description (optional)
        - permission_ids: List of permission IDs (optional)

    Returns:
        JSON response with created role.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Check permissions (admin only)
    if not check_permission(user, "roles", "write"):
        return {"message": "Permission denied"}, 403

    data = request.get_json()

    if not data:
        return {"message": "No data provided"}, 400

    if "name" not in data:
        return {"message": "Missing required field: name"}, 400

    # Check if role name already exists
    if Role.query.filter_by(name=data["name"]).first():
        return {"message": "Role name already exists"}, 400

    role = Role(name=data["name"], description=data.get("description"))

    if "permission_ids" in data:
        permissions = Permission.query.filter(
            Permission.id.in_(data["permission_ids"])
        ).all()
        role.permissions = permissions

    db.session.add(role)
    db.session.commit()

    return {"role": role.to_dict()}, 201


@roles_bp.route("/roles/<int:role_id>", methods=["PUT"])
@jwt_required()
def update_role(role_id: int) -> tuple[dict, int]:
    """Update role.

    Args:
        role_id: Role ID.

    Expected JSON:
        - name: Role name (optional)
        - description: Description (optional)
        - permission_ids: List of permission IDs (optional)

    Returns:
        JSON response with updated role.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    role = db.session.get(Role, role_id)

    if not role:
        return {"message": "Role not found"}, 404

    # Check permissions (admin only)
    if not check_permission(user, "roles", "write"):
        return {"message": "Permission denied"}, 403

    data = request.get_json()

    if not data:
        return {"message": "No data provided"}, 400

    # Update fields if provided
    if "name" in data:
        # Check if name already exists (excluding current role)
        existing = Role.query.filter_by(name=data["name"]).first()
        if existing and existing.id != role_id:
            return {"message": "Role name already exists"}, 400
        role.name = data["name"]

    if "description" in data:
        role.description = data["description"]

    if "permission_ids" in data:
        permissions = Permission.query.filter(
            Permission.id.in_(data["permission_ids"])
        ).all()
        role.permissions = permissions

    db.session.commit()

    return {"role": role.to_dict()}, 200


@roles_bp.route("/roles/<int:role_id>", methods=["DELETE"])
@jwt_required()
def delete_role(role_id: int) -> tuple[dict, int]:
    """Delete role.

    Args:
        role_id: Role ID.

    Returns:
        JSON response.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    role = db.session.get(Role, role_id)

    if not role:
        return {"message": "Role not found"}, 404

    # Check permissions (admin only)
    if not check_permission(user, "roles", "delete"):
        return {"message": "Permission denied"}, 403

    db.session.delete(role)
    db.session.commit()

    return {"message": "Role deleted successfully"}, 200
