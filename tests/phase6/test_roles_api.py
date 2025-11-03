"""Tests for Roles API."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import Role, User


def test_list_roles(client) -> None:
    """Test listing roles."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        role1 = Role(name="Admin", description="Administrator role")
        role2 = Role(name="User", description="User role")
        db.session.add_all([role1, role2])
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List roles
    response = client.get(
        "/api/roles",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "roles" in data
    assert "pagination" in data
    assert len(data["roles"]) >= 2


def test_create_role(client) -> None:
    """Test creating role."""
    with client.application.app_context():
        db.create_all()
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Create role
    response = client.post(
        "/api/roles",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Editor", "description": "Editor role"},
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "role" in data
    assert data["role"]["name"] == "Editor"


def test_update_role(client) -> None:
    """Test updating role."""
    with client.application.app_context():
        db.create_all()
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        role = Role(name="Editor", description="Editor role")
        db.session.add(role)
        db.session.commit()
        role_id = role.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Update role
    response = client.put(
        f"/api/roles/{role_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "Updated description"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["role"]["description"] == "Updated description"


def test_delete_role(client) -> None:
    """Test deleting role."""
    with client.application.app_context():
        db.create_all()
        admin_role = Role(name="admin", description="Administrator")
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        user.roles.append(admin_role)
        db.session.add_all([admin_role, user])
        db.session.commit()

        role = Role(name="Editor", description="Editor role")
        db.session.add(role)
        db.session.commit()
        role_id = role.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Delete role
    response = client.delete(
        f"/api/roles/{role_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    # Verify deleted
    get_response = client.get(
        f"/api/roles/{role_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 404
