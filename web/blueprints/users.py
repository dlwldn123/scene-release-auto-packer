"""Users blueprint."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import joinedload

from web.extensions import db
from web.models import Group, Role, User
from web.utils.permissions import check_permission, is_admin, can_manage_user

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users() -> tuple[dict, int]:
    """List users with filters and pagination.

    Query parameters:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20)
        - username: Filter by username (partial match)
        - email: Filter by email (partial match)
        - role_id: Filter by role ID

    Returns:
        JSON response with users list and pagination info.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Check permissions (admin only for list)
    if not check_permission(user, "users", "read"):
        return {"message": "Permission denied"}, 403

    # Get query parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    username = request.args.get("username", "")
    email = request.args.get("email", "")
    role_id = request.args.get("role_id", type=int)

    # Build query with eager loading to avoid N+1 queries
    query = User.query.options(joinedload(User.roles))

    if username:
        query = query.filter(User.username.like(f"%{username}%"))

    if email:
        query = query.filter(User.email.like(f"%{email}%"))

    if role_id:
        query = query.join(User.roles).filter(Role.id == role_id)

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items

    return (
        {
            "users": [user.to_dict() for user in users],
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        },
        200,
    )


@users_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id: int) -> tuple[dict, int]:
    """Get user by ID.

    Args:
        user_id: User ID.

    Returns:
        JSON response with user data.
    """
    user = db.session.get(User, user_id)

    if not user:
        return {"message": "User not found"}, 404

    return {"user": user.to_dict()}, 200


@users_bp.route("/users", methods=["POST"])
@jwt_required()
def create_user() -> tuple[dict, int]:
    """Create a new user.

    Expected JSON:
        - username: Username (required)
        - email: Email (required)
        - password: Password (required)

    Returns:
        JSON response with created user.
    """
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)

    if not current_user:
        return {"message": "User not found"}, 404

    # Check permissions (admin only)
    if not check_permission(current_user, "users", "write"):
        return {"message": "Permission denied"}, 403

    data = request.get_json()

    if not data:
        return {"message": "No data provided"}, 400

    required_fields = ["username", "email", "password"]
    for field in required_fields:
        if field not in data:
            return {"message": f"Missing required field: {field}"}, 400

    # Check if username or email already exists
    if User.query.filter_by(username=data["username"]).first():
        return {"message": "Username already exists"}, 400

    if User.query.filter_by(email=data["email"]).first():
        return {"message": "Email already exists"}, 400

    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return {"user": user.to_dict()}, 201


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id: int) -> tuple[dict, int]:
    """Update user.

    Args:
        user_id: User ID.

    Expected JSON:
        - username: Username (optional)
        - email: Email (optional)
        - password: Password (optional)
        - role_ids: List of role IDs (optional)

    Returns:
        JSON response with updated user.
    """
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)

    if not current_user:
        return {"message": "User not found"}, 404

    user = db.session.get(User, user_id)

    if not user:
        return {"message": "User not found"}, 404

    data = request.get_json()

    if not data:
        return {"message": "No data provided"}, 400

    # Check permissions (admin or self)
    if not can_manage_user(current_user, user_id):
        return {"message": "Permission denied"}, 403
    # Limited permissions for self (password only, not roles)
    if current_user.id == user_id and "role_ids" in data:
        return {"message": "Cannot change your own roles"}, 403

    # Update fields if provided
    if "username" in data:
        # Check if username already exists (excluding current user)
        existing = User.query.filter_by(username=data["username"]).first()
        if existing and existing.id != user_id:
            return {"message": "Username already exists"}, 400
        user.username = data["username"]

    if "email" in data:
        # Check if email already exists (excluding current user)
        existing = User.query.filter_by(email=data["email"]).first()
        if existing and existing.id != user_id:
            return {"message": "Email already exists"}, 400
        user.email = data["email"]

    if "password" in data:
        user.set_password(data["password"])

    if "role_ids" in data:
        # Update roles
        roles = Role.query.filter(Role.id.in_(data["role_ids"])).all()
        user.roles = roles

    db.session.commit()

    return {"user": user.to_dict()}, 200


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id: int) -> tuple[dict, int]:
    """Delete user.

    Args:
        user_id: User ID.

    Returns:
        JSON response.
    """
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)

    if not current_user:
        return {"message": "User not found"}, 404

    user = db.session.get(User, user_id)

    if not user:
        return {"message": "User not found"}, 404

    # Check permissions (admin only, cannot delete self)
    if not check_permission(current_user, "users", "delete"):
        return {"message": "Permission denied"}, 403
    if current_user.id == user_id:
        return {"message": "Cannot delete yourself"}, 403

    db.session.delete(user)
    db.session.commit()

    return {"message": "User deleted successfully"}, 200
