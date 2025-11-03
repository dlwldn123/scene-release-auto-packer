"""Tests for database setup and models."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import Group, Permission, Role, User


def test_db_connection(app) -> None:
    """Test database connection."""
    with app.app_context():
        db.create_all()
        assert db.engine is not None


def test_create_tables(app) -> None:
    """Test creating all tables."""
    from sqlalchemy import inspect

    with app.app_context():
        db.create_all()
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        assert "users" in tables
        assert "roles" in tables
        assert "permissions" in tables
        assert "groups" in tables
        assert "token_blocklist" in tables


def test_create_user(app) -> None:
    """Test creating a user."""
    with app.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.check_password("password123") is True
        assert user.check_password("wrong") is False


def test_user_relationships(app) -> None:
    """Test user relationships with roles and groups."""
    with app.app_context():
        db.create_all()

        # Create user
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")

        # Create role
        role = Role(name="admin", description="Administrator")
        db.session.add(role)

        # Create group
        group = Group(name="developers", description="Developers group")
        db.session.add(group)

        db.session.add(user)
        db.session.commit()

        # Add relationships
        user.roles.append(role)
        user.groups.append(group)
        db.session.commit()

        # Verify relationships
        assert len(user.roles.all()) == 1
        assert len(user.groups.all()) == 1
        assert user.roles.first().name == "admin"
        assert user.groups.first().name == "developers"
