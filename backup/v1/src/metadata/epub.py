"""
Module d'extraction de métadonnées depuis fichiers EPUB.
"""

import logging
import re
import zipfile
from pathlib import Path
from typing import Dict, Optional
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


def extract_epub_metadata(filepath: str | Path) -> Dict[str, Optional[str]]:
    """
    Extrait les métadonnées d'un fichier EPUB.

    Méthode : Parser XML metadata.opf après localisation via container.xml.
    Utilise ebookmeta si disponible, sinon parsing manuel XML.

    Args:
        filepath: Chemin vers fichier EPUB

    Returns:
        Dictionnaire métadonnées avec champs:
        - title, author, publisher, language, year, isbn, format, api_sources
        (valeurs None si absentes)
    """
    path = Path(filepath)

    if not path.exists():
        logger.error(f"Fichier EPUB introuvable: {path}")
        return _empty_metadata()

    metadata = _empty_metadata()
    metadata["format"] = "EPUB"

    # Tentative avec ebookmeta si disponible
    try:
        import ebookmeta

        book = ebookmeta.read_epub(str(path))
        metadata["title"] = book.title or None
        metadata["author"] = book.author or None
        metadata["publisher"] = book.publisher or None
        metadata["language"] = book.language or "en"
        metadata["isbn"] = book.isbn or None
        # Extraire année depuis date
        if book.pub_date:
            year_match = re.search(r"\b(19|20)\d{2}\b", str(book.pub_date))
            if year_match:
                metadata["year"] = year_match.group()

        logger.info(f"Métadonnées EPUB extraites avec ebookmeta: {path}")
        return metadata
    except ImportError:
        logger.debug("ebookmeta non disponible, utilisation parsing manuel")
    except Exception as e:
        logger.warning(f"ebookmeta échoué, fallback parsing manuel: {e}")

    # Parsing manuel XML
    try:
        with zipfile.ZipFile(path, "r") as zipf:
            # Lire container.xml pour localiser metadata.opf
            container_xml = zipf.read("META-INF/container.xml").decode("utf-8")
            container_root = ET.fromstring(container_xml)

            # Namespace OEBPS
            ns = {"container": "urn:oasis:names:tc:opendocument:xmlns:container"}

            # Trouver rootfile
            rootfile = container_root.find(".//container:rootfile", ns)
            if rootfile is None:
                logger.warning(f"rootfile introuvable dans container.xml: {path}")
                return metadata

            opf_path = rootfile.get("full-path")
            if not opf_path:
                logger.warning(f"full-path introuvable dans rootfile: {path}")
                return metadata

            # Lire metadata.opf
            opf_content = zipf.read(opf_path).decode("utf-8")
            opf_root = ET.fromstring(opf_content)

            # Namespaces Dublin Core et OPF
            ns_dc = {
                "dc": "http://purl.org/dc/elements/1.1/",
                "opf": "http://www.idpf.org/2007/opf",
            }

            # Extraire titre
            title_elem = opf_root.find(".//dc:title", ns_dc)
            if title_elem is None:
                title_elem = opf_root.find('.//*[@property="dcterms:title"]', ns_dc)
            if title_elem is not None and title_elem.text:
                metadata["title"] = title_elem.text.strip()

            # Extraire auteur (premier créateur trouvé)
            creator_elems = opf_root.findall(".//dc:creator", ns_dc)
            if creator_elems:
                creator = creator_elems[0]
                # Utiliser attribut file-as si disponible
                file_as = creator.get("file-as", creator.text)
                metadata["author"] = file_as.strip() if file_as else None

            # Extraire éditeur
            publisher_elem = opf_root.find(".//dc:publisher", ns_dc)
            if publisher_elem is not None and publisher_elem.text:
                metadata["publisher"] = publisher_elem.text.strip()

            # Extraire langue (première trouvée, défaut 'en')
            language_elems = opf_root.findall(".//dc:language", ns_dc)
            if language_elems:
                metadata["language"] = (
                    language_elems[0].text.strip() if language_elems[0].text else "en"
                )
            else:
                metadata["language"] = "en"

            # Extraire année depuis date
            date_elems = opf_root.findall(".//dc:date", ns_dc)
            for date_elem in date_elems:
                if date_elem.text:
                    year_match = re.search(r"\b(19|20)\d{2}\b", date_elem.text)
                    if year_match:
                        metadata["year"] = year_match.group()
                        break

            # Extraire ISBN depuis identifiants
            identifier_elems = opf_root.findall(".//dc:identifier", ns_dc)
            for id_elem in identifier_elems:
                scheme = id_elem.get("scheme", "").upper()
                id_text = id_elem.text or ""

                if scheme == "ISBN" or "ISBN" in id_text.upper():
                    # Nettoyer ISBN (supprimer tirets, espaces)
                    isbn = re.sub(r"[-\s]", "", id_text)
                    # Vérifier format ISBN (10 ou 13 chiffres)
                    if re.match(r"^(?:\d{10}|\d{13})$", isbn):
                        metadata["isbn"] = isbn
                        break
                else:
                    # Détection pattern ISBN dans identifiant
                    isbn_match = re.search(
                        r"ISBN[\s\-:]*([0-9X]{10,13})", id_text, re.IGNORECASE
                    )
                    if isbn_match:
                        isbn = re.sub(r"[-\s]", "", isbn_match.group(1))
                        if re.match(r"^(?:\d{10}|\d{13})$", isbn):
                            metadata["isbn"] = isbn
                            break

            logger.info(f"Métadonnées EPUB extraites (parsing manuel): {path}")

    except zipfile.BadZipFile:
        logger.error(f"Fichier EPUB invalide (ZIP corrompu): {path}")
    except Exception as e:
        logger.error(f"Erreur extraction métadonnées EPUB: {path}: {e}", exc_info=True)

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
