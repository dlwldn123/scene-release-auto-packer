"""
Tests d'intégration pour les blueprints Flask.

Vérifie que les endpoints API fonctionnent correctement.
"""

import json

import pytest
from flask import Flask

from web.app import create_app
from web.database import db
from web.models.job import Job, JobStatus
from web.models.user import User, UserRole


@pytest.fixture
def app():
    """Créer une instance Flask pour les tests."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Client de test Flask."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Créer un utilisateur de test."""
    with app.app_context():
        user = User(
            username="test_user",
            email="test@example.com",
            role=UserRole.ADMIN,
        )
        user.set_password("test_password")
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def auth_token(client, test_user):
    """Obtenir un token d'authentification."""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "test_user",
            "password": "test_password",
        },
    )
    data = json.loads(response.data)
    return data.get("token")


class TestAuthBlueprint:
    """Tests d'intégration pour le blueprint auth."""

    def test_login_success(self, client, test_user):
        """Test : Login réussi retourne token."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "test_user",
                "password": "test_password",
            },
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "token" in data

    def test_login_invalid_credentials(self, client):
        """Test : Login avec credentials invalides."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "invalid",
                "password": "wrong",
            },
        )

        assert response.status_code == 401

    def test_get_current_user(self, client, auth_token):
        """Test : Récupération utilisateur courant."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "user" in data


class TestJobsBlueprint:
    """Tests d'intégration pour le blueprint jobs."""

    def test_list_jobs(self, client, auth_token, app, test_user):
        """Test : Liste des jobs."""
        with app.app_context():
            # Créer quelques jobs de test
            for i in range(3):
                job = Job(
                    job_id=f"test-job-{i}",
                    user_id=test_user.id,
                    status=JobStatus.COMPLETED,
                    type="EBOOK",
                    group_name="TESTGRP",
                )
                db.session.add(job)
            db.session.commit()

        response = client.get(
            "/api/jobs",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "jobs" in data
        assert len(data["jobs"]) >= 3

    def test_get_job_details(self, client, auth_token, app, test_user):
        """Test : Détails d'un job."""
        with app.app_context():
            job = Job(
                job_id="test-job-details",
                user_id=test_user.id,
                status=JobStatus.PENDING,
                type="EBOOK",
                group_name="TESTGRP",
            )
            db.session.add(job)
            db.session.commit()
            job_id = job.job_id

        response = client.get(
            f"/api/jobs/{job_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["job"]["job_id"] == job_id

    def test_get_job_not_found(self, client, auth_token):
        """Test : Job introuvable retourne 404."""
        response = client.get(
            "/api/jobs/nonexistent-job-id",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 404


class TestHealthBlueprint:
    """Tests d'intégration pour le blueprint health."""

    def test_health_check(self, client, app):
        """Test : Health check retourne 200."""
        with app.app_context():
            response = client.get("/health")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "healthy"
            assert "database" in data


class TestPreferencesBlueprint:
    """Tests d'intégration pour le blueprint preferences."""

    def test_create_preference(self, client, auth_token, app, test_user):
        """Test : Création d'une préférence."""
        with app.app_context():
            response = client.post(
                "/api/preferences",
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "preference_key": "test_key",
                    "preference_value": {"option": "value"},
                },
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["success"] is True
            assert "preference" in data

    def test_list_preferences(self, client, auth_token):
        """Test : Liste des préférences."""
        response = client.get(
            "/api/preferences",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert "preferences" in data
