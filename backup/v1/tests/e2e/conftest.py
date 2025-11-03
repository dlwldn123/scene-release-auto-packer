"""
Configuration et fixtures pour les tests E2E.
"""

import subprocess
import threading
import time
from pathlib import Path
from typing import Generator

import pytest
import requests

# URL du serveur Flask
FLASK_URL = "http://localhost:5000"
FLASK_START_TIMEOUT = 30  # secondes


def wait_for_server(url: str, timeout: int = FLASK_START_TIMEOUT) -> bool:
    """
    Attend que le serveur Flask soit disponible.

    Args:
        url: URL du serveur
        timeout: Timeout en secondes

    Returns:
        True si serveur disponible, False sinon
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200 or response.status_code == 302:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


@pytest.fixture(scope="session")
def flask_server() -> Generator[None, None, None]:
    """
    Fixture pour démarrer le serveur Flask avant les tests.

    Note: Le serveur doit être démarré manuellement ou via script.
    Cette fixture vérifie seulement que le serveur est disponible.
    """
    # Vérifier si le serveur est déjà en cours d'exécution
    if not wait_for_server(FLASK_URL):
        pytest.skip(
            f"Serveur Flask non disponible sur {FLASK_URL}. "
            f"Veuillez démarrer le serveur avec: python web/app.py"
        )

    yield

    # Nettoyage après tests (si nécessaire)
    pass


@pytest.fixture
def base_url(flask_server) -> str:
    """Retourne l'URL de base du serveur Flask."""
    return FLASK_URL


@pytest.fixture
def admin_credentials() -> dict:
    """Retourne les credentials admin par défaut."""
    return {"username": "admin", "password": "admin"}


@pytest.fixture
def api_base_url(base_url: str) -> str:
    """Retourne l'URL de base pour les API."""
    return f"{base_url}/api"
