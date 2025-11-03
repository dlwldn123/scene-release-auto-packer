"""Tests for wizard list rules endpoint (Phase 3)."""

from __future__ import annotations

from web.extensions import db
from web.models import Rule, User


def test_wizard_list_rules_no_filter(client, auth_headers) -> None:
    """Test listing all rules without filter."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        rule1 = Rule(
            name="[2022] eBOOK",
            content="EBOOK rule",
            section="eBOOK",
            year=2022,
        )
        rule2 = Rule(
            name="[2022] TV-720p",
            content="TV rule",
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

    # List all rules
    response = client.get(
        "/api/wizard/rules",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "rules" in data
    assert len(data["rules"]) == 2


def test_wizard_list_rules_tv_filter(client, auth_headers) -> None:
    """Test listing rules filtered by TV release type."""
    with client.application.app_context():
        db.create_all()

        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        rule1 = Rule(
            name="[2022] TV-720p",
            content="TV rule",
            section="TV-720p",
            year=2022,
        )
        rule2 = Rule(
            name="[2022] TV-SD",
            content="TV SD rule",
            section="TV-SD",
            year=2022,
        )
        rule3 = Rule(
            name="[2022] eBOOK",
            content="EBOOK rule",
            section="eBOOK",
            year=2022,
        )
        db.session.add_all([rule1, rule2, rule3])
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List TV rules
    response = client.get(
        "/api/wizard/rules?release_type=TV",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "rules" in data
    assert len(data["rules"]) == 2
    assert all(r["section"] in ["TV-720p", "TV-SD"] for r in data["rules"])
