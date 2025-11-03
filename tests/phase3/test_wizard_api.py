"""Tests for Wizard API endpoints (Phase 3)."""

from __future__ import annotations

from web.extensions import db
from web.models import Group, Release, Rule, User


def test_wizard_create_draft(client, auth_headers) -> None:
    """Test creating draft release via wizard."""
    with client.application.app_context():
        db.create_all()

        # Create user
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Create group
        group = Group(name="TestGroup")
        db.session.add(group)
        db.session.commit()

        # Create rule
        rule = Rule(
            name="[2022] eBOOK",
            content="Test rule content",
            scene="English",
            section="eBOOK",
            year=2022,
        )
        db.session.add(rule)
        db.session.commit()
        rule_id = rule.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Create draft release via wizard
    response = client.post(
        "/api/wizard/draft",
        json={
            "group": "TestGroup",
            "release_type": "EBOOK",
            "rule_id": rule_id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "release_id" in data
    assert "job_id" in data

    # Verify release was created
    with client.application.app_context():
        release = Release.query.get(data["release_id"])
        assert release is not None
        assert release.release_type == "EBOOK"
        assert release.status == "draft"


def test_wizard_create_draft_requires_auth(client) -> None:
    """Test that wizard draft creation requires authentication."""
    response = client.post(
        "/api/wizard/draft",
        json={
            "group": "TestGroup",
            "release_type": "EBOOK",
        },
    )

    assert response.status_code == 401
