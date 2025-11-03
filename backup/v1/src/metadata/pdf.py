"""
Module d'extraction de métadonnées depuis fichiers PDF.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def extract_pdf_metadata(filepath: str | Path) -> Dict[str, Optional[str]]:
    """
    Extrait les métadonnées d'un fichier PDF.

    Méthode : Utilise PyPDF2.PdfReader pour accéder au dictionnaire metadata.

    Args:
        filepath: Chemin vers fichier PDF

    Returns:
        Dictionnaire métadonnées avec champs:
        - title, author, publisher, language, year, isbn, format, api_sources
        (valeurs None si absentes)
    """
    path = Path(filepath)

    if not path.exists():
        logger.error(f"Fichier PDF introuvable: {path}")
        return _empty_metadata()

    metadata = _empty_metadata()
    metadata["format"] = "PDF"

    # Utiliser PyPDF2 si disponible
    try:
        from PyPDF2 import PdfReader

        with open(path, "rb") as f:
            try:
                reader = PdfReader(f)

                # Extraire métadonnées depuis dictionnaire metadata
                if reader.metadata:
                    pdf_meta = reader.metadata

                    # Titre
                    if pdf_meta.get("/Title"):
                        metadata["title"] = pdf_meta["/Title"].strip()

                    # Auteur
                    if pdf_meta.get("/Author"):
                        metadata["author"] = pdf_meta["/Author"].strip()

                    # Éditeur (créateur)
                    if pdf_meta.get("/Creator"):
                        metadata["publisher"] = pdf_meta["/Creator"].strip()

                    # Subject peut contenir informations supplémentaires
                    # (mais pas utilisé directement comme métadonnée principale)

                    # Dates : CreationDate ou ModDate
                    date_candidates = []
                    if pdf_meta.get("/CreationDate"):
                        date_candidates.append(pdf_meta["/CreationDate"])
                    if pdf_meta.get("/ModDate"):
                        date_candidates.append(pdf_meta["/ModDate"])

                    # Extraire année depuis dates
                    for date_str in date_candidates:
                        if date_str:
                            # Format PDF date : D:YYYYMMDDHHmmSS
                            year_match = re.search(
                                r"\b(?:D:)?(19|20)(\d{2})\b", str(date_str)
                            )
                            if year_match:
                                metadata["year"] = year_match.group(
                                    1
                                ) + year_match.group(2)
                                break

                    # Langue : souvent absent des PDFs, défaut 'en'
                    metadata["language"] = "en"

                    # ISBN peut être dans Subject ou dans texte du document
                    # Recherche basique dans Subject
                    if pdf_meta.get("/Subject"):
                        subject = str(pdf_meta["/Subject"])
                        isbn_match = re.search(
                            r"ISBN[\s\-:]*([0-9X]{10,13})", subject, re.IGNORECASE
                        )
                        if isbn_match:
                            isbn = re.sub(r"[-\s]", "", isbn_match.group(1))
                            if re.match(r"^(?:\d{10}|\d{13})$", isbn):
                                metadata["isbn"] = isbn

                logger.info(f"Métadonnées PDF extraites: {path}")

            except Exception as e:
                logger.warning(f"Erreur lecture PDF avec PyPDF2: {e}")
                # Fallback : utiliser nom fichier comme titre
                metadata["title"] = path.stem

    except ImportError:
        logger.warning("PyPDF2 non disponible, utilisation métadonnées minimales")
        # Fallback : utiliser nom fichier comme titre
        metadata["title"] = path.stem
    except Exception as e:
        logger.error(f"Erreur extraction métadonnées PDF: {path}: {e}", exc_info=True)
        # Fallback : utiliser nom fichier comme titre
        if not metadata.get("title"):
            metadata["title"] = path.stem

    # Valeurs par défaut
    if not metadata.get("language"):
        metadata["language"] = "en"

    return metadata


def _empty_metadata() -> Dict[str, Optional[str]]:
    """
    Retourne un dictionnaire métadonnées vide avec structure complète.

    Returns:
        Dictionnaire avec tous champs initialisés à None sauf api_sources=[]
    """
    return {
        "title": None,
        "author": None,
        "publisher": None,
        "language": "en",
        "year": None,
        "isbn": None,
        "format": None,
        "api_sources": [],
    }
