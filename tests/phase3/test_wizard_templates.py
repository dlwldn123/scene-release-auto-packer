"""Tests for Wizard Step 7 - Templates endpoint."""

from __future__ import annotations

from web.extensions import db
from web.models import Group, Release, Rule, User


def test_wizard_list_templates_success(client, app) -> None:
    """Test listing templates successfully."""
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
            release_metadata={"wizard_step": 6},
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

    # List templates
    response = client.get(
        f"/api/wizard/{release_id}/templates",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "templates" in data
    assert len(data["templates"]) >= 1
    assert data["templates"][0]["id"] == 1
    assert data["templates"][0]["name"] == "Default Template"


def test_wizard_select_template_success(client, app) -> None:
    """Test selecting template successfully."""
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
            release_metadata={"wizard_step": 6},
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

    # Select template
    response = client.post(
        f"/api/wizard/{release_id}/templates",
        json={"template_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Template selected successfully"
    assert data["template_id"] == 1

    # Verify release metadata was updated
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.release_metadata["wizard_step"] == 7
        assert release.release_metadata["template_id"] == 1


def test_wizard_select_template_none(client, app) -> None:
    """Test selecting no template (None)."""
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
            release_metadata={"wizard_step": 6},
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

    # Select template None
    response = client.post(
        f"/api/wizard/{release_id}/templates",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Template selected successfully"

    # Verify release metadata was updated
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.release_metadata["wizard_step"] == 7


def test_wizard_templates_requires_auth(client, app) -> None:
    """Test that templates endpoints require authentication."""
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

    # Try GET without auth
    response = client.get(f"/api/wizard/{release_id}/templates")
    assert response.status_code == 401

    # Try POST without auth
    response = client.post(
        f"/api/wizard/{release_id}/templates",
        json={"template_id": 1},
    )
    assert response.status_code == 401


def test_wizard_templates_release_not_found(client, app) -> None:
    """Test templates when release not found."""
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

    # Try GET non-existent release
    response = client.get(
        "/api/wizard/99999/templates",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

    # Try POST non-existent release
    response = client.post(
        "/api/wizard/99999/templates",
        json={"template_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_wizard_templates_permission_denied(client, app) -> None:
    """Test templates when user doesn't own the release."""
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

    # Try GET release owned by user1
    response = client.get(
        f"/api/wizard/{release_id}/templates",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403

    # Try POST release owned by user1
    response = client.post(
        f"/api/wizard/{release_id}/templates",
        json={"template_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_wizard_templates_user_not_found(client, app) -> None:
    """Test templates when user not found."""
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

    # Try GET
    response = client.get(
        f"/api/wizard/{release_id}/templates",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in [401, 404]

    # Try POST
    response = client.post(
        f"/api/wizard/{release_id}/templates",
        json={"template_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code in [401, 404]
