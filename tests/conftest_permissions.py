"""Permissions fixtures for conftest."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import Permission, Role, User


@pytest.fixture
def admin_role(app):
    """Create admin role."""
    with app.app_context():
        role = Role(name="admin", description="Administrator")
        db.session.add(role)
        db.session.commit()
        yield role


@pytest.fixture
def admin_user(app, admin_role):
    """Create admin user."""
    with app.app_context():
        user = User(username="admin", email="admin@test.com")
        user.set_password("password")
        user.roles.append(admin_role)
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def create_user_with_permissions(app):
    """Helper to create user with specific permissions."""

    def _create_user(
        username: str,
        email: str,
        permissions: list[tuple[str, str]] | None = None,
    ) -> User:
        """Create user with permissions.

        Args:
            username: Username.
            email: Email.
            permissions: List of (resource, action) tuples.

        Returns:
            User object.
        """
        user = User(username=username, email=email)
        user.set_password("password")

        if permissions:
            role = Role(name=f"role_{username}", description=f"Role for {username}")
            db.session.add(role)

            for resource, action in permissions:
                permission = Permission.query.filter_by(
                    resource=resource, action=action
                ).first()
                if not permission:
                    permission = Permission(resource=resource, action=action)
                    db.session.add(permission)
                role.permissions.append(permission)

            user.roles.append(role)

        db.session.add(user)
        db.session.commit()
        return user

    return _create_user


def get_or_create_permission(resource: str, action: str) -> Permission:
    """Get existing permission or create if not exists.
    
    Args:
        resource: Resource name.
        action: Action name.
        
    Returns:
        Permission object.
    """
    permission = Permission.query.filter_by(resource=resource, action=action).first()
    if not permission:
        permission = Permission(resource=resource, action=action)
        db.session.add(permission)
        db.session.commit()
    return permission
