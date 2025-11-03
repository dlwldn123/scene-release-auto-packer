"""Tests for Releases API."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import Release, User


def test_list_releases(client) -> None:
    """Test listing releases."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release1 = Release(user_id=user.id, release_type="EBOOK", status="completed")
        release2 = Release(user_id=user.id, release_type="TV", status="draft")
        db.session.add_all([release1, release2])
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List releases
    response = client.get(
        "/api/releases",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "releases" in data
    assert "pagination" in data
    assert len(data["releases"]) == 2


def test_list_releases_with_filters(client) -> None:
    """Test listing releases with filters."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release1 = Release(user_id=user.id, release_type="EBOOK", status="completed")
        release2 = Release(user_id=user.id, release_type="TV", status="draft")
        db.session.add_all([release1, release2])
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List releases filtered by type
    response = client.get(
        "/api/releases?release_type=EBOOK",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["releases"]) == 1
    assert data["releases"][0]["release_type"] == "EBOOK"


def test_get_release(client) -> None:
    """Test getting release by ID."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(user_id=user.id, release_type="EBOOK", status="completed")
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Get release
    response = client.get(
        f"/api/releases/{release_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "release" in data
    assert data["release"]["id"] == release_id


def test_delete_release(client) -> None:
    """Test deleting release."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(user_id=user.id, release_type="EBOOK", status="completed")
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Delete release
    response = client.delete(
        f"/api/releases/{release_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    # Verify deleted
    get_response = client.get(
        f"/api/releases/{release_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 404
