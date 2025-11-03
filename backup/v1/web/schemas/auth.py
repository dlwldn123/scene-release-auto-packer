"""
Schémas Marshmallow pour l'authentification.
"""

from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    """Schéma pour la requête de login."""

    username = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    password = fields.Str(required=True, validate=validate.Length(min=1))
