import re

from marshmallow import Schema
from marshmallow import ValidationError as MarshmallowValidationError
from marshmallow import fields, validates


class PackEbookIn(Schema):
    file_path = fields.String(required=True)
    group = fields.String(required=True)
    source = fields.String(required=False, allow_none=True)
    url = fields.String(required=False, allow_none=True)
    enable_api = fields.Boolean(load_default=True)
    nfo_template = fields.String(required=False, allow_none=True)

    @validates("group")
    def validate_group(self, value):
        if not re.match(r"^[A-Za-z0-9_-]{2,32}$", value):
            raise MarshmallowValidationError(
                "Format groupe invalide (2-32 chars, alphanum + _ + -)"
            )


class PackTvIn(Schema):
    file_path = fields.String(required=True)
    release = fields.String(required=True)
    link = fields.String(required=False, allow_none=True)
    profile = fields.String(required=False, allow_none=True)


class ExtractMetadataIn(Schema):
    file_path = fields.String(required=True)
    enable_api = fields.Boolean(load_default=True)


class GroupUpdateIn(Schema):
    group = fields.String(required=True)

    @validates("group")
    def validate_group(self, value):
        if not re.match(r"^[A-Za-z0-9_-]{2,32}$", value):
            raise MarshmallowValidationError(
                "Format groupe invalide (2-32 chars, alphanum + _ + -)"
            )
