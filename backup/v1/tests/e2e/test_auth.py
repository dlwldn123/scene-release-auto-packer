"""
Tests E2E pour l'authentification avec Playwright MCP.
"""

from typing import Any, Dict

import pytest
import requests


class TestAuthenticationE2E:
    """Tests E2E pour l'authentification (login/logout)."""

    def test_login_success(self, flask_server: str):
        """
        Test : Login réussi avec credentials valides.

        RED : Écriture test qui échoue d'abord
        GREEN : Implémenter fonctionnalité pour faire passer le test
        """
        base_url = flask_server

        # Test login
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={
                "username": "test_admin",
                "password": "test_password",
            },
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Login should succeed"
        assert "token" in data, "Token should be present"
        assert data["role"] == "admin", "Role should be admin"
        assert data["user_id"] is not None, "User ID should be present"

    def test_login_invalid_credentials(self, flask_server: str):
        """
        Test : Login échoue avec credentials invalides.
        """
        base_url = flask_server

        response = requests.post(
            f"{base_url}/api/auth/login",
            json={
                "username": "invalid_user",
                "password": "wrong_password",
            },
            timeout=5,
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        data = response.json()
        assert data["success"] is False, "Login should fail"
        assert "error" in data, "Error message should be present"

    def test_get_current_user(self, flask_server: str, test_token: str):
        """
        Test : Récupération utilisateur courant avec token valide.
        """
        base_url = flask_server

        response = requests.get(
            f"{base_url}/api/auth/me",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Should succeed"
        assert "user" in data, "User data should be present"
        assert data["user"]["username"] == "test_admin", "Username should match"
        assert data["user"]["role"] == "admin", "Role should be admin"

    def test_get_current_user_without_token(self, flask_server: str):
        """
        Test : Accès protégé sans token échoue.
        """
        base_url = flask_server

        response = requests.get(
            f"{base_url}/api/auth/me",
            timeout=5,
        )

        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_refresh_token(self, flask_server: str, test_token: str):
        """
        Test : Refresh token fonctionne.
        """
        base_url = flask_server

        response = requests.post(
            f"{base_url}/api/auth/refresh",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Refresh should succeed"
        assert "token" in data, "New token should be present"
        assert data["token"] != test_token, "Token should be different"
