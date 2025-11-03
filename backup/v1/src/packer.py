#!/usr/bin/env python3
"""
Script principal CLI pour packaging d'eBooks au format Scene Release.
"""

import argparse
import hashlib
import logging
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional

import yaml

# Imports modules locaux
from src.metadata import (
    MetadataEnricher,
    detect_format,
    extract_epub_metadata,
    extract_mobi_metadata,
    extract_pdf_metadata,
)
from src.packaging import (
    create_rar_volumes,
    generate_diz,
    generate_nfo,
    generate_sfv,
    package_2022_format,
)
from src.utils import generate_release_name, validate_release

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_config(config_path: Optional[str | Path] = None) -> dict:
    """
    Charge configuration depuis config.yaml ou retourne valeurs par défaut.

    Args:
        config_path: Chemin fichier config (None = config/config.yaml)

    Returns:
        Dictionnaire configuration
    """
    if config_path is None:
        config_path = Path("config/config.yaml")
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        logger.warning(
            f"Config introuvable: {config_path}, utilisation valeurs par défaut"
        )
        return _default_config()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        logger.info(f"Configuration chargée: {config_path}")
        return config
    except Exception as e:
        logger.error(f"Erreur chargement config: {e}, utilisation valeurs par défaut")
        return _default_config()


def _default_config() -> dict:
    """Retourne configuration par défaut."""
    return {
        "api": {
            "enable_googlebooks": True,
            "enable_openlibrary": True,
            "rate_limit_delay": 0.5,
            "timeout": 10,
        },
        "diz": {
            "filename": "FILE_ID.DIZ",
            "max_lines": 30,
            "max_width": 44,
        },
        "nfo": {
            "ascii_art": True,
            "max_width": 80,
            "template_path": "templates/nfo_template.txt",
        },
        "rar": {
            "create_for_zip": True,
            "method": 5,
        },
        "sample": {
            "pdf": {"amount": 3, "type": "pages"},
            "epub": {"amount": 1, "type": "chapter"},
            "mobi": {"amount": 1, "type": "chapter"},
            "azw": {"amount": 1, "type": "chapter"},
            "cbz": {"amount": 5, "type": "pages"},
        },
        "validation": {
            "check_naming": True,
            "check_nfo": True,
            "check_rar": True,
            "check_sample": True,
            "check_sfv": True,
        },
        "zip": {
            "allowed_sizes": [
                5000000,
                10000000,
                50000000,
                100000000,
                150000000,
                200000000,
                250000000,
            ],
            "use_83_rule": True,
        },
    }


