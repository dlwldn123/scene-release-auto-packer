"""Additional tests for Releases Actions API (Phase 4)."""

from __future__ import annotations

from web.extensions import db
from web.models import Release, User


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


def test_readnfo_release_no_file_path(client, auth_headers) -> None:
    """Test READNFO action on release without file_path."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(
            user_id=user.id,
            release_type="EBOOK",
            status="completed",
            file_path=None,
        )
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    response = client.post(
        f"/api/releases/{release_id}/actions/readnfo",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "file path not found" in response.get_json()["message"].lower()


def test_dirfix_release_no_file_path(client, auth_headers) -> None:
    """Test DIRFIX action on release without file_path."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(
            user_id=user.id,
            release_type="EBOOK",
            status="completed",
            file_path=None,
        )
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    response = client.post(
        f"/api/releases/{release_id}/actions/dirfix",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "file path not found" in response.get_json()["message"].lower()


def test_repack_with_options(client, auth_headers) -> None:
    """Test REPACK action with custom options."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(
            user_id=user.id,
            release_type="EBOOK",
            status="completed",
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

    response = client.post(
        f"/api/releases/{release_id}/actions/repack",
        json={"zip_size": 100, "template_id": 5},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "job_id" in data
    assert data["job_id"] > 0
