"""
Module d'extraction de métadonnées depuis fichiers MOBI/AZW/AZW3.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def extract_mobi_metadata(filepath: str | Path) -> Dict[str, Optional[str]]:
    """
    Extrait les métadonnées d'un fichier MOBI/AZW/AZW3.

    Méthode : Utilise ebookatty si disponible, sinon lecture binaire header MOBI.

    Args:
        filepath: Chemin vers fichier MOBI/AZW/AZW3

    Returns:
        Dictionnaire métadonnées avec champs:
        - title, author, publisher, language, year, isbn, format, api_sources
        (valeurs None si absentes)
    """
    path = Path(filepath)

    if not path.exists():
        logger.error(f"Fichier MOBI introuvable: {path}")
        return _empty_metadata()

    metadata = _empty_metadata()

    # Détecter format depuis extension
    ext = path.suffix.lower()
    if ext == ".azw3":
        metadata["format"] = "AZW3"
    elif ext == ".azw":
        metadata["format"] = "AZW"
    else:
        metadata["format"] = "MOBI"

    # Tentative avec ebookatty si disponible
    try:
        import ebookatty

        # ebookatty peut extraire métadonnées basiques
        # Note: ebookatty n'a pas d'API standard documentée, utilisation basique
        # Si disponible, utiliser selon son API réelle

        logger.debug(
            "ebookatty disponible mais utilisation parsing manuel pour compatibilité"
        )
    except ImportError:
        logger.debug("ebookatty non disponible, utilisation parsing manuel")

    # Parsing manuel binaire header MOBI
    try:
        with open(path, "rb") as f:
            # Lire PalmDB header (16 bytes)
            palm_header = f.read(16)
            if len(palm_header) < 16:
                logger.warning(f"Fichier MOBI trop court: {path}")
                return metadata

            # Vérifier signature PalmDB (commence par 'BOOKMOBI' ou offset spécifique)
            # PalmDB : name[0:4] devrait être 'BOOK' ou similaire
            # Pour MOBI, chercher signature à offset 60

            f.seek(60)
            mobi_sig = f.read(8)

            if mobi_sig[:4] != b"BOOK" and mobi_sig[:4] != b"TEXt":
                logger.warning(f"Signature MOBI non trouvée: {path}")
                return metadata

            # Lire MOBI header (après PalmDB header, offset variable)
            # Structure simplifiée : chercher EXTH header pour métadonnées

            # Chercher EXTH header (commence par 'EXTH')
            # EXTH header contient les métadonnées étendues
            f.seek(0)
            content = f.read(min(1024 * 1024, path.stat().st_size))  # Lire max 1MB

            exth_pos = content.find(b"EXTH")
            if exth_pos == -1:
                logger.debug(f"EXTH header non trouvé, métadonnées limitées: {path}")
                # Essayer extraction basique depuis PalmDB name field
                return metadata

            # Parser EXTH header
            # EXTH structure: 'EXTH' + length (4 bytes) + record count + records
            exth_length_pos = exth_pos + 4
            if exth_length_pos + 4 > len(content):
                return metadata

            # Longueur EXTH (big-endian)
            exth_length = int.from_bytes(
                content[exth_length_pos : exth_length_pos + 4], byteorder="big"
            )

            # Nombre de records
            record_count_pos = exth_length_pos + 4
            if record_count_pos + 4 > len(content):
                return metadata

            record_count = int.from_bytes(
                content[record_count_pos : record_count_pos + 4], byteorder="big"
            )

            # Parser records EXTH
            offset = record_count_pos + 4
            for _ in range(min(record_count, 100)):  # Limiter à 100 records
                if offset + 8 > len(content):
                    break

                # Record structure: type (4 bytes) + length (4 bytes) + data
                record_type = int.from_bytes(
                    content[offset : offset + 4], byteorder="big"
                )
                record_length = int.from_bytes(
                    content[offset + 4 : offset + 8], byteorder="big"
                )

                if offset + record_length > len(content):
                    break

                # Extraire données record
                if record_length > 8:
                    record_data = content[offset + 8 : offset + record_length]

                    # Types EXTH courants (valeurs standard MOBI)
                    # 100 = author, 101 = publisher, 103 = description, 104 = ISBN
                    # 105 = publish date, 106 = copyright, 503 = language

                    try:
                        if record_type == 100:  # Author
                            metadata["author"] = (
                                record_data.rstrip(b"\x00")
                                .decode("utf-8", errors="ignore")
                                .strip()
                            )
                        elif record_type == 101:  # Publisher
                            metadata["publisher"] = (
                                record_data.rstrip(b"\x00")
                                .decode("utf-8", errors="ignore")
                                .strip()
                            )
                        elif record_type == 104:  # ISBN
                            isbn_raw = (
                                record_data.rstrip(b"\x00")
                                .decode("utf-8", errors="ignore")
                                .strip()
                            )
                            # Nettoyer ISBN
                            isbn = re.sub(r"[-\s]", "", isbn_raw)
                            if re.match(r"^(?:\d{10}|\d{13})$", isbn):
                                metadata["isbn"] = isbn
                        elif record_type == 105:  # Publish date
                            date_str = (
                                record_data.rstrip(b"\x00")
                                .decode("utf-8", errors="ignore")
                                .strip()
                            )
                            year_match = re.search(r"\b(19|20)\d{2}\b", date_str)
                            if year_match:
                                metadata["year"] = year_match.group()
                        elif record_type == 503:  # Language
                            lang_raw = (
                                record_data.rstrip(b"\x00")
                                .decode("utf-8", errors="ignore")
                                .strip()
                            )
                            # Convertir code langue ISO si nécessaire
                            metadata["language"] = lang_raw or "en"
                    except Exception as e:
                        logger.debug(
                            f"Erreur parsing record EXTH type {record_type}: {e}"
                        )

                offset += record_length

                # Aligner sur 4 bytes
                offset = (offset + 3) & ~3

            # Titre souvent dans PalmDB name field (offset 0-64)
            # Essayer extraction titre depuis début fichier
            f.seek(0)
            name_field = f.read(64)
            if name_field:
                # PalmDB name : jusqu'à 32 bytes, null-terminated
                name_end = name_field.find(b"\x00")
                if name_end > 0:
                    try:
                        title_candidate = (
                            name_field[:name_end]
                            .decode("utf-8", errors="ignore")
                            .strip()
                        )
                        if title_candidate and not metadata.get("title"):
                            metadata["title"] = title_candidate
                    except (UnicodeDecodeError, ValueError) as e:
                        logger.debug(f"Erreur décodage titre PalmDB: {e}")
                        pass

            # Valeurs par défaut
            if not metadata.get("language"):
                metadata["language"] = "en"

            logger.info(f"Métadonnées MOBI extraites (parsing manuel): {path}")

    except Exception as e:
        logger.error(f"Erreur extraction métadonnées MOBI: {path}: {e}", exc_info=True)

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
