"""
Schémas Marshmallow pour la configuration des APIs.
"""

from typing import Any, Dict

from marshmallow import Schema, fields, post_load, validate


class ApiConfigSchema(Schema):
    """Schéma pour sérialisation config API (sans clé en clair)."""

    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    api_name = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    # Ne jamais exposer la clé API en clair
    api_key_masked = fields.Method("get_masked_api_key", dump_only=True)

    def get_masked_api_key(self, obj):
        """Retourne une version masquée de la clé API."""
        if hasattr(obj, "api_key") and obj.api_key:
            return "***"  # Toujours masquer

    class Meta:
        ordered = True


class ApiConfigCreateSchema(Schema):
    """Schéma pour création config API."""

    api_name = fields.Str(
        required=True, validate=validate.OneOf(["omdb", "tvdb", "tmdb", "openlibrary"])
    )
    api_data = fields.Dict(
        required=True,
        validate=validate.Length(min=1),
        metadata={"description": "Dictionnaire avec clé API et autres configs"},
    )

    @post_load
    def validate_api_data(self, data, **kwargs):
        """Valide que api_data contient au moins une clé."""
        api_data = data.get("api_data", {})
        if not api_data:
            raise validate.ValidationError(
                "api_data ne peut pas être vide", field_name="api_data"
            )

        # Validation spécifique selon API
        api_name = data.get("api_name")
        if (
            api_name == "tvdb"
            and "user_key" not in api_data
            and "api_key" not in api_data
        ):
            raise validate.ValidationError(
                "tvdb nécessite api_key et user_key", field_name="api_data"
            )

        return data

    class Meta:
        ordered = True


class ApiConfigUpdateSchema(Schema):
    """Schéma pour mise à jour config API."""

    api_data = fields.Dict(
        required=True,
        validate=validate.Length(min=1),
        metadata={"description": "Dictionnaire avec clé API et autres configs"},
    )

    class Meta:
        ordered = True


class ApiConfigTestSchema(Schema):
    """Schéma pour test connexion API."""

    success = fields.Bool(dump_only=True)
    message = fields.Str(dump_only=True)
