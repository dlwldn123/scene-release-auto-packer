"""
Schémas Marshmallow pour validation et sérialisation des données API.
"""

from typing import Optional

from marshmallow import Schema
from marshmallow import ValidationError as MarshmallowValidationError
from marshmallow import fields, validate


class PackEbookIn(Schema):
    """
    Schéma validation pour requête packaging eBook.

    Args:
        file_path: Chemin fichier eBook
        group: Tag groupe Scene (requis)
        source: Type source (RETAIL, SCAN, HYBRID, optionnel)
        url: URL release (optionnel)
        enable_api: Activer enrichissement API (défaut True)
    """

    file_path = fields.Str(required=True, validate=validate.Length(min=1))
    group = fields.Str(
        required=True,
        validate=validate.Regexp(
            r"^[A-Za-z0-9_-]{2,32}$",
            error="Group tag invalide (2-32 chars, alphanum + _ + -)",
        ),
    )
    source = fields.Str(
        allow_none=True,
        validate=validate.OneOf(
            ["RETAIL", "SCAN", "HYBRID"],
            error="Source doit être RETAIL, SCAN ou HYBRID",
        ),
    )
    url = fields.Str(allow_none=True, validate=validate.URL(error="URL invalide"))
    enable_api = fields.Bool(missing=True)


class PackTvIn(Schema):
    """
    Schéma validation pour requête packaging TV/Video.

    Args:
        file_path: Chemin fichier vidéo
        release: Nom release (requis)
        link: URL release (optionnel)
        profile: Profil encodage (optionnel)
    """

    file_path = fields.Str(required=True, validate=validate.Length(min=1))
    release = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    link = fields.Str(allow_none=True, validate=validate.URL(error="URL invalide"))
    profile = fields.Str(allow_none=True)


class ExtractMetadataIn(Schema):
    """
    Schéma validation pour requête extraction métadonnées.

    Args:
        file_path: Chemin fichier eBook
        enable_api: Activer enrichissement API (défaut True)
    """

    file_path = fields.Str(required=True, validate=validate.Length(min=1))
    enable_api = fields.Bool(missing=True)


class GroupUpdateIn(Schema):
    """
    Schéma validation pour mise à jour groupe Scene.

    Args:
        group: Nom groupe (requis)
    """

    group = fields.Str(
        required=True,
        validate=validate.Regexp(r"^[A-Za-z0-9_-]{2,32}$", error="Group tag invalide"),
    )


class ConfigUpdateIn(Schema):
    """
    Schéma validation pour mise à jour configuration.

    Accepte toute configuration valide (pas de validation stricte pour flexibilité).
    """

    pass  # Configuration flexible, validation côté serveur
