"""
Tests E2E pour le flux wizard complet.
"""

from pathlib import Path
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


class TestWizardFlow:
    """Tests pour le flux wizard complet."""

    def test_wizard_step_validation_group(self, api_base_url: str, auth_headers: dict):
        """Test validation étape 1 (nom groupe)."""
        response = requests.post(
            f"{api_base_url}/wizard/step/validate",
            headers=auth_headers,
            json={"step": 1, "data": {"group": "MYGRP"}},
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["valid"] is True

    def test_wizard_step_validation_type(self, api_base_url: str, auth_headers: dict):
        """Test validation étape 2 (type release)."""
        response = requests.post(
            f"{api_base_url}/wizard/step/validate",
            headers=auth_headers,
            json={"step": 2, "data": {"type": "EBOOK"}},
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["valid"] is True

    def test_wizard_step_validation_files(self, api_base_url: str, auth_headers: dict):
        """Test validation étape 4 (fichiers)."""
        # Test avec source local
        response = requests.post(
            f"{api_base_url}/wizard/step/validate",
            headers=auth_headers,
            json={"step": 4, "data": {"source": "local", "path": "/path/to/file.pdf"}},
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_wizard_get_preferences(self, api_base_url: str, auth_headers: dict):
        """Test récupération préférences wizard."""
        response = requests.get(
            f"{api_base_url}/wizard/preferences", headers=auth_headers, timeout=5
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_wizard_save_preferences(self, api_base_url: str, auth_headers: dict):
        """Test sauvegarde préférences wizard."""
        response = requests.post(
            f"{api_base_url}/wizard/preferences",
            headers=auth_headers,
            json={"key": "wizard_test", "value": {"group": "TESTGRP", "type": "EBOOK"}},
            timeout=5,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_wizard_pack_validation(self, api_base_url: str, auth_headers: dict):
        """Test validation requête packaging wizard (sans exécution)."""
        # Test que le schéma de validation fonctionne
        # Ne pas exécuter le packaging car nécessite un fichier réel
        payload = {
            "group": "TESTGRP",
            "type": "EBOOK",
            "files": {
                "source": "local",
                "path": "/nonexistent/file.pdf",
            },  # Fichier qui n'existe pas
            "metadata": {},
            "enrichment": {"use_apis": False},
            "export": {"download": True},
        }

        response = requests.post(
            f"{api_base_url}/wizard/pack",
            headers=auth_headers,
            json=payload,
            timeout=10,
        )

        # Devrait retourner 404 (fichier introuvable) ou 400 (validation)
        # mais pas 500 (erreur serveur)
        assert response.status_code in [400, 404]

    def test_wizard_step_validation_invalid(
        self, api_base_url: str, auth_headers: dict
    ):
        """Test validation étape avec données invalides."""
        # Test étape 1 sans group
        response = requests.post(
            f"{api_base_url}/wizard/step/validate",
            headers=auth_headers,
            json={"step": 1, "data": {}},  # Pas de group
            timeout=5,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["valid"] is False
        assert "errors" in data

    def test_wizard_step_validation_invalid_type(
        self, api_base_url: str, auth_headers: dict
    ):
        """Test validation étape 2 avec type invalide."""
        response = requests.post(
            f"{api_base_url}/wizard/step/validate",
            headers=auth_headers,
            json={"step": 2, "data": {"type": "INVALID"}},
            timeout=5,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
