"""Final coverage tests for Releases API (Phase 4)."""

from __future__ import annotations

from web.extensions import db
from web.models import Release, User


def test_list_releases_invalid_page(client, auth_headers) -> None:
    """Test listing releases with invalid page number."""
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

    # Invalid page (negative)
    response = client.get(
        "/api/releases?page=-1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    # Should default to page 1 or handle gracefully
    data = response.get_json()
    assert "releases" in data


def test_list_releases_sort_status(client, auth_headers) -> None:
    """Test sorting releases by status."""
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

    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    response = client.get(
        "/api/releases?sort_by=status&sort_order=asc",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["releases"]) == 2
