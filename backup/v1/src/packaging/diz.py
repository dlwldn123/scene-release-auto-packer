"""
Module de génération de fichiers DIZ (Description In Zip) pour releases Scene.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def generate_diz(
    release_name: str,
    release_dir: str | Path,
    num_disks: int = 1,
    filename: str = "FILE_ID.DIZ",
    max_lines: int = 30,
    max_width: int = 44,
) -> Path:
    """
    Génère fichier DIZ pour release Scene.

    Format : Fichier texte descriptif avec largeur maximale 44 caractères,
    max 30 lignes.

    Args:
        release_name: Nom release complet
        release_dir: Dossier release
        num_disks: Nombre de volumes/disques (défaut 1)
        filename: Nom fichier DIZ (défaut FILE_ID.DIZ)
        max_lines: Nombre maximum lignes (défaut 30)
        max_width: Largeur maximale caractères par ligne (défaut 44)

    Returns:
        Chemin fichier DIZ créé

    Raises:
        IOError: Si erreur création DIZ
    """
    release_dir = Path(release_dir)
    release_dir.mkdir(parents=True, exist_ok=True)

    diz_path = release_dir / filename

    # Contenu DIZ
    lines = []
    lines.append(release_name)
    lines.append("")
    lines.append(f"Disks: {num_disks}")
    lines.append("")
    lines.append("Complies with International Ebook Rules 2022")

    # Wrapper lignes si trop longues
    wrapped_lines = []
    for line in lines:
        if len(line) <= max_width:
            wrapped_lines.append(line)
        else:
            # Wrapper ligne
            while len(line) > max_width:
                wrap_pos = line.rfind(" ", 0, max_width)
                if wrap_pos == -1:
                    wrap_pos = max_width
                wrapped_lines.append(line[:wrap_pos])
                line = line[wrap_pos + 1 :]
            if line:
                wrapped_lines.append(line)

    # Limiter nombre lignes
    if len(wrapped_lines) > max_lines:
        wrapped_lines = wrapped_lines[:max_lines]
        wrapped_lines.append("...")

    diz_content = "\n".join(wrapped_lines) + "\n"

    # Écrire fichier DIZ
    try:
        with open(diz_path, "w", encoding="utf-8") as f:
            f.write(diz_content)
        logger.info(f"Fichier DIZ créé: {diz_path}")
    except Exception as e:
        logger.error(f"Erreur écriture DIZ: {diz_path}: {e}")
        raise IOError(f"Impossible créer DIZ: {e}")

    return diz_path
