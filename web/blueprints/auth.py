"""Authentication blueprint."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from web.extensions import db
from web.models import TokenBlocklist, User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/login", methods=["POST"])
def login() -> tuple[dict, int]:
    """Login endpoint.

    Returns:
        JSON response with access and refresh tokens.
    """
    data = request.get_json()
    if not data:
        return {"message": "No input data provided"}, 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"message": "Username and password required"}, 400

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return {"message": "Invalid credentials"}, 401

    if not user.active:
        return {"message": "User account is inactive"}, 403

    # Create tokens
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)

    return (
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
        },
        200,
    )


@auth_bp.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh() -> tuple[dict, int]:
    """Refresh access token.

    Returns:
        JSON response with new access token.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.active:
        return {"message": "User not found or inactive"}, 404

    access_token = create_access_token(identity=user)

    return {"access_token": access_token}, 200


@auth_bp.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout() -> tuple[dict, int]:
    """Logout endpoint - revoke token.

    Returns:
        JSON response.
    """
    jti = get_jwt()["jti"]
    token_type = get_jwt()["type"]
    expires_at = datetime.fromtimestamp(get_jwt()["exp"], tz=timezone.utc)

    # Add token to blocklist
    revoked_token = TokenBlocklist(
        jti=jti, token_type=token_type, expires_at=expires_at
    )
    db.session.add(revoked_token)
    db.session.commit()

    return {"message": "Successfully logged out"}, 200


@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def get_current_user() -> tuple[dict, int]:
    """Get current user information.

    Returns:
        JSON response with user data.
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return {"message": "User not found"}, 404

    return {"user": user.to_dict()}, 200
