"""
Helper pour récupérer les configurations API depuis la base de données.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_tv_api_config(user_id: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
    """
    Récupère les configurations APIs TV (OMDb, TVDB, TMDb) depuis ApiConfig.

    Priorité : config utilisateur > config globale

    Args:
        user_id: ID utilisateur (None = config globale uniquement)

    Returns:
        Dictionnaire avec clés 'omdb', 'tvdb', 'tmdb' contenant les configs
        Exemple:
        {
            'omdb': {'api_key': '...'},
            'tvdb': {'api_key': '...', 'user_key': '...', 'username': '...'},
            'tmdb': {'api_key': '...'}
        }
    """
    from web.models.api_config import ApiConfig

    configs = {
        "omdb": None,
        "tvdb": None,
        "tmdb": None,
    }

    # Noms d'API à récupérer
    api_names = ["omdb", "tvdb", "tmdb"]

    for api_name in api_names:
        api_config = None

        # Chercher config utilisateur d'abord
        if user_id:
            api_config = ApiConfig.query.filter_by(
                user_id=user_id,
                api_name=api_name,
            ).first()

        # Fallback config globale (user_id=None)
        if not api_config:
            api_config = ApiConfig.query.filter_by(
                user_id=None,
                api_name=api_name,
            ).first()

        if api_config:
            try:
                api_data = api_config.get_api_key()
                if api_data:
                    if api_name == "tvdb":
                        # TVDB nécessite api_key, user_key, username
                        configs["tvdb"] = {
                            "api_key": api_data.get("api_key"),
                            "user_key": api_data.get("user_key"),
                            "username": api_data.get("username", "default"),
                        }
                    else:
                        # OMDb et TMDb nécessitent seulement api_key
                        configs[api_name] = {
                            "api_key": api_data.get("api_key"),
                        }
            except Exception as e:
                logger.warning(f"Erreur déchiffrement config {api_name}: {e}")

    # Nettoyer None
    return {k: v for k, v in configs.items() if v is not None}


def parse_tv_release_name(release_name: str) -> Dict[str, Any]:
    """
    Parse un nom de release TV pour extraire titre, saison, épisode.

    Format attendu: "Titre.S01E01.720p.HDTV-GROUP"
    Ou variantes: "Titre.S1E1", "Titre - S01E01", etc.

    Args:
        release_name: Nom de la release

    Returns:
        Dictionnaire avec 'title', 'season', 'episode' (optionnels)
    """
    import re

    parsed = {
        "title": None,
        "season": None,
        "episode": None,
    }

    # Pattern: S01E01, S1E1, S01.E01, etc.
    season_episode_pattern = r"[Ss](\d+)[Ee](\d+)"
    match = re.search(season_episode_pattern, release_name)

    if match:
        parsed["season"] = int(match.group(1))
        parsed["episode"] = int(match.group(2))

        # Extraire titre (tout avant SXXEXX)
        title_match = re.match(r"^(.+?)\.?[Ss]\d+", release_name)
        if title_match:
            parsed["title"] = title_match.group(1).strip().replace(".", " ")
        else:
            # Fallback: prendre tout avant SXXEXX
            title_part = release_name[: match.start()].strip()
            # Nettoyer (retirer extensions, groupes, etc.)
            title_part = re.sub(r"\.[A-Z0-9]+$", "", title_part)  # .720p, .HDTV, etc.
            parsed["title"] = title_part.replace(".", " ").strip()

    return parsed
