"""
Module de génération de fichiers NFO pour releases Scene.
"""

import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, Optional

# Import service template renderer pour utiliser rendu avancé
try:
    from web.services.template_renderer import render_nfo_template
except ImportError:
    # Fallback si import impossible (CLI standalone)
    render_nfo_template = None

logger = logging.getLogger(__name__)


def generate_nfo(
    release_name: str,
    metadata: Dict[str, Optional[str]],
    group: str,
    url: Optional[str] = None,
    release_dir: Optional[str | Path] = None,
    template_path: Optional[str | Path] = None,
    max_width: int = 80,
) -> Path:
    """
    Génère fichier NFO pour release Scene.

    Format : Encodage ASCII strict (Windows-1252 préféré, fallback UTF-8).
    Largeur maximale : 80 colonnes avec wrapper automatique.

    Args:
        release_name: Nom release complet
        metadata: Dictionnaire métadonnées (title, author, etc.)
        group: Tag groupe Scene
        url: URL release (optionnel)
        release_dir: Dossier release (si None, utilise dossier courant)
        template_path: Chemin template NFO (si None, utilise template par défaut)
        max_width: Largeur maximale colonnes (défaut 80)

    Returns:
        Chemin fichier NFO créé

    Raises:
        IOError: Si erreur écriture fichier
    """
    if release_dir is None:
        release_dir = Path.cwd()
    else:
        release_dir = Path(release_dir)
        release_dir.mkdir(parents=True, exist_ok=True)

    # Nom fichier NFO : release.name.lower().nfo
    nfo_filename = f"{release_name.lower()}.nfo"
    nfo_path = release_dir / nfo_filename

    # Charger template
    template_content = _load_template(template_path)

    # Calculer taille et checksums
    file_size = 0
    md5_hash = None
    sha1_hash = None

    if release_dir.exists():
        # Chercher fichier principal (ebook original ou archive principale)
        ebook_files = (
            list(release_dir.glob("*.epub"))
            + list(release_dir.glob("*.pdf"))
            + list(release_dir.glob("*.mobi"))
        )

        if ebook_files:
            main_file = ebook_files[0]
            file_size = main_file.stat().st_size

            # Calculer checksums
            md5_hash = _calculate_checksum(main_file, "md5")
            sha1_hash = _calculate_checksum(main_file, "sha1")

    # Format taille
    size_str = _format_size(file_size)

    # Remplacer variables template
    nfo_content = template_content

    # Utiliser service template renderer si disponible (support conditionnelles avancées)
    if render_nfo_template:
        variables = {
            "title": metadata.get("title") or "Unknown",
            "author": metadata.get("author") or "Unknown",
            "publisher": metadata.get("publisher") or "Unknown",
            "year": metadata.get("year") or "0000",
            "language": metadata.get("language") or "en",
            "isbn": metadata.get("isbn") or "",
            "format": metadata.get("format") or "UNKNOWN",
            "release_name": release_name,
            "group": group,
            "url": url or "",
            "size": size_str,
            "md5": md5_hash or "",
            "sha1": sha1_hash or "",
        }
        nfo_content = render_nfo_template(template_content, variables)
    else:
        # Fallback : remplacement simple (compatibilité)
        replacements = {
            "{{title}}": metadata.get("title") or "Unknown",
            "{{author}}": metadata.get("author") or "Unknown",
            "{{publisher}}": metadata.get("publisher") or "Unknown",
            "{{year}}": metadata.get("year") or "0000",
            "{{language}}": metadata.get("language") or "en",
            "{{isbn}}": metadata.get("isbn") or "N/A",
            "{{format}}": metadata.get("format") or "UNKNOWN",
            "{{release_name}}": release_name,
            "{{group}}": group,
            "{{url}}": url or "N/A",
            "{{size}}": size_str,
            "{{md5}}": md5_hash or "N/A",
            "{{sha1}}": sha1_hash or "N/A",
        }

        for key, value in replacements.items():
            nfo_content = nfo_content.replace(key, str(value))

    # Wrapper lignes longues (max_width colonnes)
    wrapped_lines = []
    for line in nfo_content.splitlines():
        if len(line) <= max_width:
            wrapped_lines.append(line)
        else:
            # Wrapper ligne trop longue
            while len(line) > max_width:
                # Trouver dernier espace avant max_width
                wrap_pos = line.rfind(" ", 0, max_width)
                if wrap_pos == -1:
                    # Pas d'espace, couper à max_width
                    wrap_pos = max_width

                wrapped_lines.append(line[:wrap_pos])
                line = line[wrap_pos + 1 :]
            if line:
                wrapped_lines.append(line)

    nfo_content_wrapped = "\n".join(wrapped_lines)

    # Vérifier encodage ASCII (Windows-1252 préféré)
    # Convertir caractères non-ASCII si nécessaire
    try:
        # Essayer encodage Windows-1252 d'abord
        nfo_bytes = nfo_content_wrapped.encode("windows-1252")
    except UnicodeEncodeError:
        # Fallback UTF-8 si caractères non-ASCII non supportés Windows-1252
        logger.warning("Caractères non-ASCII détectés, utilisation UTF-8")
        nfo_bytes = nfo_content_wrapped.encode("utf-8")

    # Écrire fichier NFO
    try:
        with open(nfo_path, "wb") as f:
            f.write(nfo_bytes)
        logger.info(f"Fichier NFO créé: {nfo_path}")
    except Exception as e:
        logger.error(f"Erreur écriture NFO: {nfo_path}: {e}")
        raise IOError(f"Impossible créer NFO: {e}")

    return nfo_path


