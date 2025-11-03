"""
Schémas Marshmallow pour les templates NFO.
"""

from marshmallow import Schema, fields, validate


class TemplateSchema(Schema):
    """Schéma pour un template NFO."""

    id = fields.Int()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    content = fields.Str()
    variables = fields.Dict(allow_none=True)
    is_default = fields.Bool()
    created_by = fields.Int(allow_none=True)
    created_at = fields.DateTime()


class TemplateCreateSchema(Schema):
    """Schéma pour créer/mettre à jour un template."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    content = fields.Str(required=True, validate=validate.Length(min=1))
    variables = fields.Dict(allow_none=True)
    is_default = fields.Bool(missing=False)


class TemplateRenderSchema(Schema):
    """Schéma pour le rendu d'un template."""

    variables = fields.Dict(required=True)
