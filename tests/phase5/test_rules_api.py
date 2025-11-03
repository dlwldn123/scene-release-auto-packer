"""Tests for Rules API."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import Rule, User


def test_list_rules(client) -> None:
    """Test listing rules."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        rule1 = Rule(
            name="Rule 1", content="Content 1", scene="EBOOK", section="naming"
        )
        rule2 = Rule(
            name="Rule 2", content="Content 2", scene="TV", section="packaging"
        )
        db.session.add_all([rule1, rule2])
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List rules
    response = client.get(
        "/api/rules",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "rules" in data
    assert "pagination" in data
    assert len(data["rules"]) == 2


def test_list_rules_with_filters(client) -> None:
    """Test listing rules with filters."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        rule1 = Rule(
            name="Rule 1", content="Content 1", scene="EBOOK", section="naming"
        )
        rule2 = Rule(
            name="Rule 2", content="Content 2", scene="TV", section="packaging"
        )
        db.session.add_all([rule1, rule2])
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List rules filtered by scene
    response = client.get(
        "/api/rules?scene=EBOOK",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["rules"]) == 1
    assert data["rules"][0]["scene"] == "EBOOK"


def test_get_rule(client) -> None:
    """Test getting rule by ID."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        rule = Rule(name="Rule 1", content="Content 1", scene="EBOOK")
        db.session.add(rule)
        db.session.commit()
        rule_id = rule.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Get rule
    response = client.get(
        f"/api/rules/{rule_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "rule" in data
    assert data["rule"]["id"] == rule_id


def test_create_rule(client) -> None:
    """Test creating rule."""
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

    # Create rule
    response = client.post(
        "/api/rules",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "New Rule", "content": "Rule content", "scene": "EBOOK"},
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "rule" in data
    assert data["rule"]["name"] == "New Rule"


def test_update_rule(client) -> None:
    """Test updating rule."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        rule = Rule(name="Rule 1", content="Content 1", scene="EBOOK")
        db.session.add(rule)
        db.session.commit()
        rule_id = rule.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Update rule
    response = client.put(
        f"/api/rules/{rule_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Updated Rule", "content": "Updated content"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["rule"]["name"] == "Updated Rule"
    assert data["rule"]["content"] == "Updated content"


def test_delete_rule(client) -> None:
    """Test deleting rule."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        rule = Rule(name="Rule 1", content="Content 1", scene="EBOOK")
        db.session.add(rule)
        db.session.commit()
        rule_id = rule.id

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Delete rule
    response = client.delete(
        f"/api/rules/{rule_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    # Verify deleted
    get_response = client.get(
        f"/api/rules/{rule_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 404