def _load_template(template_path: Optional[str | Path]) -> str:
    """
    Charge template NFO depuis fichier, DB ou retourne template par défaut.

    Args:
        template_path: Chemin template fichier, ID template DB (int), ou None = template par défaut

    Returns:
        Contenu template (string)
    """
    # Si template_path est un entier, charger depuis DB
    if isinstance(template_path, int) or (
        isinstance(template_path, str) and template_path.isdigit()
    ):
        try:
            from web.services.template_renderer import load_template_from_db

            template_id = int(template_path)
            db_content = load_template_from_db(template_id)
            if db_content:
                return db_content
        except Exception as e:
            logger.warning(f"Erreur chargement template DB {template_path}: {e}")

    # Sinon, charger depuis fichier
    if template_path:
        path = Path(template_path)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Erreur chargement template: {e}, utilisation défaut")

    # Template par défaut depuis DB si disponible
    try:
        from web.services.template_renderer import get_default_template_from_db

        default_db = get_default_template_from_db()
        if default_db:
            return default_db
    except (ImportError, AttributeError, RuntimeError) as e:
        logger.debug(
            f"Erreur récupération template DB: {e}, utilisation template système"
        )
        pass  # Fallback vers template système

    # Template par défaut système
    return """┌──────────────────────────────────────────────────────────────────────────────┐
│                           RELEASE INFORMATION                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Title: {{title}}                                                           │
│  Author: {{author}}                                                          │
│  Publisher: {{publisher}}                                                   │
│  Year: {{year}}                                                              │
│  Language: {{language}}                                                      │
│  ISBN: {{isbn}}                                                              │
│  Format: {{format}}                                                          │
│                                                                              │
│  Release Name: {{release_name}}                                              │
│  Group: {{group}}                                                            │
│                                                                              │
│  URL: {{url}}                                                                │
│  Size: {{size}}                                                              │
│  MD5: {{md5}}                                                                │
│  SHA1: {{sha1}}                                                              │
│                                                                              │
│  Note: This release complies with International Ebook Rules 2022            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
"""


def _calculate_checksum(filepath: Path, algorithm: str = "md5") -> Optional[str]:
    """
    Calcule checksum MD5 ou SHA1 d'un fichier.

    Args:
        filepath: Chemin fichier
        algorithm: 'md5' ou 'sha1'

    Returns:
        Checksum hexadécimal ou None si erreur
    """
    try:
        hash_obj = hashlib.md5() if algorithm == "md5" else hashlib.sha1()

        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()
    except (IOError, OSError, PermissionError, MemoryError) as e:
        logger.warning(f"Erreur calcul checksum {algorithm}: {e}")
        return None


def _format_size(size_bytes: int) -> str:
    """
    Formate taille en format lisible (KB, MB, GB).

    Args:
        size_bytes: Taille en bytes

    Returns:
        String formatée (ex: "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
