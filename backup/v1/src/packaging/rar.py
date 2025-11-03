"""
Module de création d'archives RAR volumisées pour releases Scene.
"""

import logging
import subprocess
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def create_rar_volumes(
    filepath: str | Path,
    output_dir: str | Path,
    volume_size_mb: int = 15,
    method: int = 5,
) -> List[Path]:
    """
    Crée archives RAR volumisées depuis un fichier.

    Méthode : Utilise RAR CLI avec options compression et volumes.
    Fallback : Librairie Python rarfile si CLI indisponible (non implémenté car rarfile
    ne supporte pas création, seulement extraction).

    Args:
        filepath: Chemin fichier à archiver
        output_dir: Dossier de sortie pour archives RAR
        volume_size_mb: Taille volumes RAR en MB (défaut 15MB)
        method: Méthode compression (0-5, 5=Best, défaut 5)

    Returns:
        Liste chemins fichiers RAR créés (rar, r01, r02, etc.)

    Raises:
        RuntimeError: Si RAR CLI indisponible ou erreur création
    """
    filepath = Path(filepath)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not filepath.exists():
        raise FileNotFoundError(f"Fichier introuvable: {filepath}")

    # Nom archive RAR basé sur nom fichier
    rar_basename = filepath.stem
    rar_path = output_dir / f"{rar_basename}.rar"

    # Vérifier RAR CLI disponible
    if not _check_rar_cli():
        raise RuntimeError(
            "RAR CLI non disponible. "
            "Installation: sudo apt-get install rar (Debian/Ubuntu) "
            "ou brew install rar (macOS)"
        )

    # Commande RAR : rar a -m{method} -v{size}M <output.rar> <input>
    volume_size_str = f"{volume_size_mb}M"

    cmd = [
        "rar",
        "a",  # Add files to archive
        f"-m{method}",  # Compression method
        f"-v{volume_size_str}",  # Volume size
        str(rar_path),
        str(filepath),
    ]

    try:
        logger.info(f"Création RAR volumes: {filepath} -> {rar_path}")
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )

        # Lister fichiers RAR créés
        rar_files = sorted(list(output_dir.glob(f"{rar_basename}.rar"))) + sorted(
            list(output_dir.glob(f"{rar_basename}.r*"))
        )

        # Filtrer seulement fichiers RAR (rar, r01, r02, etc.)
        rar_files = [
            f
            for f in rar_files
            if f.suffix.lower() == ".rar"
            or (
                f.suffix.lower().startswith(".r")
                and len(f.suffix) >= 2
                and f.suffix[1:].isdigit()
            )
        ]

        logger.info(f"{len(rar_files)} volume(s) RAR créé(s)")
        return rar_files

    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur création RAR: {e.stderr}")
        raise RuntimeError(f"Erreur création RAR: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("RAR CLI non trouvé dans PATH")
    except Exception as e:
        logger.error(f"Erreur inattendue création RAR: {e}", exc_info=True)
        raise RuntimeError(f"Erreur création RAR: {e}")


def _check_rar_cli() -> bool:
    """
    Vérifie si RAR CLI est disponible dans PATH.

    Returns:
        True si RAR CLI disponible, False sinon
    """
    try:
        # 'rar --version' n'est pas supporté, on appelle 'rar' sans arguments
        # et on vérifie que la sortie contient 'RAR' (code retour peut être != 0)
        result = subprocess.run(
            ["rar"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return "RAR" in output.upper()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