def process_ebook(
    ebook_path: str | Path,
    group: str,
    output_dir: Optional[str | Path] = None,
    source_type: Optional[str] = None,
    url: Optional[str] = None,
    enable_api: bool = True,
    config: Optional[dict] = None,
    verbose: bool = False,
    nfo_template_path: Optional[str | Path] = None,
) -> str:
    """
    Traite un eBook et crée release Scene complète.

    Processus:
    1. Détecter format
    2. Extraire métadonnées
    3. Enrichir via APIs (optionnel)
    4. Générer nom release
    5. Créer sample
    6. Packager (ZIP + RAR + NFO + SFV + DIZ)
    7. Valider release

    Args:
        ebook_path: Chemin fichier eBook
        group: Tag groupe Scene
        output_dir: Dossier sortie (None = releases/)
        source_type: Type source ('RETAIL', 'SCAN', 'HYBRID', None=auto)
        url: URL release (optionnel)
        enable_api: Activer enrichissement API (défaut True)
        config: Configuration (None = charger depuis config.yaml)
        verbose: Mode verbose (défaut False)

    Returns:
        Nom release créé

    Raises:
        FileNotFoundError: Si eBook introuvable
        ValueError: Si group invalide
        RuntimeError: Si erreur packaging
    """
    ebook_path = Path(ebook_path)

    if not ebook_path.exists():
        raise FileNotFoundError(f"eBook introuvable: {ebook_path}")

    if config is None:
        config = load_config()

    # Configuration logging
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Détecter format
    logger.info(f"Détection format: {ebook_path}")
    format_type = detect_format(ebook_path)
    if not format_type:
        # Fallback : utiliser extension
        format_type = ebook_path.suffix[1:].lower() if ebook_path.suffix else "unknown"
        logger.warning(f"Format non détecté, utilisation extension: {format_type}")

    format_type_upper = format_type.upper()

    # Extraire métadonnées
    logger.info(f"Extraction métadonnées: {format_type}")
    metadata = _extract_metadata_by_format(ebook_path, format_type)

    # Enrichissement API
    if enable_api:
        logger.info("Enrichissement métadonnées via APIs...")
        api_config = config.get("api", {})
        enricher = MetadataEnricher(
            enable_googlebooks=api_config.get("enable_googlebooks", True),
            enable_openlibrary=api_config.get("enable_openlibrary", True),
            timeout=api_config.get("timeout", 10),
            rate_limit_delay=api_config.get("rate_limit_delay", 0.5),
        )
        metadata = enricher.enrich(metadata)
        if metadata.get("api_sources"):
            logger.info(f"Sources API utilisées: {', '.join(metadata['api_sources'])}")

    # Générer nom release
    logger.info("Génération nom release...")
    release_name = generate_release_name(
        metadata,
        format_type_upper,
        group,
        source_type=source_type,
        filepath=str(ebook_path),
    )

    # Créer dossier release
    if output_dir is None:
        output_dir = Path("releases")
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    release_dir = output_dir / release_name
    release_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Release: {release_name}")
    logger.info(f"Dossier: {release_dir}")

    # Copier eBook dans release
    ebook_dest = release_dir / ebook_path.name
    shutil.copy2(ebook_path, ebook_dest)
    logger.info(f"eBook copié: {ebook_dest}")

    # Créer sample
    sample_dir = release_dir / "Sample"
    sample_dir.mkdir(exist_ok=True)
    _create_sample(ebook_path, sample_dir, format_type, config)

    # Packager (ZIP + RAR)
    logger.info("Packaging format 2022...")
    zip_config = config.get("zip", {})
    rar_config = config.get("rar", {})

    packaging_config = {
        "zip": zip_config,
        "rar": rar_config,
    }

    zip_files = package_2022_format(
        ebook_dest,
        release_dir,
        release_name,
        config=packaging_config,
    )

    logger.info(f"{len(zip_files)} volume(s) ZIP créé(s)")

    # Générer fichiers NFO, SFV, DIZ
    logger.info("Génération fichiers release...")

    nfo_config = config.get("nfo", {})
    generate_nfo(
        release_name,
        metadata,
        group,
        url=url,
        release_dir=release_dir,
        template_path=(
            str(nfo_template_path)
            if nfo_template_path
            else nfo_config.get("template_path")
        ),
        max_width=nfo_config.get("max_width", 80),
    )

    generate_sfv(
        release_name,
        release_dir,
    )

    diz_config = config.get("diz", {})
    # Compter volumes ZIP pour DIZ
    num_disks = len(zip_files)
    generate_diz(
        release_name,
        release_dir,
        num_disks=num_disks,
        filename=diz_config.get("filename", "FILE_ID.DIZ"),
        max_lines=diz_config.get("max_lines", 30),
        max_width=diz_config.get("max_width", 44),
    )

    # Valider release
    logger.info("Validation release...")
    validation_config = config.get("validation", {})
    is_valid, errors = validate_release(
        release_dir,
        release_name,
        verbose=verbose,
        config=validation_config,
    )

    if not is_valid:
        logger.warning(f"Release invalide ({len(errors)} erreur(s)):")
        for error in errors:
            logger.warning(f"  - {error}")
    else:
        logger.info("✓ Release valide")

    return release_name


def _extract_metadata_by_format(
    filepath: Path, format_type: str
) -> Dict[str, Optional[str]]:
    """
    Extrait métadonnées selon format détecté.

    Args:
        filepath: Chemin fichier eBook
        format_type: Format détecté ('epub', 'pdf', 'mobi', etc.)

    Returns:
        Dictionnaire métadonnées
    """
    format_type_lower = format_type.lower()

    if format_type_lower == "epub":
        return extract_epub_metadata(filepath)
    elif format_type_lower in ("mobi", "azw", "azw3"):
        return extract_mobi_metadata(filepath)
    elif format_type_lower == "pdf":
        return extract_pdf_metadata(filepath)
    elif format_type_lower == "cbz":
        # CBZ: métadonnées minimales (nom fichier = titre)
        return {
            "title": filepath.stem,
            "author": None,
            "publisher": None,
            "language": "en",
            "year": None,
            "isbn": None,
            "format": "CBZ",
            "api_sources": [],
        }
    else:
        # Format inconnu : métadonnées minimales
        logger.warning(f"Format inconnu: {format_type}, métadonnées minimales")
        return {
            "title": filepath.stem,
            "author": None,
            "publisher": None,
            "language": "en",
            "year": None,
            "isbn": None,
            "format": format_type_upper,
            "api_sources": [],
        }


