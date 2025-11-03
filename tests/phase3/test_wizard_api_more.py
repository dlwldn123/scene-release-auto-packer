"""Additional tests for Wizard API endpoints (Phase 3)."""

from __future__ import annotations

from web.extensions import db
from web.models import Rule, User


def test_wizard_list_rules(client, auth_headers) -> None:
    """Test listing rules filtered by release type."""
    with client.application.app_context():
        db.create_all()

        # Create user
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Create rules
        rule1 = Rule(
            name="[2022] eBOOK",
            content="EBOOK rule content",
            scene="English",
            section="eBOOK",
            year=2022,
        )
        rule2 = Rule(
            name="[2022] TV-720p",
            content="TV rule content",
            scene="English",
            section="TV-720p",
            year=2022,
        )
        db.session.add_all([rule1, rule2])
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List EBOOK rules
    response = client.get(
        "/api/wizard/rules?release_type=EBOOK",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "rules" in data
    assert len(data["rules"]) == 1
    assert data["rules"][0]["section"] == "eBOOK"


def test_wizard_create_draft_invalid_group(client, auth_headers) -> None:
    """Test creating draft with invalid group."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        rule = Rule(
            name="[2022] eBOOK",
            content="Test rule",
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

    # Create draft with empty group
    response = client.post(
        "/api/wizard/draft",
        json={
            "group": "",
            "release_type": "EBOOK",
            "rule_id": rule_id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "Group is required" in response.get_json()["message"]


def test_wizard_create_draft_invalid_rule(client, auth_headers) -> None:
    """Test creating draft with invalid rule ID."""
    with client.application.app_context():
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

    # Create draft with non-existent rule
    response = client.post(
        "/api/wizard/draft",
        json={
            "group": "TestGroup",
            "release_type": "EBOOK",
            "rule_id": 99999,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert "Rule not found" in response.get_json()["message"]
