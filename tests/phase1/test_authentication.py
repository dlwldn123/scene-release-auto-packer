"""Tests for JWT authentication."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import User


def test_login_success(client) -> None:
    """Test successful login."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    assert data["user"]["username"] == "testuser"


def test_login_invalid_credentials(client) -> None:
    """Test login with invalid credentials."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    data = response.get_json()
    assert "Invalid credentials" in data["message"]


def test_refresh_token(client) -> None:
    """Test refresh token."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    # Login first
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    refresh_token = login_response.get_json()["refresh_token"]

    # Refresh access token
    response = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data


def test_logout(client) -> None:
    """Test logout."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    # Login first
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    access_token = login_response.get_json()["access_token"]

    # Logout
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "Successfully logged out" in data["message"]


def test_get_current_user(client) -> None:
    """Test get current user."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    # Login first
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    access_token = login_response.get_json()["access_token"]

    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "user" in data
    assert data["user"]["username"] == "testuser"


def test_protected_route_requires_auth(client) -> None:
    """Test that protected routes require authentication."""
    response = client.get("/api/auth/me")

    assert response.status_code == 401
