"""
Service pour enrichissement métadonnées TV via APIs externes (OMDb, TVDB, TMDb).
"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests
from flask_caching import Cache

from src.metadata.tvdb_auth import TvdbApiClient, TvdbAuthenticator

logger = logging.getLogger(__name__)


class TvApiEnricher:
    """
    Enrichisseur métadonnées TV via APIs externes.

    Supporte :
    - OMDb (http://www.omdbapi.com/)
    - TVDB (https://api.thetvdb.com/)
    - TMDb (https://api.themoviedb.org/)

    Fusion intelligente avec priorité : TVDB > TMDb > OMDb
    """

    def __init__(
        self,
        cache: Optional[Cache] = None,
        timeout: float = 10.0,
        max_retries: int = 3,
        retry_delays: Optional[List[float]] = None,
    ):
        """
        Initialise l'enrichisseur.

        Args:
            cache: Instance Flask-Caching (optionnel)
            timeout: Timeout requêtes (secondes)
            max_retries: Nombre max de tentatives
            retry_delays: Délais entre tentatives (défaut: [1, 2, 4])
        """
        self.cache = cache
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delays = retry_delays or [1, 2, 4]

    def enrich_from_omdb(
        self,
        title: str,
        season: Optional[int] = None,
        episode: Optional[int] = None,
        api_key: str = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Enrichit depuis OMDb API.

        Args:
            title: Titre de la série
            season: Numéro saison (optionnel)
            episode: Numéro épisode (optionnel)
            api_key: Clé API OMDb

        Returns:
            Dictionnaire métadonnées enrichies ou None
        """
        if not api_key:
            return None

        # Clé cache
        cache_key = (
            f"omdb:{title}:{season}:{episode}"
            if season and episode
            else f"omdb:{title}"
        )

        # Vérifier cache
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Résultat OMDb depuis cache: {cache_key}")
                return cached

        for attempt in range(self.max_retries):
            try:
                params = {
                    "apikey": api_key,
                    "t": title,
                    "type": "series",
                }

                if season:
                    params["Season"] = season
                if episode:
                    params["Episode"] = episode

                response = requests.get(
                    "http://www.omdbapi.com/", params=params, timeout=self.timeout
                )

                response.raise_for_status()
                data = response.json()

                if data.get("Response") == "True":
                    # Normaliser métadonnées
                    enriched = self._normalize_omdb_data(data)
                    enriched["sources"] = ["omdb"]

                    # Mettre en cache
                    if self.cache:
                        self.cache.set(cache_key, enriched, timeout=86400)  # 24h

                    return enriched
                else:
                    error_msg = data.get("Error", "Unknown error")
                    logger.debug(f"OMDb erreur: {error_msg}")
                    return None

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    logger.warning(f"Timeout OMDb, retry dans {delay}s")
                    time.sleep(delay)
                else:
                    logger.error("Timeout OMDb après toutes les tentatives")
                    return None
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    logger.warning(f"Erreur OMDb, retry dans {delay}s: {e}")
                    time.sleep(delay)
                else:
                    logger.error(f"Erreur OMDb après toutes les tentatives: {e}")
                    return None
            except Exception as e:
                logger.error(f"Erreur inattendue OMDb: {e}", exc_info=True)
                return None

        return None

    def enrich_from_tvdb(
        self,
        title: str,
        season: Optional[int] = None,
        episode: Optional[int] = None,
        api_key: str = None,
        user_key: str = None,
        username: str = "default",
    ) -> Optional[Dict[str, Any]]:
        """
        Enrichit depuis TVDB API.

        Args:
            title: Titre de la série
            season: Numéro saison (optionnel)
            episode: Numéro épisode (optionnel)
            api_key: Clé API TVDB
            user_key: Clé utilisateur TVDB
            username: Nom utilisateur TVDB

        Returns:
            Dictionnaire métadonnées enrichies ou None
        """
        if not api_key or not user_key:
            return None

        # Clé cache
        cache_key = (
            f"tvdb:{title}:{season}:{episode}"
            if season and episode
            else f"tvdb:{title}"
        )

        # Vérifier cache
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Résultat TVDB depuis cache: {cache_key}")
                return cached

        try:
            # Créer authentificateur et client
            authenticator = TvdbAuthenticator(
                api_key=api_key,
                user_key=user_key,
                username=username,
            )
            client = TvdbApiClient(authenticator)

            # Rechercher série
            search_results = client.search_series(title)
            if not search_results or "data" not in search_results:
                return None

            # Prendre premier résultat
            series_data = search_results["data"][0] if search_results["data"] else None
            if not series_data:
                return None

            series_id = series_data.get("id")
            if not series_id:
                return None

            # Récupérer infos série
            series_info = client.get_series_info(series_id)
            if not series_info or "data" not in series_info:
                return None

            # Récupérer infos épisode si saison/épisode fournis
            episode_info = None
            if season and episode:
                episode_info = client.get_episode_info(series_id, season, episode)

            # Normaliser métadonnées
            enriched = self._normalize_tvdb_data(series_info["data"], episode_info)
            enriched["sources"] = ["tvdb"]

            # Mettre en cache
            if self.cache:
                self.cache.set(cache_key, enriched, timeout=86400)  # 24h

            return enriched

        except Exception as e:
            logger.error(f"Erreur enrichissement TVDB: {e}", exc_info=True)
            return None

    def enrich_from_tmdb(
        self,
        title: str,
        season: Optional[int] = None,
        episode: Optional[int] = None,
        api_key: str = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Enrichit depuis TMDb API.

        Args:
            title: Titre de la série
            season: Numéro saison (optionnel)
            episode: Numéro épisode (optionnel)
            api_key: Clé API TMDb

        Returns:
            Dictionnaire métadonnées enrichies ou None
        """
        if not api_key:
            return None

        # Clé cache
        cache_key = (
            f"tmdb:{title}:{season}:{episode}"
            if season and episode
            else f"tmdb:{title}"
        )

        # Vérifier cache
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Résultat TMDb depuis cache: {cache_key}")
                return cached

        for attempt in range(self.max_retries):
            try:
                # Recherche série
                search_params = {
                    "api_key": api_key,
                    "query": title,
                }
                search_response = requests.get(
                    "https://api.themoviedb.org/3/search/tv",
                    params=search_params,
                    timeout=self.timeout,
                )

                search_response.raise_for_status()
                search_data = search_response.json()

                if not search_data.get("results"):
                    return None

                # Prendre premier résultat
                series_data = search_data["results"][0]
                series_id = series_data.get("id")

                if not series_id:
                    return None

                # Récupérer infos série
                series_info_response = requests.get(
                    f"https://api.themoviedb.org/3/tv/{series_id}",
                    params={"api_key": api_key},
                    timeout=self.timeout,
                )
                series_info_response.raise_for_status()
                series_info = series_info_response.json()

                # Récupérer infos épisode si saison/épisode fournis
                episode_info = None
                if season and episode:
                    episode_response = requests.get(
                        f"https://api.themoviedb.org/3/tv/{series_id}/season/{season}/episode/{episode}",
                        params={"api_key": api_key},
                        timeout=self.timeout,
                    )
                    if episode_response.status_code == 200:
                        episode_info = episode_response.json()

                # Normaliser métadonnées
                enriched = self._normalize_tmdb_data(series_info, episode_info)
                enriched["sources"] = ["tmdb"]

                # Mettre en cache
                if self.cache:
                    self.cache.set(cache_key, enriched, timeout=86400)  # 24h

                return enriched

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    logger.warning(f"Timeout TMDb, retry dans {delay}s")
                    time.sleep(delay)
                else:
                    logger.error("Timeout TMDb après toutes les tentatives")
                    return None
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    logger.warning(f"Erreur TMDb, retry dans {delay}s: {e}")
                    time.sleep(delay)
                else:
                    logger.error(f"Erreur TMDb après toutes les tentatives: {e}")
                    return None
            except Exception as e:
                logger.error(f"Erreur inattendue TMDb: {e}", exc_info=True)
                return None

        return None

    def enrich(
        self,
        title: str,
        season: Optional[int] = None,
        episode: Optional[int] = None,
        config: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Enrichit métadonnées TV avec fusion intelligente de plusieurs sources.

        Priorité : TVDB > TMDb > OMDb

        Args:
            title: Titre de la série
            season: Numéro saison (optionnel)
            episode: Numéro épisode (optionnel)
            config: Dictionnaire avec clés API :
                {
                    'tvdb': {'api_key': '...', 'user_key': '...', 'username': '...'},
                    'tmdb': {'api_key': '...'},
                    'omdb': {'api_key': '...'}
                }

        Returns:
            Dictionnaire métadonnées enrichies (fusionné)
        """
        if not config:
            return {}

        enriched = {"sources": []}

        # Essayer TVDB en premier (meilleure qualité)
        if "tvdb" in config:
            tvdb_config = config["tvdb"]
            tvdb_data = self.enrich_from_tvdb(
                title=title,
                season=season,
                episode=episode,
                api_key=tvdb_config.get("api_key"),
                user_key=tvdb_config.get("user_key"),
                username=tvdb_config.get("username", "default"),
            )
            if tvdb_data:
                enriched.update(tvdb_data)
                return enriched  # TVDB suffit, retourner directement

        # Sinon essayer TMDb
        if "tmdb" in config:
            tmdb_config = config["tmdb"]
            tmdb_data = self.enrich_from_tmdb(
                title=title,
                season=season,
                episode=episode,
                api_key=tmdb_config.get("api_key"),
            )
            if tmdb_data:
                enriched.update(tmdb_data)
                return enriched  # TMDb suffit

        # En dernier essayer OMDb
        if "omdb" in config:
            omdb_config = config["omdb"]
            omdb_data = self.enrich_from_omdb(
                title=title,
                season=season,
                episode=episode,
                api_key=omdb_config.get("api_key"),
            )
            if omdb_data:
                enriched.update(omdb_data)

        return enriched

    def _normalize_omdb_data(self, data: Dict) -> Dict[str, Any]:
        """Normalise données OMDb vers format standard."""
        return {
            "title": data.get("Title"),
            "year": data.get("Year"),
            "plot": data.get("Plot"),
            "rating": data.get("imdbRating"),
            "imdb_id": data.get("imdbID"),
            "genre": data.get("Genre"),
            "director": data.get("Director"),
            "actors": data.get("Actors"),
        }

    def _normalize_tvdb_data(
        self, series_data: Dict, episode_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Normalise données TVDB vers format standard."""
        normalized = {
            "title": series_data.get("seriesName"),
            "year": (
                series_data.get("firstAired", "").split("-")[0]
                if series_data.get("firstAired")
                else None
            ),
            "plot": series_data.get("overview"),
            "rating": (
                str(series_data.get("rating", ""))
                if series_data.get("rating")
                else None
            ),
            "genre": (
                ", ".join(series_data.get("genre", []))
                if series_data.get("genre")
                else None
            ),
            "network": series_data.get("network"),
            "tvdb_id": (
                str(series_data.get("id", "")) if series_data.get("id") else None
            ),
        }

        if episode_data and "data" in episode_data:
            ep = episode_data["data"]
            normalized.update(
                {
                    "episode_title": ep.get("episodeName"),
                    "episode_plot": ep.get("overview"),
                    "episode_airdate": ep.get("firstAired"),
                }
            )

        return normalized

    def _normalize_tmdb_data(
        self, series_data: Dict, episode_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Normalise données TMDb vers format standard."""
        normalized = {
            "title": series_data.get("name"),
            "year": (
                series_data.get("first_air_date", "").split("-")[0]
                if series_data.get("first_air_date")
                else None
            ),
            "plot": series_data.get("overview"),
            "rating": (
                str(series_data.get("vote_average", ""))
                if series_data.get("vote_average")
                else None
            ),
            "genre": (
                ", ".join([g.get("name", "") for g in series_data.get("genres", [])])
                if series_data.get("genres")
                else None
            ),
            "network": (
                ", ".join([n.get("name", "") for n in series_data.get("networks", [])])
                if series_data.get("networks")
                else None
            ),
            "tmdb_id": (
                str(series_data.get("id", "")) if series_data.get("id") else None
            ),
        }

        if episode_data:
            normalized.update(
                {
                    "episode_title": episode_data.get("name"),
                    "episode_plot": episode_data.get("overview"),
                    "episode_airdate": episode_data.get("air_date"),
                }
            )

        return normalized
