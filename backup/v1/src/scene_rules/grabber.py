"""
Module de gestion des règles Scene depuis scenerules.org.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Dossier cache par défaut
CACHE_DIR = Path("rules_cache")


def grab_rules_list() -> List[Dict[str, str]]:
    """
    Récupère liste règles disponibles depuis scenerules.org.

    Scraping HTML de la page principale pour extraire liens règles groupées par année.

    Returns:
        Liste dictionnaires avec clés: name, url, year
        Exemple: [{'name': '2022_EBOOK', 'url': '...', 'year': '2022'}, ...]
    """
    url = "https://scenerules.org/"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        rules = []

        # Parser HTML : chercher liens vers règles
        # Structure typique: liens avec href contenant année ou nom règle
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(strip=True)

            # Filtrer liens règles (exemple: /html/2022_EBOOK.html)
            if "/html/" in href and href.endswith(".html"):
                # Extraire nom et année depuis URL
                # Exemple: /html/2022_EBOOK.html -> name=2022_EBOOK, year=2022
                match = re.search(r"/(\d{4})_([A-Z_]+)\.html$", href)
                if match:
                    year = match.group(1)
                    name_part = match.group(2)
                    name = f"{year}_{name_part}"

                    # Construire URL complète
                    if href.startswith("/"):
                        full_url = f"https://scenerules.org{href}"
                    else:
                        full_url = f"https://scenerules.org/{href}"

                    rules.append(
                        {
                            "name": name,
                            "url": full_url,
                            "year": year,
                        }
                    )

        # Dédupliquer par nom
        seen = set()
        unique_rules = []
        for rule in rules:
            if rule["name"] not in seen:
                seen.add(rule["name"])
                unique_rules.append(rule)

        logger.info(f"{len(unique_rules)} règle(s) trouvée(s) sur scenerules.org")
        return unique_rules

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur récupération liste règles: {e}")
        return []
    except Exception as e:
        logger.error(f"Erreur parsing HTML scenerules.org: {e}", exc_info=True)
        return []


def grab_and_cache_rule(
    name: str, url: str, year: str, cache_dir: Optional[Path] = None
) -> Optional[Path]:
    """
    Télécharge une règle depuis URL et la met en cache local.

    Args:
        name: Nom règle (ex: '2022_EBOOK')
        url: URL règle HTML
        year: Année règle (ex: '2022')
        cache_dir: Dossier cache (None = CACHE_DIR par défaut)

    Returns:
        Chemin fichier cache créé ou None si échec
    """
    if cache_dir is None:
        cache_dir = CACHE_DIR

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Nom fichier cache: <year>_<name>.txt
    cache_filename = f"{year}_{name}.txt"
    cache_path = cache_dir / cache_filename

    # Si déjà en cache, retourner chemin
    if cache_path.exists():
        logger.debug(f"Règle déjà en cache: {cache_path}")
        return cache_path

    try:
        # Télécharger HTML
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Parser HTML et extraire contenu texte
        soup = BeautifulSoup(response.text, "html.parser")

        # Extraire contenu principal (body ou div principal)
        # Chercher div avec class 'content' ou utiliser body
        content_div = soup.find("div", class_="content") or soup.find(
            "div", class_="main"
        )

        if content_div:
            content_text = content_div.get_text(separator="\n", strip=True)
        else:
            # Fallback : utiliser body
            body = soup.find("body")
            if body:
                content_text = body.get_text(separator="\n", strip=True)
            else:
                content_text = soup.get_text(separator="\n", strip=True)

        # Sauvegarder dans cache
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(f"# Rule: {name}\n")
            f.write(f"# Year: {year}\n")
            f.write(f"# URL: {url}\n")
            f.write("\n" + "=" * 80 + "\n\n")
            f.write(content_text)

        logger.info(f"Règle mise en cache: {cache_path}")
        return cache_path

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur téléchargement règle {name}: {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur mise en cache règle {name}: {e}", exc_info=True)
        return None


def grab_all_rules(
    force_update: bool = False, cache_dir: Optional[Path] = None
) -> Dict[str, List[Dict[str, str]]]:
    """
    Télécharge toutes règles disponibles et les met en cache.

    Args:
        force_update: Forcer mise à jour même si déjà en cache
        cache_dir: Dossier cache (None = CACHE_DIR par défaut)

    Returns:
        Dictionnaire groupé par année:
        {
            '2022': [{'name': '...', 'url': '...', 'year': '2022'}, ...],
            ...
        }
    """
    rules_list = grab_rules_list()

    if cache_dir is None:
        cache_dir = CACHE_DIR

    cache_dir = Path(cache_dir)

    rules_by_year = {}

    for rule in rules_list:
        name = rule["name"]
        url = rule["url"]
        year = rule["year"]

        # Télécharger et mettre en cache (si force_update ou pas encore en cache)
        cache_path = cache_dir / f"{year}_{name}.txt"
        if force_update or not cache_path.exists():
            grab_and_cache_rule(name, url, year, cache_dir)

        # Grouper par année
        if year not in rules_by_year:
            rules_by_year[year] = []
        rules_by_year[year].append(rule)

    logger.info(
        f"{len(rules_list)} règle(s) traitée(s), groupées par {len(rules_by_year)} année(s)"
    )
    return rules_by_year


def get_cached_rule(
    name: str, year: str, cache_dir: Optional[Path] = None
) -> Optional[str]:
    """
    Récupère contenu règle depuis cache local.

    Args:
        name: Nom règle (ex: '2022_EBOOK')
        year: Année règle
        cache_dir: Dossier cache (None = CACHE_DIR par défaut)

    Returns:
        Contenu texte règle ou None si non trouvé
    """
    if cache_dir is None:
        cache_dir = CACHE_DIR

    cache_dir = Path(cache_dir)
    cache_filename = f"{year}_{name}.txt"
    cache_path = cache_dir / cache_filename

    if not cache_path.exists():
        logger.warning(f"Règle non trouvée dans cache: {cache_path}")
        return None

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Erreur lecture cache règle: {cache_path}: {e}")
        return None


def list_cached_rules(cache_dir: Optional[Path] = None) -> List[Dict[str, str]]:
    """
    Liste toutes règles en cache local avec métadonnées.

    Args:
        cache_dir: Dossier cache (None = CACHE_DIR par défaut)

    Returns:
        Liste dictionnaires avec clés: name, year, path, size, modified
    """
    if cache_dir is None:
        cache_dir = CACHE_DIR

    cache_dir = Path(cache_dir)

    if not cache_dir.exists():
        return []

    cached_rules = []

    for cache_file in cache_dir.glob("*_*.txt"):
        # Parser nom fichier: <year>_<name>.txt
        match = re.match(r"^(\d{4})_(.+?)\.txt$", cache_file.name)
        if match:
            year = match.group(1)
            name = match.group(2)

            stat = cache_file.stat()

            cached_rules.append(
                {
                    "name": name,
                    "year": year,
                    "path": str(cache_file),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                }
            )

    # Trier par année puis nom
    cached_rules.sort(key=lambda x: (x["year"], x["name"]))

    return cached_rules
