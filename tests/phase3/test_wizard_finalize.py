"""Tests for Wizard Step 9 - Finalize Release endpoint."""

from __future__ import annotations

from web.extensions import db
from web.models import Group, Job, Release, Rule, User


def test_wizard_finalize_release_success(client, app) -> None:
    """Test finalizing release successfully."""
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
            release_metadata={"wizard_step": 8},
        )
        db.session.add(release)
        db.session.flush()

        # Create job
        job = Job(
            release_id=release.id,
            created_by=user.id,
            status="draft",
            config_json={"group": "TestGroup"},
        )
        db.session.add(job)
        db.session.commit()
        release_id = release.id
        job_id = job.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Finalize release
    response = client.post(
        f"/api/wizard/{release_id}/finalize",
        json={"destination_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Release finalized successfully"
    assert data["release_id"] == release_id
    assert data["job_id"] == job_id
    assert data["status"] == "ready"

    # Verify release was updated
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.status == "ready"
        assert release.release_metadata["wizard_step"] == 9
        assert release.release_metadata["completed"] is True
        assert release.release_metadata["destination_id"] == 1

        # Verify job was updated
        job = db.session.get(Job, job_id)
        assert job.status == "ready"
        assert job.config_json["destination_id"] == 1


def test_wizard_finalize_release_no_destination(client, app) -> None:
    """Test finalizing release without destination."""
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
            release_metadata={"wizard_step": 8},
        )
        db.session.add(release)
        db.session.flush()

        job = Job(release_id=release.id, created_by=user.id, status="draft")
        db.session.add(job)
        db.session.commit()
        release_id = release.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Finalize without destination
    response = client.post(
        f"/api/wizard/{release_id}/finalize",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Release finalized successfully"

    # Verify release was updated
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.status == "ready"
        assert release.release_metadata["wizard_step"] == 9
        assert release.release_metadata["completed"] is True


def test_wizard_finalize_release_no_job(client, app) -> None:
    """Test finalizing release when no job exists."""
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
            release_metadata={"wizard_step": 8},
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

    # Finalize release (no job exists)
    response = client.post(
        f"/api/wizard/{release_id}/finalize",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Release finalized successfully"
    assert data["job_id"] is None

    # Verify release was updated
    with app.app_context():
        release = db.session.get(Release, release_id)
        assert release.status == "ready"


def test_wizard_finalize_release_requires_auth(client, app) -> None:
    """Test that finalize requires authentication."""
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

    # Try finalize without auth
    response = client.post(
        f"/api/wizard/{release_id}/finalize",
        json={},
    )

    assert response.status_code == 401


def test_wizard_finalize_release_not_found(client, app) -> None:
    """Test finalize when release not found."""
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

    # Try finalize non-existent release
    response = client.post(
        "/api/wizard/99999/finalize",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert "release not found" in response.get_json()["message"].lower()


def test_wizard_finalize_release_permission_denied(client, app) -> None:
    """Test finalize when user doesn't own the release."""
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

    # Try finalize release owned by user1
    response = client.post(
        f"/api/wizard/{release_id}/finalize",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "permission denied" in response.get_json()["message"].lower()


def test_wizard_finalize_release_updates_job_config(client, app) -> None:
    """Test that finalize updates job config_json."""
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
            release_metadata={"wizard_step": 8},
        )
        db.session.add(release)
        db.session.flush()

        job = Job(
            release_id=release.id,
            created_by=user.id,
            status="draft",
            config_json={"group": "TestGroup"},
        )
        db.session.add(job)
        db.session.commit()
        release_id = release.id
        job_id = job.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Finalize with destination
    response = client.post(
        f"/api/wizard/{release_id}/finalize",
        json={"destination_id": 42},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    # Verify job config was updated
    with app.app_context():
        job = db.session.get(Job, job_id)
        assert job.config_json["destination_id"] == 42
        assert job.config_json["group"] == "TestGroup"  # Existing config preserved


def test_wizard_finalize_release_user_not_found(client, app) -> None:
    """Test finalize when user not found."""
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

    # Try finalize
    response = client.post(
        f"/api/wizard/{release_id}/finalize",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    # JWT might validate first (401) or endpoint checks user (404)
    assert response.status_code in [401, 404]
