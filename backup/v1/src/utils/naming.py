"""
Module de génération de noms de releases conforme Scene Rules 2022.
"""

import logging
import re
import unicodedata
from typing import Optional

logger = logging.getLogger(__name__)


def generate_release_name(
    metadata: dict,
    format_type: str,
    group_tag: str,
    source_type: Optional[str] = None,
    filepath: Optional[str] = None,
) -> str:
    """
    Génère nom release conforme Scene Rules 2022.

    Format: author.title.year.source.format-lang.group

    Args:
        metadata: Dictionnaire métadonnées (title, author, year, language)
        format_type: Format fichier ('EPUB', 'PDF', 'MOBI', etc.)
        group_tag: Tag groupe Scene (2-32 chars, alphanum + _ + -)
        source_type: Type source ('RETAIL', 'SCAN', 'HYBRID', None=auto-détection)
        filepath: Chemin fichier original (pour auto-détection source, optionnel)

    Returns:
        Nom release normalisé (max 255 chars)

    Raises:
        ValueError: Si group_tag invalide ou métadonnées essentielles manquantes
    """
    # Valider group_tag
    if not re.match(r"^[A-Za-z0-9_-]{2,32}$", group_tag):
        raise ValueError(
            f"Group tag invalide: {group_tag} (2-32 chars, alphanum + _ + -)"
        )

    # Normaliser composants
    author = normalize_string(metadata.get("author") or "Unknown")
    title = normalize_string(metadata.get("title") or "Unknown")
    year = metadata.get("year") or "0000"

    # Valider année (4 chiffres)
    if not re.match(r"^\d{4}$", str(year)):
        year = "0000"

    # Détecter source si non spécifiée
    if source_type is None:
        source_type = _detect_source_type(filepath) or "RETAIL"

    # Normaliser format (MAJUSCULES)
    format_normalized = format_type.upper()

    # Langue : extraire depuis métadonnées et normaliser
    language = metadata.get("language") or "en"
    lang_normalized = _normalize_language(language)

    # Normaliser group_tag (minuscules)
    group_normalized = group_tag.lower()

    # Construire nom release
    parts = [
        author,
        title,
        year,
        source_type,
        format_normalized,
        lang_normalized,
        group_normalized,
    ]
    release_name = ".".join(parts)

    # Tronquer si >255 chars (conforme Scene Rules)
    if len(release_name) > 255:
        logger.warning(f"Nom release trop long ({len(release_name)} chars), troncature")
        # Tronquer progressivement en conservant parties essentielles
        # Garder: source.format-lang.group (fixe) + tronquer author.title.year
        fixed_part = (
            f"{source_type}.{format_normalized}-{lang_normalized}.{group_normalized}"
        )
        max_author_title_year = 255 - len(fixed_part) - 3  # -3 pour points séparateurs
        variable_part = ".".join([author, title, year])
        if len(variable_part) > max_author_title_year:
            # Tronquer title d'abord (plus flexible)
            available_for_title = max_author_title_year - len(author) - len(year) - 2
            if available_for_title > 0:
                title_truncated = title[:available_for_title]
                variable_part = ".".join([author, title_truncated, year])
            else:
                # Tronquer author aussi si nécessaire
                available_total = max_author_title_year - len(year) - 2
                if available_total > 0:
                    author_truncated = author[: available_total // 2]
                    title_truncated = title[: available_total // 2]
                    variable_part = ".".join([author_truncated, title_truncated, year])
        release_name = f"{variable_part}.{fixed_part}"

    logger.debug(f"Nom release généré: {release_name}")
    return release_name


def normalize_string(text: str) -> str:
    """
    Normalise string pour nom release Scene.

    Conversion:
    - Supprimer accents (normalisation Unicode NFD + suppression diacritiques)
    - Remplacer espaces/caractères spéciaux par points
    - Caractères autorisés: lettres ASCII (a-z), chiffres (0-9), points (.), tirets (-), underscores (_)
    - Séparateurs multiples points remplacés par un seul point

    Args:
        text: Texte à normaliser

    Returns:
        String normalisée
    """
    if not text:
        return "Unknown"

    # Normalisation Unicode NFD et suppression diacritiques
    normalized = unicodedata.normalize("NFD", text)
    normalized = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

    # Convertir en minuscules
    normalized = normalized.lower()

    # Remplacer caractères non autorisés par points
    # Caractères autorisés: a-z, 0-9, points, tirets, underscores
    normalized = re.sub(r"[^a-z0-9._-]", ".", normalized)

    # Remplacer séparateurs multiples points par un seul point
    normalized = re.sub(r"\.{2,}", ".", normalized)

    # Supprimer points en début/fin
    normalized = normalized.strip(".")

    # Si vide après normalisation, retourner 'Unknown'
    if not normalized:
        return "Unknown"

    return normalized


def _detect_source_type(filepath: Optional[str]) -> Optional[str]:
    """
    Détecte type source depuis nom fichier.

    Cherche patterns: -retail, -scan, -hybrid dans nom fichier.

    Args:
        filepath: Chemin fichier

    Returns:
        Type source ('RETAIL', 'SCAN', 'HYBRID') ou None si non détecté
    """
    if not filepath:
        return None

    filename_lower = filepath.lower()

    if "-retail" in filename_lower or "_retail" in filename_lower:
        return "RETAIL"
    elif "-scan" in filename_lower or "_scan" in filename_lower:
        return "SCAN"
    elif "-hybrid" in filename_lower or "_hybrid" in filename_lower:
        return "HYBRID"

    return None


def _normalize_language(lang_code: str) -> str:
    """
    Normalise code langue pour nom release.

    Conversion codes ISO 639-1 vers noms complets (si nécessaire).

    Args:
        lang_code: Code langue (ISO 639-1 ou nom complet)

    Returns:
        Code langue normalisé (ex: 'english', 'french')
    """
    lang_lower = lang_code.lower().strip()

    # Mapping codes ISO 639-1 vers noms
    lang_map = {
        "en": "english",
        "fr": "french",
        "de": "german",
        "es": "spanish",
        "it": "italian",
        "pt": "portuguese",
        "ru": "russian",
        "ja": "japanese",
        "zh": "chinese",
        "ko": "korean",
    }

    if lang_lower in lang_map:
        return lang_map[lang_lower]

    # Si déjà nom complet, normaliser
    lang_normalized = normalize_string(lang_code)

    # Valeur par défaut si non reconnu
    if not lang_normalized or lang_normalized == "unknown":
        return "english"

    return lang_normalized
