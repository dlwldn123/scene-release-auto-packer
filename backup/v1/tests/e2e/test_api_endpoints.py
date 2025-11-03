"""
Tests E2E pour tous les endpoints API existants.
"""

from typing import Dict

import pytest
import requests


@pytest.fixture
def auth_token(api_base_url: str, admin_credentials: dict) -> str:
    """Fixture pour obtenir un token d'authentification."""
    response = requests.post(
        f"{api_base_url}/auth/login", json=admin_credentials, timeout=5
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def auth_headers(auth_token: str) -> Dict[str, str]:
    """Fixture pour obtenir les headers d'authentification."""
    return {"Authorization": f"Bearer {auth_token}"}


class TestJobsEndpoints:
    """Tests pour les endpoints jobs."""

    def test_list_jobs(self, api_base_url: str, auth_headers: dict):
        """Test liste jobs."""
        response = requests.get(f"{api_base_url}/jobs", headers=auth_headers, timeout=5)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "jobs" in data
        assert isinstance(data["jobs"], list)


class TestPreferencesEndpoints:
    """Tests pour les endpoints préférences."""

    def test_list_preferences(self, api_base_url: str, auth_headers: dict):
        """Test liste préférences."""
        response = requests.get(
            f"{api_base_url}/preferences", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "preferences" in data

    def test_create_preference(self, api_base_url: str, auth_headers: dict):
        """Test création préférence."""
        response = requests.post(
            f"{api_base_url}/preferences",
            headers=auth_headers,
            json={"key": "test_key", "value": {"test": "value"}},
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestPathsEndpoints:
    """Tests pour les endpoints chemins."""

    def test_get_path_config(self, api_base_url: str, auth_headers: dict):
        """Test récupération config chemin."""
        response = requests.get(
            f"{api_base_url}/paths/MYGRP/EBOOK", headers=auth_headers, timeout=5
        )

        # Peut retourner 200 (config existe) ou 404 (config n'existe pas)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True


class TestDestinationsEndpoints:
    """Tests pour les endpoints destinations."""

    def test_list_destinations(self, api_base_url: str, auth_headers: dict):
        """Test liste destinations."""
        response = requests.get(
            f"{api_base_url}/destinations", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "destinations" in data


class TestUsersEndpoints:
    """Tests pour les endpoints utilisateurs (admin uniquement)."""

    def test_list_users(self, api_base_url: str, auth_headers: dict):
        """Test liste utilisateurs (admin)."""
        response = requests.get(
            f"{api_base_url}/users", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "users" in data


class TestTemplatesEndpoints:
    """Tests pour les endpoints templates."""

    def test_list_templates(self, api_base_url: str, auth_headers: dict):
        """Test liste templates."""
        response = requests.get(
            f"{api_base_url}/templates", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "templates" in data


class TestWizardEndpoints:
    """Tests pour les endpoints wizard."""

    def test_get_preferences(self, api_base_url: str, auth_headers: dict):
        """Test récupération préférences wizard."""
        response = requests.get(
            f"{api_base_url}/wizard/preferences", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
