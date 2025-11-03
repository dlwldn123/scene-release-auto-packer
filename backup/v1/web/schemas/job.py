"""
Schémas Marshmallow pour les jobs.
"""

from datetime import datetime

from marshmallow import Schema, fields


class JobResponseSchema(Schema):
    """Schéma pour la réponse d'un job."""

    id = fields.Int()
    job_id = fields.Str()
    user_id = fields.Int()
    status = fields.Str()
    type = fields.Str()
    group_name = fields.Str()
    release_name = fields.Str(allow_none=True)
    config = fields.Dict()
    created_at = fields.DateTime()
    started_at = fields.DateTime(allow_none=True)
    completed_at = fields.DateTime(allow_none=True)
    error_message = fields.Str(allow_none=True)


class JobListSchema(Schema):
    """Schéma pour la liste des jobs."""

    jobs = fields.List(fields.Nested(JobResponseSchema))
    total = fields.Int()
    limit = fields.Int()
    offset = fields.Int()
