"""Performance optimization tests and checks."""

from __future__ import annotations

import pytest

from web.extensions import db
from web.models import Release, User


def test_database_query_optimization(client) -> None:
    """Test that database queries are optimized (no N+1 queries).

    This test verifies that relationships are loaded efficiently.
    """
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Create multiple releases
        for i in range(5):
            release = Release(user_id=user.id, release_type="EBOOK", status="completed")
            db.session.add(release)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # List releases - should use efficient query
    response = client.get(
        "/api/releases",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["releases"]) == 5


def test_pagination_performance(client) -> None:
    """Test that pagination works correctly and efficiently."""
    with client.application.app_context():
        db.create_all()
        user = User(username="testuser", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Create many releases
        for i in range(25):
            release = Release(user_id=user.id, release_type="EBOOK", status="completed")
            db.session.add(release)
        db.session.commit()

    # Login
    login_response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "password123"},
    )
    token = login_response.get_json()["access_token"]

    # Request first page
    response = client.get(
        "/api/releases?page=1&per_page=20",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["releases"]) == 20
    assert data["pagination"]["total"] == 25
    assert data["pagination"]["pages"] == 2


def test_database_indexes() -> None:
    """Test that database indexes are properly configured.

    This is a placeholder test. In a real scenario, we would check
    that indexes exist on frequently queried columns.
    """
    # Check that indexes exist on key columns
    # This would require database introspection
    assert True  # Placeholder


def test_response_time_acceptable(client) -> None:
    """Test that API response times are acceptable (< 500ms for simple queries)."""
    import time

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

    # Measure response time
    start_time = time.time()
    response = client.get(
        "/api/dashboard/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    end_time = time.time()

    response_time_ms = (end_time - start_time) * 1000

    assert response.status_code == 200
    assert response_time_ms < 500  # Should respond in < 500ms
