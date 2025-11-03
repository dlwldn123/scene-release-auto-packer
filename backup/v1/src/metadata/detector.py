"""
Module de détection du format de fichier eBook.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def detect_format(filepath: str | Path) -> Optional[str]:
    """
    Détecte le format d'un fichier eBook par vérification extension + header binaire.

    Formats supportés : EPUB, MOBI, AZW, AZW3, PDF, CBZ

    Args:
        filepath: Chemin vers le fichier eBook

    Returns:
        Format détecté en minuscules ('epub', 'pdf', 'mobi', etc.) ou None si
        format inconnu ou fichier introuvable
    """
    path = Path(filepath)

    if not path.exists():
        logger.warning(f"Fichier introuvable: {path}")
        return None

    # Vérifier extension d'abord
    ext = path.suffix.lower()

    # EPUB : vérifier ZIP magic bytes + présence mimetype
    if ext == ".epub":
        try:
            with open(path, "rb") as f:
                header = f.read(4)
                if header == b"PK\x03\x04":  # ZIP magic bytes
                    # Vérifier présence mimetype
                    import zipfile

                    try:
                        with zipfile.ZipFile(path, "r") as zipf:
                            if "mimetype" in zipf.namelist():
                                mimetype_content = zipf.read("mimetype").decode(
                                    "utf-8", errors="ignore"
                                )
                                if "application/epub+zip" in mimetype_content:
                                    return "epub"
                    except Exception as e:
                        logger.debug(f"Erreur vérification EPUB: {e}")
        except Exception as e:
            logger.debug(f"Erreur lecture header EPUB: {e}")

    # MOBI/AZW : Vérifier signature BOOKMOBI ou TEXtREAd
    if ext in (".mobi", ".azw", ".azw3"):
        try:
            with open(path, "rb") as f:
                # Lire offset 60-67 pour vérifier signature MOBI
                f.seek(60)
                mobi_sig = f.read(8)
                if mobi_sig[:4] == b"BOOK" or mobi_sig[:4] == b"TEXt":
                    # Vérifier signature complète
                    f.seek(60)
                    header = f.read(68)
                    if b"BOOKMOBI" in header or b"TEXtREAd" in header:
                        if ext == ".azw3":
                            return "azw3"
                        elif ext == ".azw":
                            return "azw"
                        else:
                            return "mobi"
        except Exception as e:
            logger.debug(f"Erreur lecture header MOBI: {e}")

    # PDF : Vérifier magic bytes %PDF
    if ext == ".pdf":
        try:
            with open(path, "rb") as f:
                header = f.read(4)
                if header == b"%PDF":
                    return "pdf"
        except Exception as e:
            logger.debug(f"Erreur lecture header PDF: {e}")

    # CBZ : Vérifier ZIP magic bytes + convention nommage
    if ext == ".cbz":
        try:
            with open(path, "rb") as f:
                header = f.read(4)
                if header == b"PK\x03\x04":
                    # CBZ est un ZIP contenant des images
                    return "cbz"
        except Exception as e:
            logger.debug(f"Erreur lecture header CBZ: {e}")

    # Fallback : utiliser extension fichier comme format présumé
    if ext in (".epub", ".mobi", ".azw", ".azw3", ".pdf", ".cbz"):
        format_map = {
            ".epub": "epub",
            ".mobi": "mobi",
            ".azw": "azw",
            ".azw3": "azw3",
            ".pdf": "pdf",
            ".cbz": "cbz",
        }
        logger.info(f"Format détecté par extension: {format_map.get(ext)}")
        return format_map.get(ext)

    logger.warning(f"Format inconnu pour fichier: {path}")
    return None
