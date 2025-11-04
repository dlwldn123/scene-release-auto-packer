"""Tests for Wizard Step 5 - Analyze File endpoint."""

from __future__ import annotations

from web.extensions import db
from web.models import Group, Release, Rule, User


def test_wizard_analyze_file_success(client, app) -> None:
    """Test analyzing file successfully."""
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

        # Create release with file_path
        release = Release(
            user_id=user.id,
            group_id=group.id,
            release_type="EBOOK",
            status="draft",
            file_path="uploads/wizard/release_1_TestGroup-Author-Title-EPUB-en-2022-1234567890-eBook.epub",
            release_metadata={"wizard_step": 4, "file_size": 1024},
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

    # Analyze file
    response = client.post(
        f"/api/wizard/{release_id}/analyze",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "File analyzed successfully"
    assert "analysis" in data
    assert "file_path" in data["analysis"]
    assert "filename" in data["analysis"]

    # Verify release metadata was updated
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.release_metadata["wizard_step"] == 5
        assert "analysis" in release.release_metadata


def test_wizard_analyze_file_detects_group_and_author(client, app) -> None:
    """Test that analysis detects group and author from filename."""
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
            file_path="uploads/wizard/release_1_TestGroup-AuthorName-BookTitle-EPUB.epub",
            release_metadata={"wizard_step": 4, "file_size": 1024},
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

    # Analyze file
    response = client.post(
        f"/api/wizard/{release_id}/analyze",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    analysis = data["analysis"]
    assert analysis.get("detected_group") == "TestGroup"
    assert analysis.get("detected_author") == "AuthorName"


def test_wizard_analyze_file_requires_auth(client, app) -> None:
    """Test that analyze requires authentication."""
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
            file_path="test.epub",
        )
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    # Try analyze without auth
    response = client.post(f"/api/wizard/{release_id}/analyze")

    assert response.status_code == 401


def test_wizard_analyze_file_release_not_found(client, app) -> None:
    """Test analyze when release not found."""
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

    # Try analyze non-existent release
    response = client.post(
        "/api/wizard/99999/analyze",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert "release not found" in response.get_json()["message"].lower()


def test_wizard_analyze_file_permission_denied(client, app) -> None:
    """Test analyze when user doesn't own the release."""
    with app.app_context():
        db.create_all()

        user1 = User(username="user1", email="user1@example.com")
        user1.set_password("password123")
        user2 = User(username="user2", email="user2@example.com")
        user2.set_password("password123")
        db.session.add_all([user1, user2])
        db.session.commit()

        release = Release(
            user_id=user1.id,
            release_type="EBOOK",
            status="draft",
            file_path="test.epub",
        )
        db.session.add(release)
        db.session.commit()
        release_id = release.id

    # Login as user2
    login_response = client.post(
        "/api/auth/login",
        json={"username": "user2", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Try analyze release owned by user1
    response = client.post(
        f"/api/wizard/{release_id}/analyze",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "permission denied" in response.get_json()["message"].lower()


def test_wizard_analyze_file_no_file_uploaded(client, app) -> None:
    """Test analyze when no file uploaded."""
    with app.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Create release without file_path
        release = Release(
            user_id=user.id,
            release_type="EBOOK",
            status="draft",
            file_path=None,
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

    # Try analyze without file
    response = client.post(
        f"/api/wizard/{release_id}/analyze",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "no file uploaded" in response.get_json()["message"].lower()


def test_wizard_analyze_file_user_not_found(client, app) -> None:
    """Test analyze when user not found."""
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
            file_path="test.epub",
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

    # Delete user after login
    with app.app_context():
        db.session.delete(user)
        db.session.commit()

    # Try analyze
    response = client.post(
        f"/api/wizard/{release_id}/analyze",
        headers={"Authorization": f"Bearer {token}"},
    )

    # JWT might validate first (401) or endpoint checks user (404)
    assert response.status_code in [401, 404]
