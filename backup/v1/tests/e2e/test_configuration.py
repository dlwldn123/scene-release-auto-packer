"""
Tests E2E pour la configuration (préférences, chemins, destinations).
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


class TestPreferencesConfiguration:
    """Tests pour la configuration des préférences."""

    def test_create_preference(self, api_base_url: str, auth_headers: dict):
        """Test création préférence."""
        response = requests.post(
            f"{api_base_url}/preferences",
            headers=auth_headers,
            json={"key": "test_pref", "value": {"test": "value"}},
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_preference(self, api_base_url: str, auth_headers: dict):
        """Test récupération préférence."""
        # Créer préférence
        requests.post(
            f"{api_base_url}/preferences",
            headers=auth_headers,
            json={"key": "test_get_pref", "value": {"test": "value"}},
            timeout=5,
        )

        # Récupérer
        response = requests.get(
            f"{api_base_url}/preferences/test_get_pref", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "preference" in data


class TestPathsConfiguration:
    """Tests pour la configuration des chemins par groupe/type."""

    def test_create_path_config(self, api_base_url: str, auth_headers: dict):
        """Test création config chemin."""
        response = requests.post(
            f"{api_base_url}/paths/TESTGRP/EBOOK",
            headers=auth_headers,
            json={
                "output_dir": "/data/releases/TESTGRP",
                "destination_dir": "/ftp/TESTGRP",
            },
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_path_config(self, api_base_url: str, auth_headers: dict):
        """Test récupération config chemin."""
        # Créer config
        requests.post(
            f"{api_base_url}/paths/TESTGRP2/EBOOK",
            headers=auth_headers,
            json={
                "output_dir": "/data/releases/TESTGRP2",
                "destination_dir": "/ftp/TESTGRP2",
            },
            timeout=5,
        )

        # Récupérer
        response = requests.get(
            f"{api_base_url}/paths/TESTGRP2/EBOOK", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "output_dir" in data
        assert "destination_dir" in data

    def test_list_paths_by_group(self, api_base_url: str, auth_headers: dict):
        """Test liste configs par groupe."""
        response = requests.get(
            f"{api_base_url}/paths/groups", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "groups" in data


class TestDestinationsConfiguration:
    """Tests pour la configuration des destinations FTP/SFTP."""

    def test_create_destination(self, api_base_url: str, auth_headers: dict):
        """Test création destination FTP."""
        response = requests.post(
            f"{api_base_url}/destinations",
            headers=auth_headers,
            json={
                "name": "test_ftp",
                "type": "ftp",
                "host": "ftp.test.com",
                "port": 21,
                "username": "testuser",
                "password": "testpass",
                "path": "/releases/test",
            },
            timeout=5,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "destination" in data

        return data["destination"]["id"]

    def test_list_destinations(self, api_base_url: str, auth_headers: dict):
        """Test liste destinations."""
        response = requests.get(
            f"{api_base_url}/destinations", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "destinations" in data

    def test_get_destinations_by_group(self, api_base_url: str, auth_headers: dict):
        """Test destinations par groupe."""
        response = requests.get(
            f"{api_base_url}/destinations/groups/TESTGRP",
            headers=auth_headers,
            timeout=5,
        )

        # Peut retourner 200 (destinations trouvées) ou 404 (aucune)
        assert response.status_code in [200, 404]
