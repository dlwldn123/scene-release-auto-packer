"""
Schémas Marshmallow pour les utilisateurs.
"""

from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    """Schéma pour un utilisateur (lecture)."""

    id = fields.Int()
    username = fields.Str()
    email = fields.Str(allow_none=True)
    role = fields.Method("get_role")
    created_at = fields.DateTime()
    last_login = fields.DateTime(allow_none=True)

    def get_role(self, obj):
        """Retourne la valeur de l'enum role."""
        return obj.role.value if hasattr(obj.role, "value") else str(obj.role)


class UserCreateSchema(Schema):
    """Schéma pour la création d'un utilisateur."""

    username = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    password = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(allow_none=True)
    role = fields.Str(
        validate=validate.OneOf(["admin", "operator"]), load_default="operator"
    )


class UserUpdateSchema(Schema):
    """Schéma pour la mise à jour d'un utilisateur."""

    email = fields.Email(allow_none=True)
    role = fields.Str(validate=validate.OneOf(["admin", "operator"]), allow_none=True)
    password = fields.Str(validate=validate.Length(min=1), allow_none=True)
