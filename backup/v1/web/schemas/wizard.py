"""
Schémas Marshmallow pour le wizard.
"""

from marshmallow import Schema, fields, validate, validates_schema


class WizardStepValidateSchema(Schema):
    """Schéma pour la validation d'une étape."""

    step = fields.Int(required=True, validate=validate.Range(min=1, max=12))
    data = fields.Dict(required=True)


class FilesConfigSchema(Schema):
    """Schéma pour la configuration des fichiers."""

    source = fields.Str(required=True, validate=validate.OneOf(["local", "remote"]))
    path = fields.Str(allow_none=True)  # Si source=local
    url = fields.URL(allow_none=True)  # Si source=remote

    @validates_schema
    def validate_files(self, data, **kwargs):
        """Valide que path ou url est fourni selon source."""
        source = data.get("source")
        if source == "local" and not data.get("path"):
            raise validate.ValidationError(
                "path requis pour source=local", field_name="path"
            )
        elif source == "remote" and not data.get("url"):
            raise validate.ValidationError(
                "url requis pour source=remote", field_name="url"
            )


class EnrichmentConfigSchema(Schema):
    """Schéma pour la configuration d'enrichissement."""

    use_mediainfo = fields.Bool(load_default=False)
    use_apis = fields.Bool(load_default=True)
    api_keys = fields.Dict(allow_none=True)  # Override API keys optionnel


class ExportConfigSchema(Schema):
    """Schéma pour la configuration d'export."""

    download = fields.Bool(load_default=True)
    multi_volume = fields.Bool(load_default=False)
    ftp = fields.Dict(allow_none=True)  # Config FTP optionnelle
    sftp = fields.Dict(allow_none=True)  # Config SFTP optionnelle


class WizardPackRequestSchema(Schema):
    """Schéma pour la requête de packaging via wizard."""

    group = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    type = fields.Str(required=True, validate=validate.OneOf(["TV", "EBOOK", "DOCS"]))
    rules = fields.List(fields.Str(), allow_none=True)
    files = fields.Nested(FilesConfigSchema, required=True)
    metadata = fields.Dict(allow_none=True)
    enrichment = fields.Nested(EnrichmentConfigSchema, load_default={})
    template_id = fields.Str(allow_none=True)
    export = fields.Nested(ExportConfigSchema, load_default={})

    # Champs spécifiques selon type
    source_type = fields.Str(
        allow_none=True, validate=validate.OneOf(["RETAIL", "SCAN", "HYBRID"])
    )
    url = fields.URL(allow_none=True)
    release_name = fields.Str(allow_none=True)  # Pour TV
    link = fields.URL(allow_none=True)  # Pour TV
    profile = fields.Str(allow_none=True)  # Pour TV
