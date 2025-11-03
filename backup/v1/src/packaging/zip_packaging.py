"""
Module de packaging au format Scene 2022 (ZIP volumisés contenant RAR).
"""

import logging
import zipfile
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def package_2022_format(
    ebook_path: str | Path,
    output_dir: str | Path,
    release_name: str,
    config: Optional[dict] = None,
) -> List[Path]:
    """
    Crée release au format Scene 2022 : ZIP volumisés contenant RAR inside.

    Algorithme:
    1. Créer RAR de l'ebook
    2. Créer volumes ZIP contenant RAR
    3. Sélection automatique taille volumes selon taille ebook

    Args:
        ebook_path: Chemin fichier eBook
        output_dir: Dossier de sortie pour release
        release_name: Nom release (sans extension)
        config: Configuration (dict avec rar, zip settings, optionnel)

    Returns:
        Liste chemins fichiers ZIP créés (zip, z01, z02, etc.)

    Raises:
        RuntimeError: Si erreur création ZIP/RAR
        IOError: Si erreur I/O fichier
    """
    ebook_path = Path(ebook_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not ebook_path.exists():
        raise FileNotFoundError(f"eBook introuvable: {ebook_path}")

    # Configuration par défaut
    if config is None:
        config = {}

    rar_config = config.get("rar", {})
    zip_config = config.get("zip", {})

    rar_method = rar_config.get("method", 5)
    zip_allowed_sizes = zip_config.get(
        "allowed_sizes",
        [5000000, 10000000, 50000000, 100000000, 150000000, 200000000, 250000000],
    )

    # Étape 1 : Créer RAR de l'ebook
    from src.packaging.rar import create_rar_volumes

    rar_volume_size = 15  # 15MB par défaut pour volumes RAR
    try:
        rar_files = create_rar_volumes(
            ebook_path,
            output_dir / "temp_rar",
            volume_size_mb=rar_volume_size,
            method=rar_method,
        )
        logger.info(f"RAR créé: {len(rar_files)} volume(s)")
    except RuntimeError as e:
        logger.error(f"Erreur création RAR: {e}")
        raise RuntimeError(f"Impossible créer RAR: {e}")

    # Étape 2 : Sélectionner taille volumes ZIP
    total_size = sum(f.stat().st_size for f in rar_files)
    zip_volume_size = select_zip_size(total_size, zip_allowed_sizes)

    logger.info(
        f"Taille volumes ZIP sélectionnée: {zip_volume_size / (1024*1024):.1f} MB"
    )

    # Étape 3 : Créer volumes ZIP contenant RAR
    zip_files = _create_zip_volumes(
        rar_files,
        output_dir,
        release_name,
        zip_volume_size,
    )

    # Nettoyer fichiers RAR temporaires (optionnel, garder pour debug)
    # import shutil
    # shutil.rmtree(output_dir / "temp_rar", ignore_errors=True)

    return zip_files


def select_zip_size(total_size: int, allowed_sizes: List[int]) -> int:
    """
    Sélectionne taille volumes ZIP selon taille totale fichier.

    Algorithme:
    - < 5MB : volumes 5MB max
    - < 50MB : volumes 10MB
    - < 100MB : volumes 50MB
    - < 200MB : volumes 100MB
    - < 250MB : volumes 150MB
    - >= 250MB : volumes 200MB (max 250MB selon config)

    Args:
        total_size: Taille totale en bytes
        allowed_sizes: Liste tailles autorisées en bytes

    Returns:
        Taille volume sélectionnée en bytes
    """
    # Tailles en bytes
    size_5mb = 5 * 1024 * 1024
    size_10mb = 10 * 1024 * 1024
    size_50mb = 50 * 1024 * 1024
    size_100mb = 100 * 1024 * 1024
    size_150mb = 150 * 1024 * 1024
    size_200mb = 200 * 1024 * 1024
    size_250mb = 250 * 1024 * 1024

    # Sélection selon taille
    if total_size < size_5mb:
        return min([s for s in allowed_sizes if s >= size_5mb] or allowed_sizes)
    elif total_size < size_50mb:
        return min(
            [s for s in allowed_sizes if s >= size_10mb] or allowed_sizes,
            key=lambda x: abs(x - size_10mb),
        )
    elif total_size < size_100mb:
        return min(
            [s for s in allowed_sizes if size_50mb <= s <= size_100mb] or allowed_sizes,
            key=lambda x: abs(x - size_50mb),
        )
    elif total_size < size_200mb:
        return min(
            [s for s in allowed_sizes if size_100mb <= s <= size_200mb]
            or allowed_sizes,
            key=lambda x: abs(x - size_100mb),
        )
    elif total_size < size_250mb:
        return min(
            [s for s in allowed_sizes if size_150mb <= s <= size_250mb]
            or allowed_sizes,
            key=lambda x: abs(x - size_150mb),
        )
    else:
        # >= 250MB : volumes 200MB max (ou 250MB si configuré)
        return min([s for s in allowed_sizes if s >= size_200mb] or allowed_sizes)

    # Fallback : prendre taille la plus proche
    return min(allowed_sizes, key=lambda x: abs(x - total_size))


def _create_zip_volumes(
    files_to_zip: List[Path],
    output_dir: Path,
    release_name: str,
    volume_size: int,
) -> List[Path]:
    """
    Crée volumes ZIP depuis liste fichiers.

    Args:
        files_to_zip: Liste fichiers à inclure dans ZIP
        output_dir: Dossier de sortie
        release_name: Nom release (sans extension)
        volume_size: Taille maximum volume ZIP en bytes

    Returns:
        Liste chemins fichiers ZIP créés
    """
    zip_files = []
    current_zip_num = 0
    current_zip_size = 0
    current_zip = None

    for file_path in files_to_zip:
        file_size = file_path.stat().st_size

        # Si nouveau volume nécessaire
        if current_zip is None or (
            current_zip_size + file_size > volume_size and current_zip_size > 0
        ):
            if current_zip is not None:
                current_zip.close()

            # Nom fichier ZIP
            if current_zip_num == 0:
                zip_filename = f"{release_name}.ZIP"
            else:
                zip_filename = f"{release_name}.Z{current_zip_num:02d}"

            zip_path = output_dir / zip_filename
            current_zip = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
            current_zip_size = 0
            current_zip_num += 1

            zip_files.append(zip_path)
            logger.info(f"Création volume ZIP: {zip_path}")

        # Ajouter fichier au ZIP courant
        arcname = file_path.name
        current_zip.write(file_path, arcname=arcname)
        current_zip_size += file_size

    # Fermer dernier ZIP
    if current_zip is not None:
        current_zip.close()

    return zip_files
