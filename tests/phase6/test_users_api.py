"""Tests for Users API."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import Role, User


def test_list_users(client) -> None:
    """Test listing users."""
    with client.application.app_context():
        db.create_all()
        user1 = User(username="user1", email="user1@example.com")
        user1.set_password("password123")
        user2 = User(username="user2", email="user2@example.com")
        user2.set_password("password123")
        db.session.add_all([user1, user2])
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "user1", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List users
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "users" in data
    assert "pagination" in data
    assert len(data["users"]) >= 2


def test_create_user(client) -> None:
    """Test creating user."""
    with client.application.app_context():
        db.create_all()
        user = User(username="admin", email="admin@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Create user
    response = client.post(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "user" in data
    assert data["user"]["username"] == "newuser"


def test_update_user(client) -> None:
    """Test updating user."""
    with client.application.app_context():
        db.create_all()
        admin = User(username="admin", email="admin@example.com")
        admin.set_password("password123")
        user = User(username="user1", email="user1@example.com")
        user.set_password("password123")
        db.session.add_all([admin, user])
        db.session.commit()
        user_id = user.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Update user
    response = client.put(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "updated@example.com"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["user"]["email"] == "updated@example.com"


def test_delete_user(client) -> None:
    """Test deleting user."""
    with client.application.app_context():
        db.create_all()
        admin = User(username="admin", email="admin@example.com")
        admin.set_password("password123")
        user = User(username="user1", email="user1@example.com")
        user.set_password("password123")
        db.session.add_all([admin, user])
        db.session.commit()
        user_id = user.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Delete user
    response = client.delete(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    # Verify deleted
    get_response = client.get(
        f"/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 404
