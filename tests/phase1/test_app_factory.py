"""Tests for Flask App Factory."""

from __future__ import annotations

import pytest

from web.app import create_app


def test_create_app_development() -> None:
    """Test creating app with development config."""
    app = create_app("development")
    assert app.config["DEBUG"] is True
    assert app.config["TESTING"] is False


def test_create_app_production() -> None:
    """Test creating app with production config."""
    app = create_app("production")
    assert app.config["DEBUG"] is False
    assert app.config["TESTING"] is False


def test_create_app_testing() -> None:
    """Test creating app with testing config."""
    app = create_app("testing")
    assert app.config["TESTING"] is True
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_create_app_default() -> None:
    """Test creating app with default config."""
    app = create_app()
    assert app is not None
    assert isinstance(app, type(create_app("development")))


def test_health_endpoint(client) -> None:
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "message" in data
