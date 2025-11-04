"""Tests for Wizard Step 8 - Update Options endpoint."""

from __future__ import annotations

from web.extensions import db
from web.models import Group, Release, Rule, User


def test_wizard_update_options_success(client, app) -> None:
    """Test updating packaging options successfully."""
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
            release_metadata={"wizard_step": 7},
            config={},
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

    # Update options
    options = {
        "create_nfo": True,
        "create_diz": True,
        "create_sfv": True,
        "zip_level": 6,
    }

    response = client.post(
        f"/api/wizard/{release_id}/options",
        json={"options": options},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Options updated successfully"
    assert "options" in data

    # Verify release config was updated
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.release_metadata["wizard_step"] == 8
        assert release.config["create_nfo"] is True
        assert release.config["zip_level"] == 6


def test_wizard_update_options_merges_with_existing(client, app) -> None:
    """Test that options update merges with existing config."""
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
            release_metadata={"wizard_step": 7},
            config={"existing_option": "existing_value"},
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

    # Update options
    options = {"new_option": "new_value"}

    response = client.post(
        f"/api/wizard/{release_id}/options",
        json={"options": options},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    # Verify config was merged
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.config["existing_option"] == "existing_value"
        assert release.config["new_option"] == "new_value"


def test_wizard_update_options_requires_auth(client, app) -> None:
    """Test that update options requires authentication."""
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
        f"/api/wizard/{release_id}/options",
        json={"options": {}},
    )

    assert response.status_code == 401


def test_wizard_update_options_release_not_found(client, app) -> None:
    """Test update options when release not found."""
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
        "/api/wizard/99999/options",
        json={"options": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert "release not found" in response.get_json()["message"].lower()


def test_wizard_update_options_permission_denied(client, app) -> None:
    """Test update options when user doesn't own the release."""
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
        f"/api/wizard/{release_id}/options",
        json={"options": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "permission denied" in response.get_json()["message"].lower()


def test_wizard_update_options_no_data_provided(client, app) -> None:
    """Test update options when no data provided."""
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
        f"/api/wizard/{release_id}/options",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "no data provided" in response.get_json()["message"].lower()


def test_wizard_update_options_empty_options(client, app) -> None:
    """Test update options with empty options dict."""
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
            release_metadata={"wizard_step": 7},
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

    # Update with empty options
    response = client.post(
        f"/api/wizard/{release_id}/options",
        json={"options": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    # Should still update wizard_step
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.release_metadata["wizard_step"] == 8


def test_wizard_update_options_user_not_found(client, app) -> None:
    """Test update options when user not found."""
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
        f"/api/wizard/{release_id}/options",
        json={"options": {}},
        headers={"Authorization": f"Bearer {token}"},
    )

    # JWT might validate first (401) or endpoint checks user (404)
    assert response.status_code in [401, 404]
