"""
Modèles SQLAlchemy pour l'application.
"""

from web.models.api_config import ApiConfig
from web.models.destination import Destination
from web.models.job import Artifact, Job, JobLog
from web.models.preference import GlobalPreference, UserPreference
from web.models.template import NfoTemplate
from web.models.user import User

__all__ = [
    "User",
    "Job",
    "JobLog",
    "Artifact",
    "UserPreference",
    "GlobalPreference",
    "NfoTemplate",
    "ApiConfig",
    "Destination",
]
