"""
Schémas Marshmallow pour les préférences.
"""

from marshmallow import Schema, fields


class PreferenceSchema(Schema):
    """Schéma pour une préférence."""

    id = fields.Int()
    user_id = fields.Int(allow_none=True)
    preference_key = fields.Str()
    preference_value = fields.Dict()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class PreferenceListSchema(Schema):
    """Schéma pour la liste des préférences."""

    preferences = fields.List(fields.Nested(PreferenceSchema))
