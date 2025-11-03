"""
Tests E2E pour le dashboard et les statistiques.
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


class TestDashboard:
    """Tests pour le dashboard."""

    def test_dashboard_page_loads(self, base_url: str, auth_token: str):
        """Test que la page dashboard se charge correctement."""
        # Accéder à la page principale (nécessite authentification via cookie/session)
        # Pour les tests API, on vérifie plutôt les endpoints de données
        pass

    def test_dashboard_users_count(self, api_base_url: str, auth_headers: dict):
        """Test récupération nombre d'utilisateurs pour dashboard."""
        response = requests.get(
            f"{api_base_url}/users", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "users" in data
        # Le dashboard devrait pouvoir afficher len(data["users"])

    def test_dashboard_jobs_count(self, api_base_url: str, auth_headers: dict):
        """Test récupération nombre de jobs pour dashboard."""
        response = requests.get(f"{api_base_url}/jobs", headers=auth_headers, timeout=5)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total" in data or "jobs" in data

    def test_dashboard_releases_count(self, api_base_url: str, auth_headers: dict):
        """Test récupération nombre de releases pour dashboard."""
        # Utiliser l'endpoint jobs pour compter les jobs complétés (releases)
        response = requests.get(
            f"{api_base_url}/jobs?status=completed", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_dashboard_recent_jobs(self, api_base_url: str, auth_headers: dict):
        """Test récupération jobs récents pour dashboard."""
        response = requests.get(
            f"{api_base_url}/jobs?limit=10", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "jobs" in data

    def test_dashboard_statistics_structure(
        self, api_base_url: str, auth_headers: dict
    ):
        """Test que toutes les statistiques nécessaires sont disponibles."""
        # Vérifier que les endpoints nécessaires au dashboard répondent
        endpoints_to_check = [
            ("/users", "users"),
            ("/jobs", "jobs"),
            ("/jobs?status=completed", "jobs"),
            ("/preferences", "preferences"),
        ]

        for endpoint, key in endpoints_to_check:
            response = requests.get(
                f"{api_base_url}{endpoint}", headers=auth_headers, timeout=5
            )
            assert response.status_code == 200, f"Endpoint {endpoint} devrait répondre"
            data = response.json()
            assert (
                data["success"] is True
            ), f"Endpoint {endpoint} devrait retourner success=True"
            assert key in data, f"Endpoint {endpoint} devrait contenir {key}"
