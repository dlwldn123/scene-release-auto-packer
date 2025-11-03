"""Tests for Wizard API."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import Job, Rule, User


def test_save_draft_step1(client) -> None:
    """Test saving draft step 1 (group)."""
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

    # Save draft step 1
    response = client.post(
        "/api/wizard/draft",
        json={"step": 1, "step_data": {"group": "TestGroup"}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "job_id" in data
    assert data["step"] == 1


def test_save_draft_step2(client) -> None:
    """Test saving draft step 2 (release type)."""
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

    # Save draft step 2
    response = client.post(
        "/api/wizard/draft",
        json={"step": 2, "step_data": {"release_type": "EBOOK"}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "job_id" in data


def test_save_draft_invalid_group(client) -> None:
    """Test saving draft with invalid group format."""
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

    # Save draft with invalid group
    response = client.post(
        "/api/wizard/draft",
        json={"step": 1, "step_data": {"group": "Invalid Group Name!"}},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400


def test_list_rules(client) -> None:
    """Test listing rules."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)

        rule1 = Rule(
            name="[2022] eBOOK",
            content="Full rule content",
            scene="eBOOK",
            section="EBOOK",
            year=2022,
        )
        rule2 = Rule(
            name="[2022] TV",
            content="Full rule content",
            scene="TV",
            section="TV",
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

    # List rules
    response = client.get(
        "/api/wizard/rules?release_type=EBOOK",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "rules" in data
    assert len(data["rules"]) > 0
