"""Tests for Dashboard API."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import Job, Release, User


def test_dashboard_stats(client, auth_headers) -> None:
    """Test dashboard stats endpoint."""
    with client.application.app_context():
        db.create_all()

        # Create user
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Create some test data
        release1 = Release(user_id=user.id, release_type="EBOOK", status="completed")
        release2 = Release(user_id=user.id, release_type="TV", status="draft")
        db.session.add_all([release1, release2])

        job1 = Job(release_id=release1.id, created_by=user.id, status="completed")
        db.session.add(job1)
        db.session.commit()

    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Get dashboard stats
    response = client.get(
        "/api/dashboard/stats",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "total_releases" in data
    assert "total_jobs" in data
    assert "user_releases" in data
    assert "user_jobs" in data
    assert "user" in data
    assert data["user_releases"] == 2
    assert data["user_jobs"] == 1


def test_dashboard_stats_requires_auth(client) -> None:
    """Test that dashboard stats requires authentication."""
    response = client.get("/api/dashboard/stats")

    assert response.status_code == 401
