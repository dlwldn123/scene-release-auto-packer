"""
Module de validation de releases Scene.
"""

import logging
import re
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


def validate_release(
    release_dir: str | Path,
    release_name: str,
    verbose: bool = False,
    config: dict = None,
) -> Tuple[bool, List[str]]:
    """
    Valide une release Scene complète.

    Vérifications:
    1. Nommage conforme Scene Rules (si config.check_naming=True)
    2. Fichiers obligatoires présents (NFO, SFV, DIZ, ZIP/RAR, Sample)
    3. Structure dossiers correcte
    4. Contenu NFO valide (largeur ≤80 cols, encodage)
    5. Contenu SFV valide (format lignes)

    Args:
        release_dir: Dossier release
        release_name: Nom release
        verbose: Afficher détails validation
        config: Configuration validation (dict avec check_* flags)

    Returns:
        Tuple (is_valid, errors_list)
        - is_valid: True si release valide
        - errors_list: Liste messages d'erreur (vide si valide)
    """
    release_dir = Path(release_dir)
    errors = []

    if config is None:
        config = {}

    # Vérifier existence dossier
    if not release_dir.exists():
        errors.append(f"Dossier release introuvable: {release_dir}")
        return (False, errors)

    # 1. Validation nommage (si activée)
    if config.get("check_naming", True):
        if not _validate_naming(release_name):
            errors.append(f"Nom release invalide (format Scene Rules): {release_name}")

    # 2. Fichiers obligatoires
    check_nfo = config.get("check_nfo", True)
    check_sfv = config.get("check_sfv", True)
    check_diz = config.get("check_diz", True)
    check_rar = config.get("check_rar", True)
    check_sample = config.get("check_sample", True)

    if check_nfo:
        nfo_files = list(release_dir.glob("*.nfo"))
        if not nfo_files:
            errors.append("Fichier NFO manquant")
        else:
            # Valider contenu NFO
            nfo_path = nfo_files[0]
            nfo_errors = _validate_nfo_content(nfo_path)
            errors.extend(nfo_errors)

    if check_sfv:
        sfv_files = list(release_dir.glob("*.sfv"))
        if not sfv_files:
            errors.append("Fichier SFV manquant")
        else:
            # Valider contenu SFV
            sfv_path = sfv_files[0]
            sfv_errors = _validate_sfv_content(sfv_path)
            errors.extend(sfv_errors)

    if check_diz:
        diz_files = list(release_dir.glob("FILE_ID.DIZ"))
        if not diz_files:
            errors.append("Fichier DIZ (FILE_ID.DIZ) manquant")

    if check_rar:
        # Vérifier présence ZIP ou RAR volumisés
        zip_files = list(release_dir.glob("*.ZIP")) + list(release_dir.glob("*.Z*"))
        rar_files = list(release_dir.glob("*.rar")) + list(release_dir.glob("*.r*"))

        if not zip_files and not rar_files:
            errors.append("Aucune archive ZIP ou RAR volumisée trouvée")

    if check_sample:
        sample_dir = release_dir / "Sample"
        if not sample_dir.exists():
            errors.append("Dossier Sample/ manquant")
        else:
            sample_files = list(sample_dir.glob("*"))
            if not sample_files:
                errors.append("Aucun fichier sample dans dossier Sample/")

    # 3. Structure dossiers
    # Sample/ doit exister si check_sample=True
    # Fichiers principaux dans racine release_dir

    is_valid = len(errors) == 0

    if verbose:
        if is_valid:
            logger.info(f"Release valide: {release_name}")
        else:
            logger.warning(
                f"Release invalide: {release_name} ({len(errors)} erreur(s))"
            )

    return (is_valid, errors)


def _validate_naming(release_name: str) -> bool:
    """
    Valide format nom release conforme Scene Rules 2022.

    Format attendu: author.title.year.source.format-lang.group

    Args:
        release_name: Nom release

    Returns:
        True si format valide
    """
    # Vérifier structure basique (au moins 5 parties séparées par points)
    parts = release_name.split(".")
    if len(parts) < 5:
        return False

    # Vérifier présence format-lang (partie avec tiret)
    has_format_lang = any("-" in part for part in parts)
    if not has_format_lang:
        return False

    # Vérifier caractères autorisés (a-z, 0-9, points, tirets, underscores)
    if not re.match(r"^[a-z0-9._-]+$", release_name.lower()):
        return False

    # Vérifier longueur max 255
    if len(release_name) > 255:
        return False

    return True


def _validate_nfo_content(nfo_path: Path) -> List[str]:
    """
    Valide contenu fichier NFO.

    Vérifications:
    - Largeur lignes ≤80 colonnes
    - Encodage ASCII/UTF-8 valide

    Args:
        nfo_path: Chemin fichier NFO

    Returns:
        Liste erreurs (vide si valide)
    """
    errors = []

    try:
        with open(nfo_path, "rb") as f:
            content_bytes = f.read()

        # Vérifier encodage
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content = content_bytes.decode("windows-1252")
            except UnicodeDecodeError:
                errors.append(f"NFO encodage invalide: {nfo_path}")
                return errors

        # Vérifier largeur lignes (max 80 colonnes)
        for i, line in enumerate(content.splitlines(), 1):
            line_length = len(line)
            if line_length > 80:
                errors.append(
                    f"NFO ligne {i} trop longue ({line_length} > 80 colonnes): {nfo_path}"
                )

    except Exception as e:
        errors.append(f"Erreur lecture NFO: {nfo_path}: {e}")

    return errors


def _validate_sfv_content(sfv_path: Path) -> List[str]:
    """
    Valide contenu fichier SFV.

    Vérifications:
    - Format lignes: <filename> <crc32> (ou commentaires avec ;)

    Args:
        sfv_path: Chemin fichier SFV

    Returns:
        Liste erreurs (vide si valide)
    """
    errors = []

    try:
        with open(sfv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Format ligne SFV : <filename> <crc32> ou commentaire (;)
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith(";"):
                continue  # Commentaire ou ligne vide

            # Vérifier format: filename crc32 (hexadécimal 8 chars)
            parts = line.split()
            if len(parts) != 2:
                errors.append(f"SFV ligne {i} format invalide: {line}")
                continue

            filename, crc32 = parts
            if not re.match(r"^[0-9A-Fa-f]{8}$", crc32):
                errors.append(f"SFV ligne {i} CRC32 invalide: {crc32}")

    except Exception as e:
        errors.append(f"Erreur lecture SFV: {sfv_path}: {e}")

    return errors
