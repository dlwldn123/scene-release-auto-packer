"""Tests for ORM models."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import Group, Permission, Role, User


def test_user_password_hashing(app) -> None:
    """Test user password hashing."""
    with app.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")

        assert user.password_hash != "password123"
        assert user.check_password("password123") is True
        assert user.check_password("wrong") is False


def test_user_role_relationship(app) -> None:
    """Test user-role many-to-many relationship."""
    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")

        role1 = Role(name="admin", description="Administrator")
        role2 = Role(name="user", description="Regular user")

        db.session.add_all([user, role1, role2])
        db.session.commit()

        user.roles.append(role1)
        user.roles.append(role2)
        db.session.commit()

        assert len(user.roles.all()) == 2
        assert role1 in user.roles.all()
        assert role2 in user.roles.all()

        # Test reverse relationship
        assert user in role1.users.all()


def test_user_group_relationship(app) -> None:
    """Test user-group many-to-many relationship."""
    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")

        group1 = Group(name="developers", description="Developers group")
        group2 = Group(name="testers", description="Testers group")

        db.session.add_all([user, group1, group2])
        db.session.commit()

        user.groups.append(group1)
        user.groups.append(group2)
        db.session.commit()

        assert len(user.groups.all()) == 2
        assert group1 in user.groups.all()
        assert group2 in user.groups.all()

        # Test reverse relationship
        assert user in group1.users.all()


def test_role_permission_relationship(app) -> None:
    """Test role-permission many-to-many relationship."""
    with app.app_context():
        db.create_all()

        role = Role(name="admin", description="Administrator")

        permission1 = Permission(resource="users", action="READ")
        permission2 = Permission(resource="users", action="WRITE")

        db.session.add_all([role, permission1, permission2])
        db.session.commit()

        role.permissions.append(permission1)
        role.permissions.append(permission2)
        db.session.commit()

        assert len(role.permissions.all()) == 2
        assert permission1 in role.permissions.all()
        assert permission2 in role.permissions.all()

        # Test reverse relationship
        assert role in permission1.roles.all()


def test_user_to_dict(app) -> None:
    """Test user to_dict method."""
    with app.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        user_dict = user.to_dict()

        assert "id" in user_dict
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert "password_hash" not in user_dict  # Should not expose password


def test_user_crud_operations(app) -> None:
    """Test user CRUD operations."""
    with app.app_context():
        db.create_all()

        # Create
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        user_id = user.id
        assert user_id is not None

        # Read
        found_user = User.query.get(user_id)
        assert found_user is not None
        assert found_user.username == "testuser"

        # Update
        found_user.email = "newemail@example.com"
        db.session.commit()

        updated_user = User.query.get(user_id)
        assert updated_user.email == "newemail@example.com"

        # Delete
        db.session.delete(updated_user)
        db.session.commit()

        deleted_user = User.query.get(user_id)
        assert deleted_user is None
