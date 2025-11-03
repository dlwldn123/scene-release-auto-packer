"""
Tests E2E pour les préférences utilisateur.
"""

import json

import pytest
import requests


class TestPreferencesE2E:
    """Tests E2E pour la gestion des préférences."""

    def test_list_user_preferences(self, flask_server: str, test_token: str):
        """
        Test : Liste des préférences utilisateur.
        """
        base_url = flask_server

        response = requests.get(
            f"{base_url}/api/preferences",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Should succeed"
        assert "preferences" in data, "Preferences list should be present"
        assert isinstance(data["preferences"], list), "Preferences should be a list"

    def test_create_preference(self, flask_server: str, test_token: str):
        """
        Test : Création d'une préférence utilisateur.
        """
        base_url = flask_server

        preference_data = {
            "preference_key": "test_key",
            "preference_value": {"option1": "value1", "option2": True},
        }

        response = requests.post(
            f"{base_url}/api/preferences",
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
        assert "preference" in data, "Preference should be present"
        assert data["preference"]["preference_key"] == "test_key", "Key should match"

    def test_get_preference(self, flask_server: str, test_token: str):
        """
        Test : Récupération d'une préférence spécifique.
        """
        base_url = flask_server

        # Créer d'abord une préférence
        preference_data = {
            "preference_key": "test_get_key",
            "preference_value": {"test": "value"},
        }
        requests.post(
            f"{base_url}/api/preferences",
            headers={
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json",
            },
            json=preference_data,
            timeout=5,
        )

        # Récupérer la préférence
        response = requests.get(
            f"{base_url}/api/preferences/test_get_key",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Should succeed"
        assert "preference" in data, "Preference should be present"
        assert (
            data["preference"]["preference_key"] == "test_get_key"
        ), "Key should match"

    def test_update_preference(self, flask_server: str, test_token: str):
        """
        Test : Mise à jour d'une préférence.
        """
        base_url = flask_server

        # Créer d'abord une préférence
        preference_data = {
            "preference_key": "test_update_key",
            "preference_value": {"old": "value"},
        }
        requests.post(
            f"{base_url}/api/preferences",
            headers={
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json",
            },
            json=preference_data,
            timeout=5,
        )

        # Mettre à jour
        update_data = {"value": {"new": "value"}}
        response = requests.put(
            f"{base_url}/api/preferences/test_update_key",
            headers={
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json",
            },
            json=update_data,
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Should succeed"
        assert (
            data["preference"]["preference_value"]["new"] == "value"
        ), "Value should be updated"

    def test_delete_preference(self, flask_server: str, test_token: str):
        """
        Test : Suppression d'une préférence.
        """
        base_url = flask_server

        # Créer d'abord une préférence
        preference_data = {
            "preference_key": "test_delete_key",
            "preference_value": {"test": "value"},
        }
        requests.post(
            f"{base_url}/api/preferences",
            headers={
                "Authorization": f"Bearer {test_token}",
                "Content-Type": "application/json",
            },
            json=preference_data,
            timeout=5,
        )

        # Supprimer
        response = requests.delete(
            f"{base_url}/api/preferences/test_delete_key",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Should succeed"

        # Vérifier que la préférence n'existe plus
        get_response = requests.get(
            f"{base_url}/api/preferences/test_delete_key",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )
        assert get_response.status_code == 404, "Preference should not exist anymore"

    def test_export_preferences(self, flask_server: str, test_token: str):
        """
        Test : Export des préférences en JSON.
        """
        base_url = flask_server

        response = requests.post(
            f"{base_url}/api/preferences/export",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Should succeed"
        assert "preferences" in data, "Preferences should be present"
        assert isinstance(data["preferences"], dict), "Preferences should be a dict"
