"""Tests for Release Edit API (Phase 4)."""

from __future__ import annotations

from web.extensions import db
from web.models import Release, User


def test_update_release_metadata_only(client, auth_headers) -> None:
    """Test updating release with only metadata."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(
            user_id=user.id,
            release_type="EBOOK",
            status="draft",
            release_metadata={"title": "Original"},
        )
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    response = client.put(
        f"/api/releases/{release_id}",
        json={"release_metadata": {"title": "Updated", "author": "Author"}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["release"]["release_metadata"]["title"] == "Updated"
    assert data["release"]["release_metadata"]["author"] == "Author"


def test_update_release_config_only(client, auth_headers) -> None:
    """Test updating release with only config."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(
            user_id=user.id,
            release_type="EBOOK",
            status="draft",
            config={"zip_size": 50},
        )
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    response = client.put(
        f"/api/releases/{release_id}",
        json={"config": {"zip_size": 100}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["release"]["config"]["zip_size"] == 100


def test_update_release_all_fields(client, auth_headers) -> None:
    """Test updating release with all fields."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(
            user_id=user.id,
            release_type="EBOOK",
            status="draft",
            release_metadata={"title": "Original"},
            config={"zip_size": 50},
        )
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    response = client.put(
        f"/api/releases/{release_id}",
        json={
            "release_metadata": {"title": "Updated"},
            "config": {"zip_size": 100},
            "status": "completed",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["release"]["status"] == "completed"
    assert data["release"]["release_metadata"]["title"] == "Updated"
    assert data["release"]["config"]["zip_size"] == 100
