"""
Modèles pour les jobs de packaging et leurs artefacts.
"""

import enum
import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from web.database import db


class JobStatus(enum.Enum):
    """Statuts des jobs."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(db.Model):
    """
    Modèle job de packaging.

    Chaque job représente un packaging de release avec:
    - Configuration complète (JSON)
    - Statut et progression
    - Logs associés
    - Artefacts générés
    """

    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, index=True
    )
    status = db.Column(
        db.Enum(JobStatus), nullable=False, default=JobStatus.PENDING, index=True
    )
    type = db.Column(db.String(50), nullable=False, index=True)  # TV/EBOOK/DOCS
    group_name = db.Column(db.String(100), nullable=False)
    release_name = db.Column(db.String(255), nullable=True)
    config = db.Column(db.JSON, nullable=False)  # Configuration complète job
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)

    # Relations
    logs = db.relationship(
        "JobLog",
        backref="job",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="JobLog.timestamp",
    )
    artifacts = db.relationship(
        "Artifact", backref="job", lazy=True, cascade="all, delete-orphan"
    )

    # Indexes pour performance queries
    __table_args__ = (
        db.Index("idx_job_user_created", "user_id", "created_at"),
        db.Index("idx_job_status_created", "status", "created_at"),
        db.Index("idx_job_type_created", "type", "created_at"),
    )

    def __init__(self, **kwargs):
        """Initialise le job avec un UUID unique."""
        if "job_id" not in kwargs:
            kwargs["job_id"] = str(uuid.uuid4())
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Job {self.job_id} ({self.status.value})>"

    def get_config(self) -> Dict[str, Any]:
        """
        Retourne la configuration du job.

        Returns:
            Dictionnaire de configuration
        """
        if isinstance(self.config, str):
            return json.loads(self.config)
        return self.config or {}

    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Définit la configuration du job.

        Args:
            config: Dictionnaire de configuration
        """
        self.config = config

    def start(self) -> None:
        """Marque le job comme démarré."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
        db.session.commit()

    def complete(self, release_name: Optional[str] = None) -> None:
        """
        Marque le job comme terminé.

        Args:
            release_name: Nom de la release générée (optionnel)
        """
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if release_name:
            self.release_name = release_name
        db.session.commit()

    def fail(self, error_message: str) -> None:
        """
        Marque le job comme échoué.

        Args:
            error_message: Message d'erreur
        """
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        db.session.commit()

    def add_log(self, level: str, message: str) -> None:
        """
        Ajoute un log au job.

        Args:
            level: Niveau de log (INFO/WARNING/ERROR/DEBUG)
            message: Message de log
        """
        log = JobLog(
            job_id=self.id,
            level=level.upper(),
            message=message,
            timestamp=datetime.utcnow(),
        )
        db.session.add(log)
        db.session.commit()


class JobLog(db.Model):
    """
    Logs associés à un job.

    Permet de tracer toutes les étapes du packaging.
    """

    __tablename__ = "job_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False, index=True)
    level = db.Column(db.String(20), nullable=False)  # INFO/WARNING/ERROR/DEBUG
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    __table_args__ = (db.Index("idx_job_logs_job_timestamp", "job_id", "timestamp"),)

    def __repr__(self) -> str:
        return f"<JobLog {self.level} @ {self.timestamp}>"


class Artifact(db.Model):
    """
    Artefacts générés par un job.

    Fichiers créés: ZIP, RAR, NFO, DIZ, SFV, etc.
    """

    __tablename__ = "artifacts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False, index=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # zip/rar/nfo/diz/sfv
    file_size = db.Column(db.BigInteger, nullable=True)
    crc32 = db.Column(db.String(8), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Artifact {self.file_type} ({self.file_path})>"
