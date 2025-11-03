"""
Authentification TVDB avec gestion JWT et refresh automatique.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)


class TvdbAuthenticator:
    """
    Gestion authentification TVDB avec cache token JWT.

    Le token TVDB expire après 30 jours, cette classe gère :
    - Authentification initiale
    - Cache token en mémoire
    - Refresh automatique si token expiré
    - Retry avec refresh si 401 détecté
    """

    def __init__(
        self,
        api_key: str,
        user_key: str,
        username: str,
        cache_ttl_days: int = 30,
    ):
        """
        Initialise l'authentificateur TVDB.

        Args:
            api_key: Clé API TVDB
            user_key: Clé utilisateur TVDB
            username: Nom d'utilisateur TVDB
            cache_ttl_days: Durée de vie du cache (défaut 30 jours)
        """
        self.api_key = api_key
        self.user_key = user_key
        self.username = username
        self.cache_ttl_days = cache_ttl_days

        # Cache token
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    def get_token(self, force_refresh: bool = False) -> str:
        """
        Récupère le token JWT (depuis cache ou nouvelle authentification).

        Args:
            force_refresh: Force refresh même si token valide

        Returns:
            Token JWT
        """
        # Vérifier si token en cache et valide
        if not force_refresh and self._token and self._token_expires_at:
            if datetime.utcnow() < self._token_expires_at:
                return self._token
            else:
                logger.debug("Token TVDB expiré, refresh nécessaire")

        # Refresh token
        return self.refresh_token()

    def refresh_token(self) -> str:
        """
        Force le refresh du token JWT.

        Returns:
            Nouveau token JWT
        """
        try:
            response = requests.post(
                "https://api.thetvdb.com/login",
                json={
                    "apikey": self.api_key,
                    "userkey": self.user_key,
                    "username": self.username,
                },
                timeout=10,
                headers={"Content-Type": "application/json"},
            )

            response.raise_for_status()
            data = response.json()

            if "token" not in data:
                raise ValueError("Token non reçu dans réponse TVDB")

            self._token = data["token"]

            # Calculer expiration (30 jours par défaut, ou utiliser expires_at si fourni)
            if "expires_at" in data:
                # Parser expires_at si fourni
                try:
                    self._token_expires_at = datetime.fromisoformat(
                        data["expires_at"].replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError) as e:
                    logger.warning(
                        f"Erreur parsing date expiration TVDB: {e}, utilisation TTL par défaut"
                    )
                    self._token_expires_at = datetime.utcnow() + timedelta(
                        days=self.cache_ttl_days
                    )
            else:
                # Cache pour 30 jours (sécurité)
                self._token_expires_at = datetime.utcnow() + timedelta(
                    days=self.cache_ttl_days
                )

            logger.info(f"Token TVDB rafraîchi, expire le {self._token_expires_at}")
            return self._token

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur authentification TVDB: {e}")
            raise ValueError(f"Erreur authentification TVDB: {e}") from e
        except Exception as e:
            logger.error(f"Erreur inattendue authentification TVDB: {e}", exc_info=True)
            raise

    def clear_cache(self) -> None:
        """Efface le cache du token."""
        self._token = None
        self._token_expires_at = None


class TvdbApiClient:
    """
    Client API TVDB avec authentification automatique.

    Gère les appels API TVDB avec refresh automatique du token si nécessaire.
    """

    def __init__(self, authenticator: TvdbAuthenticator):
        """
        Initialise le client avec un authentificateur.

        Args:
            authenticator: Instance TvdbAuthenticator
        """
        self.authenticator = authenticator
        self.base_url = "https://api.thetvdb.com"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        max_retries: int = 3,
    ) -> Optional[Dict]:
        """
        Fait une requête API TVDB avec refresh automatique si 401.

        Args:
            method: Méthode HTTP (GET, POST, etc.)
            endpoint: Endpoint API (sans base_url)
            params: Paramètres de requête
            max_retries: Nombre max de tentatives (avec refresh)

        Returns:
            Réponse JSON ou None si erreur
        """
        token = self.authenticator.get_token()

        for attempt in range(max_retries):
            try:
                url = f"{self.base_url}{endpoint}"
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                }

                if method.upper() == "GET":
                    response = requests.get(
                        url, headers=headers, params=params, timeout=10
                    )
                elif method.upper() == "POST":
                    response = requests.post(
                        url, headers=headers, json=params, timeout=10
                    )
                else:
                    raise ValueError(f"Méthode HTTP non supportée: {method}")

                # Si 401, refresh token et retry
                if response.status_code == 401 and attempt < max_retries - 1:
                    logger.warning("Token TVDB expiré, refresh...")
                    token = self.authenticator.refresh_token()
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401 and attempt < max_retries - 1:
                    token = self.authenticator.refresh_token()
                    continue
                logger.error(f"Erreur HTTP TVDB: {e}")
                return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur requête TVDB: {e}")
                return None

        return None

    def search_series(self, title: str) -> Optional[Dict]:
        """
        Recherche une série par titre.

        Args:
            title: Titre de la série

        Returns:
            Résultats de recherche ou None
        """
        return self._make_request("GET", "/search/series", params={"name": title})

    def get_series_info(self, series_id: int) -> Optional[Dict]:
        """
        Récupère les informations d'une série.

        Args:
            series_id: ID série TVDB

        Returns:
            Informations série ou None
        """
        return self._make_request("GET", f"/series/{series_id}")

    def get_episode_info(
        self, series_id: int, season: int, episode: int
    ) -> Optional[Dict]:
        """
        Récupère les informations d'un épisode.

        Args:
            series_id: ID série TVDB
            season: Numéro saison
            episode: Numéro épisode

        Returns:
            Informations épisode ou None
        """
        return self._make_request(
            "GET",
            f"/series/{series_id}/episodes/query",
            params={"airedSeason": season, "airedEpisode": episode},
        )
