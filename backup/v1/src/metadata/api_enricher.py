"""
Module d'enrichissement de métadonnées via APIs externes (OpenLibrary, Google Books).
"""

import logging
import time
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class MetadataEnricher:
    """
    Classe pour enrichir métadonnées eBooks via APIs externes.

    Supporte OpenLibrary et Google Books avec fusion intelligente des données.
    """

    def __init__(
        self,
        enable_googlebooks: bool = True,
        enable_openlibrary: bool = True,
        timeout: float = 10.0,
        rate_limit_delay: float = 0.5,
    ):
        """
        Initialise l'enrichisseur avec configuration APIs.

        Args:
            enable_googlebooks: Activer Google Books API
            enable_openlibrary: Activer OpenLibrary API
            timeout: Timeout requêtes HTTP (secondes)
            rate_limit_delay: Délai entre appels API (secondes)
        """
        self.enable_googlebooks = enable_googlebooks
        self.enable_openlibrary = enable_openlibrary
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.last_api_call = 0.0

    def enrich(self, metadata: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        """
        Enrichit métadonnées via APIs externes.

        Stratégie:
        1. Si ISBN présent : recherche prioritaire par ISBN
        2. Sinon : recherche par titre + auteur
        3. Fusion intelligente : priorité API → métadonnées locales

        Args:
            metadata: Dictionnaire métadonnées à enrichir

        Returns:
            Dictionnaire métadonnées enrichi avec api_sources mis à jour
        """
        enriched = metadata.copy()

        # S'assurer que api_sources existe
        if "api_sources" not in enriched:
            enriched["api_sources"] = []

        # Si ISBN présent : recherche prioritaire par ISBN
        isbn = enriched.get("isbn")
        if isbn:
            isbn_cleaned = isbn.replace("-", "").replace(" ", "")

            # OpenLibrary ISBN
            if self.enable_openlibrary:
                ol_data = self._search_openlibrary_isbn(isbn_cleaned)
                if ol_data:
                    enriched = self._merge_metadata(enriched, ol_data, "openlibrary")

            # Google Books ISBN (si OpenLibrary échoue ou pour complément)
            if self.enable_googlebooks and "googlebooks" not in enriched.get(
                "api_sources", []
            ):
                gb_data = self._search_googlebooks_isbn(isbn_cleaned)
                if gb_data:
                    enriched = self._merge_metadata(enriched, gb_data, "googlebooks")

            # Si ISBN trouvé des données, retourner directement
            if enriched.get("api_sources"):
                return enriched

        # Sinon : recherche par titre + auteur
        title = enriched.get("title")
        author = enriched.get("author")

        if title or author:
            # OpenLibrary titre + auteur
            if self.enable_openlibrary:
                ol_data = self._search_openlibrary_title_author(title, author)
                if ol_data:
                    enriched = self._merge_metadata(enriched, ol_data, "openlibrary")

            # Google Books titre + auteur
            if self.enable_googlebooks:
                gb_data = self._search_googlebooks_title_author(title, author)
                if gb_data:
                    enriched = self._merge_metadata(enriched, gb_data, "googlebooks")

        return enriched

    def _rate_limit(self):
        """Applique délai rate limiting entre appels API."""
        current_time = time.time()
        time_since_last = current_time - self.last_api_call

        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)

        self.last_api_call = time.time()

    def _search_openlibrary_isbn(self, isbn: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Recherche livre OpenLibrary par ISBN.

        Args:
            isbn: ISBN (format nettoyé, sans tirets)

        Returns:
            Dictionnaire métadonnées ou None si échec
        """
        self._rate_limit()

        url = f"https://openlibrary.org/isbn/{isbn}.json"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Parser données OpenLibrary
            metadata = {}

            if data.get("title"):
                metadata["title"] = data["title"]

            if data.get("authors"):
                # Prendre premier auteur, récupérer nom depuis référence
                author_key = (
                    data["authors"][0].get("key")
                    if isinstance(data["authors"][0], dict)
                    else None
                )
                if author_key:
                    # Récupérer nom auteur depuis API
                    try:
                        author_url = f"https://openlibrary.org{author_key}.json"
                        author_resp = requests.get(author_url, timeout=self.timeout)
                        if author_resp.ok:
                            author_data = author_resp.json()
                            if author_data.get("name"):
                                metadata["author"] = author_data["name"]
                    except Exception as e:
                        logger.debug(f"Erreur récupération auteur OpenLibrary: {e}")

            if data.get("publishers"):
                metadata["publisher"] = data["publishers"][0]

            if data.get("publish_date"):
                # Extraire année
                import re

                year_match = re.search(r"\b(19|20)\d{2}\b", str(data["publish_date"]))
                if year_match:
                    metadata["year"] = year_match.group()

            if data.get("languages"):
                # Convertir code langue en nom si nécessaire
                lang_code = (
                    data["languages"][0].get("key", "").replace("/languages/", "")
                )
                if lang_code:
                    metadata["language"] = lang_code

            if metadata:
                logger.info(f"Métadonnées OpenLibrary récupérées pour ISBN {isbn}")
                return metadata

        except requests.exceptions.RequestException as e:
            logger.debug(f"Erreur API OpenLibrary ISBN: {e}")
        except Exception as e:
            logger.debug(f"Erreur parsing OpenLibrary ISBN: {e}")

        return None

    def _search_openlibrary_title_author(
        self,
        title: Optional[str],
        author: Optional[str],
    ) -> Optional[Dict[str, Optional[str]]]:
        """
        Recherche livre OpenLibrary par titre + auteur.

        Args:
            title: Titre livre
            author: Auteur livre

        Returns:
            Dictionnaire métadonnées ou None si échec
        """
        self._rate_limit()

        # Construire query
        query_parts = []
        if title:
            query_parts.append(f"title={title}")
        if author:
            query_parts.append(f"author={author}")

        if not query_parts:
            return None

        url = "https://openlibrary.org/search.json"
        params = {}
        if title:
            params["title"] = title
        if author:
            params["author"] = author

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Prendre premier résultat
            if data.get("docs") and len(data["docs"]) > 0:
                first_result = data["docs"][0]

                metadata = {}

                if first_result.get("title"):
                    metadata["title"] = first_result["title"]

                if first_result.get("author_name"):
                    metadata["author"] = (
                        first_result["author_name"][0]
                        if isinstance(first_result["author_name"], list)
                        else first_result["author_name"]
                    )

                if first_result.get("publisher"):
                    metadata["publisher"] = (
                        first_result["publisher"][0]
                        if isinstance(first_result["publisher"], list)
                        else first_result["publisher"]
                    )

                if first_result.get("publish_year"):
                    metadata["year"] = (
                        str(first_result["publish_year"][0])
                        if isinstance(first_result["publish_year"], list)
                        else str(first_result["publish_year"])
                    )

                if first_result.get("isbn"):
                    # Prendre premier ISBN trouvé
                    isbn_raw = (
                        first_result["isbn"][0]
                        if isinstance(first_result["isbn"], list)
                        else first_result["isbn"]
                    )
                    isbn_cleaned = isbn_raw.replace("-", "").replace(" ", "")
                    if len(isbn_cleaned) in (10, 13):
                        metadata["isbn"] = isbn_cleaned

                if first_result.get("language"):
                    lang_code = (
                        first_result["language"][0]
                        if isinstance(first_result["language"], list)
                        else first_result["language"]
                    )
                    metadata["language"] = lang_code

                if metadata:
                    logger.info(
                        f"Métadonnées OpenLibrary récupérées pour titre+ auteur"
                    )
                    return metadata

        except requests.exceptions.RequestException as e:
            logger.debug(f"Erreur API OpenLibrary titre+ auteur: {e}")
        except Exception as e:
            logger.debug(f"Erreur parsing OpenLibrary titre+ auteur: {e}")

        return None

    def _search_googlebooks_isbn(self, isbn: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Recherche livre Google Books par ISBN.

        Args:
            isbn: ISBN (format nettoyé)

        Returns:
            Dictionnaire métadonnées ou None si échec
        """
        self._rate_limit()

        url = "https://www.googleapis.com/books/v1/volumes"
        params = {"q": f"isbn:{isbn}"}

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if data.get("totalItems", 0) == 0:
                return None

            # Prendre premier résultat
            volume = data["items"][0]
            volume_info = volume.get("volumeInfo", {})

            metadata = {}

            if volume_info.get("title"):
                metadata["title"] = volume_info["title"]

            if volume_info.get("authors"):
                metadata["author"] = volume_info["authors"][0]

            if volume_info.get("publisher"):
                metadata["publisher"] = volume_info["publisher"]

            if volume_info.get("publishedDate"):
                # Extraire année
                import re

                year_match = re.search(
                    r"\b(19|20)\d{2}\b", volume_info["publishedDate"]
                )
                if year_match:
                    metadata["year"] = year_match.group()

            if volume_info.get("language"):
                metadata["language"] = volume_info["language"]

            if volume_info.get("industryIdentifiers"):
                # Chercher ISBN
                for identifier in volume_info["industryIdentifiers"]:
                    if identifier.get("type") in ("ISBN_10", "ISBN_13"):
                        metadata["isbn"] = (
                            identifier.get("identifier", "")
                            .replace("-", "")
                            .replace(" ", "")
                        )
                        break

            if metadata:
                logger.info(f"Métadonnées Google Books récupérées pour ISBN {isbn}")
                return metadata

        except requests.exceptions.RequestException as e:
            logger.debug(f"Erreur API Google Books ISBN: {e}")
        except Exception as e:
            logger.debug(f"Erreur parsing Google Books ISBN: {e}")

        return None

    def _search_googlebooks_title_author(
        self,
        title: Optional[str],
        author: Optional[str],
    ) -> Optional[Dict[str, Optional[str]]]:
        """
        Recherche livre Google Books par titre + auteur.

        Args:
            title: Titre livre
            author: Auteur livre

        Returns:
            Dictionnaire métadonnées ou None si échec
        """
        self._rate_limit()

        # Construire query
        query_parts = []
        if title:
            query_parts.append(f"intitle:{title}")
        if author:
            query_parts.append(f"inauthor:{author}")

        if not query_parts:
            return None

        url = "https://www.googleapis.com/books/v1/volumes"
        params = {"q": "+".join(query_parts)}

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            if data.get("totalItems", 0) == 0:
                return None

            # Prendre premier résultat
            volume = data["items"][0]
            volume_info = volume.get("volumeInfo", {})

            metadata = {}

            if volume_info.get("title"):
                metadata["title"] = volume_info["title"]

            if volume_info.get("authors"):
                metadata["author"] = volume_info["authors"][0]

            if volume_info.get("publisher"):
                metadata["publisher"] = volume_info["publisher"]

            if volume_info.get("publishedDate"):
                # Extraire année
                import re

                year_match = re.search(
                    r"\b(19|20)\d{2}\b", volume_info["publishedDate"]
                )
                if year_match:
                    metadata["year"] = year_match.group()

            if volume_info.get("language"):
                metadata["language"] = volume_info["language"]

            if volume_info.get("industryIdentifiers"):
                # Chercher ISBN
                for identifier in volume_info["industryIdentifiers"]:
                    if identifier.get("type") in ("ISBN_10", "ISBN_13"):
                        metadata["isbn"] = (
                            identifier.get("identifier", "")
                            .replace("-", "")
                            .replace(" ", "")
                        )
                        break

            if metadata:
                logger.info(f"Métadonnées Google Books récupérées pour titre+ auteur")
                return metadata

        except requests.exceptions.RequestException as e:
            logger.debug(f"Erreur API Google Books titre+ auteur: {e}")
        except Exception as e:
            logger.debug(f"Erreur parsing Google Books titre+ auteur: {e}")

        return None

    def _merge_metadata(
        self,
        base: Dict[str, Optional[str]],
        api_data: Dict[str, Optional[str]],
        source: str,
    ) -> Dict[str, Optional[str]]:
        """
        Fusionne métadonnées API avec métadonnées locales.

        Stratégie : Priorité API → métadonnées locales (API remplace seulement si valeur présente).

        Args:
            base: Métadonnées de base (locales)
            api_data: Métadonnées depuis API
            source: Nom source API ('openlibrary', 'googlebooks')

        Returns:
            Dictionnaire métadonnées fusionné
        """
        merged = base.copy()

        # Ajouter source API
        if "api_sources" not in merged:
            merged["api_sources"] = []
        if source not in merged["api_sources"]:
            merged["api_sources"].append(source)

        # Fusion : API remplace seulement si valeur présente et locale absente ou None
        for key, value in api_data.items():
            if value and (not merged.get(key) or merged[key] is None):
                merged[key] = value

        return merged