def _create_sample(
    ebook_path: Path,
    sample_dir: Path,
    format_type: str,
    config: dict,
) -> Optional[Path]:
    """
    Crée fichier sample selon format.

    - PDF : Extraire 3 premières pages
    - EPUB/MOBI/AZW : Copie complète (extraction chapitres complexe, simplifié)
    - CBZ : Copie complète

    Args:
        ebook_path: Chemin fichier eBook
        sample_dir: Dossier Sample/
        format_type: Format détecté
        config: Configuration (section sample)

    Returns:
        Chemin fichier sample créé ou None si échec
    """
    format_type_lower = format_type.lower()
    sample_config = config.get("sample", {})

    # Nom sample
    sample_name = f"{ebook_path.stem}-sample{ebook_path.suffix}"
    sample_path = sample_dir / sample_name

    try:
        if format_type_lower == "pdf":
            # Extraire premières pages PDF
            pages_config = sample_config.get("pdf", {})
            num_pages = pages_config.get("amount", 3)

            try:
                from PyPDF2 import PdfReader, PdfWriter

                reader = PdfReader(ebook_path)
                writer = PdfWriter()

                # Extraire premières pages
                max_pages = min(num_pages, len(reader.pages))
                for i in range(max_pages):
                    writer.add_page(reader.pages[i])

                with open(sample_path, "wb") as f:
                    writer.write(f)

                logger.info(f"Sample PDF créé: {sample_path} ({max_pages} page(s))")
                return sample_path

            except ImportError:
                logger.warning(
                    "PyPDF2 indisponible, copie complète fichier comme sample"
                )
                shutil.copy2(ebook_path, sample_path)
            except Exception as e:
                logger.warning(f"Erreur extraction pages PDF: {e}, copie complète")
                shutil.copy2(ebook_path, sample_path)

        elif format_type_lower in ("epub", "mobi", "azw", "azw3", "cbz"):
            # Copie complète (extraction chapitres complexe, simplifié pour MVP)
            shutil.copy2(ebook_path, sample_path)
            logger.info(f"Sample créé (copie): {sample_path}")
            return sample_path

        else:
            # Format inconnu : copie complète
            shutil.copy2(ebook_path, sample_path)
            logger.info(f"Sample créé (copie, format inconnu): {sample_path}")
            return sample_path

    except Exception as e:
        logger.error(f"Erreur création sample: {e}", exc_info=True)
        return None


def main():
    """Point d'entrée CLI principal."""
    parser = argparse.ArgumentParser(
        description="Scene Ebook Packer - Packaging d'eBooks au format Scene Release",
    )

    parser.add_argument(
        "ebook",
        type=str,
        help="Chemin fichier eBook (EPUB, PDF, MOBI, etc.)",
    )

    parser.add_argument(
        "-g",
        "--group",
        type=str,
        required=True,
        help="Tag groupe Scene (ex: MYGRP)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Dossier sortie release (défaut: releases/)",
    )

    parser.add_argument(
        "-s",
        "--source",
        type=str,
        choices=["RETAIL", "SCAN", "HYBRID"],
        default=None,
        help="Type source (RETAIL, SCAN, HYBRID, défaut: auto-détection)",
    )

    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="URL release (optionnel)",
    )

    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Désactiver enrichissement API",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=None,
        help="Chemin fichier config (défaut: config/config.yaml)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Mode verbose",
    )

    args = parser.parse_args()

    # Configuration logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        config = load_config(args.config)

        release_name = process_ebook(
            ebook_path=args.ebook,
            group=args.group,
            output_dir=args.output,
            source_type=args.source,
            url=args.url,
            enable_api=not args.no_api,
            config=config,
            verbose=args.verbose,
        )

        print(f"\n✓ Release créée avec succès: {release_name}")
        sys.exit(0)

    except FileNotFoundError as e:
        logger.error(f"Fichier introuvable: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Erreur validation: {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Erreur packaging: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interruption utilisateur")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
