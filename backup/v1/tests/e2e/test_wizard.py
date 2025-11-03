"""
Tests E2E pour le wizard de packaging.
"""

import tempfile
from pathlib import Path

import pytest
import requests


class TestWizardE2E:
    """Tests E2E pour le wizard de packaging."""

    def test_validate_step_group(self, flask_server: str, test_token: str):
        """
        Test : Validation étape 1 (nom groupe).
        """
        base_url = flask_server

        # Test validation groupe valide
        response = requests.post(
            f"{base_url}/api/wizard/step/validate",
            headers={
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json",
            },
            json={
                "step": 1,
                "data": {"group": "MYGRP"},
            },
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Should succeed"
        assert data["valid"] is True, "Should be valid"

    def test_validate_step_group_invalid(self, flask_server: str, test_token: str):
        """
        Test : Validation étape 1 échoue avec groupe vide.
        """
        base_url = flask_server

        response = requests.post(
            f"{base_url}/api/wizard/step/validate",
            headers={
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json",
            },
            json={
                "step": 1,
                "data": {"group": ""},
            },
            timeout=5,
        )

        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert data["success"] is False, "Should fail"
        assert "errors" in data, "Errors should be present"

    def test_validate_step_type(self, flask_server: str, test_token: str):
        """
        Test : Validation étape 2 (type release).
        """
        base_url = flask_server

        # Test validation type valide
        response = requests.post(
            f"{base_url}/api/wizard/step/validate",
            headers={
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json",
            },
            json={
                "step": 2,
                "data": {"type": "EBOOK"},
            },
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["valid"] is True, "Should be valid"

    def test_get_wizard_preferences(self, flask_server: str, test_token: str):
        """
        Test : Récupération préférences wizard.
        """
        base_url = flask_server

        response = requests.get(
            f"{base_url}/api/wizard/preferences?key=MYGRP+EBOOK+default",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Should succeed"
        # Préférence peut être None si n'existe pas
        assert "preference" in data, "Preference field should be present"

    def test_save_wizard_preferences(self, flask_server: str, test_token: str):
        """
        Test : Sauvegarde préférences wizard.
        """
        base_url = flask_server

        preference_data = {
            "key": "test_wizard_pref",
            "value": {"template_id": 1, "enable_api": True},
        }

        response = requests.post(
            f"{base_url}/api/wizard/preferences",
            headers={
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json",
            },
            json=preference_data,
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Should succeed"
