"""
Tests E2E pour le système de jobs avec Playwright MCP.
"""

import uuid
from pathlib import Path

import pytest
import requests


class TestJobsE2E:
    """Tests E2E pour la gestion des jobs."""

    def test_list_jobs(self, flask_server: str, test_token: str):
        """
        Test : Liste des jobs retourne succès.
        """
        base_url = flask_server

        response = requests.get(
            f"{base_url}/api/jobs",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Should succeed"
        assert "jobs" in data, "Jobs list should be present"
        assert isinstance(data["jobs"], list), "Jobs should be a list"

    def test_list_jobs_with_filters(self, flask_server: str, test_token: str):
        """
        Test : Filtrage des jobs par statut fonctionne.
        """
        base_url = flask_server

        response = requests.get(
            f"{base_url}/api/jobs?status=completed&limit=10",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["success"] is True, "Should succeed"
        assert "total" in data, "Total count should be present"

    def test_get_job_not_found(self, flask_server: str, test_token: str):
        """
        Test : Récupération job inexistant retourne 404.
        """
        base_url = flask_server
        fake_job_id = str(uuid.uuid4())

        response = requests.get(
            f"{base_url}/api/jobs/{fake_job_id}",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()
        assert data["success"] is False, "Should fail"

    def test_get_job_logs(self, flask_server: str, test_token: str):
        """
        Test : Récupération logs d'un job (même si job n'existe pas).
        """
        base_url = flask_server
        fake_job_id = str(uuid.uuid4())

        response = requests.get(
            f"{base_url}/api/jobs/{fake_job_id}/logs",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        # Devrait retourner 404 si job n'existe pas
        assert response.status_code in [
            200,
            404,
        ], f"Expected 200 or 404, got {response.status_code}"

    def test_get_job_artifacts(self, flask_server: str, test_token: str):
        """
        Test : Récupération artefacts d'un job.
        """
        base_url = flask_server
        fake_job_id = str(uuid.uuid4())

        response = requests.get(
            f"{base_url}/api/jobs/{fake_job_id}/artifacts",
            headers={"Authorization": f"Bearer {test_token}"},
            timeout=5,
        )

        # Devrait retourner 404 si job n'existe pas
        assert response.status_code in [
            200,
            404,
        ], f"Expected 200 or 404, got {response.status_code}"
