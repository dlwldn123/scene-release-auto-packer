"""Tests for Wizard Step 6 - Update Metadata endpoint."""

from __future__ import annotations

from web.extensions import db
from web.models import Group, Release, Rule, User


def test_wizard_update_metadata_success(client, app) -> None:
    """Test updating metadata successfully."""
    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        group = Group(name="TestGroup")
        rule = Rule(name="[2022] eBOOK", content="Test rule", section="eBOOK")
        db.session.add_all([group, rule])
        db.session.commit()

        release = Release(
            user_id=user.id,
            group_id=group.id,
            release_type="EBOOK",
            status="draft",
            release_metadata={"wizard_step": 5},
        )
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Update metadata
    enriched_metadata = {
        "title": "Test Book Title",
        "author": "Test Author",
        "isbn": "1234567890",
        "year": 2022,
    }

    response = client.post(
        f"/api/wizard/{release_id}/metadata",
        json={"enriched_metadata": enriched_metadata},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Metadata updated successfully"
    assert "metadata" in data

    # Verify release metadata was updated
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.release_metadata["wizard_step"] == 6
        assert release.release_metadata["title"] == "Test Book Title"
        assert release.release_metadata["author"] == "Test Author"


def test_wizard_update_metadata_merges_with_existing(client, app) -> None:
    """Test that metadata update merges with existing metadata."""
    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(
            user_id=user.id,
            release_type="EBOOK",
            status="draft",
            release_metadata={"wizard_step": 5, "existing_field": "existing_value"},
        )
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Update metadata
    enriched_metadata = {"title": "New Title"}

    response = client.post(
        f"/api/wizard/{release_id}/metadata",
        json={"enriched_metadata": enriched_metadata},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    # Verify metadata was merged
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.release_metadata["wizard_step"] == 6
        assert release.release_metadata["existing_field"] == "existing_value"
        assert release.release_metadata["title"] == "New Title"


def test_wizard_update_metadata_requires_auth(client, app) -> None:
    """Test that update metadata requires authentication."""
    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(user_id=user.id, release_type="EBOOK", status="draft")
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    # Try update without auth
    response = client.post(
        f"/api/wizard/{release_id}/metadata",
        json={"enriched_metadata": {}},
    )

    assert response.status_code == 401


def test_wizard_update_metadata_release_not_found(client, app) -> None:
    """Test update metadata when release not found."""
    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Try update non-existent release
    response = client.post(
        "/api/wizard/99999/metadata",
        json={"enriched_metadata": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert "release not found" in response.get_json()["message"].lower()


def test_wizard_update_metadata_permission_denied(client, app) -> None:
    """Test update metadata when user doesn't own the release."""
    with app.app_context():
        db.create_all()

        user1 = User(username="user1", email="user1@example.com")
        user1.set_password("password123")
        user2 = User(username="user2", email="user2@example.com")
        user2.set_password("password123")
        db.session.add_all([user1, user2])
        db.session.commit()

        release = Release(user_id=user1.id, release_type="EBOOK", status="draft")
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    # Login as user2
    login_response = client.post(
        "/api/auth/login",
        json={"username": "user2", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Try update release owned by user1
    response = client.post(
        f"/api/wizard/{release_id}/metadata",
        json={"enriched_metadata": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "permission denied" in response.get_json()["message"].lower()


def test_wizard_update_metadata_no_data_provided(client, app) -> None:
    """Test update metadata when no data provided."""
    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(user_id=user.id, release_type="EBOOK", status="draft")
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Try update without data
    response = client.post(
        f"/api/wizard/{release_id}/metadata",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "no data provided" in response.get_json()["message"].lower()


def test_wizard_update_metadata_empty_enriched_metadata(client, app) -> None:
    """Test update metadata with empty enriched_metadata."""
    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(
            user_id=user.id,
            release_type="EBOOK",
            status="draft",
            release_metadata={"wizard_step": 5},
        )
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Update with empty metadata
    response = client.post(
        f"/api/wizard/{release_id}/metadata",
        json={"enriched_metadata": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    # Should still update wizard_step
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.release_metadata["wizard_step"] == 6


def test_wizard_update_metadata_user_not_found(client, app) -> None:
    """Test update metadata when user not found."""
    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        release = Release(user_id=user.id, release_type="EBOOK", status="draft")
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Delete user after login
    with app.app_context():
        db.session.delete(user)
        db.session.commit()

    # Try update
    response = client.post(
        f"/api/wizard/{release_id}/metadata",
        json={"enriched_metadata": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    # JWT might validate first (401) or endpoint checks user (404)
    assert response.status_code in [401, 404]
