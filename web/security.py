"""Security callbacks for JWT."""

from __future__ import annotations

from datetime import datetime, timezone

from flask import current_app
from flask_jwt_extended import JWTManager

from web.extensions import db
from web.models import TokenBlocklist, User


def init_jwt(jwt: JWTManager) -> None:
    """Initialize JWT callbacks.

    Args:
        jwt: JWTManager instance.
    """

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header: dict, jwt_payload: dict) -> bool:
        """Check if token is revoked.

        Args:
            jwt_header: JWT header.
            jwt_payload: JWT payload.

        Returns:
            True if token is revoked.
        """
        jti = jwt_payload.get("jti")
        if jti is None:
            return True

        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None

    @jwt.user_identity_loader
    def user_identity_lookup(user: User) -> int:
        """User identity loader.

        Args:
            user: User instance.

        Returns:
            User ID.
        """
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(jwt_header: dict, jwt_payload: dict) -> User | None:
        """User lookup callback.

        Args:
            jwt_header: JWT header.
            jwt_payload: JWT payload.

        Returns:
            User instance or None.
        """
        identity = jwt_payload.get("sub")
        if identity is None:
            return None

        return User.query.filter_by(id=identity, active=True).first()

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header: dict, jwt_payload: dict) -> tuple[dict, int]:
        """Expired token callback.

        Args:
            jwt_header: JWT header.
            jwt_payload: JWT payload.

        Returns:
            Error response.
        """
        return {"message": "Token has expired"}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error: str) -> tuple[dict, int]:
        """Invalid token callback.

        Args:
            error: Error message.

        Returns:
            Error response.
        """
        return {"message": f"Invalid token: {error}"}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error: str) -> tuple[dict, int]:
        """Missing token callback.

        Args:
            error: Error message.

        Returns:
            Error response.
        """
        return {"message": f"Authorization required: {error}"}, 401
