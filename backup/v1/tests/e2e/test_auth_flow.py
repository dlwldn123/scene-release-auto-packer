"""
Tests E2E pour le flux d'authentification.
"""

from typing import Dict

import pytest
import requests


class TestAuthFlow:
    """Tests pour le flux d'authentification complet."""

    def test_login_success(self, base_url: str, admin_credentials: dict):
        """Test login avec credentials valides."""
        response = requests.post(
            f"{base_url}/api/auth/login", json=admin_credentials, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data
        assert data["role"] == "admin"
        assert data["user_id"] is not None

        return data["token"]

    def test_login_failure(self, base_url: str):
        """Test login avec credentials invalides."""
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"username": "invalid", "password": "invalid"},
            timeout=5,
        )

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_get_current_user(self, base_url: str, admin_credentials: dict):
        """Test récupération utilisateur courant après login."""
        # Login
        login_response = requests.post(
            f"{base_url}/api/auth/login", json=admin_credentials, timeout=5
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]

        # Get current user
        response = requests.get(
            f"{base_url}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user" in data
        assert data["user"]["username"] == admin_credentials["username"]
        assert data["user"]["role"] == "admin"

    def test_protected_endpoint_without_auth(self, api_base_url: str):
        """Test accès endpoint protégé sans authentification."""
        response = requests.get(f"{api_base_url}/jobs", timeout=5)

        assert response.status_code == 401

    def test_protected_endpoint_with_auth(
        self, api_base_url: str, admin_credentials: dict
    ):
        """Test accès endpoint protégé avec authentification."""
        # Login
        login_response = requests.post(
            f"{api_base_url}/auth/login", json=admin_credentials, timeout=5
        )
        token = login_response.json()["token"]

        # Accès endpoint protégé
        response = requests.get(
            f"{api_base_url}/jobs",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
