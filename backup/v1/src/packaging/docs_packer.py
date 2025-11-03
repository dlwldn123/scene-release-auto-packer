"""
Service de packaging DOCS conforme Scene Rules.

TDD - GREEN phase : Implémentation minimale pour faire passer les tests.
"""

import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import PyPDF2

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

from src.packaging import generate_diz, generate_nfo, generate_sfv, package_2022_format
from src.utils import generate_release_name

logger = logging.getLogger(__name__)


def extract_docs_metadata(doc_path: Path) -> Dict[str, Optional[str]]:
    """
    Extrait métadonnées depuis un document.

    Supporte : PDF, DOCX, TXT, ODT, RTF

    Args:
        doc_path: Chemin fichier document

    Returns:
        Dictionnaire métadonnées
    """
    metadata = {
        "title": None,
        "author": None,
        "publisher": None,
        "year": None,
        "language": "en",
        "format": doc_path.suffix[1:].upper() if doc_path.suffix else "UNKNOWN",
        "isbn": None,
    }

    ext = doc_path.suffix.lower()

    try:
        if ext == ".pdf":
            with open(doc_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                if pdf_reader.metadata:
                    metadata["title"] = pdf_reader.metadata.get("/Title")
                    metadata["author"] = pdf_reader.metadata.get("/Author")
                    metadata["publisher"] = pdf_reader.metadata.get("/Producer")
                    if "/CreationDate" in pdf_reader.metadata:
                        date_str = pdf_reader.metadata["/CreationDate"]
                        # Extraire année depuis format PDF date
                        if date_str and len(date_str) >= 4:
                            metadata["year"] = date_str[2:6]

        elif ext == ".docx" and DocxDocument:
            doc = DocxDocument(doc_path)
            core_props = doc.core_properties
            metadata["title"] = core_props.title
            metadata["author"] = core_props.author
            if core_props.created:
                metadata["year"] = str(core_props.created.year)

        elif ext == ".txt":
            # Parsing basique : première ligne = titre potentiel
            with open(doc_path, "r", encoding="utf-8", errors="ignore") as f:
                first_line = f.readline().strip()
                if first_line and len(first_line) < 100:
                    metadata["title"] = first_line

        elif ext == ".odt":
            # ODT est un ZIP contenant XML
            try:
                import xml.etree.ElementTree as ET
                import zipfile

                with zipfile.ZipFile(doc_path, "r") as odt_file:
                    # Lire meta.xml
                    if "meta.xml" in odt_file.namelist():
                        meta_xml = odt_file.read("meta.xml")
                        root = ET.fromstring(meta_xml)

                        # Namespace ODT
                        ns = {
                            "dc": "http://purl.org/dc/elements/1.1/",
                            "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
                        }

                        title_elem = root.find(".//dc:title", ns)
                        if title_elem is not None:
                            metadata["title"] = title_elem.text

                        creator_elem = root.find(".//dc:creator", ns)
                        if creator_elem is not None:
                            metadata["author"] = creator_elem.text

                        date_elem = root.find(".//meta:creation-date", ns)
                        if date_elem is not None and date_elem.text:
                            # Format: 2024-01-01T00:00:00
                            try:
                                date_text = date_elem.text.strip()
                                if len(date_text) >= 4:
                                    metadata["year"] = date_text[:4]
                            except (ValueError, IndexError, AttributeError) as e:
                                logger.debug(f"Erreur parsing date ODT: {e}")
            except Exception as e:
                logger.debug(f"Erreur extraction ODT: {e}")

        elif ext == ".rtf":
            # RTF : parsing basique (RTF est complexe, extraction minimale)
            RTF_MAX_READ_SIZE = 5000  # Nombre max de caractères à lire pour parsing RTF
            try:
                with open(doc_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(RTF_MAX_READ_SIZE)  # Lire les premiers caractères

                    # Chercher \title{...}
                    import re

                    title_match = re.search(r"\\title\s*([^{}]+)", content)
                    if title_match:
                        metadata["title"] = title_match.group(1).strip()

                    # Chercher \author{...}
                    author_match = re.search(r"\\author\s*([^{}]+)", content)
                    if author_match:
                        metadata["author"] = author_match.group(1).strip()
            except Exception as e:
                logger.debug(f"Erreur extraction RTF: {e}")

        # Fallback : utiliser nom fichier comme titre
        if not metadata["title"]:
            metadata["title"] = doc_path.stem

    except Exception as e:
        logger.warning(f"Erreur extraction métadonnées {ext}: {e}")

    return metadata


def pack_docs_release(
    doc_path: str | Path,
    group: str,
    output_dir: Optional[str | Path] = None,
    source_type: Optional[str] = None,
    url: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    nfo_template_path: Optional[str | Path] = None,
) -> str:
    """
    Packager un document en release Scene DOCS conforme.

    Processus:
    1. Détecter format
    2. Extraire métadonnées
    3. Générer nom release
    4. Créer structure release
    5. Packager (ZIP + RAR + NFO + DIZ + SFV)
    6. Valider release

    Args:
        doc_path: Chemin fichier document
        group: Tag groupe Scene
        output_dir: Dossier sortie (None = releases/)
        source_type: Type source ('RETAIL', 'SCAN', 'HYBRID', None=auto)
        url: URL release (optionnel)
        config: Configuration (None = charger depuis config.yaml)
        nfo_template_path: Chemin template NFO (optionnel)

    Returns:
        Nom release créé

    Raises:
        FileNotFoundError: Si document introuvable
        ValueError: Si group invalide
        RuntimeError: Si erreur packaging
    """
    doc_path = Path(doc_path)

    if not doc_path.exists():
        raise FileNotFoundError(f"Document introuvable: {doc_path}")

    logger.info(f"Packaging DOCS: {doc_path.name}")

    # Charger config si nécessaire
    if config is None:
        from src.packer import load_config

        config = load_config()

    # Détecter format
    format_type = doc_path.suffix[1:].lower() if doc_path.suffix else "unknown"
    format_type_upper = format_type.upper()

    # Extraire métadonnées
    logger.info(f"Extraction métadonnées DOCS: {format_type}")
    metadata = extract_docs_metadata(doc_path)

    # Générer nom release
    release_name = generate_release_name(
        metadata=metadata,
        format_type=format_type_upper,
        group_tag=group,
        source_type=source_type,
        filepath=str(doc_path),
    )

    logger.info(f"Nom release: {release_name}")

    # Dossier sortie
    if output_dir is None:
        output_dir = Path("releases")
    else:
        output_dir = Path(output_dir)

    release_dir = output_dir / release_name
    release_dir.mkdir(parents=True, exist_ok=True)

    # Copier document dans release_dir
    doc_copy = release_dir / doc_path.name
    import shutil

    shutil.copy2(doc_path, doc_copy)

    # Packager en ZIP multi-volumes (même règles que EBOOK)
    logger.info("Packaging ZIP multi-volumes...")
    zip_files = package_2022_format(
        ebook_path=doc_copy,
        output_dir=release_dir,
        release_name=release_name,
        config=config,
    )

    # Générer NFO
    logger.info("Génération NFO...")
    generate_nfo(
        release_name=release_name,
        metadata=metadata,
        group=group,
        url=url,
        release_dir=release_dir,
        template_path=nfo_template_path,
        max_width=config.get("nfo", {}).get("max_width", 80),
        ascii_art=config.get("nfo", {}).get("ascii_art", True),
    )

    # Générer DIZ
    logger.info("Génération DIZ...")
    diz_config = config.get("diz", {})
    generate_diz(
        release_name=release_name,
        release_dir=release_dir,
        num_disks=len(zip_files),
        filename=diz_config.get("filename", "FILE_ID.DIZ"),
        max_lines=diz_config.get("max_lines", 30),
        max_width=diz_config.get("max_width", 44),
    )

    # Générer SFV
    logger.info("Génération SFV...")
    generate_sfv(
        release_name=release_name,
        release_dir=release_dir,
    )

    # RAR inside ZIP si configuré
    rar_config = config.get("rar", {})
    if rar_config.get("create_for_zip", False):
        logger.info("Création RAR inside ZIP...")
        from src.packaging.rar import create_rar_volumes

        # Créer RAR depuis ZIP principal
        main_zip = zip_files[0] if zip_files else None
        if main_zip:
            create_rar_volumes(
                filepath=main_zip,
                output_dir=release_dir,
                volume_size_mb=15,
                method=rar_config.get("method", 5),
            )

    logger.info(f"Release DOCS créée: {release_name}")

    return release_name
