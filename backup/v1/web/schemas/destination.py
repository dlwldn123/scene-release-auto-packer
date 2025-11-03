"""
Schémas Marshmallow pour les destinations FTP/SFTP.
"""

from marshmallow import Schema, fields, validate


class DestinationSchema(Schema):
    """Schéma pour une destination."""

    id = fields.Int()
    user_id = fields.Int()
    name = fields.Str()
    type = fields.Str()
    host = fields.Str()
    port = fields.Int()
    username = fields.Str()
    path = fields.Str(allow_none=True)
    created_at = fields.DateTime()
    # password exclu par sécurité


class DestinationCreateSchema(Schema):
    """Schéma pour créer une destination."""

    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    type = fields.Str(required=True, validate=validate.OneOf(["ftp", "sftp"]))
    host = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    port = fields.Int(required=True, validate=validate.Range(min=1, max=65535))
    username = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    password = fields.Str(required=True, validate=validate.Length(min=1))
    path = fields.Str(allow_none=True, validate=validate.Length(max=500))


class DestinationUpdateSchema(Schema):
    """Schéma pour mettre à jour une destination."""

    name = fields.Str(validate=validate.Length(min=1, max=255))
    host = fields.Str(validate=validate.Length(min=1, max=255))
    port = fields.Int(validate=validate.Range(min=1, max=65535))
    username = fields.Str(validate=validate.Length(min=1, max=255))
    password = fields.Str(validate=validate.Length(min=1))
    path = fields.Str(allow_none=True, validate=validate.Length(max=500))
