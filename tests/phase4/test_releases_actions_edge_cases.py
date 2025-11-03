"""Edge case tests for Releases Actions API to improve coverage (Phase 4)."""

from __future__ import annotations

from web.extensions import db
from web.models import User


def test_nfofix_release_not_found(client, auth_headers) -> None:
    """Test NFOFIX action on non-existent release."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    response = client.post(
        "/api/releases/99999/actions/nfofix",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_readnfo_release_not_found(client, auth_headers) -> None:
    """Test READNFO action on non-existent release."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    response = client.post(
        "/api/releases/99999/actions/readnfo",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_repack_release_not_found(client, auth_headers) -> None:
    """Test REPACK action on non-existent release."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    response = client.post(
        "/api/releases/99999/actions/repack",
        json={"zip_size": 100},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_dirfix_release_not_found(client, auth_headers) -> None:
    """Test DIRFIX action on non-existent release."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    response = client.post(
        "/api/releases/99999/actions/dirfix",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
