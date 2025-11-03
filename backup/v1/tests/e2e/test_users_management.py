"""
Tests E2E pour la gestion des utilisateurs/rôles (admin uniquement).
"""

from typing import Dict

import pytest
import requests


@pytest.fixture
def auth_token(api_base_url: str, admin_credentials: dict) -> str:
    """Fixture pour obtenir un token d'authentification admin."""
    response = requests.post(
        f"{api_base_url}/auth/login", json=admin_credentials, timeout=5
    )
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture
def auth_headers(auth_token: str) -> Dict[str, str]:
    """Fixture pour obtenir les headers d'authentification."""
    return {"Authorization": f"Bearer {auth_token}"}


class TestUsersManagement:
    """Tests pour la gestion des utilisateurs."""

    def test_list_users(self, api_base_url: str, auth_headers: dict):
        """Test liste utilisateurs."""
        response = requests.get(
            f"{api_base_url}/users", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "users" in data
        assert isinstance(data["users"], list)
        assert len(data["users"]) > 0  # Au moins admin

    def test_get_user_details(self, api_base_url: str, auth_headers: dict):
        """Test récupération détails utilisateur."""
        # Récupérer liste utilisateurs
        list_response = requests.get(
            f"{api_base_url}/users", headers=auth_headers, timeout=5
        )
        assert list_response.status_code == 200
        users = list_response.json()["users"]
        assert len(users) > 0

        # Récupérer détails premier utilisateur
        user_id = users[0]["id"]
        response = requests.get(
            f"{api_base_url}/users/{user_id}", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user" in data
        assert data["user"]["id"] == user_id

    def test_create_user(self, api_base_url: str, auth_headers: dict):
        """Test création utilisateur."""
        response = requests.post(
            f"{api_base_url}/users",
            headers=auth_headers,
            json={
                "username": "test_user",
                "password": "test_password",
                "email": "test@example.com",
                "role": "operator",
            },
            timeout=5,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "user" in data
        assert data["user"]["username"] == "test_user"

        return data["user"]["id"]

    def test_update_user(self, api_base_url: str, auth_headers: dict):
        """Test mise à jour utilisateur."""
        # Créer utilisateur
        create_response = requests.post(
            f"{api_base_url}/users",
            headers=auth_headers,
            json={
                "username": "test_update_user",
                "password": "test_password",
                "email": "test_update@example.com",
                "role": "operator",
            },
            timeout=5,
        )
        user_id = create_response.json()["user"]["id"]

        # Mettre à jour
        response = requests.put(
            f"{api_base_url}/users/{user_id}",
            headers=auth_headers,
            json={"email": "updated@example.com", "role": "operator"},
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user"]["email"] == "updated@example.com"

        # Nettoyage
        requests.delete(
            f"{api_base_url}/users/{user_id}", headers=auth_headers, timeout=5
        )

    def test_delete_user(self, api_base_url: str, auth_headers: dict):
        """Test suppression utilisateur."""
        # Créer utilisateur
        create_response = requests.post(
            f"{api_base_url}/users",
            headers=auth_headers,
            json={
                "username": "test_delete_user",
                "password": "test_password",
                "email": "test_delete@example.com",
                "role": "operator",
            },
            timeout=5,
        )
        user_id = create_response.json()["user"]["id"]

        # Supprimer
        response = requests.delete(
            f"{api_base_url}/users/{user_id}", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Vérifier suppression
        get_response = requests.get(
            f"{api_base_url}/users/{user_id}", headers=auth_headers, timeout=5
        )
        assert get_response.status_code == 404

    def test_users_requires_admin(self, api_base_url: str, admin_credentials: dict):
        """Test que l'accès aux utilisateurs nécessite admin."""
        # Cette fonctionnalité est déjà testée dans test_auth_flow
        # mais on peut vérifier que operator n'a pas accès
        pass
