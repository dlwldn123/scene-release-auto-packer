"""
Schémas Marshmallow pour les configurations de chemins.
"""

from marshmallow import Schema, fields, validate


class PathConfigSchema(Schema):
    """Schéma pour la configuration de chemin."""

    output_dir = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    destination_dir = fields.Str(allow_none=True, validate=validate.Length(max=500))
